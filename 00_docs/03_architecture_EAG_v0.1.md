# Epistemic Authority Gate (EAG) — Spesifikasi Arsitektur v0.1

Tanggal: 5 Oktober 2026 · Status: **draf ide, novelty belum terverifikasi.** Lihat `04_prior_art_EAG_v0.1.md` (dikerjakan agent literature-scout) sebelum mengklaim apa pun sebagai baru.

---

## 1. Motivasi

LLM standar memberi generator **otoritas penuh** atas distribusi output. Probabilitas selalu bisa ditaruh pada token klaim, ada evidence atau tidak. Upaya mitigasi yang ada umumnya:
- **memberi informasi** ke generator (RAG, sinyal reader di prompt), atau
- **mengkritik setelahnya** (verifier, CoVe).

Keduanya tidak mengubah siapa yang berwenang memutuskan sebuah klaim boleh keluar.

Pilot #1 menguji ini secara langsung lewat H3a: apakah sinyal epistemik yang hanya *disampaikan* (advisory) diabaikan generator? Kawada & Kellis (2026) melaporkan hal serupa di level internal: representasi verifikasi dapat di-decode, tetapi tidak efektif secara kausal. Jika H3a menunjukkan advisory ≈ off, itu motivasi empiris untuk menanam otoritas epistemik **di dalam arsitektur**, bukan di prompt.

Analogi (inspirasi fungsional saja): sistem verbal pada split-brain menyusun narasi tanpa akses ke informasi penyebab. EAG menambah jalur yang (1) membaca evidence yang benar-benar sampai, dan (2) berwenang menahan narasi.

---

## 2. Definisi Formal

### 2.1 Notasi
- Model dasar beku: decoder Transformer f dengan L layer dan dimensi d.
- Pertanyaan q; paket evidence **E** = (u₁, …, u_k): unit kalimat dengan judul, sama dengan pilot.
- Reader pass (model beku yang sama, pemanggilan terpisah): setiap unit u_j dienkode lalu di-*mean-pool* dari layer ℓ_r, menghasilkan **m_j ∈ ℝ^d**. Hasilnya **M = [m₁ … m_k] ∈ ℝ^{k×d}** (memori epistemik level-unit).
- Generator pass: hidden state di layer ℓ_g pada posisi t adalah **h_t ∈ ℝ^d**.
- t₀ = **commitment point**, yaitu posisi token jawaban pertama. Untuk QA jawaban pendek: posisi tepat setelah "Answer:".

### 2.2 Epistemic head (bagian yang dilatih)

```
q_t   = W_q · LN(h_t)                         W_q ∈ ℝ^{d_e×d}
K, V  = M·W_kᵀ, M·W_vᵀ                         W_k, W_v ∈ ℝ^{d_e×d}
a_t   = softmax(q_t Kᵀ / √d_e)  ∈ Δ^k          (distribusi atensi ke unit evidence)
c_t   = a_t · V                                (ringkasan evidence yang relevan)
φ_t   = [ q_t ; c_t ; q_t ⊙ c_t ; max_j a_tj ; H(a_t) ]
σ_t   = sigmoid( MLP(φ_t) )   ∈ (0, 1)         (skor dukungan epistemik)
```

Parameternya hanya W_q, W_k, W_v, dan MLP. Dengan d_e = 256, jumlahnya sekitar 1–2 juta parameter.

### 2.3 Otoritas atas output (inti)

Pada commitment point t₀:

  **P_EAG(y) = σ_{t₀} · P_gen(y | h_{t₀}) + (1 − σ_{t₀}) · δ_ABSTAIN(y)**

Implementasi praktis untuk inferensi deterministik:
- **σ_{t₀} < τ** → output `INSUFFICIENT EVIDENCE` (generator tidak dipanggil lebih lanjut).
- **σ_{t₀} ≥ τ** → generator menyusun jawaban seperti biasa.

τ tidak dipilih tunggal; seluruh **kurva risk–coverage** dilaporkan dengan menyapu τ, lalu τ dipilih pada dev set untuk target coverage tertentu.

Perbedaan dengan prompt arbitration di pilot (`enforced`): di pilot, keputusan dibuat oleh reader LLM lewat teks. Di EAG, keputusan adalah **fungsi terlatih dari h_t dan M**. Ia membaca state generator *dan* evidence sekaligus, dan dilatih untuk sensitif terhadap intervensi kanal.

### 2.4 Masalah terbuka: gating per-token untuk jawaban panjang

Gating di setiap token akan menahan kata fungsi ("The", "is"). Untuk v0.1, gate hanya berlaku pada **commitment point** (QA pendek). Generalisasi ke jawaban panjang (gate pada awal setiap klaim atau kalimat, ditentukan oleh detektor batas klaim) dicatat sebagai pertanyaan riset lanjutan.

---

## 3. Pelatihan: supervisi dari intervensi kanal

### 3.1 Data
HotpotQA **train** (~90k item), dikonstruksi dengan kode `eaa/conditions.py` yang sama dengan pilot. Setiap item menghasilkan 4 paket kontrafaktual: `full`, `drop_ans`, `drop_other`, dan `drop_all`.

**Label dukungan:** s = `answer_available`, dihitung dari paket yang dirender. Untuk yes/no, s = 1 hanya pada `full`.

Test set (dev) tidak pernah dipakai untuk pelatihan. Sampel pilot 500 item berasal dari dev, sehingga terpisah dari data latih.

### 3.2 Loss

  **L = λ_s · L_sup + λ_c · L_contrast  (+ λ_lm · L_LM pada fase 2)**

- **L_sup = BCE(σ_{t₀}, s)**: kalibrasi skor dukungan.
- **L_contrast = max(0, γ − [logit σ(full) − logit σ(drop_ans)])**: pasangan dengan pertanyaan yang sama dan paket yang sama kecuali paragraf jawaban. Skor **harus turun** ketika akses dicabut, sementara semua hal lain tetap. Inilah yang membedakan "membaca evidence" dari "menebak dari pertanyaan" (knowledge-boundary probe).
- **L_LM (fase 2, opsional):** LoRA pada generator, hanya untuk contoh yang answerable, supaya kemampuan menjawab tidak rusak.

**Klaim kontribusi yang dikejar (menunggu verifikasi prior art):** sinyal pelatihan untuk otoritas epistemik diperoleh dari **intervensi kausal pada kanal evidence** (pasangan kontrafaktual yang dicocokkan panjang dan posisinya), bukan dari label kebenaran output saja.

---

## 4. Hipotesis lanjutan

| | Hipotesis | Falsifier |
|---|---|---|
| H5 | EAG mencapai **AURC** (area under risk–coverage) lebih rendah daripada prompt arbitration (pilot `enforced`) dan probe tanpa evidence, dengan budget parameter yang dicocokkan | Probe pada h_t saja (tanpa cross-attention ke M) menyamai EAG, artinya akses evidence tidak berperan |
| H6 | L_contrast meningkatkan **access sensitivity** Δσ = σ(full) − σ(drop_ans) dan robustness OOD | Tanpa L_contrast hasilnya sama |
| H7 | Gate yang dilatih di HotpotQA tergeneralisasi ke 2WikiMultiHopQA / MuSiQue tanpa fine-tuning | Kinerja runtuh ke level baseline di luar distribusi latih |

---

## 5. Baseline & ablasi (budget dicocokkan)

| Sistem | Apa yang diuji |
|---|---|
| Off (generator saja) | batas bawah |
| Prompt advisory / enforced (pilot) | otoritas lewat teks vs lewat arsitektur |
| **Probe-only**: MLP(h_{t₀}), tanpa M | apakah gate cuma knowledge-boundary probe |
| **Evidence-only**: MLP(pool(M), q) | apakah gate cuma retrieval-sufficiency classifier |
| Lookback-Lens-style: rasio atensi ke konteks | detektor berbasis atensi |
| Context-Aware Decoding | kontras logit dengan dan tanpa konteks |
| Self-consistency / semantic entropy threshold | gate berbasis ketidakpastian, tanpa training |
| EAG tanpa L_contrast | kontribusi supervisi intervensi |
| EAG penuh | — |

**Metrik:** AURC, selective risk @ coverage 80/90%, false refusal pada `full`, ECE dari σ, Δσ (access sensitivity), dan latensi tambahan.

---

## 6. Rencana komputasi (RTX 5050 8 GB / Colab T4)

- **Backbone:** Qwen2.5-0.5B atau 1.5B-Instruct, fp16, beku. 3B untuk replikasi.
- **Ekstraksi fitur sekali saja:** h_{t₀} (d) dan M (k × d per paket, level-unit). Untuk 1.5B (d = 1536) dengan k ≈ 10 dan fp16: ~31 KB per paket. Untuk 20k item × 4 level ≈ 2,5 GB. Muat di disk, dan training head berjalan di CPU/GPU dalam hitungan menit.
- **Head:** ~1–2 juta parameter, cepat dilatih, sehingga banyak seed dan ablasi bisa dijalankan.
- **Fase 2 (LoRA generator):** di Colab, jika fase 1 menjanjikan.

## 7. Rencana implementasi

```
eaa/eag/
  features.py   ekstraksi h_t0 (generator pass) + M (reader pass, mean-pool per unit), cache .pt
  model.py      EpistemicHead (cross-attn ke unit + MLP -> sigma)
  train.py      L_sup + L_contrast, early stopping pada dev split dari train
  evaluate.py   risk-coverage, AURC, Δσ, ECE; perbandingan dengan baseline
```

## 8. Urutan kerja

1. Pilot #1 selesai → baca hasil H3a (apakah sinyal advisory diabaikan?).
2. Prior art EAG (`04_prior_art_EAG_v0.1.md`) → revisi bagian 2–3 bila ada tumpang tindih.
3. Implementasi fitur + head pada Qwen2.5-0.5B, 5k item train → uji kelayakan (Δσ > 0? AURC < probe-only?).
4. Skala ke 20k item dan 1.5B; jalankan ablasi lengkap.
5. Tulis Paper: *pilot (fenomena) + EAG (arsitektur)*.
