# H5 + H7 process log — audit rules (H5a injection, H5b real value) and failure-data value (H7a PVDF, H7b DES)

Chronological, honest notes. Times are container time (UTC, 2026-10-07), taken from `date -u` at the moment of writing.
Failures, bugs, dead ends and deviations are recorded here as they happen (the user asked for the process, not only the result).

## 11:55 — Setup and profiling

- Read PREREG.md (H5, H7 and the common protocol), vrr_common.py, vrr_data.py, v1 `scripts/survivor.py`, and the head of
  `process/h2h3h6_log.md` / `ledger/h6.csv` for conventions (lineage-cleaned variant = `subset(ds, ~copy_mask(ds))`).
- Loader profile (rows / sources): ES1 777/54, ES2 267/28, DYE 131/12, DES_RHO 6937/132 (lineage-clean 4962),
  DES_ETA 5789/114 (lineage-clean 5533), DES_MP 3390/115, IL_CELL 674/33. ES1 PVDF failure set: 351 rows, 32 unstable rows,
  10 failure papers (matches PREREG "32건/10편").
- Timing: RF(300 trees, n_jobs=2) fit on ~4,500 DES rows ≈ 1.0–1.1 s; HistGB 0.7–3.7 s. Load average 1.3–2.5 (another agent active).

### What I looked at before fixing the rules (disclosure)
To decide the *units* of each column (needed to write R1), I printed column ranges at 11:59:
- DES T 278.15–413.15 K (RHO) / 278.15–378.15 K (ETA), mode 298.15 K in both lineage-clean bases.
- ES1 fiber_diameter_nm 55–13,080 nm; ES1 temperature_c reported in 571/777 rows, 18–50 °C; rh reported in 768/777 rows.
- ES2 D 28–7,994 (→ nm). DYE T 100–115 (→ °C). IL_CELL T 20–200 (→ °C).
- DES_MP y range 77.9–598.8 K, and 2,594 / 3,390 rows have melting T > 298.15 K (the H7b "failure" class is the *majority*).
  Note: this also told me that R1's 150–500 K temperature range will flag some real DES_MP rows in H5b. R1's bounds are fixed
  by PREREG, so nothing could be tuned with this knowledge, but it is disclosed.
- No audit flag count, no injection result, no AUC had been computed when the commitments below were written.

## ~12:02 — Design commitments fixed BEFORE writing/running any test code

Audit rules (PREREG R1–R4; the parts PREREG leaves open are fixed here and coded in `scripts/vrr_audit.py`):
- R1 physical range. Target: density 0.5–3.0 g/cm³ (DES_RHO y_raw), viscosity 0.2–1e7 cP (DES_ETA y_raw),
  fiber diameter 10–50,000 nm (ES1 fiber_diameter_nm, ES2 D). Temperature 150–500 K on every temperature column
  (DES T in K; ES1 temperature_c, DYE T, IL_CELL T are °C → +273.15 before the check; imputed/missing values are not checked)
  **and on the target when the target is a temperature (DES_MP melting T)**. No R1 bound exists in PREREG for exhaustion (DYE)
  or cellulose solubility (IL_CELL) → no target range check there (not added, to stay inside PREREG).
- R2 robust z, |z| > 5 on the modelling scale `ds.y`:
  R2a within-material (ds.material groups with ≥ 3 rows), z = (y − median)/(1.4826·MAD); the scale is floored at
  0.05 × the dataset-wide robust scale (1.4826·MAD(y)) so that groups of identical values (MAD = 0) do not flag every deviation.
  R2b out-of-source residual: RF (make_model "RF", seed 0), GroupKFold(10) by source (group_folds seed 0), residual robust z.
- R3 copy: a row is flagged if a row of a *different* source has the same key and the same value (|rel diff| ≤ 1e-4 on
  y_raw if present, else y). Both sides of a pair are flagged (literal PREREG wording) — so R3 precision for injected copies
  is ≤ ~0.5 by construction (not graded in PREREG).
- R4 default concentration: condition columns = ambient / measurement conditions that are typically unreported and filled
  with a nominal value: DES_RHO/DES_ETA `T`; ES1 `rh` and `temperature_c` (reported values only). Set-point process
  parameters (voltage, flow, distance, dye T/pH/owf, dissolution T/time) are not R4 columns → R4 does not apply to
  ES2, DYE, IL_CELL, DES_MP. For each R4 column: dataset mode of reported values; a source is suspicious if > 40 % of its
  reported rows equal the mode; the flagged rows are that source's rows equal to the mode.

H5a (injection) commitments:
- Bases: lineage-cleaned DES_RHO, DES_ETA (`subset(ds, ~copy_mask(ds))`), and ES1 (no copies). 5 % of rows (round(0.05·n)),
  seeds 0–9, one error type per run. Candidate rows are only rows where the injection changes the value
  (e.g. DEFAULT never hits a row already at the default; ES1 TEMP only hits rows with a reported temperature).
- UNIT: density ×1000; viscosity ×0.001 (y = log10 → −3); ES1 diameter ×0.001 (log10 → −3).
- TEMP: DES T (K) → T − 273.15 (in df and in the X column `T`; DES key recomputed from the new T).
  **ES1 has no K column (PREREG gap).** Primary (graded) ES1 TEMP = a Fahrenheit value written into the °C column
  (°C·9/5+32), as suggested by the orchestrator: a realistic unit confusion that R1 is *not* designed to catch, so this is the
  harder, non-circular choice. Exploratory variant ES1 TEMP_K = K value written into the °C column (+273.15).
  Logged as a protocol deviation; the H5a overall verdict is also reported with ES1-TEMP treated as not applicable.
- COPY: round(0.05·n) rows duplicated, each assigned to a random *other existing* source (rows appended).
- DEFAULT: DES T = 298.15 K; ES1 rh = 45 % (and rh_missing = 0, i.e. a missing value "filled" with the default).
- Detection metrics: per type, the *designated* rules are UNIT → R1∪R2, TEMP → R1∪R2, COPY → R3, DEFAULT → R4.
  recall = injected rows flagged by the designated rules / injected rows; precision = injected flagged / all rows flagged by the
  designated rules (non-injected flagged rows count as false positives even if they are genuine errors of the base).
  Graded: UNIT·TEMP recall ≥ 0.8 and precision ≥ 0.8 (seed mean), COPY recall ≥ 0.9. Also reported, not graded:
  any-rule (R1∪R2∪R3∪R4) recall/precision, and per-rule recall.
- Model harm: fixed source→fold map (group_folds seed 0 on the clean base, 10 folds), RF seed 0 for every arm (isolates the
  injection effect). RMSE pooled over the *clean* (non-injected) rows of held-out sources for: orig (clean base training),
  inj (injected training), filt (injected training minus rows flagged by ANY rule = the full audit; primary),
  filt_R12 (minus R1∪R2 flags only; sensitivity). Recovery = (mean RMSE_inj − mean RMSE_filt)/(mean RMSE_inj − mean RMSE_orig),
  means over seeds. If the harm (inj − orig) is not measurable (seed mean ≤ 0 or 95 % seed-bootstrap CI lower ≤ 0), the
  recovery cell is INCONCLUSIVE ("no harm to recover"). No leak removal in H5a (base is lineage-clean; copies are the treatment).
- Overall H5a: any graded cell FAIL → FAIL; else any INCONCLUSIVE → PARTIAL; else PASS.

H5b commitments: raw datasets (7). Audit once per dataset. Source GroupKFold(10), seeds 0–4 (fold seed = RF seed), leak rows
of held-out sources removed from training in both arms (common protocol). Arms: train-all vs train-unflagged (any rule).
Evaluation on unflagged rows only. Per source: seed-mean RMSE per arm → rel = RMSE_unflagged/RMSE_all − 1; dataset value =
mean over sources, 95 % source-bootstrap CI. Dataset "improves" if CI upper < 0. PASS if ≥ 2 datasets improve.

H7 commitments:
- H7a: load_es1_failure("PVDF"), X = ES1_FEATS. Leave-one-failure-paper-out over the 10 failure papers. One-class models
  trained on stable rows of the other papers: IsolationForest(300, seed), OneClassSVM(rbf, nu=0.1, StandardScaler),
  kNN distance (mean distance to 5 nearest stable training rows, StandardScaler). Supervised on all other-paper rows:
  RandomForestClassifier(300, class_weight balanced, seed) (as survivor.py), HistGradientBoostingClassifier(max_iter 300,
  lr 0.05, min_samples_leaf 10, class_weight balanced). Seeds 0–4. AUC pooled over the test rows of the 10 papers, averaged
  over seeds. Best = highest seed-mean AUC within each class; also all 6 pairings. CI: 2,000 paper-bootstrap resamples
  (resample failure papers, pool their rows, seed-mean AUC per model, difference).
- H7b: DES_MP, failure = melting T > 298.15 K. Success-only reference = unique materials (A, B, xA rounded 3) of raw DES_RHO
  ∪ DES_ETA, descriptor features without T. Supervised RF / HistGB on DES_MP labels, source GroupKFold(10), seeds 0–4.
  AUC pooled over all DES_MP rows (each predicted with its source held out). CI: 2,000 source-bootstrap resamples.
  Learning curve: RF, fold seed 0, keep n ∈ {5,10,20,50,100,all} failure rows per training fold (all successes kept),
  10 draws. Exploratory sensitivities (not graded): reference restricted to materials measured at T ≤ 298.15 K;
  reference excluding materials present in DES_MP; one-class trained on DES_MP's own successes in the training folds.
- Verdict per case: (best supervised − best one-class) AUC ≥ 0.10 and CI lower > 0. H7 PASS needs both cases;
  one case → PARTIAL; none → FAIL.

## 12:02 — Rules file written (before any injection)

- `scripts/vrr_audit.py` written at **2026-10-07 12:02:13 UTC**, sha256 `5d77a8d6706ec7d97d9db584b53dee4030fc55c49aefd9c34febc2b3fb3a0ba3`.
  No injection had been generated or run at this point. Any later edit to this file is logged below with the reason
  (bug fixes only; thresholds are PREREG-fixed).

## 12:03–12:06 — h5_audit.py written; injection sanity check; clean-base audits

- Sanity check of `inject()` (seed 0): every in-place type changes exactly round(0.05·n) rows (ES1 39, DES_RHO 248,
  DES_ETA 277); DES TEMP/DEFAULT keys are recomputed; df['y'] stays consistent with ds.y. Example: ES1 UNIT 100 nm → 0.1 nm.
  Side observation: the first DES_ETA injected row has viscosity 0.1 cP *in the clean base* (below R1's 0.2 cP bound).
- Clean-base audit (no injection) — these background flags become false positives in H5a precision:
  - ES1: R1 0, R2a 7, R2b 0, R3 0, **R4 492 / 777 rows (63 %)**, any 496. R4 on ES1 ambient conditions (rh, temperature_c)
    flags most of the dataset: most papers report the modal room temperature / humidity for > 40 % of their rows.
  - DES_RHO_lineage: R1 0, R2a 15, **R2b 541 / 4,962**, R3 0, R4 64, any 604. The out-of-source residuals are heavy-tailed
    (most rows predicted very well, so the MAD-based scale is small) → R2b flags ~11 % of clean rows.
  - DES_ETA_lineage: R1 28 (viscosity < 0.2 cP present in the clean base), R2a 6, R2b 231, R3 0, R4 172, any 403.
  - First surprise / likely failure mode, written down before any injection result: with 541 background R2 flags on
    DES_RHO against 248 injected rows, UNIT/TEMP precision on DES_RHO cannot exceed ~0.31 even with perfect recall.
    The rules are NOT changed (PREREG-fixed; R2b scale definition was fixed at 12:02).
- Clean-base RF RMSE (source GroupKFold 10, seed 0): ES1 0.3247, DES_RHO 0.05097, DES_ETA 0.6235. Timing 10 s / 27 s / 28 s.

## 12:06–12:17 — ES1 injections running (≈18 s per seed: audit CV + 3 CV arms)

- First bash call chained all ES1 types in one foreground command and hit the 9-min tool timeout; it was moved to the
  background automatically and kept writing per-seed parts (resumable), so nothing was lost. Lesson: launch DES runs
  (≈50 s per seed) explicitly in the background, one (dataset, type) per command.
- Interim observations (per-seed console lines, not yet aggregated):
  - ES1 UNIT: recall 1.000 in every seed (R1 diameter < 10 nm catches ×0.001), precision 0.91–0.95 (the 7 R2a background
    flags are the false positives). RMSE on clean rows: orig ≈ 0.326, inj ≈ 0.39–0.41, filtered with the full audit ≈ 0.35
    (R4 removes ~490 training rows), filtered with R1|R2 only ≈ 0.33.
  - **ES1 TEMP (°F written as °C): recall 0.000 in every seed.** 77–122 "°C" is still inside 150–500 K, and temperature
    barely affects the RF, so R2b does not see it either. Harm is also ~0 (inj ≈ orig), so the recovery cell will be
    INCONCLUSIVE. This is the non-circular case and the rules simply cannot see it — a genuine limitation.
  - ES1 COPY: recall 1.000, precision 0.25–0.29 (both pair members + ES1's within-paper duplicate rows are flagged).
    Copies make the evaluation *look better* (RMSE 0.29–0.30 < 0.325 orig): the harm of copies is optimism, not error.

## 12:17–12:32 — Runners, a performance bug, and smoke tests (disclosed: they showed real numbers)

- 12:17 launched a background runner for the 8 DES (dataset × type) H5a jobs (≈ 54 s per seed, ≈ 9.5 min per job), and a
  second runner that waits for it and then runs H7a, H7b, H5b (7 datasets) and the H7b learning curve, so that my CPU use
  stays at 2 cores (another agent is running H9 on the other 2).
- **Bug / dead end (performance):** the first H7a smoke test (1 seed) was killed after 500 s. Profiling one fold:
  IF 0.34 s, OCSVM 0.00 s, kNN 0.17 s, RF 0.38 s, **HistGB 165.9 s** on 300 rows. Cause: HistGradientBoosting uses OpenMP
  with all cores; with the machine already oversubscribed the OpenMP threads thrash (load average went to 7.5).
  Fix: `OMP_NUM_THREADS=1` → HistGB 0.31 s. Runner 2 now exports `OMP_NUM_THREADS=2 VRR_NJOBS=2`. No result was affected
  (the killed run wrote nothing). H5 only uses RF (joblib), so the H5a runs were not affected.
- Smoke tests (written to the scratchpad, not to results/): H7a 1 seed (10 s), H7b 1 seed (25 s), H7 summarize with 200 boots.
  **These showed real seed-0 numbers, which I disclose here:** H7a RF AUC 0.758 vs best one-class (IF) 0.396 → diff 0.362,
  paper-bootstrap CI [0.02, 0.70]; all three one-class AUCs are *below 0.5* (0.21–0.40): with these features the reported
  failures look *less* unusual than the stable rows of the same papers. H7b HGB 0.851 / RF 0.850 vs best one-class kNN 0.746
  → diff 0.104, CI [0.027, 0.196] — **right at the 0.10 threshold**, so the 5-seed result may land on either side.
  Nothing was changed after seeing these (rules, models, thresholds are as committed at 12:02).
- H7b meta: reference set = 1,289 unique RHO/ETA materials (1,023 measured at ≤ 298.15 K; 1,051 not in DES_MP);
  238 reference materials also occur in DES_MP; 356 DES_MP rows (77 of them failures) have their material in the reference —
  i.e. the "success DB" does contain materials that are solid at room temperature (measured hot).
- H5b smoke on DYE (1 seed): only 4 rows flagged (R3), pooled RMSE all 30.153 vs unflagged 30.180. H5 summarize smoke on the
  partial H5a parts revealed two presentation problems, fixed at 12:31 (summarize only, no effect on computed numbers):
  (1) the any-rule recall/precision were packed into one ledger row (precision in the ci_lo column) → split into two rows
  with seed CIs; (2) when harm is not measurable the bootstrap of the recovery ratio produced absurd CIs (e.g. −2,323)
  from draws with a near-zero denominator → CI now left blank in that case (the value and RMSEs are still reported).
- Partial H5a facts seen in the smoke summary (complete for ES1 and DES_RHO UNIT):
  ES1 UNIT recall 1.00 / precision 0.919 / recovery 0.713 (full-audit filter; 0.983 with R1|R2 filter);
  ES1 TEMP(°F) recall 0.008 / precision 0.043 / harm not measurable; ES1 TEMP_K (exploratory) recall 1.00 / precision 0.854;
  ES1 DEFAULT recall 0.244 / precision 0.019; DES_RHO UNIT recall 1.00 / **precision 0.515 (FAIL)** / recovery ≈ 1.0.
  → H5a will be FAIL whatever happens in the remaining cells (DES_RHO UNIT precision and ES1 TEMP already fail).

## 12:21–13:27 — H5a DES injections (8 jobs, 10 seeds each, 43–54 s per seed)

Per-job seed means (from `results/raw/h5_parts/inj_*.csv`, aggregated at 13:28; RMSE = clean rows, source GroupKFold 10):

| dataset | type | recall | precision | RMSE orig / inj / filt(any) / filt(R1∣R2) | remark |
|---|---|---|---|---|---|
| DES_RHO_lineage | UNIT | 1.000 | 0.515 | 0.0510 / 101.5 / 0.0520 / 0.0518 | huge harm, fully recovered; precision fails on R2b background |
| DES_RHO_lineage | TEMP | 1.000 | 0.332 | inj ≈ orig | **K→°C in 5 % of rows does not harm the RF at all** (low-T rows form their own branch) |
| DES_RHO_lineage | COPY | 1.000 | 0.496 | 0.0510 / ~0.042 / ~0.055 / ~0.045 | copies make the CV look 13–21 % better |
| DES_RHO_lineage | DEFAULT | 0.026 | 0.071 | inj ≈ orig | as PREREG predicted: R4 cannot see scattered defaults |
| DES_ETA_lineage | UNIT | 0.971 | 0.687 | 0.623 / ~0.64 / ~0.61 / ~0.60 | recovery > 1: the filter also removes clean-base anomalies |
| DES_ETA_lineage | TEMP | 1.000 | 0.585 | inj ≈ orig | no measurable harm again |
| DES_ETA_lineage | COPY | 1.000 | 0.493 | 0.623 / ~0.50 / ~0.62 / ~0.48 | **5 % copies make the CV RMSE look ~20 % better**; full audit removes the optimism, R1∣R2 does not |
| DES_ETA_lineage | DEFAULT | 0.004 | 0.007 | inj ≈ orig | |

- Surprise 1: the TEMP error (the one R1 catches perfectly) is the one that does no damage to an RF; the error that does the
  most damage to the *evaluation* (COPY) is invisible to accuracy and only shows up as optimism.
- Surprise 2: filtering always removes many clean rows too (R2b and R4 background; e.g. ~550–1,000 rows per DES run),
  so when there is no harm, filtering makes RMSE slightly worse (e.g. DES_RHO TEMP 0.0502 → 0.0524).
- Precision fails on both DES sets for UNIT and TEMP: the PREREG R2b (|z| > 5 on out-of-source residuals) has a heavy
  background rate on real DES data. Not tuned.

## 13:27–13:31 — H7a and H7b full runs (5 seeds); first H7 summary at 13:33 (learning curve still running)

- **The H7a verdict flipped relative to the 1-seed smoke test.** Smoke: RF − IF = 0.362, CI [0.02, 0.70] (would PASS).
  Full 5 seeds: RF AUC 0.734 (seed range 0.707–0.758), IF 0.392 (0.385–0.402) → diff **0.342, paper-bootstrap CI
  [−0.040, 0.692] → FAIL** (CI lower ≤ 0). With only 10 failure papers the CI is extremely wide; the point estimate is large.
  Pairings: RF−KNN5 and HGB−KNN5 would meet the rule, RF−IF, RF−OCSVM, HGB−IF, HGB−OCSVM would not.
- All one-class AUCs in H7a are below 0.5 (IF 0.392, OCSVM 0.376, kNN 0.214; within-paper means 0.18–0.33): the failed
  PVDF runs sit in the *dense* part of the stable-run condition space. A success-only anomaly detector ranks them as the
  *most normal* rows. (Flipping the sign would be a post-hoc choice and is not used for any verdict.)
- H7b: HGB 0.854 / RF 0.853 vs one-class kNN 0.746 / IF 0.646 / OCSVM 0.587 → best diff **0.107, source-bootstrap CI
  [0.031, 0.195] → PASS**, by a margin of 0.007 above the 0.10 threshold — fragile. All six pairings meet the rule.
  Exploratory: reference restricted to RT-measured materials → diff 0.120; reference without DES_MP materials → 0.156;
  one-class on DES_MP's own successes (same folds) → 0.213. So the borderline H7b pass is, if anything, conservative:
  the overlap between the success DB and the DES_MP test materials *helps* the one-class side.
- H7 overall (rule fixed before running): **PARTIAL** (H7a FAIL, H7b PASS).

## 13:31–13:37 — H5b (raw data, 5 seeds) console lines
- ES1: unflagged training is *worse* on unflagged rows (e.g. seed 3: 0.304 → 0.337); R4 removes most of ES1.
- ES2: no rows flagged at all → both arms identical (RMSE 0.556 = 0.556).
- DYE, IL_CELL: small changes of either sign. DES_MP: ~1 % better (38.67 → 38.32). DES_RHO: worse (0.0225 → 0.0266):
  raw DES_RHO has 1,975 copy rows; R3 flags both sides, so the unflagged training set loses the originals too.
- DES_ETA: worse (e.g. seed 3: 0.406 → 0.441).

## 13:39–13:47 — H7b learning curve (RF, fold seed 0, 10 draws per n; ≈ 70 s per n)
- Mean pooled AUC by failure labels kept per training fold (successes ≈ 716 per fold always kept):
  n=5 0.682 (0/10 draws beat the best success-only model, kNN 0.746) · n=10 0.727 (2/10) · n=20 0.769 (8/10) ·
  n=50 0.801 (10/10) · n=100 0.823 (10/10) · all (≈ 2,335) 0.853 (10/10).
  → about 20 labelled failures per training fold are enough to beat a 1,289-material success-only database. Descriptive.

## 13:42–13:50 — Final summaries, checks, housekeeping
- `h5_audit.py summarize` (13:42, re-run 13:48 after a cosmetic fix: NaN cells written as empty instead of "nan";
  numbers unchanged). `h7_failure.py summarize` final at 13:47.
- Checks: `fast_auc` vs sklearn `roc_auc_score` on all 125 (case, model, seed) groups: max |diff| 2.2e-16.
  Recall column vs tp/n_injected: max |diff| 1.1e-16. All 13 (dataset, type) injection cells have 10 seeds.
  `vrr_audit.py` sha256 unchanged since 12:02 (`5d77a8d6…`), i.e. the rules were never edited after writing.
- Housekeeping: the H7 score parts (17 MB) were duplicated in `results/raw/h7_parts/`; they are now gzipped
  (`scores_a.csv.gz`, `scores_b.csv.gz`) and summarize reads the .gz files. Re-running summarize afterwards produced a
  byte-identical ledger and summary (diff empty). `results/raw/h7_scores.csv` (17 MB, every row score) is kept as specified.

## Final verdicts (as written in the ledgers)

H5 (ledger/h5.csv) — **H5a FAIL, H5b FAIL, H5 module FAIL** (H5b FAIL had been predicted in PREREG; H5a FAIL had not).
- H5a graded cells: 12 PASS, 6 FAIL, 3 INCONCLUSIVE of 21.
  - PASS: UNIT recall (RHO 1.000, ETA 0.971, ES1 1.000); TEMP recall (RHO 1.000, ETA 1.000); COPY recall (1.000 ×3);
    UNIT recovery (RHO 1.000, ETA 1.223, ES1 0.713); UNIT precision ES1 0.919.
  - FAIL: UNIT precision RHO 0.515 / ETA 0.687; TEMP precision RHO 0.332 / ETA 0.585; ES1 TEMP(°F) recall 0.008 and
    precision 0.043.
  - INCONCLUSIVE: TEMP recovery on all 3 datasets — the TEMP error did not measurably harm the model (harm CI includes 0).
  - Even with ES1 TEMP treated as not applicable (sensitivity), H5a is FAIL (4 precision cells).
- H5b: 0 of 7 datasets improve; the only negative mean is DES_MP −2.1 % (CI −5.4 % … +1.4 %). Filtering made things
  worse on DES_RHO (+51 %, CI +31 … +75 %, because R3 flags 3,923 rows = both sides of every copy) and was a no-op on ES2
  (0 flags).

H7 (ledger/h7.csv) — **H7 PARTIAL**: H7a FAIL (diff 0.342, CI −0.040 … 0.692), H7b PASS (diff 0.107, CI 0.031 … 0.195).

## What this means (my reading, for the report writers)
- The audit rules work as *detectors of gross, rule-shaped errors* (unit slips, K/°C confusion, copies): recall ≈ 1.
  They do not work as *filters*: on real DES data R2b and R4 flag hundreds to thousands of legitimate rows, so precision
  is 0.33–0.69 and dropping flagged rows never improved held-out accuracy (H5b 0/7). The honest position is the PREREG's
  own fallback: the audit is a **trust label / warning layer**, not a cleaning step.
- The most damaging error class in this study is **copies** (5 % copies make DES_ETA CV RMSE look ~20 % better), and the
  audit's value there is in *removing optimism*, which accuracy-based tests (H5a recovery, H5b) cannot reward.
- A realistic unit confusion (°F written as °C) is invisible to all four rules. R1 only catches what violates physics.
- Failure data: in DES, a few dozen failure labels beat a large success-only DB (H7b PASS, but by 0.007 over the bar);
  in PVDF electrospinning the direction is the same and large (+0.34 AUC) but 10 failure papers are too few for a
  confident claim (CI crosses 0). One-class models there are *worse than random* (AUC 0.21–0.39): failures are not outliers.
