"""EAG v2 — gate + pointer at the output layer (plan: 00_docs/21_EAG_v2_pointer_gate_plan.md).

  P(y_t) = 1[σ ≥ τ] · [ g_t·P_gen(y_t) + (1 − g_t)·P_ptr(y_t) ],   σ < τ → ABSTAIN
  P_ptr(v) = Σ_j a_tj · 1[x_j = v],  a_t = softmax(q_t·k_j/√d_e) over evidence tokens j

  python -m eaa.eag.pointer train      frozen Qwen2.5-3B; HotpotQA *train* packets (full → gold, drop_ans → ABSTAIN)
  python -m eaa.eag.pointer decode     greedy decoding with the mixed distribution on the dev items (steer_dev set)
  python -m eaa.judge --config configs/pilot_v0.1.yaml --extra 05_outputs/eag_v2_dev/generations.jsonl
  python -m eaa.eag.pointer analyze    off / veto / ptr / ptr_σ / eag_v2 / CAA steer_σ
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from .. import prompts as P

MODEL = "03_models/Qwen2.5-3B-Instruct"
TRAIN_PACKETS = Path("01_data/eag_train_packets.jsonl")
TRAIN_RAW = [Path("01_data/raw/hotpot_qa_distractor_train_0.parquet"), Path("01_data/raw/hotpot_qa_distractor_train_1.parquet")]
RUN = Path("08_architecture/eag_v2")
OUT = Path("05_outputs/eag_v2_dev")
REP = Path("07_analysis/eag_v2")
LAYER = 27
DE, HG = 256, 64
LR, WD, ACCUM, EPOCHS = 1e-3, 0.01, 16, 2
N_VAL = 400            # fixed val subset (200 full + 200 drop_ans) to keep validation cheap
SEED = 20261028
TAU = 0.5
MAX_NEW = 24
SMOKE = False          # --smoke: tiny run into 07_analysis/eag_v2_smoke (code check only)


def _msgs(user: str) -> list[dict]:
    return [{"role": "system", "content": P.SYSTEM}, {"role": "user", "content": user}]


def _head():
    import torch
    import torch.nn as nn

    class PointerGate(nn.Module):
        def __init__(self, d: int):
            super().__init__()
            self.ln_q, self.ln_k, self.ln_g = nn.LayerNorm(d), nn.LayerNorm(d), nn.LayerNorm(d)
            self.q, self.k, self.gp = nn.Linear(d, DE), nn.Linear(d, DE), nn.Linear(d, DE)
            self.g = nn.Sequential(nn.Linear(DE + 3, HG), nn.GELU(), nn.Linear(HG, 1))
            nn.init.constant_(self.g[-1].bias, 2.2)          # start by trusting the generator (g ≈ 0.9)

        def forward(self, hq, hk, hg, lp_max):
            a = torch.softmax(self.q(self.ln_q(hq)) @ self.k(self.ln_k(hk)).T / DE ** 0.5, -1)   # [T, J]
            ent = -(a.clamp_min(1e-9).log() * a).sum(-1, keepdim=True)
            feat = torch.cat([self.gp(self.ln_g(hg)), a.max(-1, keepdim=True).values, ent, lp_max[:, None]], -1)
            return a, torch.sigmoid(self.g(feat)).squeeze(-1)
    return PointerGate


class _Backbone:
    """Frozen backbone helpers: evidence token positions, copy ids (raw / no-leading-space), forward."""

    def __init__(self):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(MODEL)
        self.model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float16, device_map="cuda").eval()
        for p in self.model.parameters():
            p.requires_grad_(False)
        self.end_id = self.tok.convert_tokens_to_ids("<|im_end|>")
        self._nosp = {}

    def nospace(self, i: int) -> int:
        if i not in self._nosp:
            s = self.tok.convert_ids_to_tokens(i)
            j = self.tok.convert_tokens_to_ids(s[1:]) if isinstance(s, str) and s.startswith("Ġ") and len(s) > 1 else None
            self._nosp[i] = j if isinstance(j, int) and j >= 0 and j != self.tok.unk_token_id else i
        return self._nosp[i]

    def encode_prompt(self, user: str):
        text = self.tok.apply_chat_template(_msgs(user), tokenize=False, add_generation_prompt=True)
        enc = self.tok(text, add_special_tokens=False, return_offsets_mapping=True)
        a, b = text.find("Evidence:\n") + len("Evidence:\n"), text.rfind("\n\nQuestion: ")
        ev = [k for k, (s, e) in enumerate(enc["offset_mapping"]) if s >= a and e <= b and e > s]
        ids = enc["input_ids"]
        raw = [ids[k] for k in ev]
        return ids, ev, raw, [self.nospace(i) for i in raw]


def _gold_answers(ids: set[str]) -> dict[str, str]:
    out = {}
    for p in TRAIN_RAW:
        df = pd.read_parquet(p, columns=["id", "answer"])
        df = df[df["id"].isin(ids)]
        out.update(dict(zip(df["id"], df["answer"])))
    return out


def train():
    import torch

    sys.stdout.reconfigure(encoding="utf-8")
    torch.manual_seed(SEED)
    rows = [json.loads(l) for l in open(TRAIN_PACKETS, encoding="utf-8")]
    rows = [r for r in rows if r["level"] in ("full", "drop_ans")]
    gold = _gold_answers({r["item_id"] for r in rows})
    tr = [r for r in rows if r["split"] == "train"]
    if SMOKE:
        tr = tr[:48]
    va_all = [r for r in rows if r["split"] == "val"]
    rng = random.Random(SEED)
    nv = 8 if SMOKE else N_VAL
    va = rng.sample([r for r in va_all if r["level"] == "full"], nv // 2) + \
         rng.sample([r for r in va_all if r["level"] == "drop_ans"], nv // 2)
    bb = _Backbone()
    d = bb.model.config.hidden_size
    head = _head()(d).cuda()
    opt = torch.optim.AdamW(head.parameters(), lr=LR, weight_decay=WD)
    print(f"params: {sum(p.numel() for p in head.parameters()):,}; train packets {len(tr)}, val {len(va)}")

    def loss_of(r):
        ids, ev, raw, nos = bb.encode_prompt(r["prompt"])
        target = gold[r["item_id"]] if r["level"] == "full" else P.ABSTAIN_TOKEN
        t_ids = bb.tok(target, add_special_tokens=False)["input_ids"] + [bb.end_id]
        seq = torch.tensor([ids + t_ids], device="cuda")
        with torch.no_grad():
            hs = bb.model.model(input_ids=seq, output_hidden_states=True).hidden_states
            qpos = torch.arange(len(ids) - 1, len(ids) + len(t_ids) - 1, device="cuda")
            lp = torch.log_softmax(bb.model.lm_head(hs[-1][0, qpos]).float(), -1)
            y = torch.tensor(t_ids, device="cuda")
            lp_y, lp_max = lp[torch.arange(len(t_ids)), y], lp.max(-1).values
            hq, hk, hg = hs[LAYER][0, qpos].float(), hs[LAYER][0, ev].float(), hs[-1][0, qpos].float()
        a, g = head(hq, hk, hg, lp_max)
        copy_ids = torch.tensor([nos] + [raw] * (len(t_ids) - 1), device="cuda")          # [T, J]
        p_ptr = (a * (copy_ids == y[:, None]).float()).sum(-1)
        p = g * lp_y.exp() + (1 - g) * p_ptr
        return -(p + 1e-9).log().mean()

    best, hist = float("inf"), []
    RUN.mkdir(parents=True, exist_ok=True)
    from tqdm import tqdm
    for ep in range(1 if SMOKE else EPOCHS):
        head.train()
        order = tr[:]
        rng.shuffle(order)
        opt.zero_grad()
        run_loss = []
        for k, r in enumerate(tqdm(order, desc=f"epoch {ep}")):
            loss = loss_of(r) / ACCUM
            loss.backward()
            run_loss.append(float(loss) * ACCUM)
            if (k + 1) % ACCUM == 0:
                opt.step()
                opt.zero_grad()
        head.eval()
        with torch.no_grad():
            vl = float(np.mean([float(loss_of(r)) for r in va]))
        hist.append({"epoch": ep, "train_loss": float(np.mean(run_loss)), "val_loss": vl})
        print(json.dumps(hist[-1]))
        if vl < best:
            best = vl
            torch.save({"state": head.state_dict(), "d": d, "layer": LAYER, "hist": hist}, RUN / "pointer_gate.pt")
    (RUN / "train_hist.json").write_text(json.dumps(hist, indent=2))


def decode():
    import torch
    from tqdm import tqdm

    from ..steer_dev import CONDS, _base

    sys.stdout.reconfigure(encoding="utf-8")
    items, prim, fold, off, lab, pk = _base()
    bb = _Backbone()
    ck = torch.load(RUN / "pointer_gate.pt", weights_only=False)
    head = _head()(ck["d"]).cuda()
    head.load_state_dict(ck["state"])
    head.eval()
    OUT.mkdir(parents=True, exist_ok=True)
    gen = OUT / "generations.jsonl"
    done = {json.loads(l)["key"] for l in open(gen, encoding="utf-8")} if gen.exists() else set()
    V = bb.model.config.vocab_size
    with open(gen, "a", encoding="utf-8") as f:
        for i in tqdm(prim[:3] if SMOKE else prim, desc="eag_v2 decode"):
            for lv, pol in CONDS:
                key = f"ptr|{i}|{lv}|{pol}"
                if key in done:
                    continue
                ids, ev, raw, nos = bb.encode_prompt(pk[(i, lv, pol)])
                raw_t, nos_t = torch.tensor(raw, device="cuda"), torch.tensor(nos, device="cuda")
                out_ids, gs, copied = [], [], 0
                with torch.inference_mode():
                    o = bb.model(input_ids=torch.tensor([ids], device="cuda"), use_cache=True, output_hidden_states=True)
                    hk = o.hidden_states[LAYER][0, ev].float()
                    for t in range(MAX_NEW):
                        hq = o.hidden_states[LAYER][0, -1:].float()
                        hg = o.hidden_states[-1][0, -1:].float()
                        pg = torch.softmax(o.logits[0, -1].float(), -1)
                        a, g = head(hq, hk, hg, pg.log().max()[None])
                        pp = torch.zeros(pg.shape[0], device="cuda").index_add_(0, nos_t if t == 0 else raw_t, a[0])
                        mix = g[0] * pg + (1 - g[0]) * pp
                        nxt = int(mix.argmax())
                        copied += int((1 - g[0]) * pp[nxt] > g[0] * pg[nxt])
                        gs.append(float(g[0]))
                        if nxt == bb.end_id:
                            break
                        out_ids.append(nxt)
                        o = bb.model(input_ids=torch.tensor([[nxt]], device="cuda"), past_key_values=o.past_key_values,
                                     use_cache=True, output_hidden_states=True)
                text = bb.tok.decode(out_ids, skip_special_tokens=True).strip()
                f.write(json.dumps({"key": key, "arm": "ptr", "item_id": i, "level": lv, "policy": pol, "output": text,
                                    "g_mean": float(np.mean(gs)) if gs else None, "g_first": gs[0] if gs else None,
                                    "copied_tokens": copied, "n_tokens": len(out_ids)}, ensure_ascii=False) + "\n")
                f.flush()
    print(f"done -> {gen}")


def analyze():
    from .. import evaluate as E
    from ..steer_dev import OUT as STEER_OUT, SIGMA, _base

    sys.stdout.reconfigure(encoding="utf-8")
    items, prim, fold, off, lab, pk = _base()
    sig = pd.read_csv(SIGMA).set_index(["item_id", "level", "policy"]).sigma
    g = pd.read_json(OUT / "generations.jsonl", lines=True)
    st = pd.read_json(STEER_OUT / "generations.jsonl", lines=True)
    st = st[st.config == "L24_a2"]
    ptr = {(r.item_id, r.level, r.policy): r for r in g.itertuples()}
    caa = {(r.item_id, r.level, r.policy): r.output for r in st.itertuples()}
    keys = [(i, lv, pol) for i in prim for lv, pol in (("full", "length"), ("drop_ans", "entity_poor"))]
    abst = {"correct": 0, "hallucination": 0, "abstain": 1}
    L = lambda k, o: E.label(str(o), items[k[0]]["answer"], k[0])
    arms = {}
    for k in keys:
        s = sig.get(k, np.nan)
        hi = s >= TAU
        b = lab[k]
        p = L(k, ptr[k].output) if k in ptr else None
        c = L(k, caa[k]) if k in caa else None
        arms[k] = {"off": b, "veto": b if hi else abst, "ptr": p,
                   "ptr_σ": (p if hi else b) if p else None, "eag_v2": (p if hi else abst) if p else None,
                   "caa_σ": (c if hi else b) if c else None}
    names = ["off", "veto", "ptr", "ptr_σ", "eag_v2", "caa_σ"]
    full = [k for k in keys if k[1] == "full" and arms[k]["ptr"] is not None]
    drop = [k for k in keys if k[1] == "drop_ans" and arms[k]["ptr"] is not None]
    hal = [k for k in full if lab[k]["hallucination"] == 1]
    cor = [k for k in full if lab[k]["correct"] == 1]
    probe = Path("07_analysis/diagnosis/probe_scores.csv")
    k1 = set()
    if probe.exists():
        ps = pd.read_csv(probe)
        ps = ps[(ps.group == "halluc") & (ps.primary == 1)]
        for i, gg in ps.groupby("item_id"):
            gd, gr = gg[gg.kind == "gold"], gg[gg.kind == "greedy"]
            if len(gd) and len(gr) and gd["int_L27"].iloc[0] > gr["int_L27"].iloc[0]:
                k1.add(i)
    rows = []
    for a in names:
        if any(arms[k][a] is None for k in full + drop):
            continue
        m = lambda ks, c: float(np.mean([arms[k][a][c] for k in ks])) if ks else np.nan
        U = np.mean([(np.mean([arms[k][a]["correct"] - 2 * arms[k][a]["hallucination"] for k in ((i, "full", "length"), (i, "drop_ans", "entity_poor"))]))
                     for i in {k[0] for k in full}])
        rows.append({"lengan": a, "benar@full": m(full, "correct"), "halu@full": m(full, "hallucination"),
                     "abstain@full": m(full, "abstain"), "halu@drop_ans": m(drop, "hallucination"),
                     "halu→benar": m(hal, "correct"), "rusak": 1 - m(cor, "correct"), "U(λ=2)": U,
                     "halu→benar K1": m([k for k in hal if k[0] in k1], "correct"),
                     "halu→benar nonK1": m([k for k in hal if k[0] not in k1], "correct")})
    T = pd.DataFrame(rows)
    diag = g.groupby("level")[["g_first", "g_mean", "copied_tokens", "n_tokens"]].mean()
    REP.mkdir(parents=True, exist_ok=True)
    T.to_csv(REP / "dev_pilot.csv", index=False)
    pt = T.set_index("lengan").loc["ptr_σ"] if "ptr_σ" in set(T.lengan) else None
    verdict = ""
    if pt is not None:
        d_drop = pt["halu@drop_ans"] - T.set_index("lengan").loc["off", "halu@drop_ans"]
        ok = pt["halu→benar"] >= 0.15 and pt["rusak"] <= 0.05 and d_drop <= 0.02
        verdict = (f"\nAmbang pilot (dokumen 21 §4): halu→benar ≥ 0,15, rusak ≤ 0,05, Δhalu@drop_ans ≤ +0,02 → "
                   f"halu→benar {pt['halu→benar']:.3f}, rusak {pt['rusak']:.3f}, Δhalu@drop_ans {d_drop:+.3f}: "
                   f"**{'TERCAPAI' if ok else 'TIDAK TERCAPAI'}**\n")
    md = ["# EAG v2 — pilot di dev (eksploratif)\n", "Rencana: `00_docs/21_EAG_v2_pointer_gate_plan.md`. Qwen2.5-3B beku, "
          f"255 item utama; halusinasi off@full = {len(hal)}, K1 = {len([k for k in hal if k[0] in k1])}.\n",
          "```\n" + T.round(3).to_string(index=False) + "\n```\n",
          "Diagnostik penunjuk (rata-rata per baris):\n```\n" + diag.round(3).to_string() + "\n```\n", verdict]
    (REP / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["train", "decode", "analyze"])
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        global SMOKE, RUN, OUT, REP
        SMOKE, RUN = True, Path("07_analysis/eag_v2_smoke/run")
        OUT, REP = Path("07_analysis/eag_v2_smoke/out"), Path("07_analysis/eag_v2_smoke/rep")
    {"train": train, "decode": decode, "analyze": analyze}[a.mode]()


if __name__ == "__main__":
    main()
