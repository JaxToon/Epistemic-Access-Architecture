# Pre-registration — EAG Phase 1

Ditulis: 2026-10-05, **sebelum** fitur test diekstrak dan sebelum head mana pun dievaluasi pada data pilot.
Kode: `eaa/eag/` (build_train, features, model, train, evaluate). Perubahan setelah tanggal ini wajib dicatat di `research_log.md` sebagai deviasi.

## 1. Setup tetap

- **Backbone beku:** Qwen2.5-3B-Instruct (fp16), yaitu generator pilot yang sama.
- **Fitur:**
  - h = hidden state di posisi terakhir prompt generator (commitment point) pada layer {18, 27, 36};
  - M = unit evidence di-mean-pool pada layer 22;
  - qv = span pertanyaan di-mean-pool pada layer 22.
  (L = 36 → L/2, 3L/4, L, dan round(0.6L).)
- **Data latih:** HotpotQA *train*, 6.000 item train + 1.000 val (seed 20261005), masing-masing 4 level kanal. Label: `full` = 1; level parsial = string jawaban ada di paket.
- **Data uji:** sampel pilot 493 item dev (tidak pernah dipakai untuk training). Gate dievaluasi pada output **`off`** pilot (Qwen2.5-3B, greedy), yaitu jawaban yang identik untuk semua gate.
- **Varian** (masing-masing 3 seed {0, 1, 2}, skor dirata-rata antar seed):
  - `probe`: hanya h
  - `qe`: pertanyaan → evidence, tanpa state generator
  - `eag`: h → evidence + h, λ_c = 1
  - `eag_lc0`: eag tanpa loss kontrastif
- **Pembanding:** `reader_p_suff` (skor reader LLM berbasis prompt), gate acak (= laju halusinasi), dan oracle (`answer_available`).
- **Hyperparameter dibekukan** (train.py): d_e = 256, hidden = 256, dropout = 0.1, AdamW lr = 1e-3, wd = 0.01, batch = 256, maks 30 epoch, patience 5 pada val BCE, γ = 2.

## 2. Hipotesis dan aturan keputusan

Populasi primer: `primary` (open, jawaban di tepat satu paragraf emas). Metrik utama: **AURC** atas output `off` di keempat level (lebih rendah = lebih baik), dengan CI bootstrap per item (B = 1000).

| ID | Hipotesis | Didukung jika | Gagal jika |
|---|---|---|---|
| **H5a** | EAG lebih baik dari gate reader berbasis prompt | AURC(eag) − AURC(reader_p_suff) < 0, dengan 95% CI tidak memuat 0 | CI memuat 0 atau > 0 |
| **H5b** | Akses ke evidence menambah nilai di atas state generator | AURC(eag) − AURC(probe) < 0, dengan 95% CI tidak memuat 0 | probe ≈ eag → gate hanyalah knowledge-boundary probe |
| **H5c** | State generator menambah nilai di atas reader | AURC(eag) < AURC(qe), dengan CI tidak memuat 0 | qe ≈ eag → "generator state" tidak berperan (justru hasil yang menarik, dilaporkan apa adanya) |
| **H6** | Supervisi intervensi kanal meningkatkan access sensitivity | Δσ = σ(full) − σ(drop_ans) lebih besar untuk eag (λ_c = 1) daripada eag_lc0, dan AURC tidak memburuk | Tidak ada perbedaan |

Hasil yang dilaporkan apa pun hasilnya: AUROC σ terhadap `answer_available`, AUROC σ untuk benar-vs-halusinasi di antara jawaban, dan tabel lengkap semua varian.

Koreksi multipel: H5a, H5b, dan H5c dianggap satu famili (Holm atas p bootstrap dua sisi).

## 3. Langkah berikutnya bergantung hasil (diputuskan sekarang)

- **H5a dan H5b didukung** → fase 1b: *σ advisory vs σ authoritative*. σ yang sama dimasukkan ke prompt generator ("support score: x"), lalu dibandingkan dengan hard gate. Ini satu-satunya kontribusi yang bertahan dari deep-read prior art. Keterbatasan yang dicatat: varian advisory di fase 1b tidak di-fine-tune (deep-read menyarankan fine-tune untuk perbandingan yang adil; itu fase 2).
- **H5b gagal** (probe ≈ eag) → laporkan sebagai temuan: pada skala 3B, "kecukupan evidence" sudah terkode di state generator. Pertanyaannya bergeser ke **otoritas** (H3), bukan akses.
- **Semua gagal** → gate terlatih tidak mengalahkan reader berbasis prompt. EAG ditunda; fokus pada temuan pilot.

## 4. Baseline yang wajib ditambahkan sebelum klaim publikasi (dari deep-read, bukan bagian fase 1)

CAA-style LoRA pada data yang identik (2608.29934), RINSE (2609.37469), dan Critic-Driven Decoding yang diadaptasi (2310.16964). Fase 1 hanya uji kelayakan internal.

## 5. Amandemen v0.2 — 2026-10-05, sebelum fitur uji diekstrak dan sebelum hasil apa pun

Dasar: review methodology-critic. Semua perubahan dibuat **tanpa melihat data uji**.

1. **Target training = kecukupan** (1 hanya pada `full`). Sebelumnya: "string jawaban ada di paket". Alasan: label lama memberi 1 pada `drop_other` (bridge hilang) di 93% baris, sehingga σ belajar "ada kandidat jawaban", padahal itu pola halusinasi multi-hop. `answer_available` tetap dilaporkan sebagai oracle sekunder.
2. **`drop_other` ditahan dari train dan val.** Level ini dipakai hanya di uji, sebagai **intervensi yang tidak pernah dilatih**.
3. **H6 dioperasionalkan ulang** (versi lama tautologis karena loss mengoptimalkan Δσ(full − drop_ans) secara langsung). H6 didukung jika:
   - Δσ_untrained = σ(full) − σ(drop_other) lebih besar untuk eag_lc1 daripada eag_lc0 (95% CI bootstrap > 0), **dan**
   - AURC non-inferior: CI atas AURC(eag_lc1) − AURC(eag_lc0) < **0,005**.
4. **Populasi AURC primer** = item primer **dengan `answered == 1`** pada output `off`. Gate hanya bisa menahan jawaban substantif, dan baris yang sudah abstain akan terhitung sebagai error 0. Semua-baris dilaporkan sebagai sekunder. AURC dihitung **tie-aware**.
5. **H5a/H5b/H5c** dihitung dalam satu bootstrap item berpasangan (B = 1000); Holm atas tiga p dua-sisi.
6. **Penafsiran ulang varian:**
   - `probe` = probe **kontekstual** (h sudah melihat evidence), bukan probe batas pengetahuan parametrik.
   - `qe` = σ dari unit evidence + pertanyaan yang dienkode **terpisah**: forward khusus pertanyaan, tanpa evidence dan tanpa state generator. Pada v0.1 qv di-pool dari dalam prompt generator, sehingga sudah melihat evidence.
   - Semua varian dilatih dengan loss yang sama (λ_c = 1); hanya eag_lc0 yang tanpa hinge.
   - BCE dihitung pada baris batch saja; partner kontrafaktual hanya masuk hinge.
7. **Baseline tambahan:**
   - `cue_only`: regresi logistik pada fitur permukaan paket (jumlah judul unik/berulang, overlap pertanyaan–judul/evidence, panjang), dilatih pada paket train yang sama;
   - `oracle_full` (level == full);
   - `oracle_answer` (`answer_available`).

   Jika eag ≈ cue_only, keunggulan apa pun dianggap artefak konstruksi.
8. **Status H5a:** uji kelayakan, bukan klaim. Head disupervisi in-distribution (prosedur konstruksi sama dengan uji), sedangkan reader zero-shot.
9. **Fase 1b:**
   - **Kontras primer:** selective risk(authority@matched) − selective risk(sigma_advisory). τ* dipilih supaya laju menjawab hard gate sama dengan laju menjawab advisory; ini cakupan yang disamakan.
   - **Sekunder:** akurasi pada kontras yang sama, authority@0.5, dan hasil 3 kategori.
   - **Kontrol plasebo wajib:** teks advisory identik dengan σ diacak antar-baris.
   - Skor yang dipakai: `eag_lc1` (rata-rata 3 seed).
