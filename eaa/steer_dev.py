"""Plan 18 §C — steering pilot on the Study 4 *dev* items (Study 2/3 items; Qwen2.5-3B).

  python -m eaa.steer_dev hidden                 t0 hidden states of `full` prompts (layers 18/21/24/27)
  python -m eaa.steer_dev grid                   L x alpha grid, cross-fitted directions (2 folds by item)
  python -m eaa.judge --config configs/pilot_v0.1.yaml --extra 05_outputs/steer_dev_qwen2.5-3b/generations.jsonl
  python -m eaa.steer_dev analyze                recovered / damaged / Δhalluc@drop_ans, selection criterion
  python -m eaa.steer_dev random --layer L --alpha A   random-direction control at the selected config

Direction for fold k: mean h_L(t0 | full correct) − mean h_L(t0 | full hallucination), computed on the
OTHER fold only. The vector α·v is added to the output of decoder layer L at every position.
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

ITEMS = Path("01_data/hotpot_dev_study2_n400_seed20261006.jsonl")
S2_DIR = Path("05_outputs/study2_qwen2.5-3b")
PACKETS = Path("01_data/study3_packets.jsonl")
SIGMA = Path("07_analysis/study3/sigma.csv")
MODEL = "03_models/Qwen2.5-3B-Instruct"
OUT = Path("05_outputs/steer_dev_qwen2.5-3b")
REP = Path("07_analysis/steer_dev")
LAYERS = [18, 21, 24, 27]
ALPHAS = [0.5, 1.0, 2.0, 4.0]
REL = [0.025, 0.05, 0.1, 0.2]          # plan 19: ‖α·v‖ / mean ‖h_L‖
CONDS = [("full", "length"), ("drop_ans", "entity_poor")]
SEED = 20261017
MAX_DROP_HALLUC = 0.02


def _msgs(user: str) -> list[dict]:
    return [{"role": "system", "content": P.SYSTEM}, {"role": "user", "content": user}]


def _base():
    """Primary items, fold assignment, off outputs + labels (same labelling as all studies)."""
    from . import evaluate as E
    from .conditions import question_class
    from .judge import load_cache

    E.JUDGED.clear()
    E.JUDGED.update(load_cache())
    items = {it["id"]: it for it in load_items(ITEMS)}
    s2pk = {(r["item_id"], r["level"], r["policy"]): r
            for r in map(json.loads, open(S2_DIR / "packets.jsonl", encoding="utf-8"))}
    prim = sorted(i for i in items if (i, "full", "length") in s2pk and question_class(items[i]) == "open"
                  and s2pk[(i, "full", "length")]["answer_para_defined"])
    rng = np.random.default_rng(SEED)
    fold = {i: int(k) for i, k in zip(rng.permutation(prim), np.arange(len(prim)) % 2)}
    off = {(r["item_id"], r["level"], r["policy"]): r["output"]
           for r in map(json.loads, open(S2_DIR / "generations.jsonl", encoding="utf-8")) if r["prompt"] == "extractive"}
    lab = {k: E.label(str(o), items[k[0]]["answer"], k[0]) for k, o in off.items() if k[0] in fold}
    pk = {(r["item_id"], r["level"], r["policy"]): r["prompt"] for r in map(json.loads, open(PACKETS, encoding="utf-8"))}
    return items, prim, fold, off, lab, pk


def _load():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(MODEL, padding_side="left")
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float16, device_map="cuda").eval()
    return tok, model


def hidden(level: str = "full", policy: str = "length", fname: str = "t0_hidden.pt"):
    import torch
    from tqdm import tqdm

    items, prim, fold, off, lab, pk = _base()
    tok, model = _load()
    H = {}
    for i in tqdm(prim, desc=f"t0 hidden {level}"):
        text = tok.apply_chat_template(_msgs(pk[(i, level, policy)]), tokenize=False, add_generation_prompt=True)
        ids = tok(text, return_tensors="pt", add_special_tokens=False).to("cuda")
        with torch.inference_mode():
            hs = model.model(**ids, output_hidden_states=True).hidden_states
        H[i] = torch.stack([hs[l][0, -1] for l in LAYERS]).float().cpu()
    OUT.mkdir(parents=True, exist_ok=True)
    torch.save({"H": H, "layers": LAYERS}, OUT / fname)
    print(f"saved {len(H)} -> {OUT / fname}")


def _directions():
    import torch

    items, prim, fold, off, lab, pk = _base()
    H = torch.load(OUT / "t0_hidden.pt", weights_only=False)["H"]
    V = {}
    for k in (0, 1):
        other = [i for i in prim if fold[i] != k]
        cor = [i for i in other if lab[(i, "full", "length")]["correct"] == 1]
        hal = [i for i in other if lab[(i, "full", "length")]["hallucination"] == 1]
        diff = torch.stack([H[i] for i in cor]).mean(0) - torch.stack([H[i] for i in hal]).mean(0)
        for li, L in enumerate(LAYERS):
            V[(L, k)] = diff[li]
    return V


def _within():
    """Plan 19: mean over OTHER-fold items of h(full) − h(drop_ans) for the same item; plus mean ‖h‖."""
    import torch

    items, prim, fold, off, lab, pk = _base()
    Hf = torch.load(OUT / "t0_hidden.pt", weights_only=False)["H"]
    Hd = torch.load(OUT / "t0_hidden_dropans.pt", weights_only=False)["H"]
    hn = torch.stack([Hf[i] for i in prim]).norm(dim=-1).mean(0)
    V = {}
    for k in (0, 1):
        other = [i for i in prim if fold[i] != k]
        diff = torch.stack([Hf[i] - Hd[i] for i in other]).mean(0)
        for li, L in enumerate(LAYERS):
            V[(L, k)] = diff[li]
    return V, {L: float(hn[li]) for li, L in enumerate(LAYERS)}


def grid_within():
    import torch

    V, hn = _within()
    for L in LAYERS:
        c = float(torch.nn.functional.cosine_similarity(V[(L, 0)], V[(L, 1)], dim=0))
        print(f"L{L}: |v|/|h| = {float(V[(L, 0)].norm()) / hn[L]:.3f}, kosinus antar lipatan = {c:.3f}")
    cfgs = [(f"W_L{L}_r{r:g}", L, 1.0, {k: V[(L, k)] / V[(L, k)].norm() * r * hn[L] for k in (0, 1)})
            for L in LAYERS for r in REL]
    _generate(cfgs, "generations.jsonl")


def random_within(layer: int, rel: float):
    import torch

    V, hn = _within()
    g = torch.Generator().manual_seed(SEED)
    vecs = {}
    for k in (0, 1):
        r = torch.randn(V[(layer, k)].shape, generator=g)
        vecs[k] = r / r.norm() * rel * hn[layer]
    _generate([(f"RAND_W_L{layer}_r{rel:g}", layer, 1.0, vecs)], "generations.jsonl")


def _generate(configs: list[tuple[str, int, float, dict]], tag_file: str):
    """configs: (name, layer, alpha, {fold: vector})."""
    import torch
    from tqdm import tqdm

    items, prim, fold, off, lab, pk = _base()
    tok, model = _load()
    gen = OUT / tag_file
    done = {json.loads(l)["key"] for l in open(gen, encoding="utf-8")} if gen.exists() else set()
    with open(gen, "a", encoding="utf-8") as f:
        for name, L, alpha, vecs in configs:
            for k in (0, 1):
                rows = [(i, lv, pol) for i in prim if fold[i] == k for lv, pol in CONDS
                        if f"{name}|{i}|{lv}|{pol}" not in done]
                if not rows:
                    continue
                delta = (alpha * vecs[k]).to("cuda", torch.float16)

                def hook(mod, inp, out):
                    if isinstance(out, tuple):
                        return (out[0] + delta,) + tuple(out[1:])
                    return out + delta
                h = model.model.layers[L - 1].register_forward_hook(hook)   # hidden_states[L] = output of layer L-1
                try:
                    texts = {r: tok.apply_chat_template(_msgs(pk[r]), tokenize=False, add_generation_prompt=True) for r in rows}
                    rows.sort(key=lambda r: len(texts[r]))
                    for b in tqdm(range(0, len(rows), 4), desc=f"{name} f{k}"):
                        chunk = rows[b:b + 4]
                        enc = tok([texts[r] for r in chunk], return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
                        with torch.inference_mode():
                            g = model.generate(**enc, max_new_tokens=24, do_sample=False, temperature=None, top_p=None,
                                               top_k=None, pad_token_id=tok.pad_token_id)
                        outs = [s.strip() for s in tok.batch_decode(g[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)]
                        for (i, lv, pol), o in zip(chunk, outs):
                            f.write(json.dumps({"key": f"{name}|{i}|{lv}|{pol}", "config": name, "layer": L, "alpha": alpha,
                                                "fold": k, "item_id": i, "level": lv, "policy": pol, "output": o},
                                               ensure_ascii=False) + "\n")
                        f.flush()
                finally:
                    h.remove()
    print(f"done -> {gen}")


def grid():
    V = _directions()
    cfgs = [(f"L{L}_a{a:g}", L, a, {k: V[(L, k)] for k in (0, 1)}) for L in LAYERS for a in ALPHAS]
    _generate(cfgs, "generations.jsonl")


def random_ctrl(layer: int, alpha: float):
    import torch

    V = _directions()
    g = torch.Generator().manual_seed(SEED)
    vecs = {}
    for k in (0, 1):
        r = torch.randn(V[(layer, k)].shape, generator=g)
        vecs[k] = r / r.norm() * V[(layer, k)].norm()
    _generate([(f"RAND_L{layer}_a{alpha:g}", layer, alpha, vecs)], "generations.jsonl")


def analyze():
    from . import evaluate as E

    sys.stdout.reconfigure(encoding="utf-8")
    items, prim, fold, off, lab, pk = _base()
    gen = pd.read_json(OUT / "generations.jsonl", lines=True)
    L_ = [E.label(str(o), items[i]["answer"], i) for i, o in zip(gen.item_id, gen.output)]
    for c in ("correct", "hallucination", "abstain", "judge_missing"):
        gen[c] = [l[c] for l in L_]
    sig = pd.read_csv(SIGMA).set_index(["item_id", "level", "policy"]).sigma
    gen["sigma"] = [sig.get((i, lv, p), np.nan) for i, lv, p in zip(gen.item_id, gen.level, gen.policy)]
    base = {k: v for k, v in lab.items()}

    def wil(k, n, z=1.96):
        if n == 0:
            return (np.nan, np.nan)
        p = k / n
        d = 1 + z * z / n
        c = (p + z * z / (2 * n)) / d
        h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return (c - h, c + h)

    probe = Path("07_analysis/diagnosis/probe_scores.csv")
    k1 = set()
    if probe.exists():
        ps = pd.read_csv(probe)
        ps = ps[(ps.group == "halluc") & (ps.primary == 1)]
        for i, g in ps.groupby("item_id"):
            gd, gr = g[g.kind == "gold"], g[g.kind == "greedy"]
            if len(gd) and len(gr) and gd["int_L27"].iloc[0] > gr["int_L27"].iloc[0]:
                k1.add(i)

    rows = []
    for name, g in gen.groupby("config"):
        F = g[g.level == "full"].set_index("item_id")
        D = g[g.level == "drop_ans"].set_index("item_id")
        for trig in ("all", "sigma"):
            def pick(df, lv, pol):
                out = {}
                for i, r in df.iterrows():
                    use = trig == "all" or (r.sigma >= 0.5)
                    out[i] = r if use else pd.Series(base[(i, lv, pol)])
                return out
            Fp, Dp = pick(F, "full", "length"), pick(D, "drop_ans", "entity_poor")
            ids = sorted(set(Fp) & set(Dp))
            b_full = {i: base[(i, "full", "length")] for i in ids}
            b_drop = {i: base[(i, "drop_ans", "entity_poor")] for i in ids}
            wrong = [i for i in ids if b_full[i]["correct"] == 0]
            hal = [i for i in ids if b_full[i]["hallucination"] == 1]
            cor = [i for i in ids if b_full[i]["correct"] == 1]
            rec = sum(Fp[i]["correct"] for i in wrong)
            rec_h = sum(Fp[i]["correct"] for i in hal)
            dam = sum(1 - Fp[i]["correct"] for i in cor)
            d_hal_drop = np.mean([Dp[i]["hallucination"] - b_drop[i]["hallucination"] for i in ids])
            d_abs = np.mean([Fp[i]["abstain"] - b_full[i]["abstain"] for i in ids])
            d_cor = np.mean([Fp[i]["correct"] - b_full[i]["correct"] for i in ids])
            hk1 = [i for i in hal if i in k1]
            hk2 = [i for i in hal if i not in k1]
            rows.append({"config": name, "trigger": trig, "n": len(ids),
                         "pulih": rec / max(len(wrong), 1), "pulih_halu": rec_h / max(len(hal), 1),
                         "rusak": dam / max(len(cor), 1), "net_benar": d_cor, "d_abstain_full": d_abs,
                         "d_halu_drop": d_hal_drop,
                         "pulih_halu_K1": (sum(Fp[i]["correct"] for i in hk1) / len(hk1)) if hk1 else np.nan,
                         "pulih_halu_nonK1": (sum(Fp[i]["correct"] for i in hk2) / len(hk2)) if hk2 else np.nan,
                         "n_K1": len(hk1), "n_nonK1": len(hk2),
                         "judge_missing": int(g.judge_missing.sum())})
    T = pd.DataFrame(rows).sort_values(["trigger", "config"])
    T["family"] = np.where(T.config.str.startswith("RAND"), "acak",
                           np.where(T.config.str.startswith("W_"), "di dalam item", "CAA lintas item"))
    REP.mkdir(parents=True, exist_ok=True)
    T.to_csv(REP / "grid.csv", index=False)
    md = ["# Pilot steering pada dev (eksploratif)\n",
          "Rencana: dokumen 18 §C (CAA lintas item) dan 19 (arah di dalam item). Qwen2.5-3B, 255 item utama; "
          "arah cross-fit 2 lipatan. Dibandingkan dengan `off`.\n",
          "```\n" + T.drop(columns=["family"]).round(3).to_string(index=False) + "\n```\n"]
    for fam in ("CAA lintas item", "di dalam item"):
        ok = T[(T.d_halu_drop <= MAX_DROP_HALLUC) & (T.family == fam)]
        if not len(ok):
            continue
        best = ok.loc[(ok.pulih - ok.rusak).idxmax()]
        md.append(f"\nTerpilih [{fam}] (maks pulih − rusak, Δhalu@drop_ans ≤ {MAX_DROP_HALLUC}): "
                  f"**{best.config} (pemicu {best.trigger})**: pulih {best.pulih:.3f}, halu→benar {best.pulih_halu:.3f}, "
                  f"rusak {best.rusak:.3f}, Δbenar {best.net_benar:+.3f}, Δhalu@drop_ans {best.d_halu_drop:+.3f}\n")
    (REP / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


def main():
    sys.stdout.reconfigure(encoding="utf-8")   # Windows console (cp1252) cannot print ‖, σ, →
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["hidden", "hidden_drop", "grid", "grid_within", "random", "random_within", "analyze"])
    ap.add_argument("--layer", type=int)
    ap.add_argument("--alpha", type=float)
    ap.add_argument("--rel", type=float)
    a = ap.parse_args()
    if a.mode == "random":
        random_ctrl(a.layer, a.alpha)
    elif a.mode == "random_within":
        random_within(a.layer, a.rel)
    elif a.mode == "hidden_drop":
        hidden("drop_ans", "entity_poor", "t0_hidden_dropans.pt")
    else:
        {"hidden": hidden, "grid": grid, "grid_within": grid_within, "analyze": analyze}[a.mode]()


if __name__ == "__main__":
    main()
