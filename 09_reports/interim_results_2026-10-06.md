# Interim results — Epistemic Access Architecture (2026-10-06)

**Question.** When a language model answers from retrieved evidence, does hallucination depend on whether the key evidence *reaches* the generator (access), and on whether a sufficiency signal is merely *shown* to the generator or *enforced* (authority)? Split-brain confabulation motivated the framing but serves only as a functional analogy. No biological mechanism is claimed or tested.

**Design.** Within-item experiments on HotpotQA (distractor setting) with Qwen2.5-3B-Instruct, greedy decoding. Each item has exactly two gold paragraphs. We manipulate the channel at paragraph level: `full`, `drop_ans` (answer paragraph removed), `drop_other` (bridge paragraph removed) and `drop_all`. Removed paragraphs are replaced by length-matched filler (packet length ratio ≈ 1.0). Pilot: 500 dev items, of which 311 are in the pre-registered primary population (open questions, answer in exactly one gold paragraph). The pilot covers no gate (`off`), advisory (reader verdict shown), enforced (verdict gates the answer) and two-turn restoration with a format control. EAG phase 1 trains small heads on frozen generator states (HotpotQA train, 27.7k packets) and compares them as answer gates on the identical pilot outputs, by AURC. Study 2 is a pre-registered causal test on 396 fresh dev items (255 primary): entity-rich vs entity-poor filler, extractive vs open prompt. Unit of analysis is the item. Rate contrasts use exact McNemar tests, CIs are 95% item bootstraps, and Holm correction is applied within each pre-registered family. Hallucination = a substantive answer that is not correct. Results under primary labels are shown together with a robustness check across three label sets (audit→judge [primary], judge-only, strict rule).

## Results (primary labels; robustness = same verdict under judge-only and strict labels?)

| Hypothesis | Estimate [95% CI], Holm p | Verdict | Robust? |
|---|---|---|---|
| H1a access: halluc. full→drop_ans ↑ | +0.013 [−0.045, 0.074], p=0.75 | not supported | yes (strict: −0.13, significant in the opposite direction) |
| H1b access: full→drop_all ↑ | −0.196 [−0.251, −0.141], p<0.001 | not supported (opposite direction: the model abstains) | yes |
| H2 restoration: drop_ans→restored ↓ | −0.045 [−0.100, 0.013], p=0.44 | not supported | yes (strict: +0.10, opposite) |
| H2eq restored ≈ format control (TOST ±0.05) | +0.013, 90% CI [−0.026, 0.051] | inconclusive (CI marginally exceeds the margin) | yes (judge-only: +0.045, 90% CI [0.006, 0.084]) |
| H3a off→advisory @drop_ans | +0.016 [−0.010, 0.045], p=0.72 | no effect detected, as predicted (no equivalence test) | yes |
| H3b advisory→enforced, selective risk ↓ | −0.220 [−0.456, 0.002], p=0.21 | not supported (direction as predicted) | yes (judge-only: CI excludes 0, Holm p=0.15) |
| H4 cost: false refusal @full within +0.10 | +0.579 [0.521, 0.637] | not supported (prompted reader too conservative) | yes (labels do not affect it) |
| H5a EAG gate < prompted reader (AURC) | −0.041 [−0.088, 0.006], p=0.15 | not supported | yes |
| H5b EAG < generator-state probe | +0.023 [−0.001, 0.045], p=0.15 | not supported (probe ≥ EAG) | yes |
| H5c EAG < question+evidence head | −0.045 [−0.083, −0.004], p=0.07 | not supported after Holm | yes |
| H6 contrastive supervision ↑ sensitivity, AURC non-inferior (0.005) | Δσ +0.017 [0.003, 0.032]; ΔAURC +0.013 [−0.008, 0.033] | not supported | **no**: met under strict labels (ΔAURC −0.023 [−0.043, −0.004]) |
| S2-H1 entity-rich filler ↑ halluc. (drop_ans) | +0.016 [−0.024, 0.059], p=1.0 | not supported | yes |
| S2-H2 same, drop_all | −0.004 [−0.035, 0.027], p=1.0 | not supported | yes |
| S2-H3 ≥50% of drop_ans confabulations copied from packet | 0.735, Wilson [0.663, 0.796] | supported | yes |
| S2-H4 copying under open prompt (S2-H1(open) also null) | 0.931 [0.864, 0.966]; rich−poor −0.004 | copy part supported; filler part not | yes |

The only verdict that changes across label sets is H6. Under strict labels, correct paraphrases count as errors, which changes the AURC target. We therefore treat H6 as not supported and label-sensitive. Analyses restricted to items the model does not know closed-book (`param_known = 0`) give the same pattern (n = 297). The `param_known` stratum (n = 14) is too small to analyse on its own.

**EAG context.** On answered primary rows (258 items), AURC was 0.393 for EAG, 0.370 for the generator-state probe, 0.434 for the prompted reader score, 0.389 for the sufficiency oracle and 0.485 for a random gate. Trained gates rank `full` above `drop_*` packets for 98–99% of items, including the never-trained `drop_other`. At 3B, evidence sufficiency already appears to be linearly readable from the generator's own state. Gating on sufficiency has a low ceiling, because most errors at `full` are misreadings rather than missing evidence.

## Exploratory findings confirmed on fresh items

1. **Selective risk jumps when access is blocked.** The per-item hallucination rate barely changes from `full` to `drop_ans`, because the model shifts to abstaining. However, the answers it still gives are mostly wrong. Pilot (exploratory): selective risk 0.35 → 0.81, +0.47 [0.38, 0.55]. Study 2 (fresh items, all four filler × prompt cells): +0.43 to +0.48, all CIs > +0.33. The jump holds under all three label sets, including strict at +0.36 to +0.40. The pre-registered H1, which uses hallucination per item, mixes willingness to answer with accuracy. This is a design lesson, not a positive result for H1. The selective-risk contrast was not pre-registered as a confirmatory test in Study 2, so it should be read as a replication of a descriptive effect.
2. **Confabulations are copied from the delivered evidence, independent of filler candidate density.** 74% (extractive) and 93% (open prompt) of `drop_ans` confabulations are strings from the packet. Most come from the remaining relevant gold paragraph: 46% extractive and 65% open, against 27–28% from filler. Manipulating how many answer-type candidates the filler contains had no effect (S2-H1/H2/H1-open all null, CIs within about ±0.06). The pilot's "anchoring on available candidates" hypothesis is therefore rejected. What remains is narrower: the model takes entities from question-relevant evidence. Copying is not an artefact of the extractive instruction.

## Limitations

- One model family and one size so far (Qwen2.5-3B); HotpotQA only; short extractive QA with greedy decoding.
- Correctness for rule-ambiguous answers was labelled by Claude audit (181 pilot + 85 Study 2 cases) overriding a Qwen2.5-7B judge. Judge-audit agreement was 0.82 (κ = 0.61). The judge does fill the remaining cases, and the auditor was not blind to the study. The robustness table mitigates but does not remove this.
- The prompted reader verdict was almost always INSUFFICIENT. H3a/H3b/H4 therefore test an uninformative signal and say little about authority per se.
- Deviations are logged in `00_docs/research_log.md`:
  - GLMM was replaced by item bootstrap plus McNemar;
  - correctness labels were changed after the pilot (two labelling bugs; tiered judge; audit-first labels chosen before the confirmatory reading);
  - a P(SUFFICIENT) score gate was added after the smoke test;
  - phase 1b was run even though H5a/H5b failed its precondition;
  - the pilot run was resumed with a different batch order;
  - Study 2 batch size was changed (8 → 4);
  - the restoration test is two-turn.
- EAG phase 1 is an internal feasibility test. Heads are supervised in-distribution, the reader is zero-shot, and the required external baselines (CAA-style LoRA, RINSE, critic-driven decoding) are not yet run.

## Next steps

- **Phase 1b (running):** the same σ (EAG, at oracle level) given to the generator as advisory text vs used as a hard gate. Primary contrast: selective risk at matched coverage, with a shuffled-σ placebo. This is the cleaner test of authority that H3 could not provide.
- **Study 2 replications (queued):** Qwen2.5-1.5B and Qwen2.5-7B (4-bit). Any new ambiguous cases will be audited before analysis.
- Afterwards: a second model family, a non-extractive / long-form task, and blind or double audit of labels.

*Files:* robustness tables `07_analysis/robustness/summary.md` (+ `forest_label_robustness.png`); primary analyses `07_analysis/pilot_v0.2_qwen2.5-3b/`, `07_analysis/eag_phase1/`, `07_analysis/study2_qwen2.5-3b/`.

---

## Addendum (added after the report above): Phase 1b, same signal as advice vs as authority

*Signal:* σ = EAG head `eag_lc1` (frozen Qwen2.5-3B; sufficiency AUROC ≈ 0.94 on test). *Population:* primary pilot items, all four channel levels, 1,244 rows.

- **Pre-registered primary contrast was degenerate and is not interpretable.** It compared a hard gate with advisory *at matched answer rate*. Advisory raised the answer rate (0.406 → 0.481) above anything a hard gate on the same generator outputs can reach, so the matched threshold collapsed to τ* = 0.
- **Placebo (pre-registered): supported null.** Advisory text with the true σ and advisory text with σ shuffled across rows were indistinguishable (Δ hallucination −0.002 [−0.014, 0.008]). The generator does not use the value of σ. The advisory text itself increased hallucination by +0.047 [0.031, 0.067] relative to no signal.
- **Secondary / exploratory: authority at τ = 0.5 vs no signal.**

  | Outcome | Change |
  |---|---|
  | Hallucination | −0.108 [−0.128, −0.089] |
  | Selective risk | −0.124 [−0.156, −0.091] |
  | Correct answers | −0.051 [−0.066, −0.038] |
  | False refusal on complete evidence | +0.084 [0.055, 0.113] (vs +0.58 for the prompt-based reader gate) |

- **Reading:** the same epistemic signal is inert as advice but effective as authority. This is consistent with the thesis that the bottleneck is epistemic authority rather than information. It is not yet a confirmatory result: the primary contrast failed, it is a single model, and the advisory arm was not fine-tuned to use σ.
