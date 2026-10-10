# 09 — Teori, posisi benchmark, dan kosakata (EAA)

Tanggal: 2026-10-11 · Penyusun: literature-scout · Label: **[V]** = halaman/abstrak/HTML dibaca lewat WebFetch pada sesi ini; **[S]** = hanya hasil pencarian.
Catatan: banyak halaman arXiv hanya memberi abstrak; bila sebuah angka/teorema tidak terbaca, ditulis "tidak terbaca" dan TIDAK ditebak.

---

## A. TEORI — apa yang diketahui secara matematis

### A1. Xu, Jain, Kankanhalli, *Hallucination is Inevitable* (arXiv 2401.11817, v2 Feb 2025) [V, abstrak]
- Klaim: LLM dan ground truth dimodelkan sebagai fungsi *computable*; halusinasi = ketidaksesuaian keduanya. Dengan teori pembelajaran, "LLM tidak dapat mempelajari semua fungsi computable", sehingga halusinasi tak terhindarkan bila LLM dipakai sebagai *general problem solver*.
- Berlaku untuk: model sebagai solver umum, di dunia formal. Tidak menyatakan laju halusinasi pada tugas sempit/berkonteks, dan tidak menyatakan abstensi mustahil.
- Relasi: **tidak melarang gate kita.** Gate mengubah keluaran menjadi "abstain", yang bukan jawaban salah; argumen diagonalisasi hanya menyerang model yang diwajibkan menjawab semua input.

### A2. Kalai & Vempala, *Calibrated Language Models Must Hallucinate* (STOC 2024, arXiv 2311.14648) [V, abstrak]
- Klaim: model pra-latih yang terkalibrasi punya batas bawah statistik halusinasi untuk "fakta arbitrer" (tak dapat disimpulkan dari data); laju kira-kira sebesar proporsi fakta yang muncul **tepat sekali** di data latih (estimasi Good-Turing / *missing mass*).
- Asumsi: kalibrasi statistik, probabilitas maksimum tiap fakta terbatas, data latih tanpa kesalahan. Tidak berlaku untuk fakta yang muncul >1 kali atau fakta sistematis (aritmetika).
- Relasi: batas ini untuk **pengetahuan parametrik**. Pada setting kita (evidence di konteks) kuantitas yang relevan bukan "fakta singleton di data latih" melainkan "apakah evidence cukup". Batas ini justru **memotivasi abstensi/pasca-latih**, dan tidak dapat dipakai untuk mengklaim bahwa halusinasi dengan evidence yang lengkap tak terhindarkan.

### A3. Kalai, Nachum, Vempala, Zhang, *Why Language Models Hallucinate* (arXiv 2509.04664, 4 Sep 2025) [V, HTML 100k karakter pertama]
- Teorema 1: untuk distribusi latih apa pun dengan p(V)=1 dan model dasar p̂: **err ≥ 2·err_iiv − max_c|V_c| / min_c|E_c| − δ**; err = laju galat generatif, err_iiv = galat klasifikasi "Is-It-Valid" (IIV), δ = |p̂(A) − p(A)| (miskalibrasi pada ambang 1/min_c|E_c|). Ringkasan: galat generatif ≳ 2 × galat klasifikasi IIV. Klasifier IIV: f̂(x)=+ bila p̂(x) > 1/|E|.
- Argumen sosio-teknis: evaluasi biner (benar=1, salah=0, "tidak tahu"=0) menghadiahi tebakan. **Usulan (Sec. 4.2):** cantumkan target keyakinan t di prompt; benar = +1, salah = −t/(1−t), "tidak tahu" = 0. Menjawab menguntungkan secara ekspektasi **tepat bila P(benar) > t**. t=0 → penilaian biner; t=0,5/0,75/0,9 → penalti 1/2/9.
- Bagian 45k karakter terakhir (diskusi, lampiran) tidak terbaca.

### A4. Geifman & El-Yaniv, *Selective Classification for Deep Neural Networks* (NeurIPS 2017, arXiv 1705.08500) [V, abstrak; venue NeurIPS dari pengetahuan, halaman hanya memberi arXiv]
- Klaim: pengguna menentukan **tingkat risiko** yang diinginkan; saat uji, classifier menolak instans seperlunya agar risiko (galat di antara yang diterima) ≤ target **dengan probabilitas tinggi**. Contoh abstrak: galat top-5 2% dijamin dengan probabilitas 99,9% pada coverage ≈60% (ImageNet).
- Konsep: risk–coverage curve, AURC, aturan reject-option (Chow). Ini kerangka baku yang akan dipakai penguji.

### A5. Mohri & Hashimoto, *Language Models with Conformal Factuality Guarantees* (ICML 2024, arXiv 2402.10978) [V, HTML]
- Jaminan: **P(keluaran yang dikembalikan ter-entail oleh referensi) ≥ 1 − α**, probabilitas atas data kalibrasi dan uji yang *exchangeable*; ambang = kuantil empiris dari "ambang aman" per contoh pada set kalibrasi berlabel; berlaku untuk α dalam [1/(n+1), 1].
- Batas yang dicatat paper/HTML: jaminan **marginal** (bukan kondisional per input), marginal atas draw kalibrasi (set kecil → deviasi), dan **gugur saat distribution shift**.

### A6. Hasil 2025–2026 lain
- Karbasi, Montasser, Sous, Velegkas, *(Im)possibility of Automated Hallucination Detection* (arXiv 2504.17004) [V, abstrak]: bila detektor hanya melihat contoh benar, deteksi ≈ *language identification* dan "mustahil untuk kebanyakan koleksi bahasa"; dengan **contoh negatif berlabel pakar**, deteksi mungkin untuk semua koleksi terhitung. Relasi: pelatihan σ kita memakai negatif kontrafaktual (ablasi evidence) — secara struktural masuk rezim "dengan negatif", tetapi hasil itu tentang kelas hipotesis abstrak, bukan jaminan untuk head 3,4M param.
- Karpowicz, *On the Fundamental Impossibility of Hallucination Control* (arXiv 2506.06382) [S]: tidak ada mekanisme inferensi yang memenuhi serentak empat sifat (truthful generation, konservasi informasi semantik, pengungkapan pengetahuan relevan, optimalitas terbatas pengetahuan). Belum dibaca; jangan dikutip detailnya.
- Xu et al., *Geometry-Calibrated Conformal Abstention* (arXiv 2604.27914, Apr 2026) [V, abstrak]: jaminan sampel-hingga atas peluang **berpartisipasi (tidak abstain)** dan peluang **respons benar**; bentuk bound dan asumsi tidak terbaca dari abstrak.
- Wu et al., *BAS: decision-theoretic evaluation of LLM confidence* (arXiv 2604.03216, Apr 2026) [V, abstrak]: model utilitas jawab-atau-abstain; "keyakinan yang jujur secara unik memaksimalkan BAS yang diharapkan". Ini versi teori-keputusan dari argumen Kalai 2025.

### A7. Hubungan dengan gate dan aturan berhenti kita (turunan sendiri, bukan klaim paper)
Aturan: lanjut ⇔ σ·g − λ(1−σ) − μ > 0 ⇔ **σ > (λ+μ)/(g+λ)**.
- Dengan g=1, μ=0: σ > λ/(1+λ). Substitusi λ = t/(1−t) memberi **σ > t**, yaitu persis aturan jawab-bila-P(benar)>t pada skor ber-penalti t/(1−t) (Kalai 2025) dan pada Bayes-rule biaya (CASS, sudah dicatat di `07_prior_art_stopping_rule.md`). Gate σ<0,5 = t=0,5 = λ=1 (penalti simetris). Utilitas P3 kita U = benar − 2·halusinasi = λ=2 ↔ t=2/3.
- **Syarat yang membuat ini "instance" dan bukan sekadar analogi:** σ harus sama dengan P(jawaban benar | fitur). Pada kita σ = P(evidence **cukup**). Cukup ≠ benar (generator 3B bisa salah walau evidence cukup; bisa benar tanpa evidence cukup lewat memori parametrik/tebakan). Maka ambang optimal pada σ hanya optimal bila P(benar|σ) naik-monoton dan dikalibrasi; ini harus **diukur** (reliability diagram P(benar) vs σ), bukan diasumsikan.
- Yang baru dari aturan kita hanyalah g (sisa evidence tak terliput) dan μ (biaya melanjutkan); teorinya sendiri adalah teori keputusan standar. Ablasi g=1 tetap wajib.

### A8. Apa yang rumus BISA dan TIDAK BISA menjamin
BISA:
- Optimalitas keputusan *dengan syarat* probabilitas dikalibrasi dan biaya diketahui (A7; Kalai 2025 Sec. 4.2; BAS).
- Jaminan marginal berfrekuensi untuk risiko/factuality di bawah *exchangeability* (Geifman & El-Yaniv; Mohri & Hashimoto), dengan harga coverage (jangan lupa: risiko turun karena menolak).
- Menunjukkan bahwa tebakan dihadiahi oleh penilaian biner (Kalai 2025) — argumen untuk melaporkan skor ber-penalti.
TIDAK BISA:
- Menghilangkan halusinasi: A1–A3 (di bawah asumsi masing-masing) menyatakan model generatif tanpa abstensi tetap salah; abstensi memindahkan galat ke false refusal, tidak menghapusnya. Kita memang mengukur harganya: **+11 poin false refusal**.
- Menjamin kebenaran pada input individual (jaminan konformal marginal, bukan kondisional).
- Bertahan di bawah distribution shift (Mohri & Hashimoto; hasil kita: σ dilatih pada HotpotQA ablasi paragraf, bukan di domain lain).
- Menjamin σ itu kalibrasi untuk *kebenaran* (lihat A7).
- Membuktikan bahwa 0,99 pairwise accuracy berarti deteksi kecukupan yang baik di luar distribusi ablasi buatan (A6/Karbasi: bergantung pada distribusi negatif).

---

## B. POSISI BENCHMARK — angka yang bisa dibandingkan

Aturan keras: **tidak ada angka di bawah ini yang langsung sebanding dengan hasil kita** kecuali dinyatakan; pembanding sejati harus dijalankan ulang pada data/model kita.

| Karya | Dataset / model | Metrik | Angka (terbaca) | Sebanding? |
|---|---|---|---|---|
| Joren et al., *Sufficient Context* (arXiv 2411.06037, v3 Apr 2025) [V HTML] | FreshQA 452 (77,4% cukup), Musique-Ans 500 (~44,6% cukup), HotPotQA 500 (top-5 retrieved, ~44% cukup); Gemini 1.5 Pro/Flash, GPT-4o, Claude 3.5, Gemma 27B | autorater kecukupan; selective generation | Autorater Gemini 1.5 Pro 1-shot akurasi 93,0% (F1 0,935) pada 115 contoh berlabel manusia; FLAMe 24B 87,8%. Selective generation: +2–10 poin fraksi jawaban benar di antara yang dijawab; >10 poin Gemma 27B HotPotQA di coverage tinggi-akurasi, >5 poin Gemini 1.5 Pro HotPotQA di ~70% coverage; Musique Gemma 27B: tanpa gain. Konteks tak cukup: Gemini 1.5 Pro menjawab 50%, halusinasi 40,4% (subset manusia, 45,2% tak cukup) | **Paling dekat secara konsep, tidak langsung sebanding**: model 27B–frontier vs 3B; konteks retrieval alami vs ablasi paragraf; metrik gain akurasi@coverage vs penurunan halusinasi absolut. Layak sebagai baseline *autorater* (jalankan ulang). Perbandingan angka kualitatif: model besar juga menjawab pada konteks tak cukup (sejalan dengan 22,6% halusinasi kita). |
| SURE-RAG (arXiv 2605.03534, v2 Jul 2026) [V abstrak] | HotpotQA-RAG v3 (benchmark terkontrol); verifier klaim–evidence | Macro-F1 tiga arah; risk@coverage | Macro-F1 0,9075 (GPT-4o judge 0,7284); risk@30% coverage 0,2588 → 0,1642 (−37% relatif) | **Paling mirip tugas** (kecukupan multi-hop → selective answering), tapi dataset buatan sendiri, metrik berbeda; bukan bandingan angka. Wajib dibaca sebagai prior art/baseline. |
| Farquhar et al., semantic entropy (Nature 630, 2024) [V PMC] | TriviaQA, SQuAD1.1, BioASQ, NQ-Open, SVAMP; LLaMA-2-chat 7/13/70B, Falcon 7/40B, Mistral 7B; 10 sampel | AUROC (deteksi jawaban salah), AURAC | AUROC rata-rata 30 kombinasi: SE 0,790; P(True) 0,698; naive entropy 0,691; embedding regression 0,687; SE 0,78–0,81 lintas model 7B–70B | **Tidak sebanding**: QA tanpa konteks (parametrik), metrik AUROC jawaban-salah, bukan kecukupan evidence. Dipakai sebagai baseline *metode* (jalankan SE/P(True) pada Qwen2.5-3B kita). |
| Kossen et al., Semantic Entropy Probes (arXiv 2406.15927) [S/V parsial: abstrak tanpa angka] | beragam | AUROC | Kisaran 0,7–0,95 dari ringkasan sekunder (S) | Tidak sebanding; angka per-model tidak terbaca. Baseline probe hidden-state yang paling mirip arsitektur head kita. |
| Chuang et al., Lookback Lens (EMNLP 2024, arXiv 2407.07071) [V HTML] | LLaMA-2-7B-Chat; CNN/DM, NQ; detektor lintas tugas | AUROC deteksi halusinasi kontekstual | Predefined span: Lookback Lens 98,3/97,7 in-domain, 85,3/82,0 transfer; hidden state 100,0 in-domain, 79,4–84,7 transfer; NLI SoTA transfer 76,6/58,6. Sliding window 8: 88,3/86,2, transfer 66,1/66,0 | Tidak sebanding (deteksi *halusinasi dalam jawaban tergenerasi*, bukan kecukupan sebelum jawab; label berbeda). Pelajaran penting: **probe hidden-state ~100 in-domain tetapi turun ke ~80 transfer** — pairwise 0,99 kita juga in-domain. Baseline: Lookback Lens + probe hidden-state. |
| AbstentionBench (Kirichenko et al., NeurIPS 2025, arXiv 2506.09038) [V abstrak] | 20 dataset, 20 LLM frontier | abstensi pada pertanyaan tak terjawab/kurang spesifik/premis salah | Reasoning fine-tuning menurunkan abstensi rata-rata 24%; scaling tak banyak membantu; system prompt membantu tetapi tidak menyelesaikan. Metrik/dataset rinci tidak terbaca dari abstrak. | Tidak sebanding secara angka. Hanya benchmark yang **wajib dijalankan** bila kita mau klaim abstensi umum. |
| Self-RAG (Asai et al., arXiv 2310.11511) [V abstrak] | 7B/13B | open-domain QA, fakta, sitasi | Abstrak hanya klaim kualitatif (mengungguli ChatGPT & Llama2-chat+RAG); angka tidak terbaca | Tidak sebanding; baseline arsitektur. |
| CRAG (Yan et al., arXiv 2401.15884) [V abstrak] | 4 dataset | – | Hanya "meningkat signifikan"; angka tidak terbaca | Tidak sebanding. |
| R-Tuning (Zhang et al., NAACL 2024, arXiv 2311.09677) [V abstrak] | – | akurasi pada yang dijawab, refusal | Angka tidak terbaca | Tidak sebanding (refusal parametrik, bukan evidence-conditioned). |
| Compression-Aware Abstention; RINSE | – | – | Sudah di matrix #20 dan #23 (V pada sesi sebelumnya); **pencarian ulang hari ini tidak menemukan RINSE/Compression-Aware**, jadi angka tidak diulang di sini | Cek ulang ID arXiv di matrix sebelum dikutip di tulisan. Compression-Aware adalah pembanding terdekat (halusinasi −97%, tetapi definisi dan setting berbeda). |
| Lain 2026 (hanya [S]) | GRACE (RL abstain, 2601.04525); OverSearchQA (2601.05503); LIT-RAGBench (2603.06198); "Learning Evidence Sufficiency Boundaries" (2609.01687, tidak-answerable 0,095 vs 0,101); HALT (2608.02009, stopping retrieval); I-CALM (2604.03904) | – | – | Belum dibaca; kandidat prior art. |

### B2. Apa yang akan diminta penguji (metrik)
1. **Risk–coverage curve + AURC** (σ sebagai skor konfidensi) dan *risk@coverage* / *coverage@risk* (Geifman & El-Yaniv). Kita sudah punya selective risk 0,19–0,36 → 0,75–0,84 saat paragraf jawaban dibuang; laporkan kurvanya, bukan hanya titik τ=0,5.
2. **AUROC σ untuk "jawaban benar vs salah"** (bukan hanya pairwise kecukupan), plus **ECE / reliability diagram**; AUROC dan ECE pada σ → *kebenaran* (lihat A7).
3. **Abstention precision/recall/F1** (abstain bila seharusnya) dan **false refusal pada evidence lengkap** (sudah ada) dengan CI.
4. **Skor ber-penalti ala Kalai 2025** (t = 0,5; 0,75; 0,9) selain U(λ=2), supaya terbaca di komunitas.
5. Eksternal: setidaknya satu set dari **AbstentionBench** atau QA multi-hop lain (MuSiQue, 2Wiki) untuk generalisasi; sekarang hanya HotpotQA distractor.
6. Hasil lintas-seed/model; audit manusia atas label (sudah ada audit Claude, tapi bukan manusia).

### B3. Baseline yang wajib dijalankan sendiri (pada Qwen2.5-3B / Gemma 4 E4B, set yang sama)
- (a) Konfidensi generator: probabilitas token jawaban, rata-rata log-prob, **P(True)**, verbalized confidence → semuanya sebagai skor selective (AURC).
- (b) **Semantic entropy** (10 sampel) dan **SE probe** (hidden state).
- (c) **Autorater kecukupan zero-/few-shot** (gaya Joren et al.) dengan LLM yang sama dan dengan judge yang lebih besar; dan kombinasi autorater + konfidensi (selective RAG Joren).
- (d) **Probe linear pada hidden state** tanpa head arsitektur (pengendali: apakah 3,4M param perlu?), **YOPO-style direction** (matrix #24), **Lookback Lens**.
- (e) Gate-**acak** dan gate-oracle kecukupan (batas atas) pada tingkat abstensi yang sama; ini mengendalikan klaim "turun 13,3 poin" yang tergantung tingkat abstensi.
- (f) Prompt abstain-eksplisit ("jawab 'tidak cukup' bila evidence tak memuat jawaban") sebagai pembanding sederhana untuk advice/otoritas.
- (g) Conformal threshold (Mohri & Hashimoto / Geifman) untuk menetapkan τ, bukan 0,5 buatan tangan.

---

## C. "HOW NOT TO SOUND NAIVE"

### C1. Istilah yang harus dipakai dengan benar
1. **Selective prediction / reject option**: model + fungsi seleksi g; kinerja = (coverage, selective risk). "Hallucination turun" harus dibaca sebagai risk di antara jawaban yang diberikan, bukan kebenaran total.
2. **Risk–coverage trade-off, AURC**: menurunkan risiko dengan menolak itu *wajar*; yang bernilai adalah kurva yang lebih baik dari skor konfidensi lain pada coverage sama.
3. **Abstention vs refusal**: abstention = menahan jawaban karena ketidakpastian/kecukupan; *refusal* (safety refusal) = menolak karena kebijakan. Pakai "abstention"; "false refusal" boleh hanya sebagai istilah operasional kita, definisikan sekali.
4. **Faithfulness (terhadap konteks) vs factuality (terhadap dunia)**: 74–84% confabulation menyalin string dari evidence tersisa = unfaithful-to-sufficiency tetapi bukan "karangan dari nol". Hasil kita tentang *faithfulness/groundedness*, bukan factuality umum.
5. **Intrinsic vs extrinsic hallucination** (Ji et al. survei), **confabulation** (Farquhar: jawaban arbitrer/tidak konsisten) — jangan mencampur dengan "kesalahan sistematis".
6. **Context-faithfulness & knowledge conflict** (Xu et al. 2024 survei; matrix #13): parametrik vs konteks; bedakan "evidence tidak ada" dari "evidence konflik".
7. **Calibration**: ECE, reliability diagram, *proper scoring rule*; σ yang dilatih BCE tidak otomatis terkalibrasi, apalagi untuk kebenaran.
8. **Sufficiency vs relevance vs correctness**: Joren et al.: konteks cukup bila *dapat menyimpulkan* jawaban; relevan tidak berarti cukup (RINSE). σ kita = kecukupan, bukan kebenaran.
9. **Conformal prediction / exchangeability / marginal coverage**: sebut asumsi bila bicara "jaminan".
10. **Counterfactual evidence ablation vs natural insufficiency**: ablasi paragraf adalah distribusi sintetis; retrieval alami yang tak cukup berbeda (perhatikan Karbasi: distribusi negatif menentukan).
11. **Advisory (in-context) vs enforced (decoding/gate) control**; padanan literatur: *prompting vs constrained decoding / guardrail*; "otoritas" bukan istilah baku — gunakan "hard gate / enforced abstention".
12. **Placebo/shuffled control, TOST equivalence**: sudah kuat; sebut bahwa TOST ±0,02 adalah margin pilihan sendiri.

### C2. Klaim yang akan dianggap overclaim
- "Menghilangkan/mengurangi halusinasi 13,3 poin": kurang tepat bila tanpa coverage. Halusinasi didefinisikan sebagai jawaban salah dalam populasi *bersama* abstain→0; harus dibandingkan dengan gate-acak/ konfidensi biasa pada tingkat abstensi sama. Teori (A1–A3) menyatakan galat tidak hilang, hanya dialihkan ke abstensi.
- "Saran tidak bekerja / otoritas bekerja" sebagai sifat umum: terbukti hanya untuk Qwen2.5-3B dan Gemma 4 E4B, satu format prompt, satu dataset; Gemma P2 gagal kriteria pre-reg (−0,042 > −0,05). Katakan "pada setting ini".
- "Replikasi lintas keluarga": hanya satu generator non-Qwen; σ tetap dari Qwen.
- "σ = P(evidence sufficient)" sebagai probabilitas: tanpa uji kalibrasi itu skor. 0,99 pairwise ≠ AUROC kecukupan penuh atau AUROC kebenaran.
- Menyebut aturan σ·g − λ(1−σ) − μ "baru/ditemukan": bentuk g=1 identik Kalai 2025/CASS/teori Bayes; yang mungkin baru hanya g online dan penyatuan abstain+stop; belum diuji.
- "Epistemic arbitration/ akses epistemik" sebagai bukti: eksperimen kita black-box pada perilaku; bukan klaim mekanistik tentang model "tahu".
- Membandingkan langsung dengan Sufficient Context/Compression-Aware tanpa menyamakan model, data, metrik.
- Lupa bahwa 22,6% baseline halusinasi mungkin dipengaruhi judge/label (ada audit ambigu 22 kasus): laporkan sensitivitas.

---

## Sumber
- https://arxiv.org/abs/2401.11817 · https://arxiv.org/abs/2311.14648 · https://arxiv.org/abs/2509.04664 (HTML: https://arxiv.org/html/2509.04664v1)
- https://arxiv.org/abs/1705.08500 · https://arxiv.org/abs/2402.10978 (HTML: https://arxiv.org/html/2402.10978)
- https://arxiv.org/abs/2504.17004 · https://arxiv.org/abs/2506.06382 [S] · https://arxiv.org/abs/2604.27914 · https://arxiv.org/abs/2604.03216
- https://arxiv.org/abs/2411.06037 (HTML: https://arxiv.org/html/2411.06037) · https://arxiv.org/abs/2605.03534
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11186750 · https://arxiv.org/abs/2406.15927 · https://arxiv.org/html/2407.07071v2
- https://arxiv.org/abs/2506.09038 · https://arxiv.org/abs/2310.11511 · https://arxiv.org/abs/2401.15884 · https://arxiv.org/abs/2311.09677
