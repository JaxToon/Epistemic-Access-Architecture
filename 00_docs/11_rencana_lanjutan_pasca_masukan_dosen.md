# Rencana Lanjutan setelah Masukan Pak Alfan (14 Oktober 2026)

Status: draf rencana, belum ada pre-registrasi baru. Analisis eksploratif yang disebut di sini tercatat di `research_log.md` (entri 2026-10-14).

## 1. Rekap masukan dan posisi kita

| Masukan Pak Alfan | Posisi kita saat ini | Tindak lanjut |
| --- | --- | --- |
| σ = sigmoid dari NN kecil di atas *hidden state* LLM beku | Benar. σ final = rata-rata sigmoid dari 3 seed. Satu contoh data adalah satu paket (bukan per dokumen), label 1 hanya jika kedua gold ada. "Otoritas" adalah status sinyal, bukan σ | Sudah diluruskan di balasan |
| P1: mirip *selective prediction*; bedakan "tahu tapi tidak mengungkap" vs "tidak tahu"; *activation steering* | 71 jawaban salah pada `full` (Qwen 3B) punya median σ 0,965, sama dengan jawaban benar. Belum terbukti bahwa *jawaban*-nya ada di *hidden state* | Fase 1, lalu Fase 4 |
| P2: saran vs otoritas pada subset "full tapi salah", mana yang memulihkan | Eksploratif: saran 1/71, otoritas 0/71, Gemma 0/36. Otoritas versi kita hanya veto, jadi tidak mungkin memulihkan | Fase 4: tambahkan otoritas berupa intervensi |
| P3: verifikasi kebaruan sendiri, waspadai ide dari LLM | Komponen EAG sudah ada di literatur. Untuk *steering*, prior art yang sudah tercatat: YOPO (*sufficiency direction* + *steering* pada LM beku), SHIFT (*gate-modulated steering*), Kawada & Kellis (efek *steering* bergantung model), CANOE/ContextFocus (*steering* untuk kesetiaan konteks), Orgad dkk. (ICLR 2025) | Fase 3, wajib sebelum Fase 4 |
| P4: multibahasa (inklusivitas, ACL) | Belum ada data atau eksperimen | Fase 5 |
| P6: tema ACL 2027 *Homogenization and Knowledge Collapse* (untuk relevansi, bukan target submit) | Kaitan paling kuat: pengetahuan *siapa* yang tidak diungkapkan atau ditolak (popularitas entitas, bahasa) | Fase 2, lalu Fase 5 |

## 2. Benang merah

Inti riset tetap: **jarak antara pengetahuan yang tersedia dan yang diungkapkan, serta bentuk otoritas yang bisa menutupnya.** Masukan dosen menambah dua hal:

- **Tangga otoritas.** Saran (terbukti setara plasebo), lalu veto (menekan halusinasi tetapi tidak memulihkan), lalu intervensi pada *hidden state* (belum diuji).
- **Siapa yang terdampak.** Apakah jarak itu lebih besar untuk entitas yang jarang dan bahasa sumber daya rendah. Ini yang menghubungkan riset ke tema *knowledge collapse*.

RQ gabungan (draf):

> Apakah jarak antara pengetahuan yang tersedia dan yang diungkapkan lebih besar untuk entitas yang jarang dan bahasa sumber daya rendah, dan apakah intervensi pada *hidden state* yang dipicu σ dapat menutupnya tanpa menaikkan penolakan?

## 3. Alur kerja

### Fase 1. Diagnosis "tahu tapi tidak mengungkap" (data yang sudah ada, Qwen 3B)

- **Tujuan:** memisahkan kasus (1) model tahu jawabannya tetapi tidak mengungkapkan, dari kasus (2) model memang tidak tahu, pada subset `full` yang salah.
- **Cara (murah ke mahal):**
  1. Bandingkan log-prob jawaban emas dengan log-prob jawaban model, diberikan *prompt* `full`. Hitung peringkat token pertama jawaban emas di t₀.
  2. *Logit lens*: di lapisan mana jawaban emas sempat muncul lalu hilang.
  3. *Probe* jawaban: apakah benar/salah dapat diprediksi dari *hidden state* pada kasus `full`, terpisah dari σ.
  4. Pisahkan sumber pengetahuan memakai data *closed-book* yang sudah ada: dari konteks atau dari memori internal (sesuai pembedaan Pak Alfan).
  5. Kategorikan jenis kesalahan: jembatan *multi-hop* gagal, memilih entitas pengecoh, jawaban parsial atau beda format.
- **Keluaran:** proporsi kasus (1) dan (2), beserta jenis kesalahannya.
- **Titik keputusan:** jika kasus (1) sangat sedikit, tidak banyak yang bisa dipulihkan oleh *steering*. Fokus bergeser ke kasus (2) dan ke Fase 2.

### Fase 2. Analisis popularitas (data yang sudah ada; bisa paralel dengan Fase 1)

- **Tujuan:** menguji apakah penolakan, halusinasi, dan kasus "σ tinggi tetapi salah" menumpuk pada entitas yang jarang.
- **Cara:** tambahkan jumlah kunjungan halaman Wikipedia (Wikimedia Pageviews API) untuk judul paragraf emas dan entitas jawaban. Bandingkan metrik per kuantil popularitas, untuk lengan `off`, saran, dan *gate*.
- **Disiplin:** tulis rencana analisis singkat sebelum melihat hasil, karena datanya sudah ada (sama seperti praktik pre-registrasi sebelumnya).
- **Titik keputusan:** jika tidak ada efek popularitas, sudut *knowledge collapse* lewat popularitas lemah, dan kaitan ke tema bertumpu pada sisi bahasa (Fase 5).

### Fase 3. Cek literatur (mulai sekarang, wajib selesai sebelum Fase 4)

- Baca langsung paper sumber, bukan ringkasan LLM:
  - *steering*: YOPO, SHIFT, Kawada & Kellis, CANOE, ContextFocus, ITI, CAA, Orgad dkk.;
  - efek popularitas entitas dan konflik antara pengetahuan konteks dan parametrik;
  - metrik homogenisasi dan *knowledge collapse*;
  - konsistensi pengetahuan lintas bahasa.
- **Keluaran:** celah kebaruan yang tegas. Kandidat saat ini: perbandingan langsung tiga bentuk otoritas (saran, veto, intervensi) dengan sinyal yang sama, pada subset "*evidence* lengkap tetapi salah". Jika YOPO atau paper lain sudah melakukannya, kandidat ini gugur.

### Fase 4. Studi 4: intervensi *hidden state* (pre-registered)

- **Populasi:** `full` yang salah (target pemulihan), `full` yang benar (ukur kerusakan), dan `drop_*` (pastikan halusinasi tidak naik ketika *evidence* memang kurang).
- **Lengan:** `off`; saran; veto (σ < 0,5); *steering* yang dipicu σ; *steering* dengan arah acak (kontrol); *steering* selalu aktif.
- **Arah *steering*:** selisih rata-rata aktivasi (gaya CAA) antara kasus benar dan salah pada `full`. Lapisan dan kekuatan dipilih di split latih/validasi, lalu dikunci sebelum uji.
- **Metrik:** laju pemulihan (salah → benar), laju kerusakan (benar → salah), halusinasi pada `drop_*`, dan *false refusal*.
- **Catatan teknis:** Gemma via Ollama tidak menyediakan *hidden state*. *Steering* pada Gemma butuh bobot HF (kemungkinan 4-bit agar muat di 8 GB). Mulai dari Qwen 3B.

### Fase 5. Studi 5: multibahasa

- **Bahasa:** Inggris, Indonesia, dan satu bahasa sumber daya rendah (kandidat: Jawa atau Sunda, tergantung ketersediaan data).
- **Data:** cari dulu dataset QA multi-hop multibahasa yang ada (Fase 3). Jika tidak ada, terjemahkan subset HotpotQA dengan pemeriksaan manusia pada sampel, sambil mewaspadai artefak terjemahan.
- **Model:** Qwen2.5, Gemma (HF), dan satu model yang kuat di bahasa Asia Tenggara (cek ketersediaan).
- **Pertanyaan:**
  - Apakah kecukupan *evidence* tetap terbaca di *hidden state* per bahasa, termasuk apakah *head* yang dilatih dalam bahasa Inggris bisa dipakai lintas bahasa?
  - Apakah jarak antara "terbaca" dan "dipakai", serta laju penolakan, lebih besar di bahasa sumber daya rendah?
  - Apakah *steering* membantu secara merata?

## 4. Perkiraan jadwal

| Minggu (mulai 14 Okt 2026) | Pekerjaan |
| --- | --- |
| 1–2 | Fase 1 dan Fase 2 (data yang ada); Fase 3 dimulai |
| 2–3 | Fase 3 selesai; keputusan arah; pre-registrasi Studi 4 |
| 3–6 | Studi 4 (Qwen 3B), lalu replikasi pada model kedua jika memungkinkan |
| 6–12 | Studi 5 (multibahasa) |

Target ARR ACL 2027 (4 Jan 2027) tidak dijadikan patokan, sesuai arahan dosen. Tema ACL dipakai sebagai pembingkaian.

## 5. Risiko

- **Kebaruan *steering* tipis.** YOPO dan SHIFT sudah dekat. Mitigasi: Fase 3 sebelum Fase 4, dan bingkai sebagai perbandingan bentuk otoritas, bukan metode *steering* baru.
- **Kasus "tahu tapi tidak mengungkap" sedikit.** Hasil ini tetap temuan, dan arah bergeser ke Fase 2 dan 5.
- **Efek *steering* bergantung model** (Kawada & Kellis). Butuh minimal dua keluarga model sebelum menarik kesimpulan umum.
- **Artefak terjemahan** pada Studi 5.
- **Ide kerangka ini disusun dengan bantuan LLM.** Setiap klaim kebaruan harus diverifikasi sendiri dari paper sumber.

## 6. Status per 17 Oktober 2026

| Fase | Status | Hasil utama | Dokumen |
| --- | --- | --- | --- |
| 1 Diagnosis | Selesai (eksploratif) | Pengetahuan hampir seluruhnya dari konteks; 48% halusinasi "nyaris" (emas 5 besar); 61% memilih entitas lain dari paragraf emas. Kriteria K1 primer cacat (dicatat) | 12, `07_analysis/diagnosis/summary.md` |
| 1b Probe | Selesai (eksploratif) | **"Tahu tapi tidak mengungkap" didukung:** *probe* mengurutkan emas di atas jawaban salah pada 69% kasus vs *decoy* 10%; K_internal − K_eksternal +0,24 | 14, `probe_summary.md` |
| 2 Popularitas | Selesai (eksploratif) | *Gate* tidak menolak entitas jarang lebih sering. Halusinasi justru naik pada entitas populer (16% → 41%) | 12, `summary.md` |
| 3 Literatur | Selesai tahap 1 | YOPO dan Lu dkk. dekat; ruang yang tersisa: tangga otoritas dengan nilai sinyal identik + plasebo, kegagalan alami multi-hop, bahasa | 13 |
| 4 Studi 4 | **Draf** pre-registrasi | Menunggu tinjauan dan diskusi dengan pembimbing | 17 |
| 5a Lintas bahasa | Selesai (pilot) | *Evidence* non-Inggris: benar −19 poin; σ terurut tetapi kalibrasinya runtuh, sehingga *gate* menolak 68% *evidence* lengkap (EN 23%) | 15, 16, `07_analysis/xling/summary.md` |
| 5b Monolingual ID | Belum | Perlu terjemahan sendiri | 15 |

**Pembaruan (17 Okt, sore):**
- *Decoy* ketat: emas peringkat 1 di antara semua judul paket pada 65% (peluang acak 15%).
- Replikasi *probe*: didukung pada 7B; sebagian pada 1.5B.
- Pilot *steering* pada *dev*: L24 α2, halusinasi → benar 8,5%, arah acak 0%.
- Draf Studi 4 direvisi (§9): H4.1 diganti, ukuran sampel ±1.700 item.
