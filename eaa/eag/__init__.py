"""Epistemic Authority Gate (EAG) — phase 1: frozen backbone, trainable epistemic head.

build_train.py  HotpotQA-train counterfactual packets (same channel construction as the pilot)
features.py     one frozen forward pass per packet -> h_t0 (generator state at the commitment
                point), M (evidence units, mean-pooled), qv (question span, mean-pooled)
model.py        head variants: probe (h only), qe (question->evidence, no generator state), eag
train.py        BCE(sigma, answer_available) + contrastive margin (full vs drop_ans)
evaluate.py     gate the pilot's generator outputs with sigma -> AURC, access sensitivity
"""
