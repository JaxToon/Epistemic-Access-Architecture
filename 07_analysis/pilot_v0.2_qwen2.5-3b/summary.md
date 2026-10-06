# Analysis — pilot_v0.2_qwen2.5-3b

Items: 500 · primary population: 311 · qclass: {'open': 413, 'answer_in_question': 51, 'yesno': 29}

## Channel manipulation check (off)

```
            answer_available  gold_kept  len_ratio_min  len_ratio_max      tokens
level                                                                            
full                0.995943   1.000000       1.000000       1.000000  376.385396
drop_ans            0.210953   0.483478       0.780000       1.041522  374.612576
drop_other          0.937120   0.516522       0.767263       1.047022  374.902637
drop_all            0.000000   0.000000       0.764706       1.047022  373.129817
```

## Reader verdict vs answer availability (off rows)

```
answer_available  0.0  1.0
reader_verdict            
INSUFFICIENT      896  936
SUFFICIENT         19  121
```

Reader `missing` leak rate: 11.51%


## Stratum: primary (items=311)

```
          system      level   n  halluc  h_lo  h_hi  correct  abstain  non_answer  sel_risk  false_refusal  abst_precision  halluc_if_unavail  unsup_correct  tokens
     closed_book          - 311   0.141 0.103 0.180    0.045    0.814       0.000     0.759            NaN             NaN                NaN          0.000  78.588
             off       full 311   0.283 0.238 0.338    0.534    0.183       0.026     0.346          0.183             0.0                NaN          0.000 379.791
             off   drop_ans 311   0.296 0.244 0.347    0.068    0.637       0.019     0.814            NaN             1.0              0.296          0.068 378.042
             off drop_other 311   0.122 0.087 0.161    0.222    0.656       0.023     0.355          0.656             0.0                NaN          0.000 378.222
             off   drop_all 311   0.087 0.055 0.119    0.013    0.900       0.006     0.871            NaN             1.0              0.087          0.013 376.473
        advisory       full 311   0.264 0.212 0.315    0.540    0.196       0.106     0.328          0.196             0.0                NaN          0.000 387.791
        advisory   drop_ans 311   0.312 0.264 0.367    0.074    0.614       0.251     0.808            NaN             1.0              0.312          0.074 386.042
        advisory drop_other 311   0.100 0.068 0.135    0.228    0.672       0.232     0.304          0.672             0.0                NaN          0.000 386.222
        advisory   drop_all 311   0.096 0.064 0.129    0.016    0.887       0.177     0.857            NaN             1.0              0.096          0.016 384.473
advisory_missing       full 311   0.238 0.193 0.286    0.486    0.277       0.077     0.329          0.277             0.0                NaN          0.000 404.183
advisory_missing   drop_ans 311   0.241 0.193 0.286    0.087    0.672       0.093     0.735            NaN             1.0              0.241          0.087 406.215
advisory_missing drop_other 311   0.093 0.064 0.129    0.219    0.688       0.100     0.299          0.688             0.0                NaN          0.000 406.264
advisory_missing   drop_all 311   0.084 0.055 0.116    0.029    0.887       0.071     0.743            NaN             1.0              0.084          0.029 406.486
        enforced       full 311   0.087 0.055 0.119    0.151    0.762       0.003     0.365          0.762             0.0                NaN          0.000 387.791
        enforced   drop_ans 311   0.032 0.013 0.051    0.023    0.945       0.000     0.588            NaN             1.0              0.032          0.023 386.042
        enforced drop_other 311   0.003 0.000 0.010    0.013    0.984       0.000     0.200          0.984             0.0                NaN          0.000 386.222
        enforced   drop_all 311   0.000 0.000 0.000    0.000    1.000       0.000     0.000            NaN             1.0              0.000          0.000 384.473
 enforced_oracle       full 311   0.283 0.235 0.334    0.534    0.183       0.026     0.346          0.183             0.0                NaN          0.000 379.791
 enforced_oracle   drop_ans 311   0.000 0.000 0.000    0.000    1.000       0.000     0.000            NaN             1.0              0.000          0.000 378.042
 enforced_oracle drop_other 311   0.122 0.090 0.161    0.222    0.656       0.023     0.355          0.656             0.0                NaN          0.000 378.222
 enforced_oracle   drop_all 311   0.000 0.000 0.000    0.000    1.000       0.000     0.000            NaN             1.0              0.000          0.000 376.473
   restored_ctrl       full 311   0.238 0.193 0.286    0.572    0.190       0.010     0.294          0.190             0.0                NaN          0.000 751.196
        restored       full 311   0.251 0.203 0.299    0.563    0.186       0.010     0.308          0.186             0.0                NaN          0.000 750.325
  enforced_score       full 311   0.087 0.055 0.119    0.158    0.756       0.003     0.355          0.756             0.0                NaN          0.000 387.791
  enforced_score   drop_ans 311   0.032 0.016 0.051    0.023    0.945       0.000     0.588            NaN             1.0              0.032          0.023 386.042
  enforced_score drop_other 311   0.003 0.000 0.010    0.013    0.984       0.000     0.200          0.984             0.0                NaN          0.000 386.222
  enforced_score   drop_all 311   0.000 0.000 0.000    0.000    1.000       0.000     0.000            NaN             1.0              0.000          0.000 384.473
```

### Risk–coverage (gates on advisory outputs, all levels)

```
   gate_score    n   aurc  ci95_lo  ci95_hi  random_gate
reader_p_suff 1244 0.3186   0.2719   0.3657       0.1929
       oracle 1244 0.1758   0.1466   0.2081       0.1929
```

### Contrasts (diff = b − a)

```
                  id hypothesis  primary                                                 contrast  n_items  rate_a  rate_b    diff  ci95_lo  ci95_hi  ci90_lo  ci90_hi  a0_b1  a1_b0      p                       test  coverage_a  coverage_b  p_holm tost_equivalent within_margin
                 H1a         H1     True                           off: full -> drop_ans [halluc]      311  0.2830  0.2958  0.0129  -0.0450   0.0740  -0.0386   0.0643   48.0   44.0 0.7547              McNemar exact         NaN         NaN  0.7547             NaN           NaN
                 H1b         H1     True                           off: full -> drop_all [halluc]      311  0.2830  0.0868 -0.1961  -0.2508  -0.1415  -0.2412  -0.1511   14.0   75.0 0.0000              McNemar exact         NaN         NaN  0.0000             NaN           NaN
                 H1c         H1    False                         off: full -> drop_other [halluc]      311  0.2830  0.1222 -0.1608  -0.2122  -0.1125  -0.2026  -0.1190   10.0   60.0 0.0000              McNemar exact         NaN         NaN     NaN             NaN           NaN
                  H2         H2     True                        off@drop_ans -> restored [halluc]      311  0.2958  0.2508 -0.0450  -0.0997   0.0129  -0.0900   0.0032   33.0   47.0 0.1456              McNemar exact         NaN         NaN  0.4369             NaN           NaN
                H2eq         H2    False                restored_ctrl -> restored [halluc] (TOST)      311  0.2379  0.2508  0.0129  -0.0322   0.0579  -0.0257   0.0514   28.0   24.0 0.6778              McNemar exact         NaN         NaN     NaN           False           NaN
                 H3a         H3     True                       off -> advisory @drop_ans [halluc]      311  0.2958  0.3119  0.0161  -0.0096   0.0450  -0.0064   0.0386   12.0    7.0 0.3593              McNemar exact         NaN         NaN  0.7186             NaN           NaN
                 H3b         H3     True          advisory -> enforced @drop_ans [selective risk]      311  0.8083  0.5882 -0.2201  -0.4561   0.0018  -0.4087  -0.0367    NaN    NaN 0.0520 bootstrap (selective risk)      0.3859      0.0547  0.2080             NaN           NaN
                  H4         H4     True off -> enforced @full [false refusal | answer available]      311  0.1833  0.7621  0.5788   0.5209   0.6367   0.5305   0.6270  180.0    0.0 0.0000              McNemar exact         NaN         NaN  0.0000             NaN         False
            H3a_full         H3    False                           off -> advisory @full [halluc]      311  0.2830  0.2637 -0.0193  -0.0514   0.0096  -0.0450   0.0064    9.0   15.0 0.3075              McNemar exact         NaN         NaN     NaN             NaN           NaN
            H3b_full         H3    False              advisory -> enforced @full [selective risk]      311  0.3280  0.3649  0.0369  -0.0550   0.1322  -0.0393   0.1144    NaN    NaN 0.4480 bootstrap (selective risk)      0.8039      0.2379     NaN             NaN           NaN
      H3a_drop_other         H3    False                     off -> advisory @drop_other [halluc]      311  0.1222  0.0997 -0.0225  -0.0450   0.0000  -0.0418  -0.0032    3.0   10.0 0.0923              McNemar exact         NaN         NaN     NaN             NaN           NaN
      H3b_drop_other         H3    False        advisory -> enforced @drop_other [selective risk]      311  0.3039  0.2000 -0.1039  -0.3617   0.3299  -0.3474   0.2217    NaN    NaN 0.5420 bootstrap (selective risk)      0.3280      0.0161     NaN             NaN           NaN
        H3a_drop_all         H3    False                       off -> advisory @drop_all [halluc]      311  0.0868  0.0965  0.0096  -0.0129   0.0322  -0.0096   0.0289    8.0    5.0 0.5811              McNemar exact         NaN         NaN     NaN             NaN           NaN
        H3b_drop_all         H3    False          advisory -> enforced @drop_all [selective risk]      311  0.8571  0.0000 -0.8571  -0.9688  -0.7352  -0.9488  -0.7586    NaN    NaN 0.0005 bootstrap (selective risk)      0.1125      0.0000     NaN             NaN           NaN
      H3b_score_full         H3    False        advisory -> enforced_score @full [selective risk]      311  0.3280  0.3553  0.0273  -0.0614   0.1201  -0.0505   0.1049    NaN    NaN 0.5580 bootstrap (selective risk)      0.8039      0.2444     NaN             NaN           NaN
  H3b_score_drop_ans         H3    False    advisory -> enforced_score @drop_ans [selective risk]      311  0.8083  0.5882 -0.2201  -0.4427  -0.0196  -0.4084  -0.0422    NaN    NaN 0.0390 bootstrap (selective risk)      0.3859      0.0547     NaN             NaN           NaN
H3b_score_drop_other         H3    False  advisory -> enforced_score @drop_other [selective risk]      311  0.3039  0.2000 -0.1039  -0.3608   0.3548  -0.3458   0.2408    NaN    NaN 0.5140 bootstrap (selective risk)      0.3280      0.0161     NaN             NaN           NaN
  H3b_score_drop_all         H3    False    advisory -> enforced_score @drop_all [selective risk]      311  0.8571  0.0000 -0.8571  -0.9667  -0.7368  -0.9459  -0.7568    NaN    NaN 0.0005 bootstrap (selective risk)      0.1125      0.0000     NaN             NaN           NaN
                leak    control    False          advisory -> advisory_missing @drop_ans [halluc]      311  0.3119  0.2412 -0.0707  -0.1158  -0.0257  -0.1093  -0.0322   15.0   37.0 0.0032              McNemar exact         NaN         NaN     NaN             NaN           NaN
```

### Restored, by turn-1 status

```
              hallucination       correct      
                       mean count    mean count
turn1_status                                   
abstain               0.162   198   0.596   198
correct               0.048    21   0.952    21
hallucination         0.489    92   0.402    92
```

## Stratum: primary_param_unknown (items=297)

```
          system      level   n  halluc  h_lo  h_hi  correct  abstain  non_answer  sel_risk  false_refusal  abst_precision  halluc_if_unavail  unsup_correct  tokens
     closed_book          - 297   0.148 0.111 0.192    0.000    0.852       0.000     1.000            NaN             NaN                NaN          0.000  78.677
             off       full 297   0.283 0.236 0.333    0.525    0.192       0.027     0.350          0.192             0.0                NaN          0.000 381.121
             off   drop_ans 297   0.296 0.246 0.350    0.051    0.653       0.020     0.854            NaN             1.0              0.296          0.051 379.370
             off drop_other 297   0.121 0.084 0.162    0.202    0.677       0.024     0.375          0.677             0.0                NaN          0.000 379.532
             off   drop_all 297   0.091 0.061 0.125    0.000    0.909       0.007     1.000            NaN             1.0              0.091          0.000 377.781
        advisory       full 297   0.269 0.222 0.323    0.529    0.202       0.108     0.338          0.202             0.0                NaN          0.000 389.121
        advisory   drop_ans 297   0.310 0.259 0.364    0.061    0.630       0.259     0.836            NaN             1.0              0.310          0.061 387.370
        advisory drop_other 297   0.101 0.067 0.135    0.209    0.690       0.239     0.326          0.690             0.0                NaN          0.000 387.532
        advisory   drop_all 297   0.098 0.064 0.135    0.000    0.902       0.178     1.000            NaN             1.0              0.098          0.000 385.781
advisory_missing       full 297   0.239 0.195 0.290    0.481    0.279       0.081     0.332          0.279             0.0                NaN          0.000 405.141
advisory_missing   drop_ans 297   0.239 0.192 0.286    0.074    0.687       0.098     0.763            NaN             1.0              0.239          0.074 407.865
advisory_missing drop_other 297   0.094 0.064 0.131    0.205    0.700       0.094     0.315          0.700             0.0                NaN          0.000 407.535
advisory_missing   drop_all 297   0.088 0.057 0.121    0.010    0.902       0.067     0.897            NaN             1.0              0.088          0.010 407.801
        enforced       full 297   0.091 0.061 0.125    0.155    0.754       0.003     0.370          0.754             0.0                NaN          0.000 389.121
        enforced   drop_ans 297   0.030 0.013 0.051    0.024    0.946       0.000     0.562            NaN             1.0              0.030          0.024 387.370
        enforced drop_other 297   0.003 0.000 0.010    0.013    0.983       0.000     0.200          0.983             0.0                NaN          0.000 387.532
        enforced   drop_all 297   0.000 0.000 0.000    0.000    1.000       0.000     0.000            NaN             1.0              0.000          0.000 385.781
 enforced_oracle       full 297   0.283 0.232 0.337    0.525    0.192       0.027     0.350          0.192             0.0                NaN          0.000 381.121
 enforced_oracle   drop_ans 297   0.000 0.000 0.000    0.000    1.000       0.000     0.000            NaN             1.0              0.000          0.000 379.370
 enforced_oracle drop_other 297   0.121 0.084 0.158    0.202    0.677       0.024     0.375          0.677             0.0                NaN          0.000 379.532
 enforced_oracle   drop_all 297   0.000 0.000 0.000    0.000    1.000       0.000     0.000            NaN             1.0              0.000          0.000 377.781
   restored_ctrl       full 297   0.232 0.189 0.279    0.572    0.195       0.010     0.289          0.195             0.0                NaN          0.000 753.936
        restored       full 297   0.249 0.202 0.303    0.556    0.195       0.010     0.310          0.195             0.0                NaN          0.000 753.074
  enforced_score       full 297   0.091 0.061 0.125    0.162    0.747       0.003     0.360          0.747             0.0                NaN          0.000 389.121
  enforced_score   drop_ans 297   0.030 0.013 0.051    0.024    0.946       0.000     0.562            NaN             1.0              0.030          0.024 387.370
  enforced_score drop_other 297   0.003 0.000 0.010    0.013    0.983       0.000     0.200          0.983             0.0                NaN          0.000 387.532
  enforced_score   drop_all 297   0.000 0.000 0.000    0.000    1.000       0.000     0.000            NaN             1.0              0.000          0.000 385.781
```

### Risk–coverage (gates on advisory outputs, all levels)

```
   gate_score    n   aurc  ci95_lo  ci95_hi  random_gate
reader_p_suff 1188 0.3247   0.2849   0.3670       0.1944
       oracle 1188 0.1958   0.1613   0.2372       0.1944
```

### Contrasts (diff = b − a)

```
                  id hypothesis  primary                                                 contrast  n_items  rate_a  rate_b    diff  ci95_lo  ci95_hi  ci90_lo  ci90_hi  a0_b1  a1_b0      p                       test  coverage_a  coverage_b  p_holm tost_equivalent within_margin
                 H1a         H1     True                           off: full -> drop_ans [halluc]      297  0.2828  0.2963  0.0135  -0.0471   0.0741  -0.0370   0.0673   46.0   42.0 0.7493              McNemar exact         NaN         NaN  0.9614             NaN           NaN
                 H1b         H1     True                           off: full -> drop_all [halluc]      297  0.2828  0.0909 -0.1919  -0.2525  -0.1347  -0.2424  -0.1414   14.0   71.0 0.0000              McNemar exact         NaN         NaN  0.0000             NaN           NaN
                 H1c         H1    False                         off: full -> drop_other [halluc]      297  0.2828  0.1212 -0.1616  -0.2121  -0.1111  -0.2054  -0.1212    9.0   57.0 0.0000              McNemar exact         NaN         NaN     NaN             NaN           NaN
                  H2         H2     True                        off@drop_ans -> restored [halluc]      297  0.2963  0.2492 -0.0471  -0.1044   0.0101  -0.0943   0.0000   31.0   45.0 0.1354              McNemar exact         NaN         NaN  0.4062             NaN           NaN
                H2eq         H2    False                restored_ctrl -> restored [halluc] (TOST)      297  0.2323  0.2492  0.0168  -0.0303   0.0640  -0.0236   0.0572   28.0   23.0 0.5758              McNemar exact         NaN         NaN     NaN           False           NaN
                 H3a         H3     True                       off -> advisory @drop_ans [halluc]      297  0.2963  0.3098  0.0135  -0.0135   0.0404  -0.0101   0.0370   11.0    7.0 0.4807              McNemar exact         NaN         NaN  0.9614             NaN           NaN
                 H3b         H3     True          advisory -> enforced @drop_ans [selective risk]      297  0.8364  0.5625 -0.2739  -0.4987  -0.0578  -0.4572  -0.0899    NaN    NaN 0.0180 bootstrap (selective risk)      0.3704      0.0539  0.0720             NaN           NaN
                  H4         H4     True off -> enforced @full [false refusal | answer available]      297  0.1919  0.7542  0.5623   0.5051   0.6162   0.5150   0.6094  167.0    0.0 0.0000              McNemar exact         NaN         NaN  0.0000             NaN         False
            H3a_full         H3    False                           off -> advisory @full [halluc]      297  0.2828  0.2694 -0.0135  -0.0438   0.0168  -0.0370   0.0135    9.0   13.0 0.5235              McNemar exact         NaN         NaN     NaN             NaN           NaN
            H3b_full         H3    False              advisory -> enforced @full [selective risk]      297  0.3376  0.3699  0.0323  -0.0595   0.1222  -0.0423   0.1076    NaN    NaN 0.4940 bootstrap (selective risk)      0.7980      0.2458     NaN             NaN           NaN
      H3a_drop_other         H3    False                     off -> advisory @drop_other [halluc]      297  0.1212  0.1010 -0.0202  -0.0438   0.0000  -0.0404  -0.0034    3.0    9.0 0.1460              McNemar exact         NaN         NaN     NaN             NaN           NaN
      H3b_drop_other         H3    False        advisory -> enforced @drop_other [selective risk]      297  0.3261  0.2000 -0.1261  -0.3902   0.3370  -0.3762   0.2376    NaN    NaN 0.4550 bootstrap (selective risk)      0.3098      0.0168     NaN             NaN           NaN
        H3a_drop_all         H3    False                       off -> advisory @drop_all [halluc]      297  0.0909  0.0976  0.0067  -0.0168   0.0303  -0.0135   0.0269    7.0    5.0 0.7744              McNemar exact         NaN         NaN     NaN             NaN           NaN
        H3b_drop_all         H3    False          advisory -> enforced @drop_all [selective risk]      297  1.0000  0.0000 -1.0000  -1.0000  -1.0000  -1.0000  -1.0000    NaN    NaN 0.0005 bootstrap (selective risk)      0.0976      0.0000     NaN             NaN           NaN
      H3b_score_full         H3    False        advisory -> enforced_score @full [selective risk]      297  0.3376  0.3600  0.0224  -0.0654   0.1140  -0.0504   0.0956    NaN    NaN 0.6500 bootstrap (selective risk)      0.7980      0.2525     NaN             NaN           NaN
  H3b_score_drop_ans         H3    False    advisory -> enforced_score @drop_ans [selective risk]      297  0.8364  0.5625 -0.2739  -0.5135  -0.0462  -0.4682  -0.0781    NaN    NaN 0.0210 bootstrap (selective risk)      0.3704      0.0539     NaN             NaN           NaN
H3b_score_drop_other         H3    False  advisory -> enforced_score @drop_other [selective risk]      297  0.3261  0.2000 -0.1261  -0.3908   0.3557  -0.3724   0.2361    NaN    NaN 0.4430 bootstrap (selective risk)      0.3098      0.0168     NaN             NaN           NaN
  H3b_score_drop_all         H3    False    advisory -> enforced_score @drop_all [selective risk]      297  1.0000  0.0000 -1.0000  -1.0000  -1.0000  -1.0000  -1.0000    NaN    NaN 0.0005 bootstrap (selective risk)      0.0976      0.0000     NaN             NaN           NaN
                leak    control    False          advisory -> advisory_missing @drop_ans [halluc]      297  0.3098  0.2391 -0.0707  -0.1145  -0.0269  -0.1111  -0.0337   14.0   35.0 0.0038              McNemar exact         NaN         NaN     NaN             NaN           NaN
```

### Restored, by turn-1 status

```
              hallucination       correct      
                       mean count    mean count
turn1_status                                   
abstain               0.160   194   0.593   194
correct               0.000    15   1.000    15
hallucination         0.489    88   0.398    88
```

## Stratum: primary_param_known (items=14)

```
          system      level  n  halluc  h_lo  h_hi  correct  abstain  non_answer  sel_risk  false_refusal  abst_precision  halluc_if_unavail  unsup_correct  tokens
     closed_book          - 14   0.000 0.000 0.000    1.000    0.000       0.000     0.000            NaN             NaN                NaN          0.000  76.714
             off       full 14   0.286 0.071 0.500    0.714    0.000       0.000     0.286          0.000             NaN                NaN          0.000 351.571
             off   drop_ans 14   0.286 0.071 0.500    0.429    0.286       0.000     0.400            NaN             1.0              0.286          0.429 349.857
             off drop_other 14   0.143 0.000 0.357    0.643    0.214       0.000     0.182          0.214             0.0                NaN          0.000 350.429
             off   drop_all 14   0.000 0.000 0.000    0.286    0.714       0.000     0.000            NaN             1.0              0.000          0.286 348.714
        advisory       full 14   0.143 0.000 0.357    0.786    0.071       0.071     0.154          0.071             0.0                NaN          0.000 359.571
        advisory   drop_ans 14   0.357 0.143 0.643    0.357    0.286       0.071     0.500            NaN             1.0              0.357          0.357 357.857
        advisory drop_other 14   0.071 0.000 0.214    0.643    0.286       0.071     0.100          0.286             0.0                NaN          0.000 358.429
        advisory   drop_all 14   0.071 0.000 0.214    0.357    0.571       0.143     0.167            NaN             1.0              0.071          0.357 356.714
advisory_missing       full 14   0.214 0.000 0.429    0.571    0.214       0.000     0.273          0.214             0.0                NaN          0.000 383.857
advisory_missing   drop_ans 14   0.286 0.071 0.500    0.357    0.357       0.000     0.444            NaN             1.0              0.286          0.357 371.214
advisory_missing drop_other 14   0.071 0.000 0.214    0.500    0.429       0.214     0.125          0.429             0.0                NaN          0.000 379.286
advisory_missing   drop_all 14   0.000 0.000 0.000    0.429    0.571       0.143     0.000            NaN             1.0              0.000          0.429 378.571
        enforced       full 14   0.000 0.000 0.000    0.071    0.929       0.000     0.000          0.929             0.0                NaN          0.000 359.571
        enforced   drop_ans 14   0.071 0.000 0.214    0.000    0.929       0.000     1.000            NaN             1.0              0.071          0.000 357.857
        enforced drop_other 14   0.000 0.000 0.000    0.000    1.000       0.000     0.000          1.000             0.0                NaN          0.000 358.429
        enforced   drop_all 14   0.000 0.000 0.000    0.000    1.000       0.000     0.000            NaN             1.0              0.000          0.000 356.714
 enforced_oracle       full 14   0.286 0.071 0.500    0.714    0.000       0.000     0.286          0.000             NaN                NaN          0.000 351.571
 enforced_oracle   drop_ans 14   0.000 0.000 0.000    0.000    1.000       0.000     0.000            NaN             1.0              0.000          0.000 349.857
 enforced_oracle drop_other 14   0.143 0.000 0.357    0.643    0.214       0.000     0.182          0.214             0.0                NaN          0.000 350.429
 enforced_oracle   drop_all 14   0.000 0.000 0.000    0.000    1.000       0.000     0.000            NaN             1.0              0.000          0.000 348.714
   restored_ctrl       full 14   0.357 0.143 0.571    0.571    0.071       0.000     0.385          0.071             0.0                NaN          0.000 693.071
        restored       full 14   0.286 0.071 0.500    0.714    0.000       0.000     0.286          0.000             NaN                NaN          0.000 692.000
  enforced_score       full 14   0.000 0.000 0.000    0.071    0.929       0.000     0.000          0.929             0.0                NaN          0.000 359.571
  enforced_score   drop_ans 14   0.071 0.000 0.214    0.000    0.929       0.000     1.000            NaN             1.0              0.071          0.000 357.857
  enforced_score drop_other 14   0.000 0.000 0.000    0.000    1.000       0.000     0.000          1.000             0.0                NaN          0.000 358.429
  enforced_score   drop_all 14   0.000 0.000 0.000    0.000    1.000       0.000     0.000            NaN             1.0              0.000          0.000 356.714
```

### Risk–coverage (gates on advisory outputs, all levels)

```
   gate_score  n   aurc  ci95_lo  ci95_hi  random_gate
reader_p_suff 56 0.2184   0.0371   0.4346       0.1607
       oracle 56 0.1332   0.0403   0.2655       0.1607
```

### Contrasts (diff = b − a)

```
                  id hypothesis  primary                                                 contrast  n_items  rate_a  rate_b    diff  ci95_lo  ci95_hi  ci90_lo  ci90_hi  a0_b1  a1_b0      p                       test  coverage_a  coverage_b  p_holm tost_equivalent within_margin
                 H1a         H1     True                           off: full -> drop_ans [halluc]       14  0.2857  0.2857  0.0000  -0.2857   0.2857  -0.2143   0.2143    2.0    2.0 1.0000              McNemar exact         NaN         NaN  1.0000             NaN           NaN
                 H1b         H1     True                           off: full -> drop_all [halluc]       14  0.2857  0.0000 -0.2857  -0.5714  -0.0714  -0.5000  -0.0714    0.0    4.0 0.1250              McNemar exact         NaN         NaN  0.6250             NaN           NaN
                 H1c         H1    False                         off: full -> drop_other [halluc]       14  0.2857  0.1429 -0.1429  -0.4286   0.1429  -0.3571   0.0714    1.0    3.0 0.6250              McNemar exact         NaN         NaN     NaN             NaN           NaN
                  H2         H2     True                        off@drop_ans -> restored [halluc]       14  0.2857  0.2857  0.0000  -0.2857   0.2857  -0.2143   0.2143    2.0    2.0 1.0000              McNemar exact         NaN         NaN  1.0000             NaN           NaN
                H2eq         H2    False                restored_ctrl -> restored [halluc] (TOST)       14  0.3571  0.2857 -0.0714  -0.2143   0.0000  -0.2143   0.0000    0.0    1.0 1.0000              McNemar exact         NaN         NaN     NaN           False           NaN
                 H3a         H3     True                       off -> advisory @drop_ans [halluc]       14  0.2857  0.3571  0.0714   0.0000   0.2143   0.0000   0.2143    1.0    0.0 1.0000              McNemar exact         NaN         NaN  1.0000             NaN           NaN
                 H3b         H3     True          advisory -> enforced @drop_ans [selective risk]       14  0.5000  1.0000  0.5000  -0.7000   0.7273  -0.6250   0.6667    NaN    NaN 0.7340 bootstrap (selective risk)      0.7143      0.0714  1.0000             NaN           NaN
                  H4         H4     True off -> enforced @full [false refusal | answer available]       14  0.0000  0.9286  0.9286   0.7857   1.0000   0.7857   1.0000   13.0    0.0 0.0002              McNemar exact         NaN         NaN  0.0015             NaN         False
            H3a_full         H3    False                           off -> advisory @full [halluc]       14  0.2857  0.1429 -0.1429  -0.3571   0.0000  -0.2857   0.0000    0.0    2.0 0.5000              McNemar exact         NaN         NaN     NaN             NaN           NaN
            H3b_full         H3    False              advisory -> enforced @full [selective risk]       14  0.1538  0.0000 -0.1538  -0.3846   0.0000  -0.3333   0.0000    NaN    NaN 0.2250 bootstrap (selective risk)      0.9286      0.0714     NaN             NaN           NaN
      H3a_drop_other         H3    False                     off -> advisory @drop_other [halluc]       14  0.1429  0.0714 -0.0714  -0.2143   0.0000  -0.2143   0.0000    0.0    1.0 1.0000              McNemar exact         NaN         NaN     NaN             NaN           NaN
      H3b_drop_other         H3    False        advisory -> enforced @drop_other [selective risk]       14  0.1000  0.0000 -0.1000  -0.3083   0.0000  -0.2727   0.0000    NaN    NaN 0.7350 bootstrap (selective risk)      0.7143      0.0000     NaN             NaN           NaN
        H3a_drop_all         H3    False                       off -> advisory @drop_all [halluc]       14  0.0000  0.0714  0.0714   0.0000   0.2143   0.0000   0.2143    1.0    0.0 1.0000              McNemar exact         NaN         NaN     NaN             NaN           NaN
        H3b_drop_all         H3    False          advisory -> enforced @drop_all [selective risk]       14  0.1667  0.0000 -0.1667  -0.5000   0.0000  -0.5000   0.0000    NaN    NaN 0.7030 bootstrap (selective risk)      0.4286      0.0000     NaN             NaN           NaN
      H3b_score_full         H3    False        advisory -> enforced_score @full [selective risk]       14  0.1538  0.0000 -0.1538  -0.3571   0.0000  -0.3333   0.0000    NaN    NaN 0.2730 bootstrap (selective risk)      0.9286      0.0714     NaN             NaN           NaN
  H3b_score_drop_ans         H3    False    advisory -> enforced_score @drop_ans [selective risk]       14  0.5000  1.0000  0.5000  -0.7000   0.7273  -0.6250   0.6667    NaN    NaN 0.6750 bootstrap (selective risk)      0.7143      0.0714     NaN             NaN           NaN
H3b_score_drop_other         H3    False  advisory -> enforced_score @drop_other [selective risk]       14  0.1000  0.0000 -0.1000  -0.3333   0.0000  -0.2727   0.0000    NaN    NaN 0.6870 bootstrap (selective risk)      0.7143      0.0000     NaN             NaN           NaN
  H3b_score_drop_all         H3    False    advisory -> enforced_score @drop_all [selective risk]       14  0.1667  0.0000 -0.1667  -0.5000   0.0000  -0.4286   0.0000    NaN    NaN 0.7390 bootstrap (selective risk)      0.4286      0.0000     NaN             NaN           NaN
                leak    control    False          advisory -> advisory_missing @drop_ans [halluc]       14  0.3571  0.2857 -0.0714  -0.3571   0.1429  -0.2857   0.1429    1.0    2.0 1.0000              McNemar exact         NaN         NaN     NaN             NaN           NaN
```

### Restored, by turn-1 status

```
              hallucination       correct      
                       mean count    mean count
turn1_status                                   
abstain               0.250     4   0.750     4
correct               0.167     6   0.833     6
hallucination         0.500     4   0.500     4
```

## Stratum: all (items=500)

```
          system      level   n  halluc  h_lo  h_hi  correct  abstain  non_answer  sel_risk  false_refusal  abst_precision  halluc_if_unavail  unsup_correct  tokens
     closed_book          - 500   0.150 0.118 0.184    0.076    0.774       0.000     0.664            NaN             NaN                NaN          0.000  78.022
             off       full 493   0.237 0.201 0.276    0.535    0.227       0.020     0.307          0.226           0.009              0.000          0.002 376.385
             off   drop_ans 493   0.239 0.203 0.276    0.099    0.661       0.020     0.707          0.548           0.825              0.247          0.049 374.613
             off drop_other 493   0.101 0.075 0.128    0.237    0.661       0.016     0.299          0.643           0.089              0.032          0.002 374.903
             off   drop_all 493   0.067 0.045 0.091    0.010    0.923       0.006     0.868            NaN           1.000              0.067          0.010 373.130
        advisory       full 493   0.213 0.178 0.249    0.552    0.235       0.144     0.279          0.234           0.009              0.000          0.002 384.385
        advisory   drop_ans 493   0.245 0.207 0.284    0.114    0.641       0.266     0.684          0.567           0.813              0.262          0.061 382.613
        advisory drop_other 493   0.091 0.067 0.118    0.241    0.667       0.260     0.274          0.660           0.073              0.161          0.004 382.903
        advisory   drop_all 493   0.081 0.059 0.105    0.016    0.903       0.217     0.833            NaN           1.000              0.081          0.016 381.130
advisory_missing       full 493   0.193 0.160 0.227    0.501    0.306       0.128     0.278          0.308           0.000              0.000          0.004 401.675
advisory_missing   drop_ans 493   0.195 0.158 0.229    0.114    0.692       0.130     0.632          0.606           0.815              0.203          0.065 403.379
advisory_missing drop_other 493   0.087 0.063 0.112    0.243    0.669       0.140     0.264          0.649           0.091              0.000          0.002 403.493
advisory_missing   drop_all 493   0.079 0.057 0.103    0.026    0.895       0.112     0.750            NaN           1.000              0.079          0.026 403.278
        enforced       full 493   0.059 0.039 0.081    0.152    0.789       0.002     0.279          0.790           0.003              0.000          0.002 384.385
        enforced   drop_ans 493   0.026 0.012 0.041    0.016    0.957       0.000     0.619          0.962           0.788              0.026          0.014 382.613
        enforced drop_other 493   0.006 0.000 0.014    0.016    0.978       0.000     0.273          0.976           0.064              0.000          0.000 382.903
        enforced   drop_all 493   0.002 0.000 0.006    0.000    0.998       0.000     1.000            NaN           1.000              0.002          0.000 381.130
 enforced_oracle       full 493   0.237 0.203 0.276    0.533    0.229       0.020     0.308          0.226           0.018              0.000          0.000 376.385
 enforced_oracle   drop_ans 493   0.045 0.026 0.065    0.051    0.905       0.008     0.468          0.548           0.872              0.000          0.000 374.613
 enforced_oracle drop_other 493   0.099 0.073 0.126    0.235    0.665       0.016     0.297          0.643           0.095              0.000          0.000 374.903
 enforced_oracle   drop_all 493   0.000 0.000 0.000    0.000    1.000       0.000     0.000            NaN           1.000              0.000          0.000 373.130
   restored_ctrl       full 493   0.189 0.154 0.225    0.570    0.241       0.006     0.249          0.242           0.000              0.000          0.004 744.314
        restored       full 493   0.205 0.172 0.239    0.564    0.231       0.008     0.266          0.232           0.000              0.000          0.004 743.404
  enforced_score       full 493   0.059 0.039 0.079    0.156    0.785       0.002     0.274          0.786           0.003              0.000          0.002 384.385
  enforced_score   drop_ans 493   0.026 0.012 0.043    0.016    0.957       0.000     0.619          0.962           0.788              0.026          0.014 382.613
  enforced_score drop_other 493   0.006 0.000 0.014    0.016    0.978       0.000     0.273          0.976           0.064              0.000          0.000 382.903
  enforced_score   drop_all 493   0.002 0.000 0.006    0.000    0.998       0.000     1.000            NaN           1.000              0.002          0.000 381.130
```

### Risk–coverage (gates on advisory outputs, all levels)

```
   gate_score    n   aurc  ci95_lo  ci95_hi  random_gate
reader_p_suff 1972 0.2621   0.2237   0.3006       0.1577
       oracle 1972 0.1574   0.1340   0.1832       0.1577
```

### Contrasts (diff = b − a)

```
                  id hypothesis  primary                                                 contrast  n_items  rate_a  rate_b    diff  ci95_lo  ci95_hi  ci90_lo  ci90_hi  a0_b1  a1_b0      p                       test  coverage_a  coverage_b  p_holm tost_equivalent within_margin
                 H1a         H1     True                           off: full -> drop_ans [halluc]      493  0.2373  0.2394  0.0020  -0.0446   0.0467  -0.0385   0.0406   66.0   65.0 1.0000              McNemar exact         NaN         NaN  1.0000             NaN           NaN
                 H1b         H1     True                           off: full -> drop_all [halluc]      493  0.2373  0.0669 -0.1704  -0.2130  -0.1318  -0.2049  -0.1379   18.0  102.0 0.0000              McNemar exact         NaN         NaN  0.0000             NaN           NaN
                 H1c         H1    False                         off: full -> drop_other [halluc]      493  0.2373  0.1014 -0.1359  -0.1724  -0.0974  -0.1663  -0.1034   16.0   83.0 0.0000              McNemar exact         NaN         NaN     NaN             NaN           NaN
                  H2         H2     True                        off@drop_ans -> restored [halluc]      493  0.2394  0.2049 -0.0345  -0.0771   0.0061  -0.0710   0.0000   47.0   64.0 0.1285              McNemar exact         NaN         NaN  0.5139             NaN           NaN
                H2eq         H2    False                restored_ctrl -> restored [halluc] (TOST)      493  0.1886  0.2049  0.0162  -0.0183   0.0507  -0.0122   0.0446   39.0   31.0 0.4030              McNemar exact         NaN         NaN     NaN            True           NaN
                 H3a         H3     True                       off -> advisory @drop_ans [halluc]      493  0.2394  0.2454  0.0061  -0.0162   0.0264  -0.0122   0.0243   16.0   13.0 0.7111              McNemar exact         NaN         NaN  1.0000             NaN           NaN
                 H3b         H3     True          advisory -> enforced @drop_ans [selective risk]      493  0.6836  0.6190 -0.0646  -0.2589   0.1187  -0.2321   0.0944    NaN    NaN 0.5430 bootstrap (selective risk)      0.3590      0.0426  1.0000             NaN           NaN
                  H4         H4     True off -> enforced @full [false refusal | answer available]      491  0.2261  0.7902  0.5642   0.5193   0.6090   0.5255   0.6008  277.0    0.0 0.0000              McNemar exact         NaN         NaN  0.0000             NaN         False
            H3a_full         H3    False                           off -> advisory @full [halluc]      493  0.2373  0.2130 -0.0243  -0.0487   0.0020  -0.0446  -0.0041   14.0   26.0 0.0807              McNemar exact         NaN         NaN     NaN             NaN           NaN
            H3b_full         H3    False              advisory -> enforced @full [selective risk]      493  0.2785  0.2788  0.0003  -0.0722   0.0730  -0.0616   0.0619    NaN    NaN 0.9980 bootstrap (selective risk)      0.7647      0.2110     NaN             NaN           NaN
      H3a_drop_other         H3    False                     off -> advisory @drop_other [halluc]      493  0.1014  0.0913 -0.0101  -0.0304   0.0081  -0.0264   0.0061    9.0   14.0 0.4049              McNemar exact         NaN         NaN     NaN             NaN           NaN
      H3b_drop_other         H3    False        advisory -> enforced @drop_other [selective risk]      493  0.2744  0.2727 -0.0017  -0.2586   0.2825  -0.2145   0.2262    NaN    NaN 0.9560 bootstrap (selective risk)      0.3327      0.0223     NaN             NaN           NaN
        H3a_drop_all         H3    False                       off -> advisory @drop_all [halluc]      493  0.0669  0.0811  0.0142  -0.0020   0.0325   0.0000   0.0284   13.0    6.0 0.1671              McNemar exact         NaN         NaN     NaN             NaN           NaN
        H3b_drop_all         H3    False          advisory -> enforced @drop_all [selective risk]      493  0.8333  1.0000  0.1667  -0.9048   0.2609  -0.8864   0.2439    NaN    NaN 0.7100 bootstrap (selective risk)      0.0974      0.0020     NaN             NaN           NaN
      H3b_score_full         H3    False        advisory -> enforced_score @full [selective risk]      493  0.2785  0.2736 -0.0049  -0.0785   0.0663  -0.0685   0.0556    NaN    NaN 0.8960 bootstrap (selective risk)      0.7647      0.2150     NaN             NaN           NaN
  H3b_score_drop_ans         H3    False    advisory -> enforced_score @drop_ans [selective risk]      493  0.6836  0.6190 -0.0646  -0.2698   0.1247  -0.2375   0.0955    NaN    NaN 0.5420 bootstrap (selective risk)      0.3590      0.0426     NaN             NaN           NaN
H3b_score_drop_other         H3    False  advisory -> enforced_score @drop_other [selective risk]      493  0.2744  0.2727 -0.0017  -0.2624   0.2855  -0.2234   0.2278    NaN    NaN 0.9430 bootstrap (selective risk)      0.3327      0.0223     NaN             NaN           NaN
  H3b_score_drop_all         H3    False    advisory -> enforced_score @drop_all [selective risk]      493  0.8333  1.0000  0.1667  -0.9024   0.2619  -0.8864   0.2433    NaN    NaN 0.7670 bootstrap (selective risk)      0.0974      0.0020     NaN             NaN           NaN
                leak    control    False          advisory -> advisory_missing @drop_ans [halluc]      493  0.2454  0.1947 -0.0507  -0.0832  -0.0203  -0.0771  -0.0243   20.0   45.0 0.0026              McNemar exact         NaN         NaN     NaN             NaN           NaN
```

### Restored, by turn-1 status

```
              hallucination       correct      
                       mean count    mean count
turn1_status                                   
abstain               0.141   326   0.555   326
correct               0.020    49   0.918    49
hallucination         0.458   118   0.441   118
```