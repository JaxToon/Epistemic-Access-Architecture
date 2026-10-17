# DRAF Pre-registrasi Studi 4: Tangga Otoritas (Saran, Veto, Intervensi)

Status: **DRAF, belum dikunci.** Wajib ditinjau (*methodology review*) dan dibahas dengan pembimbing sebelum data uji dilihat. Ditulis 17 Oktober 2026, berdasarkan hasil eksploratif Fase 1, 1b, 2, dan 5a (research log 17 Okt) serta cek literatur (dokumen 13).

## 1. Pertanyaan

Dengan sinyal kecukupan σ yang **identik**, bentuk otoritas mana yang memulihkan jawaban benar pada kegagalan alami ketika *evidence* multi-hop lengkap?

- **Saran:** nilai σ ditulis di *prompt*.
- **Veto:** σ < τ → jawaban ditahan.
- **Intervensi:** σ ≥ τ → *hidden state* digeser ke arah "pakai *evidence*".

Hasil Fase 1b menunjukkan bahwa pada sekitar 69% halusinasi dengan *evidence* lengkap, *hidden state* lebih menyukai jawaban emas daripada jawaban yang dikeluarkan. Hasil itu eksploratif. Studi ini menguji secara konfirmatori apakah pengetahuan internal tersebut bisa dimunculkan.

## 2. Data

- **Pengembangan (*dev*):** 396 item Studi 2/3 yang sudah ada. Dipakai untuk memilih arah *steering*, lapisan, dan kekuatan, serta melatih *probe* K1. **Tidak** dipakai untuk uji.
- **Uji:** sampel baru dari HotpotQA dev (*distractor*), seed baru, tanpa tumpang-tindih dengan item pilot, Studi 2, atau Studi 3. Ukuran sampel ditentukan dari analisis daya (§6).
- Kondisi `full` (target pemulihan) dan `drop_ans` (cek bahwa intervensi tidak menaikkan halusinasi ketika *evidence* kurang). *Prompt* ekstraktif yang sama.

## 3. Lengan (Qwen2.5-3B, *greedy*)

| Lengan | Deskripsi |
| --- | --- |
| `off` | Tanpa sinyal |
| `advice` | σ di *prompt* (teks Studi 3) |
| `placebo` | Teks sama, σ diacak antar item |
| `veto` | `off` dengan σ < 0,5 → INSUFFICIENT EVIDENCE |
| `steer_σ` | Intervensi hanya jika σ ≥ 0,5 |
| `steer_rand` | Sama dengan `steer_σ`, tetapi arahnya acak dengan norma sama (kontrol) |
| `steer_all` | Intervensi pada semua item (kontrol pemicu) |

**Intervensi (dikunci di *dev*):** penambahan vektor gaya CAA, α·v, pada aliran residu satu lapisan L di semua posisi generasi. v = selisih rata-rata aktivasi di t₀ antara kasus `full` yang benar dan yang salah di *dev*. L ∈ {18, 21, 24, 27} dan α dari *grid* dipilih di *dev* dengan kriteria: maksimalkan (pulih − rusak) pada `full`, dengan syarat halusinasi@`drop_ans` tidak naik lebih dari 2 poin. Nilai terpilih dicatat sebelum uji. *Opsi yang dipertimbangkan:* arah dari bobot *probe* L27; probe kondisional terlatih ala YOPO (hanya sebagai pembanding, bukan kontribusi).

## 4. Hipotesis (draf)

- **H4.1 (pemulihan):** di antara item yang salah pada `off` @`full`, laju pulih (menjadi benar) `steer_σ` > `advice`.
- **H4.2 (kontrol arah):** laju pulih `steer_σ` > `steer_rand`.
- **H4.3 (manfaat bersih):** U(λ = 2) = benar − 2·halusinasi: `steer_σ` > `veto`.
- **H4.4 (prediksi Lu dkk. 2026):** laju pulih pada kasus K1 (*probe* *dev* L27 mengurutkan emas di atas *greedy*) > pada kasus non-K1.
- **H4.5 (biaya):** laju rusak (benar → tidak benar) `steer_σ` tidak lebih dari 5 poin; halusinasi@`drop_ans` `steer_σ` − `off` tidak lebih dari +2 poin (TOST).

## 5. Analisis

Uji berpasangan per item (McNemar *exact* untuk proporsi berpasangan), *bootstrap* item 2.000× untuk IK 95%, dan koreksi Holm atas H4.1–H4.4. Label kebenaran memakai aturan + *judge* Qwen2.5-7B, dengan audit kasus ambigu seperti Studi 3. Analisis sensitivitas memakai label ketat.

## 6. Ukuran sampel (perlu dihitung)

Dari Studi 3: ±28% item salah pada `off` @`full` (71/255) di populasi utama. Jika pemulihan `steer_σ` sekitar 20% dan `advice` sekitar 2%, dibutuhkan sekitar 60 item salah untuk daya 0,8 (McNemar). Itu berarti sekitar 250 item utama, atau ±400 item sampel. **Angka ini perlu dihitung ulang** setelah efek di *dev* diketahui.

## 7. Replikasi

Model kedua dari keluarga lain (Gemma via bobot HF, 4-bit). Efek *steering* bergantung model (Kawada & Kellis 2026). Jika tidak muat di 8 GB, gunakan Qwen2.5-1.5B dan 7B sebagai replikasi ukuran, dengan keterbatasan dicatat.

## 8. Yang perlu diputuskan sebelum dikunci

1. Arah intervensi: CAA t₀ vs arah *probe* vs keduanya (multiplisitas).
2. Ambang τ = 0,5 tetap, atau disesuaikan dengan cakupan.
3. Apakah lengan multibahasa (*evidence* XL) dimasukkan. Fase 5a menunjukkan kalibrasi σ runtuh lintas bahasa, sehingga pemicu σ ≥ 0,5 jarang aktif di XL. Ini justru bisa menjadi uji tersendiri.
4. Tinjauan metodologi (*confound*, kebocoran *dev*/uji, kriteria pemilihan α).

## 9. Masukan dari pilot *dev* (17 Okt 2026; rencana 18 §C; `07_analysis/steer_dev/summary.md`)

- **Konfigurasi terpilih dengan kriteria pra-tetap: L24, α = 2** (CAA selisih rata-rata, *cross-fit* 2 lipatan).
  - Pulih (tidak benar → benar) 10,8%; halusinasi → benar 8,5%; rusak 4,0%; Δbenar +3,5 poin; Δabstain −3,5; Δhalusinasi@`drop_ans` +1,2.
  - Dengan pemicu σ: hampir sama (pulih 9,2%, rusak 3,2%).
- **Kontrol arah acak** (norma sama): pulih 0%, rusak 8,8%. Efeknya spesifik pada arah.
- **Pratinjau H4.4:** pulih pada halusinasi K1 6/49 = 12,2% vs non-K1 0/22. Pada L24 α = 4: 20,4% vs 4,5%. Arahnya sesuai prediksi Lu dkk., tetapi n kecil.
- **Arah tidak stabil:** kosinus antara arah dua lipatan hanya −0,17 sampai 0,23, dan norma arah 2–9% dari norma *hidden state*. Selisih rata-rata benar vs salah lintas item sebagian besar menangkap perbedaan topik. Pertimbangkan arah dari kontras **di dalam item** atau arah *probe*.
- **Revisi yang diperlukan:**
  1. **H4.1 harus diganti menjadi "halusinasi → benar"**, bukan "tidak benar → benar". Di Studi 3, saran (17/130) dan plasebo (15/130) sudah "memulihkan" 11–13% item tidak benar, hampir seluruhnya karena abstain → menjawab. Dengan definisi lama, H4.1 akan gagal walaupun *steering* bekerja.
  2. **Ukuran sampel:** simulasi McNemar (*steer* vs saran 1,4%) memberi daya 0,78 pada 150 halusinasi jika efek 8,5%, dan 0,83 pada 300 halusinasi jika efek 6%. Efek *dev* terkena *winner's curse* (dipilih dari 16 konfigurasi), jadi rencanakan sekitar 300 halusinasi, atau ±1.700 item sampel. **Kumpulan uji 600 item tidak cukup**; perlu diperbesar sebelum dikunci.
  3. Laporkan *net benefit* (benar − 2·halusinasi) sebagai uji utama alternatif, karena lebih stabil daripada proporsi pulih.
