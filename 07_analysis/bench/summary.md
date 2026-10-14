# Benchmark — EAG σ vs standard uncertainty signals (Qwen2.5-3B, Study 3 primary)

answered rows: 447 / 1275; coverage-matched answer rate = 0.180

## AURC on substantive answers (lower = better) and AUROC

```
            gate   AURC  diff_vs_eag            diff_ci  AUROC(correct vs halluc)
       eag_sigma 0.4985       0.0000         (0.0, 0.0)                    0.7149
   reader_p_suff 0.5258       0.0273  (-0.0205, 0.0793)                    0.6725
          p_true 0.5247       0.0262   (-0.0398, 0.091)                    0.6936
        seq_conf 0.5205       0.0220  (-0.0322, 0.0795)                    0.6621
self_consistency 0.5937       0.0952   (0.0463, 0.1438)                    0.5476
     oracle_full 0.4341      -0.0644 (-0.1036, -0.0198)                    0.7888
          random 0.6443          NaN                NaN                       NaN
```

## Gates at the same answer rate as σ<0.5

```
                     gate  threshold  answer_rate  halluc  correct  false_refusal_full
                eag_sigma     0.5002       0.1804  0.0925   0.0878              0.3451
            reader_p_suff     0.0011       0.1804  0.0949   0.0855              0.4549
                   p_true     0.0000       0.1804  0.0910   0.0894              0.5098
                 seq_conf    -0.0144       0.1804  0.0965   0.0839              0.5059
         self_consistency     1.0000       0.2478  0.1451   0.1027              0.3765
              oracle_full     0.0000       0.1804  0.0776   0.1027              0.2314
random (same answer rate)        NaN       0.1804  0.1162   0.0642              0.6045
            no gate (off)        NaN       0.3506  0.2259   0.1247              0.2314
```
