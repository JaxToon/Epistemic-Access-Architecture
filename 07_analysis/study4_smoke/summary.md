# Studi 4 — tangga otoritas

Item utama: 3; halusinasi off@full: 1; judge_missing: 0; k1 file: 07_analysis\study4_smoke\k1.csv

```
             benar@full  halu@full  abstain@full  halu@drop_ans  halu→benar
off               0.333      0.333         0.333          0.333         0.0
advice            0.333      0.000         0.667          0.667         0.0
placebo           0.333      0.000         0.667          0.333         0.0
veto              0.333      0.000         0.667          0.000         0.0
steer             0.333      0.333         0.333          0.333         0.0
steer_sigma       0.333      0.333         0.333          0.333         0.0
steer_rand        0.333      0.333         0.333          0.333         0.0
rand_sigma        0.333      0.333         0.333          0.333         0.0
```

```
  id                                                        uji       a   b  n10  n01     p   lo  hi verdict  p_holm
H4.1              halusinasi→benar: steer_σ vs advice (McNemar)  0.0000 0.0  0.0  0.0 1.000  NaN NaN     NaN     1.0
H4.2        halusinasi→benar: steer_σ vs steer_rand_σ (McNemar)  0.0000 0.0  0.0  0.0 1.000  NaN NaN     NaN     1.0
H4.3           U(λ=2) steer_σ − veto, full+drop_ans (bootstrap) -0.6667 NaN  NaN  NaN 0.566 -2.0 0.0     NaN     1.0
H4.4 halusinasi→benar steer_σ: K1 vs non-K1 (Fisher, satu sisi)  0.0000 NaN  1.0  0.0 1.000  NaN NaN     NaN     1.0
H4.5 rusak steer_σ ≤ 0,05 dan Δhalu@drop_ans ≤ +0,02 (TOST 90%)  0.0000 0.0  NaN  NaN   NaN  0.0 0.0      ok     NaN
```
