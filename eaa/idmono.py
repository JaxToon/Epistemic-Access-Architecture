"""Phase 5b pilot — monolingual Indonesian question + evidence (plan: 00_docs/20_analysis_plan_phase5b_indonesian.md).

  python -m eaa.idmono translate   Gemma 4 E4B (Ollama) translates every unique title / sentence / question
  python -m eaa.idmono packets     EN* (identical to Phase 5a) and ID prompts -> 01_data/idmono_packets.jsonl
  python -m eaa.idmono quality     answer-string preservation + 40-pair human audit sample
  python -m eaa.idmono generate    Qwen2.5-3B greedy (reuses eaa.xling)
  python -m eaa.eag.features --packets 01_data/idmono_packets.jsonl --out 08_architecture/features_idmono.pt
  python -m eaa.idmono sigma
  python -m eaa.judge --config configs/pilot_v0.1.yaml --extra 05_outputs/idmono_qwen2.5-3b/generations.jsonl
  python -m eaa.idmono analyze
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from . import prompts as P
from . import xling as X
from .data import load_items
from .evaluate import normalize_answer

SRC = Path("01_data/xling_packets.jsonl")             # EN* rows of Phase 5a (prompt already says "in English")
PACKETS = Path("01_data/idmono_packets.jsonl")
OUT = Path("05_outputs/idmono_qwen2.5-3b")
FEATS = Path("08_architecture/features_idmono.pt")
REP = Path("07_analysis/idmono")
CACHE = REP / "translations.jsonl"
TRANSLATOR = "gemma4:e4b"
SYSTEM_T = ("You are a professional translator. Translate the user's text from English into Indonesian. "
            "Keep names of people, places, organisations and titles of works, and all numbers, as they are "
            "normally written in Indonesian. Output only the translation, nothing else.")
SEED = 20261028


def _units(evidence: str):
    out = []
    for x in evidence.split("\n"):
        m = re.match(r"^\[e(\d+)\] \((.*?)\) (.*)$", x)
        if m:
            out.append((int(m.group(1)), m.group(2), m.group(3)))
    return out


def _evidence_of(prompt: str) -> str:
    return prompt[prompt.find("Evidence:\n") + len("Evidence:\n"):prompt.rfind("\n\nQuestion: ")]


def translate():
    import urllib.request
    from concurrent.futures import ThreadPoolExecutor

    from tqdm import tqdm

    items = {it["id"]: it for it in load_items(X.ITEMS)}
    rows = [r for r in map(json.loads, open(SRC, encoding="utf-8")) if r["arm"] == "EN"]
    todo = set()
    for r in rows:
        for _, t, s in _units(_evidence_of(r["prompt"])):
            todo.update([t, s])
        todo.add(items[r["item_id"]]["question"])
    REP.mkdir(parents=True, exist_ok=True)
    done = {}
    if CACHE.exists():
        done = {d["src"]: d["tgt"] for d in map(json.loads, open(CACHE, encoding="utf-8"))}
    todo = sorted(t for t in todo if t not in done)

    def one(src: str) -> str:
        body = json.dumps({"model": TRANSLATOR, "stream": False, "think": False,
                           "messages": [{"role": "system", "content": SYSTEM_T}, {"role": "user", "content": src}],
                           "options": {"temperature": 0, "seed": 0, "num_predict": 256}}).encode()
        req = urllib.request.Request("http://localhost:11434/api/chat", body, {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=600) as resp:
            return " ".join(json.load(resp)["message"]["content"].split())

    with open(CACHE, "a", encoding="utf-8") as f, ThreadPoolExecutor(4) as ex:
        for i in tqdm(range(0, len(todo), 16), desc="translate"):
            chunk = todo[i:i + 16]
            for src, tgt in zip(chunk, ex.map(one, chunk)):
                f.write(json.dumps({"src": src, "tgt": tgt}, ensure_ascii=False) + "\n")
            f.flush()
    print(f"translated {len(todo)} new strings -> {CACHE}")


def packets():
    items = {it["id"]: it for it in load_items(X.ITEMS)}
    tr = {d["src"]: d["tgt"] for d in map(json.loads, open(CACHE, encoding="utf-8"))}
    n = miss = 0
    with open(PACKETS, "w", encoding="utf-8") as g:
        for r in map(json.loads, open(SRC, encoding="utf-8")):
            if r["arm"] != "EN":
                continue
            g.write(json.dumps(r, ensure_ascii=False) + "\n")
            units = _units(_evidence_of(r["prompt"]))
            ev = []
            for k, t, s in units:
                miss += int(t not in tr) + int(s not in tr)
                ev.append(f"[e{k}] ({tr.get(t, t)}) {tr.get(s, s)}")
            q = items[r["item_id"]]["question"]
            prompt = P.GENERATOR.format(evidence="\n".join(ev), advisory="", question=tr.get(q, q)).replace(X.OLD, X.NEW)
            g.write(json.dumps({**r, "arm": "ID", "ans_lang": "id", "prompt": prompt}, ensure_ascii=False) + "\n")
            n += 2
    print(f"wrote {n} prompts (untranslated strings: {miss}) -> {PACKETS}")


def quality():
    sys.stdout.reconfigure(encoding="utf-8")
    items = {it["id"]: it for it in load_items(X.ITEMS)}
    rows = [r for r in map(json.loads, open(PACKETS, encoding="utf-8")) if r["level"] == "full"]
    keep = {}
    for r in rows:
        a = normalize_answer(items[r["item_id"]]["answer"])
        if a in {"yes", "no"}:
            continue
        ev = normalize_answer(_evidence_of(r["prompt"]))
        keep.setdefault(r["item_id"], {})[r["arm"]] = int(f" {a} " in f" {ev} ")
    df = pd.DataFrame(keep).T
    both = df.dropna()
    REP.mkdir(parents=True, exist_ok=True)
    df.to_csv(REP / "answer_preservation.csv", index_label="item_id")
    pairs = [d for d in map(json.loads, open(CACHE, encoding="utf-8")) if len(d["src"].split()) >= 5]
    rng = np.random.default_rng(SEED)
    pick = [pairs[i] for i in rng.choice(len(pairs), 40, replace=False)]
    pd.DataFrame([{"src": p["src"], "tgt": p["tgt"], "nilai (benar/salah_makna/nama_angka_berubah)": ""} for p in pick]) \
        .to_csv(REP / "audit_sample.csv", index=False, encoding="utf-8-sig")
    print(f"answer string present in full packet: EN {both.EN.mean():.3f}, ID {both.ID.mean():.3f} (n={len(both)}); "
          f"lost in ID only: {int(((both.EN == 1) & (both.ID == 0)).sum())}")
    print(f"audit sample -> {REP / 'audit_sample.csv'}")


def _bind():
    X.PACKETS, X.OUT, X.FEATS, X.REP, X.XARM = PACKETS, OUT, FEATS, REP, "ID"


def main():
    sys.stdout.reconfigure(encoding="utf-8")   # Windows console (cp1252) cannot print ‖, σ, →
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["translate", "packets", "quality", "generate", "sigma", "analyze"])
    a = ap.parse_args()
    if a.mode in ("generate", "sigma", "analyze"):
        _bind()
        {"generate": X.generate, "sigma": X.sigma, "analyze": X.analyze}[a.mode]()
    else:
        {"translate": translate, "packets": packets, "quality": quality}[a.mode]()


if __name__ == "__main__":
    main()
