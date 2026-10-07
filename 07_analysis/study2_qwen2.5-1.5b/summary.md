# Study 2 — evidence-anchored confabulation (qwen2.5-1.5b)

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
extractive drop_all entity_poor 255    0.024   0.298    0.678        82        76     0.927
extractive drop_all entity_rich 255    0.012   0.286    0.702        76        73     0.961
extractive drop_ans entity_poor 255    0.090   0.482    0.427       146       123     0.842
extractive drop_ans entity_rich 255    0.075   0.478    0.447       141       122     0.865
extractive     full      length 255    0.573   0.314    0.114       226        80     0.354
      open drop_all entity_poor 255    0.024   0.282    0.694        78        72     0.923
      open drop_all entity_rich 255    0.020   0.302    0.678        82        77     0.939
      open drop_ans entity_poor 255    0.082   0.518    0.400       153       132     0.863
      open drop_ans entity_rich 255    0.090   0.518    0.392       155       132     0.852
      open     full      length 255    0.576   0.271    0.153       216        69     0.319
```

## Confirmatory contrasts (rich − poor)

```
         id     prompt    level  n_items  halluc_poor  halluc_rich    diff   ci_lo  ci_hi  poor0_rich1  poor1_rich0      p  abstain_poor  abstain_rich  p_holm
      S2-H1 extractive drop_ans      255       0.4824       0.4784 -0.0039 -0.0510 0.0392           15           16 1.0000        0.4275        0.4471     1.0
      S2-H2 extractive drop_all      255       0.2980       0.2863 -0.0118 -0.0588 0.0314           17           20 0.7428        0.6784        0.7020     1.0
S2-H1(open)       open drop_ans      255       0.5176       0.5176  0.0000 -0.0510 0.0510           20           20 1.0000        0.4000        0.3922     1.0
S2-H2(open)       open drop_all      255       0.2824       0.3020  0.0196 -0.0314 0.0667           23           18 0.5327        0.6941        0.6784     NaN
```

## Source of hallucinated answers (S2-H3 / S2-H4: drop_ans rows)

```
    prompt    level  n_halluc  copied_from_packet  wilson_lo  wilson_hi  from_gold_unit  from_filler  not_in_packet
extractive     full        80               0.788      0.686      0.863           0.650        0.138          0.212
extractive drop_ans       245               0.739      0.680      0.790           0.376        0.363          0.261
extractive drop_all       149               0.745      0.669      0.808           0.000        0.745          0.255
      open     full        69               0.812      0.704      0.886           0.768        0.043          0.188
      open drop_ans       264               0.845      0.796      0.883           0.527        0.318          0.155
      open drop_all       149               0.758      0.684      0.820           0.000        0.758          0.242
```
