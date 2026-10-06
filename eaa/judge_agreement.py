"""Agreement between the LLM judge (06_evaluation/judge_cache.jsonl) and the Claude audit
(06_evaluation/audit_ambiguous_claude.jsonl) on the pilot's ambiguous cases."""
from __future__ import annotations

import json
from pathlib import Path

from .judge import JUDGE_CACHE, load_cache


def main():
    judge = load_cache(JUDGE_CACHE, "judge")
    audit = {(r["item_id"], r["pred_norm"]): r["correct"]
             for r in map(json.loads, open("06_evaluation/audit_ambiguous_claude.jsonl", encoding="utf-8"))}
    both = [k for k in audit if k in judge]
    if not both:
        print("no overlap")
        return
    tp = sum(audit[k] and judge[k] for k in both)
    tn = sum((not audit[k]) and (not judge[k]) for k in both)
    fp = sum((not audit[k]) and judge[k] for k in both)
    fn = sum(audit[k] and (not judge[k]) for k in both)
    n = len(both)
    po = (tp + tn) / n
    pa, pj = (tp + fn) / n, (tp + fp) / n
    pe = pa * pj + (1 - pa) * (1 - pj)
    kappa = (po - pe) / (1 - pe) if pe < 1 else float("nan")
    res = {"n": n, "agreement": round(po, 4), "cohen_kappa": round(kappa, 4),
           "judge_yes_audit_no": fp, "judge_no_audit_yes": fn,
           "audit_correct_rate": round(pa, 4), "judge_correct_rate": round(pj, 4)}
    print(json.dumps(res))
    Path("06_evaluation/judge_agreement.json").write_text(json.dumps(res, indent=2))
    dis = [{"item_id": k[0], "pred_norm": k[1], "audit": audit[k], "judge": judge[k]}
           for k in both if audit[k] != judge[k]]
    Path("06_evaluation/judge_disagreements.json").write_text(json.dumps(dis, indent=2, ensure_ascii=False),
                                                             encoding="utf-8")


if __name__ == "__main__":
    main()
