# Fase 1b — pengetahuan internal vs eksternal (eksploratif)

Rencana: `00_docs/14_analysis_plan_phase1b_probe.md`. Qwen2.5-3B, `full`. Probe dilatih hanya pada kandidat buatan model (cross-fit 5 lipatan per item); emas tidak pernah dilatih.

Kandidat (setelah membuang ambigu yang belum dinilai: 25):
```
          n  benar
kind              
gold    396  1.000
greedy  299  0.712
sample  230  0.317
```

## Uji 1 — K (Gekhman), populasi utama
```
Item dengan kandidat buatan model benar & salah: 37
K[int_L27] = 0.911
K[external] = 0.649
K[surface] = 0.632
K[int_L18] = 0.772
K[int_L33] = 0.916
K[int_L36] = 0.800
K[int_L27] − K[external] = +0.262  [95%: +0.114; +0.420]
K[int_L27] − K[surface] = +0.279  [95%: +0.124; +0.430]
K[surface] − K[external] = -0.017  [95%: -0.047; +0.000]
```

## Uji 2 — kasus halusinasi: emas vs jawaban greedy
```
halusinasi: skor[int_L27](emas) > skor(greedy salah): 48/71 = 0.676 [0.561; 0.773]
halusinasi: skor[external](emas) > skor(greedy salah): 0/71 = 0.000 [0.000; 0.051]
halusinasi: skor[surface](emas) > skor(greedy salah): 0/71 = 0.000 [0.000; 0.051]
halusinasi: skor[int_L18](emas) > skor(greedy salah): 40/71 = 0.563 [0.448; 0.673]
halusinasi: skor[int_L33](emas) > skor(greedy salah): 46/71 = 0.648 [0.532; 0.749]
halusinasi: skor[int_L36](emas) > skor(greedy salah): 44/71 = 0.620 [0.503; 0.724]
acuan (kelompok benar, n=24): skor(greedy benar) > skor(sampel salah), rata-rata: int_L27 0.854, external 0.778, surface 0.757, int_L18 0.736, int_L33 0.941, int_L36 0.875
```

## Uji 3 — silang dengan Fase 1
```
K1_loose             R_final<=5  R_final>5  All
int_L27                                        
probe: emas>greedy           26         22   48
probe: greedy>=emas           8         15   23
All                          34         37   71
```

Jenis kesalahan × probe(emas > greedy):
```
int_L27              0.0  1.0  All
etype                             
1_hop_pertama          4    4    8
2_pengecoh             2    7    9
3_emas_entitas_lain   13   30   43
4_parsial_format       1    3    4
5_lainnya              3    4    7
All                   23   48   71
```
