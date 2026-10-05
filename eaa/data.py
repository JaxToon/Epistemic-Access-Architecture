"""HotpotQA (distractor) download + fixed-seed sampling with an auditable manifest."""
from __future__ import annotations

import hashlib
import json
import random
import urllib.request
from pathlib import Path

PARQUET_URL = (
    "https://huggingface.co/api/datasets/hotpotqa/hotpot_qa/parquet/distractor/validation/0.parquet"
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download_dev(raw_dir: Path) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    out = raw_dir / "hotpot_qa_distractor_validation.parquet"
    if not out.exists():
        urllib.request.urlretrieve(PARQUET_URL, out)
    return out


def _to_item(row) -> dict:
    ctx = row["context"]
    sf = row["supporting_facts"]
    return {
        "id": row["id"],
        "question": row["question"],
        "answer": row["answer"],
        "type": row["type"],
        "level": row["level"],
        "context": [
            {"title": t, "sentences": [str(s) for s in sents]}
            for t, sents in zip(ctx["title"], ctx["sentences"])
        ],
        "supporting_facts": [
            {"title": t, "sent_id": int(i)} for t, i in zip(sf["title"], sf["sent_id"])
        ],
    }


def build_sample(raw_dir: Path, out_dir: Path, n: int, seed: int) -> Path:
    import pandas as pd

    parquet = download_dev(raw_dir)
    df = pd.read_parquet(parquet)
    items = [_to_item(r) for _, r in df.iterrows()]
    items.sort(key=lambda x: x["id"])
    rng = random.Random(seed)
    sample = rng.sample(items, n)

    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"hotpot_dev_n{n}_seed{seed}.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for it in sample:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    manifest = {
        "source_url": PARQUET_URL,
        "source_file": parquet.name,
        "source_sha256": _sha256(parquet),
        "source_n_items": len(items),
        "sample_file": out.name,
        "sample_sha256": _sha256(out),
        "n": n,
        "seed": seed,
        "sampling": "sorted by id, random.Random(seed).sample",
    }
    (out_dir / f"{out.stem}.manifest.json").write_text(json.dumps(manifest, indent=2))
    return out


def load_items(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
