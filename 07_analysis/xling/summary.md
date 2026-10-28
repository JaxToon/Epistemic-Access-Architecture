# Fase 5a — evidence lintas bahasa (pilot eksploratif)

Rencana: `00_docs/16_analysis_plan_phase5a_crosslingual.md`. Qwen2.5-3B, pertanyaan bahasa Inggris, evidence diterjemahkan (XHotpotQA, GPT-4o mini); kedua lengan diminta menjawab dalam bahasa Inggris.

Populasi utama, item berpasangan: 255; judge_missing: 0; unit XL tak terpetakan (rata-rata per paket): 0.05

Keluaran XL@full yang memuat aksara non-Latin: 0.031

## Kontras XL − EN* (bootstrap item, IK 95%)
```
                              ukuran   EN*    XL  XL−EN*     lo     hi
                          benar@full 0.486 0.298  -0.188 -0.247 -0.129
                     halusinasi@full 0.290 0.392   0.102  0.043  0.165
                        abstain@full 0.224 0.310   0.086  0.031  0.141
                 halusinasi@drop_ans 0.325 0.329   0.004 -0.051  0.063
akurasi berpasangan σ(full>drop_ans) 0.984 0.941  -0.043 -0.075 -0.012
           gate menolak@full (σ<0,5) 0.227 0.682   0.455  0.392  0.514
                  σ@full (rata-rata) 0.745 0.339  -0.406 -0.445 -0.366
```

## Per aksara paragraf jawaban (deskriptif)
```
                    n  benar_X  d_benar  halu_X  abstain_X  sigma_X
script                                                             
Latin             104    0.337   -0.115   0.375      0.288    0.382
en (kontrol)       14    0.357   -0.071   0.500      0.143    0.605
non-Latin         125    0.240   -0.256   0.408      0.352    0.283
tidak terpetakan   12    0.500   -0.250   0.250      0.250    0.234
```

## Per bahasa paragraf jawaban (deskriptif, n kecil; bukan untuk klaim per bahasa)
```
           n  benar_X  d_benar  abstain_X  sigma_X
ans_lang                                          
ar        13    0.154   -0.538      0.077    0.400
ur        11    0.182   -0.455      0.273    0.244
zh        12    0.167   -0.333      0.500    0.325
el        12    0.083   -0.333      0.583    0.194
fa        10    0.400   -0.300      0.200    0.164
fr        10    0.200   -0.300      0.300    0.460
sw         4    0.250   -0.250      0.000    0.178
sv        13    0.385   -0.231      0.308    0.374
es         9    0.222   -0.222      0.556    0.429
pl         9    0.222   -0.222      0.111    0.504
hi        15    0.333   -0.200      0.267    0.384
ru        10    0.200   -0.200      0.200    0.286
tr        11    0.273   -0.182      0.545    0.281
ko        11    0.273   -0.182      0.545    0.196
th         9    0.222   -0.111      0.444    0.420
id        10    0.300   -0.100      0.500    0.305
ja        13    0.308   -0.077      0.231    0.306
en        14    0.357   -0.071      0.143    0.605
nl        14    0.571   -0.071      0.071    0.372
it         9    0.222    0.000      0.222    0.339
bn         9    0.333    0.000      0.667    0.128
pt         1    0.000    0.000      0.000    0.116
de         8    0.500    0.125      0.250    0.409
vi         6    0.500    0.333      0.167    0.562
```
