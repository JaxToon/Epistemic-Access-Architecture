# Rencana Analisis: *Decoy* Ketat, Replikasi *Probe*, dan Pilot *Steering* pada *Dev*

Ditulis 17 Oktober 2026, **sebelum** salah satu bagian di bawah dijalankan. Status: eksploratif. Bagian C memakai data *dev* Studi 4 (item Studi 2/3), yang memang dicadangkan untuk penyetelan; data uji Studi 4 belum diambil.

## A. *Decoy* ketat (Fase 1b, Qwen 3B)

- **Kandidat *decoy* ketat:** semua judul unit dalam paket `full` item itu (judul paragraf penghubung, judul paragraf jawaban, dan judul pengecoh), setelah duplikat dibuang. Dikecualikan: judul yang sama dengan, memuat, atau termuat dalam jawaban emas (setelah normalisasi), serta judul yang sama dengan jawaban *greedy*. Judul adalah entitas yang relevan secara topik dan muncul di *evidence*, jadi pesaing yang jauh lebih masuk akal daripada emas dari soal lain.
- **Skor:** *probe* L27 dari lipatan *cross-fit* item tersebut; tidak pernah dilatih pada *decoy*.
- **Uji (71 kasus halusinasi):**
  - A1: proporsi item dengan emas berada di peringkat 1 di antara {emas, *greedy*, semua *decoy* ketat}, dibandingkan peluang acak (rata-rata 1/n kandidat per item);
  - A2: proporsi item dengan *decoy* ketat terbaik > *greedy*;
  - hal yang sama untuk skor eksternal.
- **Interpretasi:** temuan Fase 1b dianggap kuat jika A1 jelas di atas peluang acak (IK Wilson tidak memuat rata-rata peluang).

## B. Replikasi *probe* pada Qwen2.5-1.5B dan 7B (4-bit)

- Data: keluaran Studi 2 ekstraktif @`full` untuk masing-masing model, diberi label dengan aturan + *judge*.
- Prosedur identik dengan Fase 1b: *greedy* + 10 sampel + emas + *decoy* (emas soal lain), *cross-fit* 5 lipatan, dilatih hanya pada kandidat buatan model.
- Lapisan proporsional dengan 3B: 0,5 / **0,75 (primer)** / 0,92 / 1,0 dari kedalaman. Untuk 28 lapisan: 14 / **21** / 26 / 28.
- Dilaporkan: Uji 1 (K_internal − K_eksternal), Uji 2 (emas > *greedy* salah), dan kontrol *decoy*.

## C. Pilot *steering* pada *dev* (Qwen 3B)

- **Item:** 255 item utama Studi 2/3, `full` (`length`) dan `drop_ans` (`entity_poor`), *prompt* ekstraktif yang sama dengan `off`.
- **Arah (cross-fit 2 lipatan menurut item, seed tetap):** untuk item di lipatan k, v_L = rata-rata h_L(t₀) kasus `full` benar − rata-rata h_L(t₀) kasus `full` halusinasi, keduanya dihitung dari lipatan lain. Arah tidak pernah dihitung dari item yang sedang diuji.
- **Intervensi:** tambahkan α·v_L pada keluaran lapisan L di semua posisi (*prompt* dan generasi). *Grid*: L ∈ {18, 21, 24, 27} × α ∈ {0,5; 1; 2; 4}.
- **Kontrol:** arah acak dengan norma sama pada konfigurasi terpilih.
- **Ukuran (dibandingkan dengan `off`):**
  - pulih = tidak benar → benar @`full` (juga dilaporkan khusus halusinasi → benar);
  - rusak = benar → tidak benar @`full`;
  - Δabstain@`full`;
  - Δhalusinasi@`drop_ans`.
  - Varian dipicu σ (σ ≥ 0,5 memakai keluaran *steer*, sisanya `off`) dihitung dari keluaran yang sama.
- **Kriteria pemilihan** (akan dipakai di Studi 4): maksimalkan (pulih − rusak) @`full` dengan syarat Δhalusinasi@`drop_ans` ≤ +0,02. Semua konfigurasi dilaporkan.
- **Pratinjau H4.4:** laju pulih pada halusinasi K1 (*probe* L27: emas > *greedy*) vs non-K1.
- **Label:** aturan + *judge* Qwen2.5-7B untuk kasus ambigu baru.
