# Fase 1b — pengetahuan internal vs eksternal (eksploratif)

Rencana: `00_docs/14_analysis_plan_phase1b_probe.md`. Qwen2.5-3B, `full`. Probe dilatih hanya pada kandidat buatan model (cross-fit 5 lipatan per item); emas tidak pernah dilatih.

Kandidat (setelah membuang ambigu yang belum dinilai: 0):
```
          n  benar
kind              
decoy   396  0.000
gold    396  1.000
greedy  339  0.684
sample  803  0.367
```

## Uji 1 — K (Gekhman), populasi utama
```
Item dengan kandidat buatan model benar & salah: 117
K[int_L21] = 0.723
K[external] = 0.714
K[surface] = 0.720
K[int_L14] = 0.650
K[int_L26] = 0.738
K[int_L28] = 0.764
K[int_L21] − K[external] = +0.009  [95%: -0.060; +0.082]
K[int_L21] − K[surface] = +0.002  [95%: -0.065; +0.071]
K[surface] − K[external] = +0.006  [95%: -0.015; +0.024]
```

## Uji 2 — kasus halusinasi: emas vs jawaban greedy
```
halusinasi: skor[int_L21](emas) > skor(greedy salah): 44/80 = 0.550 [0.441; 0.654]
halusinasi: skor[external](emas) > skor(greedy salah): 5/80 = 0.062 [0.027; 0.138]
halusinasi: skor[surface](emas) > skor(greedy salah): 9/80 = 0.113 [0.060; 0.200]
halusinasi: skor[int_L14](emas) > skor(greedy salah): 38/80 = 0.475 [0.369; 0.583]
halusinasi: skor[int_L26](emas) > skor(greedy salah): 48/80 = 0.600 [0.490; 0.700]
halusinasi: skor[int_L28](emas) > skor(greedy salah): 43/80 = 0.537 [0.429; 0.643]
KONTROL decoy: skor[int_L21](emas soal lain) > skor(greedy salah): 12/80 = 0.150 [0.088; 0.244]
KONTROL decoy: skor[external](emas soal lain) > skor(greedy salah): 0/80 = 0.000 [-0.000; 0.046]
KONTROL decoy: skor[surface](emas soal lain) > skor(greedy salah): 0/80 = 0.000 [-0.000; 0.046]
KONTROL decoy: skor[int_L14](emas soal lain) > skor(greedy salah): 6/80 = 0.075 [0.035; 0.154]
KONTROL decoy: skor[int_L26](emas soal lain) > skor(greedy salah): 15/80 = 0.188 [0.117; 0.287]
KONTROL decoy: skor[int_L28](emas soal lain) > skor(greedy salah): 11/80 = 0.138 [0.079; 0.230]
emas − decoy (proporsi menang atas greedy, int_L21): +0.400 [95%: +0.287; +0.525], n=80
acuan (kelompok benar, n=68): skor(greedy benar) > skor(sampel salah), rata-rata: int_L21 0.824, external 0.947, surface 0.948, int_L14 0.733, int_L26 0.850, int_L28 0.835
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
n/a       36   44   80
All       36   44   80
```
