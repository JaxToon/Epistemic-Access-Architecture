"""Phase 1/2 after supervisor feedback (plan: 00_docs/12_analysis_plan_diagnosis_popularity.md).

  python -m eaa.diagnose score       GPU: teacher-forced log-probs (gold / own / abstain), logit lens
                                     at t0, closed-book generation + gold log-prob (Qwen2.5-3B)
  python -m eaa.diagnose pageviews   Wikipedia pageviews 2025 for the two gold titles of every item
  python -m eaa.diagnose analyze     K1/K2, knowledge source, error types, popularity regressions

Exploratory: the data already exist; definitions were fixed in the plan before any of these
quantities were computed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

from . import prompts as P
from .data import load_items
from .evaluate import f1_score, normalize_answer

ITEMS = Path("01_data/hotpot_dev_study2_n400_seed20261006.jsonl")
S2_DIR = Path("05_outputs/study2_qwen2.5-3b")
PACKETS = Path("01_data/study3_packets.jsonl")
EVAL = Path("07_analysis/study3/qwen2.5-3b/eval.csv")
MODEL = "03_models/Qwen2.5-3B-Instruct"
OUT = Path("07_analysis/diagnosis")
SEED = 20261017
B = 2000
UA = "EAA-research/0.1 (academic research script; HotpotQA entity popularity)"


def _msgs(user: str) -> list[dict]:
    return [{"role": "system", "content": P.SYSTEM}, {"role": "user", "content": user}]


# ------------------------------------------------------------------------------------- score
def score():
    import torch
    from tqdm import tqdm
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float16, device_map="cuda").eval()
    body, head = model.model, model.lm_head
    n_layers = model.config.num_hidden_layers

    items = {it["id"]: it for it in load_items(ITEMS)}
    off = {(r["item_id"], r["level"], r["policy"]): r["output"]
           for r in map(json.loads, open(S2_DIR / "generations.jsonl", encoding="utf-8"))
           if r["prompt"] == "extractive"}
    pk = [r for r in map(json.loads, open(PACKETS, encoding="utf-8")) if r["level"] in ("full", "drop_ans")]

    @torch.inference_mode()
    def run(user: str, conts: dict[str, str], lens_token: str | None):
        text = tok.apply_chat_template(_msgs(user), tokenize=False, add_generation_prompt=True)
        p_ids = tok(text, add_special_tokens=False)["input_ids"]
        names = [k for k, v in conts.items() if v]
        c_ids = [tok(conts[k], add_special_tokens=False)["input_ids"] for k in names]
        L = max(len(p_ids) + len(c) for c in c_ids)
        ids = torch.full((len(names), L), tok.pad_token_id or 0, dtype=torch.long)
        att = torch.zeros((len(names), L), dtype=torch.long)
        for b, c in enumerate(c_ids):
            seq = p_ids + c
            ids[b, : len(seq)] = torch.tensor(seq)
            att[b, : len(seq)] = 1
        out = body(input_ids=ids.cuda(), attention_mask=att.cuda(), output_hidden_states=True)
        hs = out.hidden_states
        res = {}
        t0 = len(p_ids) - 1
        for b, (k, c) in enumerate(zip(names, c_ids)):
            pos = torch.arange(t0, t0 + len(c), device="cuda")
            lp = torch.log_softmax(head(hs[-1][b, pos]).float(), -1)
            tl = lp[torch.arange(len(c)), torch.tensor(c, device="cuda")]
            res[f"lp_{k}"] = float(tl.mean())
            res[f"lpsum_{k}"] = float(tl.sum())
            res[f"ntok_{k}"] = len(c)
        if lens_token:
            g0 = tok(lens_token, add_special_tokens=False)["input_ids"][0]
            ranks = []
            for l in range(1, n_layers + 1):
                h = hs[l][0, t0]
                h = h if l == n_layers else body.norm(h)        # HF Qwen2: last entry already normed
                lg = head(h).float()
                ranks.append(int((lg > lg[g0]).sum()) + 1)
            res["rank_layers"] = ranks
            res["rank_final"] = ranks[-1]
            res["rank_min"] = int(min(ranks))
            res["rank_min_layer"] = int(np.argmin(ranks)) + 1
        del out, hs
        return res

    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / "scores.jsonl"
    done = {json.loads(l)["key"] for l in open(dst, encoding="utf-8")} if dst.exists() else set()
    with open(dst, "a", encoding="utf-8") as f:
        for r in tqdm(pk, desc="packets"):
            key = f"{r['item_id']}|{r['level']}|{r['policy']}"
            if key in done:
                continue
            gold = items[r["item_id"]]["answer"]
            own = off[(r["item_id"], r["level"], r["policy"])]
            res = run(r["prompt"], {"gold": gold, "own": own, "abs": P.ABSTAIN_TOKEN}, gold)
            f.write(json.dumps({"key": key, "item_id": r["item_id"], "level": r["level"], "policy": r["policy"],
                                "own": own, **res}, ensure_ascii=False) + "\n")
            f.flush()

    # closed book: greedy generation (same settings as the pilot) + gold log-prob
    cb = OUT / "closed_book.jsonl"
    done = {json.loads(l)["item_id"] for l in open(cb, encoding="utf-8")} if cb.exists() else set()
    todo = [it for it in items.values() if it["id"] not in done]
    gtok = AutoTokenizer.from_pretrained(MODEL, padding_side="left")
    with open(cb, "a", encoding="utf-8") as f:
        for i in tqdm(range(0, len(todo), 16), desc="closed-book"):
            chunk = todo[i:i + 16]
            users = [P.CLOSED_BOOK.format(question=it["question"]) for it in chunk]
            texts = [gtok.apply_chat_template(_msgs(u), tokenize=False, add_generation_prompt=True) for u in users]
            enc = gtok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
            with torch.inference_mode():
                g = model.generate(**enc, max_new_tokens=24, do_sample=False, temperature=None, top_p=None,
                                   top_k=None, pad_token_id=gtok.pad_token_id)
            outs = [s.strip() for s in gtok.batch_decode(g[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)]
            for it, u, o in zip(chunk, users, outs):
                res = run(u, {"gold": it["answer"]}, it["answer"])
                f.write(json.dumps({"item_id": it["id"], "cb_output": o, "cb_lp_gold": res["lp_gold"],
                                    "cb_rank_final": res["rank_final"]}, ensure_ascii=False) + "\n")
            f.flush()
    print(f"done -> {dst}, {cb}")


# --------------------------------------------------------------------------------- pageviews
def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {}
            time.sleep(30 * (attempt + 1) if e.code == 429 else 2 ** attempt)
        except Exception:
            time.sleep(2 ** attempt)
    raise RuntimeError(f"failed: {url}")


def pageviews():
    items = load_items(ITEMS)
    titles = sorted({sf["title"] for it in items for sf in it["supporting_facts"]})
    # resolve redirects / normalisation (titles come from the 2017 dump)
    resolved = {}
    for i in range(0, len(titles), 50):
        chunk = titles[i:i + 50]
        q = urllib.parse.urlencode({"action": "query", "format": "json", "redirects": 1,
                                    "titles": "|".join(chunk)})
        js = _get(f"https://en.wikipedia.org/w/api.php?{q}").get("query", {})
        m = {t: t for t in chunk}
        for n in js.get("normalized", []):
            m = {k: (n["to"] if v == n["from"] else v) for k, v in m.items()}
        for rd in js.get("redirects", []):
            m = {k: (rd["to"] if v == rd["from"] else v) for k, v in m.items()}
        missing = {p["title"] for p in js.get("pages", {}).values() if "missing" in p}
        for k, v in m.items():
            resolved[k] = None if v in missing else v
        time.sleep(0.2)
    OUT.mkdir(parents=True, exist_ok=True)
    cache_p = OUT / "pageviews_cache.jsonl"          # resumable: the REST API rate-limits (429)
    cache = {}
    if cache_p.exists():
        cache = {r["title"]: r for r in map(json.loads, open(cache_p, encoding="utf-8"))}
    with open(cache_p, "a", encoding="utf-8") as f:
        for t in titles:
            if t in cache:
                continue
            r = resolved.get(t)
            views = 0
            if r:
                art = urllib.parse.quote(r.replace(" ", "_"), safe="")
                js = _get("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/"
                          f"all-access/user/{art}/monthly/20250101/20251231")
                views = int(sum(x["views"] for x in js.get("items", [])))
                time.sleep(1.0)
            cache[t] = {"title": t, "resolved": r, "views_2025": views}
            f.write(json.dumps(cache[t], ensure_ascii=False) + "\n")
            f.flush()
    rows = [cache[t] for t in titles]
    pd.DataFrame(rows).to_csv(OUT / "pageviews.csv", index=False)
    print(f"{len(rows)} titles, unresolved {sum(r['resolved'] is None for r in rows)}, "
          f"zero views {sum(r['views_2025'] == 0 for r in rows)} -> {OUT / 'pageviews.csv'}")


# ----------------------------------------------------------------------------------- analyze
def _wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def _units(evidence: str, flags: list[bool]):
    lines = [l for l in evidence.split("\n") if re.match(r"^\[e\d+\] ", l)]
    gold, dis = [], []
    for l, g in zip(lines, flags):
        (gold if g else dis).append(l)
    return " ".join(gold), " ".join(dis)


def _contains(hay: str, needle: str) -> bool:
    return bool(needle) and f" {needle} " in f" {normalize_answer(hay)} "


def _logit_boot(x: np.ndarray, y: np.ndarray, rng) -> tuple[float, float, float]:
    """Logistic slope (per SD of x) with item bootstrap; plain Newton IRLS (no extra deps)."""
    def fit(xx, yy):
        X = np.c_[np.ones_like(xx), xx]
        w = np.zeros(2)
        for _ in range(50):
            p = 1 / (1 + np.exp(-X @ w))
            H = X.T @ (X * (p * (1 - p))[:, None]) + 1e-6 * np.eye(2)
            step = np.linalg.solve(H, X.T @ (yy - p))
            w += step
            if np.abs(step).max() < 1e-8:
                break
        return w[1]
    z = (x - x.mean()) / x.std()
    est = fit(z, y)
    reps = []
    for _ in range(B):
        i = rng.integers(0, len(z), len(z))
        if y[i].min() == y[i].max():
            continue
        reps.append(fit(z[i], y[i]))
    lo, hi = np.percentile(reps, [2.5, 97.5])
    return float(est), float(lo), float(hi)


def analyze():
    from scipy.stats import mannwhitneyu, spearmanr

    from . import evaluate as E
    from .judge import load_cache

    sys.stdout.reconfigure(encoding="utf-8")
    E.JUDGED.clear()
    E.JUDGED.update(load_cache())
    rng = np.random.default_rng(SEED)
    items = {it["id"]: it for it in load_items(ITEMS)}
    ev = pd.read_csv(EVAL)
    off = ev[(ev.arm == "off")]
    sc = pd.read_json(OUT / "scores.jsonl", lines=True)
    cb = pd.read_json(OUT / "closed_book.jsonl", lines=True)
    s2pk = {(r["item_id"], r["level"], r["policy"]): r
            for r in map(json.loads, open(S2_DIR / "packets.jsonl", encoding="utf-8"))}

    # closed-book labels
    cbl = [E.label(str(o), items[i]["answer"], i) for i, o in zip(cb.item_id, cb.cb_output)]
    cb["cb_correct"] = [l["correct"] for l in cbl]
    cb["cb_answered"] = [l["answered"] for l in cbl]
    cb["cb_judge_missing"] = [l["judge_missing"] for l in cbl]

    full = off[off.level == "full"].merge(sc[sc.level == "full"], on=["item_id", "level", "policy"])
    da = sc[sc.level == "drop_ans"].groupby("item_id")[["lp_gold"]].mean().rename(columns={"lp_gold": "lp_gold_dropans"})
    full = full.merge(da, on="item_id").merge(cb, on="item_id")
    full["d_lp_ctx"] = full.lp_gold - full.lp_gold_dropans
    full["group"] = np.select([full.correct == 1, full.hallucination == 1, full.abstain == 1],
                              ["correct", "halluc", "abstain"], "other")
    prim = full[full.primary == 1].copy()

    # titles
    def titles(i):
        it = items[i]
        g = list(dict.fromkeys(sf["title"] for sf in it["supporting_facts"]))
        a = normalize_answer(it["answer"])
        paras = {c["title"]: " ".join(c["sentences"]) for c in it["context"]}
        ans = [t for t in g if _contains(paras.get(t, ""), a)]
        ans_t = ans[0] if len(ans) == 1 else None
        bridge = [t for t in g if t != ans_t]
        return g, ans_t, (bridge[0] if ans_t and bridge else None)

    # K1/K2 + error types for hallucinations
    def etype(r):
        own = normalize_answer(str(r.output))
        _, _, bridge = titles(r.item_id)
        p = s2pk[(r.item_id, r.level, r.policy)]
        gtxt, dtxt = _units(p["evidence"], p["gold_flags"])
        if bridge and (own == normalize_answer(bridge) or _contains(bridge, own)):
            return "1_hop_pertama"
        if f1_score(str(r.output), items[r.item_id]["answer"]) > 0:
            return "4_parsial_format"
        if _contains(gtxt, own):
            return "3_emas_entitas_lain"
        if _contains(dtxt, own):
            return "2_pengecoh"
        return "5_lainnya"

    H = prim[prim.group == "halluc"].copy()
    H["K1"] = (H.lp_gold > H.lp_own).astype(int)
    H["K1_loose"] = (H.rank_final <= 5).astype(int)
    H["K2"] = ((H.lp_gold <= H.lp_own) & (H.rank_final > 5)).astype(int)
    H["source"] = np.where(H.cb_correct == 1, "memori", "konteks saja")
    H["etype"] = [etype(r) for r in H.itertuples()]
    A = prim[prim.group == "abstain"].copy()
    A["gold_over_abs"] = (A.lp_gold > A.lp_abs).astype(int)

    md = ["# Diagnosis \"tahu tapi tidak mengungkap\" + popularitas (eksploratif)\n",
          "Rencana: `00_docs/12_analysis_plan_diagnosis_popularity.md`. Qwen2.5-3B, `full`, populasi utama.\n",
          f"closed-book judge_missing: {int(cb.cb_judge_missing.sum())} (fallback strict)\n"]

    g = prim.groupby("group")
    desc = pd.DataFrame({
        "n": g.size(),
        "LP_gold_med": g.lp_gold.median(), "LP_own_med": g.lp_own.median(), "LP_abs_med": g.lp_abs.median(),
        "R_final_med": g.rank_final.median(), "R_final<=5": g.rank_final.apply(lambda s: (s <= 5).mean()),
        "R_min_med": g.rank_min.median(), "dLP_ctx_med": g.d_lp_ctx.median(),
        "CB_correct": g.cb_correct.mean(), "sigma_med": g.sigma.median()})
    md += ["## Ringkasan per kelompok (`off`)\n", "```\n" + desc.round(3).to_string() + "\n```\n"]

    n = len(H)
    lines = []
    for k in ("K1", "K1_loose", "K2"):
        c = int(H[k].sum())
        lo, hi = _wilson(c, n)
        lines.append(f"{k}: {c}/{n} = {c / n:.3f}  [Wilson 95%: {lo:.3f}; {hi:.3f}]")
    c = int(A.gold_over_abs.sum())
    lo, hi = _wilson(c, len(A))
    lines.append(f"abstain dengan LP_gold > LP_abs: {c}/{len(A)} = {c / len(A):.3f} [{lo:.3f}; {hi:.3f}]")
    md += ["## Klasifikasi kasus halusinasi\n", "```\n" + "\n".join(lines) + "\n```\n",
           "K1 × sumber pengetahuan:\n```\n" + pd.crosstab(H.K1, H.source, margins=True).to_string() + "\n```\n",
           "Jenis kesalahan × K1:\n```\n" + pd.crosstab(H.etype, H.K1, margins=True).to_string() + "\n```\n"]

    mw = []
    for col in ("lp_gold", "rank_final", "d_lp_ctx", "sigma"):
        a, b = prim[prim.group == "correct"][col], prim[prim.group == "halluc"][col]
        mw.append(f"{col}: benar vs halusinasi, Mann–Whitney p = {mannwhitneyu(a, b).pvalue:.4g}")
    md += ["Perbandingan (deskriptif, tanpa koreksi):\n```\n" + "\n".join(mw) + "\n```\n"]

    # logit lens profile: median rank per layer by group
    prof = pd.DataFrame({grp: np.median(np.stack(prim[prim.group == grp].rank_layers.to_numpy()), axis=0)
                         for grp in ("correct", "halluc", "abstain")})
    prof.index = range(1, len(prof) + 1)
    prof.to_csv(OUT / "logit_lens_median_rank.csv", index_label="layer")
    md += ["*Logit lens* (median peringkat token pertama jawaban emas di t₀; lapisan terpilih):\n```\n" +
           prof.loc[[9, 18, 24, 27, 30, 33, 34, 35, 36]].to_string() + "\n```\n"]

    # ---------------- popularity
    pv_path = OUT / "pageviews.csv"
    if pv_path.exists():
        pv = pd.read_csv(pv_path).set_index("title")
        lv = np.log10(1 + pv.views_2025)

        def pop(i):
            g_, _, _ = titles(i)
            v = [lv.get(t, 0.0) for t in g_]
            return np.mean(v), np.min(v)
        full[["pop_mean", "pop_min"]] = [pop(i) for i in full.item_id]
        prim = full[full.primary == 1].copy()
        prim["gate_refuse"] = (prim.sigma < 0.5).astype(int)
        prim["hi_sigma_wrong"] = ((prim.sigma >= 0.5) & (prim.correct == 0)).astype(int)
        outs = ["correct", "hallucination", "abstain", "gate_refuse", "hi_sigma_wrong"]
        reg = []
        for xcol in ("pop_mean", "pop_min"):
            for y in outs:
                est, lo, hi = _logit_boot(prim[xcol].to_numpy(), prim[y].to_numpy().astype(float), rng)
                reg.append({"x": xcol, "outcome": y, "slope_per_SD": est, "lo": lo, "hi": hi,
                            "ci_excl_0": int(lo > 0 or hi < 0)})
        reg = pd.DataFrame(reg)
        prim["Q"] = pd.qcut(prim.pop_mean, 4, labels=["Q1 (jarang)", "Q2", "Q3", "Q4 (populer)"])
        qt = prim.groupby("Q", observed=True)[outs + ["sigma"]].mean()
        qt.insert(0, "n", prim.groupby("Q", observed=True).size())
        rho, pr = spearmanr(prim.pop_mean, prim.sigma)
        # secondary: drop_ans hallucination vs popularity; K1 vs popularity
        dl = off[(off.level == "drop_ans") & (off.primary == 1)].groupby("item_id").hallucination.mean()
        dd = prim.set_index("item_id").join(dl.rename("halluc_dropans"))
        rho2, p2 = spearmanr(dd.pop_mean, dd.halluc_dropans)
        Hp = H.merge(prim[["item_id", "pop_mean"]], on="item_id")
        # K1 primary is degenerate (greedy; see deviation in plan 12) -> K1_loose
        k1 = _logit_boot(Hp.pop_mean.to_numpy(), Hp.K1_loose.to_numpy().astype(float), rng)
        unresolved = int(pv.resolved.isna().sum())
        md += ["## Popularitas entitas (pageviews 2025)\n",
               f"judul: {len(pv)}, tidak ter-resolve: {unresolved}, views = 0: {int((pv.views_2025 == 0).sum())}\n",
               "Regresi logistik (kemiringan per 1 SD popularitas, IK 95% bootstrap item):\n```\n" +
               reg.round(3).to_string(index=False) + "\n```\n",
               "Per kuartil popularitas (rata-rata log10 views kedua judul emas):\n```\n" +
               qt.round(3).to_string() + "\n```\n",
               f"Spearman popularitas vs σ: ρ = {rho:.3f} (p = {pr:.3g})\n",
               f"Sekunder: Spearman popularitas vs halusinasi @drop_ans: ρ = {rho2:.3f} (p = {p2:.3g})\n",
               f"Sekunder: K1_longgar vs popularitas (logistik, per SD): {k1[0]:.3f} [{k1[1]:.3f}; {k1[2]:.3f}]\n"]
        reg.to_csv(OUT / "popularity_regression.csv", index=False)
        qt.to_csv(OUT / "popularity_quartiles.csv")

    H.drop(columns=["rank_layers"]).to_csv(OUT / "halluc_cases.csv", index=False)
    full.drop(columns=["rank_layers"]).to_csv(OUT / "full_scored.csv", index=False)
    (OUT / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["score", "pageviews", "analyze"])
    a = ap.parse_args()
    {"score": score, "pageviews": pageviews, "analyze": analyze}[a.mode]()


if __name__ == "__main__":
    main()
