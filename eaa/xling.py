"""Phase 5a pilot — cross-lingual evidence (plan: 00_docs/16_analysis_plan_phase5a_crosslingual.md).

  python -m eaa.xling packets      EN* and XL prompts (XL: units replaced by XHotpotQA translations)
  python -m eaa.xling generate     Qwen2.5-3B greedy, both arms
  python -m eaa.eag.features --packets 01_data/xling_packets.jsonl --out 08_architecture/features_xling.pt
  python -m eaa.xling sigma        frozen eag_lc1 heads (English-trained) -> sigma.csv
  python -m eaa.judge --config configs/pilot_v0.1.yaml --extra 05_outputs/xling_qwen2.5-3b/generations.jsonl
  python -m eaa.xling analyze      XL − EN* contrasts
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from . import prompts as P
from .data import load_items
from .evaluate import normalize_answer

ITEMS = Path("01_data/hotpot_dev_study2_n400_seed20261006.jsonl")
S2_DIR = Path("05_outputs/study2_qwen2.5-3b")
XH = [Path(f"01_data/raw/xhotpotqa/validation-0000{i}.parquet") for i in (0, 1)]
PACKETS = Path("01_data/xling_packets.jsonl")
OUT = Path("05_outputs/xling_qwen2.5-3b")
FEATS = Path("08_architecture/features_xling.pt")
RUNS = Path("08_architecture/eag_runs")
REP = Path("07_analysis/xling")
MODEL = "03_models/Qwen2.5-3B-Instruct"
CONDS = {("full", "length"), ("drop_ans", "entity_poor")}
OLD = "Give only the short answer (a few words), no explanation."
NEW = "Give only the short answer (a few words) in English, no explanation."
LATIN = {"en", "es", "fr", "de", "pt", "it", "nl", "pl", "sv", "tr", "vi", "id", "sw"}
SEED = 20261017
B = 2000
XARM = "XL"          # second arm name; Phase 5b (eaa.idmono) rebinds it to "ID"


def _norm(s) -> str:
    return " ".join(str(s).split())


def _answer_title(it: dict) -> str | None:
    a = normalize_answer(it["answer"])
    paras = {c["title"]: " ".join(c["sentences"]) for c in it["context"]}
    gold = list(dict.fromkeys(sf["title"] for sf in it["supporting_facts"]))
    hit = [t for t in gold if a and f" {a} " in f" {normalize_answer(paras.get(t, ''))} "]
    return hit[0] if len(hit) == 1 else None


def packets():
    items = {it["id"]: it for it in load_items(ITEMS)}
    xh = pd.concat([pd.read_parquet(p) for p in XH])
    smap, tmap = {}, {}
    for cands in xh.candidates:
        for c in cands:
            src, tr = list(c["source_sentences"]), list(c["sentences"])
            tmap.setdefault(c["source_title"], (_norm(c["title"]), c["language_code"]))
            if len(src) == len(tr):
                for a, b in zip(src, tr):
                    smap.setdefault((c["source_title"], _norm(a)), (_norm(b), c["language_code"]))
    n = 0
    with open(PACKETS, "w", encoding="utf-8") as g:
        for line in open(S2_DIR / "packets.jsonl", encoding="utf-8"):
            p = json.loads(line)
            if (p["level"], p["policy"]) not in CONDS:
                continue
            it = items[p["item_id"]]
            lines = [x for x in p["evidence"].split("\n") if re.match(r"^\[e\d+\] ", x)]
            xl, unmapped, langs = [], 0, Counter()
            at = _answer_title(it)
            for k, x in enumerate(lines, 1):
                m = re.match(r"^\[e\d+\] \((.*?)\) (.*)$", x)
                title, sent = m.group(1), _norm(m.group(2))
                hit = smap.get((title, sent))
                if hit is None:
                    unmapped += 1
                    xl.append(x)
                    continue
                ttitle = tmap.get(title, (title, hit[1]))[0]
                xl.append(f"[e{k}] ({ttitle}) {hit[0]}")
                if title == at:
                    langs[hit[1]] += 1
            ans_lang = langs.most_common(1)[0][0] if langs else None
            q = it["question"]
            for arm, ev in (("EN", p["evidence"]), ("XL", "\n".join(xl))):
                prompt = P.GENERATOR.format(evidence=ev, advisory="", question=q).replace(OLD, NEW)
                assert NEW in prompt
                g.write(json.dumps({"item_id": p["item_id"], "level": p["level"], "policy": p["policy"],
                                    "arm": arm, "split": "test", "n_unmapped": unmapped if arm == "XL" else 0,
                                    "ans_lang": ans_lang if arm == "XL" else "en", "prompt": prompt},
                                   ensure_ascii=False) + "\n")
                n += 1
    print(f"wrote {n} prompts -> {PACKETS}")


def generate(batch_size: int = 8):
    from tqdm import tqdm

    from .backends import HFBackend
    from .run import _msgs

    OUT.mkdir(parents=True, exist_ok=True)
    gen = OUT / "generations.jsonl"
    done = {json.loads(l)["key"] for l in open(gen, encoding="utf-8")} if gen.exists() else set()
    rows = [r for r in map(json.loads, open(PACKETS, encoding="utf-8"))
            if f"{r['item_id']}|{r['level']}|{r['policy']}|{r['arm']}" not in done]
    be = HFBackend(MODEL)
    todo = sorted(rows, key=lambda r: be.prompt_tokens(_msgs(r["prompt"])))
    with open(gen, "a", encoding="utf-8") as f:
        for i in tqdm(range(0, len(todo), batch_size), desc="xling"):
            chunk = todo[i:i + batch_size]
            outs = be.generate([_msgs(r["prompt"]) for r in chunk], 24)
            for r, o in zip(chunk, outs):
                f.write(json.dumps({"key": f"{r['item_id']}|{r['level']}|{r['policy']}|{r['arm']}",
                                    "item_id": r["item_id"], "level": r["level"], "policy": r["policy"],
                                    "arm": r["arm"], "output": o, "model": be.name,
                                    "prompt_version": P.PROMPT_VERSION + "+en"}, ensure_ascii=False) + "\n")
            f.flush()
    print(f"done -> {gen}")


def sigma():
    import torch

    from .eag.model import EpistemicHead
    from .eag.train import predict

    data = torch.load(FEATS, weights_only=False)
    meta, feats = data["meta"], data["feats"]
    runs = [r["name"] for r in json.loads((RUNS / "train_summary.json").read_text())
            if r["name"].startswith("eag_lc1_")]
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    cols = []
    for name in runs:
        c = torch.load(RUNS / f"{name}.pt", weights_only=False, map_location="cpu")
        m = EpistemicHead(c["d"], c["n_layers_g"], c["variant"]).to(dev)
        m.load_state_dict(c["state"])
        cols.append(1 / (1 + np.exp(-predict(m, feats, list(range(len(meta))), dev))))
    df = pd.DataFrame([{k: m[k] for k in ("item_id", "level", "policy", "arm")} for m in meta])
    df["sigma"] = np.mean(cols, axis=0)
    REP.mkdir(parents=True, exist_ok=True)
    df.to_csv(REP / "sigma.csv", index=False)
    print(df.groupby(["arm", "level"]).sigma.mean().round(3))


def analyze():
    from . import evaluate as E
    from .conditions import question_class
    from .judge import load_cache

    sys.stdout.reconfigure(encoding="utf-8")
    E.JUDGED.clear()
    E.JUDGED.update(load_cache())
    rng = np.random.default_rng(SEED)
    items = {it["id"]: it for it in load_items(ITEMS)}
    s2pk = {(r["item_id"], r["level"], r["policy"]): r
            for r in map(json.loads, open(S2_DIR / "packets.jsonl", encoding="utf-8"))}
    meta = pd.DataFrame([{k: v for k, v in r.items() if k != "prompt"}
                         for r in map(json.loads, open(PACKETS, encoding="utf-8"))])
    gen = pd.read_json(OUT / "generations.jsonl", lines=True)
    sig = pd.read_csv(REP / "sigma.csv")
    d = gen.merge(meta, on=["item_id", "level", "policy", "arm"]).merge(sig, on=["item_id", "level", "policy", "arm"])
    lab = [E.label(str(o), items[i]["answer"], i) for i, o in zip(d.item_id, d.output)]
    for k in ("correct", "hallucination", "abstain", "judge_missing"):
        d[k] = [l[k] for l in lab]
    d["primary"] = [int(question_class(items[i]) == "open" and s2pk[(i, "full", "length")]["answer_para_defined"])
                    for i in d.item_id]
    d["gate_refuse"] = (d.sigma < 0.5).astype(int)
    d["non_latin_out"] = d.output.astype(str).map(lambda s: int(bool(re.search(r"[^\x00-ɏ\s\W\d]", s))))
    d.to_csv(REP / "eval.csv", index=False)

    P_ = d[d.primary == 1]
    W = {(a, lv): P_[(P_.arm == a) & (P_.level == lv)].set_index("item_id").sort_index()
         for a in ("EN", XARM) for lv in ("full", "drop_ans")}
    ids = W[("EN", "full")].index.intersection(W[(XARM, "full")].index) \
        .intersection(W[("EN", "drop_ans")].index).intersection(W[(XARM, "drop_ans")].index)

    def vec(a, lv, col):
        return W[(a, lv)].loc[ids, col].to_numpy().astype(float)

    pair = {a: (vec(a, "full", "sigma") > vec(a, "drop_ans", "sigma")).astype(float) for a in ("EN", XARM)}
    rows = []
    for name, x, y in [
        ("benar@full", vec("EN", "full", "correct"), vec(XARM, "full", "correct")),
        ("halusinasi@full", vec("EN", "full", "hallucination"), vec(XARM, "full", "hallucination")),
        ("abstain@full", vec("EN", "full", "abstain"), vec(XARM, "full", "abstain")),
        ("halusinasi@drop_ans", vec("EN", "drop_ans", "hallucination"), vec(XARM, "drop_ans", "hallucination")),
        ("akurasi berpasangan σ(full>drop_ans)", pair["EN"], pair[XARM]),
        ("gate menolak@full (σ<0,5)", vec("EN", "full", "gate_refuse"), vec(XARM, "full", "gate_refuse")),
        ("σ@full (rata-rata)", vec("EN", "full", "sigma"), vec(XARM, "full", "sigma")),
    ]:
        dif = y - x
        reps = [dif[rng.integers(0, len(dif), len(dif))].mean() for _ in range(B)]
        lo, hi = np.percentile(reps, [2.5, 97.5])
        rows.append({"ukuran": name, "EN*": x.mean(), XARM: y.mean(), f"{XARM}−EN*": dif.mean(), "lo": lo, "hi": hi})
    con = pd.DataFrame(rows)

    xf = W[(XARM, "full")].loc[ids].copy()
    ef = W[("EN", "full")].loc[ids]
    xf["d_correct"] = xf.correct.to_numpy() - ef.correct.to_numpy()
    xf["script"] = xf.ans_lang.map(lambda l: "tidak terpetakan" if not isinstance(l, str) else
                                   ("en (kontrol)" if l == "en" else "Latin" if l in LATIN else "non-Latin"))
    by_script = xf.groupby("script").agg(n=("correct", "size"), benar_X=("correct", "mean"),
                                         d_benar=("d_correct", "mean"), halu_X=("hallucination", "mean"),
                                         abstain_X=("abstain", "mean"), sigma_X=("sigma", "mean"))
    by_lang = xf.groupby("ans_lang").agg(n=("correct", "size"), benar_X=("correct", "mean"),
                                         d_benar=("d_correct", "mean"), abstain_X=("abstain", "mean"),
                                         sigma_X=("sigma", "mean")).sort_values("d_benar")
    md = ["# Fase 5a — evidence lintas bahasa (pilot eksploratif)\n",
          "Rencana: `00_docs/16_analysis_plan_phase5a_crosslingual.md`. Qwen2.5-3B, pertanyaan bahasa Inggris, "
          "evidence diterjemahkan (XHotpotQA, GPT-4o mini); kedua lengan diminta menjawab dalam bahasa Inggris.\n",
          f"Populasi utama, item berpasangan: {len(ids)}; judge_missing: {int(d.judge_missing.sum())}; "
          f"unit {XARM} tak terpetakan (rata-rata per paket): {d[d.arm == XARM].n_unmapped.mean():.2f}\n",
          f"Keluaran {XARM}@full yang memuat aksara non-Latin: {xf.non_latin_out.mean():.3f}\n",
          f"## Kontras {XARM} − EN* (bootstrap item, IK 95%)\n```\n" + con.round(3).to_string(index=False) + "\n```\n",
          "## Per aksara paragraf jawaban (deskriptif)\n```\n" + by_script.round(3).to_string() + "\n```\n",
          "## Per bahasa paragraf jawaban (deskriptif, n kecil; bukan untuk klaim per bahasa)\n```\n" +
          by_lang.round(3).to_string() + "\n```\n"]
    con.to_csv(REP / "contrasts_primary.csv", index=False)
    (REP / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["packets", "generate", "sigma", "analyze"])
    a = ap.parse_args()
    {"packets": packets, "generate": generate, "sigma": sigma, "analyze": analyze}[a.mode]()


if __name__ == "__main__":
    main()
