# Literature Matrix v0.1 — Epistemic Access Architecture (EAA)

Tanggal: 5 Oktober 2026 · Status: sprint Hari 1–5, putaran pertama (belum sistematis/PRISMA)

Legenda status verifikasi:
- **[V]** abstrak/halaman paper dibaca langsung pada sesi ini
- **[S]** hanya dari hasil pencarian — wajib dibaca penuh sebelum dikutip

---

## 1. Temuan utama putaran ini (baca ini dulu)

### F1 — "Presence ≠ Accessibility" untuk knowledge parametrik **sudah ditunjukkan**
Gekhman et al. (COLM 2025) [V] mengukur knowledge internal (hidden states) vs eksternal (token probability) dan menemukan gap relatif rata-rata **40%**, termasuk jawaban yang "diketahui sempurna" secara internal tetapi tidak pernah keluar dalam 1.000 sampel. Orgad et al. (ICLR 2025) [V] dan Kandpal et al. (ICML 2023) [V] mendukung dari sisi lain.

→ **Konsekuensi:** Paper/Study 1 di rencana awal ("Knowledge Presence vs Knowledge Accessibility") **tidak bisa lagi diklaim sebagai temuan baru** dalam bentuk umum. Novelty harus datang dari *penyempurnaan* (lihat F5).

### F2 — "Evidence terbaca tapi tidak mengontrol generation" **sudah ditunjukkan secara mekanistik**
Kawada & Kellis (arXiv, 3 Sep 2026) [V]: 10 juta trial, 12 LLM, 4 family. Model mengintegrasikan kandidat jawaban eksternal *bahkan setelah secara internal memverifikasi bahwa kandidat itu tidak valid* (93–100%). Representasi verifikasi dapat di-decode, tetapi efek kausalnya **bergantung model** (steering/patching: nol pada Llama-3.1-70B, lemah pada Qwen3-8B, signifikan pada Gemma-4-31B; koreksi 2026-10-05 setelah deep-read), dan sepenuhnya terpisah (dissociable) dari state integrasi kandidat.

→ Ini adalah dukungan empiris terkuat untuk premis H2 ("epistemic state ada tapi tidak punya *authority* atas generation" — Access tipe F di context file). Tapi ini juga **mengambil sebagian ruang Study 3 (mekanistik)**. Prioritas baca penuh #1.

### F3 — NAF terverifikasi: **konseptual saja, tanpa eksperimen**
Saavedra (SSRN, April 2026, v5.1) [V]: arsitektur dua-"hemisphere", protokol arbitrase 5 fase, inspirasi split-brain/interpreter. Tidak ada hasil, eksperimen, atau protokol validasi.

→ Diferensiasi via **operasionalisasi + intervensi kausal** tetap valid.

### F4 — Label "known" dari corpus count punya confound serius
Nik Khah (arXiv, Sep 2026) [V]: pada Pythia & OLMo-2, korelasi rank antara loss dan jumlah duplikasi hanya ≈ −0.08. Sinyal baru kuat di atas ~1.000 salinan, dan di situ **"terkenal" tidak bisa dibedakan dari "dihafal"**. Kontrol berupa edit satu kata menghasilkan sinyal palsu.

→ "Fakta ada di Pile" ≠ "model telah mempelajarinya". Kondisi B ("Known") **tidak boleh** dilabel hanya dari keanggotaan corpus. Wajib stratifikasi frekuensi.

### F5 — Masalah konseptual dalam desain pilot saat ini (paling penting)
Dokumen-dokumen yang ada memakai kata "access" untuk **dua hal yang berbeda**:

| | (a) Akses parametrik | (b) Akses kanal/konteks |
|---|---|---|
| Knowledge berada di | bobot model (dari pretraining) | konteks / paket evidence dari reader |
| "Restricted" artinya | recall gagal walau knowledge ter-encode | evidence dimask/dipindah/dikompres |
| Relevansi auditabilitas Pythia | **tinggi** | **hampir nol** — evidence sudah diberikan eksplisit |
| Prior art utama | Gekhman 2025, Orgad 2025, Wang 2024 | Lost in the Middle, Kawada & Kellis 2026 |

Pilot #1 (kondisi C/D/E: evidence penuh → dimask → dipulihkan) adalah tipe (b), sementara justifikasi pemilihan Pythia adalah tipe (a). Kalau evidence dimask lalu halusinasi naik, hasil itu nyaris trivial ("informasi berkurang → error naik"). Ini persis confound "information quantity" yang sudah Anda tulis sendiri.

**Usulan penajaman State B** — pecah menjadi dua:
- **B1 — Seen, not encoded:** ada di corpus (terverifikasi), tetapi probe internal tidak menemukannya → *kegagalan penyimpanan*, bukan akses.
- **B2 — Encoded, not expressed:** probe internal menemukannya, tetapi generation salah/halusinasi → **inilah "known-but-inaccessible" yang sebenarnya.**

Kombinasi *audit corpus* (Pythia/LMEnt) **+** *probe hidden knowledge* (gaya Gekhman) **+** *intervensi restorasi kausal* pada item B2 belum terlihat dikerjakan bersamaan pada putaran pencarian ini. Ini kandidat celah novelty yang paling bisa dipertahankan untuk Paper 1. Masih perlu dicek lebih dalam.

### F6 — Intervensi "restore access" untuk knowledge parametrik sudah punya alat yang tersedia
- Activation patching memulihkan factual recall pada VLM yang terdegradasi ("Too Late to Recall", arXiv 2512.03276) [S]
- Reasoning trace membuka knowledge parametrik yang tadinya tak terjangkau (Google Research, "Thinking to recall") [S]
- Priming dengan bridging triples: >50% memunculkan knowledge yang tidak bisa diakses lewat prompting langsung (Ying et al., VAKE, arXiv Aug 2026) [V]

→ Kondisi "restored" untuk tipe (a) bisa dioperasionalkan **tanpa menambah informasi baru** (patching dari prompt sumber lain pada model yang sama). Itu memisahkan "lebih banyak informasi" dari "akses lebih baik".

---

## 2. Matrix

| # | Work | Venue/Tahun | Ver. | Inti | Relasi ke tesis | Yang masih terbuka | Status |
|---|---|---|---|---|---|---|---|
| 1 | Gekhman et al., *Inside-Out: Hidden Factual Knowledge in LLMs* | COLM 2025 | V | Internal vs external knowledge; gap 40%; jawaban yang diketahui tapi tidak pernah di-generate | **Hampir identik dengan H1/Study 1** (parametrik) | Tanpa audit corpus; tanpa intervensi restorasi kausal; tanpa link ke halusinasi vs abstensi | **Ancaman novelty** |
| 2 | Kawada & Kellis, *Evidence Integration in LLMs* | arXiv 2609.04290 (Sep 2026) | V | Verifikasi decodable; efek kausal bergantung model (koreksi); integrasi kandidat terjadi di layer akhir | **Mendukung premis H2 / Access tipe F** | Tidak mengusulkan arsitektur; fokus evidence eksternal | **Ancaman novelty (Study 3)** + dukungan |
| 3 | Saavedra, *Neural Arbitration Framework* | SSRN WP v5.1 (Apr 2026) | V | Generatif vs epistemik, arbitrase interuptif, split-brain | Prior art konseptual terdekat | Tanpa eksperimen sama sekali | Prior art konseptual |
| 4 | Kusuma, Qorib & Ng, *Parametric Knowledge is Not All You Need* | Findings ACL 2026 | V | Benchmark honesty berbasis Pythia + retrieval dari pretraining data | Substrat eksperimen (known/unknown terkontrol) | Tidak memisahkan B1/B2; fokus honesty | Fondasi |
| 5 | Gottesman et al., *LMEnt* | TACL 2026 | V | 12 model ≤1B, 4.000 checkpoint, corpus beranotasi entitas (Wikipedia-grounded) | **Substrat alternatif yang mungkin lebih baik dari Pythia** untuk label exposure | Skala kecil (≤1B) | Fondasi (kandidat) |
| 6 | Nik Khah, *Detectable Only Where It Is Confounded* | arXiv 2609.10830 (Sep 2026) | V | Duplikasi corpus lemah sebagai bukti membership; confound fame | **Ancaman validitas** untuk label "Known" | — | Wajib dikontrol |
| 7 | Cheang et al., *Do LLMs Really Know What They Don't Know?* | arXiv 2510.09033 (v2 Apr 2026) | V | Hidden states mencerminkan *recall*, bukan kebenaran; Associated vs Unassociated hallucination | Taksonomi pelengkap; ancaman untuk probe sebagai "oracle" | — | Kritis |
| 8 | Orgad et al., *LLMs Know More Than They Show* | ICLR 2025 | V | Info truthfulness terkonsentrasi di token tertentu | Mendukung presence ≠ expression | — | Kritis |
| 9 | Kandpal et al., *LLMs Struggle to Learn Long-Tail Knowledge* | ICML 2023 | V | Akurasi QA ∝ jumlah dokumen relevan di pretraining (korelasional + kausal) | Metodologi entity-linking corpus untuk label exposure | — | Metodologi |
| 10 | Chang et al., *How Do LLMs Acquire Factual Knowledge During Pretraining?* | NeurIPS 2024 | V | Injeksi fictional knowledge ke OLMo checkpoint; dinamika lupa | **Cara terbersih membuat State A vs B terkontrol** (injeksi fakta fiktif) | — | Metodologi |
| 11 | Ying et al., *From Storage to Access (VAKE)* | arXiv 2608.18581 (Aug 2026) | V | RL untuk aktivasi knowledge parametrik; framing "storage vs access" eksplisit | Bahasa "storage vs access" sudah dipakai orang lain | Bukan intervensi kausal; tanpa audit corpus | Prior art (terminologi) |
| 12 | Carletti et al., *When Text and Numbers Disagree: Evidence Arbitration* | arXiv 2608.20116 (Aug 2026) | V | Arbitrase evidence yang konflik mengikuti heuristik (recency > reliability) | Relevan untuk State D (Conflicted) | — | Relevan |
| 13 | Xu et al., *Knowledge Conflicts for LLMs: A Survey* | EMNLP 2024 | S | Context-memory / inter-context / intra-memory conflict | Taksonomi State D | — | Bacaan wajib |
| 14 | *Too Late to Recall* | arXiv 2512.03276 | S | Activation patching memulihkan factual recall | **Alat restorasi kausal** | — | Metodologi |
| 15 | Google Research, *Thinking to recall* | blog/paper | S | Reasoning membuka knowledge parametrik | Restorasi akses tanpa info baru | — | Metodologi |
| 16 | Infini-gram (Liu et al.) | COLM 2024 | V | Query n-gram cepat atas Pile dan corpus lain | **Alat audit exposure** untuk Pythia | — | Tool |
| 17 | Liu et al., *Lost in the Middle* | TACL 2024 | (dari dokumen) | Evidence di konteks tidak selalu dipakai | Akses tipe (b) | — | Esensial |
| 18 | Wang et al., *Knowledge Neurons / factual recall* | EMNLP 2024 | (dari dokumen) | Recall gagal walau ada sinyal internal | Akses tipe (a) | — | Kritis |
| 19 | Self-RAG, CoVe, FLARE, LLM2, HaluSearch, RETRO, RAG | 2020–2025 | (dari dokumen) | Retrieval/verifier/dual-process | Baseline arsitektur | — | Baseline |
| 20 | Khodabandehlou & Krishnamachari, *Compression-Aware Abstention* | arXiv 2608.29934 (Aug 2026) | V | Label abstain dari apakah span pembawa jawaban bertahan/terhapus; LoRA 10M di atas base frozen; halusinasi −97% | **Overlap terbesar dengan pelatihan kontrafaktual EAG (C5)**; relevan untuk H3/H4 | Tanpa σ per token, tanpa hard-mix, tanpa ablasi advisory vs enforced | **Ancaman novelty (EAG)** |
| 21 | Lango & Dušek, *Critic-Driven Decoding* | EMNLP 2023 | V | Critic biner per token (data+prefix+kandidat) dikalikan dengan P_LM saat decoding | **Overlap terbesar dengan skor support + gate distribusi EAG (C2–C4)** | Critic terpisah, tanpa ABSTAIN, negatif dari perturbasi output | **Ancaman novelty (EAG)** + baseline |
| 22 | Yu et al., *TokenMem* | arXiv 2607.22625 (Jun 2026) | V | Adapter cross-attn ber-gate di LLM frozen + curriculum kontrafaktual | Overlap dengan C1 (+C5 parsial) EAG | Tanpa abstensi | Ancaman novelty (EAG) |
| 23 | Chen et al., *RINSE: Relevance Is Not Sufficient Evidence* | arXiv 2609.37469 (Sep 2026) | V | Deteksi evidence gap sebelum generasi; benchmark berpasangan deletion/substitution | Argumen "abstensi = judgment evidence, bukan knowledge boundary" mendukung EAG | Bukan modul internal, bukan per token | Dukungan + baseline |
| 24 | Luo et al., *YOPO* | arXiv 2608.14465 (Aug 2026) | V | Sufficiency direction zero-shot di residual stream LM frozen untuk abstensi | Sinyal kecukupan internal (alternatif σ) | Tanpa cross-attn, tanpa mixture | Baseline |
| 25 | Shi et al., *Context-Aware Decoding* | NAACL 2024 | V | Kontras P(y\|c,x) vs P(y\|x) saat inferensi, tanpa training | Versi inferensi dari kontras with/without evidence | Tanpa abstensi | Baseline |
| 26 | Chuang et al., *Lookback Lens* | EMNLP 2024 | S | Classifier lookback-ratio + guided decoding | Skor grounding per langkah | Tanpa abstensi/intervensi | Baseline |
| 27 | See et al., *Pointer-Generator* | ACL 2017 | S | p_gen = σ(w·[h_t; ctx; x_t]) mixture | **Matematika hard-mix EAG identik** (P_B diganti ABSTAIN) | — | Prior art struktural |
| 28 | Joren et al., *Sufficient Context* | ICLR 2025 | S | Autorater kecukupan + selective generation | Konsep kecukupan → abstensi | Tingkat respons, eksternal | Baseline |
| 29 | Du, *Pair-ID: Paired Evidence Interventions* | arXiv 2608.08944 (Aug 2026) | V | Audit offline tambah support/hapus nonsupport pada query sama | Desain intervensi kanal sebagai audit (H1/H2) | Tanpa training | Metodologi |
| 30 | Zhang et al., *R-Tuning* | NAACL 2024 | V | Data refusal-aware dari batas knowledge parametrik | Abstensi dipelajari (tipe a) | Bukan evidence-conditioned | Baseline |

*Detail lengkap dan novelty verdict EAG: lihat `04_prior_art_EAG_v0.1.md`.*

---

## 3. Dampak terhadap rencana

1. **Tulis ulang klaim novelty Paper 1.** Dari "presence ≠ accessibility" (sudah ada) menjadi: *pemisahan B1 (seen-not-encoded) vs B2 (encoded-not-expressed) dengan exposure teraudit, dan uji kausal apakah memulihkan akses pada B2 menurunkan halusinasi tanpa menambah informasi.*
2. **Pisahkan dua program eksperimen** — (a) parametrik [Pythia/LMEnt] dan (b) kanal reader→generator [arsitektur EAA]. Jangan gabungkan dalam satu pilot.
3. **Uji H3 (state distinction) jadi primary outcome pilot**: apakah item B2 berhalusinasi dengan cara berbeda dari item A (unseen), misalnya lebih yakin dan lebih sedikit abstensi? Prediksi ini bisa gagal (falsifiable) dan tidak trivial.
4. **Kontak penting baru:** Zorik Gekhman / Roi Reichart (hidden knowledge), Sebastien Kawada / Manolis Kellis (evidence integration), Mor Geva (LMEnt).

## 4. Daftar baca penuh (urutan prioritas)
1. Kawada & Kellis 2026 — arXiv 2609.04290
2. Gekhman et al. 2025 — arXiv 2503.15299
3. Kusuma, Qorib & Ng 2026 — arXiv 2601.21218
4. LMEnt — arXiv 2509.03405
5. Nik Khah 2026 — arXiv 2609.10830
6. Cheang et al. — arXiv 2510.09033
7. Chang et al. 2024 — arXiv 2406.11813

## 5. Sumber
- https://arxiv.org/abs/2503.15299
- https://arxiv.org/abs/2410.02707
- https://arxiv.org/abs/2609.04290
- https://victorsaavedra.com/naf.html
- https://aclanthology.org/2026.findings-acl.1935/ · https://arxiv.org/abs/2601.21218
- https://arxiv.org/abs/2509.03405
- https://arxiv.org/abs/2609.10830
- https://arxiv.org/abs/2510.09033
- https://arxiv.org/abs/2211.08411
- https://arxiv.org/abs/2406.11813
- https://arxiv.org/abs/2608.18581
- https://arxiv.org/abs/2608.20116
- https://aclanthology.org/2024.emnlp-main.486/
- https://arxiv.org/html/2512.03276v1
- https://research.google/blog/thinking-to-recall-how-reasoning-unlocks-parametric-knowledge-in-llms/
- https://infini-gram.readthedocs.io/en/latest/api.html
