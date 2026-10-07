# H1 + H9 process log — Evaluation inflation (H1) and source-aware trust intervals (H9)

Chronological, honest notes. Times are local container time (date 2026-10-07).
Nothing below the "commitments" section was decided after seeing an H1/H9 number unless explicitly marked.

## 10:36 — Setup and profiling (no H1/H9 modelling result seen yet)

- Read PREREG.md §2 H1 and H9, vrr_common.py, vrr_data.py, the H4 log (for conventions).
- Profile (rows / sources / max source size / sources >= 8 rows / materials / copy rows by copy_mask / leak rows summed over sources):
  - ES1 777 / 54 / 96 / 33 / 23 / 0 / 0
  - ES2 267 / 28 / 56 / 10 / 25 / 0 / 0
  - DYE 131 / 12 / 70 / 4 / 129 / 2 / 4
  - DES_RHO 6937 / 132 / **2667** / 101 / 838 / **1975** / 3982
  - DES_ETA 5789 / 114 / 1461 / 79 / 882 / 256 / 514
  - DES_MP 3390 / 115 / 388 / 71 / 2144 / 10 / 20
  - IL_CELL 674 / 33 / 117 / 19 / 342 / 4 / 7
  - Lineage-cleaned (subset(ds, ~copy_mask(ds))): DES_RHO 4962 rows, DES_ETA 5533 rows.
- Timing with VRR_NJOBS=2, OMP_NUM_THREADS=2 (HistGB uses OpenMP; I pin it to 2 threads so as not to take the other
  agent's cores): full DES_RHO fit RF 1.5 s, GB 0.8 s, KNN 0.1 s; ES1 RF 0.46 s.
- Note: DES_RHO has one source with 2667 of 6937 rows (38%). Any row-pooled metric is dominated by it; I report
  source-averaged versions next to every row-pooled one (decided now, before results).

## 10:40 — Interpretations fixed BEFORE running (pre-results commitments)

### H1
1. Schemes (all via vrr_common): `random` = random_folds(n, 5, seed); `group` = group_folds(ds.group, 10, seed)
   (GroupKFold(min(10, n_sources)) with seeded relabelling); `material` = group_folds(ds.material, 10, seed)
   (diagnostic, not graded). Seeds 0–4; the model seed equals the fold seed. Models RF, GB, KNN (make_model).
2. Plain GroupKFold for `group` (no leak removal), as the task specifies. An extra RF-only scheme `group_leakfree`
   (same folds, but training rows that duplicate key+value of a test-fold row from another source are dropped,
   leak_mask_for_source union over test sources) is EXPLORATORY: it shows how much copies hide the gap.
3. Gap per model = mean_seed(RMSE_group) / mean_seed(RMSE_random) − 1 (RMSE over all rows, one out-of-fold prediction
   per row per seed). Per-seed gaps are kept in the raw file.
   95% CI = source bootstrap (2000, seed 0): resample sources; gap* = sqrt(ΣSE_group / ΣSE_random) − 1 where SE is the
   per-row squared error averaged over the 5 seeds. (Point estimate and CI use slightly different averaging — mean of
   RMSE vs RMSE of mean SE — the difference is tiny; noted, not hidden.)
4. Negative control: 20 seeds j = 0..19, groups = pseudo_groups(ds.group, seed=j), folds = group_folds(pseudo, 10, seed=j)
   (so the same k = min(10, n_sources) as the real group scheme), RF only (model seed j).
   pseudo gap_j = RMSE_pseudo_j / mean_seed(RMSE_random, RF) − 1. Threshold = np.percentile(pseudo gaps, 95) (linear).
5. Dataset rule (PREREG): PASS iff RF gap >= 0.20 AND RF gap > pseudo p95 AND max(GB gap, KNN gap) >= 0.10; else FAIL.
6. Which variant is graded for DES_RHO / DES_ETA: the **raw** variant counts for the 7-dataset overall (all 7 datasets
   are defined raw in PREREG §1). The lineage-cleaned variants get their own graded rows (dataset = DES_RHO_lineage,
   DES_ETA_lineage) and an overall sensitivity row (same rule with the clean variants substituted). If the sensitivity
   verdict differs from the primary, both are reported and the discrepancy is stated.
7. Overall: >= 5 of 7 PASS → PASS, <= 3 → FAIL, 4 → PARTIAL.
8. Leave-material-out (`material`) gap: DESCRIPTIVE only.

### H9
1. Outer split: group_folds(ds.group, 10, seed) — source GroupKFold(10). Seeds 0–4 (common protocol: 5 seeds), the seed
   changes outer folds, inner folds, RF seed and anchor draws. RF only (PREREG).
2. Protocol lineage rule: for each outer fold, outer-training rows that duplicate (key+value) a row of an outer-test
   source are removed (union of leak_mask_for_source over test sources). Applies equally to all three methods.
3. Final model: RF fit on the (leak-cleaned) outer-training part, predicts the outer-test rows.
4. Calibration residuals inside the outer-training part:
   (i) naive: random_folds(n_train, 5, seed) out-of-fold residuals (no leak removal — that is what "naive" means);
   (ii) source-aware: group_folds(group_train, 10, seed) (k = min(10, n_train_sources)) out-of-source residuals, with
        the same leak removal inside each inner fold.
   (The fold counts differ, 5 vs 10, as in the task text; 10-fold trains on more data, which makes (ii) residuals
   slightly *smaller*, i.e. conservative against H9.)
5. Split-conformal 90%: score = |residual|, q = np.quantile(scores, min(1, ceil((n+1)·0.9)/n), method="higher");
   interval = pred ± q; width = 2q.
6. (iii) anchor-adjusted, only for outer-test sources with >= 8 rows: 10 draws of k = 3 random anchor rows;
   offset = mean(y − pred) over anchors; adjusted interval = pred + offset ± q'; evaluated on non-anchor rows.
   q' = conformal quantile of simulated scores on calibration sources: for every outer-training source with >= 8 rows
   (same eligibility as test), 10 draws of 3 anchors from its (ii) out-of-source residuals, score = |r − mean(r_anchor)|
   on the non-anchor rows; all scores pooled (n = number of pooled scores).
   RNG: default_rng([seed, fold, 1]) for calibration simulation, default_rng([seed, fold, 2]) for test anchors;
   sources iterated in sorted order.
7. Primary coverage = row-pooled over all outer-test rows (each row once per seed), averaged over the 5 seeds;
   width = row-weighted mean of 2q. 95% CI = source bootstrap (2000, seed 0) of pooled coverage (per-source covered
   counts summed over seeds). Secondary (DESCRIPTIVE): source-averaged coverage, share of sources with coverage < 0.8.
8. Anchor comparison is paired: width ratio = mean 2q' / mean 2q_aware over exactly the same evaluated
   (non-anchor) rows; coverage of (iii) on those rows (aware coverage on the same rows also reported).
9. Dataset-level conditions: C1 naive coverage < 0.85; C2 aware coverage >= 0.87; C3 anchor width ratio <= 0.9 AND
   anchor coverage >= 0.87. Hypothesis: PASS iff C1 holds in >= 4 of 7, C2 in >= 5 of 7, C3 in >= 3 of 7; else FAIL.
   PREREG gives no PARTIAL band for H9, so none is invented.
10. EXPLORATORY extra (not graded): anchor offset applied but with the un-recalibrated q_aware (shows whether the
    recalibration step q' is needed).

## 10:44–10:52 — Scripts written: `scripts/h1_cv.py`, `scripts/h9_conformal.py`

- h1_cv.py modes: `cv DATASET [--variant raw|lineage] [--models ...]`, `pseudo DATASET [--variant]`, `summarize`.
  Partial outputs per (dataset, variant, part) under `results/raw/h1_parts/` so that every command stays < 9 min.
- Smoke test on DYE (cv 183 s, pseudo 85 s) and a summarize dry-run with only DYE present: the code path works
  (other datasets correctly reported as INCONCLUSIVE "not run" in that dry-run; that ledger was overwritten later).
- DYE cv was surprisingly slow for 131 rows (183 s): RF with n_jobs=2 has ~0.4 s fixed overhead per fit (thread pool
  start-up), so small datasets are overhead-dominated. No change made.

## 10:47–11:48 — H1 runs (dataset by dataset)

| unit | cv wall | pseudo wall |
|---|---|---|
| DYE raw | 183 s | 85 s |
| ES2 raw | 111 s | 83 s |
| ES1 raw | 141 s | 87 s |
| IL_CELL raw | 150 s | 96 s |
| DES_MP raw | 257 s | 196 s |
| DES_RHO raw | 240 s (RF) + 104 s (GB,KNN) | 286 s |
| DES_ETA raw | 233 s (RF) + 98 s (GB,KNN) | 265 s |
| DES_RHO lineage | 295 s | 231 s |
| DES_ETA lineage | 324 s | 263 s |

- Process mistakes (no effect on results, but cost time):
  1. I waited for the ES2 background job with `until grep "pseudo ES2/raw:"`, but I had piped the job through
     `tail -3`, which only kept the `time` lines, so the marker never appeared; the waiter hit its 9-min timeout.
  2. `pkill -f "until grep -q"` then killed my own new shell (its command line contained the same string) → exit 144;
     re-ran ES1 without the pkill. Lesson: run each chunk in the foreground with its own timeout.
- No exceptions, no NaN predictions (assert in oof()), no deviations from the protocol: all 5 seeds, 3 models,
  20 pseudo seeds, both lineage variants were run in full. HistGB pinned with OMP_NUM_THREADS=2.

## 11:49 — H1 graded result (first look at H1 numbers)

- All 7 datasets PASS all three conditions; both lineage-cleaned variants PASS too → **H1 overall PASS (7/7)**,
  sensitivity (lineage variants substituted) also 7/7.
- RF gap (pooled, mean of 5 seeds) [source-bootstrap 95% CI]: ES1 0.885 [0.635, 1.267]; ES2 2.089 [0.736, 3.164];
  DYE 0.331 [0.083, 0.676]; DES_RHO 1.003 [0.466, 1.729]; DES_ETA 1.560 [0.903, 2.292]; DES_MP 1.448 [0.989, 1.948];
  IL_CELL 0.555 [0.266, 0.919]; DES_RHO_lineage 1.165; DES_ETA_lineage 1.615.
- The pseudo-source control never came close: pseudo gaps range from −0.066 to +0.107 (p95 ≤ 0.069 everywhere), i.e.
  random fake "sources" behave like random CV. So the gap is not an artefact of 10-fold vs 5-fold or of uneven fold sizes.
  Honest caveat: this control is easy to pass (it only rules out fold-mechanics artefacts, not material novelty).
- Weakest case: DYE (12 sources; RF gap 0.33, CI lower bound 0.08; one source of 70/131 rows carries 60% of the
  group-CV squared error).

## 11:51 — Things the H1 numbers do NOT show (looked at per-source and the material diagnostic)

- **Pooled gaps are pulled by some sources.** Per-source view (RF): median per-source RMSE ratio group/random is
  1.70 (ES1), 1.42 (ES2), 1.10 (DYE), **1.02 (DES_RHO)**, 1.36 (DES_ETA), 1.57 (DES_MP), 1.32 (IL_CELL).
  In DES_RHO only 60% of sources get worse under source CV; the typical density source is predicted about as well as
  under random CV, and the pooled 100% gap comes from a subset of sources with large errors. (The source-averaged
  gap, each source weighted equally, is 0.33 for DES_RHO; 0.22 for DYE; 0.38–0.92 elsewhere.) Added as a
  DESCRIPTIVE ledger row `H1_desc_source_avg` (the source-averaged view was declared at 10:36, before results; the
  exact form of the row — mean ratio, median, top-1 share — was chosen now, after seeing results).
- **Source novelty vs material novelty (diagnostic, not graded).** Leave-material-out gap (RF): ES1 1.10 (> source gap 0.88),
  ES2 1.87, DES_RHO 1.01 (≈ source gap), DES_ETA 0.54, DES_MP 0.12, IL_CELL 0.16, DYE −0.02.
  - ES1/ES2/DES_RHO: unseen-material error is as large as unseen-source error, so in these sets the H1 gap cannot be
    attributed to "source effects" alone; papers mostly study their own material systems (ES1: 27/33 papers report a
    single polymer–solvent system, see H4 log).
  - DES_ETA, DES_MP, IL_CELL: source gap ≫ material gap → a large part of the new-source error is NOT explained by
    material novelty. Caveat: 'material' for DES = exact composition A|B|x_A, so leave-material-out still keeps the same
    component pair at other ratios; this diagnostic is weaker than a leave-component-pair-out split.
  - DYE: 129 materials for 131 rows, so leave-material-out ≈ random CV (gap −0.02) — uninformative.
- **Copies hide part of the gap (EXPLORATORY, RF).** With leak-free group folds (copies of test-fold rows removed from
  training) DES_RHO's gap rises from 1.00 to 1.66; DES_ETA 1.56 → 1.61; others unchanged (no or few copies).
  In DES_RHO the compilation copies make plain source-CV look better than it is. The lineage-cleaned DES_RHO gap is 1.17.

## 11:53–13:03 — H9 runs (per dataset, seeds chunked so each command < 9 min)

| dataset | wall time (5 seeds) | note |
|---|---|---|
| DYE | 357 s | smoke test; summarize dry-run on DYE only to test the code path |
| ES2 | 369 s | |
| ES1 | 290 s (seeds 0–3) + 74 s (seed 4) | |
| IL_CELL | 285 s + 71 s | |
| DES_MP | 342 s (0–1) + 512 s (2–4) | the 3-seed chunk took 8.5 min — too close to the limit; switched to ≤ 2 seeds per command |
| DES_RHO | 195 s + 377 s + 379 s | load average 5.5 at that time (other agents running) |
| DES_ETA | 380 s + 383 s + 192 s | |

- No exceptions, no NaN residuals (asserted), no protocol deviation: 5 seeds × 10 outer folds × 7 datasets = 350
  fold records per method; every row is predicted exactly once per seed and every source sits in exactly one outer
  fold per seed (checked from h9_rows.csv.gz).
- Small datasets are again overhead-dominated (DYE 131 rows took as long as ES2/ES1).

## 13:00 — H9 graded result (first look at H9 numbers)

Row-pooled coverage of the 90% interval on new (outer-test) sources, mean of 5 seeds [source-bootstrap 95% CI]:

| dataset | naive (i) | aware (ii) | anchor (iii) | width ratio anchor/aware (same rows) | C1 | C2 | C3 |
|---|---|---|---|---|---|---|---|
| ES1 | 0.662 [0.547, 0.775] | 0.899 [0.834, 0.954] | 0.892 | 0.835 | yes | yes | **yes** |
| ES2 | 0.407 [0.250, 0.622] | **0.853** [0.659, 0.996] | **0.829** | 0.612 | yes | **no** | **no** (coverage) |
| DYE | 0.766 [0.683, 0.991] | 0.889 [0.828, 1.000] | **0.775** | 0.836 | yes | yes | **no** (coverage) |
| DES_RHO | 0.585 [0.508, 0.723] | 0.911 [0.886, 0.953] | 0.882 | **0.945** | yes | yes | **no** (width) |
| DES_ETA | 0.625 [0.518, 0.695] | 0.901 [0.820, 0.946] | 0.900 | 0.795 | yes | yes | **yes** |
| DES_MP | 0.623 [0.515, 0.711] | 0.904 [0.840, 0.949] | 0.907 | 0.788 | yes | yes | **yes** |
| IL_CELL | 0.710 [0.633, 0.809] | 0.912 [0.862, 0.956] | 0.899 | **0.992** | yes | yes | **no** (width) |

- C1 7/7 (need 4), C2 6/7 (need 5), C3 3/7 (need 3) → **H9 PASS**, but C3 is met with zero margin.

## 13:04 — Honest reading of H9 (what is strong, what is weak, what failed)

Strong:
- Naive (random-CV) calibration under-covers new sources in **every** dataset (0.41–0.77 vs nominal 0.90); the upper
  CI bound is < 0.85 in 6/7 (ES1 0.775, ES2 0.622, DES_RHO 0.723, DES_ETA 0.695, DES_MP 0.711, IL_CELL 0.809); the
  exception is DYE (upper bound 0.991, 12 sources). Per-seed spread is tiny (e.g. DES_RHO 0.583–0.588).
- Source-aware calibration restores ~0.90 pooled coverage in 6/7 datasets.

Weak / failed:
- **ES2 fails C2 (0.853).** One source (10.1117/12.837918, 56 of 267 rows) has aware coverage 0.35; the source-averaged
  aware coverage is 0.97. The pooled estimand is dominated by that source. (I committed to the pooled estimand before
  results; I do not switch.)
- **The point estimates pass, the CIs do not:** the lower CI bound of aware coverage is below 0.87 in 6/7 datasets
  (only DES_RHO 0.886 is above). With 12–132 sources, "≥ 0.87" is not established with confidence anywhere except DES_RHO.
- **Coverage is marginal, not per source.** Share of sources with aware coverage < 0.8: ES1 0.22, ES2 0.04, DYE 0.08,
  DES_RHO 0.12, DES_ETA 0.18, DES_MP 0.22, IL_CELL 0.15. A trust label built this way is a population statement,
  not a per-lab guarantee.
- **Honest intervals are wide.** Mean width / SD(y) (descriptive, added after results): aware 3.33 (ES1), 3.25 (ES2),
  3.47 (DYE), 2.99 (IL_CELL) — about the width of a 90% Gaussian interval of the whole dataset (3.29 SD), i.e. for a new
  source the model's honest interval is barely narrower than knowing nothing but the dataset spread (consistent with H1:
  source-CV R² 0.07 ES1, −0.15 ES2, −0.19 DYE, 0.21 IL_CELL). DES sets are more informative: DES_RHO 1.19, DES_ETA 2.18,
  DES_MP 2.19. Naive intervals are 2–5x narrower (DES_RHO naive width is 0.20x the aware width) — that is exactly the
  over-confidence H9 is about.
- **Anchor recalibration (iii) only helps where H4 anchors help.** It narrows intervals by 16–21% at ~0.90 coverage in
  ES1, DES_ETA, DES_MP; in ES2 it narrows by 39% but coverage is 0.829 (< 0.87; still better than aware's 0.780 on the
  same rows); in DYE coverage drops to 0.775 (the 70-row in-house "Lab" source: 0.71); in DES_RHO it barely narrows
  (0.945) and the 2667-row source 10.1002/aic.18095 loses coverage (0.885 → 0.794) — the same density failure as H4;
  in IL_CELL q' ≈ q (ratio 0.992), no gain. Of the 3 passing datasets, the anchor coverage CI lower bounds are below 0.87
  (ES1 0.813, DES_ETA 0.859, DES_MP 0.844).
- EXPLORATORY: applying the anchor offset but keeping the un-recalibrated aware q gives 0.93–0.95 coverage in ES1,
  ES2, DES_ETA, DES_MP (over-coverage at full width) → the recalibration step is what converts the anchor gain into
  narrower intervals.

Implementation notes / possible objections (logged, not changed):
- Conformal quantile uses np.quantile(|r|, ceil((n+1)·0.9)/n, method="higher") as in the common reference code. That is
  one order statistic above the textbook ceil((n+1)·0.9)-th smallest score → very slightly conservative (n ≥ 61 here).
- The calibration residuals come from inner models trained on 80% (naive) / ~90% (aware) of the outer-training part,
  the final model on 100%: standard CV-based conformal approximation, not exact split-conformal.
- Pooled anchor calibration scores (10 draws per calibration source) are not exchangeable in the textbook sense; q' is
  an empirical recalibration, not a finite-sample guarantee.
- Verification: recomputed per-fold naive/aware coverage from h9_rows.csv.gz: aware identical (max diff 1e-16); naive
  max diff 0.002 in one fold = CSV rounding (%.6g) of a residual sitting at the q boundary. H1 RMSEs recomputed from the
  stored per-seed predictions: max relative diff 5e-6. All 450 H1 cv rows have 5 seeds; all 9 pseudo units have 20 seeds.

## 13:06 — Deviations from PREREG / task text (complete list)

1. None in scope: all datasets, variants, seeds (5), models (RF/GB/KNN), pseudo seeds (20) and H9 methods were run in full.
2. Choices that PREREG left open were fixed at 10:40 before results (see above): raw variant counts for H1 overall;
   pooled coverage graded for H9; leak removal in H9 outer and aware-inner folds but not in naive folds; plain GroupKFold
   for H1 group scheme.
3. Added after seeing results (all non-graded): H1_desc_source_avg row form (top-1 share, gap without top source),
   H9_desc_width_over_sd. Exploratory rows (H1_explore_group_leakfree, H9_explore_offset_q_aware) were declared at 10:40.

## 13:08 — Files

- scripts/h1_cv.py, scripts/h9_conformal.py
- results/h1_summary.json, results/h9_summary.json
- ledger/h1.csv (83 rows), ledger/h9.csv (53 rows)
- raw (for figures): results/raw/h1_cv.csv (dataset, variant, model, seed, scheme, rmse, r2, ...; 450 rows),
  h1_pseudo.csv (180 rows = 9 units × 20 seeds), h1_seed_gaps.csv, h1_per_source.csv (per-source RMSE per scheme),
  h1_rows.csv.gz (row-level seed-mean predictions); h9_conformal.csv (dataset, seed, fold, method, coverage, width, n, q ...),
  h9_per_source.csv, h9_rows.csv.gz (row-level y, pred, q_naive, q_aware, q_anchor per seed/fold).
- results/raw/h1_parts/ (8.2 MB, per-seed predictions) and h9_parts/ (2.0 MB) are the per-chunk caches that
  `summarize` reads; they can be regenerated with the run commands.
