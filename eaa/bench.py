"""Benchmark: EAG sigma vs standard uncertainty signals as answer gates (pre-reg: 08_..., section
"Benchmark gate vs metode standar"). Data: Qwen2.5-3B `off` outputs of Study 3 (= Study 2 extractive).

  python -m eaa.bench score      # seq_conf, p_true, self_consistency, reader_p_suff -> 07_analysis/bench/scores.csv
  python -m eaa.bench analyze    # AURC (answered), AUROC, coverage-matched gates
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from . import prompts as P
from .data import load_items
from .evaluate import normalize_answer

REP = Path("07_analysis/bench")
S3 = Path("07_analysis/study3/qwen2.5-3b/eval.csv")
PACKETS = Path("01_data/study3_packets.jsonl")
MODEL = "03_models/Qwen2.5-3B-Instruct"
ITEMS = Path("01_data/hotpot_dev_study2_n400_seed20261006.jsonl")
SEED = 20261011
N_SAMPLES, TEMP, TOP_P = 5, 0.7, 0.95

PTRUE = ("Evidence:\n{evidence}\n\nQuestion: {question}\nProposed answer: {answer}\n\n"
         "Is the proposed answer correct and supported by the evidence? Answer True or False.\nAnswer:")


def _evidence(prompt: str) -> str:
    a = prompt.find("Evidence:\n") + len("Evidence:\n")
    return prompt[a:prompt.rfind("\n\nQuestion: ")]


def score(batch_size: int):
    import torch
    from tqdm import tqdm

    from .backends import HFBackend
    from .run import READER_OPTIONS, READER_PREFIX, _msgs

    ev = pd.read_csv(S3)
    # Only substantive primary answers: a gate can only withhold an answer that was given, so
    # scores for abstained rows never change any metric (they stay abstained under every gate).
    off = ev[(ev.arm == "off") & (ev.primary == 1) & (ev.answered == 1)].reset_index(drop=True)
    pk ={(r["item_id"], r["level"], r["policy"]): r["prompt"] for r in map(json.loads, open(PACKETS, encoding="utf-8"))}
    q = {it["id"]: it["question"] for it in load_items(ITEMS)}
    be = HFBackend(MODEL)
    tok, model = be.tok, be.model
    rows = []
    torch.manual_seed(SEED)
    for i in tqdm(range(0, len(off), batch_size), desc="bench"):
        chunk = off.iloc[i:i + batch_size]
        msgs = [_msgs(pk[(r.item_id, r.level, r.policy)]) for r in chunk.itertuples()]
        answers = [str(a) if isinstance(a, str) else "" for a in chunk.output]
        # 1) sequence confidence: mean log-prob of the greedy answer tokens
        seq = []
        for m, a in zip(msgs, answers):
            if not a:
                seq.append(np.nan)
                continue
            lp = be.score_continuations([m], "", [a])[0][0]
            n = max(len(tok(a, add_special_tokens=False)["input_ids"]), 1)
            seq.append(lp / n)
        # 2) P(True) with evidence in context
        pt = []
        for r, a in zip(chunk.itertuples(), answers):
            m = _msgs(PTRUE.format(evidence=_evidence(pk[(r.item_id, r.level, r.policy)]),
                                   question=q[r.item_id], answer=a or "(no answer)"))
            t, f = be.score_continuations([m], "", ["True", "False"])[0]
            pt.append(1 / (1 + np.exp(f - t)))
        # 3) self-consistency: agreement of samples with the greedy answer
        texts = [be._render(m) for m in msgs]
        enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
        with torch.inference_mode():
            out = model.generate(**enc, max_new_tokens=24, do_sample=True, temperature=TEMP, top_p=TOP_P,
                                 num_return_sequences=N_SAMPLES, pad_token_id=tok.pad_token_id)
        dec = tok.batch_decode(out[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
        sc = []
        for k, a in enumerate(answers):
            samp = [normalize_answer(s) for s in dec[k * N_SAMPLES:(k + 1) * N_SAMPLES]]
            sc.append(np.mean([s == normalize_answer(a) for s in samp]))
        # 4) prompt reader P(SUFFICIENT)
        rd = []
        for r in chunk.itertuples():
            m = _msgs(P.READER.format(evidence=_evidence(pk[(r.item_id, r.level, r.policy)]), question=q[r.item_id]))
            s_, i_ = be.score_continuations([m], READER_PREFIX, READER_OPTIONS)[0]
            rd.append(1 / (1 + np.exp(i_ - s_)))
        for r, a, b, c, d in zip(chunk.itertuples(), seq, pt, sc, rd):
            rows.append({"item_id": r.item_id, "level": r.level, "policy": r.policy,
                         "seq_conf": a, "p_true": b, "self_consistency": c, "reader_p_suff": d})
    REP.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(REP / "scores.csv", index=False)
    print(f"wrote {REP / 'scores.csv'}")


def analyze():
    from .eag.evaluate import aurc
    from .eag.train import auroc

    sys.stdout.reconfigure(encoding="utf-8")
    ev = pd.read_csv(S3)
    off = ev[(ev.arm == "off") & (ev.primary == 1)].reset_index(drop=True)
    sc = pd.read_csv(REP / "scores.csv")
    d = off.merge(sc, on=["item_id", "level", "policy"], how="left").rename(columns={"sigma": "eag_sigma"})
    d["oracle_full"] = (d.level == "full").astype(float) + 1e-6 * np.random.default_rng(SEED).random(len(d))
    gates = ["eag_sigma", "reader_p_suff", "p_true", "seq_conf", "self_consistency", "oracle_full"]
    ans = d[d.answered == 1].reset_index(drop=True)
    rng = np.random.default_rng(SEED)
    items = ans.item_id.unique()
    pos = {i: np.flatnonzero(ans.item_id.to_numpy() == i) for i in items}
    boots = [np.concatenate([pos[i] for i in rng.choice(items, len(items))]) for _ in range(2000)]
    err = ans.hallucination.to_numpy()
    S = {g: ans[g].fillna(-np.inf).to_numpy() for g in gates}
    pt = {g: aurc(S[g], err) for g in gates}
    rep = {g: np.array([aurc(S[g][b], err[b]) for b in boots]) for g in gates}
    t1 = pd.DataFrame([{"gate": g, "AURC": pt[g],
                        "diff_vs_eag": pt[g] - pt["eag_sigma"],
                        "diff_ci": tuple(np.round(np.percentile(rep[g] - rep["eag_sigma"], [2.5, 97.5]), 4)),
                        "AUROC(correct vs halluc)": auroc(ans.correct.to_numpy(), ans[g].fillna(-1e9).to_numpy())}
                       for g in gates])
    t1.loc[len(t1)] = {"gate": "random", "AURC": err.mean()}
    # coverage-matched gates: every score thresholded to the answer rate of the sigma<0.5 gate
    target = (d.answered * (d.eag_sigma >= 0.5)).mean()
    rows = []
    for g in gates:
        s = d[g].fillna(-np.inf).to_numpy()
        cand = np.unique(s[d.answered == 1])
        rates = np.array([(d.answered.to_numpy() * (s >= t)).mean() for t in cand])
        t = cand[np.argmin(np.abs(rates - target))]
        keep = (s >= t) & (d.answered.to_numpy() == 1)
        full = (d.level == "full").to_numpy()
        rows.append({"gate": g, "threshold": t, "answer_rate": keep.mean(),
                     "halluc": (d.hallucination.to_numpy() * keep).mean(),
                     "correct": (d.correct.to_numpy() * keep).mean(),
                     "false_refusal_full": 1 - keep[full].mean()})
    # random gate at the same answer rate: keeps a uniform share of answers (expected values)
    share = target / d.answered.mean()
    rows.append({"gate": "random (same answer rate)", "answer_rate": target,
                 "halluc": d.hallucination.mean() * share, "correct": d.correct.mean() * share,
                 "false_refusal_full": 1 - d.answered[d.level == "full"].mean() * share})
    rows.append({"gate": "no gate (off)", "answer_rate": d.answered.mean(), "halluc": d.hallucination.mean(),
                 "correct": d.correct.mean(), "false_refusal_full": 1 - d.answered[d.level == "full"].mean()})
    t2 = pd.DataFrame(rows)
    md = ["# Benchmark — EAG σ vs standard uncertainty signals (Qwen2.5-3B, Study 3 primary)\n",
          f"answered rows: {len(ans)} / {len(d)}; coverage-matched answer rate = {target:.3f}\n",
          "## AURC on substantive answers (lower = better) and AUROC\n",
          "```\n" + t1.round(4).to_string(index=False) + "\n```\n",
          "## Gates at the same answer rate as σ<0.5\n",
          "```\n" + t2.round(4).to_string(index=False) + "\n```\n"]
    REP.mkdir(parents=True, exist_ok=True)
    t1.to_csv(REP / "aurc.csv", index=False)
    t2.to_csv(REP / "matched_gates.csv", index=False)
    (REP / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["score", "analyze"])
    ap.add_argument("--batch-size", type=int, default=4)
    a = ap.parse_args()
    score(a.batch_size) if a.mode == "score" else analyze()


if __name__ == "__main__":
    main()
