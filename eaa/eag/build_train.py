"""Build counterfactual training packets from HotpotQA *train* (never dev; the pilot sample is dev).

Output jsonl rows: {item_id, split, level, label, qclass, prompt (user message), answer_para_defined}
label: full -> 1 (sufficient by construction); partial packets -> answer string present in packet.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from .. import prompts as P
from ..conditions import LEVELS, plan_item, question_class, render_units
from ..data import _to_item


def available(plan, level: str) -> int:
    """`full` delivers both gold paragraphs, sufficient by HotpotQA construction even when the
    answer is not verbatim in the text; partial packets: answer string must have crossed the
    channel (yes/no answers cannot be checked -> 0)."""
    if level == "full":
        return 1
    return int(plan.answer_in_packet(level) or 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", nargs="+", default=["01_data/raw/hotpot_qa_distractor_train_0.parquet",
                                                 "01_data/raw/hotpot_qa_distractor_train_1.parquet"])
    ap.add_argument("--n-train", type=int, default=6000)
    ap.add_argument("--n-val", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=20261005)
    ap.add_argument("--tokenizer", default="03_models/Qwen2.5-3B-Instruct")
    ap.add_argument("--out", default="01_data/eag_train_packets.jsonl")
    args = ap.parse_args()

    import pandas as pd
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(args.tokenizer)
    count = lambda s: len(tok(s, add_special_tokens=False)["input_ids"])

    df = pd.concat([pd.read_parquet(p) for p in args.raw], ignore_index=True)
    ids = sorted(df["id"].tolist())
    rng = random.Random(args.seed)
    chosen = rng.sample(ids, args.n_train + args.n_val)
    split = {i: ("train" if k < args.n_train else "val") for k, i in enumerate(chosen)}
    rows = df[df["id"].isin(split)]

    n_ok = 0
    with open(args.out, "w", encoding="utf-8") as f:
        for _, r in rows.iterrows():
            it = _to_item(r)
            plan = plan_item(it, args.seed, 4, count)
            if plan is None:
                continue
            n_ok += 1
            for lv in LEVELS:
                ev = render_units(plan.packet(lv))
                f.write(json.dumps({
                    "item_id": it["id"], "split": split[it["id"]], "level": lv,
                    "label": available(plan, lv), "qclass": question_class(it),
                    "answer_para_defined": plan.answer_para_defined,
                    "prompt": P.GENERATOR.format(evidence=ev, advisory="", question=it["question"]),
                }, ensure_ascii=False) + "\n")
    print(f"items ok={n_ok} -> {args.out}")


if __name__ == "__main__":
    main()
