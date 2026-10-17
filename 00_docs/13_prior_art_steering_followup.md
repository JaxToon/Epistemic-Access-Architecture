# Cek Literatur Fase 3: *Steering* dan "Tahu tapi Tidak Mengungkap"

Tanggal: 17 Oktober 2026. Tujuan: memeriksa kebaruan Studi 4 (dokumen 11) **sebelum** desainnya dikunci, sesuai peringatan Pak Alfan (P3). Status verifikasi: halaman abstrak arXiv dibaca langsung (V-abs). Isi lengkap belum dibaca kecuali disebutkan.

## Temuan

| # | Paper | Status | Isi yang relevan | Dampak bagi rencana |
| --- | --- | --- | --- | --- |
| 1 | Luo dkk., *You Only Pass Once (YOPO)*, arXiv 2608.14465 (14 Agt 2026) | V-abs | LM beku memakai kurang dari yang tersedia di *residual stream*. Menggabungkan *conditional steering probe* yang memulihkan akurasi dengan *sufficiency direction* untuk abstensi, dalam satu *forward pass*. **Qwen2.5 1.5B/3B/7B**, replikasi termasuk MuSiQue (multi-hop) dan SQuAD2. Membandingkan beberapa keluarga *gate*. Abstrak tidak menyebut perbandingan dengan sinyal di *prompt* | **Ancaman kebaruan terbesar untuk Studi 4.** "*Steering* + *gate* kecukupan pada Qwen2.5" sudah dikerjakan. Studi 4 tidak boleh dibingkai sebagai metode *steering* baru |
| 2 | Lu dkk., *Disentangling Deception and Hallucination Failures in LLMs*, arXiv 2602.14529 (Feb 2026) | V-abs | Memisahkan *Knowledge Existence* dari *Behavior Expression*, dan memasukkan kasus "*known-incorrect*". Lingkungan terkontrol untuk QA faktual berbasis entitas, dianalisis dengan *probe*, interpretabilitas *sparse*, dan *steering* | **Dikotomi Pak Alfan (P1) sudah dirumuskan di sini**, untuk pengetahuan parametrik dalam lingkungan sintetis. Wajib dikutip |
| 3 | Li dkk., arXiv 2606.27786 | V-abs | v1 (26 Jun 2026): *SHIFT: Gate-Modulated Activation Steering for Knowledge Conflict Mitigation in RAG*. **v2 (13 Okt 2026) berganti judul menjadi *SPARK: Adaptive Parametric Knowledge Participation for Faithful RAG***. *Policy* ringan (±0,01% parameter) pada LLM beku, dilatih dengan *reward* kesetiaan, tanpa abstensi | Entri A5 di `04_prior_art_EAG_v0.1.md` benar untuk v1. Catat perubahan judul agar sitasi tidak tampak salah |
| 4 | Kawada & Kellis, arXiv 2609.04290 | V-full (sudah ada di 04) | Representasi verifikasi dapat di-*decode*, tetapi efek *steering*/*patching* bergantung model | Studi 4 butuh minimal dua keluarga model |

### YOPO, isi lengkap (HTML, ±100 ribu dari 130 ribu karakter dibaca)

- ***Steering probe*:** MLP kecil (±1% parameter *backbone*) yang membaca *residual stream* di lima posisi *prompt*, lalu menulis balik suntingan dengan arah yang bergantung pada input dan besaran ber-*gate*. Disuntikkan di lapisan tengah (16, 20, 24 untuk 3B). Dilatih dengan *cross-entropy* jawaban, *backbone* beku. Jadi ini *steering* terlatih, bukan vektor kontrastif.
- **Pembanding verbal ada:** "*zero-shot spoken judgment*", *forced chain-of-thought*, "*behavioral route*" (menjawab dengan izin eksplisit untuk abstain), dan *prompt* tiga-arah. Semua ini adalah **instruksi**. Tidak ada pembanding yang menampilkan **nilai sinyal yang sama** di *prompt*, dan tidak ada kontrol plasebo.
- **Tidak melaporkan** jumlah item yang berubah dari salah menjadi benar pada konteks cukup. Hanya akurasi dan AUROC agregat.
- **Data:** αNLI, HellaSwag, RepLiQA, BoolQ, SQuAD 2.0, MuSiQue. **Tanpa HotpotQA, tanpa analisis popularitas, tanpa multibahasa.**

### Lu dkk., isi lengkap (HTML, ±100 ribu dari 238 ribu karakter dibaca)

- **"Tahu" diukur secara operasional** dari kebenaran model dasar ("*correctness under L is used as a proxy for knowledge existence*"), ditambah *jailbreak probing*. Tidak memakai *probe*, log-prob, atau *logit lens*.
- **Empat kasus:** KC (*known-correct*), KA (*known-avoid*), KI (*known-incorrect*), dan hal (tidak tahu tetapi menjawab).
- **Perilakunya sintetis.** KI dan KA diinduksi dengan DPO. Pengetahuannya **parametrik**, QA faktual satu-hop, empat tipe entitas. Model: LLaMA-3.1-8B-Instruct.
- ***Steering*:** sekitar 45% KI → KC dan sekitar 47% KA → KC. Kasus **halusinasi hampir tidak bisa dipulihkan** (*flip rate* ≈ 0). Catatan: satu *flip* dihitung jika ada sudut mana pun dari 10° sampai 350° yang berhasil, jadi angka ini batas atas.
- **Implikasi untuk kita:** prediksi yang bisa diuji di Studi 4 adalah bahwa *steering* memulihkan kasus K1 tetapi tidak K2. Dengan begitu, Fase 1 (memisahkan K1/K2) menjadi syarat yang tepat sebelum Fase 4.

## Ruang yang masih tersisa (sementara)

1. **Perbandingan tiga bentuk otoritas dengan nilai sinyal yang identik, ditambah kontrol plasebo:** saran di *prompt* vs veto vs intervensi. YOPO punya pembanding verbal berupa instruksi, bukan nilai sinyal yang sama, dan tanpa plasebo. Ruang ini **menyempit tetapi masih ada**. Temuan kita (saran ≈ plasebo, veto tidak memulihkan) adalah dua dari tiga anak tangga.
2. **Kegagalan alami pada konteks *multi-hop* yang lengkap.** Lu dkk. bekerja dengan perilaku yang diinduksi DPO, pengetahuan parametrik, dan soal satu-hop. Ruang ini **jelas masih ada**. Kasus "evidence lengkap tetapi salah" pada HotpotQA terjadi secara alami, dan sumber pengetahuannya bisa dipisahkan (konteks vs memori, lewat *closed-book*).
3. **Siapa yang terdampak:** popularitas entitas dan bahasa. Tidak terlihat di abstrak 1–3.

## Tindakan

- Baca utuh YOPO dan Lu dkk. sebelum pre-registrasi Studi 4. Yang perlu dicek: apakah YOPO melaporkan pemulihan khusus pada kasus konteks cukup, dan bagaimana Lu dkk. mengukur "*knowing*".
- Jika YOPO ternyata sudah membandingkan sinyal di *prompt*, ruang no. 1 gugur, dan fokus beralih ke no. 2–3.
- Perbarui `04_prior_art_EAG_v0.1.md` (A5: catatan ganti judul) dan matriks literatur.

## Sumber

- https://arxiv.org/abs/2608.14465
- https://arxiv.org/abs/2602.14529
- https://arxiv.org/abs/2606.27786 (v1 dan v2)
