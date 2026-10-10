# Study 3 — advice vs authority (confirmatory) — generator qwen2.5-3b

judge_missing (unaudited ambiguous): 0


## PRIMARY (items=255, rows/arm=1275)

```
             arm  halluc  correct  abstain  sel_risk  false_refusal_full  U_lambda2
             off  0.2259   0.1247   0.6494    0.6443              0.2314    -0.3271
          advice  0.2988   0.1357   0.5655    0.6877              0.1137    -0.4620
         placebo  0.3067   0.1318   0.5616    0.6995              0.1333    -0.4816
       authority  0.0925   0.0878   0.8196    0.5130              0.3451    -0.0973
advice_authority  0.1153   0.0910   0.7937    0.5589              0.2588    -0.1396
```

```
  id                                     contrast     est      lo      hi      verdict  p_holm
  P1 halluc advice − placebo (90% CI, TOST ±0.02) -0.0078 -0.0173  0.0016    supported     NaN
  P2                       halluc authority − off -0.1333 -0.1608 -0.1090    supported   0.001
  P3                    U(λ=2) authority − advice  0.3647  0.2973  0.4314    supported   0.001
cost          false refusal @full authority − off  0.1137  0.0745  0.1529 exceeds 0.15     NaN
```

Secondary:
```
                 contrast    est     lo     hi
U(λ=1) authority − advice 0.1584 0.1192 0.1969
U(λ=4) authority − advice 0.7773 0.6533 0.9043
      halluc advice − off 0.0729 0.0533 0.0933
```

Per level (hallucination):
```
arm       advice  advice_authority  authority    off  placebo
level                                                        
drop_all   0.131             0.022      0.018  0.100    0.149
drop_ans   0.425             0.116      0.100  0.325    0.431
full       0.380             0.302      0.227  0.278    0.373
```


## all items (items=396, rows/arm=1980)

```
             arm  halluc  correct  abstain  sel_risk  false_refusal_full  U_lambda2
             off  0.1747   0.1551   0.6702    0.5299              0.2449    -0.1944
          advice  0.2369   0.1747   0.5884    0.5755              0.1288    -0.2990
         placebo  0.2434   0.1697   0.5869    0.5892              0.1515    -0.3172
       authority  0.0737   0.1131   0.8131    0.3946              0.3308    -0.0343
advice_authority  0.0929   0.1207   0.7864    0.4350              0.2374    -0.0652
```

```
  id                                     contrast     est      lo      hi   verdict  p_holm
  P1 halluc advice − placebo (90% CI, TOST ±0.02) -0.0066 -0.0141  0.0010 supported     NaN
  P2                       halluc authority − off -0.1010 -0.1212 -0.0823 supported   0.001
  P3                    U(λ=2) authority − advice  0.2646  0.2121  0.3167 supported   0.001
cost          false refusal @full authority − off  0.0859  0.0581  0.1162        ok     NaN
```

Secondary:
```
                 contrast    est     lo     hi
U(λ=1) authority − advice 0.1015 0.0712 0.1323
U(λ=4) authority − advice 0.5909 0.4929 0.6904
      halluc advice − off 0.0621 0.0465 0.0778
```

Per level (hallucination):
```
arm       advice  advice_authority  authority    off  placebo
level                                                        
drop_all   0.106             0.015      0.011  0.076    0.126
drop_ans   0.337             0.095      0.082  0.253    0.336
full       0.298             0.245      0.182  0.217    0.293
```
