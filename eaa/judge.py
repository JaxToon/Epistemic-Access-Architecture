"""Tiered answer correctness: rules for clear cases, a stronger local LLM judge for ambiguous ones.

Audit (2026-10-05, research_log): ~1/3 of `off@full` "hallucinations" under the containment rule
were correct answers in a different surface form ("Al Capone" vs "Alphonse Gabriel Capone",
"42" vs "42 members", "Australia" vs "Australian").

  rule_correct   EM, gold ⊂ pred, or yes/no first-token match          -> correct
  rule_wrong     no content-token overlap with gold (prefix-5 / digit match) -> wrong
  ambiguous      everything else -> judge (Qwen2.5-7B-Instruct, 4-bit, deterministic
                 log P("YES") vs log P("NO")), cached per (item_id, normalized prediction)

The judge never sees the evidence or the condition, only question / gold / prediction.
Usage: python -m eaa.judge --config configs/pilot_v0.1.yaml [--extra file.jsonl ...]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from .evaluate import is_correct, normalize_answer, response_class

JUDGE_CACHE = Path("06_evaluation/judge_cache.jsonl")
JUDGE_MODEL = "03_models/Qwen2.5-7B-Instruct"
STOP = {"of", "and", "in", "on", "at", "for", "to", "by", "with", "from", "is", "was", "be", "it",
        "its", "his", "her", "their", "as", "or", "that", "this", "which", "who"}

JUDGE_PROMPT = (
    "You are grading a question-answering system.\n"
    "Question: {q}\nGold answer: {g}\nSystem answer: {p}\n\n"
    "Does the system answer refer to the same entity, value or fact as the gold answer? "
    "Answer YES if it is correct even if it is shorter, longer or phrased differently "
    "(e.g. 'Al Capone' for 'Alphonse Gabriel Capone', 'Australia' for 'Australian'). "
    "Answer NO if it names a different entity or value, or if it is too vague to identify the gold "
    "answer.\nReply with YES or NO only."
)


def _content(s: str) -> list[str]:
    return [t for t in normalize_answer(s).split() if t not in STOP]


def rule_verdict(pred: str, gold: str) -> str:
    """'correct' | 'wrong' | 'ambiguous' (only for substantive predictions)."""
    if is_correct(pred, gold):
        return "correct"
    g, p = _content(gold), _content(pred)
    if normalize_answer(gold) in {"yes", "no"}:
        return "wrong"
    for a in p:
        for b in g:
            if a == b or (a.isdigit() and a == b) or (len(a) >= 5 and len(b) >= 5 and a[:5] == b[:5]):
                return "ambiguous"
    return "wrong"


AUDIT_GLOB = "audit_ambiguous_*.jsonl"


def load_cache(path: Path = JUDGE_CACHE, mode: str | None = None) -> dict[tuple[str, str], bool]:
    """Labels for rule-ambiguous predictions.

    mode (env EAA_LABELS, default "audit_then_judge"):
      judge             LLM judge only
      audit_then_judge  documented per-item audit labels (06_evaluation/audit_ambiguous_*.jsonl)
                        override the judge; judge fills the rest  [primary since 2026-10-06:
                        judge agreed with the audit on 82%, kappa 0.61, and its disagreements were
                        mostly clear errors, see research_log]
    Strict labels (rule only) are always available as `correct_strict`."""
    import os

    mode = mode or os.environ.get("EAA_LABELS", "audit_then_judge")
    out = {}
    if path.exists():
        for line in open(path, encoding="utf-8"):
            r = json.loads(line)
            out[(r["item_id"], r["pred_norm"])] = bool(r["correct"])
    if mode == "audit_then_judge":
        for fp in sorted(path.parent.glob(AUDIT_GLOB)):
            for line in open(fp, encoding="utf-8"):
                r = json.loads(line)
                out[(r["item_id"], r["pred_norm"])] = bool(r["correct"])
    return out


def main():
    import yaml

    from .backends import HFBackend
    from .data import load_items

    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--extra", nargs="*", default=[], help="more jsonl files with item_id + output")
    ap.add_argument("--batch-size", type=int, default=8)
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config, encoding="utf-8"))
    items = {}
    for fp in [Path(cfg["items_path"]), *sorted(Path("01_data").glob("hotpot_dev_*.jsonl"))]:
        items.update({it["id"]: it for it in load_items(fp)})   # pilot + Study 2 item sets
    files = [Path(cfg["output_root"]) / cfg["run_name"] / "generations.jsonl"] + [Path(x) for x in args.extra]

    cache = load_cache()
    todo = {}
    n_rule = {"correct": 0, "wrong": 0, "ambiguous": 0}
    for fp in files:
        for line in open(fp, encoding="utf-8"):
            r = json.loads(line)
            if r.get("task") in {"reader", "reader_score"}:
                continue
            pred = r["output"]
            if response_class(pred) != "substantive":
                continue
            v = rule_verdict(pred, items[r["item_id"]]["answer"])
            n_rule[v] += 1
            key = (r["item_id"], normalize_answer(pred))
            if v == "ambiguous" and key not in cache:
                todo[key] = pred
    print(f"rule verdicts over substantive outputs: {n_rule}; new ambiguous to judge: {len(todo)}")
    if not todo:
        return

    be = HFBackend(JUDGE_MODEL, load_in_4bit=True)
    keys = list(todo)
    from tqdm import tqdm
    JUDGE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    with open(JUDGE_CACHE, "a", encoding="utf-8") as f:
        for i in tqdm(range(0, len(keys), args.batch_size), desc="judge"):
            chunk = keys[i:i + args.batch_size]
            msgs = [[{"role": "user", "content": JUDGE_PROMPT.format(
                q=items[k[0]]["question"], g=items[k[0]]["answer"], p=todo[k])}] for k in chunk]
            scores = be.score_continuations(msgs, "", ["YES", "NO"])
            for k, (y, n) in zip(chunk, scores):
                f.write(json.dumps({"item_id": k[0], "pred_norm": k[1], "pred": todo[k],
                                    "gold": items[k[0]]["answer"], "logp_yes": y, "logp_no": n,
                                    "correct": y > n, "judge": JUDGE_MODEL}, ensure_ascii=False) + "\n")
            f.flush()


if __name__ == "__main__":
    main()
