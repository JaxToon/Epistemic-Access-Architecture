"""Per-item labelling (v0.2).

Response classes (mutually exclusive):
  abstain       starts with the instructed abstain token ("INSUFFICIENT EVIDENCE", "I DON'T KNOW")
  non_answer    other refusal-like text ("the evidence does not mention ...") — audited separately
  substantive   anything else
correct        substantive and (EM, or gold contained in prediction at word boundaries;
               yes/no: first token equals gold)
hallucination  substantive and not correct
unsupported_correct  correct although the answer was not available in the delivered packet

Systems:
  closed_book, off@level, advisory@level (verdict only), advisory_missing@level,
  enforced@level         advisory, gated: reader verdict INSUFFICIENT => abstain
  enforced_score@level   advisory, gated by reader P(SUFFICIENT) < SCORE_TAU
  enforced_oracle@level  off, gated: answer not available in packet => abstain (upper bound)
  restored / restored_ctrl  two-turn; evidence in turn 2 is full
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import re
import string
from pathlib import Path

ABSTAIN_PREFIXES = ["insufficient evidence", "i don t know", "i do not know"]
NON_ANSWER_RE = re.compile(
    r"\b(?:(?:evidence|context|information|text|passage)s? (?:does not|doesn t|do not|did not)"
    r" (?:mention|provide|contain|state|specify|say|include|indicate)"
    r"|not (?:mentioned|provided|specified|stated|given|available|enough|sufficient)"
    r"|can ?not be (?:\w+ )?(?:determined|answered|found|identified)"
    r"|unable to (?:\w+ )?(?:determine|answer|find|identify)|no (?:relevant )?information|insufficient)\b"
)


def normalize_answer(s: str) -> str:
    s = s.lower()
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())


def f1_score(pred: str, gold: str) -> float:
    p, g = normalize_answer(pred).split(), normalize_answer(gold).split()
    if not p or not g:
        return float(p == g)
    common = collections.Counter(p) & collections.Counter(g)
    same = sum(common.values())
    if same == 0:
        return 0.0
    prec, rec = same / len(p), same / len(g)
    return 2 * prec * rec / (prec + rec)


def response_class(pred: str) -> str:
    n = normalize_answer(pred)
    if n == "" or any(n.startswith(p) for p in ABSTAIN_PREFIXES):
        return "abstain"
    if NON_ANSWER_RE.search(" ".join(re.sub(r"[^\w\s]", " ", pred.lower()).split())):
        return "non_answer"
    return "substantive"


def is_abstain(pred: str) -> bool:
    return response_class(pred) != "substantive"


def is_correct(pred: str, gold: str) -> bool:
    p, g = normalize_answer(pred), normalize_answer(gold)
    if not g:
        return False
    if g in {"yes", "no"}:
        return p.split()[:1] == [g]
    return p == g or f" {g} " in f" {p} "


def parse_reader(raw: str) -> tuple[str, str]:
    m = re.search(r"\{.*\}", raw, flags=re.S)
    if m:
        try:
            obj = json.loads(m.group(0))
            v = str(obj.get("verdict", "")).upper()
            if v in {"SUFFICIENT", "INSUFFICIENT"}:
                return v, str(obj.get("missing", "") or "")
        except json.JSONDecodeError:
            pass
    up = raw.upper()
    if "INSUFFICIENT" in up:
        return "INSUFFICIENT", ""
    if "SUFFICIENT" in up:
        return "SUFFICIENT", ""
    return "PARSE_ERROR", ""


def label(pred: str, gold: str) -> dict:
    cls = response_class(pred)
    sub = cls == "substantive"
    correct = sub and is_correct(pred, gold)
    return {
        "response_class": cls,
        "abstain": int(not sub),            # abstain or non_answer (withheld)
        "answered": int(sub),
        "em": float(normalize_answer(pred) == normalize_answer(gold)),
        "f1": f1_score(pred, gold),
        "correct": int(correct),
        "hallucination": int(sub and not correct),
        "verbose": int(len(normalize_answer(pred).split()) > len(normalize_answer(gold).split()) + 8),
    }


def _leak(text: str, gold: str) -> int:
    g = normalize_answer(gold)
    if not text.strip() or g in {"", "yes", "no"}:
        return 0
    return int(f" {g} " in f" {normalize_answer(text)} " or f1_score(text, gold) >= 0.5)


GATED = "INSUFFICIENT EVIDENCE"
SCORE_TAU = 0.5   # pre-registered threshold for enforced_score; full risk-coverage curve also reported


def evaluate(run_dir: Path, items_path: Path) -> Path:
    import pandas as pd

    from .data import load_items

    gold = {it["id"]: it["answer"] for it in load_items(items_path)}
    recs = {}
    with open(run_dir / "generations.jsonl", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            recs[r["key"]] = r
    packets = {}
    with open(run_dir / "packets.jsonl", encoding="utf-8") as f:
        for line in f:
            p = json.loads(line)
            packets[(p["item_id"], p["level"])] = p
    qclass = {iid: p["qclass"] for (iid, _), p in packets.items()}
    apd = {iid: p["answer_para_defined"] for (iid, _), p in packets.items()}

    def available(p) -> int:
        if p["answer_in_packet"] is None:          # yes/no: needs both paragraphs
            return int(p["level"] == "full")
        return int(p["answer_in_packet"])

    rows = []
    for (iid, lv), p in packets.items():
        g = gold[iid]
        base = {"item_id": iid, "level": lv, "gold_kept_frac": p["gold_kept_frac"],
                "answer_available": available(p), "len_ratio_vs_full": p["len_ratio_vs_full"]}
        rd = recs.get(f"{iid}|reader|{lv}")
        verdict, missing = parse_reader(rd["output"]) if rd else ("MISSING", "")
        base.update(reader_verdict=verdict, reader_missing_leak=_leak(missing, g))
        rsc = recs.get(f"{iid}|reader_score|{lv}")
        if rsc:
            lp = json.loads(rsc["output"])
            base["reader_p_suff"] = 1 / (1 + math.exp(lp["INSUFFICIENT"] - lp["SUFFICIENT"]))

        def add(system, out, ptok):
            rows.append({**base, "system": system, "prompt_tokens": ptok, "output": out, **label(out, g)})

        off = recs.get(f"{iid}|off|{lv}")
        if off:
            add("off", off["output"], off["prompt_tokens"])
            add("enforced_oracle", off["output"] if base["answer_available"] else GATED,
                off["prompt_tokens"])
        adv = recs.get(f"{iid}|advisory|{lv}")
        if adv:
            add("advisory", adv["output"], adv["prompt_tokens"])
            add("enforced", GATED if verdict == "INSUFFICIENT" else adv["output"], adv["prompt_tokens"])
            if "reader_p_suff" in base:
                add("enforced_score", adv["output"] if base["reader_p_suff"] >= SCORE_TAU else GATED,
                    adv["prompt_tokens"])
        advm = recs.get(f"{iid}|advisory_missing|{lv}")
        if advm:
            add("advisory_missing", advm["output"], advm["prompt_tokens"])

    for r in recs.values():
        iid = r["item_id"]
        if r["task"] == "closed_book":
            rows.append({"item_id": iid, "system": "closed_book", "level": None,
                         "prompt_tokens": r["prompt_tokens"], "output": r["output"],
                         **label(r["output"], gold[iid])})
        elif r["task"] in {"restored", "restored_ctrl"}:
            t1 = recs.get(f"{iid}|off|{r['level']}")
            t1_lab = label(t1["output"], gold[iid]) if t1 else {}
            t1_status = ("correct" if t1_lab.get("correct") else
                         "hallucination" if t1_lab.get("hallucination") else "abstain")
            rows.append({"item_id": iid, "system": r["task"], "level": "full",
                         "turn1_level": r["level"], "turn1_status": t1_status,
                         "gold_kept_frac": 1.0,
                         "answer_available": available(packets[(iid, "full")]),
                         "prompt_tokens": r["prompt_tokens"], "output": r["output"],
                         **label(r["output"], gold[iid])})

    df = pd.DataFrame(rows)
    df["qclass"] = df["item_id"].map(qclass)
    df["answer_para_defined"] = df["item_id"].map(apd)
    cb = df[df["system"] == "closed_book"].set_index("item_id")["correct"]
    df["param_known"] = df["item_id"].map(cb).fillna(0).astype(int)
    df.loc[df["qclass"] == "yesno", "param_known"] = 0   # 50% guess rate: not evidence of knowledge
    df["unsupported_correct"] = ((df["correct"] == 1) & (df["answer_available"] == 0)
                                 & (df["system"] != "closed_book")).astype(int)
    # primary analysis population (pre-registered)
    df["primary"] = ((df["qclass"] == "open") & (df["answer_para_defined"] == True)).astype(int)

    out_dir = Path(str(run_dir).replace("05_outputs", "06_evaluation"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "eval.csv"
    df.to_csv(out, index=False)
    return out


def main():
    import yaml

    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--run-name", default=None)
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config, encoding="utf-8"))
    run_dir = Path(cfg["output_root"]) / (args.run_name or cfg["run_name"])
    out = evaluate(run_dir, Path(cfg["items_path"]))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
