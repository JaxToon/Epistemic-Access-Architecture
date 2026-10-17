# Diagnosis "tahu tapi tidak mengungkap" + popularitas (eksploratif)

Rencana: `00_docs/12_analysis_plan_diagnosis_popularity.md`. Qwen2.5-3B, `full`, populasi utama.

closed-book judge_missing: 6 (fallback strict)

## Ringkasan per kelompok (`off`)

```
           n  LP_gold_med  LP_own_med  LP_abs_med  R_final_med  R_final<=5  R_min_med  dLP_ctx_med  CB_correct  sigma_med
group                                                                                                                    
abstain   59       -3.534      -0.013      -0.013         26.0       0.322       18.0        5.198       0.000      0.629
correct  125       -0.038      -0.002      -3.995          1.0       0.880        1.0        5.194       0.032      0.962
halluc    71       -3.304      -0.010      -3.841          7.0       0.479        6.0        3.963       0.028      0.965
```

## Klasifikasi kasus halusinasi

```
K1: 0/71 = 0.000  [Wilson 95%: 0.000; 0.051]
K1_loose: 34/71 = 0.479  [Wilson 95%: 0.367; 0.593]
K2: 37/71 = 0.521  [Wilson 95%: 0.407; 0.633]
abstain dengan LP_gold > LP_abs: 3/59 = 0.051 [0.017; 0.139]
```

K1 × sumber pengetahuan:
```
source  konteks saja  memori  All
K1                               
0                 69       2   71
All               69       2   71
```

Jenis kesalahan × K1:
```
K1                    0  All
etype                       
1_hop_pertama         8    8
2_pengecoh            9    9
3_emas_entitas_lain  43   43
4_parsial_format      4    4
5_lainnya             7    7
All                  71   71
```

Perbandingan (deskriptif, tanpa koreksi):
```
lp_gold: benar vs halusinasi, Mann–Whitney p = 2.202e-16
rank_final: benar vs halusinasi, Mann–Whitney p = 6.508e-19
d_lp_ctx: benar vs halusinasi, Mann–Whitney p = 0.01737
sigma: benar vs halusinasi, Mann–Whitney p = 0.7314
```

*Logit lens* (median peringkat token pertama jawaban emas di t₀; lapisan terpilih):
```
    correct   halluc  abstain
9   29103.0  23875.0  34175.0
18  20341.0  17970.0  20993.0
24  84786.0  72494.0  72556.0
27  70073.0  79521.0  78147.0
30  27592.0  56028.0  37669.0
33      2.0    667.0    288.0
34      1.0     23.0     56.0
35      1.0     11.0     33.0
36      1.0      7.0     26.0
```

## Popularitas entitas (pageviews 2025)

judul: 795, tidak ter-resolve: 10, views = 0: 10

Regresi logistik (kemiringan per 1 SD popularitas, IK 95% bootstrap item):
```
       x        outcome  slope_per_SD     lo    hi  ci_excl_0
pop_mean        correct        -0.185 -0.445 0.061          0
pop_mean  hallucination         0.411  0.135 0.720          1
pop_mean        abstain        -0.177 -0.457 0.111          0
pop_mean    gate_refuse        -0.102 -0.417 0.217          0
pop_mean hi_sigma_wrong         0.260  0.011 0.544          1
 pop_min        correct        -0.206 -0.498 0.037          0
 pop_min  hallucination         0.431  0.122 0.798          1
 pop_min        abstain        -0.145 -0.418 0.125          0
 pop_min    gate_refuse        -0.020 -0.317 0.283          0
 pop_min hi_sigma_wrong         0.233 -0.023 0.541          0
```

Per kuartil popularitas (rata-rata log10 views kedua judul emas):
```
               n  correct  hallucination  abstain  gate_refuse  hi_sigma_wrong  sigma
Q                                                                                    
Q1 (jarang)   64    0.594          0.156    0.250        0.250           0.250  0.752
Q2            64    0.484          0.281    0.234        0.188           0.375  0.758
Q3            63    0.460          0.270    0.270        0.190           0.429  0.754
Q4 (populer)  64    0.422          0.406    0.172        0.188           0.422  0.789
```

Spearman popularitas vs σ: ρ = 0.053 (p = 0.395)

Sekunder: Spearman popularitas vs halusinasi @drop_ans: ρ = 0.090 (p = 0.15)

Sekunder: K1_longgar vs popularitas (logistik, per SD): 0.050 [-0.399; 0.594]
