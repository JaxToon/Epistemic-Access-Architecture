# Persiapan Fase 5: Data Multibahasa dan Literatur Pendukung Fase 2

Tanggal: 17 Oktober 2026. Status: pencarian awal. Abstrak arXiv dibaca langsung (V-abs); isi lengkap belum dibaca.

## Syarat data untuk Fase 5

Manipulasi kanal membutuhkan soal multi-hop **dengan paragraf *evidence***, yaitu dua paragraf emas dan beberapa pengecoh, supaya paragraf emas bisa dihapus dan diganti. Dataset *closed-book* tidak memenuhi syarat ini.

## Kandidat

| Sumber | Status | Bahasa | Ada *evidence*? | Catatan |
| --- | --- | --- | --- | --- |
| XHotpotQA, Barati dkk., arXiv 2608.27481 (Agt 2026) | V-abs | Belum disebut di abstrak | Ya: setiap contoh punya label bahasa untuk pertanyaan, *evidence* penghubung, *evidence* jawaban, dan pengecoh. 7.405 validasi, 15.661 latih | Paling cocok secara struktur. Lisensi CC BY-SA 4.0 (dari HotpotQA). **Perlu dicek apakah ada bahasa Indonesia**, dan apakah teksnya terjemahan mesin |
| DaPT, Wang dkk., arXiv 2603.19097 (Mar 2026) | V-abs | Lima bahasa (tidak disebut di abstrak) | Belum jelas | Menerjemahkan HotpotQA, 2Wiki, dan MuSiQue. Rilis data belum jelas |
| ID-MoCQA, Permadi dkk., arXiv 2602.03709 (Feb 2026) | V-abs | Indonesia, Inggris | Belum jelas | Budaya Indonesia, multi-hop. Hasil pencarian menyebut versi TACL, tetapi **belum diverifikasi** |
| Pt-HotpotQA (JBCS) | Dari hasil pencarian | Portugis | Ya (terjemahan HotpotQA) | Contoh preseden metode terjemahan |
| Terjemahan sendiri | — | Indonesia + satu bahasa daerah | Ya | Subset item Studi 2/3 diterjemahkan dengan MT, lalu sampel diperiksa manusia. Paket identik lintas bahasa memungkinkan perbandingan berpasangan per soal |

**Rekomendasi sementara:** terjemahkan sendiri subset item Studi 2/3. Alasannya: soal, paket, σ, dan label bahasa Inggris sudah ada, sehingga perbandingan lintas bahasa bisa berpasangan per soal. XHotpotQA dipakai sebagai pembanding atau validasi jika memuat bahasa Indonesia. Risiko utama: artefak terjemahan. Mitigasi: periksa sampel secara manual, dan pastikan string jawaban tetap terdeteksi di paragraf jawaban setelah diterjemahkan.

## Literatur bahasa Indonesia dan bahasa daerah (konteks, bukan kebaruan)

- MATH-IDN (EACL 2026 Findings): penalaran matematika dalam bahasa Indonesia, Jawa, Sunda, dan Bugis.
- LoraxBench (arXiv 2508.12459): 20 bahasa di Indonesia. Kinerja turun jelas pada bahasa sumber daya rendah.
- NusaWrites (arXiv 2309.10661): LLM sulit menggeneralisasi ke bahasa yang tidak dilihat.
- Putri dkk. (EMNLP 2024): pembuatan soal pengetahuan dalam bahasa Indonesia dan Sunda.
- Belum ditemukan studi "pengetahuan dimiliki ≠ diekspresikan" lintas bahasa Indonesia dan bahasa daerah. Perlu pencarian lanjutan dengan kata kunci "*cross-lingual factual consistency*" dan "*multilingual knowledge probing*".

## Literatur pendukung Fase 2 (popularitas)

- **Mallen dkk., *When Not to Trust Language Models* (ACL 2023), PopQA:** popularitas diukur dengan *pageviews* Wikipedia. Memori parametrik lemah pada entitas yang jarang. *Retrieval* membantu entitas jarang tetapi bisa merugikan entitas populer, karena konteks bisa menyesatkan model.
  - **Relevansi:** ukuran popularitas kita sama dengan Mallen dkk. Bedanya, kita bertanya apakah **pemakaian konteks yang sudah lengkap** dan **penolakan oleh *gate*** bergantung pada popularitas, bukan apakah memori parametrik bergantung pada popularitas. Prediksi dari Mallen dkk.: pada entitas populer, memori bisa bersaing dengan konteks.
- Tindak lanjut 2024 (arXiv 2403.01432): *fine-tuning* vs RAG per kelompok popularitas (PopQA, WitQA, EntityQuestions). Perlu dibaca.

## Sumber

- https://arxiv.org/abs/2608.27481
- https://arxiv.org/abs/2603.19097
- https://arxiv.org/abs/2602.03709
- https://journals-sol.sbc.org.br/index.php/jbcs/article/view/5801
- https://arxiv.org/html/2508.12459v1
- https://arxiv.org/pdf/2309.10661
- https://aclanthology.org/2024.emnlp-main.1145/
- https://arxiv.org/pdf/2212.10511v3
- https://arxiv.org/pdf/2403.01432v2

## Pembaruan 17 Okt 2026: XHotpotQA sudah diperiksa (data diunduh)

- Repositori: https://github.com/Iman998/XhotpotQA (kode, MIT). Data: https://huggingface.co/datasets/Iman998/XhotpotQA (V1.1 *audited*, CC BY-SA 4.0). Disimpan di `01_data/raw/xhotpotqa/` (validasi, 7.405 item).
- **24 bahasa, termasuk bahasa Indonesia.** Paragraf **diterjemahkan mesin** (V1: GPT-4o mini). Kalimat sumber bahasa Inggris disimpan berdampingan dengan terjemahannya, per kalimat.
- **Setiap paragraf diterjemahkan ke satu bahasa acak**, jadi tidak ada versi monolingual Indonesia.
- **Kecocokan dengan data kita:** semua 400 item Studi 2/3 ada di XHotpotQA. 2.536/2.556 unit paket `full` (99%) dan 971/972 unit emas bisa dipetakan ke terjemahannya per kalimat.
- **Sebaran bahasa unit emas** pada paket kita kira-kira rata (20–54 unit per bahasa). Bahasa Indonesia hanya 34 unit, terlalu sedikit untuk klaim per bahasa.
- **Implikasi:**
  - **Fase 5a (lintas bahasa, bisa segera):** soal dan paket yang sama, dengan unit *evidence* diganti terjemahan XHotpotQA, pertanyaan tetap bahasa Inggris. Perbandingannya berpasangan per soal dengan hasil bahasa Inggris. Rencana: dokumen 16.
  - **Fase 5b (monolingual Indonesia dan bahasa daerah):** tetap perlu menerjemahkan sendiri.
