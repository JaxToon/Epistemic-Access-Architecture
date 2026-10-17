# Rencana Analisis Fase 1b: Pengetahuan Internal vs Eksternal

Ditulis 17 Oktober 2026, **sebelum** sampel kandidat, *hidden state*, atau *probe* dihitung. Status: **eksploratif**. Menggantikan kriteria K1 primer Fase 1 yang cacat (lihat deviasi di dokumen 12). Pendekatannya mengikuti Gekhman dkk. (COLM 2025): model "tahu lebih banyak secara internal" jika penilai berbasis *hidden state* mengurutkan jawaban benar di atas jawaban salah lebih baik daripada distribusi keluaran model sendiri.

## Data dan kandidat

- Item Studi 2/3, kondisi `full`, *prompt* ekstraktif, Qwen2.5-3B-Instruct. Semua 396 item dipakai untuk melatih *probe* (*cross-fitting*). Pelaporan pada populasi utama (255 item).
- **Kandidat per item:**
  - jawaban *greedy* (`off`);
  - 10 sampel (temperatur 1,0, top-p 1,0, maksimum 24 token, seed tetap), duplikat dibuang setelah normalisasi;
  - jawaban emas HotpotQA.
  - Kandidat non-substantif (abstain/non-jawaban) dibuang.
- **Label kandidat:** `evaluate.label` (aturan + *judge cache*). Kandidat ambigu yang belum dinilai *judge* (`judge_missing = 1`) dikeluarkan dari pelatihan dan evaluasi. Jawaban emas berlabel benar.

## Skor

- **Eksternal:** rata-rata log-prob per token kandidat, diberikan *prompt* (*teacher forcing*).
- **Internal:** *probe* logistik (StandardScaler + LogisticRegression, C = 1,0) pada *hidden state* token terakhir kandidat (*teacher forcing* *prompt* + kandidat). Lapisan primer **27**, lapisan sekunder 18, 33, dan 36.
- **Pelatihan *probe*:** hanya kandidat **buatan model** (*greedy* + sampel). Jawaban emas **tidak** dipakai sebagai contoh latih, supaya *probe* tidak belajar gaya penulisan string emas. *Cross-fitting* 5 lipatan menurut item: setiap item dinilai oleh *probe* yang tidak melihat item tersebut.
- **Pembanding permukaan:** regresi logistik pada fitur [panjang token, skor eksternal, kandidat termuat di teks *evidence*], dilatih dan di-*cross-fit* dengan cara yang sama.

## Uji

1. **K_internal vs K_external (ala Gekhman).** Untuk item dengan minimal satu kandidat buatan model yang benar dan satu yang salah: K = proporsi pasangan (benar, salah) yang diurutkan benar. Selisih K_internal − K_external dengan *bootstrap* item 2.000× (IK 95%). Hal yang sama dilakukan untuk K_permukaan.
2. **Kasus halusinasi (71 item, inti pertanyaan Pak Alfan).** Proporsi item dengan skor_internal(emas) > skor_internal(jawaban *greedy* yang salah), beserta IK Wilson. Bandingkan dengan:
   - skor eksternal (diharapkan ≈ 0 karena *greedy*);
   - skor permukaan;
   - acuan pada kelompok **benar**, yaitu proporsi skor_internal(*greedy* = benar) > skor_internal(sampel salah) bila ada.
3. **Tabulasi silang** hasil uji 2 dengan K1 longgar Fase 1 (R_final ≤ 5).

## Interpretasi yang ditetapkan sekarang

- **"Tahu tapi tidak mengungkap" didukung** pada populasi ini jika uji 1 memberi K_internal − K_external > 0 (IK tidak memuat 0) **dan** uji 2 memberi proporsi internal(emas) > internal(*greedy*) yang lebih tinggi daripada pembanding permukaan.
- Jika *probe* tidak lebih baik daripada fitur permukaan, kesimpulannya: tidak ada bukti pengetahuan internal melebihi yang diekspresikan.

## Keterbatasan yang sudah diketahui

- Sebagian string emas HotpotQA tidak berbentuk jawaban. Ini bisa menurunkan skor emas di semua penilai.
- *Probe* linear pada satu lapisan hanya batas bawah dari pengetahuan internal.

## Tambahan sebelum hasil final (17 Okt 2026, setelah uji coba kode)

Uji coba kode (sebelum *judge* menilai 25 kandidat ambigu) menunjukkan *probe* sering mengurutkan emas di atas *greedy* yang salah. Karena itu ditambahkan **kontrol umpan (*decoy*)**, ditetapkan sebelum dijalankan:

- Untuk setiap item halusinasi, ambil jawaban emas dari **item lain** (acak, seed tetap, dari jenis jawaban yang sama: angka/tahun vs bukan angka). Kandidat ini bergaya emas tetapi salah untuk soal tersebut. Skor dengan *probe* yang sama (lipatan *cross-fit* item itu).
- **Uji:** proporsi skor_internal(*decoy*) > skor_internal(*greedy* salah).
- **Interpretasi:** jika proporsi *decoy* mendekati proporsi emas (uji 2), *probe* mendeteksi gaya string emas, dan uji 2 **tidak** dihitung sebagai bukti "tahu tapi tidak mengungkap". Bukti dianggap ada hanya jika emas > *decoy* secara jelas (selisih berpasangan, IK 95% *bootstrap* item tidak memuat 0).
- Hasil final dilaporkan setelah *judge* menilai kandidat ambigu yang tersisa.
