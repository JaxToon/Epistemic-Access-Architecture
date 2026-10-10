# 10 — Audit sitasi (status publikasi) · 2026-10-11

Cakupan: semua karya yang disebut di `01_literature_matrix_v0.1.md`, `04_prior_art_EAG_v0.1.md`, `07_prior_art_stopping_rule.md`, `09_benchmark_and_theory.md`.

## Metode dan batasan (baca dulu)
- Semantic Scholar API mengembalikan HTTP 429 dan DBLP diblokir (Anubis) pada sesi ini, jadi **tidak ada cross-check S2/DBLP**. OpenReview menampilkan halaman verifikasi browser, jadi forum OpenReview tidak bisa dibuka langsung.
- Sumber yang dipakai: halaman abs arXiv (kolom Comments/Journal-ref, dibuka lewat WebFetch), ACL Anthology (WebFetch + hasil pencarian terbatas ke aclanthology.org), hasil pencarian terbatas ke domain venue (iclr.cc, neurips.cc, proceedings.neurips.cc, proceedings.mlr.press, openreview.net, nature.com, dl.acm.org, colmweb.org), dan daftar COLM 2025 (dibuka langsung).
- Keterangan status:
  - **PEER-REVIEWED** = ada venue + tahun yang tercatat di situs venue/penerbit. Tanda `*` = venue hanya berasal dari kolom Comments arXiv (penulis menyatakan accepted), belum dikonfirmasi di situs venue.
  - **WORKSHOP** = diterima di workshop (umumnya tanpa proses review setara main track).
  - **PREPRINT-ONLY** = sampai 2026-10-11 tidak ditemukan bukti penerbitan di venue; ID arXiv terkonfirmasi ada.
  - **COULD-NOT-VERIFY** = judul/ID/venue tidak dapat dikonfirmasi.
- Semua ID arXiv 2026 yang dibuka (ada di tabel) **ada dan judulnya cocok**. Tidak ditemukan ID arXiv yang salah. Masalah identifikasi ada pada empat entri non-arXiv/samar (lihat "Entri yang mencurigakan").

## Tabel utama

| # | Paper | Pemakaian kita | Status | Venue | URL kanonis | Catatan |
|---|---|---|---|---|---|---|
| 1 | Gekhman et al., Inside-Out: Hidden Factual Knowledge in LLMs | F1, H1 (ancaman novelty Study 1) | PEER-REVIEWED | COLM 2025 | https://openreview.net/forum?id=f7GG1MbsSM | Terkonfirmasi di daftar accepted colmweb.org/2025 |
| 2 | Orgad et al., LLMs Know More Than They Show | presence vs expression | PEER-REVIEWED | ICLR 2025 | https://proceedings.iclr.cc/paper_files/paper/2025/hash/a712d461e57201efe35d429a6f1731c1-Abstract-Conference.html | OpenReview id KRnsX5Em3W (dari hasil pencarian) |
| 3 | Kandpal et al., LLMs Struggle to Learn Long-Tail Knowledge | metodologi exposure | PEER-REVIEWED | ICML 2023 (PMLR 202) | https://proceedings.mlr.press/v202/kandpal23a.html | |
| 4 | Chang et al., How Do LLMs Acquire Factual Knowledge During Pretraining? | injeksi fakta fiktif | PEER-REVIEWED | NeurIPS 2024 | https://proceedings.neurips.cc/paper_files/paper/2024/file/6fdf57c71bc1f1ee29014b8dc52e723f-Paper-Conference.pdf | poster: neurips.cc/virtual/2024/poster/95028 |
| 5 | Kusuma, Qorib, Ng, Parametric Knowledge is Not All You Need | substrat Pythia | PEER-REVIEWED | Findings ACL 2026 | https://aclanthology.org/2026.findings-acl.1935/ | Dibuka langsung (hal. 38858-38871) |
| 6 | Gottesman et al., LMEnt | substrat exposure | PEER-REVIEWED | TACL vol. 14, 2026 | https://aclanthology.org/2026.tacl-1.76/ | DOI 10.1162/tacl.a.746; arXiv 2509.03405 |
| 7 | Cheang et al., Do LLMs Really Know What They Don't Know? | taksonomi, kritik probe | PEER-REVIEWED | Findings ACL 2026 | https://aclanthology.org/2026.findings-acl.34/ | Ditemukan di preview.aclanthology.org (ingest-acl); **matrix #7 masih menulis arXiv**; versi arXiv terakhir v3 (bukan v2) |
| 8 | Xu et al., Knowledge Conflicts for LLMs: A Survey | taksonomi State D | PEER-REVIEWED | EMNLP 2024 | https://aclanthology.org/2024.emnlp-main.486/ | Matrix menandai [S]; kini terkonfirmasi |
| 9 | Venhoff et al., Too Late to Recall | alat restorasi (patching) | PEER-REVIEWED | NeurIPS 2025 | https://neurips.cc/virtual/2025/loc/san-diego/poster/115850 | arXiv 2512.03276; matrix hanya menulis arXiv |
| 10 | Liu et al., Infini-gram | alat audit exposure | PEER-REVIEWED | COLM 2024 (spotlight) | https://openreview.net/forum?id=POj9o27IMr | |
| 11 | Liu et al., Lost in the Middle | akses tipe (b) | PEER-REVIEWED | TACL 12, 2024 | https://aclanthology.org/2024.tacl-1.9/ | DOI 10.1162/tacl_a_00638 |
| 12 | "Wang et al., Knowledge Neurons / factual recall, EMNLP 2024" (matrix #18) | akses tipe (a) | PEER-REVIEWED (identifikasi **tidak pasti**) | EMNLP 2024 | https://aclanthology.org/2024.emnlp-main.420/ | Kandidat terdekat: Wang et al., Unveiling Factual Recall Behaviors of LLMs through Knowledge Neurons. Abstrak tidak menyatakan "recall gagal walau ada sinyal internal"; cocokkan sebelum dikutip |
| 13 | Lango & Dusek, Critic-Driven Decoding | baseline, ancaman C2-C4 | PEER-REVIEWED | EMNLP 2023 | https://aclanthology.org/2023.emnlp-main.172/ | hal. 2853-2862 |
| 14 | Shi et al., Context-Aware Decoding (Trusting Your Evidence) | baseline | PEER-REVIEWED | NAACL 2024 (short) | https://aclanthology.org/2024.naacl-short.69/ | Matrix menulis "NAACL 2024": benar, tetapi short paper |
| 15 | Chuang et al., Lookback Lens | baseline | PEER-REVIEWED | EMNLP 2024 | https://aclanthology.org/2024.emnlp-main.84/ | Matrix #26/#46 sudah V |
| 16 | See et al., Pointer-Generator | struktur hard-mix | PEER-REVIEWED | ACL 2017 | https://aclanthology.org/P17-1099/ | |
| 17 | Joren et al., Sufficient Context | baseline sufficiency | PEER-REVIEWED | ICLR 2025 | https://iclr.cc/virtual/2025/poster/30092 | arXiv 2411.06037 |
| 18 | Zhang et al., R-Tuning | baseline abstensi | PEER-REVIEWED | NAACL 2024 (long) | https://aclanthology.org/2024.naacl-long.394/ | |
| 19 | Spataru et al., Know When To Stop | ancaman stopping rule | PEER-REVIEWED | NAACL 2024 (long) | https://aclanthology.org/2024.naacl-long.202/ | Dibuka langsung |
| 20 | Mohri & Hashimoto, Conformal Factuality Guarantees | baseline, teori | PEER-REVIEWED | ICML 2024 (PMLR 235) | https://proceedings.mlr.press/v235/mohri24a.html | |
| 21 | Zhao et al., How Does Response Length Affect Long-Form Factuality | motivasi g -> 0 | PEER-REVIEWED | Findings ACL 2025 | https://aclanthology.org/2025.findings-acl.161/ | |
| 22 | Wei et al., Long-form factuality (SAFE, LongFact, F1@K) | metrik | PEER-REVIEWED | NeurIPS 2024 | https://proceedings.neurips.cc/paper_files/paper/2024/hash/937ae0e83eb08d2cb8627fe1def8c751-Abstract-Conference.html | |
| 23 | Min et al., FActScore | metrik | PEER-REVIEWED | EMNLP 2023 | https://aclanthology.org/2023.emnlp-main.741/ | |
| 24 | Quach et al., Conformal Language Modeling | terminologi "stopping rule" | PEER-REVIEWED | ICLR 2024 | https://openreview.net/forum?id=pzUhfQ74c5 | |
| 25 | Kalai & Vempala, Calibrated LMs Must Hallucinate | batas teoretis | PEER-REVIEWED | STOC 2024 | https://dl.acm.org/doi/10.1145/3618260.3649777 | |
| 26 | Geifman & El-Yaniv, Selective Classification for DNNs | risk-coverage, AURC | PEER-REVIEWED | NeurIPS 2017 | https://papers.nips.cc/paper/7073-selective-classification-for-deep-neural-networks | Doc 09 menulis venue "dari pengetahuan"; kini terkonfirmasi |
| 27 | Farquhar et al., Semantic entropy | baseline | PEER-REVIEWED | Nature 630, 2024 | https://www.nature.com/articles/s41586-024-07421-0 | DOI dari daftar pustaka pihak ketiga; PMC11186750 yang dibaca sebelumnya adalah versi yang sama |
| 28 | Kirichenko et al., AbstentionBench | benchmark | PEER-REVIEWED | NeurIPS 2025 (poster) | https://neurips.cc/virtual/2025/loc/san-diego/day/12/5 | Halaman program menampilkan poster; arXiv 2506.09038 |
| 29 | Karbasi et al., (Im)possibility of Automated Hallucination Detection | teori negatif | PEER-REVIEWED | COLM 2025 | https://openreview.net/forum?id=e5jWdZIX0Q | Doc 09 menandai arXiv saja; terkonfirmasi di daftar colmweb.org/2025 |
| 30 | Rubin-Toles et al., Conformal LM Reasoning with Coherent Factuality | baseline konformal | PEER-REVIEWED | ICLR 2025 | https://openreview.net/forum?id=AJpUZd8Clb | |
| 31 | Feng et al., Response Quality Assessment for RAG via Conditional Conformal Factuality (2506.20978) | konformal RAG | PEER-REVIEWED | SIGIR 2025 (short) | https://doi.org/10.1145/3726302.3730244 | Doc 07 menandai [S] tanpa venue; DOI dari halaman arXiv |
| 32 | Alayrac et al., Flamingo | C1 gated cross-attn | PEER-REVIEWED | NeurIPS 2022 | https://proceedings.neurips.cc/paper_files/paper/2022/hash/960a172bc7fbf0177ccccbb411a7d800-Abstract-Conference.html | |
| 33 | Borgeaud et al., RETRO | C1 | PEER-REVIEWED | ICML 2022 (PMLR 162) | https://proceedings.mlr.press/v162/borgeaud22a.html | |
| 34 | Qiu et al., Gated Attention for LLMs | disambiguasi nama | PEER-REVIEWED | NeurIPS 2025 (oral) | https://proceedings.neurips.cc/paper_files/paper/2025/hash/904e89bb4e632e75fb47f093b620b257-Abstract-Conference.html | |
| 35 | Zhu et al., Token-Guard | gate per token | PEER-REVIEWED | ICLR 2026 (main) | https://arxiv.org/abs/2601.21969 | Venue dari kolom Comments/Journal-ref arXiv; cari URL proceedings.iclr.cc |
| 36 | Chang et al., Monitoring Decoding | C2/C3 | PEER-REVIEWED | Findings ACL 2025 | https://aclanthology.org/2025.findings-acl.752/ | Matrix/doc 04 menandai [S]; kini terkonfirmasi |
| 37 | Asai et al., Self-RAG | baseline | PEER-REVIEWED | ICLR 2024 (oral) | https://iclr.cc/virtual/2024/poster/18095 | |
| 38 | Chuang et al., DoLa | decoding kontras | PEER-REVIEWED | ICLR 2024 | https://proceedings.iclr.cc/paper_files/paper/2024/hash/edc36117f795ca52a0cbf6a7b3882859-Abstract-Conference.html | |
| 39 | Khandelwal et al., kNN-LM | mixture | PEER-REVIEWED | ICLR 2020 | https://openreview.net/forum?id=HklBjCEKvH | ID dari daftar pustaka pihak ketiga |
| 40 | Liu et al., Deep Gamblers | kelas abstain | PEER-REVIEWED | NeurIPS 2019 | https://papers.nips.cc/paper_files/paper/2019/file/0c4b1eeb45c90b52bfb9d07943d855ab-MetaReview.html | Halaman proceedings utama tidak muncul; URL ini halaman meta-review resmi |
| 41 | Li et al., KAFT / Controllable Working Memory | C5 substitusi | PEER-REVIEWED | Findings ACL 2023 | https://aclanthology.org/2023.findings-acl.112/ | |
| 42 | Gao et al., ALCE | dataset uji | PEER-REVIEWED | EMNLP 2023 | https://aclanthology.org/2023.emnlp-main.398/ | |
| 43 | Stelmakh et al., ASQA | dataset uji | PEER-REVIEWED | EMNLP 2022 | https://aclanthology.org/2022.emnlp-main.566/ | |
| 44 | Song et al., VeriScore | metrik klaim | PEER-REVIEWED | Findings EMNLP 2024 | https://aclanthology.org/2024.findings-emnlp.552/ | |
| 45 | Tu et al., Modeling Coverage for NMT | g berbasis coverage | PEER-REVIEWED | ACL 2016 | https://aclanthology.org/P16-1008/ | |
| 46 | Lee et al., Selective Generation for Controllable LMs | baseline selective | PEER-REVIEWED | NeurIPS 2024 (spotlight) | https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a6815122f533193a022cbc41786c1cc-Abstract-Conference.html | |
| 47 | Pradeep et al., The Great Nugget Recall (2504.15068) | evaluasi g | PEER-REVIEWED* | SIGIR 2025 | https://arxiv.org/abs/2504.15068 | Venue dari Comments arXiv |
| 48 | Guo et al., CodeFast / When to Stop? (2407.20042) | head stop | PEER-REVIEWED* | ISSTA 2024 | https://arxiv.org/abs/2407.20042 | Venue dari Comments arXiv |
| 49 | Zamani & Bendersky, Stochastic RAG (2405.02816) | utilitas RAG | PEER-REVIEWED* | SIGIR 2024 | https://arxiv.org/abs/2405.02816 | Venue dari Comments arXiv |
| 50 | Huang et al., Optimal Bayesian Stopping (2602.05395) | optimal stopping | PEER-REVIEWED* | ICML 2026 | https://arxiv.org/abs/2602.05395 | Camera-ready per Comments |
| 51 | Deng et al., Multi-Round Evidence Ablation (2609.08943) | peringatan label ablasi (D4) | PEER-REVIEWED* | CIKM 2026 | https://doi.org/10.1145/3799682.3841076 | Doc 04 menulis "penulis belum dicek": Deng, Cao, Aletras, Wang, Stevenson |
| 52 | Xie et al., Over-Searching in Search-Augmented LLMs (2601.05503) | kandidat prior art | PEER-REVIEWED* | EACL 2026 main | https://arxiv.org/abs/2601.05503 | Doc 09 menulis nama "OverSearchQA"; judul sebenarnya di atas |
| 53 | Itai et al., LIT-RAGBench (2603.06198) | kandidat prior art | PEER-REVIEWED* | LREC 2026 | https://arxiv.org/abs/2603.06198 | |
| 54 | Roh & Han, HALT: Verification-Aware Stopping (2608.02009) | stopping retrieval | PEER-REVIEWED* | Findings EMNLP 2026 | https://arxiv.org/abs/2608.02009 | |
| 55 | Samuel et al., Beyond Relevance (2603.08819) | coverage | PEER-REVIEWED* | ICTIR 2026 | https://arxiv.org/abs/2603.08819 | |
| 56 | Li et al., Learning Evidence Highlighting for Frozen LLMs / HiLight (2604.22565) | pelengkap C1 | PEER-REVIEWED* | NeurIPS 2026 (per Comments) | https://arxiv.org/abs/2604.22565 | Belum ada proceedings per hari ini |
| 57 | Khodabandehlou & Krishnamachari, Compression-Aware Abstention (2608.29934) | **ancaman C5**, baseline | WORKSHOP | GroundLM @ EMNLP 2026 | https://arxiv.org/abs/2608.29934 | Per Comments arXiv; bukan main track |
| 58 | Park et al., Stop-RAG (2510.14337) | optimal stopping | WORKSHOP | NeurIPS 2025 Workshop on Multi-Turn Interactions in LLMs | https://neurips.cc/virtual/2025/127996 | |
| 59 | Kieback et al., TASR (2606.13814) | stopping retrieval | WORKSHOP | Agent4IR @ KDD 2026 | https://arxiv.org/abs/2606.13814 | |
| 60 | Kawada & Kellis, Evidence Integration in LLMs (2609.04290) | **H2, F2, Study 3** | PREPRINT-ONLY | arXiv 3 Sep 2026 | https://arxiv.org/abs/2609.04290 | 114 halaman; tanpa venue |
| 61 | Nik Khah, Detectable Only Where It Is Confounded (2609.10830) | validitas label Known | PREPRINT-ONLY | arXiv (v2 29 Sep 2026) | https://arxiv.org/abs/2609.10830 | Penulis: Arman Nik Khah |
| 62 | Ying et al., From Storage to Access (VAKE) (2608.18581) | terminologi storage vs access | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2608.18581 | |
| 63 | Carletti et al., When Text and Numbers Disagree (2608.20116) | State D | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2608.20116 | |
| 64 | Yu et al., TokenMem (2607.22625) | **ancaman C1+C5** | PREPRINT-ONLY | arXiv 17 Jun 2026 | https://arxiv.org/abs/2607.22625 | Matrix menulis (Jun 2026): cocok |
| 65 | Luo et al., YOPO (2608.14465) | baseline sufficiency direction | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2608.14465 | |
| 66 | Du, Pair-ID (2608.08944) | desain intervensi | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2608.08944 | |
| 67 | Luo et al., CASS / Calibration-Aware Generation (2605.01749) | **ancaman aturan ambang** | PREPRINT-ONLY | arXiv 3 May 2026 | https://arxiv.org/abs/2605.01749 | Penulis utama Wen Luo |
| 68 | Akter et al., Sequential-EDFL (2510.06478) | **ancaman stop di decoding** | PREPRINT-ONLY | arXiv (v2 Jan 2026) | https://arxiv.org/abs/2510.06478 | Setahun lebih, belum diterbitkan |
| 69 | Qiu et al., SURE-RAG (2605.03534) | **ancaman parsial** | PREPRINT-ONLY | arXiv (v1 5 Mei, v2 24 Jul 2026) | https://arxiv.org/abs/2605.03534 | "Submitted to IEEE PRAI 2026" = belum accepted. Matrix #45 menulis "Jul 2026" (itu v2) |
| 70 | Liu & Wang, CURE (2604.12046) | abstain per klaim | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2604.12046 | |
| 71 | Kan, Claim-Selective Certification (2605.21949) | abstain per klaim | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2605.21949 | |
| 72 | Itkin, Quickest Detection of Hallucination Onset (2606.12476) | monitor streaming | PREPRINT-ONLY | arXiv (v3) | https://arxiv.org/abs/2606.12476 | |
| 73 | Obeso et al., Real-Time Detection of Hallucinated Entities (2509.03531) | probe streaming | PREPRINT-ONLY | arXiv; submisi ICLR 2026, hasil keputusan tidak terkonfirmasi | https://arxiv.org/abs/2509.03531 | Jangan menulis "ICLR 2026" |
| 74 | Li et al., SHIFT (2606.27786) | gate kecil | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2606.27786 | |
| 75 | Wang, Abstention and Noise Filtering (2609.22005) | motivasi abstain attention | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2609.22005 | |
| 76 | Gupta & Choudhary, Fact Grounded Attention (2509.25252) | disebut sbg prior art | PREPRINT-ONLY | arXiv (v3) | https://arxiv.org/abs/2509.25252 | Klaim "eliminating hallucination" di judul: hati-hati |
| 77 | Xu et al., Geometry-Calibrated Conformal Abstention (2604.27914) | teori abstain | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2604.27914 | |
| 78 | Wu et al., BAS (2604.03216) | teori keputusan | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2604.03216 | |
| 79 | Chen, Hua, Xiao, RINSE (2609.37469) | **ancaman framing**, baseline | PREPRINT-ONLY | arXiv 27 Sep 2026 | https://arxiv.org/abs/2609.37469 | ID dan judul terkonfirmasi (doc 09 baris 74 bilang pencarian tidak menemukan; koreksi) |
| 80 | Kalai, Nachum, Vempala, Zhang, Why Language Models Hallucinate (2509.04664) | **teori ambang / skor ber-penalti** | PREPRINT-ONLY | arXiv Sep 2025 | https://arxiv.org/abs/2509.04664 | Pencarian tidak menemukan venue |
| 81 | Xu, Jain, Kankanhalli, Hallucination is Inevitable (2401.11817) | batas teoretis | PREPRINT-ONLY | arXiv v2 Feb 2025 | https://arxiv.org/abs/2401.11817 | Tidak ditemukan venue |
| 82 | Kossen et al., Semantic Entropy Probes (2406.15927) | baseline probe | PREPRINT-ONLY | arXiv; sempat disubmit ICLR 2025 (OpenReview YQvvJjLWX0) | https://arxiv.org/abs/2406.15927 | Tidak ada bukti penerbitan |
| 83 | Yan et al., CRAG (2401.15884) | baseline | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2401.15884 | Tidak ditemukan venue meski sering dikutip |
| 84 | Karpowicz, Fundamental Impossibility of Hallucination Control (2506.06382) | teori (belum dibaca) | PREPRINT-ONLY | arXiv (v8) | https://arxiv.org/abs/2506.06382 | |
| 85 | Dong et al., Stateful Evidence-Driven RAG (2604.14170) | evidence gap | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2604.14170 | |
| 86 | Rubashevskii et al., Adaptive Conformal Prediction (2604.13991) | konformal | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2604.13991 | |
| 87 | Ju et al., Faithfulness-QA (2604.25313) | C5 substitusi | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2604.25313 | |
| 88 | Fu, SI-FACT (2509.10208) | kontrastif | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2509.10208 | |
| 89 | Anand et al., ContextFocus (2601.04131) | steering faithfulness | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2601.04131 | |
| 90 | Zong et al., I-CALM (2604.03904) | payoff abstain | PREPRINT-ONLY | arXiv (v2 Aug 2026) | https://arxiv.org/abs/2604.03904 | |
| 91 | Xie et al., Predicting LLM Output Length via Entropy-Guided Representations (2602.11812) | prediksi sisa panjang | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2602.11812 | Doc 07 D2 menulis judul "Length prediction from hidden states (ICLR 2026)": judul tidak cocok dan **tidak ada venue ICLR di halaman arXiv** |
| 92 | Wang et al., ESTAR (2602.10004) | early stop reasoning | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2602.10004 | |
| 93 | Nagle et al., TERMINATOR (2603.12529) | early stop CoT | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2603.12529 | |
| 94 | Kalayci et al., Optimal Stopping vs Best-of-N (2510.01394) | stopping | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2510.01394 | |
| 95 | Sato et al., Learning Evidence Sufficiency Boundaries (2609.01687) | kandidat prior art | PREPRINT-ONLY | arXiv 1 Sep 2026 | https://arxiv.org/abs/2609.01687 | Belum dibaca |
| 96 | Zhao et al., GRACE (2601.04525) | RL abstain | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2601.04525 | |
| 97 | Jafari et al., Beyond Precision: Importance-Aware Recall (2604.03141) | bobot g | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2604.03141 | |
| 98 | Upadhyay et al., Overview of TREC 2025 RAG Track (2603.09891) | nugget | PREPRINT-ONLY | arXiv (laporan track) | https://arxiv.org/abs/2603.09891 | |
| 99 | Biau & Boyer, A Note on k-NN Gating in RAG (2601.13744) | tidak relevan | PREPRINT-ONLY | arXiv | https://arxiv.org/abs/2601.13744 | |
| 100 | Saavedra, Neural Arbitration Framework v5.1 | prior art konseptual terdekat | COULD-NOT-VERIFY | Working paper di situs pribadi, berlabel "SSRN Preprint" | https://victorsaavedra.com/naf.html | Tidak ada URL/ID SSRN; pencarian tidak menemukan entri SSRN; tidak ada bukti peer review |
| 101 | Teaching LLMs to Maintain Contextual Faithfulness (CANOE) (2505.16483) | C5 | COULD-NOT-VERIFY | Doc 04 menulis "ACL 2025"; tidak terkonfirmasi | https://arxiv.org/abs/2505.16483 | Pencarian ke aclanthology.org tidak menemukannya |
| 102 | Gekhman et al., Thinking to Recall (2603.09906) | restorasi tanpa info baru | COULD-NOT-VERIFY | Blog Google menyebut COLM 2026; belum terkonfirmasi di colmweb | https://arxiv.org/abs/2603.09906 | Matrix #15 hanya mengutip blog; ganti dengan ID arXiv ini |
| 103 | Amouyal et al., QAMPARI (2205.12665) | dataset uji | COULD-NOT-VERIFY | venue tidak ditemukan; hanya arXiv | https://arxiv.org/abs/2205.12665 | Cek manual di ACL Anthology |
| 104 | Controlling Risk of RAG: A Counterfactual Prompting Framework (2409.16146) | selective RAG | COULD-NOT-VERIFY | Doc 07 menulis Findings EMNLP 2024; tidak dicek | https://arxiv.org/abs/2409.16146 | Hanya muncul di hasil pencarian |
| 105 | "When silence is safer ... LLM abstention in healthcare" | framing keputusan | COULD-NOT-VERIFY | Nature Digital Medicine 2026 (tidak dibuka) | https://www.nature.com/articles/s41746-026-02882-1 | Hanya [S] |
| 106 | FLARE, CoVe, LLM2, HaluSearch, "RAG" (matrix #19) | baseline arsitektur | COULD-NOT-VERIFY | tidak ada judul/ID lengkap | - | Entri generik; tambahkan sitasi lengkap (RAG: Lewis et al., NeurIPS 2020 dan FLARE/CoVe perlu dicek) sebelum dikutip |
| 107 | U-RAG (marginal gain per dokumen) (doc 07 E4) | bahasa utilitas | COULD-NOT-VERIFY | tidak ada judul/ID | - | |

## Hitungan

- PEER-REVIEWED: 56 (46 terkonfirmasi di situs venue/penerbit; 10 bertanda `*` hanya dari Comments arXiv)
- WORKSHOP: 3
- PREPRINT-ONLY: 40
- COULD-NOT-VERIFY: 8
- Total unik: 107 baris (beberapa baris matrix berisi kelompok; kelompok diurai di sini). Rasio arXiv-only/preprint (PREPRINT-ONLY + WORKSHOP + COULD-NOT-VERIFY) = 51 dari 107.

## Entri yang mencurigakan (kemungkinan salah ID/atribusi)

1. Matrix #18 "Wang et al., Knowledge Neurons / factual recall (EMNLP 2024)": deskripsi samar. Satu kandidat (aclanthology 2024.emnlp-main.420) tidak memuat klaim yang ditulis. Perlu dicocokkan atau dihapus.
2. Doc 07 D2 "Length prediction from hidden states (ICLR 2026, 2602.11812)": judul arXiv sebenarnya Predicting LLM Output Length via Entropy-Guided Representations; venue ICLR 2026 tidak terkonfirmasi.
3. Matrix #3 / Saavedra NAF "SSRN WP v5.1": halaman memang ada (situs pribadi) tetapi tanpa ID SSRN. Jangan sitasi sebagai "SSRN" tanpa ID.
4. Doc 04 D2 "CANOE (ACL 2025)": venue tidak terkonfirmasi; judul penuh berbeda dari nama singkat.
5. Doc 09 baris 74: menyebut RINSE dan Compression-Aware "tidak ditemukan" lewat pencarian; ID arXiv (2609.37469, 2608.29934) sebenarnya benar dan halaman abs dibuka sesi ini. Catatan itu perlu dikoreksi.
6. Koreksi kecil (bukan salah ID): matrix #7 Cheang kini Findings ACL 2026 (v3 arXiv, bukan v2); matrix #45 SURE-RAG v1 Mei 2026 (Jul adalah v2); doc 09 nama "OverSearchQA" untuk 2601.05503 (judul: Over-Searching in Search-Augmented LLMs).
- Tidak ada ID arXiv yang terbukti fiktif; semua ID yang dibuka cocok dengan judul di dokumen kita.

## Klaim yang saat ini bertumpu hanya pada preprint

| Klaim kunci kita | Bertumpu pada (PREPRINT/tidak terverifikasi) | Pengganti peer-reviewed yang ada | Saran |
|---|---|---|---|
| H2: representasi verifikasi ada tetapi tidak berwenang atas generasi (F2, Study 3) | Kawada & Kellis 2609.04290 (satu-satunya bukti langsung, 114 halaman, belum direview) | Orgad ICLR 2025 (model menyandikan jawaban benar tetapi menghasilkan yang salah); Gekhman COLM 2025; Cheang Findings ACL 2026; Xu EMNLP 2024 (survei konflik) | Kutip Orgad/Gekhman untuk premis umum; Kawada & Kellis hanya sebagai "concurrent preprint", dan jangan jadikan satu-satunya dasar motivasi H2 |
| Label "Known" dari hitungan korpus berconfound | Nik Khah 2609.10830 | Kandpal ICML 2023, Chang NeurIPS 2024, LMEnt TACL 2026, Kusuma Findings ACL 2026 | Justifikasi stratifikasi frekuensi lewat Kandpal; Khah sebagai pendukung tambahan |
| Terminologi "storage vs access" sudah dipakai | Ying 2608.18581 | Gekhman COLM 2025 (hidden vs expressed knowledge) | Pakai Gekhman sebagai rujukan utama presence-vs-access |
| Celah novelty C5 (supervisi abstain dari penghapusan evidence) dan "perkalian" EAG | Compression-Aware (workshop), TokenMem, RINSE, Pair-ID, YOPO (preprint) | Joren ICLR 2025 (sufficiency -> abstain), KAFT Findings ACL 2023, CAD NAACL 2024, Lango EMNLP 2023, Self-RAG ICLR 2024, R-Tuning NAACL 2024, Flamingo/RETRO | Klaim "tidak ada yang melakukan X" hanya valid terhadap literatur yang terbit; deklarasikan "pencarian sampai 2026-10-11, termasuk preprint" dan siapkan perubahan jika preprint tersebut diterbitkan |
| Aturan ambang sigma > (lambda+mu)/(g+lambda) = ambang Kalai 2025 / CASS | Kalai et al. 2509.04664, CASS 2605.01749, BAS 2604.03216 (semua preprint) | Geifman & El-Yaniv NeurIPS 2017 (reject option, risk-coverage); Mohri ICML 2024; Lee NeurIPS 2024; Kalai & Vempala STOC 2024 (batas, bukan aturan ambang) | Tidak ada pengganti peer-reviewed untuk skor ber-penalti t/(1-t). Perlakukan sebagai teori keputusan standar (turunan sendiri), kutip Kalai 2025 sebagai preprint, dan jangan beri bobot besar |
| Stopping rule di decoding sudah ada | Sequential-EDFL 2510.06478 | Spataru NAACL 2024; Zhao Findings ACL 2025; Quach ICLR 2024 (arti berbeda) | Spataru + Zhao cukup untuk "berhenti agar faktual"; EDFL tetap preprint |
| Abstain per klaim sudah ada | CURE, Kan, Itkin, Obeso (preprint) | Mohri ICML 2024, Rubin-Toles ICLR 2025, Lee NeurIPS 2024 | Ganti rujukan utama ke peer-reviewed; preprint sebagai tambahan |
| Probe/deteksi sebagai baseline | SEP (Kossen), Obeso, CRAG | Farquhar Nature 2024, Lookback Lens EMNLP 2024, Orgad ICLR 2025 | SEP dan Obeso tetap boleh sebagai baseline yang dijalankan sendiri, tetapi status preprint dicatat |
| Batas teoretis (halusinasi tak terhindarkan) | Xu 2401.11817, Karpowicz 2506.06382 | Kalai & Vempala STOC 2024; Karbasi COLM 2025 | Gunakan Kalai & Vempala + Karbasi sebagai dasar; hapus atau beri label preprint pada Xu dan Karpowicz |
| Benchmark tugas terdekat (selective RAG sufficiency) | SURE-RAG (belum accepted), RINSE | Joren ICLR 2025; AbstentionBench NeurIPS 2025 | Joren sebagai pembanding utama |
| Konsep NAF (arbitrase epistemik) | Saavedra (working paper, tanpa SSRN ID, tanpa review) | tidak ada | Jangan dipakai sebagai landasan teori; sebut hanya sebagai "prior art konseptual non-reviewed" |
| Hasil Fase 1b sendiri (advisory vs authority) | tidak bergantung pada sitasi | - | Tidak ada tindakan sitasi |

## Rekomendasi perubahan sitasi (untuk dikerjakan pemanggil, tidak diubah di file lain)

1. Perbarui matrix #7 (Cheang: Findings ACL 2026), #14 (tambah NeurIPS 2025 untuk Venhoff), #13 dan #36 (venue terkonfirmasi), #15 (ganti blog dengan arXiv 2603.09906, status COULD-NOT-VERIFY venue), #18 (identifikasi ulang atau tandai).
2. Gunakan URL kanonis non-arXiv (kolom "URL kanonis") di bagian Sumber, arXiv hanya sebagai tautan sekunder, untuk 46 entri peer-reviewed terkonfirmasi.
3. Beri tag `[preprint]` di teks untuk 40 entri PREPRINT-ONLY dan `[workshop]` untuk 3 entri workshop, terutama Kawada & Kellis, Compression-Aware, RINSE, TokenMem, CASS, Kalai 2025.
4. Verifikasi manual 10 entri `*` (Comments arXiv saja) sebelum menulis nama venue di paper.
5. Cek ulang status publikasi semua preprint sebelum submit paper (Kawada & Kellis, TokenMem, RINSE, CASS, SURE-RAG, Obeso, Akter paling mungkin sudah terbit dalam beberapa bulan).

## Sumber yang dipakai
- arXiv abs: 2609.04290, 2609.10830, 2608.18581, 2608.20116, 2608.29934, 2609.37469, 2607.22625, 2608.14465, 2608.08944, 2605.01749, 2510.06478, 2605.03534, 2604.12046, 2605.21949, 2606.12476, 2510.09033, 2606.27786, 2609.22005, 2509.25252, 2601.21969, 2604.27914, 2604.03216, 2512.03276, 2601.21218, 2509.03405, 2604.14170, serta semua ID lain di tabel (https://arxiv.org/abs/<id>)
- https://colmweb.org/2025/AcceptedPapers.html
- https://aclanthology.org/2026.findings-acl.1935/ · https://aclanthology.org/2026.tacl-1.76/ · https://preview.aclanthology.org/ingest-acl/2026.findings-acl.34/
- https://victorsaavedra.com/naf.html
- URL kanonis lain: lihat kolom "URL kanonis".
