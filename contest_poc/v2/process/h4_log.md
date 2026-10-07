# H4 process log — Anchor (reference-point) join protocol

Chronological, honest notes. Times are local container time (date 2026-10-07).

## 09:47 — Setup and profiling (no H4 modelling results seen yet)

- Read PREREG.md §2 H4, vrr_common.py, vrr_data.py, v1 `scripts/poc_anchor.py`.
- Dataset profile (rows / sources / sources with >=8 rows):
  - ES1 777 / 54 / 33; ES2 267 / 28 / 10; DYE 131 / 12 / 4 (descriptive only, as preregistered);
  - DES_RHO 6937 / 132 / 101 (largest source 2667 rows); DES_ETA 5789 / 114 / 79; DES_MP 3390 / 115 / 71; IL_CELL 674 / 33 / 19.
  - All 6 graded datasets meet the eligibility rule (>=8 sources with >=8 rows). ES2 is the tightest (10 sources).
- Timing (n_jobs=2): RF300 on full DES_RHO 1.6 s, RF150 0.8 s; leak masks for all sources < 1 s.
  DES_RHO has 3982 leak rows in total (copies are common in DES compilations), ES1 has 0.

## 09:50 — Interpretations fixed BEFORE running (pre-results commitments)

These are the places where PREREG leaves room for choice. I fix them now, before any H4 number exists.

1. **Base model**: RF (vrr_common.make_model('RF', seed=0), 300 trees), trained on all rows not in source s and not in
   `leak_mask_for_source(ds, s)` (copies of s held by other sources). One fit per eligible source (leave-one-source-out).
2. **Anchor draws**: k in {1,2,3,5}, 30 draws each; rng = default_rng([crc32(dataset), crc32(source), k, draw]).
   k = 0 has no randomness, so it is evaluated once (1 "draw"); its change is 0 by definition for every method.
   Anchor rows are removed from the evaluation rows; RMSE_0 is recomputed on exactly the same evaluation rows (paired).
3. **Per-source metric**: rel_change(draw) = RMSE_k / RMSE_0 − 1 on the draw's evaluation rows; draw_mean_rel_change =
   mean over draws. Dataset metric = mean over sources; 95% CI = vrr_common.boot_ci over sources (2000 resamples, seed 0).
4. **OFF**: prediction + mean(anchor residuals).
5. **SHR**: prediction + w_k · mean(anchor residuals), w_k = kτ²/(kτ²+σ²). Estimator (training sources only):
   - residuals = GroupKFold(10, seed 0) out-of-source RF residuals over the whole dataset, with leak removal per fold
     (rows of other sources that duplicate a test-fold row's key+value are dropped from that fold's training). Same
     residual definition as H3a.
   - for source s: drop rows of s and rows in leak_mask_for_source(s); per remaining source j: mean m_j, n_j.
   - σ² = pooled within-source variance Σ(n_j−1)v_j / Σ(n_j−1) over sources with n_j >= 2.
   - τ² = max(0, Var_j(m_j, ddof=1) − σ²·mean_j(1/n_j)) (unweighted method of moments, all sources with n_j >= 1).
   - Caveat (logged): those GroupKFold residuals of other sources come from models that may have included s in training.
     s therefore influences two scalars (τ², σ²) very weakly; s's own residuals never enter. Accepted as allowed by the task.
6. **FAKE (graded control)**: offset = mean of k out-of-source (GroupKFold) residuals drawn from ONE other random source s'
   (s' drawn uniformly among sources ≠ s with >= k rows and with no rows in leak_mask_for_source(s)); applied unshrunk
   (same as OFF). Reason for using out-of-source residuals: the base model for s was trained on s', so in-sample residuals
   of s' would be ~0 and the control would be trivially passed.
   **FAKE_SHR (EXPLORATORY, not graded)**: the same fake offset with the SHR weight w_k (a stricter control, because
   shrinkage reduces the noise penalty that makes an unshrunk fake offset look bad).
7. **RET**: retrain with the k anchors added to the training set (sample_weight 5 for anchors, 1 otherwise), first 5 of the
   30 draws, RF with 150 trees (seed 0). Its RMSE_0 reference is an identically configured RF150 base (seed 0) without anchors,
   so the only difference is the anchors. RET runs on all eligible sources for datasets with <= 1000 rows (ES1, ES2, IL_CELL,
   DYE) and on a 30-source random subset (default_rng(20261007), drawn from the sorted eligible-source list) for DES_RHO,
   DES_ETA, DES_MP. RET is not part of the pass rule (rule uses OFF or SHR), so its rows are DESCRIPTIVE.
8. **Dataset pass rule** (PREREG H4): PASS iff there is a method m in {OFF, SHR} with mean change at k=3 <= −10% AND that
   same method's CI upper bound < 0, AND FAKE k=3 mean change >= −2%. Otherwise FAIL. INCONCLUSIVE only if the dataset is
   ineligible or incomplete.
9. **Overall H4**: PASS if >= 4 of 6 datasets PASS, otherwise FAIL (PREREG gives no PARTIAL band for H4, so I do not invent one).
10. **Secondary prediction**: per dataset, SHR k=1 mean change <= 0 → holds; overall PASS if it holds in >= 4 of 6.
11. **Gap closure** (reported, not graded): (RMSE_0 − RMSE_k) / (RMSE_0 − RMSE_randomCV).
    - primary = pooled-row version: RMSE over all evaluation rows of eligible sources (draw-averaged SSE), random-CV RMSE =
      random 5-fold RF (5 seeds, mean of per-seed RMSE) evaluated on the same eligible-source rows (raw data, no lineage cleaning).
    - secondary = source-mean version (mean per-source RMSE). Undefined (NaN) if the denominator <= 0.
12. **Fraction improved**: share of sources with draw_mean_rel_change < 0.

## 09:55 — Script written: `scripts/h4_anchor.py`

- Two modes: `run DATASET --budget SEC` (resumable; one part file per source under `results/raw/h4_parts/DATASET/`,
  written atomically, so an interrupted run resumes cleanly) and `aggregate` (all raw CSVs, curves, summary, ledger).
- First draft bug fixed before any run: part-file paths were derived with `str.replace("src_", "rows_")` on the
  full path (fragile); replaced by an explicit `part_path()` helper plus a crc32-collision assert on source names.
  The JSON writer also needed a numpy-bool-aware default (np.bool_ would otherwise have been serialised as 0.0/1.0).

## 09:58 — Smoke test on ES2 (76 s) and DYE (39 s); first H4 numbers seen

- ES2: OFF k3 −34.4% [−56.1, −14.7], SHR k3 −34.8% [−55.0, −16.3], FAKE k3 +83.0% → rule met (PASS for ES2).
  τ² ≈ 0.14 vs σ² ≈ 0.057 (log10 units²) → between-source variance dominates; SHR k=1 weight ≈ 0.72.
- DYE (descriptive): OFF k3 −22.4% but CI upper +7.7% (only 4 sources), so the rule would not be met even if graded.
- Observation: the unshrunk FAKE offset strongly *hurts* (+83% ES2, +24% DYE). The FAKE control is therefore easy to
  pass when between-source offsets are large; the stricter EXPLORATORY FAKE_SHR also hurts (+70% ES2, +14% DYE).
  This is reported as a caveat on how informative the preregistered control is, not used to change the rule.
- Per-source cost ≈ 6 s for small datasets (dominated by RET: 1 + 20 RF150 fits per source).

## 10:05–10:45 — Full runs (dataset by dataset, resumable)

| dataset | sources | passes | wall time | note |
|---|---|---|---|---|
| ES2 | 10 | 1 | 76 s | smoke test |
| DYE | 4 | 1 | 39 s | descriptive |
| ES1 | 33 | 1 | 215 s | |
| IL_CELL | 19 | 1 | 129 s | |
| DES_MP | 71 (RET 30) | 1 | 468 s | finished just inside the 470 s budget |
| DES_ETA | 79 (RET 30) | 2 | 450 + 198 s | budget stop at 47/79, resumed cleanly |
| DES_RHO | 101 (RET 30) | 2 | 450 + 264 s | budget stop at 55/101, resumed cleanly |

- No crashes. Source names in IL_CELL contain mojibake (`â€“`) inherited from the loader's `encoding_errors="ignore"`;
  harmless for H4 (names are only identifiers), flagged for the loader owner.
- No draw had RMSE_0 = 0 (so no ratio was undefined).
- RET cost: ~6 s/source on small sets, ~13 s (DES_MP), ~18 s (DES_ETA), ~19 s (DES_RHO). Doing RET on all DES sources
  would have needed ~45 extra minutes; the preregistered 30-source subset was used (no deviation).

## 10:46 — Aggregate: H4 graded result

- ES1 PASS, ES2 PASS, DES_ETA PASS, DES_MP PASS, IL_CELL PASS, **DES_RHO FAIL** → H4 overall PASS (5/6).
- Secondary (SHR k=1 <= 0): holds in 5/6 (fails in DES_RHO: +0.7%) → PASS.
- **DES_RHO failure details**: OFF k3 **+8.7%** [+2.3, +14.5] (anchors make density predictions *worse*), SHR k3 −0.4%
  [−4.5, +3.2] (does nothing), only 22% (OFF) / 35% (SHR) of sources improve. RET (descriptive, 30-source subset) does help:
  −11.9% [−20.3, −4.9].
- **Weak passes / caveats seen in the numbers**:
  - IL_CELL passes on the mean (OFF −18.3%, SHR −18.4%) but the OFF median is only −1.3% and only 53% of sources improve
    with OFF (84% with SHR); pooled gap closure is small (OFF 9%, SHR 19%). A few sources with big offsets drive the mean.
  - DES_ETA / DES_MP: means −15 to −17% at k=3, medians −9 to −14%; ~60–66% of sources improve.
  - k=1 OFF is useless or harmful outside ES1/ES2 (DES_RHO +24%, DES_ETA +0.8%, DES_MP +0.8%, IL_CELL −1.9%);
    shrinkage (SHR) is what makes k=1 safe. This supports the SHR design choice.
- **FAKE control is weak as a discriminator**: unshrunk fake offsets hurt a lot everywhere (+64% … +116% at k=3), so the
  "FAKE >= −2%" criterion was never close to binding. It does show the gain is not a generic bias correction, but it is a
  low bar. EXPLORATORY FAKE_SHR also hurts everywhere (+44% … +88%).

## 10:50 — EXPLORATORY diagnostics (post hoc, defined after seeing the DES_RHO FAIL; not graded)

(a) Offset signal-to-noise per source: |LOPO mean residual| / within-source residual SD.
    Median: ES1 1.13, ES2 1.47, DES_ETA 0.76, DES_MP 0.82, IL_CELL 0.81, DYE 0.85, **DES_RHO 0.35**.
    LOPO between-source share of residual variance: DES_RHO 0.28 vs 0.44–0.83 for the others.
    Median within-source residual excess kurtosis: DES_RHO +1.76 (heavy tails) vs −0.5 … 0 for the others.
    Within each dataset the Spearman correlation between source SNR and OFF k3 change is −0.72 … −0.99; this is largely
    mechanical (RMSE_0² ≈ bias² + SD²), so it explains *where* anchors help but is not independent evidence.
(b) Material-disjoint anchors (defined here BEFORE computing it): same draws as the main run (same rng seeds), but
    every evaluation row whose material equals the material of any anchor row is removed from the evaluation; RMSE_0 is
    recomputed on the same remaining rows. Draws with no remaining evaluation rows are skipped; sources with a single
    material are ineligible. Methods OFF and SHR, k in {1,2,3,5}. Purpose: tests whether the anchor offset is a property of
    the *source* (transfers to the source's other materials) rather than a material-specific model error. Uses cached
    LOPO residuals (h4_base_rows.csv); no refitting. 'material' = loader's material id (DES: A|B|x_A; ES1: polymer|solvent;
    ES2: PVDF|solvent|ratio; IL_CELL: cation.anion|cellulose; DYE: dye).

## 10:58 — EXPLORATORY results (material-disjoint anchors, k=3; not graded)

| dataset | multi-material sources | OFF k3 | SHR k3 [95% CI] | main run, same sources (SHR) |
|---|---|---|---|---|
| ES1 | 6 of 33 (27 single-material) | +7.3% | +1.6% [−33.6, +36.6] | −8.9% |
| ES2 | 2 of 10 | −55.2% | −56.3% (n=2, not interpretable) | −35.0% |
| DES_RHO | 100 of 101 | +25.2% | **+8.3% [+2.9, +13.7]** | +0.1% |
| DES_ETA | 77 of 79 | −0.5% | −5.4% [−13.1, +3.5] | −17.0% |
| DES_MP | 71 of 71 | −9.0% | **−13.0% [−20.3, −5.1]** | −17.1% |
| IL_CELL | 19 of 19 | −18.1% | **−18.3% [−28.8, −9.0]** | −18.4% |

Reading (honest):
- In IL_CELL the anchor offset transfers to the source's *other* materials (cation.anion|cellulose) with no loss:
  this is the cleanest evidence that a source offset is a lab/paper property.
- DES_MP keeps most of its gain (material = exact composition A|B|x_A, so "other material" can still be the same
  component pair at another ratio; the check is weaker there).
- DES_ETA's gain (−17%) mostly disappears (−5%, CI includes 0) when same-composition rows are removed: most of the
  DES_ETA anchor gain is composition-specific correction (anchors = same DES at other temperatures), not a portable
  source offset.
- ES1 cannot be tested this way: 27/33 papers report a single polymer–solvent system, so in ES1 "source offset" and
  "material-system offset" are confounded by design of the data.
- DES_RHO: anchors from other compositions make density predictions worse.
- Implication for the concept: the preregistered H4 (random anchors) supports "calibrate a new source with k of its
  own measurements"; it does **not** by itself establish "calibrate with a *different* reference material", which is
  what a physical reference-sample (round-robin) protocol needs. Evidence for that stronger claim is IL_CELL (yes),
  DES_MP (partly), DES_ETA (no), DES_RHO (no), ES1/ES2 (not testable). H3b (physical reference DES) is the
  preregistered test of that stronger claim.

## 11:00 — Verification and wrap-up

- Independent recomputation of 648 draw-level OFF/SHR values from cached LOPO residuals and the same rng seeds:
  max |diff| 3.9e-6 (CSV rounding). k=0 change exactly 0 everywhere; FAKE never drew the held-out source;
  30 draws per (source, k>0) for OFF/SHR/FAKE and 5 for RET, as specified.
- Final verdicts: H4_join ES1 PASS, ES2 PASS, DES_RHO FAIL, DES_ETA PASS, DES_MP PASS, IL_CELL PASS → **H4 overall PASS
  (5/6)**; secondary SHR k=1 <= 0: PASS in 5/6 (DES_RHO FAIL, +0.7%) → **secondary PASS**. DYE descriptive only
  (rule would not be met: OFF k3 CI upper +7.7%, 4 sources).
- What H4 does NOT show (to keep in the report):
  1. The FAKE control is weak (it hurts by +64% … +116%); passing it is easy.
  2. Means are pulled by sources with large offsets; medians are smaller (IL_CELL OFF median −1.3%).
  3. Random anchors often share a material with the evaluation rows (see material-disjoint table above).
  4. Density (DES_RHO), the property with the smallest between-source disagreement, fails, consistent with anchors only
     paying off when source offsets are large relative to within-source scatter (median |bias|/SD 0.35 vs 0.76–1.47).
     RET (retraining with anchors) still helps on the DES_RHO subset (−11.9% [−20.3, −4.9]), so "offset" is the wrong
     correction model for density, not "anchors are useless".
- Files: scripts/h4_anchor.py; results/h4_summary.json; ledger/h4.csv (80 rows); results/raw/h4_anchor_per_source.csv,
  h4_curves.csv, h4_anchor_draws.csv.gz (every draw), h4_source_meta.csv, h4_base_rows.csv (row-level LOPO/OOF
  residuals), h4_explore_offset_snr.csv, h4_explore_matdisjoint_per_source.csv, h4_explore_matdisjoint_curves.csv.
  results/raw/h4_parts/ (26 MB) is the resumable cache used by `aggregate` (per-source parts + prep.npz with GroupKFold
  OOF residuals and random-CV predictions); it can be deleted and regenerated with `run`.

## Fix round (14:20–15:45) — response to the adversarial verification (process/h4_verify.md)

Rule for this round: the preregistered H4 verdicts and headline numbers (RF seed 0, `h4_anchor.py`) are kept as they
are. PREREG thresholds are unchanged. Everything new is labelled EXPLORATORY (robustness) in `ledger/h4.csv`
(test_id `H4R_*`) and lives in `h4_summary.json["robustness"]`. New script: `scripts/h4_robust.py`.
The new aggregate runs after `h4_anchor.py aggregate`, appends to the ledger and summary, and is idempotent.

### 14:24 Safety net before touching anything
- Backed up h4_summary.json, ledger/h4.csv, h4_anchor.py, this log and the raw tables to the scratchpad. Recorded md5
  sums of the 5 main raw files.
- Counted within-source exact duplicates (identical X rounded to 1e-9 AND identical y, same source) in **every**
  dataset, not only the two the verifier flagged. This avoids choosing the scope after seeing the issue.

| dataset | rows | redundant rows | rows having a twin | sources with dups | eligible -> eligible on unique rows |
|---|---|---|---|---|---|
| ES1 | 777 | 162 (20.8%) | 185 | 8 | 33 -> 28 (3 single-measurement + 2 with 6/55 and 5/44 unique rows) |
| ES2 | 267 | 8 (3.0%) | 13 | 3 | 10 -> 10 |
| DYE | 131 | 0 | 0 | 0 | 4 -> 4 |
| DES_RHO | 6937 | 45 (0.6%) | 90 | 7 | 101 -> 101 |
| DES_ETA | 5789 | 77 (1.3%) | 154 | 2 | 79 -> 79 |
| DES_MP | 3390 | 1209 (35.7%) | 2418 (71.3%) | 43 | 71 -> 64 |
| IL_CELL | 674 | 5 (0.7%) | 10 | 4 | 19 -> 18 |

- Small discrepancy with the verifier, reported rather than smoothed over: the verifier wrote that "64% of rows have a
  twin" in DES_MP. My count is 2,418/3,390 = 71.3% of all rows, or 2,408/3,269 = 73.7% of eligible-source rows. The
  redundant-row count (1,209) agrees exactly. The verifier probably used a different denominator. This does not
  affect any number below.
- The three ES1 single-measurement sources are confirmed from `results/raw/h4r_dup_audit.csv`:
  10.1016/j.jmrt.2023.01.007 (9 rows, 1 unique), 10.1016/j.mtsust.2022.100275 (13/1), 10.1016/j.polymer.2020.123366 (13/1).

### Issue 1 [MAJOR] within-source duplicates inflate ES1 / DES_MP effect sizes — FIXED as robustness, verdicts kept
What I did:
- **R2 twin-disjoint**: the main-run draws (same rng) re-scored with every evaluation row that is an exact (X, y) twin of
  an anchor removed. Covers OFF/SHR/FAKE/FAKE_SHR, k = 1, 2, 3, 5, all 7 datasets, using the full-precision cached LOPO
  residuals.
- **R3 dedup-refit** (new; the verifier only re-scored cached residuals): each dataset is de-duplicated inside each
  source. Then GroupKFold OOF residuals, the LOPO RF, tau²/sigma² and the anchor draws are all recomputed. Eligibility is
  >= 8 unique rows. RET at k = 3 is included (5 draws, RF150).
- **R2c dedup-cached**: the verifier's variant, kept as a cross-check. It reproduces the verifier's numbers exactly.
- **R5 RET twin-disjoint** at k = 3: re-fitted RF150 with the main-run anchors wherever an anchor had a twin. Re-fitted
  sources: ES1 6/33, ES2 2/10, IL_CELL 4/19, DES_MP 17/30, DES_RHO 2/30, DES_ETA 0/30, DYE 0/4. Elsewhere the result
  equals the main run by construction.
- **R7**: ES1 without its 3 single-measurement sources.

Before -> after (k = 3, mean relative RMSE change, source-bootstrap 95% CI):

| dataset | OFF main | OFF twin-disjoint | OFF dedup-refit | SHR main | SHR twin-disjoint | SHR dedup-refit | rule (twin / dedup) |
|---|---|---|---|---|---|---|---|
| ES1 | -30.0 [-42.3,-18.6] | -21.5 [-31.9,-11.4] | -19.1 [-29.7,-8.1] | -29.9 [-39.7,-20.3] | -23.9 [-33.0,-15.0] | -21.5 [-31.0,-11.7] | met / met |
| ES2 | -34.4 [-56.1,-14.7] | -34.4 [-56.1,-14.7] | -32.2 [-53.8,-12.2] | -34.8 [-55.0,-16.3] | -34.8 [-54.9,-16.3] | -33.0 [-53.3,-14.0] | met / met |
| DES_RHO | +8.7 [+2.3,+14.5] | +8.7 [+2.3,+14.5] | +8.7 [+2.7,+14.4] | -0.4 [-4.5,+3.2] | -0.4 [-4.5,+3.2] | +0.1 [-4.0,+3.9] | FAIL / FAIL |
| DES_ETA | -14.9 [-21.5,-8.3] | -14.9 [-21.5,-8.3] | -15.0 [-21.8,-8.4] | -17.1 [-23.1,-10.9] | -17.1 [-23.1,-10.9] | -16.9 [-23.2,-10.8] | met / met |
| DES_MP | -14.5 [-21.3,-8.0] | **-9.0 [-17.8,+0.7]** | -11.8 [-18.5,-5.3] | -17.1 [-23.0,-11.5] | -13.0 [-20.3,-5.1] | -14.8 [-20.7,-9.3] | met **via SHR only** / met |
| IL_CELL | -18.3 [-33.7,-4.9] | -18.6 [-33.8,-5.2] | -17.3 [-33.2,-2.7] | -18.4 [-28.8,-9.3] | -18.7 [-29.0,-9.4] | -18.3 [-29.0,-8.5] | met / met |
| DYE (descr.) | -22.4 [-62.4,+7.7] | -22.4 | -20.7 [-62.5,+11.8] | -19.6 [-45.7,+2.9] | -19.6 | -17.8 [-43.9,+5.4] | not met / not met |

- Dedup-cached (verifier variant): ES1 OFF -19.4 / SHR -22.2; DES_MP OFF -12.8 / SHR -15.7. Identical to the
  verifier's numbers.
- ES1 without the 3 single-measurement sources: OFF -23.0, SHR -25.0. Same as the verifier.
- RET k3 (descriptive), main -> twin-disjoint -> dedup-refit:
  - ES1: -36.3 -> -28.4 -> -29.6
  - DES_MP: -27.7 -> -24.4 -> -25.2
  - DES_RHO: -11.9 -> -11.8 -> -13.3
  - Others change by 2.2 pp or less. DYE dedup-refit moves -25.9 -> -30.9 with only 4 sources.
- Secondary prediction (SHR k1 <= 0): under twin-disjoint, dedup-cached and dedup-refit it still holds in 5/6.
  ES1 SHR k1 changes from -20.2 to -16.1 (twin) and -15.1 (dedup-refit).
- **Overall rule**: met in 5/6 under every duplicate-handling variant, so H4 stays PASS. The ES1 effect should be
  quoted as about -19% to -25%, not -30%. **DES_MP passes via SHR only under twin-disjoint** (OFF CI upper +0.7%); it
  passes via both under dedup-refit.
- New finding while doing this: DES_MP twin-disjoint is **identical** to the earlier EXPLORATORY material-disjoint
  analysis in 69/71 sources (SHR k3 -13.0% vs -13.0%). The reason is that inside a DES_MP source the only rows with the
  same composition are the swapped-order duplicates; (source, material) groups have size 1 (970) or 2 (1,206). The
  earlier log line (10:58) said DES_MP "keeps most of its gain" under material-disjoint (-17.1 -> -13.0). That loss is
  entirely the duplicate effect. On unique rows, DES_MP anchors do transfer to other compositions of the same source,
  which slightly strengthens the "source offset" reading for DES_MP. This is recorded in
  summary["robustness"]["twin_vs_matdisjoint_k3"].
- Regression checks:
  - Rescoring the main draws from cached residuals matches the full-precision part files to 4e-15. It matches the
    draws file to at most 5e-4, which is only the `%.6g` rounding of FAKE ratios up to +158.5 in DES_RHO.
  - RET re-fits reproduce the file to within 5e-7.

### Issue 2 [minor] DES_RHO bootstrap units not independent — DONE (all datasets)
- Cluster bootstrap (`H4R_cluster_*`): eligible sources linked by `vrr_common.copy_relations` are merged into connected
  components.
- DES_RHO: 64 copy-related pairs among 101 eligible sources give **39 clusters**.
  - OFF k3 +8.7%: CI [+2.3, +14.5] -> [+4.2, +22.7]
  - SHR k3 -0.4%: CI [-4.5, +3.2] -> [-3.8, +7.6]
  - SHR k1: CI [-1.9, +3.3] -> [-1.9, +5.4]
  - The FAIL is unchanged.
- Other datasets: ES1 0 pairs (33 clusters), ES2 0, DES_ETA 4 pairs (75 clusters), DES_MP 1 (70), IL_CELL 1 (18), DYE 0.
  Their CIs change by 0.8 pp or less.

### Issue 3 [minor] single RF seed, no HistGB/kNN, logged as "No deviation" — FIXED (logged + protocol completed)
- `h4_summary.json["deviations"]` now reads: DEVIATION 1 = single RF seed for the graded run (PREREG common protocol: 5
  seeds and HistGB/kNN robustness); DEVIATION 2 = RET uses RF150 instead of RF300. The old "No deviation" text was
  wrong and has been replaced.
- Instead of only citing the verifier's re-runs, I ran the missing protocol items with the H4 code: RF seeds 1-4 (new
  model seed, GroupKFold seed and anchor draws per seed), HistGB seed 0 and kNN. Methods were OFF/SHR/FAKE/FAKE_SHR at
  every k. RET was not re-run (descriptive; noted as a scope limit).
- Regression test: config `rf_s0_repro` (RF seed 0 through the new code path) reproduces the main run's sse0/ssek on
  ES2 to < 1e-9 (200/200 cells). It was run on ES2 only.
- Results (rule met / k3 means):
  - RF seeds 0-4: **5/6 datasets in every seed** (DES_RHO fails in 5/5 seeds); secondary 5/6 in every seed. The
    seed-averaged per-source analysis gives 5/6 as well.
  - HistGB: rule met 5/6; secondary **6/6**, because DES_RHO SHR k1 = -0.6% [-2.4, +1.3] with HistGB, essentially 0.
  - kNN: rule met 5/6; secondary 5/6.
  - **OFF is model-sensitive.** With HistGB, IL_CELL OFF is -8.5% [-19.1, +0.5], so it passes only via SHR (-12.3%
    [-19.0, -6.4]). With kNN, ES2 OFF is -20.3% [-42.9, +3.1], so it passes only via SHR (-21.6% [-41.5, -1.2]), close
    to the CI boundary. SHR met the rule in every config for every passing dataset.

### Issue 4 [minor] medians are seed-sensitive — FIXED (reported across seeds)
- RF seeds 0-4, k3 median ranges, SHR (OFF):
  - ES1 -27.2..-25.8 (-25.5..-21.6)
  - ES2 -36.6..-31.7
  - DES_ETA -10.9..-6.3 (-8.7..-5.2)
  - DES_MP -14.8..-10.9
  - IL_CELL -14.0..-7.8 (-8.5..-1.1)
  - DES_RHO +2.6..+4.3
- k3 means move by at most 3.6 pp across seeds (the largest range is DYE, which is descriptive). SHR medians move by
  up to 6.2 pp (IL_CELL).
- In the summary caveats medians are now printed as "median~" and point to `robustness.seed_medians`.
- Process note (an honest slip): my first draft of this caveat contained a hand-typed "means move by <= ~3 pp". The
  computed value is 3.6 pp, so the guess was wrong. The string is now generated from the data. In the same pass I
  replaced the hand-copied "9/13/13" (from the verifier's text) and the "-19 to -25%" range with values computed from
  the audit and rule tables.

### Issue 5 [minor] DES_RHO near-copies (1e-4 < rel.diff <= 1e-2) left in training — checked, verdict unaffected
- 479 DES_RHO held-out rows have such a near copy in their LOPO training set (DES_ETA 50, DES_MP 27, ES1 1, IL_CELL 1,
  ES2 0, DYE 0).
- With them excluded from evaluation (main draws), DES_RHO gives OFF k3 +10.1% [+2.8, +17.7] and SHR +0.5%
  [-4.1, +5.1]. This is still a FAIL; near-copies are not why DES_RHO fails. All other datasets change by 0.4 pp or less.
- Twin + near-copy exclusion combined also gives 5/6.
- Caveat on the lineage rule: rtol 1e-4 misses near-copies. Owners of H6 and the loader may want a looser rule.

### Issue 6 [minor] DES_ETA journal-URL pseudo-source — reported, sensitivity done
- Dropping `http://pubs.acs.org/journal/acscii` (1,461 rows, one bootstrap unit) changes OFF k3 -14.9 -> -15.2 and SHR
  -17.1 -> -17.4, so the effect is negligible. The loader was not changed, because it is frozen at the prereg commit
  and shared by all families. Listed in summary["robustness"]["notes_for_other_owners"].

### Issue 7 [minor] wording "No deviation"; SNR diagnostic includes zero-SD sources — FIXED
- Deviations reworded as described under Issue 3.
- `h4_anchor.py explore_dataset` now excludes sources with within-source residual SD = 0 from the SNR median and
  Spearman, and counts them (`n_zero_sd_sources_excluded_from_snr`).
  - ES1: 3 excluded. Median SNR 1.129 -> 1.096; Spearman(SNR, OFF k3) -0.984 -> -0.978; share of sources with SNR > 1
    0.64 -> 0.60.
  - Other datasets: 0 excluded, unchanged.

### Integrity check after re-running `h4_anchor.py aggregate`
- h4_anchor_per_source.csv, h4_curves.csv, h4_base_rows.csv and h4_source_meta.csv are byte-identical to before (md5).
- h4_anchor_draws.csv.gz has a different md5 only because the gzip header stores a timestamp. Its content is
  regenerated from the same unchanged part files, and the per-source table derived from it is byte-identical.
- All curve numbers in h4_summary.json show 0 numeric differences.
- Ledger: the 80 original rows have the same test_id, dataset, value, CI and verdict. The only exceptions are the ES1
  `H4X_offset_snr` value (the intended SNR fix) and the notes (the robustness suffix on H4_join and the zero-SD note on
  the SNR rows). 283 `H4R_*` EXPLORATORY/DESCRIPTIVE rows were added, for 363 rows in total.

### Timings, deviations of this round, files
- Timings (VRR_NJOBS=2, OMP_NUM_THREADS=2):
  - rescore of all 7 datasets: about 55 s
  - dedup-refit: ES1 64 s, ES2 24 s, IL_CELL 42 s, DYE 12 s, DES_MP 142 s, DES_ETA about 263 s and DES_RHO about
    316 s (each stopped once at the budget and resumed cleanly)
  - RET twin: 90 s
  - one RF seed config: about 8 min (DES_RHO 177 s, DES_ETA 134 s, DES_MP 89 s)
  - HistGB: about 5 min; kNN: 35 s
  - each aggregate: about 75 s
- Scope limits of this round (logged):
  - RET was not re-run for the seed and model configs.
  - RET twin and dedup-refit cover k = 3 only.
  - The `rf_s0_repro` regression covers ES2 only.
  - HistGB was run with seed 0 only; kNN is deterministic.
- Files:
  - Script: `scripts/h4_robust.py`. `scripts/h4_anchor.py` was edited (SNR, deviations, median wording).
  - Raw tables: `results/raw/h4r_dup_audit.csv`, `h4r_per_source.csv`, `h4r_curves.csv`, `h4r_rules.csv`,
    `h4r_cluster_bootstrap.csv`, `h4r_source_meta.csv`, `h4r_rescore_draws.csv.gz`, `h4r_ret_twin_draws.csv`
  - Every draw and every row of each refit config: `h4r_draws_<config>.csv.gz` and `h4r_base_rows_<config>.csv.gz`
  - Small per-dataset metadata: `results/raw/h4r_parts/`
  - Cache: `results/raw/h4_parts_robust/` (172 MB) is a regenerable resume cache and was added to
    `contest_poc/.gitignore`. Everything the figures need is in the `h4r_*` files.
- Notes for other owners (also in the summary):
  - Loader owner: deduplicate swapped-order DES rows (DES_MP) and identical Cogni-e-SpinDB rows (ES1). The DES_ETA
    journal-URL source label is a pooled pseudo-source. IL_CELL source names contain mojibake.
  - H1/H3/H9 owners: within-source duplicates also inflate random-CV optimism (H1), split-half reliability for
    single-measurement sources (H3a) and k=3 anchor intervals (H9) in ES1 and DES_MP. A twin-disjoint or dedup
    sensitivity is advisable there.

### Bottom line after the fix round
- H4 stays **PASS (5/6)** with DES_RHO as the one FAIL. The secondary prediction stays PASS (5/6).
- 5/6 holds under twin-disjoint, dedup-refit, dedup-cached, near-copy exclusion, RF seeds 0-4, seed-averaging, HistGB,
  kNN and the cluster bootstrap. Not one of these variants turns DES_RHO into a pass or any other dataset into a fail.
- What got weaker:
  - ES1's effect is about -19% to -25%, not -30%.
  - DES_MP OFF loses significance under twin-disjoint and passes via SHR only.
  - OFF alone fails the CI criterion for IL_CELL with HistGB and for ES2 with kNN.
- Practical lesson: the shrunken offset (SHR) is the robust method; the unshrunk offset (OFF) is not.
