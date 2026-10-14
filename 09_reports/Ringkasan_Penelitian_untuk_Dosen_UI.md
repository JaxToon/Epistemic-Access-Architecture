# Ringkasan Penelitian: Otoritas Epistemik dan Halusinasi pada Model Bahasa Besar

## Ringkasan

Penelitian awal ini menunjukkan bahwa model bahasa kecil sebenarnya "tahu" kapan *evidence*-nya tidak cukup, tetapi pengetahuan itu tidak mengendalikan apakah model tetap menjawab.

Saya memanipulasi secara terkontrol "kanal" *evidence* antara *reader* dan *generator* pada HotpotQA, menggunakan Qwen2.5 berukuran 1.5B, 3B, dan 7B. Seluruh studi didaftarkan lebih dahulu (*pre-registered*), lengkap dengan kriteria kegagalannya. Ada tiga temuan utama:

1. **Jawaban yang tetap diberikan sebagian besar salah.** Ketika paragraf jawaban dihapus, proporsi jawaban yang salah di antara jawaban yang diberikan (*selective risk*) naik dari 0,19–0,36 menjadi 0,75–0,84 pada ketiga ukuran model.
2. **Jawaban karangan disusun dari evidence yang tersisa.** Sebanyak 74–84% jawaban karangan berasal dari teks *evidence* yang masih ada, bukan dari ingatan model.
3. **Sinyal kecukupan evidence hanya berpengaruh jika diberi otoritas.** Sinyal ini dapat dibaca dari *hidden state* model dengan akurasi berpasangan 0,99. Jika hanya disampaikan sebagai saran di *prompt*, efeknya setara dengan plasebo. Jika diberi wewenang sebagai *gate*, halusinasi turun dari 22,6% menjadi 9,3%, tetapi laju menjawab juga turun dari 35% menjadi 18%. Pada laju menjawab yang sama, keunggulannya atas penolakan acak sekitar 2,4 poin, dan penolakan atas soal yang sebenarnya dapat dijawab jauh lebih sedikit dibandingkan metode standar. Pola ini dikonfirmasi pada 400 soal baru dan pada model Gemma (Studi 3, pra-registrasi).

Ini adalah riset mandiri yang saya kerjakan atas rasa ingin tahu pribadi, bukan bagian dari program studi. Dokumen ini saya siapkan untuk memohon pendapat Bapak/Ibu sebagai orang yang lebih ahli atas arah penelitian, terutama atas gagasan lanjutan tentang **kapan model sebaiknya berhenti menghasilkan jawaban**.

## Latar belakang dan pertanyaan penelitian

Pertanyaan yang menjadi titik tolak: **jika model sebenarnya memiliki pengetahuan yang relevan, mengapa ia tetap mengarang?**

Gagasan awal terinspirasi secara fungsional dari penelitian *split-brain*. Pada pasien *split-brain*, sistem verbal tetap menyusun penjelasan yang koheren walaupun tidak memiliki akses ke informasi yang sebenarnya memicu perilaku. Analogi ini hanya saya gunakan sebagai inspirasi (spesialisasi, kanal komunikasi terbatas, narasi dari informasi parsial). Saya tidak mengklaim bahwa LLM bekerja seperti otak.

**Titik berangkat: eksperimen *split-brain*.** Penelitian ini berawal dari eksperimen klasik pada pasien yang *corpus callosum*-nya, penghubung kedua belahan otak, dipotong untuk mengobati epilepsi berat. Penelitian manusianya dipelopori Roger Sperry bersama Joseph Bogen dan Michael Gazzaniga sejak 1960-an. Sperry menerima Hadiah Nobel Fisiologi atau Kedokteran 1981 ([Sandrone, *J. Neurol.* 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9363358/)).

- **Caranya.** Pasien menatap titik di tengah, lalu gambar ditampilkan sekilas di bidang pandang kiri atau kanan. Yang dipisah adalah *bidang pandang*, bukan mata. Informasi dari bidang pandang kiri masuk ke belahan otak kanan, dan sebaliknya.
- **Eksperimen "cakar ayam dan salju".** Pasien P.S. melihat cakar ayam di bidang pandang yang terhubung ke belahan kiri (yang dapat berbicara) dan pemandangan salju di bidang pandang yang terhubung ke belahan kanan. Tangan kirinya memilih gambar sekop salju, tangan kanannya memilih ayam.
- **Penjelasan yang dikarang.** Ketika ditanya alasannya, P.S. langsung menjawab: "Cakar ayam cocok dengan ayam, dan kita butuh sekop untuk membersihkan kandang ayam." Belahan otak yang berbicara tidak pernah melihat salju, tetapi tetap menyusun penjelasan yang masuk akal dari informasi yang dimilikinya. Gazzaniga menyebut fungsi ini *left-hemisphere interpreter* ([Volz & Gazzaniga, *Brain* 2017](https://academic.oup.com/brain/article/140/7/2051/3892700); uraian lengkap dalam Gazzaniga & LeDoux, *The Integrated Mind*, 1978).

Pertanyaan saya: apakah LLM melakukan hal serupa, yaitu menyusun jawaban yang koheren ketika *evidence* kunci tidak sampai ke bagian yang menghasilkan jawaban? Temuan 2 menunjukkan pola yang mirip: ketika paragraf jawaban dihapus, model merakit jawaban dari paragraf relevan yang tersisa, seperti "kandang ayam" pada P.S. Kemiripan ini saya perlakukan sebagai analogi fungsional saja. Tinjauan modern juga mengingatkan bahwa integrasi kedua belahan otak tidak sepenuhnya terputus pada pasien *split-brain*.

Penelusuran literatur menunjukkan bahwa klaim umum "pengetahuan yang dimiliki ≠ pengetahuan yang diekspresikan" sudah dibuktikan (Gekhman dkk., COLM 2025). Arsitektur bergaya *split-brain* untuk LLM juga sudah diusulkan secara konseptual tanpa eksperimen (Neural Arbitration Framework, 2026; makalah kerja tanpa peer review). Karena itu fokus penelitian saya geser ke hal yang dapat diuji secara kausal. Data kemudian menggeser fokus itu sekali lagi, dari *akses* ke *otoritas*:

- **RQ1 (akses):** apakah memotong kanal *evidence* antara *reader* dan *generator* secara kausal menaikkan halusinasi?
- **RQ2 (mekanisme):** dari mana materi jawaban karangan berasal ketika akses diblokir?
- **RQ3 (otoritas):** apakah sinyal kecukupan *evidence* yang sama berbeda efeknya ketika diberikan sebagai saran dibandingkan sebagai keputusan yang mengikat?

## Metode

Setiap soal diuji terhadap dirinya sendiri dalam beberapa kondisi. Antarkondisi, yang berubah hanya paragraf mana yang sampai ke *generator*.

- **Data.** HotpotQA (*distractor setting*). Setiap soal membutuhkan tepat dua paragraf emas. Pilot memakai 500 soal (311 masuk populasi utama); Studi 2 memakai 400 soal baru (255 populasi utama).
- **Model.** Qwen2.5-Instruct ukuran 1.5B, 3B, dan 7B (7B dalam kuantisasi 4-bit), *greedy decoding*, pada satu GPU laptop 8 GB.
- **Manipulasi kanal.** Paragraf emas dihapus utuh dan diganti, di posisi yang sama, dengan kalimat pengecoh yang panjang token-nya setara (rasio panjang 0,99–1,00).

| Kondisi | Yang sampai ke *generator* |
| --- | --- |
| `full` | kedua paragraf emas |
| `drop_ans` | paragraf penghubung saja; jawaban tidak ada di teks |
| `drop_other` | paragraf jawaban saja; rantai penalaran terputus |
| `drop_all` | tidak ada paragraf emas |

- **Sinyal epistemik.** Sinyal ini dibandingkan dalam dua bentuk:
  - verdict "cukup/tidak cukup" dari *reader* berbasis *prompt*;
  - skor σ dari *head* kecil (3,4 juta parameter) yang membaca *hidden state* model beku dan representasi tiap kalimat *evidence*. Cara melatih dan memakainya diuraikan pada bagian berikutnya.

  Kedua sinyal diberikan sebagai saran di *prompt* atau sebagai *gate* yang mengikat.
- **Metrik.**
  - Halusinasi: jawaban substantif yang salah.
  - *Selective risk*: halusinasi dibagi jumlah jawaban substantif.
  - *False refusal*: menolak menjawab padahal *evidence* lengkap.
  - AURC: area di bawah kurva *risk–coverage*.
- **Pengaman metodologis.**
  - Hipotesis dan kriteria kegagalan ditulis sebelum data dilihat; setiap deviasi dicatat beserta alasannya.
  - Uji berpasangan per soal (McNemar *exact*), *bootstrap* per soal untuk interval kepercayaan, dan koreksi Holm.
  - Desain ditinjau ulang sebelum setiap studi. Tiga putaran tinjauan menemukan masalah, misalnya kebocoran jawaban lewat judul paragraf, dan semuanya diperbaiki sebelum data dilihat.
  - Label kebenaran bertingkat: aturan untuk kasus yang jelas, audit per soal untuk 379 kasus ambigu, serta *LLM judge* dan label ketat sebagai analisis sensitivitas.

## Cara melatih *head* σ dan memakainya saat *inference*

Prinsipnya: bobot Qwen2.5-3B dibekukan dan tidak pernah diubah. Yang dilatih hanya sebuah *head* kecil, dengan *supervised learning* biasa. Labelnya diketahui dari cara paket *evidence* dibuat, bukan dari jawaban model. Kodenya ada di `eaa/eag/` (`build_train.py`, `features.py`, `model.py`, `train.py`).

```
paket evidence + pertanyaan ──► Qwen2.5-3B (beku, 1 forward pass, tanpa generate)
                                   │
              ┌────────────────────┼─────────────────────┐
              ▼                    ▼                     ▼
   h: state posisi terakhir   M: tiap kalimat evidence   (qv: pertanyaan saja,
   lapisan 18, 27, 36         di-rata-rata, lapisan 22    hanya varian pembanding)
              │                    │
              └──────► head 3,4 juta parameter ──► logit ──► σ = sigmoid(logit)
```

### Langkah 1. Membuat data latih kontrafaktual

- **Sumber.** 7.000 soal acak (seed tetap) dari HotpotQA *train*: 6.000 untuk latih dan 1.000 untuk validasi. Soal uji diambil dari HotpotQA *dev*, sehingga tidak ada soal uji yang ikut dilatih. Sebanyak 6.931 soal lolos; sisanya tidak dapat dibuatkan pengecoh dengan panjang token yang setara.
- **Empat paket per soal.** Setiap soal dirakit menjadi empat paket (`full`, `drop_ans`, `drop_other`, `drop_all`) dengan cara yang sama persis seperti saat uji. Hasilnya 27.724 paket. Setiap paket dibungkus dengan *prompt generator* yang sama dengan saat uji, tanpa teks saran.
- **Label.** y = 1 hanya untuk `full`, dan y = 0 untuk tiga kondisi lainnya. Label ini benar menurut konstruksi HotpotQA, karena setiap soal membutuhkan kedua paragraf emas. Model tidak perlu menjawab apa pun untuk memperoleh label.
  - Versi awal memakai label "string jawaban ada di paket". Label itu saya ganti sebelum melihat hasil uji, karena memberi nilai 1 pada paket yang memuat kandidat jawaban tetapi kehilangan paragraf penghubung. Padahal kondisi itulah pola halusinasi *multi-hop*.
- **Kondisi yang ditahan.** Semua paket `drop_other` dikeluarkan dari data latih maupun validasi. Kondisi ini baru dipakai saat uji, untuk melihat apakah *head* mengenali kekurangan *evidence* yang belum pernah dilihatnya.
- **Ukuran akhir.** 17.835 paket latih (5.945 soal × 3 kondisi) dan 2.958 paket validasi.

### Langkah 2. Mengekstrak fitur dari model beku (sekali saja)

Setiap paket dijalankan sekali melalui Qwen2.5-3B (fp16) hanya sampai akhir *prompt*, tepat sebelum token jawaban pertama. Tidak ada teks yang dihasilkan. Dari satu *forward pass* itu diambil:

| Fitur | Isi | Ukuran |
| --- | --- | --- |
| h | *Hidden state* pada posisi terakhir *prompt*, yaitu state yang akan mengeluarkan token jawaban pertama. Diambil dari lapisan 18, 27, dan 36 (dari 36 lapisan). | 3 × 2.048 |
| M | Setiap baris *evidence* "[eK] (judul) teks" diringkas menjadi rata-rata *hidden state* token-tokennya di lapisan 22. Karena *evidence* terletak sebelum pertanyaan dan atensi bersifat kausal, M belum "melihat" pertanyaan. | k × 2.048 (k = jumlah kalimat) |
| qv | Pertanyaan saja, dalam *forward pass* terpisah tanpa *evidence*, di-rata-rata di lapisan 22. Hanya dipakai varian pembanding `qe`. | 2.048 |

Semua fitur disimpan dalam fp16 (1,2 GB untuk 27.724 paket). Sesudah tahap ini, pelatihan tidak lagi menyentuh LLM.

### Langkah 3. Arsitektur *head*

Alur hitung varian utama (`eag`):

1. h (3 × 2.048 = 6.144 angka) dinormalisasi (LayerNorm) lalu diproyeksikan ke 256 dimensi. Hasilnya menjadi *query*.
2. Ke *query* ditambahkan vektor q0 berukuran 256 yang ikut dilatih. Komponen ini ditambahkan setelah uji sintetis menunjukkan bahwa *head* lambat belajar jika *query* hanya berasal dari h.
3. Setiap kalimat *evidence* M_i dinormalisasi lalu diproyeksikan menjadi *key* K_i dan *value* V_i (masing-masing 2.048 → 256).
4. *Cross-attention* satu kepala: a_i = softmax(*query* · K_i / √256) atas semua kalimat *evidence*, lalu c = Σ a_i V_i. Secara intuitif, state yang akan menjawab "mencari" kalimat *evidence* yang ia butuhkan.
5. Vektor gabungan [*query*, c, *query* ⊙ c, max a_i, entropi a] (770 angka) masuk ke MLP 770 → 256 → GELU → *dropout* 0,1 → 1. Keluarannya adalah *logit*.
6. σ = sigmoid(*logit*).

| Komponen | Jumlah parameter |
| --- | --- |
| LayerNorm + proyeksi h (6.144 → 256) | 1.585.408 |
| LayerNorm + proyeksi *key* dan *value* kalimat *evidence* | 1.053.184 |
| LayerNorm + proyeksi pertanyaan (hanya dipakai varian `qe`) | 528.640 |
| *Query* global q0 | 256 |
| MLP akhir | 197.633 |
| **Total** | **3.365.121** (≈ 0,1% dari Qwen2.5-3B) |

Catatan kejujuran: angka 3,4 juta adalah ukuran modul yang dibuat. Pada varian `eag`, proyeksi pertanyaan tidak dipakai dan tidak menerima gradien, sehingga parameter yang benar-benar dilatih sekitar 2,84 juta.

### Langkah 4. Fungsi *loss* dan optimasi

$$
\mathcal{L} = \text{BCE}(\text{logit}, y) \;+\; \lambda_c \cdot \operatorname{mean}\big[\max\big(0,\; \gamma - (\text{logit}_{\texttt{full}} - \text{logit}_{\texttt{drop\_ans}})\big)\big], \qquad \lambda_c = 1,\; \gamma = 2
$$

- **Suku BCE** mengajarkan *head* memisahkan paket lengkap dari paket yang tidak lengkap.
- **Suku kontrastif (*hinge*)** memasangkan dua paket dari soal yang sama: paket lengkap dan paket yang paragraf jawabannya dihapus. *Logit* paket lengkap harus lebih tinggi minimal γ = 2. Karena kedua paket hanya berbeda pada isi *evidence*, suku ini memaksa *head* membaca isi *evidence*, bukan ciri permukaan soal. Ada 3.545 pasangan, yaitu soal terbuka yang paragraf jawabannya dapat ditentukan secara tunggal. Pasangan ini hanya masuk ke suku *hinge*, sehingga tidak terhitung dua kali di BCE.
- **Optimasi.** AdamW (*learning rate* 10⁻³, *weight decay* 0,01), *batch* 256, maksimum 30 *epoch*, dan *early stopping* dengan *patience* 5 pada BCE validasi. Bobot dengan BCE validasi terendah yang disimpan; dalam praktik itu tercapai pada *epoch* 5–7.
- **Seed dan waktu.** Setiap konfigurasi dilatih dengan tiga seed (0, 1, 2). Dua belas *run* (4 konfigurasi × 3 seed) selesai dalam sekitar 6 menit pada GPU laptop RTX 5050, karena yang dilatih hanya *head* di atas fitur yang sudah tersimpan.

Semua varian memakai data, *loss*, dan prosedur yang sama. Yang berbeda hanya masukannya:

| Varian | Masukan | BCE validasi | AUROC validasi |
| --- | --- | --- | --- |
| `probe` | h saja (MLP, tanpa atensi) | 0,284–0,293 | 0,950–0,953 |
| `qe` | pertanyaan membaca *evidence*, tanpa state *generator* | 0,528–0,551 | 0,825–0,845 |
| `eag` (λ_c = 1) | h membaca *evidence* | 0,238–0,261 | 0,960–0,964 |
| `eag` tanpa *hinge* (λ_c = 0) | sama dengan `eag` | 0,230–0,236 | 0,965–0,968 |

Rentang angka menunjukkan variasi antara tiga seed. σ yang dipakai di semua studi berasal dari `eag` dengan λ_c = 1, sesuai pra-registrasi.

### Langkah 5. Menghasilkan σ untuk masukan baru

1. *Prompt generator* untuk soal dan paket *evidence* baru dirakit seperti biasa.
2. Qwen2.5-3B beku menjalankan satu *forward pass* atas *prompt* itu. Fitur h dan M diambil dengan cara yang sama seperti Langkah 2.
3. Ketiga *head* `eag` (seed 0, 1, 2) dijalankan. σ adalah rata-rata sigmoid dari ketiga *logit*.
4. σ lalu dipakai dalam salah satu dari dua bentuk:
   - **Saran.** Angka σ dituliskan di *prompt*, dan *generator* menjawab dengan bebas.
   - ***Gate*.** *Generator* menjawab seperti biasa. Jika σ < 0,5, jawabannya diganti dengan penolakan; jika tidak, jawaban dikeluarkan apa adanya.

Beberapa hal tentang biaya dan cakupan:

- *Forward pass* untuk σ sama dengan tahap *prefill* yang memang harus dilakukan untuk menjawab. Dalam implementasi saya, tahap ini masih dijalankan terpisah, tetapi pada prinsipnya h dan M dapat diambil dari *prefill* generasi itu sendiri. *Head*-nya sendiri sangat ringan dibandingkan LLM.
- Pada Studi 3 dengan Gemma, σ tetap dihitung dari *hidden state* Qwen. *Gate*-nya kemudian diterapkan pada jawaban Gemma.
- Selama pelatihan, *head* tidak pernah melihat jawaban *generator*. Karena itu σ memperkirakan P(*evidence* cukup), bukan P(jawaban benar). Ini menjelaskan hasil kalibrasi pada bagian "Seberapa jauh matematika dapat mengurangi halusinasi".

## Hasil utama

Temuan yang paling kokoh adalah lonjakan *selective risk* ketika paragraf jawaban dihapus. Lonjakan ini muncul pada ketiga ukuran model dan bertahan di ketiga versi label.

| Model | Halusinasi: `full` → `drop_ans` | *Selective risk* | Jawaban karangan yang disalin dari *evidence* |
| --- | --- | --- | --- |
| Qwen2.5-1.5B | 0,31 → 0,48 (+0,17; IK 95% [0,10; 0,24]) | 0,35 → 0,84 | 74% |
| Qwen2.5-3B | 0,28 → 0,32 (+0,04; tidak signifikan) | 0,36 → 0,84 | 74% |
| Qwen2.5-7B | 0,16 → 0,25 (+0,09; IK 95% [0,04; 0,15]) | 0,19 → 0,75 | 84% |

**1. Akses diblokir, jawaban yang tetap diberikan hampir semuanya salah.** Model 3B lebih banyak menolak menjawab sehingga laju halusinasinya tidak naik secara signifikan. Pada 1.5B dan 7B laju halusinasi ikut naik. Pada ketiga model, jawaban yang tetap diberikan 75–84% salah.

**2. Konfabulasi disusun dari evidence yang tersisa.** Hanya 1% jawaban karangan sama dengan jawaban model tanpa *evidence* (*closed-book*). Sebagian besar disalin dari paragraf relevan yang masih tersedia. Jumlah kandidat nama atau angka dalam teks pengecoh tidak berpengaruh: pengecoh kaya entitas dan miskin entitas memberikan hasil yang sama pada ketiga ukuran (uji *pre-registered*).

**3. Sinyal kecukupan hanya efektif jika diberi otoritas.** Semua varian *head* terlatih membedakan *evidence* lengkap dari tidak lengkap dengan akurasi berpasangan 0,98–0,99, termasuk pada kondisi yang tidak pernah dilatih. *Probe* yang hanya membaca *hidden state* sama baiknya, artinya sinyal itu sudah ada di dalam model.

| Bentuk sinyal σ (model 3B, populasi utama) | Halusinasi | Jawaban benar | *False refusal* (*evidence* lengkap) |
| --- | --- | --- | --- |
| Tanpa sinyal | 0,197 | 0,209 | 0,18 |
| σ sebagai saran di *prompt* | 0,244 | 0,236 | 0,12 |
| σ acak sebagai saran (plasebo) | 0,247 | 0,236 | 0,14 |
| σ sebagai *gate* (σ < 0,5 → menolak) | **0,089** | 0,158 | 0,27 |

Saran dengan σ asli tidak berbeda dari plasebo (Δ halusinasi −0,002, IK 95% [−0,014; 0,008]). Sebagai *gate*, σ yang sama menurunkan halusinasi 10,8 poin (IK 95% [−0,128; −0,089]) dengan biaya 5,1 poin jawaban benar (fase 1b, hasil sekunder). Sebagai pembanding, *gate* dari *reader* berbasis *prompt* menaikkan *false refusal* sebesar 58 poin.

**Konfirmasi pada 400 soal baru (Studi 3, *pre-registered*).** Uji ulang dengan kontras yang selalu terdefinisi mengonfirmasi pola ini. Polanya juga muncul pada keluarga model lain (Gemma 4 E4B). Untuk Gemma, σ tetap dihitung oleh *reader* Qwen, sehingga *reader* dan *generator* adalah model yang berbeda.

| Uji (populasi utama, 255 soal × 5 kondisi) | Qwen2.5-3B | Gemma 4 E4B |
| --- | --- | --- |
| P1: saran setara plasebo (TOST ±0,02) | −0,008 [−0,017; 0,002]: **didukung** | +0,009 [0,002; 0,017]: **didukung** |
| P2: *gate* menurunkan halusinasi ≥ 5 poin | −0,133 [−0,161; −0,109]: **didukung** | −0,042 [−0,059; −0,027]: signifikan, tetapi di bawah ambang 5 poin |
| P3: utilitas (benar − 2 × halusinasi), *gate* > saran | +0,365 [0,297; 0,431]: **didukung** | +0,035 [0,005; 0,068]: **didukung** |
| Biaya: kenaikan *false refusal* (*evidence* lengkap) | +0,114 [0,075; 0,153] | +0,098 [0,063; 0,137] |

Besar efek *gate* bergantung pada seberapa sering *generator* berhalusinasi tanpa sinyal: Qwen 22,6%, Gemma 8,6%. Pada Qwen, batas atas biaya *false refusal* sedikit melewati ambang praktis 0,15 yang ditetapkan sebelumnya.

## Hipotesis yang tidak terdukung dan keterbatasan

Sebelas dari enam belas uji konfirmatori tidak terdukung. Kegagalan itu justru menggeser pertanyaan dari akses ke otoritas.

**Tidak terdukung.**

- Memotong kanal menaikkan halusinasi pada model 3B (+0,013; IK 95% [−0,045; 0,074]).
- Peringatan *reader* di *prompt* mengurangi halusinasi. Peringatan itu diabaikan. Jika dipaksakan, 76% soal yang dapat dijawab justru ditolak.
- *Head* terlatih lebih baik daripada *probe* atau *reader* berbasis *prompt* (AURC). Tidak terbukti, tetapi semuanya mencapai tingkat oracle.
- Banyaknya kandidat dalam teks memicu lebih banyak konfabulasi.
- Kontras utama "saran vs *gate*" pada cakupan menjawab yang sama tidak dapat dihitung secara bermakna. Saran justru menaikkan laju menjawab (0,41 → 0,48) melampaui yang dapat dicapai *gate*. Kontras ini kemudian dirancang ulang dan diuji secara konfirmatori pada Studi 3 (lihat Hasil utama).

**Keterbatasan.**

- Baru satu keluarga model (Qwen2.5) dan satu dataset (HotpotQA) dengan jawaban pendek.
- Kasus ambigu dilabel melalui audit per soal, belum oleh anotator manusia independen. *LLM judge* sepakat 82% (κ = 0,61); hanya satu verdict yang berubah antarversi label.
- Lengan "saran" belum di-*fine-tune* untuk memakai σ, sehingga perbandingannya belum adil dalam arti terkuat.
- *Baseline* wajib dari penelitian terdekat belum dijalankan: Compression-Aware Abstention (workshop GroundLM @ EMNLP 2026, arXiv 2608.29934) dan RINSE (preprint, arXiv 2609.37469).

## Gagasan lanjutan: kapan model sebaiknya berhenti

Jika model tidak memiliki "rem", gagasan berikutnya adalah merumuskan rem itu secara matematis sebagai masalah *optimal stopping*. Rumus dasarnya ternyata sudah ada di literatur; yang mungkin baru adalah cara menghitung salah satu suku dan cara aturan itu ditegakkan.

**Formulasi.** Jawaban dipecah per klaim (per kalimat). Sebelum menulis klaim berikutnya, sistem menghitung tiga hal:

- σ: peluang klaim berikutnya didukung *evidence*. Diperoleh dari *head* yang sudah dibangun.
- *g*: sisa informasi ber-*evidence* yang belum disampaikan, yaitu bobot unit *evidence* relevan yang belum terekspresikan.
- λ, μ: biaya satu klaim karangan dan biaya panjang jawaban.

Klaim berikutnya hanya ditulis jika manfaat yang diharapkan positif:

```latex
\text{lanjut} \iff \sigma\, g - \lambda (1-\sigma) - \mu > 0 \iff \sigma > \frac{\lambda + \mu}{g + \lambda}
```

Satu aturan ini mencakup dua jenis "berhenti":

- **Abstain.** Jika *evidence* kurang, σ kecil, sehingga sistem berhenti sebelum klaim pertama.
- **Berhenti setelah cukup terelaborasi.** Jika semua informasi penting sudah tersampaikan, *g* mendekati 0. Ambangnya naik melewati 1, sehingga sistem berhenti walaupun model masih yakin.

**Posisi terhadap literatur** (penelusuran 11 Oktober 2026; rincian di `00_docs/07_prior_art_stopping_rule.md`).

| Bagian | Status | Rujukan terdekat |
| --- | --- | --- |
| Memecah jawaban per klaim dan menyaring klaim dengan ambang terkalibrasi | sudah ada | [Mohri & Hashimoto, 2024](https://arxiv.org/abs/2402.10978) |
| Aturan "jawab jika peluang ≥ rasio biaya" | sudah ada; dengan *g* = 1 dan μ = 0 rumus di atas identik | [CASS/CAG, 2026](https://arxiv.org/abs/2605.01749) |
| *Trade-off* panjang jawaban vs faktualitas | sudah ada | [Spataru dkk., NAACL 2024](https://aclanthology.org/2024.naacl-long.202/) |
| Aturan berhenti di dalam *decoding* | sudah ada, tetapi berbasis kepastian internal model, bukan *evidence* | [Sequential-EDFL, 2025](https://arxiv.org/abs/2510.06478) |
| *g* sebagai sisa *evidence* yang dihitung selama penulisan; satu aturan untuk abstain dan berhenti; diuji sebagai otoritas vs saran dengan sinyal identik | tidak ditemukan | — |

*Status rujukan pada tabel ini.*

- **Peer-reviewed:** Mohri & Hashimoto (ICML 2024), Spataru dkk. (NAACL 2024), dan ALCE (EMNLP 2023).
- **Preprint, belum melalui peer review:** CASS/CAG dan Sequential-EDFL.
- **Klaim "tidak ditemukan"** berarti tidak ditemukan dalam penelusuran sampai 11 Oktober 2026, termasuk preprint. Ini bukan bukti bahwa belum ada yang melakukannya.

**Rencana uji.**

- **Data.** Dataset jawaban panjang yang punya anotasi cakupan informasi, misalnya ASQA dan QAMPARI (lewat *benchmark* ALCE, [Gao dkk., 2023](https://arxiv.org/abs/2305.14627)).
- **Pembanding.** *Decoding* biasa, aturan σ saja, dan aturan σ + *g*.
- **Ablasi wajib, *g* = 1.** Jika hasilnya sama dengan aturan lengkap, kontribusi gagasan ini runtuh menjadi rumus yang sudah ada.
- **Hipotesis.** Aturan σ + *g* menghasilkan lebih sedikit klaim karangan tanpa kehilangan cakupan informasi dibandingkan kedua pembanding.

## Seberapa jauh matematika dapat mengurangi halusinasi

Matematika dapat menentukan kapan sebaiknya menjawab, tetapi tidak dapat menghapus halusinasi tanpa biaya. Aturan keputusan juga hanya optimal jika peluang "jawaban benar" diperkirakan secara terkalibrasi. Bagian estimasi inilah yang belum kami miliki.

| Hasil teoretis | Isi | Status rujukan |
| --- | --- | --- |
| [Kalai & Vempala, STOC 2024](https://arxiv.org/abs/2311.14648) | Model yang terkalibrasi pasti berhalusinasi pada fakta yang jarang; lajunya kira-kira sebanding dengan proporsi fakta yang hanya muncul sekali di data latih | *peer-reviewed* |
| [Xu dkk., 2024](https://arxiv.org/abs/2401.11817) | Secara komputabilitas, LLM tidak dapat menghindari halusinasi untuk semua fungsi komputabel | *preprint* |
| [Geifman & El-Yaniv, NeurIPS 2017](https://arxiv.org/abs/1705.08500) | Dengan opsi menolak (*reject option*), risiko target dapat dijamin dengan peluang tinggi | *peer-reviewed* |
| [Mohri & Hashimoto, ICML 2024](https://arxiv.org/abs/2402.10978) | Jaminan marginal P(keluaran benar) ≥ 1 − α dengan *conformal prediction*, dengan asumsi *exchangeability* | *peer-reviewed* |
| [Kalai dkk., 2025](https://arxiv.org/abs/2509.04664) | Penilaian biner mendorong model menebak. Dengan penalti t/(1 − t) untuk jawaban salah, menjawab hanya menguntungkan jika P(benar) > t | *preprint* |

**Hubungan dengan aturan kami.** Jika *g* = 1, μ = 0, dan λ = t/(1 − t), aturan pada bagian sebelumnya menjadi σ > t. Ini persis aturan skor berpenalti di atas. *Gate* σ < 0,5 yang kami uji setara dengan t = 0,5. Kesetaraan ini adalah turunan kami sendiri, bukan klaim paper tersebut.

**Batas yang kami ukur sendiri.** Aturan itu mensyaratkan σ = P(benar). Kenyataannya, σ kami mengukur P(*evidence* cukup):

| Kalibrasi σ terhadap… | ECE (0 = sempurna) | Contoh |
| --- | --- | --- |
| *Evidence* lengkap | 0,048 | σ ≈ 0,9 → sekitar 90% paket memang lengkap |
| Jawaban benar | 0,256 | Pada σ ≈ 0,98 hanya 56% jawaban benar |

Kesalahan karena salah membaca *evidence* yang lengkap tidak terlihat oleh σ. Karena itu, kemajuan berikutnya bergantung pada estimasi P(benar) yang lebih baik, misalnya dengan menggabungkan σ dengan sinyal keyakinan pada level jawaban.

**Yang dapat dan tidak dapat dijanjikan oleh rumus.**

- **Dapat:**
  - keputusan optimal bila peluangnya terkalibrasi;
  - jaminan rata-rata (marginal) lewat *conformal prediction*.
- **Tidak dapat:**
  - menghapus halusinasi tanpa memindahkan kesalahan menjadi penolakan (pada kami, +11 poin *false refusal*);
  - menjamin kebenaran per soal;
  - bertahan ketika distribusi data bergeser.

## Benchmark terhadap metode ketidakpastian standar

Pada laju menjawab yang sama, σ menekan halusinasi setara dengan metode standar. Keunggulan nyatanya adalah penolakan yang jauh lebih sedikit terhadap soal yang sebenarnya dapat dijawab. Sebagian besar penurunan halusinasi berasal dari keputusan untuk tidak menjawab, bukan dari kecermatan sinyalnya.

**Setup.** Qwen2.5-3B, Studi 3, populasi utama (1.275 baris; 447 jawaban substantif). Semua sinyal dihitung dengan model yang sama dan ditetapkan sebelum dijalankan:

- P(True) dengan *evidence* di konteks (gaya Kadavath dkk., 2022);
- rata-rata *log-prob* jawaban;
- *self-consistency* (5 sampel);
- skor *reader* berbasis *prompt*;
- σ (EAG).

**Gate pada laju menjawab yang sama (18%).**

| *Gate* | Halusinasi | Jawaban benar | *False refusal* (*evidence* lengkap) |
| --- | --- | --- | --- |
| σ (EAG) | 0,093 | 0,088 | **0,345** |
| P(True) | 0,091 | 0,089 | 0,510 |
| *Reader* berbasis *prompt* | 0,095 | 0,086 | 0,455 |
| *Log-prob* jawaban | 0,097 | 0,084 | 0,506 |
| Acak, laju menjawab sama | 0,116 | 0,064 | 0,605 |
| Tanpa *gate* | 0,226 | 0,125 | 0,231 |

**Kualitas peringkat (AURC, makin kecil makin baik).**

- σ = 0,499 dan acak = 0,644.
- Selisih σ terhadap P(True), *log-prob*, dan *reader* tidak signifikan (95% CI memuat 0).
- σ lebih baik dari *self-consistency* (+0,095 [0,046; 0,144]).
- AUROC benar-vs-halusinasi: σ 0,715; P(True) 0,694; *reader* 0,673; *log-prob* 0,662; *self-consistency* 0,548.

**Implikasi untuk klaim.**

1. Angka "halusinasi turun 13,3 poin" harus selalu disertai laju menjawab dan pembanding *gate* acak. Pada cakupan yang sama, keunggulan atas *gate* acak sekitar 2,4 poin.
2. Temuan inti tidak berubah: sinyal yang sama efektif hanya jika diberi otoritas, apa pun sumber sinyalnya.
3. Langkah berikutnya yang paling menjanjikan adalah menggabungkan σ (kecukupan *evidence*) dengan sinyal pada level jawaban (misalnya P(True)) untuk memperkirakan P(benar). Kesalahan karena salah membaca *evidence* lengkap tidak tertangkap oleh sinyal mana pun yang diuji.

## Hal yang ingin saya diskusikan dengan Bapak/Ibu

Saya sangat menghargai kritik atas satu atau dua pertanyaan berikut. Bapak/Ibu tidak perlu menanggapi semuanya.

1. **Ketajaman kerangka.** Apakah "otoritas epistemik" merupakan kerangka yang cukup tajam dan bermakna, atau terlalu dekat dengan literatur *abstention* dan *selective prediction* yang sudah ada?
2. **Desain pembanding yang adil.** Bagaimana sebaiknya membandingkan "saran" dan "otoritas" secara adil, ketika saran justru mengubah seberapa sering model menjawab? Apakah *generator* perlu di-*fine-tune* untuk memakai sinyal tersebut sebelum dibandingkan?
3. **Gagasan aturan berhenti.** Apakah formulasi *optimal stopping* pada bagian sebelumnya layak dikembangkan? Dataset jawaban panjang berbasis *evidence* mana yang paling tepat untuk mengujinya?
4. **Generalisasi.** Dengan sumber daya komputasi terbatas (satu GPU 8 GB dan Colab), keluarga model dan dataset apa yang paling meyakinkan? Apakah menguji pada data berbahasa Indonesia akan menambah nilai?
5. **Standar pelabelan.** Untuk jawaban yang ambigu, apakah audit per soal dengan dua anotator manusia sudah memadai, atau sebaiknya menggunakan protokol lain?
6. **Kelayakan untuk dikembangkan.** Menurut Bapak/Ibu, apakah temuan ini cukup menarik untuk dikembangkan lebih jauh, misalnya menjadi tulisan ilmiah? Bagian mana yang paling layak ditekuni?

**Pertanyaan utama: langkah berikutnya.** Saat ini saya sengaja menunda eksperimen baru sampai mendapat masukan. Menurut Bapak/Ibu, mana yang paling bernilai untuk dikerjakan lebih dahulu?

1. **Studi aturan berhenti (σ + *g*)** pada dataset jawaban panjang berbasis *evidence* (ASQA atau QAMPARI), dengan ablasi *g* = 1 sebagai uji kebaruan. Ini proyek yang lebih besar, tetapi paling dekat dengan pertanyaan "kapan model harus berhenti".
2. **Menurunkan biaya *gate*.** Pada Qwen, *gate* menaikkan penolakan atas soal yang sebenarnya bisa dijawab sebesar 11 poin. Pilihannya antara lain ambang τ yang dikalibrasi atau *gate* bertingkat (menjawab dengan peringatan, bukan langsung menolak). Pendekatannya akan didaftarkan lebih dahulu.
3. **Memperkuat generalisasi temuan yang sudah ada:** model dan dataset lain (termasuk data berbahasa Indonesia), *baseline* dari penelitian terdekat, dan audit label oleh anotator manusia.
4. **Arah lain** yang menurut Bapak/Ibu lebih penting untuk topik ini.

Kode, data hasil, pra-registrasi, dan catatan seluruh keputusan penelitian (*research log*) dapat saya kirimkan bila Bapak/Ibu berkenan memeriksanya lebih jauh.

## Lampiran: istilah

| Istilah | Arti dalam penelitian ini |
| --- | --- |
| Kanal *evidence* | Jalur paragraf dari *reader* ke *generator* yang dimanipulasi per paragraf utuh |
| Halusinasi | Jawaban substantif (bukan penolakan) yang salah |
| *Selective risk* | Halusinasi dibagi jumlah jawaban substantif |
| *False refusal* | Menolak menjawab padahal *evidence* lengkap |
| AURC | Area di bawah kurva *risk–coverage*; makin kecil, makin baik sebuah *gate* mengurutkan jawaban |
| σ | Skor 0–1 dari *head* kecil yang memperkirakan apakah *evidence* cukup |
| Saran | σ dituliskan di *prompt*; *generator* bebas memakainya atau tidak |
| Otoritas / *gate* | σ menentukan apakah jawaban boleh keluar |
| Plasebo | Teks saran identik, tetapi σ diacak antarsoal |
| Pra-registrasi | Hipotesis dan kriteria kegagalan ditulis sebelum data dilihat |

## Catatan tentang rujukan

Saya mengaudit status publikasi setiap rujukan lewat ACL Anthology, PMLR, prosiding NeurIPS, halaman jurnal, dan daftar penerimaan konferensi.

| Status | Jumlah (dari 107) |
| --- | --- |
| *Peer-reviewed* | 56 |
| *Workshop* | 3 |
| *Preprint* | 40 |
| Belum dapat diverifikasi | 8 |

Klaim utama dalam dokumen ini bersandar pada rujukan *peer-reviewed* bila tersedia, misalnya Gekhman dkk. (COLM 2025), Orgad dkk. (ICLR 2025), Kandpal dkk. (ICML 2023), dan Geifman & El-Yaniv (NeurIPS 2017). Rujukan *preprint* diberi label di teks. Daftar lengkap tersedia di `00_docs/10_citation_audit.md`.
