# Prior Art Hunt — "Epistemic Stopping Rule" v0.1

Tanggal: 11 Oktober 2026 · Penulis: literature-scout (putaran pertama, ±25 query; belum sistematis)
Terkait: `04_prior_art_EAG_v0.1.md`, `01_literature_matrix_v0.1.md`, `research_log.md` (Fase 1b: σ diabaikan sebagai advice, efektif sebagai authority)

Legenda: **[V]** halaman/abstrak dibaca lewat WebFetch pada sesi ini · **[S]** hanya dari hasil pencarian atau pengetahuan umum; wajib dibaca penuh sebelum dikutip. Catatan kejujuran: WebFetch mengembalikan ekstraksi model kecil, jadi [V] di sini = abstrak/halaman, bukan PDF penuh, kecuali ditulis lain. Hal yang tidak muncul ditulis "tidak ditemukan di halaman", bukan "tidak ada".

## 0. Ide yang diuji

Klaim (kalimat) diemit satu per satu. Sebelum klaim berikutnya: σ = P(klaim berikutnya didukung evidence yang dikirim), dibaca dari state generator + evidence units; g = sisa informasi evidence-supported yang belum diekspresikan (uncovered share, via entailment atau attention coverage). Lanjut iff σ·g − λ(1−σ) − μ > 0, yaitu σ > (λ+μ)/(g+λ). Satu aturan memadukan abstain (σ rendah sebelum klaim pertama) dan berhenti (g → 0). Ditegakkan di decoding (authority).

Dekomposisi: **P1** σ per klaim dari hidden state + evidence; **P2** g (coverage tersisa); **P3** aturan keputusan utilitas (reward σ·g, penalti λ untuk salah, biaya μ per klaim); **P4** penegakan di decoding; **P5** kombinasi abstain+stop dalam satu aturan.

## 1. Peta prior art

### A. Conformal factuality dan filter klaim

| # | Work | Ver. | Apa yang dilakukan | σ (P1) | g (P2) | Aturan (P3) | Di decoding? (P4) | Data / metrik |
|---|---|---|---|---|---|---|---|---|
| A1 | Mohri & Hashimoto, *Language Models with Conformal Factuality Guarantees* (ICML 2024, arXiv 2402.10978) | V (arxiv html, 100k dari 101k karakter) | Output dipecah jadi sub-klaim (GPT-4), tiap klaim diberi skor (self-confidence, frekuensi 5 resample, dll.), back-off dengan ambang t yang dikalibrasi lewat split conformal; jaminan faktualitas ≥ 1−α | Skor klaim ada, tetapi dari output lengkap (black-box), bukan state generator + evidence | **Tidak ada**; utilitas hanya "% sub-klaim yang dibuang" | Ambang tunggal terkalibrasi untuk jaminan, **bukan** utilitas dengan λ, μ; tidak ada stopping rule eksplisit | **Tidak.** Post-processing output GPT-4 yang sudah selesai (ekstraksi halaman menyebutnya "decoding-time" secara konsep, implementasinya membuang klaim) | FActScore bios, NQ, MATH; 50 output dianotasi tangan per dataset; factuality empiris vs 1−α, % klaim dibuang. Frequency scoring: FActScore ~25% → ~80% dengan ~separuh klaim tersisa |
| A2 | Rubin-Toles et al., *Conformal LM Reasoning with Coherent Factuality* (arXiv 2505.17126, ICLR 2025) | V (abstrak) | Perluasan ke reasoning: filter subgraph deducibility | Tidak (skor klaim) | Tidak | Ambang konformal | Tidak (filter pasca) | MATH, FELM |
| A3 | *Response Quality Assessment for RAG via Conditional Conformal Factuality* (arXiv 2506.20978) | S | Conformal factuality bersyarat untuk RAG, ambang klaim terkalibrasi | Skor klaim vs evidence retrieved (belum dibaca) | Tidak diketahui | Ambang | Kemungkinan pasca | belum dibaca |
| A4 | *Adaptive Conformal Prediction for Improving Factuality of Generations by LLMs* (arXiv 2604.13991, 2026) | S | Ambang adaptif pada kerangka filtrasi long-form QA | — | — | Ambang | Pasca | belum dibaca |
| A5 | Quach et al., *Conformal Language Modeling* (ICLR 2024, arXiv 2306.10193) | V (abstrak) | Mengalibrasi **stopping rule untuk sampling** (kapan cukup banyak sampel agar himpunan berisi ≥1 jawaban acceptable) + rejection rule; juga mengidentifikasi frasa/kalimat yang benar | Tidak per klaim dari state | Tidak (stop = cukup sampel, bukan cukup evidence terekspresi) | Aturan henti terkalibrasi (jaminan coverage, bukan utilitas) | **Tidak:** beroperasi pada himpunan sampel | open-domain QA, summarization, radiologi |

Catatan: istilah "stopping rule" sudah dipakai di conformal LM, tetapi artinya berhenti **mengambil sampel**, bukan berhenti **mengemit klaim**.

### B. Metrik long-form: precision, recall, dan panjang

| # | Work | Ver. | Inti | Relevansi |
|---|---|---|---|---|
| B1 | Min et al., *FActScore* (EMNLP 2023, arXiv 2305.14251) | V (abstrak) | % atomic fact didukung sumber (Wikipedia). Precision-only. Paket resmi punya penalti panjang bila fakta < gamma (default 10) [S, dari hasil pencarian] | Satuan "klaim" dan evaluasi precision; **recall tidak diukur**; dataset bios untuk uji |
| B2 | Wei et al., *Long-form factuality in LLMs* (SAFE, LongFact; NeurIPS 2024, arXiv 2403.18802) | V (abstrak) | SAFE: LLM + Google Search per fakta; **F1@K**: precision didukung, recall terhadap K = jumlah fakta didukung yang diinginkan pengguna | **F1@K adalah trade-off verbosity vs factuality yang sudah diformalkan**; K adalah "g" kasar yang tetap, bukan evidence-conditioned. Tidak ada anotasi coverage per evidence |
| B3 | Zhao et al., *How Does Response Length Affect Long-Form Factuality* (ACL Findings 2025, arXiv 2505.23295) | V (abstrak) | Respons lebih panjang → precision lebih rendah; penyebab utama = **facts exhaustion** (model kehabisan pengetahuan andal), bukan error propagation/long context | Motivasi empiris kuat untuk "g → 0 ⇒ berhenti"; tetapi pengetahuan parametrik, bukan evidence yang dikirim. Tidak mengusulkan mitigasi (dari halaman) |
| B4 | Spataru et al., *Know When To Stop: A Study of Semantic Drift in Text Generation* (NAACL 2024, aclanthology 2024.naacl-long.202) | V (halaman ACL) | Fakta benar muncul awal, salah belakangan ("semantic drift"). Membandingkan metode **early stopping**, yang menukar jumlah informasi dengan faktualitas; reranking semantik membantu. Biografi Wikipedia | **Paling dekat dengan "berhenti saat sisa klaim didukung habis"**, tapi stop berbasis heuristik/oracle pasca-hoc (angka oracle 92%/58% berasal dari ringkasan pencarian [S], cocokkan ke PDF), tanpa evidence, tanpa σ, tanpa g, tanpa utilitas |
| B5 | Song et al., *VeriScore* (arXiv 2406.19276) | S | Klaim terverifikasi saja; recall terhadap K | Metrik, mirip SAFE |
| B6 | *Beyond Precision: Importance-Aware Recall…* (arXiv 2604.03141) | S | Recall berbobot kepentingan, referensi Wikipedia | Gagasan "bobot" pada g (weighted share) |

### C. Selective generation, abstensi klaim, kalibrasi long-form

| # | Work | Ver. | Inti | σ | g | Aturan | Decoding? | Data / metrik |
|---|---|---|---|---|---|---|---|---|
| C1 | Luo et al., *Only Say What You Know: Calibration-Aware Generation (CASS/CAG)* (arXiv 2605.01749, Mei 2026) | V (abstrak + html 100k/156k karakter) | Eksplorasi–komitmen terpisah: reasoning dengan label reliabilitas per langkah (VeriScore atas klaim, ambang τ), lalu jawaban hanya dari bagian reliabel; distilasi CAPD. **Appendix: utilitas asimetris +u1 benar / −u2 salah / 0 buang; aturan Bayes-optimal commit iff P(benar) ≥ u2/(u1+u2)** | Estimasi dari verifier eksternal (VeriScore) di reasoning, bukan state + evidence | **Helpfulness R=min(S/K,1)** dengan K tetap, bukan sisa evidence | **Ya, sebagian: ambang Bayes u2/(u1+u2) = (λ)/(1+λ) bila g=1, μ=0.** Tidak ada suku g atau μ, tidak ada stop | **Tidak:** dipelajari lewat training (SFT/distilasi), bukan constraint decoding keras | AlpacaFact, Biography, FactBench-Hard, Factory-Hard, FAVA; factuality P=S/\|A\|, helpfulness R, F1. Tidak membandingkan conformal factuality (di halaman). **Abstain-only baseline memangkas recall tajam** (ekstraksi pencarian [S]) |
| C2 | Liu & Wang, *CURE: Think Through Uncertainty* (arXiv 2604.12046, Apr 2026) | V (abstrak) | Model menghasilkan klaim atomik + confidence per klaim (dilatih), lalu **abstain per klaim saat inferensi** (selective prediction) | Ya per klaim, tapi verbal/terlatih dalam generator, bukan head dari state + evidence | Tidak | Ambang confidence | Filter inferensi, bukan gate distribusi | Biography, FactBench (+2); klaim-akurasi +39,9% Biography, AUROC +16,0% FactBench, recall dipertahankan |
| C3 | Kan, *Claim-Selective Certification for High-Risk Medical RAG* (arXiv 2605.21949, Mei 2026) | V (abstrak) | Respons dipecah jadi klaim, tiap klaim diskor terhadap evidence terambil; selector memilih aksi full / partial / conflict / abstain | Ya, klaim vs evidence (post-hoc) | Tidak ada notion coverage di halaman | Selector aksi, bukan utilitas σ·g | Tidak dinyatakan; tampak pasca | set medis weak-label (n=314/319); UCCR, PAU |
| C4 | Obeso et al., *Real-Time Detection of Hallucinated Entities in Long-Form Generation* (arXiv 2509.03531) | V (abstrak) | Linear probe (streaming, token-level) pada LLM sampai 70B; AUC 0,90 vs 0,71 semantic entropy untuk Llama-3.3-70B | Mirip P1 (probe dari state), tetapi tanpa evidence eksplisit | Tidak | Tidak ada stop/abstain di halaman | Deteksi saja | dataset long-form dianotasi web search |
| C5 | Itkin, *Quickest Detection of Hallucination Onset* (arXiv 2606.12476) | V (abstrak) | Hallucination onset sebagai quickest change detection; learned CUSUM; delay 11–13 token (tertangkap) atau 56–66 token (termasuk yang terlewat) | Skor token-level | Tidak | Aturan sekuensial (CUSUM), false-alarm vs delay | Monitor streaming (stop/alarm), bukan utilitas | RAGTruth |
| C6 | I-CALM (arXiv 2604.03904); Joren et al. *Sufficient Context* (ICLR 2025, 2411.06037); Controlling Risk of RAG (Findings EMNLP 2024); SURE-RAG (2605.03534) | S | Abstain tingkat jawaban dengan payoff (I-CALM, prompting) atau sufficiency evidence | Tingkat jawaban | Tidak | I-CALM: payoff benar/salah/abstain | Prompt/pra-generasi | QA pendek |
| C7 | Lee et al., *Selective Generation* (NeurIPS 2024) | S | Selective prediction untuk generasi | — | — | Risiko terkontrol | Pasca | belum dibaca |
| C8 | Nature Digital Medicine 2026, *When silence is safer: decision-theoretic framework for LLM abstention in healthcare* | S | Kerangka keputusan abstain berbiaya | Konseptual | — | Teori keputusan | Tidak | review |

### D. Learned EOS, length control, early exit, stopping dalam decoding

| # | Work | Ver. | Inti | Relevansi |
|---|---|---|---|---|
| D1 | Akter et al., *Anytime-Valid Answer Sufficiency Certificates via Sequential Information Lift (Sequential-EDFL)* (arXiv 2510.06478) | V (abstrak) | Menghentikan generasi lewat e-process dari lift log-likelihood model penuh vs "skeleton" lemah; gate kebenaran ringan hanya menunda stop; panjang −22–28%; 10,9% stop masih salah dengan gate. **Jaminan tidak mencakup kebenaran faktual** (dinyatakan penulis) | **Stopping rule di decoding yang sudah ada**, tetapi sufficiency = informasi model, bukan evidence yang dikirim; tanpa σ-vs-evidence, tanpa utilitas. Penjaga novelty untuk klaim "stop dalam decoding" |
| D2 | Length prediction from hidden states (ICLR 2026, arXiv 2602.11812) | S | Prediksi sisa token dari hidden state, progresif | Tanpa semantik faktual |
| D3 | ESTAR (2602.10004), TERMINATOR (2603.12529) | S | Early-stop reasoning (RL / exit point CoT) | Domain reasoning, bukan faktualitas |
| D4 | CodeFast (arXiv 2407.20042) | S | Head probabilitas-stop dari hidden state untuk kode | Mirip secara arsitektur (head kecil memutuskan stop), domain kode |
| D5 | Tu et al. 2016 (NMT coverage), See et al. 2017 *Pointer-Generator* coverage (arXiv 1704.04368) | S (via ringkasan hasil pencarian) | Coverage vector = jumlah attention kumulatif; loss coverage menekan pengulangan. See et al. membuang penalti panjang MT karena ringkasan tidak perlu cakupan merata | **Prior art langsung untuk g berbasis attention coverage** (jangan klaim "attention coverage" baru). Tujuan di sana: cegah pengulangan, bukan memutuskan berhenti berdasar sisa evidence didukung |

### E. Optimal stopping dan value of information

| # | Work | Ver. | Inti | Relevansi |
|---|---|---|---|---|
| E1 | Park et al., *Stop-RAG: Value-Based Retrieval Control for Iterative RAG* (arXiv 2510.14337) | V (abstrak) | Kapan berhenti **mengambil** di iterative RAG; MDP horizon terbatas, Q(λ) | Optimal stopping untuk retrieval, bukan stop emisi klaim. Nilai dipelajari end-to-end, bukan σ·g eksplisit |
| E2 | TASR (2606.13814); Optimal Bayesian Stopping (2602.05395); Optimal Stopping vs Best-of-N (2510.01394) | S (hasil pencarian) | Stop untuk iterative retrieval / sampling / best-of-n | Stopping di tingkat panggilan, bukan klaim |
| E3 | Dong et al., *Stateful Evidence-Driven RAG* (arXiv 2604.14170) | V (abstrak) | Evidence pool dengan deficiency analysis; berhenti saat iterasi tidak lagi menambal gap (aturan tidak tampak di halaman) | Notion "evidence tersisa/gap" pada tingkat retrieval |
| E4 | Stochastic RAG (2405.02816); U-RAG (marginal gain per dokumen) | S | Expected utility end-to-end / marginal gain per dokumen | Bahasa utilitas, bukan per klaim |

Pencarian "myopic value-of-information untuk keputusan emit klaim berikutnya" tidak menemukan paper yang cocok (dua query).

### F. Coverage / completeness evidence

| # | Work | Ver. | Inti | Relevansi |
|---|---|---|---|---|
| F1 | Gao et al., *ALCE* (EMNLP 2023, arXiv 2305.14627) | V (abstrak, hanya sebagian) | Benchmark sitasi: fluency, correctness, citation quality; ELI5 (halaman menyebut); ASQA dan QAMPARI dari pengetahuan umum/pencarian | Citation recall/precision = "attributable to identified sources". Untuk uji, lihat bagian 3 |
| F2 | Pradeep et al., *Great Nugget Recall* (arXiv 2504.15068); TREC RAG 2025 overview (2603.09891); Samuel et al., *Beyond Relevance: Retrieval and RAG Information Coverage* (2603.08819) | S, S, V (abstrak) | Nugget recall sebagai ukuran completeness respons RAG; coverage nugget berkorelasi dengan metrik coverage retrieval | Evaluasi **g realisasi** (nugget yang diekspresikan), tetapi nugget bukan "klaim evidence-supported yang belum ditulis" per langkah decoding |
| F3 | Stelmakh et al., *ASQA* (EMNLP 2022) | S | 6.316 pertanyaan; QA pair disambiguasi ekstraktif yang harus bisa dijawab oleh passage hasil | Anotasi coverage **ada** (QA pair) |
| F4 | Amouyal et al., *QAMPARI* (arXiv 2205.12665) | S | Pertanyaan berjawaban daftar entitas dari banyak paragraf; pasangan jawaban–paragraf pendukung otomatis lalu divalidasi | Anotasi coverage **ada** (daftar jawaban, ukuran g alami) |

## 2. Overlap per bagian dan kombinasi

- **P1 (σ per klaim dari state + evidence):** σ per token/entitas dari hidden state sudah ada (Obeso 2025; Lookback Lens; Critic-Driven; EAG kita sendiri). σ **per klaim terhadap evidence yang dikirim**: Claim-Selective Certification (pasca-hoc), CASS (VeriScore, verifier eksternal), CURE (confidence terlatih dalam generator). **Yang tidak ditemukan:** σ klaim berikutnya dari head pada hidden state + cross-attn ke evidence units, dibaca *sebelum* klaim diemit (prediktif).
- **P2 (g, sisa evidence supported):** ada bentuk dekat: attention coverage (Tu 2016, See 2017), nugget recall (TREC), F1@K (K tetap), CASS helpfulness min(S/K,1). **Tidak ditemukan** g sebagai *sisa* (uncovered) yang dihitung online per langkah dan dipakai sebagai input keputusan. Semua bentuk terdekat adalah metrik evaluasi (pasca) atau regularizer anti-repetisi.
- **P3 (aturan utilitas):** **CASS appendix sudah menurunkan ambang Bayes u2/(u1+u2)** (+u1, −u2, 0) dan I-CALM memakai payoff. Aturan σ·g − λ(1−σ) − μ > 0 adalah perluasan: hadiah dikalikan g (nilai marginal klaim) dan biaya μ per klaim. Dengan g=1, μ=0 aturan Anda tereduksi menjadi ambang CASS (λ/(1+λ)). Jadi **ambang keputusan terhadap σ bukan baru**; yang baru hanya suku g dan μ, dan secara matematis hanya aljabar sederhana (jangan dijual sebagai teorema).
- **P4 (penegakan di decoding):** Sequential-EDFL (stop di decoding), Critic-Driven Decoding, Token-Guard, Lookback Lens menegakkan sesuatu saat decoding. Untuk abstain/filter klaim, hampir semua (conformal, CURE, CASS, Claim-Selective) bekerja pasca-hoc atau lewat training. Penegakan di decoding **dengan sinyal yang sama diuji sebagai advice** (kontras H3) tetap tidak ditemukan; ini selaras dengan §5.6 di `04_prior_art_EAG`.
- **P5 (menyatukan abstain dan stop):** Tidak ditemukan satu aturan yang sama mengatur "tidak mulai" dan "berhenti". Namun secara konsep kedua hal dipisah di literatur (selective generation vs early stopping), dan Semantic Drift (Spataru) + CURE + CASS sudah melakukan "buang/berhenti pada klaim tidak andal" dengan bahasa berbeda. Penyatuan formal itu kecil secara teknis: stop = abstain pada klaim ke-k.

## 3. Novelty verdict

**Jelas TIDAK baru (jangan diklaim):**
1. Memecah generasi jadi klaim dan memfilter klaim dengan skor + ambang terkalibrasi (conformal factuality 2024, follow-up 2025–2026, CURE, CASS, Claim-Selective).
2. Aturan Bayes-optimal "komit iff P(benar) ≥ u2/(u1+u2)" dengan utilitas asimetris (CASS appendix; I-CALM).
3. Trade-off verbosity vs faktualitas dan fakta bahwa panjang menurunkan precision; early stopping untuk menaikkan faktualitas (Zhao 2025 "facts exhaustion"; Spataru 2024; F1@K).
4. Stopping rule dalam decoding berbasis sinyal internal (Sequential-EDFL), head stop dari hidden state (CodeFast), prediksi sisa panjang dari hidden state (ICLR 2026).
5. Optimal stopping / value-based untuk retrieval (Stop-RAG) dan "stopping rule" konformal untuk sampling (Quach 2024).
6. Attention coverage sebagai pelacak apa yang sudah diekspresikan (Tu 2016, See 2017); nugget recall sebagai ukuran completeness.

**Kombinasi yang MUNGKIN baru (tahan dengan hati-hati, tanda "tidak ditemukan dalam ±25 query"):**
- Keputusan **prediktif sebelum emisi** per klaim, dari head pada hidden state generator + evidence units, dengan **g evidence-conditioned (sisa uncovered)** masuk ke utilitas, sehingga satu ambang σ*(g) = (λ+μ)/(g+λ) bergeser ke atas saat g mengecil. Prediksi yang bisa diuji: kurva berhenti-lebih-awal ketika evidence habis, bukan ketika model kehabisan pengetahuan (beda dari Zhao 2025).
- Penegakan keras di decoding **diuji terhadap advice dengan sinyal identik** (kontribusi H3 Anda), kini diperluas ke keputusan stop. Ini tetap klaim yang paling dapat dipertahankan; aturan σ·g sebaiknya dibingkai sebagai instrumen, bukan kontribusi utama.
- Risiko serius: **g sulit dibuat valid**. Entailment atas evidence units menghasilkan "sisa" yang mungkin redundan atau tak layak diekspresikan; pada prinsipnya ini nugget recall yang dibalik. Jika g tidak menaikkan AURC/F1 dibanding σ saja (g=1), kombinasi runtuh menjadi CASS-threshold. **Ablasi wajib: aturan dengan g=1, μ=0 vs penuh.**
- Jebakan interpretatif: temuan Fase 1b (advisory = plasebo, authority −11 pp halusinasi) datang dari satu model 3B, kontras primer degenerate; jangan menjadikannya motivasi utama tanpa replikasi.

**2–3 paper paling berbahaya (baca PDF penuh):**
1. **Luo et al., CASS/CAG** (https://arxiv.org/abs/2605.01749): utilitas asimetris + ambang Bayes + helpfulness vs factuality pada klaim long-form, lima benchmark. Menutup P3 sebagian besar dan kerangka evaluasi (P/R/F1). Belum membaca 56k karakter terakhir html; periksa apakah ada komponen stop atau decoding keras.
2. **Spataru et al., Know When To Stop** (https://aclanthology.org/2024.naacl-long.202/): ide "berhenti agar faktual" dan trade-off informasi vs faktualitas sudah ada pada biografi. Reviewer akan menyebutnya pertama.
3. **Akter et al., Sequential-EDFL** (https://arxiv.org/abs/2510.06478): stopping rule di decoding dengan jaminan sekuensial; mengambil klaim "stopping ditegakkan di decoding". Pembeda: sufficiency model-internal, bukan evidence dan faktualitas.
Pendamping: Mohri & Hashimoto (framing jaminan: reviewer akan meminta baseline konformal), Zhao 2025 (motivasi facts exhaustion).

**Dataset untuk uji (evidence + anotasi coverage):**

| Dataset | Evidence yang tersedia | Anotasi coverage | Catatan | Ver. |
|---|---|---|---|---|
| ASQA (via ALCE) | passage Wikipedia (korpus 21M dalam ALCE) | **Ya:** QA pair disambiguasi ekstraktif (g = share pasangan terjawab) | Metrik standar: ROUGE + QA accuracy; cocok untuk g | ASQA [S]; ALCE [V parsial] |
| QAMPARI (via ALCE) | paragraf pendukung per jawaban (otomatis, divalidasi manual) | **Ya:** daftar jawaban lengkap = g alami (share entitas tersisa) | Cocok untuk stop saat daftar habis; F1 tertinggi 32,8 menunjukkan sulit | [S] |
| ELI5 (via ALCE) | passage retrieved | **Sebagian:** setahu saya ALCE membuat klaim dari jawaban emas lewat LLM (perlu diverifikasi di paper); halaman hanya mengonfirmasi ELI5 dan citation support | Cek definisi claim recall di PDF | [V] hanya ELI5 ada; sisanya perlu cek |
| FActScore bios | halaman Wikipedia entitas | **Tidak** untuk recall (FActScore precision-only); evidence ada, "klaim yang seharusnya ada" harus dibangun (mis. atomisasi halaman) | Dipakai conformal factuality dan Semantic Drift: baseline langsung | [V abstrak] |
| LongFact (SAFE) | tidak ada evidence tetap; SAFE memakai Google Search | Tidak; recall via K | Tidak cocok kecuali dibuat evidence tetap | [V abstrak] |
| TREC RAG 2024/2025 nuggets | korpus MS MARCO V2.1 [S] | **Ya:** nugget vital/okay | Cocok untuk g sebagai nugget recall; model 3B mungkin terlalu lemah | [S] |

Rekomendasi eksperimen minimal: ASQA + QAMPARI dengan evidence units = passage gold/retrieved, g dari QA pair/daftar jawaban (anotasi yang sudah ada, sehingga g tidak perlu diestimasi lewat LLM untuk evaluasi); FActScore bios sebagai uji perbandingan terhadap Mohri & Hashimoto dan Spataru.

## 4. Baseline wajib untuk ide ini
1. Conformal factuality (frequency / self-confidence score) pada klaim yang sama.
2. Aturan CASS: σ ≥ u2/(u1+u2) (g=1, μ=0) sebagai ablasi.
3. Early stopping Semantic Drift (heuristik) dan EOS bawaan model.
4. σ sebagai advice (di prompt dan terlatih) vs authority pada aturan yang sama.
5. Metrik: F1@K / klaim didukung vs jumlah klaim, kurva risk–coverage dalam satuan klaim, nugget/QA-pair recall.

## 5. Sumber
- https://arxiv.org/abs/2402.10978 · https://arxiv.org/html/2402.10978v1 (dibaca)
- https://arxiv.org/abs/2505.17126 (dibaca)
- https://arxiv.org/abs/2306.10193 (dibaca)
- https://arxiv.org/abs/2305.14251 (dibaca) · https://arxiv.org/abs/2403.18802 (dibaca)
- https://arxiv.org/abs/2505.23295 (dibaca)
- https://aclanthology.org/2024.naacl-long.202/ (dibaca)
- https://arxiv.org/abs/2605.01749 · https://arxiv.org/html/2605.01749 (dibaca sebagian)
- https://arxiv.org/abs/2604.12046 (dibaca) · https://arxiv.org/abs/2605.21949 (dibaca)
- https://arxiv.org/abs/2509.03531 (dibaca) · https://arxiv.org/abs/2606.12476 (dibaca)
- https://arxiv.org/abs/2510.06478 (dibaca) · https://arxiv.org/abs/2510.14337 (dibaca) · https://arxiv.org/abs/2604.14170 (dibaca)
- https://arxiv.org/abs/2603.08819 (dibaca) · https://arxiv.org/abs/2305.14627 (dibaca)
- Hanya hasil pencarian: https://arxiv.org/html/2506.20978v1 · https://arxiv.org/pdf/2604.13991 · https://arxiv.org/pdf/2602.11812 · https://arxiv.org/pdf/2602.10004 · https://arxiv.org/pdf/2603.12529 · https://arxiv.org/pdf/2407.20042 · https://arxiv.org/pdf/1704.04368 · https://arxiv.org/pdf/2205.12665 · https://arxiv.org/pdf/2504.15068 · https://arxiv.org/pdf/2603.09891 · https://arxiv.org/html/2604.03904 · https://arxiv.org/html/2605.03534v1 · https://arxiv.org/pdf/2406.19276 · https://arxiv.org/pdf/2604.03141 · https://alphaxiv.org/benchmarks/carnegie-mellon-university/asqa · https://www.nature.com/articles/s41746-026-02882-1
