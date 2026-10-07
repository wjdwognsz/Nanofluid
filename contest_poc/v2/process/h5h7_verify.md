# H5 + H7 adversarial verification (audit rules; failure-data value)

## Verifier findings

Verifier: an independent agent. It did not edit any H5/H7 file (scripts, results, ledger, process log). Throwaway scripts and
outputs are in `process/verify_H5H7/` (`v_h7_boot.py`, `v_h7a_reseed.py`, `v_h7a_missing.py`, `v_h7b_reseed.py`,
`v_h5a_reseed.py`, `v_h5a_r1only.py` and their CSV outputs). Re-runs used `VRR_NJOBS=2`, `OMP_NUM_THREADS<=2`.

### Bottom line
- Every graded number in `ledger/h5.csv` and `ledger/h7.csv` recomputes exactly from the raw CSVs, and the
  `results/h5_summary.json` / `results/h7_summary.json` values match the ledgers.
- **H5a FAIL, H5b FAIL and H5 FAIL are correct and robust.** They survive new injection seeds, new bootstrap seeds,
  per-source-mean RMSE and an R1-only filter.
- **H7a FAIL and H7b PASS are correct as computed and stable under re-seeding.** H7b is fragile, though: single seeds dip below 0.10.
- **One verdict-level issue (major).** The PREREG rule for H7 is "H7a and H7b both" and has no PARTIAL band, but the
  family reports H7_overall = **PARTIAL**. Under the PREREG, and consistent with how H8 and H9 treated "all conditions"
  rules, **H7_overall should be FAIL**. The note should say that the H7b component passes and H7a does not.

### Checks that PASSED
- **Rules frozen.** `vrr_audit.py` sha256 = `5d77a8d6...` and mtime 12:02:13, so it was not edited after it was written (as logged).
- **H5a recompute** from `results/raw/h5_injection.csv` (13 cells x 10 seeds):
  - The recall column equals tp/n_injected to within 1e-16.
  - The seed means of recall, precision and recovery equal the ledger: 12 PASS / 6 FAIL / 3 INCONCLUSIVE of 21. Recovery examples: RHO UNIT 1.000, ETA UNIT 1.223, ES1 UNIT 0.713.
  - The COPY optimism claims reproduce:
    - DES_RHO: 0.0510 -> 0.0423 (-17%).
    - DES_ETA: 0.623 -> 0.502 (-19.5%).
- **H5a independent re-run** (my own driver, importing the family's `inject` and `audit`; seeds 0-3, DES_ETA UNIT):
  `rmse_inj` reproduces the family's file to 1e-15, and tp_R1 counts are identical.
- **H5a stability on new injection seeds 10-14:**
  - ES1 UNIT: recall 0.995, precision 0.929, pooled recovery 0.73 (original: 1.000 / 0.919 / 0.713).
  - DES_ETA TEMP: recall 1.000, precision 0.577 (original 0.585). Pooled harm again has mixed signs, so the cell stays INCONCLUSIVE.
- **H5b recompute** from `results/raw/h5b_real.csv`:
  - All 7 per-source means and CIs match. 0/7 datasets have CI upper < 0.
  - Bootstrap seeds 1-3 move the CI bounds by at most 0.005, and no verdict changes. DES_MP is the closest at CI upper +0.014..+0.016.
  - Flag counts in `real_meta_*.json` match the ledger notes.
- **H5b leakage.** Leak copies of held-out sources are removed from training in both arms, per fold.
- **H5a COPY leakage.** H5a uses lineage-clean bases: R3 finds 0 copies on both clean DES bases, so no residual copy leakage exists outside the COPY treatment.
- **H7 recompute** from `results/raw/h7_scores.csv`:
  - sklearn `roc_auc_score` equals the family's AUCs.
  - H7a: 144 test rows, 32 failures, 10 papers.
  - H7b: 3,390 rows, 2,594 failures, 115 sources.
  - The best models are RF/IF (H7a) and HGB/KNN5 (H7b). The diffs 0.3419 / 0.1071 match.
- **Bootstrap-seed stability** (0-4, 2,000 resamples):
  - H7a CI lower bound is -0.033..-0.042, so H7a stays FAIL. Its one-sided P(diff <= 0) is about 0.034.
  - H7b CI lower bound is 0.031..0.036, so H7b stays PASS.
- **H7a re-run with model seeds 5-9:** RF 0.732, HGB 0.694, IF 0.392. Diff 0.340, paper-bootstrap CI [-0.021, 0.666], so FAIL is unchanged.
- **H7a leakage.** No test-paper row has an identical feature vector in another paper. Only 2/144 test rows share a condition key with another paper.
- **H7b re-run with new fold/model seeds 5-9:**
  - Without leak removal: RF 0.857, HGB 0.858, KNN5 0.746 (deterministic). Best diff **0.111**.
  - With `leak_mask_for_source` removal: diff 0.110.
  - DES_MP has only 20 leak rows (10 copy rows; 79 rows whose material occurs in >= 2 sources), so lineage leakage does not inflate H7b.
- **H7 learning curve and meta.** Learning-curve values and "beats best one-class" counts (0, 2, 8, 10, 10, 10 of 10) match `h7_learning_curve.csv`.
  Meta counts match: 1,289 reference materials, 238 overlapping, 356 DES_MP rows (77 failures) in the reference.
- **Scaling.** In H7, StandardScaler, IF and OCSVM are fit only on training/reference rows. In H5, the RF has no scaler.
  The only transductive step is the ES1 median imputation, which comes from the shared loader and is negligible.

### Issues
1. **MAJOR: H7_overall = PARTIAL contradicts the PREREG.**
   - The PREREG says: "합격: H7a와 H7b 모두에서 (최선 지도학습 − 최선 단일 클래스) AUC ≥ 0.10이고 CI 하한 > 0".
     That is a single conjunctive rule with no PARTIAL band.
   - The 3-level rule (both, one, none) was introduced by the agent at 12:02. It was logged, but it is still a softening deviation.
   - H8 ("PASS iff c1 and c2 and c3 (PREREG)") and H9 ("no PARTIAL band in PREREG") used binary verdicts for the same kind of rule.
   - Fix: set H7_overall to **FAIL**, with the note "H7b component PASS (0.107, CI 0.031-0.195; margin 0.007), H7a FAIL (0.342, CI -0.040-0.692)".
     The PARTIAL reading can be kept only as an EXPLORATORY row.
2. **Minor: the graded ES1 TEMP cell uses an error type that is not in the PREREG.**
   - The graded cell writes °F into the °C column. The PREREG's type is K<->°C.
   - The closest variant to the PREREG, a K value written into the °C column (`TEMP_K`, reported as EXPLORATORY), gives recall 1.000 and precision 0.854 (both PASS) and recovery INCONCLUSIVE.
   - Grading it changes the H5a tally from 12P/6F/3I to **14P/4F/3I**. H5a stays FAIL.
   - The choice was disclosed and runs in the conservative direction.
   - Fix: add a sensitivity row "ES1 TEMP graded with TEMP_K", and say in reports that the ES1 TEMP failure is a °F confusion.
3. **Minor: H5a recovery uses pooled RMSE over clean rows, but the PREREG says "출처 단위 RMSE".**
   - The family computed per-source-mean RMSE (`msrc_*` columns) but did not report it.
   - With per-source-mean RMSE:
     - UNIT recovery is 1.00 (RHO), 0.88 (ETA) and 0.95 (ES1), all PASS.
     - DES_ETA TEMP harm becomes measurable (0.0018, seed CI [0.0002, 0.0034]) with recovery 0.94, so INCONCLUSIVE -> PASS.
       New seeds 10-14 agree: harm > 0 in 5/5 seeds, recovery 0.99.
     - DES_RHO TEMP harm becomes measurable (0.00017, CI [0.00008, 0.00026]) with recovery -7.1, so INCONCLUSIVE -> FAIL.
   - H5a stays FAIL.
   - Fix: add EXPLORATORY rows.
4. **Minor: the "harm not measurable -> INCONCLUSIVE" gate is the agent's own rule** (pre-committed and logged).
   A literal PREREG reading would grade the raw ratios: RHO TEMP -15.3 FAIL, ES1 TEMP -33.5 FAIL, ETA TEMP 22.0 "PASS" (meaningless). H5a is FAIL either way.
5. **Minor (interpretation): the precision FAILs come entirely from R2 (mostly R2b) background flags.**
   - R1 alone has precision 1.00/1.00 on RHO UNIT/TEMP, 0.90/0.91 on ETA UNIT/TEMP and 1.00 on ES1 UNIT, with recall >= 0.82.
     These values come from the `tp_R1`/`flag_R1` columns.
   - The designated R1|R2 set was pre-committed, so the verdicts are right.
   - The ledger reports per-rule recall but not per-rule precision. Adding it would show readers which rule fails.
6. **Minor: the audit is transductive.**
   - R2a, R2b and R3 are computed once on the full (injected or raw) set, so the flags on training rows use held-out-source labels.
   - This biases toward the filtered arm (toward PASS), so the H5b FAIL is robust.
   - The H5a UNIT recovery PASS does not depend on it: with a label-free R1-only filter, DES_ETA UNIT recovery = **1.095** (seeds 0-3).
7. **Minor: the ES2 H5b row is labelled FAIL with 0 rows flagged.** The two arms are identical, so the test is vacuous and INCONCLUSIVE would be more accurate. H5b overall is still FAIL.
8. **Minor (caveat): the H7a best-vs-best diff is inflated by one-class AUCs below chance.**
   - All one-class AUCs are < 0.5 (best IF 0.392). RF minus chance is only 0.234.
   - Part of the supervised signal is reporting style: failure rate is 15.5% when needle gauge is unreported vs 1.3% when reported.
   - Ablation without needle diameter (value and missing flag), 3 seeds: HGB 0.706, RF 0.660, IF 0.403. The gap stays about 0.30.
9. **Minor (caveat): the H7b PASS is borderline.**
   - The 5-seed means are stable: 0.107 (original), 0.111 (seeds 5-9), 0.110 with leak removal.
   - But 2 of 10 single seeds have HGB−KNN5 < 0.10 (seed 2: 0.0995, seed 9: 0.0976).
   - Reports should call it "borderline PASS". H7b supervised training also skipped `leak_mask_for_source`; this is negligible here (20 rows), but it should be noted.
10. **Minor (statistics): H5a CIs bootstrap over the 10 injection seeds, not over sources** as the common protocol says.
    Grading uses point estimates, so no verdict depends on these CIs except the agent's harm gate (see items 3-4).

### Verdict table (verifier recompute)

| Test | Verifier recompute |
|---|---|
| H5a cells | Agree, as listed in the ledger |
| H5a overall | FAIL, agree |
| H5b, each dataset | FAIL (7/7), agree; ES2 is better called INCONCLUSIVE |
| H5b overall | FAIL, agree |
| H5 | FAIL, agree |
| H7a | FAIL, agree |
| H7b | PASS, agree (borderline) |
| **H7 overall** | **FAIL (PREREG); family says PARTIAL** |
