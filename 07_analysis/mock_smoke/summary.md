# Analysis — mock_smoke

Items: 30 · primary population: 21 · qclass: {'open': 22, 'answer_in_question': 4, 'yesno': 4}

## Channel manipulation check (off)

```
            answer_available  gold_kept  len_ratio_min  len_ratio_max      tokens
level                                                                            
full                1.000000   1.000000       1.000000       1.000000  215.266667
drop_ans            0.033333   0.505556       0.920213       1.012821  214.366667
drop_other          0.866667   0.494444       0.907801       1.012821  214.833333
drop_all            0.000000   0.000000       0.907801       1.025641  213.933333
```

## Reader verdict vs answer availability (off rows)

```
answer_available  0.0  1.0
reader_verdict            
INSUFFICIENT       58   50
SUFFICIENT          5    7
```

Reader `missing` leak rate: 0.00%


## Stratum: primary (items=21)

```
          system      level  n  halluc  h_lo  h_hi  correct  abstain  non_answer  sel_risk  false_refusal  abst_precision  halluc_if_unavail  unsup_correct  tokens
     closed_book          - 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0            NaN             NaN                NaN            0.0  47.952
             off       full 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 222.143
             off   drop_ans 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0            NaN             NaN              1.000            0.0 220.905
             off drop_other 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 222.238
             off   drop_all 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0            NaN             NaN              1.000            0.0 221.000
        advisory       full 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 226.143
        advisory   drop_ans 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0            NaN             NaN              1.000            0.0 224.905
        advisory drop_other 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 226.238
        advisory   drop_all 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0            NaN             NaN              1.000            0.0 225.000
advisory_missing       full 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 226.143
advisory_missing   drop_ans 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0            NaN             NaN              1.000            0.0 224.905
advisory_missing drop_other 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 226.238
advisory_missing   drop_all 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0            NaN             NaN              1.000            0.0 225.000
        enforced       full 21   0.095 0.000 0.238      0.0    0.905         0.0       1.0          0.905             0.0                NaN            0.0 226.143
        enforced   drop_ans 21   0.095 0.000 0.238      0.0    0.905         0.0       1.0            NaN             1.0              0.095            0.0 224.905
        enforced drop_other 21   0.095 0.000 0.238      0.0    0.905         0.0       1.0          0.905             0.0                NaN            0.0 226.238
        enforced   drop_all 21   0.095 0.000 0.238      0.0    0.905         0.0       1.0            NaN             1.0              0.095            0.0 225.000
 enforced_oracle       full 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 222.143
 enforced_oracle   drop_ans 21   0.000 0.000 0.000      0.0    1.000         0.0       0.0            NaN             1.0              0.000            0.0 220.905
 enforced_oracle drop_other 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 222.238
 enforced_oracle   drop_all 21   0.000 0.000 0.000      0.0    1.000         0.0       0.0            NaN             1.0              0.000            0.0 221.000
   restored_ctrl       full 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 442.810
        restored       full 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 441.762
  enforced_score       full 21   0.762 0.571 0.905      0.0    0.238         0.0       1.0          0.238             0.0                NaN            0.0 226.143
  enforced_score   drop_ans 21   0.524 0.333 0.714      0.0    0.476         0.0       1.0            NaN             1.0              0.524            0.0 224.905
  enforced_score drop_other 21   0.667 0.476 0.857      0.0    0.333         0.0       1.0          0.333             0.0                NaN            0.0 226.238
  enforced_score   drop_all 21   0.762 0.571 0.905      0.0    0.238         0.0       1.0            NaN             1.0              0.762            0.0 225.000
```

### Risk–coverage (gates on advisory outputs, all levels)

```
   gate_score  n  aurc  ci95_lo  ci95_hi  random_gate
reader_p_suff 84   1.0      1.0      1.0          1.0
       oracle 84   1.0      1.0      1.0          1.0
```

### Contrasts (diff = b − a)

```
                  id hypothesis  primary                                                 contrast  n_items  rate_a  rate_b   diff  ci95_lo  ci95_hi  ci90_lo  ci90_hi  a0_b1  a1_b0     p                       test  coverage_a  coverage_b  p_holm tost_equivalent within_margin
                 H1a         H1     True                           off: full -> drop_ans [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     1.0             NaN           NaN
                 H1b         H1     True                           off: full -> drop_all [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     1.0             NaN           NaN
                 H1c         H1    False                         off: full -> drop_other [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN             NaN           NaN
                  H2         H2     True                        off@drop_ans -> restored [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     1.0             NaN           NaN
                H2eq         H2    False                restored_ctrl -> restored [halluc] (TOST)       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN            True           NaN
                 H3a         H3     True                       off -> advisory @drop_ans [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     1.0             NaN           NaN
                 H3b         H3     True          advisory -> enforced @drop_ans [selective risk]       21     1.0  1.0000 0.0000  -1.0000      0.0  -1.0000      0.0    NaN    NaN 1.768 bootstrap (selective risk)         1.0      0.0952     1.0             NaN           NaN
                  H4         H4     True off -> enforced @full [false refusal | answer available]       21     0.0  0.9048 0.9048   0.7619      1.0   0.8095      1.0   19.0    0.0 0.000              McNemar exact         NaN         NaN     0.0             NaN         False
            H3a_full         H3    False                           off -> advisory @full [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN             NaN           NaN
            H3b_full         H3    False              advisory -> enforced @full [selective risk]       21     1.0  1.0000 0.0000  -1.0000      0.0  -1.0000      0.0    NaN    NaN 1.740 bootstrap (selective risk)         1.0      0.0952     NaN             NaN           NaN
      H3a_drop_other         H3    False                     off -> advisory @drop_other [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN             NaN           NaN
      H3b_drop_other         H3    False        advisory -> enforced @drop_other [selective risk]       21     1.0  1.0000 0.0000  -1.0000      0.0  -1.0000      0.0    NaN    NaN 1.756 bootstrap (selective risk)         1.0      0.0952     NaN             NaN           NaN
        H3a_drop_all         H3    False                       off -> advisory @drop_all [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN             NaN           NaN
        H3b_drop_all         H3    False          advisory -> enforced @drop_all [selective risk]       21     1.0  1.0000 0.0000  -1.0000      0.0  -1.0000      0.0    NaN    NaN 1.765 bootstrap (selective risk)         1.0      0.0952     NaN             NaN           NaN
      H3b_score_full         H3    False        advisory -> enforced_score @full [selective risk]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    NaN    NaN 2.000 bootstrap (selective risk)         1.0      0.7619     NaN             NaN           NaN
  H3b_score_drop_ans         H3    False    advisory -> enforced_score @drop_ans [selective risk]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    NaN    NaN 2.000 bootstrap (selective risk)         1.0      0.5238     NaN             NaN           NaN
H3b_score_drop_other         H3    False  advisory -> enforced_score @drop_other [selective risk]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    NaN    NaN 2.000 bootstrap (selective risk)         1.0      0.6667     NaN             NaN           NaN
  H3b_score_drop_all         H3    False    advisory -> enforced_score @drop_all [selective risk]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    NaN    NaN 2.000 bootstrap (selective risk)         1.0      0.7619     NaN             NaN           NaN
                leak    control    False          advisory -> advisory_missing @drop_ans [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN             NaN           NaN
```

### Restored, by turn-1 status

```
              hallucination       correct      
                       mean count    mean count
turn1_status                                   
hallucination           1.0    21     0.0    21
```

## Stratum: primary_param_unknown (items=21)

```
          system      level  n  halluc  h_lo  h_hi  correct  abstain  non_answer  sel_risk  false_refusal  abst_precision  halluc_if_unavail  unsup_correct  tokens
     closed_book          - 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0            NaN             NaN                NaN            0.0  47.952
             off       full 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 222.143
             off   drop_ans 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0            NaN             NaN              1.000            0.0 220.905
             off drop_other 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 222.238
             off   drop_all 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0            NaN             NaN              1.000            0.0 221.000
        advisory       full 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 226.143
        advisory   drop_ans 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0            NaN             NaN              1.000            0.0 224.905
        advisory drop_other 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 226.238
        advisory   drop_all 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0            NaN             NaN              1.000            0.0 225.000
advisory_missing       full 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 226.143
advisory_missing   drop_ans 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0            NaN             NaN              1.000            0.0 224.905
advisory_missing drop_other 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 226.238
advisory_missing   drop_all 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0            NaN             NaN              1.000            0.0 225.000
        enforced       full 21   0.095 0.000 0.238      0.0    0.905         0.0       1.0          0.905             0.0                NaN            0.0 226.143
        enforced   drop_ans 21   0.095 0.000 0.238      0.0    0.905         0.0       1.0            NaN             1.0              0.095            0.0 224.905
        enforced drop_other 21   0.095 0.000 0.238      0.0    0.905         0.0       1.0          0.905             0.0                NaN            0.0 226.238
        enforced   drop_all 21   0.095 0.000 0.238      0.0    0.905         0.0       1.0            NaN             1.0              0.095            0.0 225.000
 enforced_oracle       full 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 222.143
 enforced_oracle   drop_ans 21   0.000 0.000 0.000      0.0    1.000         0.0       0.0            NaN             1.0              0.000            0.0 220.905
 enforced_oracle drop_other 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 222.238
 enforced_oracle   drop_all 21   0.000 0.000 0.000      0.0    1.000         0.0       0.0            NaN             1.0              0.000            0.0 221.000
   restored_ctrl       full 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 442.810
        restored       full 21   1.000 1.000 1.000      0.0    0.000         0.0       1.0          0.000             NaN                NaN            0.0 441.762
  enforced_score       full 21   0.762 0.571 0.905      0.0    0.238         0.0       1.0          0.238             0.0                NaN            0.0 226.143
  enforced_score   drop_ans 21   0.524 0.286 0.762      0.0    0.476         0.0       1.0            NaN             1.0              0.524            0.0 224.905
  enforced_score drop_other 21   0.667 0.476 0.857      0.0    0.333         0.0       1.0          0.333             0.0                NaN            0.0 226.238
  enforced_score   drop_all 21   0.762 0.571 0.905      0.0    0.238         0.0       1.0            NaN             1.0              0.762            0.0 225.000
```

### Risk–coverage (gates on advisory outputs, all levels)

```
   gate_score  n  aurc  ci95_lo  ci95_hi  random_gate
reader_p_suff 84   1.0      1.0      1.0          1.0
       oracle 84   1.0      1.0      1.0          1.0
```

### Contrasts (diff = b − a)

```
                  id hypothesis  primary                                                 contrast  n_items  rate_a  rate_b   diff  ci95_lo  ci95_hi  ci90_lo  ci90_hi  a0_b1  a1_b0     p                       test  coverage_a  coverage_b  p_holm tost_equivalent within_margin
                 H1a         H1     True                           off: full -> drop_ans [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     1.0             NaN           NaN
                 H1b         H1     True                           off: full -> drop_all [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     1.0             NaN           NaN
                 H1c         H1    False                         off: full -> drop_other [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN             NaN           NaN
                  H2         H2     True                        off@drop_ans -> restored [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     1.0             NaN           NaN
                H2eq         H2    False                restored_ctrl -> restored [halluc] (TOST)       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN            True           NaN
                 H3a         H3     True                       off -> advisory @drop_ans [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     1.0             NaN           NaN
                 H3b         H3     True          advisory -> enforced @drop_ans [selective risk]       21     1.0  1.0000 0.0000  -1.0000      0.0  -1.0000      0.0    NaN    NaN 1.756 bootstrap (selective risk)         1.0      0.0952     1.0             NaN           NaN
                  H4         H4     True off -> enforced @full [false refusal | answer available]       21     0.0  0.9048 0.9048   0.7619      1.0   0.8095      1.0   19.0    0.0 0.000              McNemar exact         NaN         NaN     0.0             NaN         False
            H3a_full         H3    False                           off -> advisory @full [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN             NaN           NaN
            H3b_full         H3    False              advisory -> enforced @full [selective risk]       21     1.0  1.0000 0.0000  -1.0000      0.0  -1.0000      0.0    NaN    NaN 1.742 bootstrap (selective risk)         1.0      0.0952     NaN             NaN           NaN
      H3a_drop_other         H3    False                     off -> advisory @drop_other [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN             NaN           NaN
      H3b_drop_other         H3    False        advisory -> enforced @drop_other [selective risk]       21     1.0  1.0000 0.0000  -1.0000      0.0  -1.0000      0.0    NaN    NaN 1.772 bootstrap (selective risk)         1.0      0.0952     NaN             NaN           NaN
        H3a_drop_all         H3    False                       off -> advisory @drop_all [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN             NaN           NaN
        H3b_drop_all         H3    False          advisory -> enforced @drop_all [selective risk]       21     1.0  1.0000 0.0000  -1.0000      0.0  -1.0000      0.0    NaN    NaN 1.764 bootstrap (selective risk)         1.0      0.0952     NaN             NaN           NaN
      H3b_score_full         H3    False        advisory -> enforced_score @full [selective risk]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    NaN    NaN 2.000 bootstrap (selective risk)         1.0      0.7619     NaN             NaN           NaN
  H3b_score_drop_ans         H3    False    advisory -> enforced_score @drop_ans [selective risk]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    NaN    NaN 2.000 bootstrap (selective risk)         1.0      0.5238     NaN             NaN           NaN
H3b_score_drop_other         H3    False  advisory -> enforced_score @drop_other [selective risk]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    NaN    NaN 2.000 bootstrap (selective risk)         1.0      0.6667     NaN             NaN           NaN
  H3b_score_drop_all         H3    False    advisory -> enforced_score @drop_all [selective risk]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    NaN    NaN 2.000 bootstrap (selective risk)         1.0      0.7619     NaN             NaN           NaN
                leak    control    False          advisory -> advisory_missing @drop_ans [halluc]       21     1.0  1.0000 0.0000   0.0000      0.0   0.0000      0.0    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN             NaN           NaN
```

### Restored, by turn-1 status

```
              hallucination       correct      
                       mean count    mean count
turn1_status                                   
hallucination           1.0    21     0.0    21
```

## Stratum: all (items=30)

```
          system      level  n  halluc  h_lo  h_hi  correct  abstain  non_answer  sel_risk  false_refusal  abst_precision  halluc_if_unavail  unsup_correct  tokens
     closed_book          - 30   1.000 1.000 1.000    0.000    0.000         0.0     1.000            NaN             NaN                NaN            0.0  46.133
             off       full 30   0.967 0.900 1.000    0.033    0.000         0.0     0.967          0.000             NaN                NaN            0.0 215.267
             off   drop_ans 30   1.000 1.000 1.000    0.000    0.000         0.0     1.000          0.000             NaN              1.000            0.0 214.367
             off drop_other 30   0.967 0.900 1.000    0.033    0.000         0.0     0.967          0.000             NaN              1.000            0.0 214.833
             off   drop_all 30   1.000 1.000 1.000    0.000    0.000         0.0     1.000            NaN             NaN              1.000            0.0 213.933
        advisory       full 30   0.967 0.900 1.000    0.033    0.000         0.0     0.967          0.000             NaN                NaN            0.0 219.267
        advisory   drop_ans 30   1.000 1.000 1.000    0.000    0.000         0.0     1.000          0.000             NaN              1.000            0.0 218.367
        advisory drop_other 30   0.967 0.900 1.000    0.033    0.000         0.0     0.967          0.000             NaN              1.000            0.0 218.833
        advisory   drop_all 30   1.000 1.000 1.000    0.000    0.000         0.0     1.000            NaN             NaN              1.000            0.0 217.933
advisory_missing       full 30   0.967 0.900 1.000    0.033    0.000         0.0     0.967          0.000             NaN                NaN            0.0 219.267
advisory_missing   drop_ans 30   1.000 1.000 1.000    0.000    0.000         0.0     1.000          0.000             NaN              1.000            0.0 218.367
advisory_missing drop_other 30   0.967 0.900 1.000    0.033    0.000         0.0     0.967          0.000             NaN              1.000            0.0 218.833
advisory_missing   drop_all 30   1.000 1.000 1.000    0.000    0.000         0.0     1.000            NaN             NaN              1.000            0.0 217.933
        enforced       full 30   0.100 0.000 0.200    0.000    0.900         0.0     1.000          0.900           0.000                NaN            0.0 219.267
        enforced   drop_ans 30   0.100 0.000 0.233    0.000    0.900         0.0     1.000          0.000           1.000              0.069            0.0 218.367
        enforced drop_other 30   0.100 0.000 0.200    0.000    0.900         0.0     1.000          0.885           0.148              0.000            0.0 218.833
        enforced   drop_all 30   0.100 0.000 0.200    0.000    0.900         0.0     1.000            NaN           1.000              0.100            0.0 217.933
 enforced_oracle       full 30   0.967 0.900 1.000    0.033    0.000         0.0     0.967          0.000             NaN                NaN            0.0 215.267
 enforced_oracle   drop_ans 30   0.033 0.000 0.100    0.000    0.967         0.0     1.000          0.000           1.000              0.000            0.0 214.367
 enforced_oracle drop_other 30   0.833 0.700 0.967    0.033    0.133         0.0     0.962          0.000           1.000              0.000            0.0 214.833
 enforced_oracle   drop_all 30   0.000 0.000 0.000    0.000    1.000         0.0     0.000            NaN           1.000              0.000            0.0 213.933
   restored_ctrl       full 30   1.000 1.000 1.000    0.000    0.000         0.0     1.000          0.000             NaN                NaN            0.0 428.933
        restored       full 30   1.000 1.000 1.000    0.000    0.000         0.0     1.000          0.000             NaN                NaN            0.0 428.233
  enforced_score       full 30   0.733 0.567 0.867    0.033    0.233         0.0     0.957          0.233           0.000                NaN            0.0 219.267
  enforced_score   drop_ans 30   0.567 0.400 0.733    0.000    0.433         0.0     1.000          1.000           0.923              0.586            0.0 218.367
  enforced_score drop_other 30   0.667 0.500 0.833    0.033    0.300         0.0     0.952          0.308           0.111              0.750            0.0 218.833
  enforced_score   drop_all 30   0.767 0.600 0.900    0.000    0.233         0.0     1.000            NaN           1.000              0.767            0.0 217.933
```

### Risk–coverage (gates on advisory outputs, all levels)

```
   gate_score   n   aurc  ci95_lo  ci95_hi  random_gate
reader_p_suff 120 0.9847   0.9137      1.0       0.9833
       oracle 120 0.9825   0.9383      1.0       0.9833
```

### Contrasts (diff = b − a)

```
                  id hypothesis  primary                                                 contrast  n_items  rate_a  rate_b    diff  ci95_lo  ci95_hi  ci90_lo  ci90_hi  a0_b1  a1_b0     p                       test  coverage_a  coverage_b  p_holm tost_equivalent within_margin
                 H1a         H1     True                           off: full -> drop_ans [halluc]       30  0.9667  1.0000  0.0333   0.0000      0.1   0.0000   0.1000    1.0    0.0 1.000              McNemar exact         NaN         NaN     1.0             NaN           NaN
                 H1b         H1     True                           off: full -> drop_all [halluc]       30  0.9667  1.0000  0.0333   0.0000      0.1   0.0000   0.1000    1.0    0.0 1.000              McNemar exact         NaN         NaN     1.0             NaN           NaN
                 H1c         H1    False                         off: full -> drop_other [halluc]       30  0.9667  0.9667  0.0000   0.0000      0.0   0.0000   0.0000    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN             NaN           NaN
                  H2         H2     True                        off@drop_ans -> restored [halluc]       30  1.0000  1.0000  0.0000   0.0000      0.0   0.0000   0.0000    0.0    0.0 1.000              McNemar exact         NaN         NaN     1.0             NaN           NaN
                H2eq         H2    False                restored_ctrl -> restored [halluc] (TOST)       30  1.0000  1.0000  0.0000   0.0000      0.0   0.0000   0.0000    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN            True           NaN
                 H3a         H3     True                       off -> advisory @drop_ans [halluc]       30  1.0000  1.0000  0.0000   0.0000      0.0   0.0000   0.0000    0.0    0.0 1.000              McNemar exact         NaN         NaN     1.0             NaN           NaN
                 H3b         H3     True          advisory -> enforced @drop_ans [selective risk]       30  1.0000  1.0000  0.0000  -1.0000      0.0   0.0000   0.0000    NaN    NaN 1.929 bootstrap (selective risk)         1.0      0.1000     1.0             NaN           NaN
                  H4         H4     True off -> enforced @full [false refusal | answer available]       30  0.0000  0.9000  0.9000   0.7667      1.0   0.8000   0.9667   27.0    0.0 0.000              McNemar exact         NaN         NaN     0.0             NaN         False
            H3a_full         H3    False                           off -> advisory @full [halluc]       30  0.9667  0.9667  0.0000   0.0000      0.0   0.0000   0.0000    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN             NaN           NaN
            H3b_full         H3    False              advisory -> enforced @full [selective risk]       30  0.9667  1.0000  0.0333  -0.9667      0.1   0.0000   0.1000    NaN    NaN 0.775 bootstrap (selective risk)         1.0      0.1000     NaN             NaN           NaN
      H3a_drop_other         H3    False                     off -> advisory @drop_other [halluc]       30  0.9667  0.9667  0.0000   0.0000      0.0   0.0000   0.0000    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN             NaN           NaN
      H3b_drop_other         H3    False        advisory -> enforced @drop_other [selective risk]       30  0.9667  1.0000  0.0333  -0.9333      0.1   0.0000   0.1000    NaN    NaN 0.744 bootstrap (selective risk)         1.0      0.1000     NaN             NaN           NaN
        H3a_drop_all         H3    False                       off -> advisory @drop_all [halluc]       30  1.0000  1.0000  0.0000   0.0000      0.0   0.0000   0.0000    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN             NaN           NaN
        H3b_drop_all         H3    False          advisory -> enforced @drop_all [selective risk]       30  1.0000  1.0000  0.0000  -1.0000      0.0   0.0000   0.0000    NaN    NaN 1.916 bootstrap (selective risk)         1.0      0.1000     NaN             NaN           NaN
      H3b_score_full         H3    False        advisory -> enforced_score @full [selective risk]       30  0.9667  0.9565 -0.0101  -0.0386      0.0  -0.0333   0.0000    NaN    NaN 0.717 bootstrap (selective risk)         1.0      0.7667     NaN             NaN           NaN
  H3b_score_drop_ans         H3    False    advisory -> enforced_score @drop_ans [selective risk]       30  1.0000  1.0000  0.0000   0.0000      0.0   0.0000   0.0000    NaN    NaN 2.000 bootstrap (selective risk)         1.0      0.5667     NaN             NaN           NaN
H3b_score_drop_other         H3    False  advisory -> enforced_score @drop_other [selective risk]       30  0.9667  0.9524 -0.0143  -0.0571      0.0  -0.0429   0.0000    NaN    NaN 0.726 bootstrap (selective risk)         1.0      0.7000     NaN             NaN           NaN
  H3b_score_drop_all         H3    False    advisory -> enforced_score @drop_all [selective risk]       30  1.0000  1.0000  0.0000   0.0000      0.0   0.0000   0.0000    NaN    NaN 2.000 bootstrap (selective risk)         1.0      0.7667     NaN             NaN           NaN
                leak    control    False          advisory -> advisory_missing @drop_ans [halluc]       30  1.0000  1.0000  0.0000   0.0000      0.0   0.0000   0.0000    0.0    0.0 1.000              McNemar exact         NaN         NaN     NaN             NaN           NaN
```

### Restored, by turn-1 status

```
              hallucination       correct      
                       mean count    mean count
turn1_status                                   
hallucination           1.0    30     0.0    30
```