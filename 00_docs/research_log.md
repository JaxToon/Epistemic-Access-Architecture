# Research Log

## 2026-10-05

- Membaca 3 dokumen awal; literature matrix v0.1 (`01_literature_matrix_v0.1.md`).
- Arah dikonfirmasi user: fokus **kanal reader↔generator + arbitrase**, bukan pivot ke akses parametrik.
- Desain pilot v0.1 ditulis (`02_hypothesis_and_pilot_design_v0.1.md`).
- **Perubahan dari desain v0.1 saat implementasi:**
  - Kondisi C7/C8 (advisory/enforced) dijalankan pada **semua** bandwidth, bukan hanya BW-50/25. Hasilnya desain faktorial bandwidth × arbitrase, dan kurva lengkapnya bisa dibandingkan.
  - `enforced` diturunkan dari keluaran `advisory` + gate verdict reader, tanpa pemanggilan generator terpisah. Prompt-nya identik, jadi hasilnya setara dan menghemat komputasi.
  - Ditambah `enforced_oracle` (off + gate oracle) sebagai batas atas arbitrase.
  - `restored` dijalankan sebagai **dua giliran** (jawab di BW-25, lalu evidence penuh), bukan single-turn yang identik dengan BW-100. Ini menguji apakah jawaban awal yang salah "melekat" (anchoring).
- Data: HotpotQA distractor validation (7.405 item) → sampel 500, seed 20261005, manifest + sha256 di `01_data/`.
- Kode pipeline `eaa/` + 7 unit test (invariant kondisi) lolos. Smoke test mock 20 item end-to-end OK; panjang prompt antar bandwidth setara (±1%).
- Agent riset dibuat di `.claude/agents/`: literature-scout, methodology-critic, experiment-runner, stats-analyst.
- Lingkungan: RTX 5050 Laptop 8 GB, torch 2.12 cu128, transformers 5.12; model Qwen2.5-3B-Instruct (fp16).

### v0.2 — perbaikan setelah review methodology-critic (sebelum run GPU apa pun)
Temuan review dan perbaikannya:
1. **Pembulatan bandwidth meruntuhkan level** (66% item punya 2 supporting facts) → kanal dimanipulasi per **paragraf emas**. Setiap item punya tepat 2 paragraf emas (terverifikasi 500/500). Level: `full`, `drop_ans`, `drop_other`, `drop_all`.
2. **Jawaban bocor lewat judul paragraf / unit tersisa** (57% paket BW-25 masih memuat jawaban) → oracle = `answer_available`, dihitung dari paket yang benar-benar dirender. Smoke check: hanya 3% paket `drop_ans` yang masih memuat jawaban.
3. **H3 advisory→enforced tautologis** → H3b diganti menjadi *selective risk* (halusinasi/terjawab). Selisih 0 berarti gate tidak lebih baik dari gate acak dengan laju abstain yang sama.
4. **Restored ter-confound oleh format dua giliran** → ditambah `restored_ctrl` (full→full, follow-up identik). Ekuivalensi diuji dengan TOST, margin 0.05 dikunci di config. Hasil dilaporkan per status giliran-1.
5. **Label abstain/correct** → abstain = prefix token; `non_answer` dijadikan kelas terpisah; correct = EM atau gold ⊂ pred (bukan F1 ≥ 0.5); `unsupported_correct` diimplementasikan.
6. **Tebakan struktural** → `qclass` (open / yesno / answer_in_question). Populasi primer = open dengan jawaban di tepat satu paragraf emas. Item yes/no tidak dihitung `param_known`.
7. **Statistik** → semua kontras dihitung per level (satu baris per item per sisi), sehingga McNemar valid; Holm hanya untuk famili primer. *Deviasi:* GLMM dari desain B6 belum diimplementasikan (statsmodels tidak terpasang); diganti bootstrap per item + McNemar per level.
8. **Kebocoran via reader** → advisory primer berisi verdict saja; `advisory_missing` menjadi kontrol sekunder dengan cek kebocoran berbasis overlap/F1.
9. **Kontrol panjang dan batching** → `len_ratio_vs_full` dicatat per paket; flag `--batch-size 1` disediakan untuk cek noise batching pada subsampel (belum dijalankan).

### Smoke test GPU (5 item, Qwen2.5-3B fp16) → v0.2.1
- Model dipindah ke `03_models/Qwen2.5-3B-Instruct`, karena cache HF gagal membuat symlink di Windows (WinError 1314).
- Reader 3B hampir selalu mengeluarkan verdict teks `INSUFFICIENT`, termasuk pada `full`. Gate teks (`enforced`) jadi hampir selalu abstain. **Ditambahkan** `reader_score`: P(SUFFICIENT) dari log-prob kontinuasi `{"verdict": "` → `enforced_score` (τ = 0.5, pre-registered) + AURC (gate skor vs acak vs oracle). Di smoke test, skor memisahkan `full` (0.14–0.84) dari `drop_*` (≈0). Skor ini juga menjadi baseline langsung untuk EAG.
- Pada kondisi advisory, generator meniru kata verdict ("INSUFFICIENT") → dihitung non_answer. Regex non_answer diperluas ("cannot be definitively determined").
- Observasi: pada item Ptolemaic, model salah di `off/full`, tetapi benar di `restored` *dan* `restored_ctrl` (efek follow-up "answer again"). Ini konfirmasi bahwa kontrol `restored_ctrl` diperlukan.
- Run penuh dimulai: `05_outputs/pilot_v0.2_qwen2.5-3b/` (500 item).

### Prior art EAG (literature-scout) → `04_prior_art_EAG_v0.1.md`
- Semua komponen EAG sudah ada secara terpisah: gated cross-attn adapter (Flamingo/RETRO/TokenMem), mixture σ·P_gen (pointer-generator, kNN-LM), skor support per token yang mengontrol decoding (Critic-Driven Decoding, Lookback Lens, Token-Guard), abstensi terlatih (R-Tuning), dan pelatihan kontrafaktual evidence-dihapus→abstain (Compression-Aware Abstention, Aug 2026).
- Kombinasi lengkapnya belum ditemukan. Pembingkaian yang disarankan: EAG sebagai **alat kausal untuk H3** (σ advisory vs σ authoritative pada modul yang sama), bukan mekanisme gate baru.
- Wajib baca penuh: arXiv 2608.29934, 2310.16964, 2607.22625, 2609.37469.

### Run pilot_v0.2 dijeda (atas permintaan user)
- Dihentikan setelah ±3 jam pada fase A; generations.jsonl valid. Lanjutkan dengan `python -m eaa.run --config configs/pilot_v0.1.yaml` (key yang sudah ada otomatis dilewati).
- Catatan: susunan batch setelah resume berbeda dari run tak terputus, sehingga output fp16 greedy bisa bergeser sangat kecil. Dampaknya dicek nanti dengan subsampel `--batch-size 1`.
- Kecepatan aktual ~3,6 s/batch-8 di RTX 5050 Laptop. Sisa: ~400 generasi fase A, 1.972 reader_score, ~2.958 fase B.

### Resume + perbaikan performa reader_score (2026-10-05 ±20:15)
- User AFK; instruksi: lanjutkan secara mandiri, catat semua keputusan.
- Run dilanjutkan; fase A selesai. `reader_score` ternyata sangat lambat (~14 s/batch, estimasi 7,4 jam), karena log-softmax full-vocab dihitung di semua posisi prompt (~2 GB, VRAM tumpah). **Perbaikan:** `lm_head` hanya dipanggil pada posisi kontinuasi. Verifikasi pada 8 prompt smoke: selisih maks 0,094 log-prob (noise fp16/batching), kecepatan ~0,8 s/prompt.
- 44 skor yang dihitung dengan kode lama **dibuang**, supaya semua skor berasal dari kode yang sama (backup: `generations.backup_before_score_fix.jsonl`).
- Koreksi literatur: Kawada & Kellis 2026 → efek kausal verifikasi *bergantung model*, bukan "tidak efektif" secara umum (diperbaiki di 01 dan 03).
- Deep-read prior art (04 §5): kontribusi "sinyal σ yang sama, advisory vs authoritative" **bertahan**; "supervisi evidence-dihapus→abstain dengan kontrol panjang" **bukan baru** (CAA 2608.29934, wajib jadi baseline).
- EAG fase 1 dibangun (`eaa/eag/`): build_train (HotpotQA train, 6.000+1.000 item → 27.724 paket), features (backbone beku, h@t0 dari 3 layer, M = unit evidence di-pool, qv), model (probe / qe / eag + learned global query q0), train (BCE + kontrastif full vs drop_ans), evaluate (AURC berpasangan vs gate reader_score pada output `off` pilot yang identik). 11 unit test lolos; uji end-to-end di CPU dengan 0.5B OK.
- Keputusan desain: label train `full` = 1 (dua paragraf emas cukup secara konstruksi), bukan dari pencocokan string. q0 ditambahkan setelah unit test sintetis menunjukkan EAG lambat belajar ketika query hanya dari h.
- Keputusan desain: backbone EAG = Qwen2.5-3B (sama dengan generator pilot), sehingga gate dibandingkan pada output generator yang identik.

### Review methodology-critic atas EAG fase 1 → perbaikan v0.2 (sebelum hasil uji apa pun)
- Rantai otomatis sempat **dihentikan sebelum ekstraksi fitur**, karena review mengubah apa yang harus diekstrak (qv).
- Perbaikan (rincian di `05_preregistration_EAG_phase1.md` §5):
  - target = kecukupan (full);
  - `drop_other` ditahan sebagai intervensi uji yang tidak pernah dilatih;
  - qv dari forward khusus pertanyaan;
  - BCE hanya baris batch (partner hanya untuk hinge);
  - AURC tie-aware pada populasi answered;
  - H5a–c dalam satu bootstrap + Holm;
  - H6 pada intervensi yang tidak dilatih + margin non-inferioritas 0,005;
  - baseline `cue_only` + oracle;
  - checkpoint dibaca dari `train_summary.json`;
  - assert span kosong/NaN;
  - p-value di-clip ≤ 1.
- Fase 1b ditulis ulang: kontras primer = selective risk pada **cakupan yang disamakan** (τ* menyamakan laju menjawab) + **plasebo** σ diacak.
- Semua 13 unit test lolos. Uji end-to-end rantai EAG di CPU (0.5B, 32 item train, 5 item smoke) berhasil.
- Rantai otomatis dipasang ulang: evaluasi + analisis pilot → fitur train (27.724 paket) → fitur test (1.972) → train 4 konfigurasi × 3 seed → evaluasi EAG.

### Pilot v0.2 selesai (21:18) — audit label menemukan 2 bug; hasil SEMENTARA
**Bug pelabelan** (mempengaruhi semua angka di `07_analysis/pilot_v0.2_qwen2.5-3b/summary.md`; angka di file itu JANGAN dipakai):
1. `I DON'T KNOW.` dihitung substantif: normalize menghapus apostrof → "i dont know", tidak cocok dengan prefix "i don t know". Closed-book "halusinasi 98%" sepenuhnya artefak. **Diperbaiki.**
2. Correct = EM atau gold ⊂ pred terlalu ketat: ±1/3 "halusinasi" @full adalah jawaban benar dalam bentuk lain ("Al Capone"/"Alphonse Gabriel Capone", "42"/"42 members"). **Diperbaiki** dengan correctness bertingkat (`eaa/judge.py`): aturan untuk kasus jelas; 181 kasus ambigu unik dinilai judge Qwen2.5-7B-Instruct 4-bit (log P(YES) vs P(NO), deterministik). Audit oleh Claude atas ke-181 kasus (127 benar / 54 salah) disimpan di `06_evaluation/audit_ambiguous_claude.jsonl` untuk menghitung agreement judge. Label lama tetap ada sebagai `correct_strict`.
3. Output "SUFFICIENT EVIDENCE" (41×) dan "[eN]" (8×) sekarang dihitung non_answer (tidak ada klaim faktual).

**Hasil sementara** (label audit Claude sebagai pengganti judge; populasi primer, 311 item; `off`):

| level | benar | halusinasi | abstain | selective risk |
|---|---|---|---|---|
| full | 0.534 | 0.283 | 0.183 | 0.346 |
| drop_ans | 0.068 | 0.296 | 0.637 | 0.814 |
| drop_other | 0.222 | 0.122 | 0.656 | 0.355 |
| drop_all | 0.013 | 0.087 | 0.900 | 0.871 |

- **H1 (konfirmatori, sesuai definisi pre-reg):** halusinasi full → drop_ans hampir tidak berubah (0.283 → 0.296). Dalam bentuk ini H1 kemungkinan **tidak didukung**: model 3B bergeser ke abstain ketika evidence hilang. Tetapi selective risk melonjak 0.35 → 0.81; hampir setiap jawaban yang tetap diberikan adalah karangan. Definisi H1 (laju halusinasi per item) mencampur *kecenderungan menjawab* dan *ketepatan*. Ini pelajaran desain untuk pre-reg berikutnya.
- **H3a:** off → advisory @drop_ans: 0.296 → 0.312 (tidak ada efek). Catatan: verdict teks reader 3B hampir selalu INSUFFICIENT (juga @full), jadi sinyalnya tidak informatif. Mengabaikannya justru rasional. Uji yang lebih bersih adalah fase 1b (σ EAG yang informatif).
- **H4:** enforced → false refusal @full 0.18 → 0.76. **Gagal**: reader berbasis prompt terlalu konservatif.
- **H2:** restored ≈ restored_ctrl (0.251 vs 0.238). Tidak ada anchoring. Menanyakan ulang dengan evidence penuh saja (ctrl) menaikkan benar 0.534 → 0.572.

**Temuan eksploratif (pasca-hoc, perlu konfirmasi):**
- *Kecenderungan menjawab bersifat spesifik item:* P(menjawab @drop_ans | menjawab @full) = 0.44, sedangkan P(menjawab @drop_ans | abstain @full) = 0.035.
- *Halusinasi saat akses diblokir adalah konfabulasi berbasis evidence parsial:* hanya 1,1% halusinasi @drop_ans sama dengan jawaban closed-book (bukan ingatan parametrik). **78%** adalah string yang disalin dari paket yang tersisa (47% dari unit emas yang tersisa, yaitu paragraf penghubung; 32% dari pengisi/pengecoh). Pada drop_all, 93% disalin dari pengecoh. Ini analog fungsional terdekat dengan "interpreter" split-brain: narasi koheren dirakit dari informasi yang kebetulan tersedia. Caveat: prompt ekstraktif ("answer using only the evidence") mendorong penyalinan, jadi perlu uji dengan prompt non-ekstraktif.

### Studi 2 dirancang dan didaftarkan (21:30), sebelum datanya dibuat
- Pre-reg: `06_preregistration_study2_confabulation.md`. Uji kausal atas temuan eksploratif "konfabulasi berbasis evidence parsial": pengisi `entity_rich` vs `entity_poor` (panjang setara) pada `drop_ans` / `drop_all`, prompt `extractive` vs `open`.
- 400 item dev baru (tidak tumpang tindih dengan pilot), seed 20261006, manifest + sha256.
- `conditions.plan_item(filler_policy=...)`: default `length` terbukti identik dengan paket pilot (160/160). Cek manipulasi pada mock: densitas kandidat pengisi rich 6,2 vs poor 1,2; rasio panjang ≈ 1,0.
- Antrean GPU kedua (`scripts/chain2_judge_study2.sh`), dijalankan otomatis setelah rantai EAG selesai dan model 7B lengkap: judge pilot → agreement judge vs audit Claude → evaluasi + analisis ulang pilot → evaluasi ulang EAG pada label terkoreksi → Studi 2 (3B) → judge Studi 2 → analisis Studi 2.
- Unduhan: Qwen2.5-7B-Instruct (judge), Qwen2.5-1.5B-Instruct (replikasi Studi 2). Unduhan via `snapshot_download` macet; diganti `curl` langsung ke `resolve/main`.

### Dijeda atas permintaan user (2026-10-05 22:55)
- **Selesai & tersimpan:** semua generasi pilot; fitur EAG `08_architecture/features_train.pt` (27.724 paket, 1,2 GB) dan `features_test.pt` (1.972); model judge Qwen2.5-7B dan Qwen2.5-1.5B terunduh lengkap; item Studi 2 disampel.
- **Terputus:** training head EAG (8/12 run selesai, tetapi `train_summary.json` baru ditulis di akhir), jadi ke-12 run akan diulang (~6 menit).
- **Belum dijalankan:** evaluasi EAG, judge, evaluasi ulang pilot, Studi 2.
- **Lanjutkan dengan satu perintah:** `bash scripts/resume.sh`. Isinya: training EAG → evaluasi EAG → judge → evaluasi ulang pilot dan EAG → Studi 2 (3B) → judge → analisis Studi 2. Perkiraan total ~2–2,5 jam.
- Setelah itu (opsional): fase 1b jika H5a dan H5b didukung; replikasi Studi 2 dengan 1.5B / 7B.

### 2026-10-06 — Resume; judge vs audit; hasil konfirmatori pilot dan EAG fase 1
**Label (deviasi, dicatat sebelum analisis konfirmatori dibaca):**
- Judge Qwen2.5-7B vs audit Claude pada 180 kasus ambigu: agreement 0,817, κ = 0,61.
- Judge sistematis menolak bentuk pendek yang jelas benar ("Todd Field" ↔ "William Todd Field", "Micky Dolenz" ↔ "George Michael Dolenz", "Mikael Stanne"), dan menerima 4 yang jelas salah ("Price's home-studio" ↔ "Stuart Price", "The Highwaymen" ↔ lagu "Highwayman").
- **Label primer = audit (terdokumentasi per item), judge mengisi sisanya** (`EAA_LABELS=audit_then_judge`). Label judge-saja dan strict dipakai sebagai analisis sensitivitas. Klaim dianggap kuat hanya jika bertahan di ketiganya.

**Pilot H1–H4 (populasi primer, 311 item, label terkoreksi):**
- H1a full→drop_ans: +0,013 [−0,045; 0,074] → **tidak didukung**. H1b full→drop_all: −0,196 (arah berlawanan; model abstain).
- H2: off@drop_ans → restored: −0,045 (n.s.). TOST restored vs ctrl: 90% CI [−0,026; 0,051] dengan margin 0,05 → **tidak konklusif** (nyaris).
- H3a: off → advisory @drop_ans: +0,016 (n.s.) → peringatan reader diabaikan.
- H3b: selective risk 0,81 → 0,59, CI [−0,456; 0,002], Holm p = 0,21 → **tidak didukung** (arah sesuai).
- H4: false refusal 0,18 → 0,76 → **gagal**.

**EAG fase 1 (AURC pada jawaban substantif, primer; acak = 0,485):**
- eag_lc1 0,393; eag_lc0 0,380; probe 0,370; qe 0,438; reader_p_suff 0,434; cue_only 0,442; oracle_full 0,389; oracle_answer 0,371.
- H5a −0,041 [−0,088; 0,006]; H5b +0,023 (probe ≥ eag); H5c −0,045 (p 0,024, Holm 0,072) → **H5a–c tidak didukung**.
- H6: Δσ_untrained +0,017 [0,003; 0,032] ✓, tetapi AURC tidak non-inferior (CI atas 0,033 > 0,005) → **tidak didukung**.
- **Temuan:** gate terlatih (probe/eag) sudah setara oracle; pairwise accuracy full > drop_* = 0,98–0,99, termasuk pada `drop_other` yang tidak pernah dilatih. Kecukupan evidence sudah terbaca dari state generator 3B (cabang "H5b gagal" di pre-reg §3). Batas atas gating berbasis kecukupan rendah, karena sebagian besar kesalahan pada `full` adalah salah baca, bukan kekurangan evidence.

**Deviasi: fase 1b tetap dijalankan.** Pre-reg §3 mensyaratkan H5a dan H5b. Namun cabang "H5b gagal" mengarahkan ke pertanyaan **otoritas**, dan fase 1b adalah uji otoritas tersebut. σ = eag_lc1 (sesuai §5.9), yang kualitasnya setara oracle. Dilaporkan sebagai uji yang dijalankan di luar syarat awal.
- Antrean 3: fase 1b (advisory + plasebo) → Studi 2 1.5B → Studi 2 7B 4-bit → judge. Kasus ambigu baru akan diaudit sebelum analisis.

### Studi 2 (Qwen2.5-3B) — hasil konfirmatori (2026-10-06 ±09:00)
- Infrastruktur: Studi 2 pada bs 8 melambat ke 8–17 s/batch karena VRAM tumpah (7,5/8 GB). Restart dengan bs 4 (resumable). Judge gagal sekali karena hanya memuat item pilot; diperbaiki (memuat semua `01_data/hotpot_dev_*.jsonl`).
- Label: 85 kasus ambigu baru diaudit Claude (66 benar / 19 salah) → `06_evaluation/audit_ambiguous_claude_study2.jsonl`.
- 396 item (4 dikecualikan), 255 primer. Cek manipulasi OK: densitas kandidat pengisi rich 4,6–4,7 vs poor 1,6; rasio panjang 0,99–1,00; jawaban tidak ada di paket drop_*.
- **S2-H1** (extractive, drop_ans): halusinasi poor 0,318 vs rich 0,333, selisih +0,016 [−0,024; 0,059], Holm p = 1 → **tidak didukung**.
- **S2-H2** (drop_all): 0,102 vs 0,098 → **tidak didukung**. Varian prompt open juga nol.
- **S2-H3:** proporsi halusinasi drop_ans yang berupa string di paket = 0,735 (Wilson [0,663; 0,796]) → **didukung**.
- **S2-H4** (open): 0,931 [0,864; 0,966] → **didukung**. Penyalinan bukan artefak instruksi ekstraktif.
- **Interpretasi:** konfabulasi saat akses diblokir dirakit dari materi evidence (terutama paragraf emas yang tersisa: 46% extractive / 65% open), tetapi **lajunya tidak bergantung pada banyaknya kandidat** di pengisi. Hipotesis "anchoring pada ketersediaan kandidat" ditolak. Yang tersisa lebih spesifik: model mengambil entitas dari evidence yang *relevan dengan pertanyaan* (paragraf penghubung), bukan dari sembarang nama yang tersedia.
- **Replikasi pilot (item baru):** halusinasi full 0,278 → drop_ans 0,318–0,333 (≈); selective risk 0,36 → 0,84.
- Eksploratif: prompt open menaikkan abstain di semua level (full 0,23 → 0,35) dan menurunkan benar @full (0,49 → 0,41).

### 2026-10-06 — Robustness label (stats-analyst)
- Kontras konfirmatori pilot (H1–H4), EAG (H5a–c, H6), dan Studi 2 (S2-H1..H4) dihitung ulang dengan tiga set label: audit→judge (primer), judge-saja, dan strict. Label primer mereproduksi angka di `07_analysis/{pilot_v0.2_qwen2.5-3b,eag_phase1,study2_qwen2.5-3b}` secara persis. Skrip: `scripts/robustness_labels.py` dan `scripts/robustness_summary.py`. Output: `07_analysis/robustness/summary.md`.
- **Satu-satunya verdict yang berubah: H6.** Pada label strict, AURC eag_lc1 − eag_lc0 = −0,023 [−0,043; −0,004], sehingga non-inferior dan H6 menjadi "didukung". Pada label primer dan judge-saja, H6 tidak didukung. Kami tetap menganggap H6 tidak didukung, dengan catatan sensitif terhadap label.
- Perubahan lain tidak mengubah verdict:
  - pada label strict, H1a (−0,13) dan H2 (+0,10) signifikan ke arah berlawanan, karena parafrase benar @full dihitung salah;
  - pada judge-saja, H2eq = +0,045, CI90 [0,006; 0,084] (ada indikasi anchoring);
  - pada judge-saja, CI H3b tidak memuat 0, tetapi Holm p = 0,15.
- Lonjakan selective risk full→drop_ans bertahan di ketiga set label, baik di pilot maupun di Studi 2.
- Laporan interim untuk supervisor: `09_reports/interim_results_2026-10-06.md`.

### Fase 1b — σ (eag_lc1) advisory vs authority (2026-10-06 ±09:30)
- Generasi: 3.944 (advisory + plasebo, 1.972 paket uji). 10 kasus ambigu baru diaudit → `06_evaluation/audit_ambiguous_claude_phase1b.jsonl`.
- **Kontras primer pre-reg (§5.9) DEGENERATE:** τ* dipilih supaya laju menjawab hard gate sama dengan advisory. Tetapi advisory *menaikkan* laju menjawab (0,406 → 0,481), sedangkan hard gate atas output `off` hanya bisa menurunkannya. Akibatnya τ* = 0 dan authority@matched ≡ off. P1 (primer) = −0,023 [−0,052; 0,003] secara substantif adalah off vs advisory. **Kontras primer tidak dapat menjawab pertanyaannya.** Dilaporkan apa adanya; pelajaran desain: kesamaan cakupan harus didefinisikan relatif terhadap cakupan yang bisa dicapai kedua sistem.
- **Plasebo (konfirmatori, pre-reg):** advisory dengan σ asli vs σ diacak: halusinasi −0,002 [−0,014; 0,008], abstain +0,002. **Generator tidak memakai nilai σ sama sekali.** Teks advisory itu sendiri menaikkan halusinasi +0,047 [0,031; 0,067] vs off.
- **Sekunder / eksploratif** (populasi primer; bootstrap item berpasangan, 2.000×):
  - authority@0.5 vs advisory: halusinasi −0,155 [−0,179; −0,133]; selective risk −0,147 [−0,189; −0,107]; benar −0,079 [−0,097; −0,060]; false refusal @full +0,148 [0,109; 0,190].
  - authority@0.5 vs off: halusinasi −0,108 [−0,128; −0,089]; selective risk −0,124 [−0,156; −0,091]; benar −0,051 [−0,066; −0,038]; false refusal @full +0,084 [0,055; 0,113]. Sebagai pembanding, gate reader-prompt (pilot H4): +0,58.
  - Kurva risk–coverage authority: selective risk turun dari 0,485 (τ=0) ke ±0,35 (τ ≥ 0,5) lalu mendatar. Lantai ini adalah kesalahan salah-baca pada `full` yang tidak terdeteksi oleh gate berbasis kecukupan.
- **Interpretasi (hati-hati):** sinyal epistemik yang sama tidak berpengaruh saat diberikan sebagai teks (value-insensitive, setara plasebo), tetapi mengurangi halusinasi ±11 pp saat diberi otoritas atas output, dengan biaya ±5 pp jawaban benar. Ini konsisten dengan tesis "masalahnya otoritas, bukan informasi". Keterbatasan: varian advisory tidak di-fine-tune (deep-read §5); satu model 3B; kontras primer gagal sehingga bukti ini sekunder.

### Koreksi (2026-10-06): ukuran head EAG
- Jumlah parameter terukur: probe 3,23 juta; qe/eag 3,37 juta (±0,11% dari Qwen2.5-3B). Angka "±1–2 juta" di `03_architecture_EAG_v0.1.md` §2.2 dan di versi awal briefing salah (dihitung dengan d_e saja, tanpa proyeksi h dari 3 layer × 2048). Briefing sudah dikoreksi.

### Replikasi Studi 2: Qwen2.5-1.5B dan Qwen2.5-7B (4-bit) — selesai 10:15
- 104 kasus ambigu baru diaudit Claude (46 benar) → `06_evaluation/audit_ambiguous_claude_replications.jsonl`.
- **S2-H1** (rich vs poor, drop_ans, extractive): 1.5B −0,004 [−0,051; 0,039]; 7B −0,020 [−0,051; 0,012] → **tidak didukung**, konsisten dengan 3B.
- **S2-H2** (drop_all): 1.5B −0,012; 7B +0,035 [0,008; 0,067], p 0,023, Holm 0,067 → tidak didukung setelah Holm (7B nyaris).
- **S2-H3/H4** (karangan disalin dari paket): 1.5B 0,739 [0,680; 0,790] / open 0,845; 7B 0,837 [0,762; 0,892] / open 0,846 → **didukung** di semua ukuran.
- **Eksploratif, lintas ukuran** (extractive, full → drop_ans poor, bootstrap item berpasangan):

| model | halusinasi full → drop_ans | selisih [95% CI] | selective risk |
|---|---|---|---|
| 1.5B | 0,314 → 0,482 | +0,169 [0,098; 0,243] | 0,35 → 0,84 |
| 3B | 0,278 → 0,318 | +0,039 [−0,024; 0,102] | 0,36 → 0,84 |
| 7B | 0,157 → 0,251 | +0,094 [0,039; 0,149] | 0,19 → 0,75 |

- **Interpretasi:** kegagalan H1 di pilot kemungkinan spesifik model 3B (yang paling banyak beralih ke abstain). Pada 1.5B dan 7B, memblokir akses menaikkan laju halusinasi. Lonjakan selective risk (+0,47 sampai +0,56) dan penyalinan dari evidence (74–85%) robust di ketiga ukuran. Ini temuan eksploratif; layak dijadikan hipotesis konfirmatori di studi berikutnya (model non-Qwen).

### Penutupan sesi (2026-10-06)
- Semua run terjadwal selesai; tidak ada proses GPU yang berjalan.
- Dokumen dibuat:
  - Briefing riset (Claude Doc): https://claude.ai/code/artifact/758ec20e-c435-468f-b552-7d1d0bf5e46f — termasuk perjalanan riset, arsitektur EAG, hasil, dan calon supervisor.
  - Memo 2 halaman untuk calon supervisor (English): https://claude.ai/code/artifact/a12100c0-0f61-4d6c-8ebf-0349805f2c70
  - Gambar: `09_reports/figures/`.
- Langkah berikutnya (butuh keputusan user, sebaiknya setelah masukan supervisor):
  1. pre-registrasi ulang advice vs authority;
  2. model non-Qwen;
  3. baseline CAA / RINSE;
  4. audit label oleh manusia;
  5. konfirmasi temuan lintas ukuran (H1 muncul di 1.5B/7B, tidak di 3B).

## 2026-10-11

### Gagasan "aturan berhenti" (optimal stopping) + cek literatur
- Usulan user: memakai matematika supaya model tahu kapan berhenti, terutama ketika informasi sudah cukup terelaborasi. Formulasi: lanjut ⇔ σ·g − λ(1−σ) − μ > 0, dengan g = sisa evidence yang belum diekspresikan.
- Literature-scout (`00_docs/07_prior_art_stopping_rule.md`):
  - **tidak baru:** filter klaim terkalibrasi (Mohri & Hashimoto 2024); aturan Bayes ambang biaya (CASS, arXiv 2605.01749, yang identik dengan rumus kita bila g = 1, μ = 0); trade-off verbosity–faktualitas (Spataru NAACL 2024); stopping di decoding berbasis keyakinan internal (Sequential-EDFL).
  - **mungkin baru:** g online dari evidence, satu aturan untuk abstain dan stop, penegakan otoritas vs saran.
  - **Ablasi g = 1 wajib.** Dataset kandidat: ASQA, QAMPARI (ALCE).
  - Belum dijalankan; dicatat sebagai studi lanjutan.

### Dokumen untuk dosen UI (Claude Doc, Bahasa Indonesia formal)
- https://claude.ai/code/artifact/b20df51d-b05c-453b-83f9-df4d40dfb14a — ringkasan, latar belakang, metode, hasil, hal yang tidak terdukung, gagasan aturan berhenti (dengan posisi literatur yang jujur), pertanyaan diskusi, lampiran istilah.

### Studi 3 / 3b — advice vs authority, konfirmatori (pre-reg `08_preregistration_study3_authority.md`)
- Didaftarkan sebelum σ dihitung. Kontras dirancang ulang supaya selalu terdefinisi:
  - **P1:** TOST advice ≈ placebo, ±0,02;
  - **P2:** authority − off ≤ −0,05;
  - **P3:** U = benar − 2·halusinasi, authority > advice.
- User memasang `gemma4:e4b` di Ollama. Dipakai sebagai **generator non-Qwen** (Studi 3b), dengan σ dari reader Qwen + EAG (arsitektur reader ≠ generator). Determinisme dicek (3/3 identik). Ditambahkan `OllamaBackend` (tidak ada hidden state, jadi hanya bisa sebagai generator).
- σ pada 400 item baru (tanpa pelatihan ulang): mean full 0,787 · drop_ans 0,180 · drop_all 0,027.
- Antrean `scripts/chain5_study3.sh` berjalan: Qwen advice/placebo → Gemma off/advice/placebo → judge.

### Studi 3 / 3b — HASIL KONFIRMATORI (2026-10-11 ±02:10)
- 22 kasus ambigu baru diaudit (13 benar) → `06_evaluation/audit_ambiguous_claude_study3.jsonl`; judge_missing = 0.
- Bug analisis diperbaiki sebelum hasil dibaca: bootstrap pada subset `full` salah indeks (sekarang mask + nanmean, resampling tetap per item); direktori laporan per generator.
- Populasi primer: 255 item × 5 paket.

**Qwen2.5-3B (σ dan generator dari model yang sama):**
- **P1** advice − placebo = −0,008, 90% CI [−0,017; 0,002] dalam ±0,02 → **didukung** (saran inert, replikasi fase 1b).
- **P2** authority − off = −0,133 [−0,161; −0,109], Holm p 0,001 → **didukung**.
- **P3** U(λ = 2) authority − advice = +0,365 [0,297; 0,431] → **didukung**.
- **Biaya:** false refusal @full +0,114 [0,075; 0,153]; batas atas melewati ambang praktis 0,15 (tipis).
- Saran menaikkan halusinasi vs off +0,073 [0,053; 0,093] (konsisten dengan fase 1b).

**Gemma 4 E4B (generator) + σ dari reader Qwen (reader ≠ generator):**
- **P1** advice − placebo = +0,009, 90% CI [0,002; 0,017] dalam ±0,02 → **didukung** (ekuivalen; ada sedikit selisih yang terdeteksi).
- **P2** authority − off = −0,042 [−0,059; −0,027] → **tidak didukung** menurut kriteria (≤ −0,05), walau penurunannya signifikan. Gemma off sudah jarang berhalusinasi (0,086) dan sangat konservatif (abstain 0,80).
- **P3** U(λ = 2) = +0,035 [0,005; 0,068], Holm p 0,018 → **didukung**.
- **Biaya:** false refusal +0,098 [0,063; 0,137], aman.

**Interpretasi:**
- Pola "saran inert, otoritas efektif" kini **konfirmatori** pada item baru untuk Qwen 3B, dan arahnya **tereplikasi lintas keluarga model** (Gemma) dengan σ dari reader model lain.
- Besaran efek otoritas bergantung pada baseline halusinasi generator.
- Biaya false refusal pada Qwen berada di batas ambang praktis.

### Jeda menunggu masukan dosen UI (2026-10-11)
- Keputusan user: eksperimen baru ditunda sampai ada masukan dosen UI.
- Pertanyaan "langkah berikutnya" ditambahkan ke dokumen (bagian diskusi):
  1. studi aturan berhenti σ + g (ASQA/QAMPARI, ablasi g = 1);
  2. menurunkan biaya false refusal gate (τ terkalibrasi / gate bertingkat);
  3. generalisasi (model/dataset lain, termasuk bahasa Indonesia; baseline; audit manusia);
  4. arah lain.
- Tidak ada proses GPU yang berjalan.

### Benchmark + teori + kalibrasi (2026-10-11, lanjutan)
- Riset literatur (`00_docs/09_benchmark_and_theory.md`): aturan kita dengan g = 1, μ = 0, λ = t/(1−t) **identik** dengan aturan skor ber-penalti Kalai dkk. 2025 ("jawab jika P(benar) > t"). Gate σ < 0,5 berarti t = 0,5. Teori ketidakmungkinan (Xu 2024; Kalai & Vempala 2024) membahas pengetahuan parametrik dan tidak melarang abstensi. Jaminan konformal bersifat marginal dan gugur saat distribution shift.
- **Kalibrasi σ (Studi 3, Qwen off, primer):**
  - ECE terhadap kecukupan = **0,048** (terkalibrasi baik);
  - ECE terhadap kebenaran jawaban = **0,256** (tidak terkalibrasi; pada σ ≈ 0,98 hanya 56% benar).
  - **Implikasi:** σ = P(cukup) ≠ P(benar). Aturan keputusan optimal butuh P(benar). Kesalahan "salah baca" saat evidence lengkap tidak tertangkap σ. Ini batas utama pendekatan sekarang.
- Benchmark (pre-reg addendum 08): skor dibatasi ke 447 jawaban substantif primer (ekuivalen untuk semua metrik gate; mempercepat 6,5 jam → ±30 menit). Ditambah baris gate acak pada laju menjawab yang sama.
- Audit sitasi (peer-reviewed vs preprint) berjalan, atas permintaan user.

### Benchmark gate vs metode standar — HASIL (pre-reg addendum 08; sekunder)
- Qwen2.5-3B, Studi 3 primer; 447 jawaban substantif dari 1.275 baris.
- **AURC** (lebih kecil lebih baik), selisih terhadap eag_sigma [95% CI]:

| gate | AURC | selisih vs eag_sigma [95% CI] |
|---|---|---|
| eag_sigma | 0,499 | — |
| p_true | 0,525 | +0,026 [−0,040; 0,091] |
| seq_conf | 0,521 | +0,022 [−0,032; 0,080] |
| reader_p_suff | 0,526 | +0,027 [−0,021; 0,079] |
| self_consistency | 0,594 | +0,095 [0,046; 0,144] |
| oracle_full | 0,434 | — |
| acak | 0,644 | — |

- **AUROC** benar-vs-halusinasi: eag 0,715 · p_true 0,694 · reader 0,673 · seq 0,662 · self-consistency 0,548.
- **Gate pada laju menjawab sama (0,180):**
  - halusinasi: eag 0,093 · p_true 0,091 · reader 0,095 · seq 0,097 · **acak 0,116** · off 0,226;
  - false refusal @full: eag **0,345** vs p_true 0,510, reader 0,455, seq 0,506 · acak 0,605.
- **Interpretasi:**
  1. Sebagian besar penurunan halusinasi berasal dari abstensi. Pada cakupan yang sama, gate terbaik hanya ±2,4 poin di bawah gate acak.
  2. Sinyal ketidakpastian standar setara dengan σ dalam menekan halusinasi (AURC tidak berbeda signifikan).
  3. Keunggulan σ yang jelas adalah false refusal pada evidence lengkap yang jauh lebih rendah (σ menargetkan kecukupan).
  4. Klaim "−13,3 poin" harus selalu disertai cakupan dan pembanding gate acak (sesuai peringatan overclaim di 09).

### Versi offline dokumen untuk dosen UI
- `09_reports/Ringkasan_Penelitian_untuk_Dosen_UI.md`: salinan Markdown dari Claude Doc (rev 25), termasuk bagian teori, benchmark, asal ide split-brain (Sperry/Gazzaniga, diverifikasi dari *Brain* 2017 dan *J. Neurol.* 2022), label status rujukan, dan konteks laju menjawab pada angka −13,3 poin.

### 2026-10-14 — Umpan balik Pak Alfan (dosen UI) + analisis eksploratif "full tapi salah"
- Dokumen untuk dosen ditambah bagian operasional pelatihan head σ (data kontrafaktual, fitur, arsitektur, loss, inference). Jumlah parameter: modul 3.365.121; pada varian eag proyeksi pertanyaan tidak terpakai → ±2,84 juta yang benar-benar dilatih.
- Umpan balik dosen: (1) σ mirip selective prediction → arahkan ke "tahu tapi tidak mengungkap" vs "tidak tahu", plus activation steering; (2) uji saran vs otoritas pada subset `full` yang tetap salah; (3) verifikasi kebaruan secara mandiri (waspada ide dari LLM); (4) multibahasa; (6) tema ACL 2027 "Homogenization and Knowledge Collapse" (deadline ARR 4 Jan 2027).
- **Analisis eksploratif (post-hoc, tidak pre-registered)** pada Studi 3, `full`, populasi primer (255 soal):
  - Qwen 3B `off`: 125 benar, 71 halusinasi, 59 abstain. Median σ: benar 0,962; **halusinasi 0,965** (82% σ ≥ 0,5); abstain 0,629. Jadi σ tidak membedakan jawaban salah dari benar ketika evidence lengkap.
  - Pemulihan halusinasi → benar: saran 1/71, plasebo 0/71, otoritas 0/71 (veto, tidak mungkin memulihkan), saran+otoritas 0/71. Gemma: 0/36 di semua lengan.
  - Tidak-benar → benar (termasuk abstain): saran 17/130 vs plasebo 15/130 (Qwen); Gemma 9/131 vs 3/131. Hampir semuanya abstain → menjawab, bukan koreksi jawaban salah.
- Implikasi desain: "otoritas" versi sekarang hanya veto. RQ pemulihan butuh intervensi pada proses generasi (mis. steering yang dipicu σ). Klaim "tahu tapi tidak mengungkap" butuh bukti bahwa *jawaban* (bukan sekadar kecukupan) ter-decode dari hidden pada 71 kasus tsb. (probe jawaban / logit lens) sebelum steering.
- Rencana lanjutan ditulis di `00_docs/11_rencana_lanjutan_pasca_masukan_dosen.md`: Fase 1 diagnosis "tahu tapi tidak mengungkap" → Fase 2 popularitas entitas → Fase 3 cek literatur steering (YOPO, SHIFT, Kawada & Kellis sudah dekat) → Fase 4 Studi 4 intervensi hidden state (tangga otoritas: saran, veto, intervensi) → Fase 5 multibahasa.

### 2026-10-17 — Fase 1 (diagnosis) + Fase 3 (literatur), eksploratif
- Rencana analisis ditulis sebelum menghitung apa pun: `00_docs/12_analysis_plan_diagnosis_popularity.md`. Kode: `eaa/diagnose.py` (score / pageviews / analyze). Output: `07_analysis/diagnosis/`.
- **Hasil Fase 1** (Qwen 3B, `full`, populasi utama; benar 125, halusinasi 71, abstain 59):
  - **Sumber pengetahuan hampir seluruhnya konteks.** *Closed-book* benar hanya 3% secara keseluruhan; dari 71 halusinasi, hanya 2 yang jawabannya diketahui dari memori.
  - **Kriteria K1 primer cacat** (keluaran *greedy* ⇒ LP_own ≈ 0; K1 = 0/71 adalah tautologi). Dicatat sebagai deviasi; tidak dipakai untuk keputusan.
  - K1 longgar (token pertama jawaban emas masuk 5 besar di t₀): **34/71 = 48%** [37%; 59%]. 19/71 ada di peringkat ≤ 2; 18/71 di atas peringkat 100. Pada jawaban benar, 88% peringkat ≤ 5.
  - Konteks lengkap tetap menaikkan peluang jawaban emas pada kasus halusinasi: ΔLP_ctx median 3,96 nat/token (benar 5,19; p = 0,017). Informasinya masuk, tetapi kalah bersaing.
  - Jenis kesalahan: **61% memilih entitas lain dari paragraf emas**, 11% berhenti di hop pertama, 13% menyalin dari pengecoh, 6% parsial, 10% lainnya.
  - *Logit lens*: jawaban emas baru muncul di 3–4 lapisan terakhir pada semua kelompok. Tidak ada pola "muncul di lapisan tengah lalu ditekan" (catatan: *logit lens* lemah di lapisan tengah Qwen).
  - σ tidak membedakan benar vs halusinasi (Mann–Whitney p = 0,73), konsisten dengan uji kalibrasi.
  - Derau label: sebagian emas HotpotQA tidak berbentuk jawaban, dan beberapa "halusinasi" nyaris benar.
- **Fase 3 (literatur)** → `00_docs/13_prior_art_steering_followup.md`:
  - YOPO (2608.14465): *steering* terlatih + *gate* kecukupan pada Qwen2.5 1.5B/3B/7B, termasuk MuSiQue. Pembanding verbalnya berupa instruksi, bukan nilai sinyal yang sama dan tanpa plasebo; tidak menghitung *flip* salah → benar; tanpa HotpotQA, popularitas, atau multibahasa.
  - Lu dkk. (2602.14529): dikotomi *knowledge existence* vs *behavior expression*; perilaku diinduksi DPO, parametrik, satu-hop, LLaMA-3.1-8B; *steering* memulihkan ±45% KI → KC, halusinasi ≈ 0.
  - SHIFT (2606.27786) berganti judul menjadi SPARK di v2 (13 Okt 2026); entri prior art diberi catatan.
- **Keputusan:** Studi 4 dibingkai sebagai perbandingan tiga bentuk otoritas (saran, veto, intervensi) dengan nilai sinyal identik dan plasebo, pada kegagalan alami multi-hop. Populasi target *steering*: kasus "nyaris" (R_final ≤ 5). Sebelum itu, jalankan Fase 1b: *probe* internal vs eksternal ala Gekhman dkk. untuk menguji "tahu tapi tidak mengungkap" secara benar.
- Fase 2 (popularitas): *pageviews* masih diambil (REST API Wikimedia membatasi laju klien tanpa kontak; ±6–12 judul/menit, 795 judul). Analisis menyusul.
