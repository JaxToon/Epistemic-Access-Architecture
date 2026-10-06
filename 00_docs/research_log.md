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
