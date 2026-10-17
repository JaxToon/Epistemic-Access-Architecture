# Rencana Analisis Fase 5a: *Evidence* Lintas Bahasa (Pilot)

Ditulis 17 Oktober 2026, **sebelum** paket lintas bahasa dibuat atau dijalankan. Status: **pilot eksploratif**. Latar: dokumen 11 (Fase 5) dan 15 (XHotpotQA).

## Pertanyaan

Jika *evidence* yang sama disajikan dalam bahasa lain (terjemahan mesin XHotpotQA) sementara pertanyaannya tetap bahasa Inggris:

1. Apakah model memakai *evidence* itu sama baiknya? (jawaban benar, halusinasi, dan penolakan pada `full`)
2. Apakah konfabulasi saat paragraf jawaban dihapus berubah? (halusinasi pada `drop_ans`)
3. Apakah σ, dari *head* yang **hanya dilatih dalam bahasa Inggris**, tetap membedakan paket lengkap dari tidak lengkap?

## Desain

- **Item:** 396 item Studi 2/3. Pelaporan utama pada populasi utama (255).
- **Kondisi:** `full` (kebijakan `length`) dan `drop_ans` (kebijakan `entity_poor`).
- **Lengan:**
  - **EN\***: paket asli bahasa Inggris.
  - **XL**: setiap unit "[eK] (judul) kalimat" diganti dengan judul dan kalimat terjemahan XHotpotQA. Unit yang tidak terpetakan (±1%) tetap bahasa Inggris dan dicatat.
- **Prompt:** templat `GENERATOR` yang sama. Baris "Give only the short answer (a few words), no explanation." diganti menjadi "Give only the short answer (a few words) in English, no explanation." **pada kedua lengan**, untuk mencegah *confound* bahasa jawaban. Karena itu EN\* dijalankan ulang dan tidak memakai `off` lama.
- **Generator:** Qwen2.5-3B-Instruct, *greedy*, maksimum 24 token.
- **σ:** fitur diekstrak ulang dari *prompt* baru (EN\* dan XL), lalu skor dari tiga *head* `eag_lc1` fase 1 yang dibekukan (rata-rata sigmoid).
- **Label:** aturan + *judge* Qwen2.5-7B untuk kasus ambigu, sama dengan studi sebelumnya. *Judge* hanya melihat pertanyaan, jawaban emas, dan prediksi.

## Analisis

- **Kontras primer (XL − EN\*)**, berpasangan per item, *bootstrap* item 2.000×, IK 95%:
  - benar@`full`, halusinasi@`full`, abstain@`full`;
  - halusinasi@`drop_ans`;
  - akurasi berpasangan σ(`full`) > σ(`drop_ans`);
  - laju penolakan oleh *gate* (σ < 0,5) pada `full`.
- **Sekunder (deskriptif):**
  - per bahasa paragraf jawaban di XL (±15 item per bahasa; **tidak untuk klaim per bahasa**);
  - per aksara paragraf jawaban (Latin vs non-Latin), sebagai proksi kasar jarak dari bahasa Inggris;
  - item yang paragraf jawabannya tetap bahasa Inggris di XL, sebagai kontrol efek "campuran bahasa";
  - proporsi keluaran XL yang memuat aksara non-Latin (jawaban tidak diterjemahkan balik).
- Tidak ada koreksi multiplisitas. Semua hasil adalah pilot eksploratif untuk merancang Fase 5b.

## Keterbatasan yang sudah diketahui

- Terjemahan mesin (GPT-4o mini) bisa mengubah atau menghilangkan string jawaban. Kesalahan bisa berasal dari terjemahan balik, bukan dari pemakaian pengetahuan.
- Setiap paragraf berbahasa acak, sehingga satu paket memuat beberapa bahasa. Ini kondisi lintas bahasa, bukan monolingual.
- *Head* σ dilatih pada bahasa Inggris. Penurunan σ bisa berarti *head* tidak bisa dipakai lintas bahasa, bukan bahwa kecukupan tidak terbaca di *hidden state*.
