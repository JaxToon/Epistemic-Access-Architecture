"""Phase 1b — internal vs external knowledge (plan: 00_docs/14_analysis_plan_phase1b_probe.md).

  python -m eaa.probe_knowledge extract   GPU: greedy + 10 samples + gold per item (`full`), teacher-
                                          forced mean log-prob and last-token hidden states
  python -m eaa.probe_knowledge analyze   cross-fitted probe (internal) vs log-prob (external) vs
                                          surface features; K (Gekhman-style) and gold-vs-greedy

The probe is trained on model-generated candidates only; gold strings are scored but never trained on.
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
from .evaluate import normalize_answer, response_class

ITEMS = Path("01_data/hotpot_dev_study2_n400_seed20261006.jsonl")
S2_DIR = Path("05_outputs/study2_qwen2.5-3b")
PACKETS = Path("01_data/study3_packets.jsonl")
EVAL = Path("07_analysis/study3/qwen2.5-3b/eval.csv")
MODEL = "03_models/Qwen2.5-3B-Instruct"
OUT = Path("07_analysis/diagnosis")
LAYERS = [18, 27, 33, 36]
PRIMARY_LAYER = 27
N_SAMPLES = 10
SEED = 20261017
B = 2000


def _msgs(user: str) -> list[dict]:
    return [{"role": "system", "content": P.SYSTEM}, {"role": "user", "content": user}]


def _in_evidence(prompt: str, cand: str) -> int:
    ev = prompt[prompt.find("Evidence:"):prompt.rfind("Question: ")]
    c = normalize_answer(cand)
    return int(bool(c) and f" {c} " in f" {normalize_answer(ev)} ")


def extract():
    import torch
    from tqdm import tqdm
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.manual_seed(SEED)
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float16, device_map="cuda").eval()
    body, head = model.model, model.lm_head
    items = {it["id"]: it for it in load_items(ITEMS)}
    off = {r["item_id"]: r["output"] for r in map(json.loads, open(S2_DIR / "generations.jsonl", encoding="utf-8"))
           if r["prompt"] == "extractive" and r["level"] == "full"}
    pk = [r for r in map(json.loads, open(PACKETS, encoding="utf-8")) if r["level"] == "full"]

    meta, H = [], []
    for r in tqdm(pk, desc="items"):
        iid, user = r["item_id"], r["prompt"]
        text = tok.apply_chat_template(_msgs(user), tokenize=False, add_generation_prompt=True)
        p_ids = tok(text, add_special_tokens=False)["input_ids"]
        with torch.inference_mode():
            g = model.generate(torch.tensor([p_ids], device="cuda"), attention_mask=torch.ones(1, len(p_ids), dtype=torch.long, device="cuda"),
                               do_sample=True, temperature=1.0, top_p=1.0, top_k=0, max_new_tokens=24,
                               num_return_sequences=N_SAMPLES, pad_token_id=tok.pad_token_id or tok.eos_token_id)
        samples = [s.strip() for s in tok.batch_decode(g[:, len(p_ids):], skip_special_tokens=True)]
        cands, seen = [], set()
        for c, kind in [(off[iid], "greedy")] + [(s, "sample") for s in samples]:
            n = normalize_answer(c)
            if response_class(c) != "substantive" or n in seen:
                continue
            seen.add(n)
            cands.append((c, kind))
        cands.append((items[iid]["answer"], "gold"))
        for i in range(0, len(cands), 4):
            chunk = cands[i:i + 4]
            c_ids = [tok(c, add_special_tokens=False)["input_ids"] for c, _ in chunk]
            L = max(len(p_ids) + len(c) for c in c_ids)
            ids = torch.full((len(chunk), L), tok.pad_token_id or 0, dtype=torch.long)
            att = torch.zeros((len(chunk), L), dtype=torch.long)
            for b, c in enumerate(c_ids):
                ids[b, : len(p_ids) + len(c)] = torch.tensor(p_ids + c)
                att[b, : len(p_ids) + len(c)] = 1
            with torch.inference_mode():
                out = body(input_ids=ids.cuda(), attention_mask=att.cuda(), output_hidden_states=True)
                hs = out.hidden_states
                for b, ((c, kind), ci) in enumerate(zip(chunk, c_ids)):
                    t0, last = len(p_ids) - 1, len(p_ids) + len(ci) - 1
                    pos = torch.arange(t0, last, device="cuda")
                    lp = torch.log_softmax(head(hs[-1][b, pos]).float(), -1)
                    tl = lp[torch.arange(len(ci)), torch.tensor(ci, device="cuda")]
                    H.append(torch.stack([hs[l][b, last] for l in LAYERS]).half().cpu())
                    meta.append({"item_id": iid, "cand": c, "kind": kind, "lp_mean": float(tl.mean()),
                                 "ntok": len(ci), "in_evidence": _in_evidence(user, c)})
            del out, hs
    OUT.mkdir(parents=True, exist_ok=True)
    torch.save({"meta": meta, "H": torch.stack(H), "layers": LAYERS}, OUT / "probe_candidates.pt")
    print(f"{len(meta)} candidates from {len(pk)} items -> {OUT / 'probe_candidates.pt'}")


def decoy():
    """Gold answer of ANOTHER item (same numeric/non-numeric type): gold-styled but wrong."""
    import torch
    from tqdm import tqdm
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float16, device_map="cuda").eval()
    body, head = model.model, model.lm_head
    items = {it["id"]: it for it in load_items(ITEMS)}
    pk = [r for r in map(json.loads, open(PACKETS, encoding="utf-8")) if r["level"] == "full"]
    rng = np.random.default_rng(SEED + 1)
    numeric = lambda a: any(ch.isdigit() for ch in a)
    pool = {True: [i for i, it in items.items() if numeric(it["answer"])],
            False: [i for i, it in items.items() if not numeric(it["answer"])]}
    meta, H = [], []
    for r in tqdm(pk, desc="decoys"):
        iid, user = r["item_id"], r["prompt"]
        gold = items[iid]["answer"]
        cand = [j for j in pool[numeric(gold)] if j != iid
                and normalize_answer(items[j]["answer"]) != normalize_answer(gold)
                and normalize_answer(items[j]["answer"]) not in {"yes", "no"}]
        c = items[cand[rng.integers(len(cand))]]["answer"]
        text = tok.apply_chat_template(_msgs(user), tokenize=False, add_generation_prompt=True)
        p_ids = tok(text, add_special_tokens=False)["input_ids"]
        ci = tok(c, add_special_tokens=False)["input_ids"]
        with torch.inference_mode():
            hs = body(input_ids=torch.tensor([p_ids + ci], device="cuda"), output_hidden_states=True).hidden_states
            t0, last = len(p_ids) - 1, len(p_ids) + len(ci) - 1
            lp = torch.log_softmax(head(hs[-1][0, t0:last]).float(), -1)
            tl = lp[torch.arange(len(ci)), torch.tensor(ci, device="cuda")]
            H.append(torch.stack([hs[l][0, last] for l in LAYERS]).half().cpu())
        meta.append({"item_id": iid, "cand": c, "kind": "decoy", "lp_mean": float(tl.mean()),
                     "ntok": len(ci), "in_evidence": _in_evidence(user, c)})
    torch.save({"meta": meta, "H": torch.stack(H), "layers": LAYERS}, OUT / "probe_decoys.pt")
    print(f"{len(meta)} decoys -> {OUT / 'probe_decoys.pt'}")


def _wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def _crossfit(X, y, groups, train_mask, seed=SEED):
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    score = np.full(len(y), np.nan)
    ug = np.unique(groups)
    rng = np.random.default_rng(seed)
    fold_of = dict(zip(rng.permutation(ug), np.arange(len(ug)) % 5))
    fold = np.array([fold_of[g] for g in groups])
    for k in range(5):
        tr = train_mask & (fold != k)
        te = fold == k
        clf = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000))
        clf.fit(X[tr], y[tr])
        score[te] = clf.decision_function(X[te])
    return score


def analyze():
    import torch

    from . import evaluate as E
    from .judge import load_cache

    sys.stdout.reconfigure(encoding="utf-8")
    E.JUDGED.clear()
    E.JUDGED.update(load_cache())
    rng = np.random.default_rng(SEED)
    items = {it["id"]: it for it in load_items(ITEMS)}
    d = torch.load(OUT / "probe_candidates.pt", weights_only=False)
    M = pd.DataFrame(d["meta"])
    Hs = d["H"].float().numpy()
    if (OUT / "probe_decoys.pt").exists():
        dd = torch.load(OUT / "probe_decoys.pt", weights_only=False)
        M = pd.concat([M, pd.DataFrame(dd["meta"])], ignore_index=True)
        Hs = np.concatenate([Hs, dd["H"].float().numpy()])
    lab = [{"correct": 1, "judge_missing": 0} if k == "gold" else {"correct": 0, "judge_missing": 0} if k == "decoy"
           else E.label(c, items[i]["answer"], i) for i, c, k in zip(M.item_id, M.cand, M.kind)]
    M["y"] = [l["correct"] for l in lab]
    M["judge_missing"] = [l["judge_missing"] for l in lab]
    keep = (M.judge_missing == 0).to_numpy()
    M, Hs = M[keep].reset_index(drop=True), Hs[keep]
    ev = pd.read_csv(EVAL)
    off = ev[(ev.arm == "off") & (ev.level == "full")].set_index("item_id")
    M["primary"] = M.item_id.map(off.primary).fillna(0).astype(int)
    M["group"] = M.item_id.map(lambda i: "correct" if off.loc[i, "correct"] == 1 else
                               "halluc" if off.loc[i, "hallucination"] == 1 else "abstain")
    gen = M.kind.isin(["greedy", "sample"]).to_numpy()     # train only on model-generated candidates
    y, groups = M.y.to_numpy(), M.item_id.to_numpy()

    for l in d["layers"]:
        M[f"int_L{l}"] = _crossfit(Hs[:, d["layers"].index(l)], y, groups, gen)
    Xs = np.c_[M.ntok, M.lp_mean, M.in_evidence].astype(float)
    M["surface"] = _crossfit(Xs, y, groups, gen)
    M["external"] = M.lp_mean
    scorers = [f"int_L{PRIMARY_LAYER}", "external", "surface"] + [f"int_L{l}" for l in d["layers"] if l != PRIMARY_LAYER]

    # ---- test 1: K (pairs among model-generated candidates)
    P_ = M[gen & (M.primary == 1).to_numpy()]
    elig = [i for i, g in P_.groupby("item_id") if g.y.nunique() == 2]

    def K(g, col):
        pos, neg = g[g.y == 1][col].to_numpy(), g[g.y == 0][col].to_numpy()
        return ((pos[:, None] > neg[None, :]) + 0.5 * (pos[:, None] == neg[None, :])).mean()
    Kt = pd.DataFrame({c: [K(P_[P_.item_id == i], c) for i in elig] for c in scorers}, index=elig)
    lines = [f"Item dengan kandidat buatan model benar & salah: {len(elig)}"]
    for c in scorers:
        lines.append(f"K[{c}] = {Kt[c].mean():.3f}")
    for a, b in [(f"int_L{PRIMARY_LAYER}", "external"), (f"int_L{PRIMARY_LAYER}", "surface"), ("surface", "external")]:
        dif = (Kt[a] - Kt[b]).to_numpy()
        reps = [dif[rng.integers(0, len(dif), len(dif))].mean() for _ in range(B)]
        lo, hi = np.percentile(reps, [2.5, 97.5])
        lines.append(f"K[{a}] − K[{b}] = {dif.mean():+.3f}  [95%: {lo:+.3f}; {hi:+.3f}]")

    # ---- test 2: gold vs greedy on hallucination items; reference on correct items
    t2 = []
    Hh = M[(M.primary == 1) & (M.group == "halluc")]
    rows = []
    for i, g in Hh.groupby("item_id"):
        gd, gr = g[g.kind == "gold"], g[g.kind == "greedy"]
        if len(gd) and len(gr):
            rows.append({"item_id": i, **{c: float(gd[c].iloc[0] > gr[c].iloc[0]) for c in scorers}})
    T2 = pd.DataFrame(rows)
    for c in scorers:
        k, n = int(T2[c].sum()), len(T2)
        lo, hi = _wilson(k, n)
        t2.append(f"halusinasi: skor[{c}](emas) > skor(greedy salah): {k}/{n} = {k / n:.3f} [{lo:.3f}; {hi:.3f}]")
    # decoy control (pre-specified addition): gold of another item vs wrong greedy
    if (M.kind == "decoy").any():
        drows = []
        for i, g in Hh.groupby("item_id"):
            dc, gr = g[g.kind == "decoy"], g[g.kind == "greedy"]
            if len(dc) and len(gr):
                drows.append({"item_id": i, **{c: float(dc[c].iloc[0] > gr[c].iloc[0]) for c in scorers}})
        TD = pd.DataFrame(drows).set_index("item_id")
        for c in scorers:
            k, n = int(TD[c].sum()), len(TD)
            lo, hi = _wilson(k, n)
            t2.append(f"KONTROL decoy: skor[{c}](emas soal lain) > skor(greedy salah): {k}/{n} = {k / n:.3f} [{lo:.3f}; {hi:.3f}]")
        c = f"int_L{PRIMARY_LAYER}"
        both = T2.set_index("item_id").index.intersection(TD.index)
        dif = T2.set_index("item_id").loc[both, c].to_numpy() - TD.loc[both, c].to_numpy()
        reps = [dif[rng.integers(0, len(dif), len(dif))].mean() for _ in range(B)]
        lo, hi = np.percentile(reps, [2.5, 97.5])
        t2.append(f"emas − decoy (proporsi menang atas greedy, {c}): {dif.mean():+.3f} [95%: {lo:+.3f}; {hi:+.3f}], n={len(dif)}")
    ref = []
    Cc = M[(M.primary == 1) & (M.group == "correct") & gen]
    for i, g in Cc.groupby("item_id"):
        gr, wr = g[g.kind == "greedy"], g[(g.kind == "sample") & (g.y == 0)]
        if len(gr) and len(wr):
            ref.append({c: float((gr[c].iloc[0] > wr[c]).mean()) for c in scorers})
    R = pd.DataFrame(ref)
    t2.append(f"acuan (kelompok benar, n={len(R)}): skor(greedy benar) > skor(sampel salah), rata-rata: " +
              ", ".join(f"{c} {R[c].mean():.3f}" for c in scorers))

    # ---- test 3: cross with Phase 1 K1_loose
    hc = pd.read_csv(OUT / "halluc_cases.csv")[["item_id", "K1_loose", "etype"]]
    T3 = T2.merge(hc, on="item_id")
    ct = pd.crosstab(T3[f"int_L{PRIMARY_LAYER}"].map({1.0: "probe: emas>greedy", 0.0: "probe: greedy>=emas"}),
                     T3.K1_loose.map({1: "R_final<=5", 0: "R_final>5"}), margins=True)
    ct2 = pd.crosstab(T3.etype, T3[f"int_L{PRIMARY_LAYER}"], margins=True)

    cnt = M.groupby("kind").agg(n=("y", "size"), benar=("y", "mean"))
    md = ["# Fase 1b — pengetahuan internal vs eksternal (eksploratif)\n",
          "Rencana: `00_docs/14_analysis_plan_phase1b_probe.md`. Qwen2.5-3B, `full`. Probe dilatih hanya pada "
          "kandidat buatan model (cross-fit 5 lipatan per item); emas tidak pernah dilatih.\n",
          f"Kandidat (setelah membuang ambigu yang belum dinilai: {int((~keep).sum())}):\n```\n" + cnt.round(3).to_string() + "\n```\n",
          "## Uji 1 — K (Gekhman), populasi utama\n```\n" + "\n".join(lines) + "\n```\n",
          "## Uji 2 — kasus halusinasi: emas vs jawaban greedy\n```\n" + "\n".join(t2) + "\n```\n",
          "## Uji 3 — silang dengan Fase 1\n```\n" + ct.to_string() + "\n```\n",
          "Jenis kesalahan × probe(emas > greedy):\n```\n" + ct2.to_string() + "\n```\n"]
    M.drop(columns=[]).to_csv(OUT / "probe_scores.csv", index=False)
    (OUT / "probe_summary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["extract", "decoy", "analyze"])
    a = ap.parse_args()
    {"extract": extract, "decoy": decoy, "analyze": analyze}[a.mode]()


if __name__ == "__main__":
    main()
