# EAG phase 1 — gates on pilot `off` outputs

configs: ['eag_lc0', 'eag_lc1', 'probe_lc1', 'qe_lc1']; seeds per config: 3


## PRIMARY: primary & answered (rows=505, items=258)

```
         gate   aurc  ci_lo  ci_hi
      eag_lc0 0.3796 0.3122 0.4471
      eag_lc1 0.3930 0.3237 0.4581
    probe_lc1 0.3700 0.3021 0.4383
       qe_lc1 0.4377 0.3659 0.5019
reader_p_suff 0.4336 0.3640 0.5057
     cue_only 0.4424 0.3668 0.5173
  oracle_full 0.3888 0.3359 0.4407
oracle_answer 0.3707 0.3148 0.4281
       random 0.4851    NaN    NaN
```

Contrasts (AURC diff; negative = eag_lc1 better):

```
     id                contrast    diff   ci_lo   ci_hi     p  p_holm non_inferior
    H5a eag_lc1 − reader_p_suff -0.0406 -0.0882  0.0063 0.090   0.148          NaN
    H5b     eag_lc1 − probe_lc1  0.0230 -0.0013  0.0446 0.074   0.148          NaN
    H5c        eag_lc1 − qe_lc1 -0.0447 -0.0828 -0.0042 0.024   0.072          NaN
    cue      eag_lc1 − cue_only -0.0494 -0.1097  0.0070 0.082     NaN          NaN
H6-AURC       eag_lc1 − eag_lc0  0.0134 -0.0081  0.0329 0.268     NaN        False
```

Per-level AURC (secondary):

```
     level  eag_lc0  eag_lc1  probe_lc1  qe_lc1  reader_p_suff  cue_only  oracle_full  oracle_answer   n
  drop_all   0.8880   0.9086     0.8972  0.9066         0.9143    0.9198       0.8710         0.8710  31
  drop_ans   0.7638   0.7481     0.7816  0.8081         0.7690    0.7930       0.8142         0.8142 113
drop_other   0.2772   0.3195     0.3113  0.3286         0.3436    0.3965       0.3551         0.3551 107
      full   0.3435   0.3614     0.3098  0.3922         0.3451    0.3397       0.3465         0.3465 254
```

Per-seed AURC:

```
         run   aurc
probe_lc1_s0 0.3649
probe_lc1_s1 0.3625
probe_lc1_s2 0.3824
   qe_lc1_s0 0.4623
   qe_lc1_s1 0.4399
   qe_lc1_s2 0.4249
  eag_lc1_s0 0.3873
  eag_lc1_s1 0.3872
  eag_lc1_s2 0.3957
  eag_lc0_s0 0.3731
  eag_lc0_s1 0.3832
  eag_lc0_s2 0.3953
```


## primary, all rows (rows=1244, items=311)

```
         gate   aurc  ci_lo  ci_hi
      eag_lc0 0.2818 0.2386 0.3271
      eag_lc1 0.2912 0.2458 0.3369
    probe_lc1 0.2858 0.2414 0.3315
       qe_lc1 0.2381 0.1985 0.2802
reader_p_suff 0.3272 0.2780 0.3736
     cue_only 0.2487 0.2043 0.2967
  oracle_full 0.2367 0.2000 0.2736
oracle_answer 0.2008 0.1692 0.2344
       random 0.1969    NaN    NaN
```

Contrasts (AURC diff; negative = eag_lc1 better):

```
     id                contrast    diff   ci_lo   ci_hi     p  p_holm non_inferior
    H5a eag_lc1 − reader_p_suff -0.0360 -0.0590 -0.0136 0.001   0.003          NaN
    H5b     eag_lc1 − probe_lc1  0.0054 -0.0064  0.0154 0.352   0.352          NaN
    H5c        eag_lc1 − qe_lc1  0.0531  0.0294  0.0764 0.001   0.003          NaN
    cue      eag_lc1 − cue_only  0.0424  0.0114  0.0723 0.008     NaN          NaN
H6-AURC       eag_lc1 − eag_lc0  0.0094 -0.0001  0.0179 0.052     NaN        False
```


## all items, answered (rows=753, items=388)

```
         gate   aurc  ci_lo  ci_hi
      eag_lc0 0.3377 0.2812 0.3897
      eag_lc1 0.3521 0.2960 0.4017
    probe_lc1 0.3387 0.2827 0.3934
       qe_lc1 0.3904 0.3327 0.4421
reader_p_suff 0.3667 0.3139 0.4177
     cue_only 0.3901 0.3254 0.4482
  oracle_full 0.3420 0.2962 0.3874
oracle_answer 0.3297 0.2850 0.3734
       random 0.4223    NaN    NaN
```

Contrasts (AURC diff; negative = eag_lc1 better):

```
     id                contrast    diff   ci_lo   ci_hi     p  p_holm non_inferior
    H5a eag_lc1 − reader_p_suff -0.0145 -0.0551  0.0197 0.390   0.432          NaN
    H5b     eag_lc1 − probe_lc1  0.0134 -0.0075  0.0321 0.216   0.432          NaN
    H5c        eag_lc1 − qe_lc1 -0.0383 -0.0704 -0.0033 0.030   0.090          NaN
    cue      eag_lc1 − cue_only -0.0379 -0.0868  0.0083 0.114     NaN          NaN
H6-AURC       eag_lc1 − eag_lc0  0.0145 -0.0016  0.0290 0.084     NaN        False
```


## Access sensitivity (primary items, all rows; drop_other never seen in training)

```
         gate  dsig_full-drop_ans  dsig_full-drop_other (UNTRAINED)  pairacc_full>drop_ans  pairacc_full>drop_other  auroc_suff(full)
      eag_lc0              0.6257                            0.5662                 0.9807                   0.9871            0.9425
      eag_lc1              0.6497                            0.5835                 0.9904                   0.9871            0.9444
    probe_lc1              0.6184                            0.5631                 0.9904                   0.9807            0.9416
       qe_lc1              0.3415                            0.2801                 0.9228                   0.8939            0.8158
reader_p_suff              0.1925                            0.2319                 0.9357                   0.9453            0.8732
     cue_only              0.1699                            0.2629                 0.8167                   0.9260            0.8129
```

{'H6: Δσ_untrained(eag_lc1) − Δσ_untrained(eag_lc0)': np.float32(0.017264545), 'ci_lo': np.float32(0.0027936534), 'ci_hi': np.float32(0.031529494), 'p': 0.014}
