# Study 3 — advice vs authority (confirmatory) — generator gemma4-e4b

judge_missing (unaudited ambiguous): 0


## PRIMARY (items=255, rows/arm=1275)

```
             arm  halluc  correct  abstain  sel_risk  false_refusal_full  U_lambda2
             off  0.0863   0.1169   0.7969    0.4247              0.3725    -0.0557
          advice  0.0722   0.1075   0.8204    0.4017              0.4000    -0.0369
         placebo  0.0627   0.0800   0.8573    0.4396              0.5569    -0.0455
       authority  0.0439   0.0855   0.8706    0.3394              0.4706    -0.0024
advice_authority  0.0424   0.0878   0.8698    0.3253              0.4627     0.0031
```

```
  id                                     contrast     est      lo      hi       verdict  p_holm
  P1 halluc advice − placebo (90% CI, TOST ±0.02)  0.0094  0.0024  0.0165     supported     NaN
  P2                       halluc authority − off -0.0424 -0.0588 -0.0267 not supported   0.001
  P3                    U(λ=2) authority − advice  0.0345  0.0047  0.0675     supported   0.018
cost          false refusal @full authority − off  0.0980  0.0627  0.1373            ok     NaN
```

Secondary:
```
                 contrast     est      lo      hi
U(λ=1) authority − advice  0.0063 -0.0125  0.0259
U(λ=4) authority − advice  0.0910  0.0369  0.1537
      halluc advice − off -0.0141 -0.0227 -0.0055
```

Per level (hallucination):
```
arm       advice  advice_authority  authority    off  placebo
level                                                        
drop_all   0.016             0.006      0.006  0.018    0.010
drop_ans   0.100             0.045      0.045  0.127    0.094
full       0.129             0.110      0.118  0.141    0.106
```


## all items (items=396, rows/arm=1980)

```
             arm  halluc  correct  abstain  sel_risk  false_refusal_full  U_lambda2
             off  0.0641   0.1359   0.8000    0.3207              0.3434     0.0076
          advice  0.0540   0.1263   0.8197    0.2997              0.3636     0.0182
         placebo  0.0475   0.0980   0.8545    0.3264              0.5101     0.0030
       authority  0.0343   0.1071   0.8586    0.2429              0.4192     0.0384
advice_authority  0.0323   0.1081   0.8596    0.2302              0.4167     0.0434
```

```
  id                                     contrast     est      lo      hi       verdict  p_holm
  P1 halluc advice − placebo (90% CI, TOST ±0.02)  0.0066  0.0025  0.0116     supported     NaN
  P2                       halluc authority − off -0.0298 -0.0409 -0.0192 not supported   0.001
  P3                    U(λ=2) authority − advice  0.0202 -0.0000  0.0414 not supported   0.060
cost          false refusal @full authority − off  0.0758  0.0505  0.1035            ok     NaN
```

Secondary:
```
                 contrast     est      lo      hi
U(λ=1) authority − advice  0.0005 -0.0126  0.0131
U(λ=4) authority − advice  0.0596  0.0212  0.1000
      halluc advice − off -0.0101 -0.0167 -0.0045
```

Per level (hallucination):
```
arm       advice  advice_authority  authority    off  placebo
level                                                        
drop_all   0.010             0.004      0.004  0.011    0.006
drop_ans   0.073             0.033      0.032  0.090    0.069
full       0.104             0.088      0.101  0.119    0.086
```
