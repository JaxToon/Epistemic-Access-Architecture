# Epistemic Access Architecture (EAA) — Pilot #1

*[English](README.md) · Bahasa Indonesia*

Uji kausal: apakah memotong kanal evidence reader→generator menaikkan halusinasi (H1), apakah membukanya kembali memulihkan (H2), dan apakah epistemic state yang **wajib diikuti** lebih efektif daripada yang hanya **disampaikan** (H3), tanpa false refusal berlebihan (H4). Desain lengkap: [00_docs/02_hypothesis_and_pilot_design_v0.1.md](00_docs/02_hypothesis_and_pilot_design_v0.1.md).

## Struktur

```
00_docs/        konteks, literature matrix, desain, research_log.md
01_data/        sampel HotpotQA + manifest (sha256)   [raw/ tidak di-commit]
configs/        config eksperimen (kunci sebelum run penuh)
eaa/            kode: data, conditions, prompts, backends, run, evaluate, analyze
05_outputs/     generations.jsonl, packets.jsonl, exclusions.json per run
06_evaluation/  eval.csv per run (label per item × sistem × bandwidth)
07_analysis/    summary.md, tabel kontras, plot kurva bandwidth
tests/          invariant pembentuk kondisi + labeling
.claude/agents/ agent riset: literature-scout, methodology-critic, experiment-runner, stats-analyst
```

## Menjalankan

```bash
python -m pytest tests -q                                            # invariant desain
python -m eaa.run --config configs/pilot_v0.1.yaml --backend mock --run-name mock_smoke --limit 20
python -m eaa.run --config configs/pilot_v0.1.yaml --limit 5 --run-name smoke_qwen3b   # GPU smoke
python -m eaa.run --config configs/pilot_v0.1.yaml                   # run penuh (resumable)
python -m eaa.evaluate --config configs/pilot_v0.1.yaml
python -m eaa.analyze  --config configs/pilot_v0.1.yaml
```

Sampel data dibuat ulang dengan:
`python -c "from pathlib import Path; from eaa.data import build_sample; build_sample(Path('01_data/raw'), Path('01_data'), 500, 20261005)"`

## Kondisi per item

| Sistem | Apa yang terjadi | Hipotesis |
|---|---|---|
| `closed_book` | tanpa evidence → label `param_known` | kontrol |
| `off` @ BW 100/75/50/25/0 | evidence saja; unit emas yang dibuang diganti pengisi dengan panjang setara, di posisi yang sama | H1 |
| `advisory` @ BW | evidence + verdict reader, generator boleh mengabaikan | H3 |
| `enforced` @ BW | seperti advisory, tetapi verdict `INSUFFICIENT` ⇒ sistem abstain | H3, H4 |
| `enforced_oracle` @ BW | `off` digate oleh kecukupan oracle (batas atas) | referensi |
| `restored` | dua giliran: jawab di BW-25, lalu kanal dibuka ke 100% | H2 |

## Catatan desain

- Reader dan generator memakai backbone yang sama dalam pemanggilan terpisah, sehingga hasil tidak bisa dijelaskan oleh perbedaan kapasitas model.
- Dengan 2 supporting facts, BW-75 dibulatkan menjadi 2/2 dan BW-25 menjadi 1/2. Karena itu analisis juga memakai `gold_kept_frac` aktual (slope H1).
- "Cukup menurut oracle" didefinisikan sebagai semua supporting facts tersampaikan. Ini pendekatan konservatif, karena sebagian fakta HotpotQA bisa redundan.
- `correct` = EM atau token-F1 ≥ 0.5. Wajib diaudit manual pada sampel sebelum klaim.
