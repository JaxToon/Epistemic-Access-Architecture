# Fase 1b — pengetahuan internal vs eksternal (eksploratif)

Rencana: `00_docs/14_analysis_plan_phase1b_probe.md`. Qwen2.5-3B, `full`. Probe dilatih hanya pada kandidat buatan model (cross-fit 5 lipatan per item); emas tidak pernah dilatih.

Kandidat (setelah membuang ambigu yang belum dinilai: 0):
```
          n  benar
kind              
decoy   396  0.000
gold    396  1.000
greedy  314  0.825
sample  170  0.576
```

## Uji 1 — K (Gekhman), populasi utama
```
Item dengan kandidat buatan model benar & salah: 32
K[int_L21] = 0.860
K[external] = 0.585
K[surface] = 0.608
K[int_L14] = 0.583
K[int_L26] = 0.716
K[int_L28] = 0.609
K[int_L21] − K[external] = +0.275  [95%: +0.091; +0.455]
K[int_L21] − K[surface] = +0.251  [95%: +0.059; +0.439]
K[surface] − K[external] = +0.023  [95%: -0.031; +0.086]
```

## Uji 2 — kasus halusinasi: emas vs jawaban greedy
```
halusinasi: skor[int_L21](emas) > skor(greedy salah): 19/40 = 0.475 [0.329; 0.625]
halusinasi: skor[external](emas) > skor(greedy salah): 0/40 = 0.000 [-0.000; 0.088]
halusinasi: skor[surface](emas) > skor(greedy salah): 0/40 = 0.000 [-0.000; 0.088]
halusinasi: skor[int_L14](emas) > skor(greedy salah): 16/40 = 0.400 [0.263; 0.554]
halusinasi: skor[int_L26](emas) > skor(greedy salah): 18/40 = 0.450 [0.307; 0.602]
halusinasi: skor[int_L28](emas) > skor(greedy salah): 14/40 = 0.350 [0.221; 0.505]
KONTROL decoy: skor[int_L21](emas soal lain) > skor(greedy salah): 0/40 = 0.000 [-0.000; 0.088]
KONTROL decoy: skor[external](emas soal lain) > skor(greedy salah): 0/40 = 0.000 [-0.000; 0.088]
KONTROL decoy: skor[surface](emas soal lain) > skor(greedy salah): 0/40 = 0.000 [-0.000; 0.088]
KONTROL decoy: skor[int_L14](emas soal lain) > skor(greedy salah): 2/40 = 0.050 [0.014; 0.165]
KONTROL decoy: skor[int_L26](emas soal lain) > skor(greedy salah): 0/40 = 0.000 [-0.000; 0.088]
KONTROL decoy: skor[int_L28](emas soal lain) > skor(greedy salah): 1/40 = 0.025 [0.004; 0.129]
emas − decoy (proporsi menang atas greedy, int_L21): +0.475 [95%: +0.325; +0.625], n=40
acuan (kelompok benar, n=21): skor(greedy benar) > skor(sampel salah), rata-rata: int_L21 0.909, external 0.643, surface 0.679, int_L14 0.619, int_L26 0.798, int_L28 0.833
```

## Uji 3 — silang dengan Fase 1
```
Empty DataFrame
Columns: []
Index: []
```

Jenis kesalahan × probe(emas > greedy):
```
int_L21  0.0  1.0  All
etype                 
n/a       21   19   40
All       21   19   40
```
