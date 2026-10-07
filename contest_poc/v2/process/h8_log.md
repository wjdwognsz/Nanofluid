# H8 process log -- link gate with permutation threshold (nested)

Chronological, honest notes. Times are container local time (2026-10-07).

## 09:45 Read-in
- Read PREREG.md (H8 section), vrr_common.py, vrr_data.py, v1 scripts poc_transfer.py / poc_transfer_null.py.
- H8 data (polyVERSE) is not covered by vrr_data.load(); the featurisation/loader is reproduced from v1
  poc_transfer.py (Morgan count FP r=2 1024 bits + 9 RDKit descriptors; ladder tokens [d],[e],[g],[t] -> [*];
  duplicates per canonical SMILES averaged). Shared pieces used from vrr_common: make_model("RF"), random_folds,
  rmse, boot_ci, ledger_write/LEDGER_COLS.
- Exploration (sizes only, no modelling): master_transport has 34 properties; 32 have >=30 polymers after
  canonicalisation (p_exp_H2O=27 and s_exp_H2O=25 do not). Extra sources: X_bandgap_chain 4208, X_atomization_H 390,
  X_ionization_E 370, X_electron_aff 368, X_CED 294. Water uptake / water diffusivity in the solvent sets have 0 water
  rows, chi_parameter has 25 water rows -> v1's X_water_* sources do not exist (same as v1, which also dropped them).
- Timing probe (random data, not real results): source RF(100 trees, mf=0.2) n=750 -> 1.0 s, n=4208 -> 7.9 s;
  target RF (make_model RF, 300 trees) n=25..150 -> 0.3-1.0 s.

## 09:50 Pre-specification (written BEFORE any H8 model was run)

What I had already seen from v1 (disclosure): v1 transfer_summary.json (aggregate: data-driven score AUROC 0.82,
top-1 gain +17.3%, physics prior top-1 +1.9%) and transfer_null.json (H2O targets x 5 sources:
X_bandgap_chain, p_exp_O2, s_exp_CH4, d_exp_H2, s_sim_N2, plus 12 permuted sources). I did NOT open the per-pair
v1 gains (transfer_pairs.csv) before fixing the PHYS mapping below; I only printed its source list and target n/base RMSE.

### Targets (11, as v1)
p_exp_H2O, s_exp_H2O, d_exp_H2O, s_exp_He, s_exp_H2, d_exp_He, d_exp_H2, s_exp_CO2, d_exp_CO2,
p_exp_CO2_sub40, p_exp_N2_sub40. The _sub40 sets are reproduced with the exact v1 code path:
rng = default_rng(0); for t in [p_exp_CO2, p_exp_N2]: series.loc[rng.choice(series.index, 40, replace=False)]
(the selected polymer keys are written to results/raw/h8_sub40_keys.csv).

### Real source pool (same rule as v1: every task with >=30 polymers; minus the target itself and its parent)
- exp transport (physically related): p_exp_{O2,N2,CO2,CH4,H2,He}, s_exp_{CO2,CH4,N2,O2,He,H2},
  d_exp_{CO2,CH4,N2,O2,H2,He,H2O}  (19)
- sim transport (simulated): s_sim_{CH4,O2,CO2,N2,H2O}, d_sim_{CO2,O2,CH4,N2}, p_sim_{O2,CO2,CH4,N2}  (13)
- unrelated DFT: X_bandgap_chain, X_ionization_E, X_electron_aff, X_atomization_H (4)
- other property: X_CED (log10 cohesive energy density, polyBERT set) (1)
=> 37 real sources in total; each target uses 35-36 of them (self / parent removed).

### Permuted (null) sources: 10
Label-permuted copies of 5 bases x 2 seeds (seeds 500..509, fixed across targets and repeats):
p_exp_O2 (exp, large), s_exp_CH4 (exp, mid), d_sim_CO2 (sim), X_CED (other property), X_ionization_E (DFT).
Deviation from v1's null (which used X_bandgap_chain and p_exp_O2): X_bandgap_chain is NOT used as a permutation
base because each bandgap source fit costs ~8 s and would roughly double the runtime; the DFT class is represented
by X_ionization_E. Logged as a protocol choice (decided before any result).

### Score, threshold, policies (PREREG H8)
- Strict new-polymer setting: for repeat r, outer partition F1..F5 (vrr_common.random_folds(n,5,seed=r)).
  g_s(i) for target polymer i in fold Fk = prediction of a source-s RF fitted on source s with all Fk polymers removed.
  So every source prediction for a polymer comes from a model that never saw that polymer.
- Nested score (outer fold f, Tr = all folds except f): score_s = |Pearson r(g_s[Tr], y[Tr])|. Only target labels of Tr
  are used. (The source models never see any target label; the cross-fitting only enforces the new-polymer setting,
  so the outer partition is reused for it: g_s on Tr polymers of fold k comes from the model that excluded Fk.
  This is v1's scheme; the selection step itself is nested because it only uses y[Tr].)
- Threshold_f = 95th percentile (numpy linear interpolation) of the 10 permuted-source scores on the same Tr.
- Policies per outer fold:
  NONE = RF(X) (make_model RF);
  PHYS = pre-specified source (below);
  TOP  = highest-score REAL source (permuted sources are never candidates);
  GATE = TOP's source if its score > Threshold_f else NONE;
  ALL3 = top-3 real sources jointly.
  Transfer model: y ~ LinearRegression(g[Tr]) + RF residual on X; prediction on Te uses g[Te].
- Metric: per outer fold RMSE on Te; gain = (RMSE_NONE - RMSE_policy)/RMSE_NONE; target gain = mean over 15 folds.
  Negative transfer = target gain < -1%.
- Pass (all three): (c1) #targets with GATE negative transfer <= 1 of 11; (c2) mean GATE gain over 11 targets > 0;
  (c3) GATE negative-transfer rate < TOP's rate OR < PHYS's rate. No PARTIAL rule exists for H8 in PREREG:
  anything else is FAIL (the ledger note says how many of the three were met).

### PHYS mapping (pre-specified rule, applied mechanically)
Rule P1: same quantity (p/s/d) for the same penetrant from an independent route (simulation) if it is in the pool.
Rule P2: otherwise, same quantity, experimental, penetrant nearest in the governing molecular parameter --
diffusivity: kinetic diameter (He 2.60, H2O 2.65, H2 2.89, CO2 3.30, O2 3.46, N2 3.64, CH4 3.80 A);
solubility: critical temperature / condensability (He 5, H2 33, N2 126, O2 155, CH4 191, CO2 304, H2O 647 K; linear
distance); for permanent-gas targets only permanent gases are eligible (H2O is a condensable H-bonding vapour).
Water permeability (no p_sim_H2O): P = S*D and the polymer-to-polymer variation of water permeability is dominated by
water sorption (hydrophilicity), so the water-specific solubility source s_sim_H2O is used.

| target | PHYS source | rule |
|---|---|---|
| p_exp_H2O | s_sim_H2O | water permeation is sorption-controlled; only water-specific source |
| s_exp_H2O | s_sim_H2O | P1 same quantity, same penetrant (simulation) |
| d_exp_H2O | d_exp_He | P2 nearest kinetic diameter (2.60 vs 2.65 A) |
| s_exp_He | s_exp_H2 | P2 nearest Tc (33 vs 5 K) |
| s_exp_H2 | s_exp_He | P2 nearest Tc (5 vs 33 K; N2 126 K is farther) |
| d_exp_He | d_exp_H2 | P2 nearest permanent-gas kinetic diameter (2.89 A) |
| d_exp_H2 | d_exp_He | P2 nearest kinetic diameter (2.60 A) |
| s_exp_CO2 | s_sim_CO2 | P1 |
| d_exp_CO2 | d_sim_CO2 | P1 |
| p_exp_CO2_sub40 | p_sim_CO2 | P1 (parent p_exp_CO2 excluded) |
| p_exp_N2_sub40 | p_sim_N2 | P1 (parent p_exp_N2 excluded) |

### Exploratory / descriptive additions (declared now, never graded)
- GATE_MAX (EXPLORATORY): threshold = max of the 10 permuted scores (a crude family-wise version; the pre-registered
  gate is a per-source 95% threshold but TOP is the max over ~36 sources, so it is not family-wise corrected).
- Per-source realized gain in every outer fold (all 35-36 real + 10 permuted sources), to show score-vs-gain,
  ORACLE (best source in hindsight, upper bound) and RANDOM (mean over real sources) -- DESCRIPTIVE.
- Pooled-RMSE gain (sqrt of mean squared error over all 15 fold predictions) as a sensitivity metric.

### Model settings
- Source models: RandomForestRegressor(100 trees, max_features=0.2, random_state=11) exactly as v1.
- Target models (NONE and residual): vrr_common.make_model("RF", seed=r) (300 trees, mf=0.33, min_leaf=2) with n_jobs=1
  inside a 2-thread joblib pool (same estimator, deterministic given random_state). Same seed for NONE and all
  policies within a repeat, so differences come from g only.
- Runtime plan: chunks of (target, repeat) via `python h8_gate.py run <target> <repeat>`; each chunk writes
  results/raw/h8_parts/*; `python h8_gate.py aggregate` builds the summary and ledger.

## 09:51 Correction to the pre-specification text above (counting error, no design change)
- I wrote "each target uses 35-36 real sources". `python h8_gate.py pool` showed 36-37: p_exp_H2O and s_exp_H2O have
  <30 polymers, so they are never in the pool and their own targets keep all 37; the other 9 targets use 36. The
  PHYS source of every target is in its pool (checked by an assert in run_chunk).
- Design change before running: the first draft cached the featurised tasks as a pickle under the scratchpad, but the
  scratchpad IS the data root ("do not write into the data root"), so the cache was removed; every process
  re-featurises in memory (~10 s). My two throw-away probe scripts (explore.py, timing.py) had been written to
  <data root>/h8work; that folder was deleted at the end (11:22). Nothing in data/ or poc_scout/ was touched.

## 09:53-11:16 Runs
- First chunk (s_exp_H2O r0) 153 s: 182 source RF fits (71 s) + 5 folds x 49 target RF fits. Structural check only
  (no design change): TOP and PHYS policy rows equal the per-source rows of the chosen source exactly.
- Added `pending <budget>` (runs unfinished chunks, starts a new one only while elapsed < budget) so every Bash call
  stayed < 9 min (2-3 chunks per call, 4.7-7.6 min per call).
- 33 chunks (11 targets x 3 repeats), 6,587 source RF fits, 81 min of chunk time in total (135-156 s per chunk;
  the CPU was shared, load average ~3). No crash, no reduction of trees, seeds or sources was needed -> no protocol
  deviation for runtime.

## 11:17 Aggregate: graded result (pre-registered) -> H8 FAIL (2 of 3 criteria)
- c1 FAIL: GATE negative transfer in 3/11 targets (bar <= 1): p_exp_H2O -28.7%, s_exp_He -3.7%, s_exp_H2 -2.7%.
- c2 PASS: mean GATE gain over targets +9.0% (bootstrap-over-targets CI -3.3% .. +21.6%, i.e. the CI includes 0;
  the pre-registered bar is only "mean > 0").
- c3 PASS, but only because PHYS is bad: GATE 3/11 = TOP 3/11 < PHYS 5/11. GATE did not beat TOP.
- Policy means (15-fold mean gain): TOP +9.3%, GATE +9.0%, ALL3 +11.1%, PHYS -3.7%; neg targets TOP 3, GATE 3,
  ALL3 2, PHYS 5.

### Why it failed (from the raw files, descriptive)
- The gate almost never closes: open in 164/165 outer folds (99.4%). Top real score mean 0.46-0.97 per target vs
  95% threshold 0.27-0.74. With ~36 candidate sources, the max real score is compared with a per-source 95%
  threshold from only 10 permuted sources -> no multiplicity control. (This was flagged as a caveat at 09:50, before
  running; the pre-registered rule was nevertheless applied as written.)
- The single closed fold (p_exp_H2O, repeat 0, fold 3; top d_sim_CO2 score 0.669 < threshold 0.700): TOP's gain in
  that fold was +51.4%, so the only gate intervention in the whole run removed a large gain (GATE -28.7% vs TOP -25.2%
  for p_exp_H2O).
- Exploratory GATE_MAX (threshold = max of the 10 permuted scores): mean +10.0%, still 3/11 negative -> a stricter
  threshold of this kind would not have rescued c1 either.
- The in-fold score is a weak predictor of out-of-fold gain: per-fold Spearman(score, realized gain) over real sources
  averages 0.17; fold-level AUROC of the score for detecting negative transfer = 0.46 (chance level).
  44% of real source-fold pairs are above the threshold (permuted: 10% by construction), so real sources do correlate
  with the target on the training part, but that correlation does not reliably carry to the test fold for n = 25-50.
- Negative transfer concentrates in the smallest / lowest-variance targets: p_exp_H2O (n=27; TOP picked d_sim_CO2 in
  9/15 folds, mean score 0.78, realized mean gain -7.4% for that source), s_exp_He (n=38, sd 0.37), s_exp_H2 (n=36,
  sd 0.40; TOP picked 7 different sources in 15 folds).

### Sensitivity / descriptive / post hoc (none of these change the graded verdict)
- Pooled-RMSE gain (declared before running): GATE +16.2%, TOP +16.5%, PHYS +2.5%, ALL3 +17.3%; negative-transfer
  targets GATE 3, TOP 3, PHYS 5, ALL3 1. c1 fails under this metric too. The metric matters a lot for tiny targets:
  p_exp_H2O PHYS is -6.3% (fold-mean) but +6.9% (pooled).
- ORACLE (hindsight, uses test labels): best source per fold +31.0%, best fixed source per target +18.7%;
  RANDOM real source -3.6%; permuted sources -9.3% mean, but 39% of permuted source-fold pairs still show a positive
  fold gain (winner's-curse material).
- Gain by source class (all source-fold pairs, mean / median): exp_transport -2.5% / +0.4%, sim_transport -5.9% /
  -0.3%, unrelated_DFT -2.5% / -0.6%, other_property (X_CED) 0.0% / -0.3%, permuted -9.3% / -1.0%.
  TOP chose exp_transport 112, sim_transport 35, unrelated_DFT 18 times (of 165).
- POST HOC (added after seeing the graded result, EXPLORATORY): the v1-style check on 398 (target, source) pairs
  (score and gain averaged over the 15 folds; not a nested quantity). Fold-mean gain: per-target Spearman 0.41,
  AUROC 0.58. Pooled gain (closer to v1's metric): Spearman 0.57 (v1: 0.56), AUROC 0.66 (v1: 0.82), share of
  negative pairs 47% (v1: 61%). So v1's ranking signal roughly reproduces, but its AUROC 0.82 does not, and inside
  a nested selection the score does not stop negative transfer.

### Surprises
- s_exp_H2O (n=25): the best and most-chosen source is X_bandgap_chain (DFT, "unrelated"; chosen 13/15, +39% mean
  gain), while the physics pick s_sim_H2O gives -14.9%. Many sources score > 0.93 on this target; with 20 training
  points a few extreme polymers probably dominate |r| (not checked further).
- PHYS rule P1 (prefer the same-gas simulation) picked simulated sources for 5 targets; 3 were negative
  (s_exp_H2O -14.9%, d_exp_CO2 -8.1%, p_exp_CO2_sub40 -21.8%), whereas TOP's experimental permeability links on the
  sub40 targets gave +43% / +37% (Robeson-type correlation between gases). The PHYS comparator depends on the rule;
  the rule was fixed before running and is NOT revised. The per-source table (h8_source_target.csv) lets anyone
  check other rules.

### Reproducibility check (11:17-11:20)
- Re-ran s_exp_H2O repeat 0. Scores, thresholds and chosen sources are identical to about 1e-15, but realized RMSEs are not
  bit-identical: the multi-threaded source RF (n_jobs=2) changes predictions at about 1e-15, and that flips RF
  tie-breaks in the target model (count fingerprints have many tied split candidates). Size: policy 5-fold mean gain
  |diff| <= 0.0005; per-source 5-fold mean gain |diff| median 0.002, max 0.012; single source-fold gain |diff| up to
  0.062. Far below the margins that decide c1 (closest: s_exp_H2 -2.75% vs the -1% bar). The rerun is kept in
  results/raw/h8_repro/; the original files (used for the aggregate) were restored into h8_parts/.

## Bottom line for the concept
- H8 as pre-registered FAILS: the permutation-threshold gate does not prevent negative transfer (3/11 targets) and
  adds nothing over TOP (the gate is open 99.4% of the time). The "link gate" module must be removed from the claims
  or redefined; any redefinition (family-wise null, minimum target n, ensemble ALL3) is untested here and would need
  its own pre-registration.
- What does hold (descriptive): data-driven selection beats the physics-intuition pick on average (TOP +9.3% vs PHYS
  -3.7%; neg targets 3 vs 5), consistent with v1's rejection of the physics prior (P8).

## Fix round (after adversarial verification, process/h8_verify.md)

Written chronologically during the fix round. The PREREG thresholds are NOT changed. The pre-fix outputs are archived
unchanged in `results/raw/h8_v0_keyexcl/` (parts, aggregated CSVs, `h8_summary_v0.json`, `h8_ledger_v0.csv`,
script snapshot `h8_gate_v0.py`), so every before/after number below can be recomputed.

### 15:23-15:27 Diagnosis of issue 1 (MAJOR, stereo twins escape key-based exclusion) -- confirmed
- Re-ran the verifier's `v2_leak.py`: 7 of 11 targets have feature-identical "twins" in pool sources under a different
  key: s_exp_He, s_exp_H2, d_exp_He, d_exp_H2, s_exp_CO2, d_exp_CO2, p_exp_N2_sub40. Twin-free: p_exp_H2O, s_exp_H2O,
  d_exp_H2O, p_exp_CO2_sub40.
- Classified every twin (scratch script): all target-source twins are cis/trans-annotated vs unannotated SMILES of the
  SAME polymer (non-isomeric canonical SMILES equal), 7 polymers in total (PTMSP, poly(1-trimethylsilyl-1-propyne)
  family / substituted polyacetylenes such as `*/C(C)=C(/*)CCCCCCC`, `*/C(Cl)=C(/*)c1ccccc1`, `*/C=C(/*)C(C)(C)C`,
  `*/C=C(/*)c1ccccc1C(F)(F)F`), EXCEPT one: a 6FDA polyimide isomer pair (meta/para ether linkage) that is a different
  polymer with an identical feature vector, found in X_CED (and its 2 permuted copies) for d_exp_H2 / d_exp_CO2.
- Within-target twins: PTMSP appears twice in d_exp_H2 (-3.585 / -3.745) and in d_exp_CO2 (-4.481 / -4.631). The
  verifier mentioned d_exp_CO2 only; d_exp_H2 has the same duplication.
- Over the whole featurised universe (5,504 keys): 60 feature-identical groups; 11 are stereo twins, 49 are distinct
  polymers that the Morgan(r=2, 1024 count)+9-descriptor representation cannot tell apart (mostly aliphatic
  polyamide/polyester repeat-unit isomers such as nylon-x,y with equal x+y). Only the one polyimide pair touches an H8
  target. (Side finding, relevant to v1 and other hypotheses that use this featurisation: the representation is not
  injective.)

### 15:27 Fix design (chosen before any re-run)
- Polymer identity = non-isomeric canonical SMILES (`Chem.MolToSmiles(m, isomericSmiles=False)`).
- Source exclusion (strict new-polymer setting): remove every source row whose identity OR feature vector equals that
  of any test-fold polymer (`excluded_keys(mode="identity")`). The union is conservative (it also removes the
  feature-identical polyimide isomer).
- Target de-duplication: merge rows of a target with the same identity (mean y), AFTER the v1 sampling, so the sub40
  draws (`default_rng(0)` on the isomeric index, v1 code path) are unchanged. groupby(sort=False) keeps the index order,
  so twin-free targets are returned bit-identical (same n, same order -> same outer folds). Effect: d_exp_H2 51 -> 50,
  d_exp_CO2 151 -> 150 (PTMSP merged); since random_folds depends on n, these two get a new outer partition.
- I did NOT switch `_key_of` itself to non-isomeric keys: that would merge stereo variants inside every source and
  change the p_exp_CO2 / p_exp_N2 index, hence the sub40 random draws, i.e. it would change two target definitions.
- Scope of re-run: `python h8_gate.py checkfix` compares, for every target x repeat 0-2 x source (36-37 real + 10
  permuted) x outer fold, the exclusion set of the old key rule and the new identity rule
  (`results/raw/h8_fix_equivalence.csv`, twin list `h8_fix_twins_rep0.csv`, de-dup record `h8_fix_dedup.json`).
  Result: the 4 twin-free targets have 0 differing exclusion sets and no merged rows in all 3 repeats -> their v0
  chunks are input-identical to the fixed code and are KEPT (no re-run; re-running would only add the known
  thread-level RF jitter, <= 0.0005 on policy means). The 7 affected targets x 3 repeats = 21 chunks are re-run.
  Escaped twin rows now excluded per repeat: s_exp_He 20, s_exp_H2 15, d_exp_He 48, d_exp_H2 36, s_exp_CO2 26,
  d_exp_CO2 36, p_exp_N2_sub40 1.
- New per-source column `n_twin_rows_excluded` in h8_scores.csv (0 for kept v0 chunks, proved by checkfix) and
  `twin_rows_excluded_total` in chunk meta.

### 15:30 Pre-declared rule for the seed-sensitivity add-on (issue 2), written BEFORE repeats 3-4 were run
- Extra outer repeats 3 and 4 (same code, fold seed = target-RF seed = repeat), all 11 targets, written to
  `results/raw/h8_parts_seedsens/`. DESCRIPTIVE only: the graded verdict stays on repeats 0-2 as pre-registered.
- A target's c1 verdict is called "seed-sensitive" iff the c1 status (gain < -1%) of the graded r0-2 mean differs
  from that of the r3-4 mean OR of the r0-4 mean. "Robust negative" iff the r0-2, r3-4 and r0-4 means are all < -1%.
- The verifier's seed runs (unfixed code, 3 targets) are kept in process/verify_H8/seed_parts as-is; my seed runs use
  the fixed code for all 11 targets.
