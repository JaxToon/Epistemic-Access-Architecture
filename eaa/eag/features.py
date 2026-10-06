"""Frozen-backbone feature extraction (one forward pass per packet).

From the *generator* prompt (system + user, chat template, generation prompt appended):
  h   [n_layers_g, d]  hidden state at the last prompt position = commitment point t0
                       (the state that emits the first answer token)
  M   [k, d]           each evidence line "[eK] (title) text" mean-pooled at layer l_r
  qv  [d]              the question ALONE ("Question: ..."), separate forward pass, mean-pooled at
                       layer l_r -> no evidence, no generator state (used by the `qe` variant)
Evidence precedes the question and attention is causal, so M never sees the question:
functionally a reader encoding of the delivered packet. h sees everything.
(v0.2: qv from a separate pass — in v0.1 it was pooled inside the generator prompt and had
already seen the evidence; methodology review 2026-10-05, item 3.)
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import torch

from .. import prompts as P


def question_of(prompt: str) -> str:
    qs = prompt.rfind("Question: ") + len("Question: ")
    return prompt[qs:prompt.find("\nAnswer:", qs)]


def _spans(text: str) -> tuple[list[tuple[int, int]], tuple[int, int]]:
    units = [(m.start(), m.end()) for m in re.finditer(r"^\[e\d+\] .*$", text, flags=re.M)]
    qs = text.rfind("Question: ")
    qe = text.find("\nAnswer:", qs)
    return units, (qs + len("Question: "), qe)


@torch.no_grad()
def extract(model, tok, prompts: list[str], layers_g: list[int], layer_r: int, device: str):
    texts = [tok.apply_chat_template([{"role": "system", "content": P.SYSTEM},
                                      {"role": "user", "content": p}],
                                     tokenize=False, add_generation_prompt=True) for p in prompts]
    enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False,
              return_offsets_mapping=True)
    offsets = enc.pop("offset_mapping")
    enc = enc.to(device)
    out = model(**enc, output_hidden_states=True)
    hs = out.hidden_states
    res = []
    for b, text in enumerate(texts):
        mask = enc["attention_mask"][b].bool()
        last = int(mask.nonzero().max())               # left padding: last real token
        h = torch.stack([hs[l][b, last] for l in layers_g]).float().cpu()
        units, (q0, q1) = _spans(text)
        off = offsets[b]
        valid = mask.cpu()

        def pool(c0, c1):
            sel = valid & (off[:, 0] >= c0) & (off[:, 1] <= c1) & (off[:, 1] > off[:, 0])
            idx = sel.nonzero().squeeze(-1)
            assert idx.numel() > 0, f"empty span {c0}:{c1}"
            return hs[layer_r][b, idx.to(device)].float().mean(0).cpu()

        assert len(units) > 0, "no evidence units found"
        M = torch.stack([pool(s, e) for s, e in units])
        res.append({"h": h, "M": M})
    del hs, out
    # question-only pass (no evidence, no instructions)
    qenc = tok([f"Question: {question_of(p)}" for p in prompts], return_tensors="pt", padding=True,
               add_special_tokens=False).to(device)
    qh = model(**qenc, output_hidden_states=True).hidden_states[layer_r]
    qm = qenc["attention_mask"].unsqueeze(-1).to(qh.dtype)
    qv = ((qh * qm).sum(1) / qm.sum(1)).float().cpu()
    for b, r in enumerate(res):
        r["qv"] = qv[b]
        for k in ("h", "M", "qv"):
            assert torch.isfinite(r[k]).all(), f"non-finite {k}"
            r[k] = r[k].half()
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="03_models/Qwen2.5-3B-Instruct")
    ap.add_argument("--packets", required=True, help="jsonl with item_id, level, prompt (+label)")
    ap.add_argument("--out", required=True, help="output .pt")
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    from transformers import AutoModelForCausalLM, AutoTokenizer
    from tqdm import tqdm

    tok = AutoTokenizer.from_pretrained(args.model, padding_side="left")
    dtype = torch.float16 if args.device == "cuda" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(args.model, dtype=dtype, device_map=args.device).eval()
    L = model.config.num_hidden_layers
    layers_g, layer_r = [L // 2, (3 * L) // 4, L], round(0.6 * L)

    rows = [json.loads(l) for l in open(args.packets, encoding="utf-8")]
    if args.limit:
        rows = rows[: args.limit]
    order = sorted(range(len(rows)), key=lambda i: len(rows[i]["prompt"]))
    feats = [None] * len(rows)
    for i in tqdm(range(0, len(order), args.batch_size), desc="features"):
        idx = order[i:i + args.batch_size]
        for j, r in zip(idx, extract(model, tok, [rows[k]["prompt"] for k in idx],
                                     layers_g, layer_r, args.device)):
            feats[j] = r
    meta = [{k: v for k, v in r.items() if k != "prompt"} for r in rows]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    torch.save({"meta": meta, "feats": feats, "layers_g": layers_g, "layer_r": layer_r,
                "model": args.model}, args.out)
    print(f"saved {len(feats)} -> {args.out}")


if __name__ == "__main__":
    main()
