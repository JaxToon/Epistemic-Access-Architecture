# Pre-registration — Study 2: Evidence-anchored confabulation

Ditulis: 2026-10-05, setelah pilot #1 (temuan eksploratif) dan **sebelum** data Studi 2 dibuat.

## Latar belakang (eksploratif, dari pilot #1)
Pada pilot (Qwen2.5-3B, 311 item primer), ketika paragraf jawaban dicabut (`drop_ans`), laju halusinasi hampir sama dengan `full`. Namun:
- hanya 1,1% jawaban karangan sama dengan jawaban closed-book;
- 78% adalah string yang **disalin dari paket yang tersisa**;
- pada `drop_all`, 93% disalin dari kalimat pengecoh.

Hipotesis kerja: ketika akses ke evidence kunci diblokir, model merakit jawaban dari kandidat yang **kebetulan tersedia** di evidence parsial. Ini analog fungsional dari "interpreter" split-brain. Pola ini ditemukan pasca-hoc, sehingga perlu konfirmasi pada data baru dengan manipulasi kausal.

## Desain
- **Item baru:** 400 item HotpotQA dev, **tidak termasuk** 500 item pilot, seed 20261006. Populasi primer: `open` dengan jawaban di tepat satu paragraf emas.
- **Manipulasi (dalam item):** kalimat pengisi yang menggantikan paragraf yang dicabut dipilih dengan dua kebijakan:
  - `entity_rich`: di antara kandidat dengan panjang setara (±15% token), pilih yang **paling banyak** kandidat bertipe jawaban (angka untuk jawaban numerik, span kapital non-awal-kalimat untuk lainnya);
  - `entity_poor`: pilih yang **paling sedikit**.

  Posisi, jumlah slot, unit non-emas, dan pertanyaan identik. `full` identik di kedua kebijakan.
- **Level:** `full`, `drop_ans` × {rich, poor}, `drop_all` × {rich, poor}.
- **Prompt:**
  - `extractive` (prompt pilot: "Answer the question using only the evidence below…");
  - `open` (evidence "may or may not be relevant", tanpa batasan "only the evidence"; aturan abstain sama).
- **Model:** Qwen2.5-3B-Instruct (utama). Replikasi skala: Qwen2.5-1.5B-Instruct dan, bila waktu cukup, Qwen2.5-7B-Instruct 4-bit.
- **Correctness:** bertingkat (`eaa/judge.py`, judge Qwen2.5-7B). Halusinasi = substantif dan tidak benar.

## Hipotesis (konfirmatori)

| ID | Prediksi | Uji |
|---|---|---|
| **S2-H1** | Pada `drop_ans`, halusinasi lebih tinggi dengan pengisi `entity_rich` daripada `entity_poor` (prompt extractive) | McNemar exact, berpasangan per item, satu sisi tidak dipakai; laporkan selisih + bootstrap 95% CI |
| **S2-H2** | Sama, pada `drop_all` | sama |
| **S2-H3** | Pada `drop_ans` (extractive, gabungan kedua kebijakan), ≥ 50% jawaban karangan adalah string yang muncul di paket yang dikirim | proporsi + Wilson 95% CI; didukung jika batas bawah > 0,5 |
| **S2-H4** | S2-H1 dan S2-H3 juga berlaku dengan prompt `open` (penyalinan bukan semata artefak instruksi ekstraktif) | uji yang sama pada prompt `open` |

Famili Holm: S2-H1, S2-H2, dan S2-H1(open). S2-H3 dan S2-H4 (proporsi) dilaporkan dengan CI.

**Cek manipulasi (wajib dilaporkan):** densitas kandidat rata-rata pengisi (rich > poor), rasio panjang token paket terhadap `full`, dan proporsi paket `drop_ans` yang masih memuat jawaban (harus ≈ 0 di populasi primer).

## Kriteria gagal
- S2-H1 dan S2-H2 tidak signifikan, dengan efek yang CI-nya memuat 0 → konfabulasi tidak bergantung pada ketersediaan kandidat. Hipotesis "anchoring" ditolak, dan temuan pilot dilaporkan sebagai korelasional saja.
- S2-H3 berlaku untuk `extractive` tetapi tidak untuk `open` → penyalinan adalah artefak instruksi.

## Analisis sekunder (eksploratif, diberi label)
Abstain rich vs poor; asal jawaban karangan (unit emas tersisa / pengisi / di luar paket); efek per tipe jawaban (numerik vs nama); efek per ukuran model.
