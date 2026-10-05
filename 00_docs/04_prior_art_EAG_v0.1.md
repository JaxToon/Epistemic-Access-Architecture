# Prior Art Hunt — Epistemic Authority Gate (EAG) v0.1

Tanggal: 5 Oktober 2026 · Penulis: literature-scout (putaran pertama, belum sistematis)
Terkait: `03_architecture_EAG_v0.1.md` (tidak disunting di sini), `01_literature_matrix_v0.1.md`

Legenda: **[V]** abstrak/halaman dibaca lewat WebFetch pada sesi ini · **[S]** hanya dari hasil pencarian / pengetahuan umum. Entri [S] wajib dibaca penuh sebelum dikutip.

## 0. Dekomposisi EAG yang diuji

| Kode | Komponen |
|---|---|
| C1 | Modul kecil yang dapat dilatih di atas decoder **frozen** yang membaca evidence lewat **cross-attention** |
| C2 | **Skor support per token** σ_t = sigmoid(wᵀ[h_t ; CrossAttn(h_t,E)]) |
| C3 | **Hard mixture** dengan token ABSTAIN: P = σ·P_gen + (1−σ)·1[ABSTAIN]. Gate ini *berwenang* atas distribusi output, bukan verifier post-hoc |
| C4 | Loss L_LM + λ·BCE(σ,s) — supervisi support per token |
| C5 | Label dan loss kontrastif dari **intervensi kanal kontrafaktual**: paket evidence dengan vs tanpa paragraf pembawa jawaban, semua hal lain tetap; σ wajib turun |

---

## 1. Peta prior art per komponen

### A. Gate dan cross-attention ke evidence (C1)

| # | Work | Ver. | Inti | Overlap dengan EAG | Yang masih ditambahkan EAG |
|---|---|---|---|---|---|
| A1 | Alayrac et al., *Flamingo* (NeurIPS 2022) | S | Gated cross-attention (tanh-gate, zero-init) antar layer LM yang frozen | **C1 secara struktural identik**: adapter cross-attn ber-gate di atas LM frozen | Gate Flamingo hanya mengatur *aliran informasi masuk*, tidak ada σ yang dibaca keluar, tidak ada abstain |
| A2 | Borgeaud et al., *RETRO* (ICML 2022) | S | Chunked cross-attention ke neighbor hasil retrieval | C1 (cross-attn ke evidence) | Tidak ada gate otoritas maupun abstensi |
| A3 | Qiu et al., *Gated Attention for LLMs* (Qwen; arXiv 2505.06708, NeurIPS 2025) | V | Sigmoid gate per head setelah SDPA → non-linearitas, sparsity, attention-sink hilang | Hanya kemiripan nama/sigmoid gate. **Bukan** gate epistemik | Tidak relevan untuk abstensi; cukup disebut agar reviewer tidak salah paham |
| A4 | Yu et al., *TokenMem: Faithful Knowledge Injection for Frozen LLMs* (arXiv 2607.22625, Jun 2026) | V | Adapter cross-attention ber-gate (~3–7M param) di setiap layer LLM frozen; curriculum fase-2 dengan pengetahuan **kontrafaktual** agar patuh pada evidence | **C1 hampir identik** + pelatihan kontrafaktual (substitusi, bukan penghapusan) | Tidak ada σ yang dibaca keluar, tidak ada token ABSTAIN, tidak ada label "evidence dihapus → harus menolak". TokenMem mendorong *kepatuhan*; EAG mendorong *kepatuhan atau abstain* |
| A5 | Li et al., *SHIFT: Gate-Modulated Activation Steering* (arXiv 2606.27786, Jun 2026) | V | Gate ringan (<0,01% param) pada LLM frozen yang memodulasi representasi untuk konflik konteks vs parametrik | C1 (gate kecil yang dapat dilatih, backbone frozen) | Tanpa abstensi; gate bekerja pada aktivasi, tidak pada distribusi output |
| A6 | Wang, *Abstention and Noise Filtering: Two Missing Primitives of Softmax Attention* (arXiv 2609.22005, Sep 2026) | V | Head attention tidak bisa "abstain" karena bobot softmax berjumlah 1; diusulkan mekanisme abstensi per head (model 10M–350M) | Konsep "abstain" di level attention, bukan output | Bukan generasi/halusinasi. Berguna sebagai motivasi teoretis |
| A7 | Gupta & Choudhary, *Fact Grounded Attention* (arXiv 2509.25252, v2 Sep 2026) | V | Menyuntikkan fakta terverifikasi ke skor attention pre-softmax | Ide "grounding di level arsitektur" | Klaim besar, evaluasi domain-sempit; tanpa abstensi atau pelatihan kontrafaktual |

### B. Skor support per token dan decoding yang di-gate (C2, C3)

| # | Work | Ver. | Inti | Overlap | Yang ditambahkan EAG |
|---|---|---|---|---|---|
| B1 | **Lango & Dušek, *Critic-Driven Decoding*** (EMNLP 2023, arXiv 2310.16964) | V | Classifier critic (XLM-R) membaca data input + prefix + kandidat token, lalu memberi P(c \| y≤i, x). Decoding: ln P ∝ λ·ln P(c\|y≤i,x) + ln P_LM. Negatif sintetis dari penggantian token | **Paling dekat untuk C2+C3 + C4**: skor "didukung oleh input" per token yang langsung mengubah distribusi output generator frozen, dilatih dengan label support biner | Critic adalah encoder **terpisah** (bukan membaca h_t generator); kombinasi multiplikatif tanpa token ABSTAIN, jadi tetap memaksa memilih token; negatif berasal dari *perturbasi output*, bukan *intervensi evidence* |
| B2 | Chuang et al., *Lookback Lens* (EMNLP 2024, arXiv 2407.07071) | S | Classifier linear atas lookback ratio (attention ke konteks vs ke token baru) per head; guided decoding per chunk | C2 (skor grounding per langkah dari state internal) + decoding yang di-gate | Detektor dipakai untuk *memilih kandidat*, bukan hard-mix ke ABSTAIN; dilatih dari label halusinasi, bukan intervensi evidence |
| B3 | Asai et al., *Self-RAG* (ICLR 2024) | S | Reflection token (IsRel, **IsSup**, IsUse) di-generate model; beam search per segmen memakai skor kritik | C2 tingkat segmen (IsSup = support oleh passage) | IsSup adalah token yang di-*generate* dan *advisory* (dipakai untuk ranking). Tidak ada otoritas keras, tidak per token, model di-fine-tune penuh |
| B4 | Zhu et al., *Token-Guard* (ICLR 2026, arXiv 2601.21969) | V | Skor risiko halusinasi per token di latent space; pruning dan regenerasi | C2 (skor per token yang mengontrol decoding) | Tanpa evidence eksplisit, tanpa abstensi, tanpa intervensi kanal |
| B5 | *Monitoring Decoding* (Findings ACL 2025, arXiv 2503.03106) | S | Fungsi monitor menandai token rawan halusinasi saat generasi, lalu intervensi | C2/C3 (gating saat generasi) | Resample, bukan abstain; tidak berbasis evidence |
| B6 | Shi et al., *Context-Aware Decoding (CAD)* (arXiv 2305.14739, NAACL 2024) | V | Distribusi kontrastif: amplifikasi selisih P(y\|c,x) dan P(y\|x); tanpa training | Memakai **kontras with/without context** (versi inferensi dari C5) | Tanpa training, tanpa skor support, tanpa abstensi. CAD *mendorong* token konteks; EAG *memblokir* token tanpa support |
| B7 | Chuang et al., *DoLa* (ICLR 2024) | S | Kontras logit antar layer untuk faktualitas | Hanya "modifikasi distribusi saat decoding" | Tanpa evidence, tanpa gate yang dipelajari |
| B8 | See et al., *Pointer-Generator* (ACL 2017) | S | p_gen = σ(w·[h_t; context; x_t]) mencampur P_vocab dan distribusi copy | **Struktur C3 identik secara matematis** (sigmoid dari [h_t ; attended context] → mixture dua distribusi) | Komponen kedua di EAG adalah *delta ABSTAIN*, bukan distribusi copy; semantik σ adalah "support", bukan "copy vs generate"; supervisi σ eksplisit |
| B9 | Khandelwal et al., *kNN-LM* (ICLR 2020) + varian gate adaptif | S | P = λ·P_kNN + (1−λ)·P_LM; varian kemudian mempelajari λ per token | Mixture distribusi dengan bobot per token | Bukan abstensi; λ tidak disupervisi oleh support |
| B10 | Liu et al., *Deep Gamblers* (NeurIPS 2019) | S | Klasifikasi m+1 kelas dengan kelas abstain; loss doubling-rate | **C3 di klasifikasi**: probabilitas dibagi antara prediksi dan "reserve" (abstain) | Bukan generasi sekuensial; tanpa evidence |

### C. Abstensi dan token "I don't know" (C3, C4)

| # | Work | Ver. | Inti | Overlap | Yang ditambahkan EAG |
|---|---|---|---|---|---|
| C1' | Zhang et al., *R-Tuning* (NAACL 2024, arXiv 2311.09677) | V | Data refusal-aware dari selisih knowledge parametrik vs data instruksi; model belajar "I don't know" | Token/respons abstensi yang dipelajari | Batas pengetahuan **parametrik**, bukan evidence yang dikirim; tidak per token, tidak ada gate |
| C2' | Joren et al., *Sufficient Context* (ICLR 2025, arXiv 2411.06037) | S | Autorater kecukupan konteks; selective generation memakai sinyal sufficiency untuk abstain (+2–10%) | **Konsep inti C5 (kecukupan evidence menentukan abstensi)** | Tingkat respons, autorater eksternal, post-hoc atau sebelum generasi; bukan gate per token dan bukan modul yang dilatih dari intervensi |
| C3' | **Khodabandehlou & Krishnamachari, *Compression-Aware Abstention*** (arXiv 2608.29934, 30 Aug 2026) | V | Label "Confident" vs "Abstain" berdasarkan apakah span pembawa jawaban **bertahan atau terhapus** oleh kompresi KV; LoRA 10,1M di atas base frozen; MuSiQue ~2.600 contoh; hallucination turun 97% saat truncation | **Sangat dekat dengan C5**: supervisi kontrafaktual "evidence pembawa jawaban ada vs dihapus → abstain", di atas model frozen dengan modul kecil | Pelatihan via LoRA (SFT) tanpa σ eksplisit, tanpa mixture keras, tanpa skor per token; intervensi datang dari kompresor, bukan dari kanal reader→generator yang dimanipulasi sistematis |
| C4' | Luo et al., *YOPO: Answering and Abstaining in a Single Forward Pass of a Frozen LM* (arXiv 2608.14465, Aug 2026) | V | "Sufficiency direction" zero-shot di residual stream untuk abstensi + steering, pada LM frozen | C2 (sinyal kecukupan internal) + abstensi pada LM frozen | Arah linear, bukan head ber-cross-attention; tidak mencampur distribusi output; tanpa intervensi kanal saat pelatihan |
| C5' | Chen et al., *RINSE: Relevance Is Not Sufficient Evidence* (arXiv 2609.37469, Sep 2026) | V | Mendeteksi evidence gap *sebelum* generasi dengan 3 sinyal (coverage, answer-containment, SLM judge); benchmark berpasangan substitution/**deletion**/question-swap | Konstruksi pasangan deletion yang sama dengan C5; gate pra-generasi | Bukan modul internal; tidak per token; tidak dilatih end-to-end dengan generator. **Kutipan penting:** abstention training yang ada "teaches the generator's own knowledge boundary rather than judgment about evidence". Ini justifikasi EAG |
| C6' | I-CALM (arXiv 2604.03904), conformal abstention (2502.06884, 2604.27914), Selective Generation (Lee et al., NeurIPS 2024) | S | Abstensi berbasis confidence/kalibrasi di tingkat respons | Kerangka evaluasi selective prediction (coverage–risk) | Baseline dan metrik untuk H4 (cost) |

### D. Pelatihan kontrafaktual atau kontrastif dengan manipulasi evidence (C5)

| # | Work | Ver. | Inti | Overlap | Yang ditambahkan EAG |
|---|---|---|---|---|---|
| D1 | Li et al., *KAFT / LLMs with Controllable Working Memory* (Findings ACL 2023, arXiv 2211.05110) | S | Augmentasi konteks kontrafaktual (wajib ikut konteks) + konteks irrelevan (kembali ke parametrik) | C5 versi substitusi/irrelevan | Tidak ada kasus "evidence dihapus → abstain"; tidak ada gate |
| D2 | *Faithfulness-QA* (arXiv 2604.25313), SI-FACT (2509.10208), CANOE (ACL 2025), ContextFocus (2601.04131) | S | Dataset substitusi entitas kontrafaktual / tuning kontrastif / steering untuk context faithfulness | C5 (kontrastif kontrafaktual) dan loss kontrastif | Fokus konflik, bukan ketiadaan evidence; tanpa gate otoritas |
| D3 | Du, *Pair-ID: Paired Evidence Interventions* (arXiv 2608.08944, Aug 2026) | V | Audit offline: tambah support yang hilang / hapus nonsupport pada query yang sama | **Desain intervensi C5 sebagai alat audit** | Tidak ada training. EAG memakai intervensi sebagai *sinyal pelatihan* |
| D4 | *Evaluating and Improving Evidence-Grounded Fact-Checking via Multi-Round Evidence Ablation* (arXiv 2609.08943; penulis belum dicek) | S | Ablasi evidence bertahap untuk mengevaluasi/meningkatkan verifier; mencatat bahwa negatif hasil ablasi bisa masih mengandung evidence tak teranotasi | C5 (supervisi via ablasi) | **Peringatan metodologis**: label hasil ablasi bisa noisy. Wajib dikontrol di EAG (paragraf lain bisa redundan) |
| D5 | TokenMem fase-2 (lihat A4) | V | Curriculum kontrafaktual | C5 parsial | — |

---

## 2. Kombinasi: adakah yang sudah melakukan C1+C2+C3+C5 bersama?

Tidak ditemukan pada putaran ini (±20 query). Yang paling dekat terhadap **kombinasi**:

- **Critic-Driven Decoding (B1)**: C2+C3(lunak)+C4. Tanpa cross-attn ke h_t, tanpa ABSTAIN, tanpa intervensi evidence.
- **Compression-Aware Abstention (C3')**: C5 + modul kecil di atas base frozen + abstain. Tanpa σ per token, tanpa mixture keras.
- **TokenMem (A4)**: C1 + pelatihan kontrafaktual. Tanpa abstain.
- **Pointer-Generator (B8)**: C3 secara matematis.

Dengan kata lain, EAG ≈ (TokenMem/Flamingo adapter) × (pointer-generator gate yang diarahkan ke ABSTAIN) × (critic-driven supervision) × (counterfactual evidence-deletion labels à la Compression-Aware Abstention). Setiap faktor sudah ada. Yang belum terlihat adalah **perkaliannya**, ditambah klaim *otoritas* yang dapat diuji secara kausal.

---

## 3. Novelty verdict

**Jelas TIDAK baru (jangan diklaim):**
1. Adapter cross-attention ber-gate di atas LLM frozen (Flamingo, RETRO, TokenMem 2026).
2. Mixture sigmoid σ·P_A + (1−σ)·P_B dari [h_t ; context] (pointer-generator 2017; kNN-LM). EAG hanya mengganti P_B dengan delta ABSTAIN. Kelas abstain dalam softmax juga sudah ada (Deep Gamblers).
3. Skor support/grounding per token yang mengontrol decoding (Critic-Driven Decoding 2023, Lookback Lens 2024, Token-Guard 2026, Self-RAG IsSup).
4. Abstensi yang dipelajari / token "I don't know" (R-Tuning, Sufficient Context, Self-RAG).
5. Kontras with-vs-without context (CAD, saat inferensi) dan pelatihan kontrafaktual untuk faithfulness (KAFT, Faithfulness-QA, TokenMem).
6. Supervisi abstain dari "evidence pembawa jawaban dihapus vs ada" pada model frozen + modul kecil (**Compression-Aware Abstention, Agustus 2026**). Ini mengambil sebagian besar ruang C5.

**Kombinasi yang *mungkin* baru (perlu dipertahankan dengan hati-hati):**
- Head epistemik **per token** yang membaca *state generator* (h_t) dan evidence lewat cross-attention, dengan **otoritas keras** atas distribusi output (σ→0 ⇒ massa probabilitas klaim = 0), dan **dilatih langsung dari intervensi kanal berpasangan** (σ wajib turun saat paragraf pembawa jawaban dihapus, ceteris paribus).
- Nilai ilmiah yang lebih kuat daripada arsitekturnya sendiri: EAG sebagai **alat untuk menguji H3** (enforced vs advisory dengan informasi identik). Varian "advisory" (σ diberikan sebagai input/prompt) vs "authoritative" (σ hard-mix) pada modul yang **sama** adalah ablasi yang belum ditemukan di prior art dan langsung menjawab temuan Kawada & Kellis 2026 (verifikasi decodable tetapi tidak efektif secara kausal).
- Risiko: reviewer akan menyebut EAG "pointer-generator + critic decoding + compression-aware abstention". Klaim novelty harus dibingkai sebagai **pemisahan kausal antara akses dan otoritas**, bukan sebagai mekanisme gate baru.

**Catatan desain dari prior art:**
- Hard-mix per token: ABSTAIN di tengah kalimat menghasilkan output yang tidak koheren. Critic-Driven Decoding memakai warmup λ. Pertimbangkan gating hanya pada token klaim/span jawaban, atau abstain di tingkat span.
- Label hasil ablasi bisa noisy (D4; HotpotQA punya paragraf redundan). Verifikasi bahwa paragraf yang dihapus memang satu-satunya pembawa jawaban.
- Baseline wajib: CAD, Critic-Driven Decoding, Lookback Lens guided decoding, Self-RAG, Compression-Aware Abstention (LoRA), Sufficient-Context selective generation.

**2–3 paper paling berbahaya (baca penuh):**
1. **Khodabandehlou & Krishnamachari, *Compression-Aware Abstention*** (2026): https://arxiv.org/abs/2608.29934. Supervisi abstain kontrafaktual (evidence bertahan vs terhapus) di atas base frozen. Overlap terbesar dengan C5.
2. **Lango & Dušek, *Critic-Driven Decoding*** (EMNLP 2023): https://arxiv.org/abs/2310.16964. Skor support per token yang dilatih dan langsung memodulasi distribusi generator. Overlap terbesar dengan C2+C3+C4.
3. **Yu et al., *TokenMem*** (2026): https://arxiv.org/abs/2607.22625. Adapter cross-attention ber-gate pada LLM frozen + curriculum kontrafaktual. Overlap terbesar dengan C1+C5. Tambahkan juga Chen et al. *RINSE* (https://arxiv.org/abs/2609.37469) sebagai bacaan pendamping, karena paper ini sudah membuat argumen "abstain dari judgment evidence, bukan dari knowledge boundary" yang ingin dibuat EAG.

## 4. Sumber
- https://arxiv.org/abs/2608.29934
- https://arxiv.org/abs/2608.14465
- https://arxiv.org/abs/2609.22005
- https://arxiv.org/abs/2606.27786
- https://arxiv.org/abs/2607.22625
- https://arxiv.org/abs/2601.21969
- https://arxiv.org/abs/2305.14739
- https://arxiv.org/abs/2505.06708
- https://arxiv.org/abs/2310.16964 · https://arxiv.org/html/2310.16964v1
- https://arxiv.org/abs/2311.09677
- https://arxiv.org/abs/2609.37469
- https://arxiv.org/abs/2608.08944
- https://arxiv.org/abs/2509.25252
- https://arxiv.org/abs/2601.13744 (k-NN gating, query-level; tidak terlalu relevan)
- https://arxiv.org/abs/2407.07071
- https://arxiv.org/abs/2310.11511
- https://arxiv.org/abs/2411.06037
- https://arxiv.org/abs/2211.05110
- https://arxiv.org/abs/1907.00208
- https://arxiv.org/abs/2503.03106
- https://arxiv.org/html/2604.25313 · https://arxiv.org/pdf/2509.10208 · https://arxiv.org/html/2601.04131
- https://arxiv.org/pdf/2609.08943
- https://arxiv.org/abs/2604.22565 (HiLight, evidence highlighting untuk LLM frozen; pelengkap)
