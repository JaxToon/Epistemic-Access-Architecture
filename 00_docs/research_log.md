# Research Log

## 2026-10-05

- Membaca 3 dokumen awal; literature matrix v0.1 (`01_literature_matrix_v0.1.md`).
- Arah dikonfirmasi user: fokus **kanal reader↔generator + arbitrase**, bukan pivot ke akses parametrik.
- Desain pilot v0.1 ditulis (`02_hypothesis_and_pilot_design_v0.1.md`).
- **Perubahan dari desain v0.1 saat implementasi:**
  - Kondisi C7/C8 (advisory/enforced) dijalankan pada **semua** bandwidth, bukan hanya BW-50/25. Hasilnya desain faktorial bandwidth × arbitrase, dan kurva lengkapnya bisa dibandingkan.
  - `enforced` diturunkan dari keluaran `advisory` + gate verdict reader, tanpa pemanggilan generator terpisah. Prompt-nya identik, jadi hasilnya setara dan menghemat komputasi.
  - Ditambah `enforced_oracle` (off + gate oracle) sebagai batas atas arbitrase.
  - `restored` dijalankan sebagai **dua giliran** (jawab di BW-25, lalu evidence penuh), bukan single-turn yang identik dengan BW-100. Ini menguji apakah jawaban awal yang salah "melekat" (anchoring).
- Data: HotpotQA distractor validation (7.405 item) → sampel 500, seed 20261005, manifest + sha256 di `01_data/`.
- Kode pipeline `eaa/` + 7 unit test (invariant kondisi) lolos. Smoke test mock 20 item end-to-end OK; panjang prompt antar bandwidth setara (±1%).
- Agent riset dibuat di `.claude/agents/`: literature-scout, methodology-critic, experiment-runner, stats-analyst.
- Lingkungan: RTX 5050 Laptop 8 GB, torch 2.12 cu128, transformers 5.12; model Qwen2.5-3B-Instruct (fp16).

### v0.2 — perbaikan setelah review methodology-critic (sebelum run GPU apa pun)
Temuan review dan perbaikannya:
1. **Pembulatan bandwidth meruntuhkan level** (66% item punya 2 supporting facts) → kanal dimanipulasi per **paragraf emas**. Setiap item punya tepat 2 paragraf emas (terverifikasi 500/500). Level: `full`, `drop_ans`, `drop_other`, `drop_all`.
2. **Jawaban bocor lewat judul paragraf / unit tersisa** (57% paket BW-25 masih memuat jawaban) → oracle = `answer_available`, dihitung dari paket yang benar-benar dirender. Smoke check: hanya 3% paket `drop_ans` yang masih memuat jawaban.
3. **H3 advisory→enforced tautologis** → H3b diganti menjadi *selective risk* (halusinasi/terjawab). Selisih 0 berarti gate tidak lebih baik dari gate acak dengan laju abstain yang sama.
4. **Restored ter-confound oleh format dua giliran** → ditambah `restored_ctrl` (full→full, follow-up identik). Ekuivalensi diuji dengan TOST, margin 0.05 dikunci di config. Hasil dilaporkan per status giliran-1.
5. **Label abstain/correct** → abstain = prefix token; `non_answer` dijadikan kelas terpisah; correct = EM atau gold ⊂ pred (bukan F1 ≥ 0.5); `unsupported_correct` diimplementasikan.
6. **Tebakan struktural** → `qclass` (open / yesno / answer_in_question). Populasi primer = open dengan jawaban di tepat satu paragraf emas. Item yes/no tidak dihitung `param_known`.
7. **Statistik** → semua kontras dihitung per level (satu baris per item per sisi), sehingga McNemar valid; Holm hanya untuk famili primer. *Deviasi:* GLMM dari desain B6 belum diimplementasikan (statsmodels tidak terpasang); diganti bootstrap per item + McNemar per level.
8. **Kebocoran via reader** → advisory primer berisi verdict saja; `advisory_missing` menjadi kontrol sekunder dengan cek kebocoran berbasis overlap/F1.
9. **Kontrol panjang dan batching** → `len_ratio_vs_full` dicatat per paket; flag `--batch-size 1` disediakan untuk cek noise batching pada subsampel (belum dijalankan).

### Smoke test GPU (5 item, Qwen2.5-3B fp16) → v0.2.1
- Model dipindah ke `03_models/Qwen2.5-3B-Instruct`, karena cache HF gagal membuat symlink di Windows (WinError 1314).
- Reader 3B hampir selalu mengeluarkan verdict teks `INSUFFICIENT`, termasuk pada `full`. Gate teks (`enforced`) jadi hampir selalu abstain. **Ditambahkan** `reader_score`: P(SUFFICIENT) dari log-prob kontinuasi `{"verdict": "` → `enforced_score` (τ = 0.5, pre-registered) + AURC (gate skor vs acak vs oracle). Di smoke test, skor memisahkan `full` (0.14–0.84) dari `drop_*` (≈0). Skor ini juga menjadi baseline langsung untuk EAG.
- Pada kondisi advisory, generator meniru kata verdict ("INSUFFICIENT") → dihitung non_answer. Regex non_answer diperluas ("cannot be definitively determined").
- Observasi: pada item Ptolemaic, model salah di `off/full`, tetapi benar di `restored` *dan* `restored_ctrl` (efek follow-up "answer again"). Ini konfirmasi bahwa kontrol `restored_ctrl` diperlukan.
- Run penuh dimulai: `05_outputs/pilot_v0.2_qwen2.5-3b/` (500 item).

### Prior art EAG (literature-scout) → `04_prior_art_EAG_v0.1.md`
- Semua komponen EAG sudah ada secara terpisah: gated cross-attn adapter (Flamingo/RETRO/TokenMem), mixture σ·P_gen (pointer-generator, kNN-LM), skor support per token yang mengontrol decoding (Critic-Driven Decoding, Lookback Lens, Token-Guard), abstensi terlatih (R-Tuning), dan pelatihan kontrafaktual evidence-dihapus→abstain (Compression-Aware Abstention, Aug 2026).
- Kombinasi lengkapnya belum ditemukan. Pembingkaian yang disarankan: EAG sebagai **alat kausal untuk H3** (σ advisory vs σ authoritative pada modul yang sama), bukan mekanisme gate baru.
- Wajib baca penuh: arXiv 2608.29934, 2310.16964, 2607.22625, 2609.37469.
