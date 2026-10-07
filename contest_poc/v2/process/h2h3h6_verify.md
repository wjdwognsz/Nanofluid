# H2 + H3 + H6 adversarial verification

Verifier: an independent agent. It did not edit the family's scripts, results or ledgers. Throwaway scripts and outputs are in
`process/verify_H2H3H6/` (v1–v11). Runs used VRR_NJOBS=2 and OMP_NUM_THREADS=2. The heaviest single command took 4 min 14 s.

## Verifier findings

### Summary
- Every graded verdict reproduces from the raw CSVs and follows PREREG:
  - H2 P2a/P2b/P2c PASS → H2 PASS
  - H3a PASS 5/5
  - H3b FAIL 0/2
  - H6a DES_RHO PASS, DES_ETA FAIL → H6a/H6 PASS
- No leakage was found:
  - OOF folds are grouped by source (0 sources split across folds, for all 7 datasets × 5 seeds).
  - Leak rows were removed in `rm` whenever a fold had any.
  - Seed-0 predictions reproduce bit-for-bit (max |Δ| ≈ 1e-14 on ES1 and IL_CELL).
- None of the issues below flips a verdict, so `must_fix = false`. Four of them should be added as caveats in the ledger notes or the summary, because the current text overstates certainty.

### Checks that passed (with numbers)
1. **Recomputing verdicts from the raw files** (`v1_recompute.py`)
   - P2a median |Δρ| = 0.00520 (≤ 0.010)
   - P2b fold = 1.3678 (≥ 1.10)
   - P2c 0.0356 − 0.1685 = −0.1329 (< 0)
   - H3a R and null p95 from `h3_splithalf*.csv` match the ledger for all 5 datasets.
   - H3b Spearman ρ = 0.245 (DES_RHO; asymptotic p 0.117) and −0.252 (DES_ETA).
   - H6a change −0.2472 and −0.0178. A source bootstrap with a different seed gives CI [−0.3845, −0.0430] and [−0.0403, −0.0042].
   - The H2 R² values (0.067 / −0.147 / −0.221 / 0.880 / 0.483 / 0.600 / 0.209) recompute exactly.
   - ES1 near-condition pairs (51 pairs, median 0.1900; 1536 same-paper pairs, median 0.00094) equal v1 `electrospin_summary.json`.
2. **New-seed re-run** (`v6_oof_seed.py` seed 11 for all five H3a-eligible sets, then `v7`, `v8`, `v10`)
   - H3a R with seed-11 residuals and fresh split/null/bootstrap RNG streams: ES1 0.903, DES_RHO 0.774, DES_ETA 0.924, DES_MP 0.951, IL_CELL 0.945. All pass.
   - H6a DES_RHO −24.85 %, CI [−38.2 %, −3.7 %] (pass). DES_ETA −1.1 %, CI [−4.1 %, +0.8 %] (fail).
3. **H3a robustness** (`v7_h3a_checks.csv`)
   - The leave-one-source-out minimum R is ≥ 0.73 in every dataset.
   - With a rank (Spearman) split-half instead of Pearson, R = 0.72–0.95.
   - With ES1's 176 exact within-paper duplicate rows collapsed: R = 0.872, CI [0.589, 0.970] > null p95 0.449. Still passes.
   - H3a overall would also stay PASS without ES1 (4/5).
4. **H6a mechanism control** (`v8`, seed 0)
   - Dropping as many *random* rows from training as there are leak rows, while keeping the copies, changes DES_RHO RMSE by only 3.6 %.
   - Removing the copies changes it by 22.5 %.
   - So the effect comes from the copies themselves, not from having less training data.
5. **H6c without any matching** (`v9`)
   - 90/90 ES2 diameters in the 14 DOI-shared papers appear among ES1's diameters for the same paper. The chance rate using values from other papers is 6.3 %.
   - 14 shared DOIs out of ES2's 28 sources is confirmed. The 100 % identity result does not depend on the matching tolerances.
6. **PREREG fidelity**
   - Thresholds, split modes, 50 splits, 200 permutations, 5000 H3b permutations, GroupKFold(10) RF with leak copies removed: all as specified.
   - Agent-chosen interpretations are disclosed in the log: point estimate decides H2; two-sided H3b; H3 and H6 combination rules.
   - PREREG was committed at 09:42, before the family's scripts ran (from 11:29).

### Issues (all minor, verdicts unchanged)
1. **H2 CIs use source pairs, not sources, as the resampling unit.**
   - PREREG's common protocol says "출처 단위 부트스트랩".
   - A source-level bootstrap gives (`v2`):
     - P2a CI [0.0025, 0.0102]
     - P2b fold CI [1.004, 1.944]
     - **P2c difference CI [−0.326, +0.029]**, which includes 0 (8 % of draws ≥ 0)
   - The verdicts are decided by point estimates, as pre-committed, so they stand. But "P2c CI excludes 0" should not be claimed.
   - Report the source-level CI next to the source-pair CI.
2. **One near-copy source pair remains in the H2 DES_ETA "independent" set.**
   - 10.1002/apj.1873 vs 10.1021/je300997v: 28 key pairs agree within 0.5 %, but not within rtol 1e-4 (`v4`).
   - Excluding it raises the fold from 1.368 to 1.474 and P2c from −0.133 to −0.173. The bias is conservative.
   - DES_RHO has no such source pair. Dropping every pair with |Δρ| ≤ 0.0006 gives a median of 0.0076, still ≤ 0.010.
   - The same exact-match lineage rule also misses this pair in the H3, H4 and H6a leak masks.
3. **The H6a DES_RHO pooled change is dominated by one compilation source.**
   - 10.1002/aic.18095 has 2667 of 6937 rows and its own change is −47.5 %.
   - Pooled change without it: −9.0 %, which would miss the −10 % rule.
   - The per-source mean over all 132 sources is −20.6 %, CI [−25.7 %, −16.0 %], so the PASS is not an artefact. But the ledger note should state that one source dominates the pooled number.
4. **The H3b DES_RHO ρ is very sensitive to the residual seed.**
   - ρ by seed (`v11_h3b_seeds.csv`):

     | seed | 0 | 1 | 2 | 3 | 4 | 11 | seed-averaged prediction |
     |---|---|---|---|---|---|---|---|
     | ρ | 0.245 | 0.187 | 0.092 | −0.003 | 0.075 | −0.007 | 0.131 |

   - The reported seed 0 is the most favourable of the six.
   - The FAIL is robust. However, the log's forking-path note ("no_copy_rows ρ = 0.313, p = 0.044 would pass") is a seed-0 artefact: other seeds give 0.045–0.254.
   - The agent reported seed robustness for H3a but not for H3b. Add it.
5. **A malformed reference string acts as one giant "source".**
   - In DES_ETA, `http://pubs.acs.org/journal/acscii` is a journal URL, not a paper, and holds 1461 rows (25 %). It is probably a pooled compilation of several papers.
   - It appears in 72 of 189 H2 pairs and is one unit in H3a and H6a.
   - Influence: P2b fold without it is 1.26, still a pass. H6a DES_ETA without it is −0.9 %.
   - This is a loader-level issue shared by all families and is not mentioned in the H2H3H6 log.
6. **Interpretation caveats (already disclosed, restated because they matter at the concept level)**
   - ES1's H3a "material-disjoint" result uses the row-random fallback for 21/26 sources. Its strict 5-source R is −0.17.
   - For DES, "material" includes the mole fraction, so the halves can share a chemical system. The system-disjoint strict R for DES_RHO is 0.571.
   - The agent defined the H3 overall label PARTIAL; PREREG gives no combination rule. The §3 core chain should cite "H3a PASS / H3b FAIL" explicitly.
   - The ledger has a "nan" CI on the exploratory ES1 strict row (cosmetic).
