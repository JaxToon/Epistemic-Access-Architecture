# Pre-registration — Study 3: Same signal, advice vs authority (confirmatory)

Ditulis: 2026-10-11, **sebelum** σ dihitung pada item Studi 3 dan sebelum generasi apa pun.

## Latar
Fase 1b (pilot items) memberi hasil sekunder: σ sebagai saran tidak berbeda dari plasebo, sedangkan σ sebagai gate menurunkan halusinasi ±11 poin. Kontras primernya gagal secara desain (pencocokan cakupan tidak mungkin, karena saran menaikkan cakupan). Studi 3 mengulang pertanyaan ini secara konfirmatori pada item baru, dengan kontras yang selalu terdefinisi.

## Desain (dibekukan)
- **Item:** 400 item Studi 2 (HotpotQA dev, tidak tumpang tindih dengan pilot dan tidak pernah dipakai melatih atau mengevaluasi head EAG). Populasi primer: `open` dengan jawaban di tepat satu paragraf emas (255 item pada Studi 2).
- **Paket:** 5 paket per item, persis seperti Studi 2 (prompt extractive): `full`, `drop_ans` × {entity_rich, entity_poor}, `drop_all` × {entity_rich, entity_poor}.
- **Generator:** Qwen2.5-3B-Instruct, greedy, `max_new_tokens = 24`.
- **σ:** head `eag_lc1` (rata-rata 3 seed) yang sudah dilatih di fase 1, **tanpa pelatihan ulang**. Fitur dari Qwen2.5-3B beku, kode `eaa/eag/features.py` tanpa perubahan.
- **Lengan:**
  - `off`: output Studi 2 yang sudah ada (prompt extractive identik);
  - `advice`: teks advisory fase 1b dengan σ asli;
  - `placebo`: teks yang sama, σ diacak antar baris (seed 20261011);
  - `authority`: output `off`, σ < 0,5 → "INSUFFICIENT EVIDENCE";
  - `advice+authority`: output `advice` yang di-gate dengan aturan yang sama.
- **Label:** bertingkat; kasus ambigu baru diaudit dengan kebijakan yang sama (`audit_then_judge`), lalu dicek sensitivitasnya dengan judge-only dan strict.

## Hipotesis primer
Unit analisis = item (semua paket satu item di-resample bersama). Bootstrap B = 2000.

| ID | Hipotesis | Didukung jika |
|---|---|---|
| **P1** | Saran inert: σ asli ≈ σ acak | TOST: 90% CI dari halusinasi(advice) − halusinasi(placebo) berada di dalam ±0,02 |
| **P2** | Otoritas mengurangi halusinasi | halusinasi(authority) − halusinasi(off): estimasi ≤ −0,05 **dan** batas atas 95% CI < 0 |
| **P3** | Otoritas mengungguli saran dalam utilitas | U = benar − 2 × halusinasi; U(authority) − U(advice): batas bawah 95% CI > 0 |

Holm atas P2 dan P3 (p bootstrap dua sisi). P1 adalah uji ekuivalensi tersendiri.

**Kendala biaya (dilaporkan, bukan hipotesis):** kenaikan false refusal pada `full` (authority − off), dengan batas atas 95% CI yang dilaporkan. Ambang kegagalan praktis: > 0,15.

## Kriteria gagal
- P1 gagal (saran dan plasebo berbeda) → generator *memakai* σ dalam prompt. Klaim "saran inert" ditarik.
- P2 atau P3 gagal → klaim "otoritas efektif" tidak direplikasi pada item baru.

## Sekunder / eksploratif (diberi label)
λ ∈ {1, 4} untuk U; kurva risk–coverage authority (τ disapu) dengan titik advice dan placebo; per level kanal; `advice+authority`; replikasi pada keluarga model non-Qwen (Studi 3b, didaftarkan terpisah sebelum dijalankan).

## Studi 3b — generator non-Qwen (ditambahkan 2026-10-11, sebelum data apa pun dibuat)
- **Generator:** Gemma 4 E4B instruction-tuned (`gemma4:e4b` via Ollama 0.40.2), `temperature = 0`, `seed = 0`, `think = false`, `num_predict = 24`. Determinisme dicek: 3 panggilan identik menghasilkan output identik.
- **σ tetap dari reader Qwen2.5-3B + head `eag_lc1`**, dihitung pada prompt paket yang sama. Ini secara eksplisit arsitektur *reader ≠ generator*. σ tidak bergantung pada generator, jadi σ yang sama dipakai untuk kedua generator.
- **Lengan:** `off`, `advice`, `placebo` (ketiganya digenerasi baru dengan Gemma), `authority` (= off Gemma di-gate σ < 0,5), `advice+authority`.
- **Hipotesis P1–P3 identik** dengan Studi 3, dengan Holm terpisah per generator.
- **Sekunder (replikasi Studi 2 pada Gemma):** selective risk full → drop_ans, proporsi karangan yang disalin dari paket, dan rich vs poor. Dilaporkan sebagai replikasi; hipotesis S2-H1..H4 dipakai apa adanya.

## Benchmark gate vs metode standar (ditambahkan 2026-10-11, sebelum baseline dihitung)
**Tujuan:** memposisikan σ (EAG) terhadap sinyal ketidakpastian yang umum dipakai di literatur. Status: **sekunder / benchmarking**, bukan uji hipotesis baru.

**Data:** output `off` Qwen2.5-3B pada Studi 3 (populasi primer, 255 item × 5 paket).

**Skor pembanding:** semuanya dihitung dengan Qwen2.5-3B yang sama; makin tinggi = makin yakin jawaban benar.
1. `seq_conf`: rata-rata log-prob token jawaban greedy (sequence likelihood).
2. `p_true`: P("True") vs P("False") untuk pertanyaan "Is the proposed answer correct and supported by the evidence?" dengan evidence di konteks (gaya Kadavath dkk. 2022).
3. `self_consistency`: proporsi 5 sampel (temperature 0,7, top-p 0,95, seed tetap) yang sama dengan jawaban greedy setelah normalisasi. Ini aproksimasi string-level dari semantic entropy (bukan clustering NLI).
4. `reader_p_suff`: skor reader berbasis prompt (sama dengan pilot).
5. `eag_sigma`: σ dari head `eag_lc1`.
6. `oracle_full`: level == full.

**Metrik:**
- AURC pada jawaban substantif (tie-aware), dengan selisih berpasangan terhadap `eag_sigma` (bootstrap item, B = 2000);
- AUROC benar-vs-halusinasi di antara jawaban;
- **gate pada cakupan yang sama:** ambang tiap skor dipilih supaya laju menjawab sama dengan gate σ < 0,5, lalu dilaporkan halusinasi, benar, dan false refusal @full.

Tidak ada pemilihan hiperparameter setelah melihat hasil.
