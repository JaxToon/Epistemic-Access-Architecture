# Label robustness of confirmatory contrasts (2026-10-06)

Label sets: **primary** = audit labels (Claude, documented per item) override the Qwen2.5-7B judge, judge fills the rest; **judge-only** = `EAA_LABELS=judge`; **strict** = rule only (EM / gold ⊂ pred; rule-ambiguous predictions count as wrong). Abstention labels are identical across sets, so H4 and H6 part 1 cannot change. diff = b − a; 95% item-bootstrap CI unless stated; p = Holm-adjusted where the contrast belongs to a pre-registered family (McNemar exact for rates, bootstrap for selective risk / AURC). Primary-label numbers reproduce `07_analysis/pilot_v0.2_qwen2.5-3b`, `07_analysis/eag_phase1` and `07_analysis/study2_qwen2.5-3b` exactly.

Script: `scripts/robustness_labels.py`, `scripts/robustness_summary.py`; EAG: `python -m eaa.eag.evaluate --eval-csv 07_analysis/robustness/evals/pilot_<labels>.csv --out 07_analysis/robustness/eag_<labels>`.


## Verdict changes across label sets

- ⚑ H6 part 2: AURC lc1−lc0 < +0.005: primary (audit→judge) = not met; judge-only = not met; strict (rule) = met
- ⚑ H6 (both parts): primary (audit→judge) = not supported; judge-only = not supported; strict (rule) = supported


## Pilot H1–H4 (primary population, 311 items; Holm over H1a,H1b,H2,H3a,H3b,H4)

| contrast | labels | rates / detail | estimate | 95% CI | p (Holm) | verdict |
|---|---|---|---|---|---|---|
| H1a | primary (audit→judge) | 0.283→0.296 | +0.013 | [-0.045, +0.074] | 0.755 | not supported |
|  | judge-only | 0.312→0.312 | +0.000 | [-0.058, +0.061] | 1.000 | not supported |
|  | strict (rule) | 0.489→0.357 | -0.132 | [-0.199, -0.068] | <0.001 | not supported (sig. opposite direction) |
| H1b | primary (audit→judge) | 0.283→0.087 | -0.196 | [-0.251, -0.141] | <0.001 | not supported (sig. opposite direction) |
|  | judge-only | 0.312→0.090 | -0.222 | [-0.277, -0.167] | <0.001 | not supported (sig. opposite direction) |
|  | strict (rule) | 0.489→0.100 | -0.389 | [-0.447, -0.331] | <0.001 | not supported (sig. opposite direction) |
| H2 | primary (audit→judge) | 0.296→0.251 | -0.045 | [-0.100, +0.013] | 0.437 | not supported |
|  | judge-only | 0.312→0.305 | -0.006 | [-0.061, +0.055] | 1.000 | not supported |
|  | strict (rule) | 0.357→0.453 | +0.096 | [+0.032, +0.161] | 0.018 | not supported (sig. opposite direction) |
| H3a | primary (audit→judge) | 0.296→0.312 | +0.016 | [-0.010, +0.045] | 0.719 | no effect detected (≈0 predicted; no equivalence test) |
|  | judge-only | 0.312→0.331 | +0.019 | [-0.010, +0.048] | 0.790 | no effect detected (≈0 predicted; no equivalence test) |
|  | strict (rule) | 0.357→0.379 | +0.023 | [-0.006, +0.051] | 0.378 | no effect detected (≈0 predicted; no equivalence test) |
| H3b | primary (audit→judge) | 0.808→0.588 | -0.220 | [-0.456, +0.002] | 0.208 | not supported |
|  | judge-only | 0.858→0.647 | -0.211 | [-0.441, -0.009] | 0.152 | not supported |
|  | strict (rule) | 0.983→0.941 | -0.042 | [-0.165, +0.023] | 0.750 | not supported |
| H2eq (TOST ±0.05) | primary (audit→judge) | 0.238→0.251 | +0.013 | 90% [-0.026, +0.051] | – | inconclusive (not equivalent within margin) |
|  | judge-only | 0.260→0.305 | +0.045 | 90% [+0.006, +0.084] | – | inconclusive (not equivalent within margin) |
|  | strict (rule) | 0.441→0.453 | +0.013 | 90% [-0.029, +0.055] | – | inconclusive (not equivalent within margin) |
| H4 (false refusal; margin +0.10) | primary (audit→judge) | 0.183→0.762 | +0.579 | [+0.521, +0.637] | <0.001 | not supported (cost exceeds margin) |
|  | judge-only | 0.183→0.762 | +0.579 | [+0.521, +0.637] | <0.001 | not supported (cost exceeds margin) |
|  | strict (rule) | 0.183→0.762 | +0.579 | [+0.521, +0.637] | <0.001 | not supported (cost exceeds margin) |

## EAG phase 1 (AURC on primary & answered; Holm over H5a–c)

| contrast | labels | rates / detail | estimate | 95% CI | p (Holm) | verdict |
|---|---|---|---|---|---|---|
| H5a | primary (audit→judge) | eag_lc1 − reader_p_suff | -0.041 | [-0.088, +0.006] | 0.148 | not supported |
|  | judge-only | eag_lc1 − reader_p_suff | -0.038 | [-0.085, +0.010] | 0.116 | not supported |
|  | strict (rule) | eag_lc1 − reader_p_suff | -0.005 | [-0.048, +0.039] | 0.820 | not supported |
| H5b | primary (audit→judge) | eag_lc1 − probe_lc1 | +0.023 | [-0.001, +0.045] | 0.148 | not supported |
|  | judge-only | eag_lc1 − probe_lc1 | +0.027 | [+0.002, +0.048] | 0.084 | not supported (unadj. CI excl. 0, favours comparator) |
|  | strict (rule) | eag_lc1 − probe_lc1 | +0.025 | [+0.000, +0.048] | 0.144 | not supported (unadj. CI excl. 0, favours comparator) |
| H5c | primary (audit→judge) | eag_lc1 − qe_lc1 | -0.045 | [-0.083, -0.004] | 0.072 | not supported (unadj. CI excl. 0, favours eag) |
|  | judge-only | eag_lc1 − qe_lc1 | -0.050 | [-0.092, -0.008] | 0.084 | not supported (unadj. CI excl. 0, favours eag) |
|  | strict (rule) | eag_lc1 − qe_lc1 | -0.040 | [-0.078, +0.001] | 0.144 | not supported |
| H6 part 1: Δσ_untrained lc1−lc0 | primary (audit→judge) | label-independent | +0.017 | [+0.003, +0.032] | 0.014 | met |
|  | judge-only | label-independent | +0.017 | [+0.003, +0.032] | 0.014 | met |
|  | strict (rule) | label-independent | +0.017 | [+0.003, +0.032] | 0.014 | met |
| H6 part 2: AURC lc1−lc0 < +0.005 **⚑ verdict changes** | primary (audit→judge) | eag_lc1 − eag_lc0 | +0.013 | [-0.008, +0.033] | 0.268 | not met |
|  | judge-only | eag_lc1 − eag_lc0 | +0.009 | [-0.013, +0.029] | 0.460 | not met |
|  | strict (rule) | eag_lc1 − eag_lc0 | -0.023 | [-0.043, -0.004] | 0.028 | met |
| H6 (both parts) **⚑ verdict changes** | primary (audit→judge) |  |  |  |  | not supported |
|  | judge-only |  |  |  |  | not supported |
|  | strict (rule) |  |  |  |  | supported |

## Study 2, Qwen2.5-3B (255 primary items; Holm over S2-H1, S2-H2, S2-H1(open))

| contrast | labels | rates / detail | estimate | 95% CI | p (Holm) | verdict |
|---|---|---|---|---|---|---|
| S2-H1 | primary (audit→judge) | poor 0.318 / rich 0.333 | +0.016 | [-0.024, +0.059] | 1.000 | not supported |
|  | judge-only | poor 0.325 / rich 0.341 | +0.016 | [-0.024, +0.055] | 1.000 | not supported |
|  | strict (rule) | poor 0.369 / rich 0.380 | +0.012 | [-0.027, +0.051] | 1.000 | not supported |
| S2-H2 | primary (audit→judge) | poor 0.102 / rich 0.098 | -0.004 | [-0.035, +0.027] | 1.000 | not supported |
|  | judge-only | poor 0.106 / rich 0.098 | -0.008 | [-0.039, +0.024] | 1.000 | not supported |
|  | strict (rule) | poor 0.106 / rich 0.102 | -0.004 | [-0.035, +0.027] | 1.000 | not supported |
| S2-H1(open) | primary (audit→judge) | poor 0.200 / rich 0.196 | -0.004 | [-0.035, +0.027] | 1.000 | not supported |
|  | judge-only | poor 0.204 / rich 0.200 | -0.004 | [-0.039, +0.027] | 1.000 | not supported |
|  | strict (rule) | poor 0.235 / rich 0.235 | +0.000 | [-0.035, +0.035] | 1.000 | not supported |
| S2-H3 (extractive) | primary (audit→judge) | n_halluc=166; gold-unit 0.46 / filler 0.27 | 0.735 | Wilson [0.663, 0.796] | – | supported |
|  | judge-only | n_halluc=170; gold-unit 0.46 / filler 0.27 | 0.735 | Wilson [0.664, 0.796] | – | supported |
|  | strict (rule) | n_halluc=191; gold-unit 0.51 / filler 0.24 | 0.749 | Wilson [0.683, 0.805] | – | supported |
| S2-H4 (open) | primary (audit→judge) | n_halluc=101; gold-unit 0.65 / filler 0.28 | 0.931 | Wilson [0.864, 0.966] | – | supported |
|  | judge-only | n_halluc=103; gold-unit 0.64 / filler 0.28 | 0.922 | Wilson [0.854, 0.960] | – | supported |
|  | strict (rule) | n_halluc=120; gold-unit 0.66 / filler 0.24 | 0.900 | Wilson [0.833, 0.942] | – | supported |

## Selective risk full→drop_ans (exploratory in pilot; replication on Study 2 items; no Holm)

| contrast | labels | rates / detail | estimate | 95% CI | p (Holm) | verdict |
|---|---|---|---|---|---|---|
| SR jump pilot extractive/length | primary (audit→judge) | 0.346→0.814 | +0.468 | [+0.381, +0.549] | – | increase (CI > 0) |
|  | judge-only | 0.382→0.858 | +0.477 | [+0.398, +0.552] | – | increase (CI > 0) |
|  | strict (rule) | 0.598→0.982 | +0.384 | [+0.320, +0.449] | – | increase (CI > 0) |
| SR jump study2 extractive/entity_poor | primary (audit→judge) | 0.362→0.835 | +0.473 | [+0.387, +0.558] | – | increase (CI > 0) |
|  | judge-only | 0.383→0.856 | +0.473 | [+0.388, +0.556] | – | increase (CI > 0) |
|  | strict (rule) | 0.566→0.969 | +0.403 | [+0.329, +0.477] | – | increase (CI > 0) |
| SR jump study2 extractive/entity_rich | primary (audit→judge) | 0.362→0.842 | +0.479 | [+0.396, +0.562] | – | increase (CI > 0) |
|  | judge-only | 0.383→0.861 | +0.479 | [+0.395, +0.557] | – | increase (CI > 0) |
|  | strict (rule) | 0.566→0.960 | +0.394 | [+0.316, +0.466] | – | increase (CI > 0) |
| SR jump study2 open/entity_poor | primary (audit→judge) | 0.373→0.823 | +0.449 | [+0.346, +0.549] | – | increase (CI > 0) |
|  | judge-only | 0.386→0.839 | +0.453 | [+0.349, +0.548] | – | increase (CI > 0) |
|  | strict (rule) | 0.608→0.968 | +0.359 | [+0.282, +0.435] | – | increase (CI > 0) |
| SR jump study2 open/entity_rich | primary (audit→judge) | 0.373→0.806 | +0.433 | [+0.328, +0.536] | – | increase (CI > 0) |
|  | judge-only | 0.386→0.823 | +0.437 | [+0.331, +0.538] | – | increase (CI > 0) |
|  | strict (rule) | 0.608→0.968 | +0.359 | [+0.280, +0.438] | – | increase (CI > 0) |

## Notes

- Strict labels count correct paraphrases ("Al Capone" for "Alphonse Gabriel Capone") as hallucinations. These occur mostly when the answer is in the evidence (`full`, `restored`), so strict labels inflate hallucination at `full` (0.49 vs 0.28 primary). This is why H1a and H2 become *significant in the opposite direction* under strict labels; their verdict (not supported) does not change.
- H2eq under judge-only: restored − ctrl = +0.045, 90% CI [+0.006, +0.084] (unadjusted McNemar p = 0.065): a hint of anchoring that is absent under primary (+0.013) and strict (+0.013) labels. Verdict (inconclusive) unchanged.
- H6 under strict labels: the AURC error target changes (strict errors include correct paraphrases, which are concentrated at `full`, where σ is high), so eag_lc1 vs eag_lc0 ranks differently. Under both labels that correct the paraphrase artefact, H6 part 2 fails. We treat H6 as not supported and flag it as label-sensitive.
- H5b: under judge-only and strict labels the unadjusted CI excludes 0 *in favour of the probe* (probe ≥ eag), consistent with the primary reading that evidence access adds no value over the generator state at 3B.
- H3b under judge-only: 95% CI excludes 0 ([−0.441, −0.009]) but Holm p = 0.152; verdict unchanged.
- param_known stratum is tiny (14 / 12 / 5 primary items by label set); param_unknown results mirror the primary ones (files `pilot_<labels>/contrasts_primary_param_{known,unknown}.csv`). In param_unknown, H3b primary = −0.274 [−0.499, −0.058], Holm p = 0.072. Study 2 has no closed-book run, so no param_known split there.
