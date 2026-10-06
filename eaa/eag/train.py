"""Train epistemic heads on cached features.

Target (v0.2, amended before any test result): SUFFICIENCY = 1 iff level == full. HotpotQA is
constructed so both gold paragraphs are needed; "answer string present" (v0.1 label) rewarded
packets with a candidate answer but a missing bridge — the multi-hop hallucination pattern.
Held-out intervention: `drop_other` rows are excluded from train AND val, and used only at test
time as an untrained intervention (H6).

Loss = BCE(logit[batch], suff) + lambda_c * mean(relu(gamma - (logit_full - logit_drop_ans)))
BCE is computed on the sampled batch only; counterfactual partners (drop_ans of each `full` row,
open questions with a uniquely defined answer paragraph) enter the hinge term only, so they are
not double-weighted. All variants (probe, qe, eag) use the same loss; eag_lc0 is the ablation.
Model selection: lowest val BCE.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from .model import EpistemicHead

HELD_OUT_LEVELS = {"drop_other"}


def collate(feats: list[dict], idx, device):
    k = max(feats[i]["M"].shape[0] for i in idx)
    d = feats[idx[0]]["M"].shape[1]
    M = torch.zeros(len(idx), k, d)
    mask = torch.zeros(len(idx), k, dtype=torch.bool)
    for r, i in enumerate(idx):
        m = feats[i]["M"]
        M[r, : m.shape[0]] = m.float()
        mask[r, : m.shape[0]] = True
    h = torch.stack([feats[i]["h"].float() for i in idx])
    qv = torch.stack([feats[i]["qv"].float() for i in idx])
    return h.to(device), M.to(device), mask.to(device), qv.to(device)


def auroc(y: np.ndarray, s: np.ndarray) -> float:
    pos, neg = s[y == 1], s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    ranks = np.argsort(np.argsort(np.concatenate([pos, neg]))) + 1
    return float((ranks[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


@torch.no_grad()
def predict(model, feats, idx, device, bs=512):
    model.eval()
    out = []
    for i in range(0, len(idx), bs):
        out.append(model(*collate(feats, idx[i:i + bs], device)).float().cpu())
    return torch.cat(out).numpy()


def train_one(data, variant, lambda_c, seed, device, epochs=30, bs=256, lr=1e-3, gamma=2.0, patience=5):
    torch.manual_seed(seed)
    np.random.seed(seed)
    meta, feats = data["meta"], data["feats"]
    y = torch.tensor([float(m["level"] == "full") for m in meta], dtype=torch.float32)
    tr = [i for i, m in enumerate(meta) if m["split"] == "train" and m["level"] not in HELD_OUT_LEVELS]
    va = [i for i, m in enumerate(meta) if m["split"] == "val" and m["level"] not in HELD_OUT_LEVELS]
    key = {(m["item_id"], m["level"]): i for i, m in enumerate(meta)}
    pairs = [(key[(m["item_id"], "full")], key[(m["item_id"], "drop_ans")])
             for m in meta if m["split"] == "train" and m["level"] == "full"
             and m["qclass"] == "open" and m["answer_para_defined"]
             and (m["item_id"], "drop_ans") in key]
    pair_of = {a: b for a, b in pairs}

    d, nl = feats[0]["M"].shape[1], feats[0]["h"].shape[0]
    model = EpistemicHead(d, nl, variant).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    best, best_state, bad, hist = float("inf"), None, 0, []
    rng = np.random.default_rng(seed)
    for ep in range(epochs):
        model.train()
        perm = rng.permutation(tr)
        for i in range(0, len(perm), bs):
            idx = perm[i:i + bs].tolist()
            # add the counterfactual partner of every `full` row in the batch
            anchors = [j for j in idx if j in pair_of] if lambda_c > 0 else []
            partners = [pair_of[j] for j in anchors]
            logit = model(*collate(feats, idx + partners, device))
            lb = logit[: len(idx)]
            loss = F.binary_cross_entropy_with_logits(lb, y[idx].to(device))   # batch rows only
            if anchors:
                pos = {j: n for n, j in enumerate(idx)}
                lf = lb[[pos[j] for j in anchors]]
                ld = logit[len(idx):]
                loss = loss + lambda_c * F.relu(gamma - (lf - ld)).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
        pv = predict(model, feats, va, device)
        yv = y[va].numpy()
        vloss = float(F.binary_cross_entropy_with_logits(torch.tensor(pv), torch.tensor(yv)))
        hist.append({"epoch": ep, "val_bce": vloss, "val_auroc": auroc(yv, pv)})
        if vloss < best - 1e-4:
            best, bad = vloss, 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= patience:
                break
    model.load_state_dict(best_state)
    return model, hist, len(pairs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", required=True)
    ap.add_argument("--out-dir", default="08_architecture/eag_runs")
    ap.add_argument("--variants", nargs="+", default=["probe", "qe", "eag"])
    ap.add_argument("--lambda-c", type=float, default=1.0)
    ap.add_argument("--ablate-contrast", action="store_true", help="also train eag with lambda_c=0")
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    data = torch.load(args.features, weights_only=False)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    configs = [(v, args.lambda_c) for v in args.variants]
    if args.ablate_contrast:
        configs.append(("eag", 0.0))
    summary = []
    for variant, lc in configs:
        for seed in args.seeds:
            model, hist, n_pairs = train_one(data, variant, lc, seed, args.device)
            name = f"{variant}_lc{lc:g}_s{seed}"
            torch.save({"state": model.state_dict(), "variant": variant, "lambda_c": lc,
                        "seed": seed, "d": data["feats"][0]["M"].shape[1],
                        "n_layers_g": data["feats"][0]["h"].shape[0]}, out / f"{name}.pt")
            best = min(hist, key=lambda r: r["val_bce"])
            summary.append({"name": name, "variant": variant, "lambda_c": lc, "seed": seed,
                            "n_pairs": n_pairs, "epochs": len(hist), **best})
            print(json.dumps(summary[-1]))
    (out / "train_summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
