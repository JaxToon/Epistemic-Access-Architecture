# Fase 1b — pengetahuan internal vs eksternal (eksploratif)

Rencana: `00_docs/14_analysis_plan_phase1b_probe.md`. Qwen2.5-3B, `full`. Probe dilatih hanya pada kandidat buatan model (cross-fit 5 lipatan per item); emas tidak pernah dilatih.

Kandidat (setelah membuang ambigu yang belum dinilai: 0):
```
           n  benar
kind               
decoy    396  0.000
gold     396  1.000
greedy   299  0.712
hard    1913  0.000
sample   255  0.345
```

## Uji 1 — K (Gekhman), populasi utama
```
Item dengan kandidat buatan model benar & salah: 41
K[int_L27] = 0.899
K[external] = 0.654
K[surface] = 0.648
K[int_L18] = 0.660
K[int_L33] = 0.842
K[int_L36] = 0.759
K[int_L27] − K[external] = +0.244  [95%: +0.106; +0.389]
K[int_L27] − K[surface] = +0.251  [95%: +0.119; +0.391]
K[surface] − K[external] = -0.007  [95%: -0.049; +0.038]
```

## Uji 2 — kasus halusinasi: emas vs jawaban greedy
```
halusinasi: skor[int_L27](emas) > skor(greedy salah): 49/71 = 0.690 [0.575; 0.786]
halusinasi: skor[external](emas) > skor(greedy salah): 0/71 = 0.000 [0.000; 0.051]
halusinasi: skor[surface](emas) > skor(greedy salah): 0/71 = 0.000 [0.000; 0.051]
halusinasi: skor[int_L18](emas) > skor(greedy salah): 37/71 = 0.521 [0.407; 0.633]
halusinasi: skor[int_L33](emas) > skor(greedy salah): 45/71 = 0.634 [0.518; 0.736]
halusinasi: skor[int_L36](emas) > skor(greedy salah): 43/71 = 0.606 [0.489; 0.711]
KONTROL decoy: skor[int_L27](emas soal lain) > skor(greedy salah): 7/71 = 0.099 [0.049; 0.190]
KONTROL decoy: skor[external](emas soal lain) > skor(greedy salah): 0/71 = 0.000 [0.000; 0.051]
KONTROL decoy: skor[surface](emas soal lain) > skor(greedy salah): 0/71 = 0.000 [0.000; 0.051]
KONTROL decoy: skor[int_L18](emas soal lain) > skor(greedy salah): 6/71 = 0.085 [0.039; 0.172]
KONTROL decoy: skor[int_L33](emas soal lain) > skor(greedy salah): 12/71 = 0.169 [0.099; 0.273]
KONTROL decoy: skor[int_L36](emas soal lain) > skor(greedy salah): 11/71 = 0.155 [0.089; 0.257]
emas − decoy (proporsi menang atas greedy, int_L27): +0.592 [95%: +0.465; +0.718], n=71
DECOY KETAT [int_L27]: emas peringkat-1 di antara emas+greedy+judul paket: 46/71 = 0.648 [0.532; 0.749] vs peluang acak 0.153; judul paket terbaik > greedy: 0.352
DECOY KETAT [external]: emas peringkat-1 di antara emas+greedy+judul paket: 0/71 = 0.000 [0.000; 0.051] vs peluang acak 0.153; judul paket terbaik > greedy: 0.056
acuan (kelompok benar, n=26): skor(greedy benar) > skor(sampel salah), rata-rata: int_L27 0.840, external 0.795, surface 0.814, int_L18 0.609, int_L33 0.800, int_L36 0.808
```

## Uji 3 — silang dengan Fase 1
```
K1_loose             R_final<=5  R_final>5  All
int_L27                                        
probe: emas>greedy           25         24   49
probe: greedy>=emas           9         13   22
All                          34         37   71
```

Jenis kesalahan × probe(emas > greedy):
```
int_L27              0.0  1.0  All
etype                             
1_hop_pertama          4    4    8
2_pengecoh             2    7    9
3_emas_entitas_lain   12   31   43
4_parsial_format       1    3    4
5_lainnya              3    4    7
All                   22   49   71
```
