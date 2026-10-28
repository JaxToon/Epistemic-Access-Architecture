# EAG v2: *Gate* + Penunjuk di Lapisan Output (Kembali ke Target Awal)

Ditulis 28 Oktober 2026, **sebelum** implementasi dan pilot. Status: rencana pilot eksploratif. Hiperparameter ditetapkan di sini dan **tidak disetel pada item *dev***, sehingga hasil pilot di *dev* adalah perkiraan yang jujur.

## 1. Kenapa (dari target awal ke EAG v2)

Rancangan awal (dokumen 03 §2.3): P_EAG(y) = σ·P_gen(y) + (1 − σ)·δ_ABSTAIN. Wewenangnya hanya dua: membiarkan generator atau menyuruhnya diam. Temuan setelah itu menunjuk ke wewenang ketiga:

- 61% halusinasi dengan *evidence* lengkap adalah **memilih entitas lain dari paragraf yang benar** (Fase 1).
- *Hidden state* lebih menyukai jawaban emas pada 65–69% kasus itu (Fase 1b, termasuk *decoy* ketat).
- Veto tidak bisa memulihkan (0/71). *Steering* hanya memulihkan 8,5% (pilot *dev*).

**EAG v2** menambah "jalur pembaca yang ikut bicara": *head* mirip *attention* yang menunjuk token *evidence*, lalu dicampur di lapisan output:

  **P(y_t) = 1[σ ≥ τ] · [ g_t · P_gen(y_t) + (1 − g_t) · P_tunjuk(y_t) ]**, dan jika σ < τ: ABSTAIN

  P_tunjuk(v) = Σ_j a_tj · 1[x_j = v],  a_t = softmax(q_t · k_j / √d_e) atas token *evidence* j

Tiga wewenang dalam satu modul: **diam** (σ), **mengoreksi** (penunjuk), **membiarkan** (g → 1).

## 2. Posisi terhadap literatur (dicek 28 Okt; abstrak dibaca)

| Karya | Yang sama | Yang berbeda dari EAG v2 |
| --- | --- | --- |
| *Pointer-generator* (See dkk., ACL 2017) | Rumus campuran copy/generate | Dilatih penuh; ringkasan; tanpa abstain |
| CopyGen (Zhang dkk., arXiv 2610.28393, NeurIPS 2026) | *Plugin* penyalin untuk LLM beku | Reproduksi span persis (kontrak, kode); tanpa QA/halusinasi; tanpa *gate* kecukupan |
| Copy-Paste LM (Godey & Artzi, arXiv 2610.19247) | *Head* copy di samping *LM head* | *Pre-training*; tanpa evaluasi halusinasi |
| CopyPasteLLM (ICLR 2026) | Kesetiaan RAG lewat menyalin | Metode pelatihan model, bukan modul pada model beku |
| YOPO (arXiv 2608.14465) | LM beku; abstain + koreksi dalam satu *pass* | Koreksi lewat *steering*, bukan menunjuk ke *evidence*; tanpa plasebo nilai sinyal |

**Klaim yang dikejar (jika pilot dan uji konfirmatori berhasil):** satu modul kecil (±1 juta parameter) pada LLM beku dengan tiga wewenang di lapisan output (diam / koreksi / biarkan), dilatih dari intervensi kanal *evidence*, yang memulihkan kegagalan alami "tahu tapi tidak mengungkap" lebih baik daripada saran, veto, dan *steering* dengan sinyal yang sama. **Bukan** klaim: mekanisme copy itu sendiri.

## 3. Desain (ditetapkan sekarang)

- **Backbone:** Qwen2.5-3B-Instruct, fp16, beku. *Prompt* ekstraktif yang sama.
- **Penunjuk:** q_t = W_q·LN(h²⁷_t), k_j = W_k·LN(h²⁷_j), d_e = 256. j = semua token di blok *evidence* (antara "Evidence:" dan "Question:"). Lapisan 27 adalah lapisan *probe* terbaik di Fase 1b.
- **Target copy dan spasi:** token ke-j yang disalin adalah x_j. Pada langkah jawaban pertama dipakai varian tanpa spasi depan (byte-level BPE: " Yoruba" ≠ "Yoruba"), jika varian itu satu token.
- ***Gate* g_t** = sigmoid(MLP([W_g·LN(h³⁶_t); max_j a_tj; H(a_t); max_v log P_gen])), dengan *hidden* MLP 64.
- **Loss** (*teacher forcing*): −mean_t log( g_t·P_gen(y*_t) + (1 − g_t)·P_tunjuk(y*_t) + 1e−9 ) atas token jawaban + token akhir `<|im_end|>`.
- **Data latih:** paket HotpotQA **train** (`01_data/eag_train_packets.jsonl`, split `train`):
  - `full` → target = jawaban emas;
  - `drop_ans` (kebijakan sama dengan pilot σ) → target = "INSUFFICIENT EVIDENCE", supaya penunjuk belajar tidak menyalin entitas ketika jawaban tidak ada.
  - Validasi: split `val`, loss validasi.
- **Optimasi:** AdamW lr 1e−3, wd 0,01, akumulasi gradien 16, 2 epoch, simpan bobot dengan loss validasi terendah. Seed 20261028.
- **Dekoding:** *greedy* pada distribusi campuran, maksimum 24 token, berhenti di `<|im_end|>`. σ dari *head* `eag_lc1` yang sama (Studi 3).

## 4. Pilot pada *dev* (255 item utama Studi 2/3; `full` + `drop_ans` `entity_poor`)

- **Lengan:**
  - `off` (sudah ada);
  - `ptr`: penunjuk di semua item;
  - `ptr_σ`: penunjuk jika σ ≥ 0,5, selain itu `off`;
  - **`eag_v2`**: penunjuk jika σ ≥ 0,5, selain itu ABSTAIN. Ini rancangan lengkapnya.
  - Pembanding yang sudah ada: `veto` (`off` + σ) dan CAA `L24_a2` (pemicu σ).
- **Ukuran:** halusinasi → benar, rusak (benar → tidak benar), Δbenar, Δabstain @`full`, Δhalusinasi@`drop_ans`, U(λ = 2) atas `full` + `drop_ans`, dan pulih pada K1 vs non-K1.
- **Ambang keberhasilan pilot (ditetapkan sekarang):** `ptr_σ` mencapai halusinasi → benar ≥ 15% (sekitar 2× CAA) dengan rusak ≤ 5 poin dan Δhalusinasi@`drop_ans` ≤ +0,02. Jika tercapai, EAG v2 dimasukkan ke Studi 4 sebagai lengan utama, menggantikan *steering*, dengan pre-registrasi direvisi sebelum dikunci.
- **Jika gagal:** dilaporkan apa adanya. Studi 4 tetap dengan *steering*.

## 5. Risiko yang sudah diketahui

- Penunjuk bisa menyalin entitas yang salah dengan yakin, sehingga halusinasi naik. Mitigasi: data latih `drop_ans`, pemicu σ, dan ukuran Δhalusinasi.
- Jawaban yang tidak ada sebagai span di *evidence* (ya/tidak, parafrasa) tidak bisa disalin; g harus belajar menyerahkan ke generator.
- Copy mengubah gaya keluaran. Label tetap dengan aturan + *judge* yang sama.
- Catatan implementasi (28 Okt): modul EAG v2 = 1.602.625 parameter (proyeksi W_g untuk gate ikut dihitung), bukan ±1 juta seperti perkiraan §2; tidak ada perubahan desain. Smoke test lolos (48 paket, 1 epoch; g ≈ 0,99, belum menyalin — wajar untuk data sekecil itu).
