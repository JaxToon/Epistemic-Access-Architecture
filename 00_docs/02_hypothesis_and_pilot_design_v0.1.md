# Hipotesis & Desain Pilot #1 — v0.1

Tanggal: 5 Oktober 2026 · Status: draf untuk dikunci (pre-registration) sebelum eksperimen dijalankan

---

## BAGIAN A — Hipotesis 1 Halaman

**Judul kerja:** *Cutting the Channel: Evidence Access and Epistemic Authority as Causal Drivers of Hallucination*

**Masalah.** LLM menghasilkan jawaban yang fasih walaupun evidence-nya tidak lengkap, tidak sampai ke generator, atau ada tetapi tidak dipakai. Arsitektur saat ini mencampur pemrosesan evidence dan generasi bahasa dalam satu jalur. Akibatnya sulit dibedakan apakah halusinasi berasal dari evidence yang **tidak ada**, evidence yang **tidak sampai**, atau evidence yang **sampai tetapi tidak berkuasa**.

**Inspirasi (fungsional, bukan anatomis).** Pada pasien split-brain, sistem verbal dapat menyusun penjelasan yang koheren tanpa akses ke informasi yang sebenarnya memicu perilaku. Prinsip yang diambil: *spesialisasi + kanal komunikasi terbatas + tekanan untuk tetap menghasilkan narasi*.

**Setup.** Satu sistem dengan dua fungsi terpisah:
- **Reader:** membaca evidence, membentuk *epistemic state* (klaim, sumber, verdict kecukupan/konflik)
- **Generator:** menyusun jawaban

Keduanya dihubungkan oleh **kanal** yang dapat dimanipulasi secara eksperimental.

**Hipotesis.**
- **H1 — Access:** dengan pertanyaan, evidence dasar, dan jumlah token tetap, mengurangi bandwidth kanal reader→generator menaikkan halusinasi.
- **H2 — Restoration:** membuka kembali kanal menurunkan halusinasi kembali ke level full-access.
- **H3 — Authority:** dengan informasi yang identik, epistemic state yang **wajib diikuti** (arbitration enforced) menurunkan halusinasi lebih besar daripada state yang hanya **disampaikan** (advisory). Prediksi tambahan berdasarkan Kawada & Kellis 2026: kondisi *advisory* akan nyaris sama dengan *off*. Artinya, sinyal epistemik yang sampai tetapi tidak punya otoritas tidak banyak berpengaruh.
- **H4 — Cost:** penurunan halusinasi pada H3 tidak dibayar dengan false refusal yang berlebihan.

**Kebaruan yang dikejar.** NAF (Saavedra 2026) mengusulkan arbitrase epistemik secara konseptual tanpa eksperimen. Pilot ini memisahkan secara eksperimental tiga hal: *ketersediaan evidence*, *akses kanal*, dan *otoritas epistemik*. Ketiganya diuji dengan desain within-item dan anggaran token yang disamakan.

**Teori dianggap gagal jika:** (i) bandwidth tidak memengaruhi halusinasi setelah token disamakan; (ii) restoration tidak memulihkan; (iii) enforced ≈ advisory ≈ off; atau (iv) enforced hanya menang karena menolak menjawab hampir semua pertanyaan.

---

## BAGIAN B — Desain Eksperimen

### B1. Hardware & model

| Lingkungan | Spesifikasi | Model | Peran |
|---|---|---|---|
| Lokal | RTX 5050 Laptop, 8 GB VRAM, PyTorch 2.12 + CUDA 12.8 | Qwen2.5-3B-Instruct atau Llama-3.2-3B-Instruct (fp16, ~6–7 GB) | Pengembangan + pilot utama |
| Colab | T4 16 GB (gratis) | Qwen2.5-7B / Llama-3.1-8B-Instruct (4-bit) | Replikasi skala (H6 kecil-kecilan) |

Reader dan generator memakai **backbone yang sama** dalam pemanggilan terpisah. Separasinya fungsional dan diwujudkan lewat kanal. Dengan begitu, perbedaan hasil tidak bisa dijelaskan oleh perbedaan kapasitas model.

Decoding dibekukan: greedy, `max_new_tokens` tetap, seed tetap.

### B2. Data

- **Sumber utama: HotpotQA (distractor setting).** Setiap pertanyaan punya *supporting facts* emas di level kalimat, ditambah paragraf pengecoh. Ini memberi **unit evidence** yang jelas untuk dipotong dan dikembalikan, serta **pengisi dengan panjang setara** dari paragraf pengecoh.
- **Ukuran pilot:** 500 pertanyaan dev (sampel acak dengan seed tetap) × 9 kondisi ≈ 4.500 generasi. Perkiraan waktunya sekitar 1–3 jam di lokal untuk jawaban pendek.
- **Kontrol pengetahuan parametrik:** jalankan *closed-book* (tanpa evidence) lebih dulu. Item yang sudah dijawab benar tanpa evidence diberi label `param_known` dan dianalisis terpisah. Tanpa kontrol ini, kondisi 0% bisa tetap "benar" dari ingatan model, dan efek kanal jadi tertutup.

### B3. Epistemic state (keluaran Reader)

```json
{
  "question_id": "...",
  "evidence_units": [{"id": "e1", "text": "...", "source": "Title A"}],
  "claims": ["..."],
  "verdict": "SUFFICIENT | INSUFFICIENT | CONFLICT",
  "missing": "deskripsi singkat informasi yang belum ada"
}
```

Verdict dihitung dari evidence **setelah** manipulasi kanal, tanpa melihat jawaban emas. Sebagai batas atas, dipakai juga **oracle verdict** yang diturunkan dari supporting facts.

### B4. Kondisi (within-item: setiap pertanyaan melewati semua kondisi)

| # | Kondisi | Yang sampai ke generator | Menguji |
|---|---|---|---|
| C0 | Closed-book | Tidak ada evidence | Baseline parametrik |
| C1 | Full | 100% unit evidence emas + pengisi | Referensi |
| C2 | BW-75 | 75% unit emas + pengisi setara | H1 |
| C3 | BW-50 | 50% unit emas + pengisi setara | H1 |
| C4 | BW-25 | 25% unit emas + pengisi setara | H1 |
| C5 | BW-0 | 0% unit emas, hanya pengisi | H1 |
| C6 | Restored | Unit dari C4 dikembalikan → 100% | H2 |
| C7 | Advisory | Evidence C3/C4 + verdict reader, generator **boleh** mengabaikan | H3 |
| C8 | Enforced | Evidence sama + verdict, dan jika `INSUFFICIENT` sistem **wajib** abstain | H3, H4 |

**Kontrol token:** setiap unit emas yang dibuang diganti kalimat pengecoh dengan panjang setara (±10% token). Panjang total input dicatat per generasi.

**Catatan C6:** secara isi, C6 identik dengan C1. Nilainya sebagai uji ada pada *urutan prosedur*: kondisi dijalankan sebagai intervensi terpisah dan dicek bahwa hasil kembali ke level C1. Jika nanti dipakai riwayat percakapan (multi-turn), C6 menjadi tidak trivial: evidence dipulihkan setelah generator pernah menjawab dalam kondisi terbatas.

### B5. Metrik

| Metrik | Definisi operasional |
|---|---|
| **Hallucination rate** (primer) | Generator memberi jawaban substantif (bukan abstain) yang **salah**, *atau* benar tetapi **tidak didukung** evidence yang sampai (dilacak terpisah: `unsupported_correct`) |
| Accuracy | EM / F1 terhadap jawaban emas + LLM-judge yang diaudit manual pada 10% sampel |
| Abstention precision | Dari semua abstain, porsi yang memang evidence-nya tidak cukup |
| False refusal | Abstain padahal evidence cukup (C1, C6) |
| Access sensitivity | Kemiringan hallucination rate terhadap bandwidth (C1→C5) |
| Authority effect | Hallucination(C7) − Hallucination(C8), pada evidence yang identik |

### B6. Analisis statistik

- Regresi logistik mixed-effects: `halusinasi ~ kondisi + (1 | item)`. Kondisi `param_known` dianalisis sebagai moderator.
- Perbandingan berpasangan (McNemar) untuk kontras kunci: C1 vs C4, C4 vs C6, C7 vs C8.
- Effect size + 95% CI dengan bootstrap per item. Laporkan juga hasil nol.
- Hipotesis, metrik primer, dan aturan eksklusi **dikunci sebelum** menjalankan kondisi C2–C8.

### B7. Ancaman validitas utama

| Ancaman | Kontrol |
|---|---|
| Efek hanya karena token berkurang | Pengisi dengan panjang setara |
| Model menjawab dari ingatan | C0 closed-book + stratifikasi `param_known` |
| Reader "bocor" (menyelesaikan soal sendiri) | Reader hanya mengeluarkan verdict + klaim, bukan jawaban; dicek otomatis |
| Enforced menang karena menolak semuanya | False refusal dilaporkan berdampingan; utilitas dihitung |
| LLM-judge bias | Audit manual 10%, laporkan agreement |
| Hasil khas satu model | Replikasi di model kedua (Colab) |

---

## BAGIAN C — Rencana Kerja

| Langkah | Output | Di mana |
|---|---|---|
| 1. Setup repo + loader HotpotQA + sampel 500 item | `01_data/`, dataset card | Lokal |
| 2. Generator + closed-book (C0) | label `param_known` | Lokal |
| 3. Pembentuk kondisi C1–C6 + kontrol token | config intervensi | Lokal |
| 4. Reader (verdict) + C7/C8 | epistemic state JSON | Lokal |
| 5. Evaluasi + audit manual | metrik per kondisi | Lokal |
| 6. Analisis + plot (kurva bandwidth, authority effect) | notebook | Lokal |
| 7. Replikasi 7–8B | tabel replikasi | Colab |
| 8. Memo 2–5 halaman → kontak supervisor | memo | — |
