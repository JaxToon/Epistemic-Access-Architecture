# Study 2 — evidence-anchored confabulation (qwen2.5-3b)

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
extractive drop_all entity_poor 255    0.004   0.102    0.894        27        26     0.963
extractive drop_all entity_rich 255    0.004   0.098    0.898        26        25     0.962
extractive drop_ans entity_poor 255    0.063   0.318    0.620        97        81     0.835
extractive drop_ans entity_rich 255    0.063   0.333    0.604       101        85     0.842
extractive     full      length 255    0.490   0.278    0.231       196        71     0.362
      open drop_all entity_poor 255    0.008   0.039    0.953        12        10     0.833
      open drop_all entity_rich 255    0.004   0.043    0.953        12        11     0.917
      open drop_ans entity_poor 255    0.043   0.200    0.757        62        51     0.823
      open drop_ans entity_rich 255    0.047   0.196    0.757        62        50     0.806
      open     full      length 255    0.408   0.243    0.349       166        62     0.373
```

## Confirmatory contrasts (rich − poor)

```
         id     prompt    level  n_items  halluc_poor  halluc_rich    diff   ci_lo  ci_hi  poor0_rich1  poor1_rich0      p  abstain_poor  abstain_rich  p_holm
      S2-H1 extractive drop_ans      255       0.3176       0.3333  0.0157 -0.0235 0.0588           16           12 0.5716        0.6196        0.6039     1.0
      S2-H2 extractive drop_all      255       0.1020       0.0980 -0.0039 -0.0353 0.0275            8            9 1.0000        0.8941        0.8980     1.0
S2-H1(open)       open drop_ans      255       0.2000       0.1961 -0.0039 -0.0353 0.0275            8            9 1.0000        0.7569        0.7569     1.0
S2-H2(open)       open drop_all      255       0.0392       0.0431  0.0039 -0.0157 0.0235            4            3 1.0000        0.9529        0.9529     NaN
```

## Source of hallucinated answers (S2-H3 / S2-H4: drop_ans rows)

```
    prompt    level  n_halluc  copied_from_packet  wilson_lo  wilson_hi  from_gold_unit  from_filler  not_in_packet
extractive     full        71               0.873      0.776      0.932           0.746        0.127          0.127
extractive drop_ans       166               0.735      0.663      0.796           0.464        0.271          0.265
extractive drop_all        51               0.725      0.591      0.829           0.000        0.725          0.275
      open     full        62               0.935      0.846      0.975           0.806        0.129          0.065
      open drop_ans       101               0.931      0.864      0.966           0.653        0.277          0.069
      open drop_all        21               0.905      0.711      0.973           0.000        0.905          0.095
```
