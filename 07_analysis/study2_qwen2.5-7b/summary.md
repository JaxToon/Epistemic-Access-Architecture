# Study 2 — evidence-anchored confabulation (qwen2.5-7b)

items: 396 · primary: 255 · judge_missing: 0

## Manipulation check

```
   level      policy  filler_density  len_ratio  answer_in_packet
drop_all entity_poor           1.585      0.989               0.0
drop_all entity_rich           4.741      0.996               0.0
drop_ans entity_poor           1.580      0.994               0.0
drop_ans entity_rich           4.631      0.997               0.0
    full      length             NaN      1.000               1.0
```

## Outcomes (primary)

```
    prompt    level      policy   n  correct  halluc  abstain  answered  halluc_n  sel_risk
extractive drop_all entity_poor 255    0.008   0.055    0.937        16        14     0.875
extractive drop_all entity_rich 255    0.004   0.090    0.906        24        23     0.958
extractive drop_ans entity_poor 255    0.082   0.251    0.667        85        64     0.753
extractive drop_ans entity_rich 255    0.067   0.231    0.702        76        59     0.776
extractive     full      length 255    0.663   0.157    0.180       209        40     0.191
      open drop_all entity_poor 255    0.008   0.016    0.976         6         4     0.667
      open drop_all entity_rich 255    0.004   0.035    0.961        10         9     0.900
      open drop_ans entity_poor 255    0.051   0.098    0.851        38        25     0.658
      open drop_ans entity_rich 255    0.055   0.106    0.839        41        27     0.659
      open     full      length 255    0.494   0.129    0.376       159        33     0.208
```

## Confirmatory contrasts (rich − poor)

```
         id     prompt    level  n_items  halluc_poor  halluc_rich    diff   ci_lo  ci_hi  poor0_rich1  poor1_rich0      p  abstain_poor  abstain_rich  p_holm
      S2-H1 extractive drop_ans      255       0.2510       0.2314 -0.0196 -0.0511 0.0118            6           11 0.3323        0.6667        0.7020  0.6646
      S2-H2 extractive drop_all      255       0.0549       0.0902  0.0353  0.0078 0.0667           11            2 0.0225        0.9373        0.9059  0.0674
S2-H1(open)       open drop_ans      255       0.0980       0.1059  0.0078 -0.0157 0.0314            5            3 0.7266        0.8510        0.8392  0.7266
S2-H2(open)       open drop_all      255       0.0157       0.0353  0.0196  0.0039 0.0392            5            0 0.0625        0.9765        0.9608     NaN
```

## Source of hallucinated answers (S2-H3 / S2-H4: drop_ans rows)

```
    prompt    level  n_halluc  copied_from_packet  wilson_lo  wilson_hi  from_gold_unit  from_filler  not_in_packet
extractive     full        40               0.850      0.709      0.929           0.775        0.075          0.150
extractive drop_ans       123               0.837      0.762      0.892           0.642        0.195          0.163
extractive drop_all        37               0.919      0.787      0.972           0.000        0.919          0.081
      open     full        33               0.879      0.727      0.952           0.818        0.061          0.121
      open drop_ans        52               0.846      0.725      0.920           0.712        0.135          0.154
      open drop_all        13               0.923      0.667      0.986           0.000        0.923          0.077
```
