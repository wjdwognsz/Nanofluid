# H1 + H9 adversarial verification

## Verifier findings

Verifier: an independent agent. I did not edit any of the family's files. Throwaway scripts and outputs are in
`process/verify_H1H9/` (v1–v11 scripts; `verifier_numbers.json` collects the numbers quoted below).

### Bottom line
- **H1 PASS (7/7) is confirmed and robust.** Every check below either reproduced it or left it standing.
- **H9 PASS reproduces exactly from the family's files, but it is fragile, and it flips to FAIL when exact duplicate
  records are removed.** C3 (the anchor condition) passes with zero margin (3/7, need 3). One of the three passes, ES1,
  comes from 161 fully identical duplicate records in the raw Cogni-e-SpinDB file. With those collapsed, ES1's anchor
  width ratio is 0.934 (> 0.9) in all 5 seeds. That leaves C3 at 2/7, so **H9 is FAIL under within-source
  deduplication**. This needs to be disclosed (must-fix), with a sensitivity row in the ledger and in the summary.

### 1. Leakage checks: passed
- **Source grouping of folds (H1 and H9).** I regenerated `group_folds(ds.group, 10, seed)` for all 7 datasets × 5 seeds.
  In 0 folds does a source appear in both train and test, and every row is tested exactly once.
- **H9 rows file.** Each row is predicted once per seed, each source sits in exactly one outer fold per seed, and y and
  source match the loader.
- **H9 anchors.** Anchor rows are excluded from evaluation. q' comes only from calibration (outer-training) sources'
  out-of-source residuals. No test row enters calibration.
- **H9 copy removal.** Leak removal (copies of a held-out source's rows) is applied in the outer fold and in the
  source-aware inner folds: on average 395 rows per fold are removed for DES_RHO, 51 for DES_ETA, and 0 for ES1/ES2.
- **Scaling.** The KNN StandardScaler sits inside the pipeline, so it is fit on training rows only.
- **Features.** All features are physical or chemical descriptors. Missing-value indicators (ES2 V/L/Q_missing, DYE
  missing columns) can act as source proxies. That helps random CV, which is the phenomenon H1 is about, so I do not
  count it as a bug.

### 2. Fidelity to PREREG
- **H1.** Implemented as specified: random 5-fold vs GroupKFold(min(10, n_sources)); 5 seeds; RF/GB/KNN; 20 pseudo seeds
  with the real size distribution; DES_RHO/DES_ETA raw and lineage-cleaned; leave-material-out is diagnostic only.
- **H1 deviation (minor, conservative).** The graded `group` scheme does not apply the common-protocol rule from PREREG
  §1, which removes copies of the held-out source from training. The family declared this choice and ran the leak-free
  version as EXPLORATORY. Leak-free gaps are greater than or equal to the plain gaps (DES_RHO 1.66 vs 1.00), so the
  verdicts cannot get worse.
- **H9.** Implemented as specified: outer GroupKFold(10), RF, naive (random 5-fold) vs source-aware (GroupKFold)
  calibration, 90 % split-conformal, k=3 anchors on sources with ≥ 8 rows, and calibration that simulates the same
  procedure. Two choices were fixed before results and are logged: row-pooled coverage, and a conformal quantile one
  order statistic above textbook, which is very slightly conservative. With source-averaged coverage instead, C2 would be
  7/7 and C3 4/7, so the pooled-vs-averaged choice does not drive the verdict.

### 3. Verdicts recomputed from the raw CSVs: all match the ledger
- **H1** (`h1_cv.csv`, `h1_pseudo.csv`): all 9 units reproduce the ledger's RF/GB/KNN gaps, pseudo p95 and condition
  flags exactly (overall 7/7 PASS). RMSEs recomputed from the stored per-seed predictions differ by at most 4e-6.
- **H9** (`h9_rows.csv.gz`, with the anchor draws replicated independently using the same RNG streams):

  | Dataset | Naive | Aware | Anchor | Ratio | C1/C2/C3 |
  |---|---|---|---|---|---|
  | ES1 | 0.6618 | 0.8991 | 0.8917 | 0.8349 | 1/1/1 |
  | ES2 | 0.4067 | 0.8532 | 0.8293 | 0.6118 | 1/0/0 |
  | DYE | 0.7664 | 0.8885 | 0.7745 | 0.8363 | 1/1/0 |
  | DES_RHO | 0.5849 | 0.9113 | 0.8817 | 0.9452 | 1/1/0 |
  | DES_ETA | 0.6250 | 0.9011 | 0.9000 | 0.7953 | 1/1/1 |
  | DES_MP | 0.6228 | 0.9044 | 0.9074 | 0.7877 | 1/1/1 |
  | IL_CELL | 0.7101 | 0.9116 | 0.8986 | 0.9921 | 1/1/0 |

  This gives C1 7/7, C2 6/7, C3 3/7, so PASS, identical to the ledger. My copy of `run()` also reproduces the family's
  seed-0 values exactly (ES1 anchor 0.891 / ratio 0.818; DES_ETA 0.896 / 0.792; DES_MP 0.910 / 0.785).

### 4. Stability: re-runs with unseen seeds
- **H1 DYE** (the weakest dataset), seeds 5–9 and pseudo seeds 20–39: RF gap 0.360 (original 0.331), GB 0.399 (0.360),
  KNN 0.474 (0.457), pseudo p95 0.084 (0.069). Still PASS.
- **H9 ES1**, seeds 5–7: naive 0.670, aware 0.899, anchor 0.897, ratio 0.838. Still C1/C2/C3 = yes.
- **H9 DES_ETA**, seed 5: 0.625 / 0.901 / 0.903, ratio 0.806. Yes.
- **H9 DES_MP**, seed 5: 0.616 / 0.902 / 0.908, ratio 0.783. Yes.
- Per-seed anchor coverage and width ratio in the family's files are tight. For each C3-passing dataset, every individual
  seed passes C3.

### 5. Statistical sanity
- **CI units.** All CIs are source bootstraps: H1 sums SE per source; H9 sums covered/n_eval per source over seeds. No
  row-level CIs.
- **H1 robustness (no verdict change):**
  - Source jackknife (drop any one source): minimum RF gap is DYE 0.243, ES2 1.28, DES_RHO 0.86; all stay ≥ 0.20.
  - Dropping DES_ETA's 28 rows below 0.2 cP: gap 1.48 (was 1.56).
  - DYE's pass depends on a few sources. Without its top-3 sources by group SE the gap is 0.065, and its CI lower
    bound (0.083) is below 0.20. This is already visible in the family's descriptive rows.

### 6. NEW issue (must-fix disclosure): within-source exact duplicates
`copy_mask` and `leak_mask_for_source` only handle duplicates between *different* sources. Within-source exact
(key, y) duplicates are not handled:

| Dataset | Rows | Within-source duplicates | Share |
|---|---|---|---|
| ES1 | 777 | 176 | 22.7 % |
| DES_MP | 3390 | 1209 | 35.7 % |
| DES_ETA | 5789 | 77 | |
| DES_RHO | 6937 | 54 | |
| ES2 | 267 | 8 | |
| IL_CELL | 674 | 4 | |
| DYE | 131 | 0 | |

- **ES1.** The raw file contains 161 fully identical records, identical in every column including the measured
  diameter. Three ES1 "sources" with ≥ 8 rows are a single record repeated 13, 13 and 9 times.
- **DES_MP.** The same DES is entered twice, once with IUPAC names and once with common names, with the components
  swapped. Canonicalisation turns these into identical rows.
- The H2H3H6 log and the H4 verifier already flagged this. The H1/H9 outputs do not mention it.

**H1 with duplicates collapsed** (same seeds as the family, full rule):

| Dataset | RF gap (orig. → dedup) | GB | KNN | Pseudo p95 | Verdict |
|---|---|---|---|---|---|
| ES1 | 0.885 → 0.618 | 0.792 | 0.603 | −0.0005 | PASS |
| DES_MP | 1.448 → 1.058 | 1.280 | 1.031 | −0.040 | PASS |

- ES1 random-CV RMSE goes from 0.177 to 0.195; DES_MP from 18.6 K to 24.2 K.
- About 30 % of these two gaps came from random CV memorising duplicate records.
- DES_MP's leave-material-out gap becomes −0.04, so the remaining DES_MP gap is clearly not material novelty.
- No verdict change. The headline gaps should be quoted alongside the dedup values.

**H9 with duplicates collapsed** (my copy of the family's `run()`):

| Dataset (seeds) | Naive | Aware | Anchor | Ratio | Effect |
|---|---|---|---|---|---|
| ES1 (5 seeds) | 0.719 | 0.903 | 0.891 | **0.934** (per seed 0.922–0.953) | **C3 fails** |
| DES_MP (2 seeds) | 0.69 | 0.90 | 0.90 | 0.77–0.79 | C3 still passes |
| ES2 (5 seeds) | 0.442 | 0.849 | 0.833 | 0.605 | still fails C2 and C3 |

- **ES1 mechanism.** The duplicate records give zero-valued anchor-calibration scores, which shrinks q'. On the test
  side they are covered trivially: the 3 single-record sources have anchor coverage 1.000. The ≥ 8-row calibration
  restriction alone already gives ratio 0.95 in the deduplicated ES1. Against that, the anchor offset narrows the
  interval by only about 2 % (0.986 / 1.005).
- **ES2.** No dataset can compensate for ES1's lost pass: ES2 still fails both conditions, and DYE (0 duplicates),
  DES_RHO (ratio 0.945) and IL_CELL (ratio 0.992) fail C3 by margins that 0–54 duplicate rows cannot close.
- **Result: C1 7/7, C2 6/7, C3 2/7, so H9 is FAIL under deduplication.**

### 7. Exploratory construct check: material overlap of anchors (no verdict change under PREREG)
Anchors are random rows of the new source, so they can share a material with the evaluated rows.

- **ES1.** 97.9 % of evaluated rows share a material with an anchor, because papers mostly study one polymer–solvent
  system. So ES1's "anchor" effect is effectively same-material calibration, not a reference-sample effect.
  - Material-disjoint evaluation with recalibrated q' (seed 0) covers only 125 evaluations from 6 sources: coverage 0.744,
    ratio 0.964.
- **DES_ETA.** 20 % of evaluated rows share a material. The result holds with material-disjoint anchors and
  recalibration (seed 0): coverage 0.898, ratio 0.826.
- **DES_MP.** 3 % share a material. Material-disjoint: coverage 0.910, ratio 0.793.
- **Control for the ≥ 8-row calibration restriction** (aware q from ≥ 8-row sources, no offset): ratio 0.985 (ES1, with
  duplicates), 0.994 (DES_ETA), 0.995 (DES_MP). On the original data, the narrowing really does come from the anchor
  offset.

### What survives
- **H1.** Robust everywhere.
- **H9 C1 (naive under-covers new sources).** Robust: 7/7, including after deduplication.
- **H9 C2 (source-aware intervals reach ~0.90 pooled coverage).** Robust in 6/7. Lower CI bounds stay < 0.87 in 6/7, as
  the family already reported.
- **H9 C3 (anchor-recalibrated intervals).** Real and robust in DES_ETA and DES_MP, including material-disjoint and
  deduplicated checks. Not supported in ES1 once duplicate records are removed.

The honest H9 headline is **"PASS as pre-registered, but FAIL under within-source deduplication. The anchor-interval
claim rests on 2 DES datasets."**
