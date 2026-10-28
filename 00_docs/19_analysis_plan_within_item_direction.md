# Rencana Analisis: Arah *Steering* dari Kontras di Dalam Item (Pilot *Dev*)

Ditulis 28 Oktober 2026, **sebelum** dijalankan. Status: eksploratif, memakai data *dev* Studi 4 (item Studi 2/3). Latar: pilot CAA (dokumen 18 §C, 17 §9) menunjukkan efek kecil tetapi spesifik arah (L24 α2: halusinasi → benar 8,5%, arah acak 0%). Kelemahannya, arahnya tidak stabil antar lipatan (kosinus −0,17 sampai 0,23), karena selisih rata-rata **lintas item** ikut menangkap perbedaan topik.

## Arah baru

- **v_L (di dalam item):** rata-rata atas item di lipatan lain dari [h_L(t₀ | `full`) − h_L(t₀ | `drop_ans`)] untuk **item yang sama**. Kebijakan `drop_ans` = `entity_poor`, sama dengan *prompt* yang dipakai.
- Karena topik soal sama di kedua sisi, selisihnya mengisolasi "paragraf jawaban hadir". Prediksi: lebih stabil antar lipatan.
- Hipotesis mekanisme: menambah arah "*evidence* jawaban hadir" mendorong model memakai paragraf jawaban, bukan entitas lain dari paket (61% kesalahan Fase 1).

## Prosedur

- Item, lipatan (seed 20261017, 2 lipatan), *prompt*, generator, label, dan ukuran sama dengan dokumen 18 §C.
- **Kekuatan relatif:** karena norma arah berbeda dari CAA, α ditetapkan supaya ‖α·v_L‖ / rata-rata ‖h_L‖ ∈ {0,025; 0,05; 0,1; 0,2}. Sebagai acuan, CAA L24 α2 ≈ 0,07.
- *Grid*: L ∈ {18, 21, 24, 27} × 4 kekuatan relatif = 16 konfigurasi.
- **Kriteria pemilihan:** sama dengan sebelumnya. Maksimalkan (pulih − rusak) @`full` dengan syarat Δhalusinasi@`drop_ans` ≤ +0,02.
- **Kontrol:** arah acak dengan norma sama pada konfigurasi terpilih.
- **Dilaporkan tambahan:** kosinus arah antar lipatan, dan halusinasi → benar (ukuran utama hasil revisi H4.1).
- **Perbandingan dengan CAA:** halusinasi → benar, rusak, dan Δbenar pada konfigurasi terpilih masing-masing. Keduanya terkena *winner's curse* yang sama (dipilih dari 16).

## Keputusan yang mengikuti

Arah yang dipakai di Studi 4 adalah yang memberi halusinasi → benar lebih tinggi dengan rusak ≤ 5 poin. Jika keduanya setara, pilih yang lebih stabil antar lipatan. Keputusan ini dicatat sebelum pre-registrasi dikunci.

## Hasil dan keputusan (28 Okt 2026)

- **Stabilitas:** kosinus arah antar lipatan 0,87–0,98, jauh di atas CAA (−0,17 sampai 0,23).
- **Efek tanpa pemicu (semua item):** arah ini terutama **mengurangi abstain** (−0,02 sampai −0,23) dan **menaikkan halusinasi@`drop_ans` sangat besar** (sampai +0,55 pada L24 r0,2). Halusinasi → benar hanya besar pada kekuatan tinggi (L18 r0,2: 18%, dengan Δhalusinasi@`drop_ans` +0,19).
- **Tafsiran mekanistik:** arah ini adalah arah "*evidence* cukup", bukan "pakai *evidence* dengan benar". Mendorongnya membuat model menjawab, termasuk ketika *evidence* kurang. Jadi **representasi kecukupan yang dibaca σ secara kausal mengendalikan keputusan menjawab/menolak.** Ini dukungan intervensional untuk klaim bahwa sinyal itu ada di dalam model, tetapi tidak dipakai sebagai otoritas.
- **Dengan pemicu σ (hanya jika σ ≥ 0,5):** efek samping pada `drop_ans` tertahan (≤ +0,035). Contoh L21 r0,1: pulih 20%, halusinasi → benar 9,9%, **rusak 0%**, **Δbenar +10,2 poin**, Δhalusinasi@`drop_ans` +0,031, sedikit melewati batas +0,02.
- **Konfigurasi terpilih sesuai kriteria pra-tetap:** W_L21_r0,025 (pemicu σ). Pulih 6,2%, tetapi halusinasi → benar hanya 1,4%. Kriteria (pulih − rusak) ternyata lebih menghargai abstain → menjawab daripada halusinasi → benar. Ini kelemahan kriteria, dicatat untuk Studi 4.
- **Keputusan (aturan dokumen 19):** bandingkan halusinasi → benar pada konfigurasi terpilih masing-masing, dengan syarat rusak ≤ 5 poin. CAA L24 α2 = 8,5% (rusak 4,0) vs di dalam item 1,4%. **Studi 4 memakai CAA L24 α2.**
- **Catatan untuk diputuskan peneliti:** σ + arah di dalam item (L21 r0,1) menunjukkan manfaat bersih terbesar yang pernah terlihat di *dev*. Konfigurasi ini dipilih **setelah** melihat hasil, jadi hanya boleh masuk Studi 4 sebagai **lengan eksploratif** (deskriptif, di luar Holm), atau diuji sebagai hipotesis baru di studi berikutnya.
