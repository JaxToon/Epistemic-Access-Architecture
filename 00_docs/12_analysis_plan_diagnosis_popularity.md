# Rencana Analisis: Diagnosis "Tahu tapi Tidak Mengungkap" dan Popularitas Entitas

Ditulis 17 Oktober 2026, **sebelum** log-prob, *logit lens*, *closed-book* Studi 2/3, atau *pageviews* dihitung. Status: **eksploratif** (data sudah ada; bukan uji konfirmatori). Konteks: `11_rencana_lanjutan_pasca_masukan_dosen.md`, Fase 1 dan 2.

## Data

- Item Studi 2/3 (`01_data/hotpot_dev_study2_n400_seed20261006.jsonl`), *generator* Qwen2.5-3B-Instruct, *prompt* ekstraktif (identik dengan lengan `off` Studi 3).
- **Populasi utama:** item primer (soal terbuka dengan paragraf jawaban yang terdefinisi tunggal), kondisi `full`, n = 255.
- Kelompok menurut label `off` di `07_analysis/study3/qwen2.5-3b/eval.csv`: **benar** (125), **halusinasi** (71), **abstain** (59).

## Fase 1. Diagnosis

### Ukuran (Qwen2.5-3B fp16, *teacher forcing*, *chat template* dan *system prompt* yang sama dengan generasi)

| Kode | Ukuran |
| --- | --- |
| LP_gold | Rata-rata log-prob per token dari string jawaban emas HotpotQA, sebagai lanjutan *prompt* |
| LP_own | Rata-rata log-prob per token dari keluaran model sendiri (`off`) |
| LP_abs | Rata-rata log-prob per token dari "INSUFFICIENT EVIDENCE" |
| R_final | Peringkat token pertama jawaban emas di t₀ (posisi terakhir *prompt*), lapisan akhir |
| R_lens | Peringkat token pertama jawaban emas di t₀ untuk setiap lapisan (*logit lens*: norm akhir + `lm_head` pada *hidden state* tiap lapisan); dicatat peringkat minimum dan lapisannya |
| ΔLP_ctx | LP_gold(`full`) − LP_gold(`drop_ans`, rata-rata dua kebijakan pengecoh): seberapa besar konteks lengkap menaikkan peluang jawaban emas |
| CB | Jawaban *closed-book* (pertanyaan saja, *prompt* `CLOSED_BOOK`), diberi label dengan `evaluate.label` yang sama |

### Klasifikasi kasus halusinasi (ditetapkan sekarang)

- **K1 "tahu tapi tidak mengungkap", primer:** LP_gold > LP_own. Model sendiri memberi peluang per token lebih tinggi pada jawaban emas daripada pada jawaban yang ia keluarkan.
- **K1 longgar, sekunder:** R_final ≤ 5.
- **K2 "tidak tahu":** LP_gold ≤ LP_own **dan** R_final > 5.
- **Sumber pengetahuan:** CB benar berarti jawaban tersedia di memori internal; CB tidak benar berarti jawaban hanya tersedia dari konteks.

### Jenis kesalahan (heuristik, ditetapkan sekarang; untuk kelompok halusinasi)

1. **Berhenti di hop pertama:** keluaran (dinormalisasi) sama dengan judul paragraf emas yang *bukan* paragraf jawaban, atau termuat di dalamnya.
2. **Salin dari pengecoh:** keluaran termuat di teks unit pengecoh dalam paket.
3. **Salin dari paragraf emas, entitas lain:** termuat di teks unit emas, tetapi bukan jawaban.
4. **Parsial/format:** F1 token terhadap jawaban emas > 0 (sudah dinilai salah oleh aturan atau *judge*).
5. **Lainnya.**

Urutan prioritas jika lebih dari satu berlaku: 1 → 4 → 3 → 2 → 5.

### Pembanding

- Distribusi LP_gold, R_final, dan R_lens pada kelompok **benar** sebagai acuan "tahu dan mengungkap".
- ΔLP_ctx per kelompok.
- Kelompok **abstain**: LP_gold vs LP_abs. Jika LP_gold > LP_abs, penolakan terjadi walaupun jawaban emas lebih disukai.

### Pelaporan

Proporsi K1/K2 beserta IK 95% (Wilson), median ukuran per kelompok, dan tabulasi silang K1 × sumber pengetahuan × jenis kesalahan. Uji perbedaan antarkelompok: Mann–Whitney (eksploratif, tanpa koreksi; dilaporkan sebagai deskriptif).

### Titik keputusan (dari dokumen 11)

Jika K1 primer < 20% dari 71 kasus halusinasi, *steering* dipandang memiliki ruang pemulihan kecil pada populasi ini.

## Fase 2. Popularitas entitas

- **Ukuran:** *pageviews* bulanan Wikipedia bahasa Inggris (Wikimedia REST API, `all-access`, `user`), Januari–Desember 2025, untuk kedua judul paragraf emas. Judul yang tidak ditemukan diberi nilai 0 dan dicatat.
- **Popularitas item, primer:** rata-rata log10(1 + *views*) kedua judul emas. **Sekunder:** minimum (hop yang paling jarang).
- **Hasil yang diuji (lengan `off`, `full`, populasi utama):** benar, halusinasi, abstain (*false refusal*), penolakan oleh *gate* (σ < 0,5), dan kasus "σ ≥ 0,5 tetapi salah".
- **Analisis:**
  - regresi logistik tiap hasil terhadap popularitas (terstandar), dengan *bootstrap* item 2.000× untuk IK 95%;
  - tabel per kuartil popularitas;
  - Spearman popularitas vs σ.
- **Sekunder:** halusinasi pada `drop_ans` terhadap popularitas (apakah entitas populer lebih sering "diisi" dari memori), dan K1 terhadap popularitas.
- **Titik keputusan:** jika tidak ada hubungan (IK memuat 0 untuk semua hasil primer), sudut *knowledge collapse* lewat popularitas dinyatakan lemah pada data ini.

## Yang tidak boleh dilakukan

- Mengubah definisi K1/K2, jenis kesalahan, atau ukuran popularitas setelah melihat hasil. Perubahan apa pun dicatat sebagai deviasi beserta alasannya.
- Menyebut hasil ini konfirmatori.

## Deviasi dan catatan setelah hasil Fase 1 (17 Okt 2026)

1. **K1 primer (LP_gold > LP_own) cacat secara konstruksi.** Keluaran `off` berasal dari *greedy decoding*, yang memilih token paling mungkin di setiap langkah. Akibatnya LP_own ≈ 0 (median −0,010), dan K1 = 0/71 adalah tautologi, bukan temuan. Hal yang sama berlaku untuk "LP_gold > LP_abs" pada kelompok abstain. Kesalahan ini ada di rencana, bukan di kode. Kriteria ini **tidak dipakai** untuk titik keputusan.
2. **Yang dipakai sebagai gantinya:** K1 longgar (R_final ≤ 5), yang sudah ditetapkan sebelumnya sebagai sekunder, ditambah sebaran R_final dan ΔLP_ctx (deskriptif).
3. **Uji yang tepat untuk "tahu tapi tidak mengungkap"** adalah pembandingan *internal* vs *eksternal* ala Gekhman dkk. (COLM 2025): *probe* pada *hidden state* yang menilai kandidat jawaban, dibandingkan dengan peringkat dari distribusi keluaran. Ini direncanakan sebagai Fase 1b dengan rencana analisis tersendiri sebelum dijalankan.
4. **Derau label:** sebagian string emas HotpotQA tidak berbentuk jawaban (mis. "It lies two kilometres WSW of Mount Everest."), dan beberapa "halusinasi" nyaris benar (mis. "Chevrolet Corvette" vs "Chevrolet Corvette Stingrays"). Peringkat token pertama untuk emas yang panjang atau aneh kurang bermakna.
