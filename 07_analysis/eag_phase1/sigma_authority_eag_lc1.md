# Phase 1b — sigma advisory vs authority (eag_lc1)


## PRIMARY: primary items (rows=1244, tau*=0.0000)

```
           system  coverage  correct  abstain  halluc  sel_risk  false_refusal(full)
              off    0.4059   0.2090   0.5941  0.1969    0.4851               0.1833
   sigma_advisory    0.4807   0.2363   0.5193  0.2444    0.5084               0.1190
    sigma_placebo    0.4831   0.2363   0.5169  0.2468    0.5108               0.1447
authority@matched    0.4059   0.2090   0.5941  0.1969    0.4851               0.1833
    authority@0.5    0.2468   0.1576   0.7532  0.0892    0.3616               0.2669
```

```
          id   metric                           contrast    diff   ci_lo   ci_hi      p
P1 (primary) sel_risk authority@matched − sigma_advisory -0.0232 -0.0523  0.0031 0.0920
         P1b  correct authority@matched − sigma_advisory -0.0273 -0.0402 -0.0161 0.0005
     placebo   halluc     sigma_advisory − sigma_placebo -0.0024 -0.0137  0.0080 0.7230
     placebo  abstain     sigma_advisory − sigma_placebo  0.0024 -0.0088  0.0129 0.7220
advisory-use   halluc               sigma_advisory − off  0.0474  0.0305  0.0667 0.0005
```


## all items (rows=1972, tau*=0.0000)

```
           system  coverage  correct  abstain  halluc  sel_risk  false_refusal(full)
              off    0.3818   0.2206   0.6182  0.1613    0.4223               0.2272
   sigma_advisory    0.4518   0.2505   0.5482  0.2013    0.4456               0.1582
    sigma_placebo    0.4493   0.2490   0.5507  0.2003    0.4458               0.1927
authority@matched    0.3818   0.2206   0.6182  0.1613    0.4223               0.2272
    authority@0.5    0.2282   0.1526   0.7718  0.0756    0.3311               0.3022
```

```
          id   metric                           contrast    diff   ci_lo   ci_hi      p
P1 (primary) sel_risk authority@matched − sigma_advisory -0.0233 -0.0463 -0.0003 0.0460
         P1b  correct authority@matched − sigma_advisory -0.0299 -0.0406 -0.0198 0.0005
     placebo   halluc     sigma_advisory − sigma_placebo  0.0010 -0.0066  0.0086 0.8850
     placebo  abstain     sigma_advisory − sigma_placebo -0.0025 -0.0101  0.0051 0.5780
advisory-use   halluc               sigma_advisory − off  0.0401  0.0264  0.0532 0.0005
```
