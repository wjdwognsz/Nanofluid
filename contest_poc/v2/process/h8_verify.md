# H8 adversarial verification (link gate with permutation threshold, nested)

## Verifier findings

Verifier: an independent agent. It did not edit any H8 file. Throwaway scripts and outputs are in `process/verify_H8/` (v1_..v11_*.py, `seed_parts/`, `featex_parts/`, `*_compare.csv`, `corrected_targets.csv`, `rerun.log`). The re-runs used `VRR_NJOBS=2`, about 150 s per chunk, 17 chunks in total.

### Bottom line
- The graded H8 verdict, **FAIL**, is correct and robust. It holds under the original run, the leak-corrected re-run and new outer seeds, because p_exp_H2O and s_exp_H2 show negative transfer in every variant and the c1 bar is at most 1 target.
- Two numbers and one per-dataset verdict change once a leak is closed (see Issue 1):
  - c1 rises from 3/11 to **4/11** (d_exp_He: PASS -> FAIL).
  - Mean GATE gain falls from +9.04% to **+8.42%**.

### Checks that PASSED
- **Verdict recomputation** from `results/raw/h8_policy.csv`:
  - GATE negative-transfer targets: GATE 3, TOP 3, PHYS 5, ALL3 2, GATE_MAX 3.
  - Mean gain: GATE +0.0904, TOP +0.0935, PHYS -0.0371, ALL3 +0.1113, GATE_MAX +0.1003.
  - c1 F / c2 T / c3 T, giving FAIL. This is identical to the ledger and summary. The PREREG has no PARTIAL rule for H8, so FAIL is correct.
- **Structural consistency in all 165 outer folds:**
  - The threshold equals `np.percentile` (95) of the 10 permuted scores.
  - TOP is the argmax over real sources only, and a permuted source is never chosen.
  - GATE is open iff top > threshold.
  - The GATE, TOP, PHYS and GATE_MAX gains equal the per-source rows of the chosen source.
  - ALL3 is the top 3.
  - Neither the target nor its parent is ever in the pool.
- **Independent re-implementation** (sklearn directly, not h8_gate modelling code), for s_exp_He repeat 0 with s_sim_CH4, s_exp_H2 and 2 permuted sources:
  - Cross-fitted scores match the file to <= 8e-16.
  - No test-fold key is ever in the source training set.
  - TOP fold gains and NONE RMSE match to 4 decimals.
- **No target-label leakage.** Scores use y[Tr] only. LinearRegression and the residual RF are fit on Tr only. There is no scaling step.
- **Descriptive claims reproduce:**
  - score-gain Spearman 0.1707 and fold AUROC 0.462
  - ORACLE +0.310 / +0.187, RANDOM -0.036, PERM -0.093
  - 39.3% of permuted source-fold pairs have gain > 0
  - pooled gains 0.162 / 0.165 / 0.025 / 0.173, with negative-target counts 3 / 3 / 5 / 1
  - the single closed fold (p_exp_H2O r0 f3: 0.6686 < 0.6997, TOP fold gain +51.4%)
  - TOP class counts 112 / 35 / 18
  - p_exp_H2O d_sim_CO2: 9 picks, -7.4%; s_exp_H2O X_bandgap_chain: 13 picks, +39.1%
- **Reproducibility files** (`h8_repro`): scores are identical to 3e-16 and the same sources are chosen. Policy 5-fold mean |diff| <= 0.0005, as the log states.
- **c2 CI with other bootstrap seeds** (1, 7, 123): [-0.023..-0.026, +0.213..+0.216]. It always includes 0, consistent with the report.
- **PREREG fidelity:**
  - 11 targets; 36-37 real sources plus 10 label-permuted sources (12 or more, including unrelated properties and permuted sources)
  - outer 5-fold x 3; nested score on the outer-training part; 95th-percentile permutation threshold
  - 5 policies; 3 criteria with the -1% definition
  - The sub40 subsamples use the v1 code path (`default_rng(0)`).

### Issues
1. **MAJOR: stereo-annotated duplicates escape the key-based source exclusion (strict new-polymer setting violated).**
   - `_key_of` uses isomeric canonical SMILES, so `*/C(C)=C(/*)[Si](C)(C)C` (PTMSP, cis/trans-annotated) and `*C(C)=C(*)[Si](C)(C)C` are different keys. They have identical feature vectors (the Morgan count fingerprint ignores stereo).
   - Up to 4 target polymers per diffusivity target have such a twin in the p_exp_* sources (also 1-2 twins in d_exp_*, s_exp_*, X_CED, X_bandgap_chain). PTMSP and the other twins are poly(substituted acetylene)s, extreme high-free-volume transport outliers.
   - **All 45 TOP choices for d_exp_He / d_exp_H2 / d_exp_CO2** used a source holding such a twin.
   - Re-run with feature-identity exclusion, same seeds 0-2:

     | target | GATE gain, original | GATE gain, leak-corrected |
     |---|---|---|
     | d_exp_He | -0.02% | **-1.89% (PASS -> FAIL)** |
     | d_exp_H2 | +7.26% | +3.97% |
     | d_exp_CO2 | +4.44% | +2.86% |

   - TOP's choice changes in 47-53% of folds for d_exp_He and d_exp_H2. Single-source gains drop by up to 8.5 pp (p_exp_O2 -> d_exp_H2).
   - Over 5 repeats, leak-corrected d_exp_He = **-4.3%**; with the original key-based exclusion it is +0.8%.
   - Regraded with these substitutions:
     - c1 = 4/11 (FAIL)
     - c2 = +8.42% (CI -4.0..+21.2%; PASS)
     - c3: GATE 4 vs TOP 4 vs PHYS 5 (PASS, with one target to spare)
     - Overall FAIL is unchanged.
   - d_exp_CO2 also contains PTMSP twice as two target rows (-4.481 / -4.631), which affects all policies alike.
   - The bug is inherited from v1 `poc_transfer.py`, so v1's transfer gains on diffusivity targets carry the same inflation.
   - Fix: use `MolToSmiles(m, isomericSmiles=False)` (or feature identity) for target de-duplication and source exclusion. Re-run d_exp_He, d_exp_H2 and d_exp_CO2 (optionally all targets), re-aggregate, and update the ledger (d_exp_He FAIL, c1 4/11).
2. **MINOR: per-dataset c1 verdicts near the -1% bar are not seed-stable.** New outer repeats 3-4, unmodified code:

   | target | repeats 0-2 | new repeats 3-4 | mean over 5 repeats | c1 on 5 repeats |
   |---|---|---|---|---|
   | s_exp_He | -3.75% | +4.93% | -0.27% | would PASS |
   | s_exp_H2 | -2.75% | -7.85% | -4.79% | stays FAIL |
   | d_exp_He | -0.02% | +2.0% | +0.8% | PASS |

   - Per-repeat GATE gains swing by 10-20 pp, and the per-target fold-bootstrap CIs all span -1%.
   - The negative-target count is therefore 2-4 depending on seed and exclusion. The overall FAIL does not depend on it.
   - Fix: state this instability in the per-dataset ledger notes.
3. **MINOR: the stated cause "no multiplicity control" is not supported.**
   - A family-wise Bonferroni Fisher-z gate (m ≈ 36) stays open in 97.6% of folds and still gives 3/11 negative targets (s_exp_He even worse at -5.2%). GATE_MAX is also 3/11.
   - Real sources genuinely exceed any null (top |r| 0.46-0.97 vs Bonferroni threshold 0.29-0.65). The binding problem is that in-sample |r| does not predict out-of-fold gain over the RF baseline (AUROC 0.46).
   - Fix: reword the overall reason.
4. **MINOR: c3 PASS hinges on the PHYS comparator.**
   - The PHYS mapping is fixed only in the process log and docstring, not in git before the runs.
   - Under v1's mechanical `physics_prior` rule, PHYS has 3/11 negatives with best-case tie-breaks (c3 would then FAIL, since 3 is not < 3) and 9/11 with worst-case tie-breaks.
   - The implementer already notes that c3 passes only because PHYS is worse. The ledger c3 note should add this fragility.
5. **MINOR: the c2 bootstrap over 11 targets treats overlapping targets as independent.**
   - s_exp_CO2 is contained in d_exp_CO2 (125/125); s_exp_H2O is contained in p_exp_H2O and d_exp_H2O; s_exp_H2 is in d_exp_H2; s_exp_He is in d_exp_He. So the CI is optimistic.
   - The verdict is unaffected: the criterion is mean > 0, and the leave-one-target-out minimum is about +5.6%.
6. **MINOR: documentation gaps.**
   - Two deviations are documented only in the log and the agent's structured output, not in `h8_summary.json` (no `deviations` key) or in any ledger note:
     - reuse of the outer partition for inner cross-fitting
     - the permutation-base change (no X_bandgap_chain)
7. **MINOR (caveat): s_exp_H2O is bimodal.**
   - 3 polymers sit at y ≈ -2.2..-2.7 and 22 at 0.3..1.35 (robust z up to 11.9; possibly a unit or curation artifact).
   - This explains why many sources reach |r| > 0.9, and the +35% gain rests on separating that cluster. The gain is spread over folds, not driven by a single fold.
