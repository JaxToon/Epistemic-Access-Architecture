"""Epistemic head variants (all output a support logit; sigma = sigmoid(logit)).

  probe  MLP(h)                                   generator state only (knowledge-boundary probe)
  qe     CrossAttn(question -> evidence units)    reader-like: evidence + question, NO generator state
  eag    CrossAttn(h -> evidence units) + h       generator state reads the delivered evidence
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

VARIANTS = ("probe", "qe", "eag")


class EpistemicHead(nn.Module):
    def __init__(self, d: int, n_layers_g: int, variant: str, de: int = 256, hidden: int = 256,
                 dropout: float = 0.1):
        super().__init__()
        assert variant in VARIANTS
        self.variant = variant
        self.h_norm = nn.LayerNorm(d * n_layers_g)
        self.h_proj = nn.Linear(d * n_layers_g, de)
        self.m_norm = nn.LayerNorm(d)
        self.q_norm = nn.LayerNorm(d)
        self.q_proj = nn.Linear(d, de)
        self.k_proj = nn.Linear(d, de)
        self.v_proj = nn.Linear(d, de)
        self.q0 = nn.Parameter(torch.zeros(de))   # learned global query: content-based evidence search
        fd = de if variant == "probe" else 3 * de + 2
        self.mlp = nn.Sequential(nn.Linear(fd, hidden), nn.GELU(), nn.Dropout(dropout),
                                 nn.Linear(hidden, 1))
        self.de = de

    def forward(self, h, M, mask, qv, return_attn: bool = False):
        """h [B, nl, d], M [B, k, d], mask [B, k] (True = real unit), qv [B, d] -> logit [B]."""
        hq = self.h_proj(self.h_norm(h.flatten(1)))
        if self.variant == "probe":
            return self.mlp(hq).squeeze(-1)
        query = (hq if self.variant == "eag" else self.q_proj(self.q_norm(qv))) + self.q0
        Mn = self.m_norm(M)
        K, V = self.k_proj(Mn), self.v_proj(Mn)
        scores = torch.einsum("bd,bkd->bk", query, K) / self.de ** 0.5
        scores = scores.masked_fill(~mask, float("-inf"))
        a = F.softmax(scores, dim=-1)
        c = torch.einsum("bk,bkd->bd", a, V)
        ent = -(a.clamp_min(1e-9).log() * a).sum(-1, keepdim=True)
        feat = torch.cat([query, c, query * c, a.max(-1, keepdim=True).values, ent], -1)
        logit = self.mlp(feat).squeeze(-1)
        return (logit, a) if return_attn else logit
