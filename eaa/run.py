"""Resumable experiment runner.

Phase A (independent): closed_book, off@level, reader@level, reader_score@level (P(SUFFICIENT))
Phase B (depends on A):
  advisory@level          evidence + reader verdict only (primary)
  advisory_missing@level  evidence + verdict + reader's free-text "missing" (secondary; leak-checked)
  restored                turn 1 at restore_from, turn 2 full evidence ("update" follow-up)
  restored_ctrl           turn 1 at full,         turn 2 identical follow-up (format control)

Every generation is appended to <output_root>/<run_name>/generations.jsonl keyed by
"item_id|task|level"; re-running skips keys already present.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import yaml
from tqdm import tqdm

from . import prompts as P
from .backends import make_backend
from .conditions import LEVELS, question_class, plan_item, render_units
from .data import load_items
from .evaluate import parse_reader


def _msgs(user: str) -> list[dict]:
    return [{"role": "system", "content": P.SYSTEM}, {"role": "user", "content": user}]


def _load_done(path: Path) -> dict[str, dict]:
    done = {}
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    done[r["key"]] = r
    return done


def build_plans(items, cfg, backend, run_dir: Path):
    plans, excluded = {}, []
    for it in items:
        plan = plan_item(it, cfg["seed"], cfg["n_extra_distractors"], backend.count_tokens)
        if plan is None:
            excluded.append(it["id"])
        else:
            plans[it["id"]] = plan
    qcls = {it["id"]: question_class(it) for it in items}
    with open(run_dir / "packets.jsonl", "w", encoding="utf-8") as f:
        for iid, plan in plans.items():
            full_tok = backend.count_tokens(render_units(plan.packet("full")))
            for lv in LEVELS:
                ev = render_units(plan.packet(lv))
                tok = backend.count_tokens(ev)
                f.write(json.dumps({
                    "item_id": iid, "level": lv, "qclass": qcls[iid],
                    "gold_kept_frac": plan.gold_kept_frac(lv),
                    "answer_in_packet": plan.answer_in_packet(lv),
                    "answer_para_defined": plan.answer_para_defined,
                    "evidence": ev, "evidence_tokens": tok, "len_ratio_vs_full": tok / full_tok,
                    "gold_flags": [u.gold for u in plan.packet(lv)],
                }, ensure_ascii=False) + "\n")
    (run_dir / "exclusions.json").write_text(json.dumps(
        {"n_excluded": len(excluded), "ids": excluded,
         "rule": "not exactly 2 gold paragraphs with valid sentences, or too few distractor sentences"},
        indent=2))
    return plans


def phase_a_tasks(items, plans, cfg):
    for it in items:
        iid, q = it["id"], it["question"]
        yield (f"{iid}|closed_book|None", iid, "closed_book", None,
               _msgs(P.CLOSED_BOOK.format(question=q)), cfg["max_new_tokens_answer"])
        if iid not in plans:
            continue
        for lv in LEVELS:
            ev = render_units(plans[iid].packet(lv))
            yield (f"{iid}|off|{lv}", iid, "off", lv,
                   _msgs(P.GENERATOR.format(evidence=ev, advisory="", question=q)),
                   cfg["max_new_tokens_answer"])
            yield (f"{iid}|reader|{lv}", iid, "reader", lv,
                   _msgs(P.READER.format(evidence=ev, question=q)), cfg["max_new_tokens_reader"])


READER_PREFIX = '{"verdict": "'
READER_OPTIONS = ["SUFFICIENT", "INSUFFICIENT"]


def score_tasks(items, plans):
    for it in items:
        iid, q = it["id"], it["question"]
        if iid not in plans:
            continue
        for lv in LEVELS:
            ev = render_units(plans[iid].packet(lv))
            yield (f"{iid}|reader_score|{lv}", iid, lv, _msgs(P.READER.format(evidence=ev, question=q)))


def run_scores(tasks, backend, cfg, out_path: Path, done: dict):
    """Reader's continuous epistemic score: log P(option | reader prompt + '{"verdict": "')."""
    todo = [t for t in tasks if t[0] not in done]
    if not todo:
        print("[reader_score] nothing to do")
        return
    bs = max(1, cfg["batch_size"] // len(READER_OPTIONS))
    with open(out_path, "a", encoding="utf-8") as f, tqdm(total=len(todo), desc="reader_score") as bar:
        for i in range(0, len(todo), bs):
            chunk = todo[i:i + bs]
            scores = backend.score_continuations([t[3] for t in chunk], READER_PREFIX, READER_OPTIONS)
            for t, sc in zip(chunk, scores):
                rec = {"key": t[0], "item_id": t[1], "task": "reader_score", "level": t[2],
                       "prompt_tokens": None, "output": json.dumps(dict(zip(READER_OPTIONS, sc))),
                       "model": backend.name, "prompt_version": P.PROMPT_VERSION, "ts": time.time()}
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                done[t[0]] = rec
            f.flush()
            bar.update(len(chunk))


def _two_turn(plan, q, done, iid, first_level):
    prev = done.get(f"{iid}|off|{first_level}")
    if prev is None:
        return None
    msgs = _msgs(P.GENERATOR.format(evidence=render_units(plan.packet(first_level)),
                                    advisory="", question=q))
    msgs += [{"role": "assistant", "content": prev["output"]},
             {"role": "user", "content": P.RESTORE_FOLLOWUP.format(
                 evidence=render_units(plan.packet("full")), question=q)}]
    return msgs


def phase_b_tasks(items, plans, cfg, done):
    for it in items:
        iid, q = it["id"], it["question"]
        if iid not in plans:
            continue
        plan = plans[iid]
        for lv in LEVELS:
            rd = done.get(f"{iid}|reader|{lv}")
            if rd is None:
                continue
            verdict, missing = parse_reader(rd["output"])
            if verdict == "PARSE_ERROR":
                verdict, missing = "UNKNOWN", ""
            ev = render_units(plan.packet(lv))
            for task, inc in (("advisory", False), ("advisory_missing", True)):
                adv = P.advisory_block(verdict, missing, include_missing=inc)
                yield (f"{iid}|{task}|{lv}", iid, task, lv,
                       _msgs(P.GENERATOR.format(evidence=ev, advisory=adv, question=q)),
                       cfg["max_new_tokens_answer"])
        for task, first in (("restored", cfg["restore_from"]), ("restored_ctrl", "full")):
            msgs = _two_turn(plan, q, done, iid, first)
            if msgs is not None:
                yield (f"{iid}|{task}|{first}", iid, task, first, msgs, cfg["max_new_tokens_answer"])


def run_tasks(tasks, backend, cfg, out_path: Path, done: dict, desc: str):
    todo = [t for t in tasks if t[0] not in done]
    if not todo:
        print(f"[{desc}] nothing to do")
        return
    todo = [(*t, backend.prompt_tokens(t[4])) for t in todo]
    # group by max_new_tokens (answers vs reader JSON), then by length to limit padding
    todo.sort(key=lambda t: (t[5], t[6]))
    bs = cfg["batch_size"]
    with open(out_path, "a", encoding="utf-8") as f, tqdm(total=len(todo), desc=desc) as bar:
        i = 0
        while i < len(todo):
            mnt = todo[i][5]
            chunk = [t for t in todo[i:i + bs] if t[5] == mnt]
            try:
                outs = backend.generate([t[4] for t in chunk], mnt)
            except RuntimeError as e:  # CUDA OOM -> shrink batch and retry
                if "out of memory" in str(e).lower() and bs > 1:
                    bs = max(1, bs // 2)
                    import torch
                    torch.cuda.empty_cache()
                    print(f"OOM: batch_size -> {bs}")
                    continue
                raise
            for t, o in zip(chunk, outs):
                rec = {"key": t[0], "item_id": t[1], "task": t[2], "level": t[3],
                       "prompt_tokens": t[6], "output": o, "model": backend.name,
                       "prompt_version": P.PROMPT_VERSION, "batch_size": bs, "ts": time.time()}
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                done[t[0]] = rec
            f.flush()
            bar.update(len(chunk))
            i += len(chunk)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--limit", type=int, default=None, help="only first N items (smoke test)")
    ap.add_argument("--backend", default=None, help="override backend (e.g. mock)")
    ap.add_argument("--run-name", default=None)
    ap.add_argument("--batch-size", type=int, default=None, help="override (1 = batching-noise check)")
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config, encoding="utf-8"))
    for k, v in (("backend", args.backend), ("run_name", args.run_name), ("batch_size", args.batch_size)):
        if v:
            cfg[k] = v
    items = load_items(Path(cfg["items_path"]))
    if args.limit:
        items = items[: args.limit]

    run_dir = Path(cfg["output_root"]) / cfg["run_name"]
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "config.resolved.yaml").write_text(yaml.safe_dump({**cfg, "limit": args.limit}))

    backend = make_backend(cfg)
    plans = build_plans(items, cfg, backend, run_dir)
    print(f"items={len(items)} planned={len(plans)} excluded={len(items) - len(plans)}")

    out_path = run_dir / "generations.jsonl"
    done = _load_done(out_path)
    run_tasks(list(phase_a_tasks(items, plans, cfg)), backend, cfg, out_path, done, "phase A")
    run_scores(list(score_tasks(items, plans)), backend, cfg, out_path, done)
    run_tasks(list(phase_b_tasks(items, plans, cfg, done)), backend, cfg, out_path, done, "phase B")
    print(f"done -> {out_path}")


if __name__ == "__main__":
    main()
