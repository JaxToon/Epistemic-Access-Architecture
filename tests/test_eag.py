import numpy as np
import torch

from eaa.eag.features import _spans
from eaa.eag.model import VARIANTS, EpistemicHead
from eaa.eag.train import auroc, train_one


def test_spans():
    text = ("sys\nEvidence:\n[e1] (A) first unit.\n[e2] (B) second unit.\n\n"
            "Question: who is it?\nAnswer:<|im_end|>")
    units, (q0, q1) = _spans(text)
    assert [text[s:e] for s, e in units] == ["[e1] (A) first unit.", "[e2] (B) second unit."]
    assert text[q0:q1] == "who is it?"


def test_head_shapes_and_mask():
    for v in VARIANTS:
        m = EpistemicHead(16, 3, v, de=8, hidden=8).eval()
        h, M, qv = torch.randn(4, 3, 16), torch.randn(4, 5, 16), torch.randn(4, 16)
        mask = torch.ones(4, 5, dtype=torch.bool)
        mask[:, 3:] = False
        out = m(h, M, mask, qv)
        assert out.shape == (4,) and torch.isfinite(out).all()
        if v != "probe":
            M2 = M.clone()
            M2[:, 3:] += 100.0          # masked units must not matter
            assert torch.allclose(out, m(h, M2, mask, qv), atol=1e-5)


def _synthetic(n_items=100, d=16, seed=0):
    """Label depends on whether a 'signal' unit is in the packet; h is uninformative."""
    g = torch.Generator().manual_seed(seed)
    sig = torch.randn(d, generator=g)
    meta, feats = [], []
    for i in range(n_items):
        split = "train" if i < 75 else "val"
        for lv in ["full", "drop_ans", "drop_other", "drop_all"]:
            has = lv == "full"
            M = torch.randn(6, d, generator=g) * 0.3
            if has:
                M[0] += sig
            meta.append({"item_id": f"i{i}", "level": lv, "split": split, "label": int(has),
                         "qclass": "open", "answer_para_defined": True})
            feats.append({"h": torch.randn(3, d, generator=g).half(), "M": M.half(),
                          "qv": torch.randn(d, generator=g).half()})
    return {"meta": meta, "feats": feats}


def test_eag_learns_from_evidence_but_probe_cannot():
    data = _synthetic()
    va = [i for i, m in enumerate(data["meta"]) if m["split"] == "val"]
    y = np.array([data["meta"][i]["label"] for i in va])
    from eaa.eag.train import predict
    res = {}
    for v in ["probe", "eag"]:
        model, hist, n_pairs = train_one(data, v, 1.0, 0, "cpu", epochs=40)
        res[v] = auroc(y, predict(model, data["feats"], va, "cpu"))
        assert n_pairs == 75
    assert res["eag"] > 0.8 and res["eag"] > res["probe"] + 0.15


def test_aurc_tie_aware_and_ordering():
    from eaa.eag.evaluate import aurc
    err = np.array([1, 0, 0, 1, 0, 0, 0, 1])
    # all scores tied -> expected risk equals the error rate at every coverage
    assert abs(aurc(np.zeros(8), err) - err.mean()) < 1e-12
    # perfect gate (errors ranked last) beats the reverse ranking
    good, bad = aurc(-err.astype(float), err), aurc(err.astype(float), err)
    assert good < err.mean() < bad


def test_question_of():
    from eaa.eag.features import question_of
    assert question_of("Evidence:\n[e1] (A) x\n\nQuestion: who is it?\nAnswer:") == "who is it?"
