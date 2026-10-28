# Rencana Analisis Fase 5b: *Evidence* dan Pertanyaan Monolingual Bahasa Indonesia (Pilot)

Ditulis 28 Oktober 2026, **sebelum** terjemahan dibuat. Status: pilot eksploratif. Latar: masukan Pak Alfan P4 (multibahasa) dan hasil Fase 5a (dokumen 16). Fase 5a memakai paket campuran bahasa. Fase 5b menguji kondisi yang lebih bersih: **seluruh** paket dan pertanyaan dalam bahasa Indonesia.

## Desain

- **Item dan kondisi:** sama dengan Fase 5a. 396 item Studi 2/3, `full` (`length`) dan `drop_ans` (`entity_poor`), pelaporan pada populasi utama.
- **Penerjemahan:** setiap judul unit, kalimat unit, dan pertanyaan diterjemahkan ke bahasa Indonesia oleh Gemma 4 E4B (Ollama lokal, temperatur 0, seed 0). Instruksi: terjemahkan ke bahasa Indonesia, pertahankan nama orang, tempat, judul karya, dan angka sebagaimana lazim dalam bahasa Indonesia, keluarkan terjemahannya saja. Setiap string unik diterjemahkan sekali dan di-*cache*.
  - Penerjemah sengaja **berbeda** dari model yang diuji (Qwen), supaya model tidak "membaca terjemahannya sendiri".
- **Lengan:**
  - **EN\***: identik dengan Fase 5a, dijalankan ulang (*greedy*, jadi deterministik).
  - **ID**: pertanyaan dan semua unit dalam bahasa Indonesia. Instruksi templat tetap bahasa Inggris, termasuk "...in English", sama dengan Fase 5a, supaya yang berubah hanya bahasa isi.
- **σ** dari *head* yang dilatih dalam bahasa Inggris. **Label:** aturan + *judge* Qwen2.5-7B.

## Ukuran

Sama dengan Fase 5a, dengan kontras **ID − EN\***:
- benar@`full`, halusinasi@`full`, abstain@`full`;
- halusinasi@`drop_ans`;
- akurasi berpasangan σ(`full` > `drop_ans`);
- penolakan oleh *gate* @`full`;
- rata-rata σ@`full`.

*Bootstrap* item 2.000×, IK 95%.

## Cek kualitas terjemahan (dilaporkan sebelum hasil utama)

1. **Kelestarian jawaban:** proporsi item jawaban non-ya/tidak yang string jawaban emasnya (dinormalisasi) masih muncul di paket ID `full`, dibandingkan dengan EN. Item yang jawabannya hilang karena terjemahan dilaporkan terpisah. Kontras utama juga dihitung ulang pada item yang jawabannya lestari (sensitivitas).
2. **Sampel audit manusia:** 40 pasang kalimat acak (seed tetap) ditulis ke `07_analysis/idmono/audit_sample.csv` untuk diperiksa penutur asli (peneliti). Diberi nilai: benar / ada kesalahan makna / nama atau angka berubah.

## Keterbatasan yang sudah diketahui

- Terjemahan mesin model kecil. Kesalahan bisa berasal dari terjemahan, bukan dari pemakaian pengetahuan oleh model.
- Gold tetap bahasa Inggris, dan model diminta menjawab dalam bahasa Inggris. Jadi kondisi ID tetap menuntut terjemahan balik untuk nama.
- Satu model yang diuji (Qwen2.5-3B).
