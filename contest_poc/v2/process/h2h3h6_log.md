# H2 + H3 + H6 process log — inter-source discrepancy (H2), offset stability & reference DES (H3), lineage & curation (H6)

Chronological, honest notes. Times are container time (UTC, date 2026-10-07). Note: I first wrote some section
times from memory and they were wrong (too late by 10–25 min); at 11:52 I corrected them from file modification times
(`ls --time-style=full-iso`). The order of events was never different from what is written.
Everything in the "commitments" section was fixed before any H2/H3/H6 *modelling* number or pair statistic existed.
Things I had already seen are listed explicitly in the "what I had seen" section.

## 11:26 — Setup and profiling

- Read PREREG.md §2 (H2, H3, H6), vrr_common.py, vrr_data.py, v1 `scripts/poc_electrospin.py` (near-condition pair
  definition), the head of `process/h4_log.md` and `process/h1h9_log.md` (for conventions), and the partial `ledger/h1.csv`.
- Profile (rows / sources / sources with >=10 rows / exact keys measured by >=2 sources / copy-relation source pairs
  (of all source pairs sharing a key) / rows flagged by copy_mask / sources with >=10 rows that have >=2 materials):
  - ES1 777 / 54 / 26 / 3 / 0 of 2 / 0 / 5
  - ES2 267 / 28 / **7** / 0 / 0 / 0 / 1
  - DYE 131 / 12 / **3** / 2 / 0 of 1 / 2 / 3
  - DES_RHO 6937 / 132 / 90 / 1996 / 68 of 370 / 1975 / 90
  - DES_ETA 5789 / 114 / 74 / 413 / 4 of 55 / 256 / 73
  - DES_MP 3390 / 115 / 56 / 33 / 2 of 27 / 10 / 56
  - IL_CELL 674 / 33 / 17 / 5 / 1 of 3 / 4 / 17
- H3a eligibility (>= 8 sources with >= 10 rows): ES1, DES_RHO, DES_ETA, DES_MP, IL_CELL eligible (5).
  ES2 (7 sources) and DYE (3) are **ineligible** → INCONCLUSIVE rows. Overall H3a PASS therefore needs 4 of the 5.
- ES1: only 5 of its 26 eligible sources have >= 2 materials (material = polymer | solvent), so the "material-disjoint"
  split falls back to row-random for 21/26 ES1 sources (PREREG rule). This makes the strict split almost the same as
  the row-random one for ES1 — a known weakness, stated now.
- Reference DES (H3b) availability, counted from SMILES/mole fraction only (no y looked at):
  ChCl canonical SMILES = `C[N+](C)(C)CCO.[Cl-]`; urea `NC(N)=O`, EG `OCCO`, glycerol `OCC(O)CO`.
  x_ChCl values present: 0.333, 0.33, 0.34, plus a composition series 0.313/0.317/0.323/0.328 (one urea paper), 0.36, 0.28 ...
  DES_RHO: ChCl:urea 117 rows / 28 sources, ChCl:EG 313 / 30, ChCl:glycerol 95 / 27 (all x).
  DES_ETA: ChCl:urea 185 / 10, ChCl:EG 203 / 11, ChCl:glycerol 200 / 7 (all x).
- H6c DOI overlap ES1-PVDF (351 rows incl. unstable, 30 DOIs) vs ES2 (raw 28 sources): exact-string overlap after
  the loaders' own normalisation = 12 DOIs; after also stripping trailing punctuation = 14 DOIs
  (`10.1007/s10965-014-0571-8.` and `10.1021/acsami.0c02578.` carry a trailing dot in ES1).
  Two more pairs are visibly the same paper but do not match as DOIs: ES2 `10.1109/-no.2013.6720964` vs ES1
  `10.1109/nano.2013.6720964` (ES2 DOI corrupted: "na" lost), and ES2 "D.D. Pise ... Study of Process Para" (no DOI)
  vs ES1's ResearchGate link for the same Pise paper. These two are themselves curation discrepancies.

### What I had already seen before fixing the commitments (disclosure)
- For H6c I printed the shared-paper rows of both databases (conditions AND fiber diameters) to understand the column
  formats (ES2 uses "-" for missing V/L/Q/D; ES1 stores w/v% for some papers where ES2's column is labelled wt%;
  ES1 contains exact within-paper duplicate rows, e.g. memsci.2018.06.050 rows 11-13 = rows 82-84, and memsci.2013.01.023
  repeats each condition 8x). Many matched diameters looked identical by eye. H6c is DESCRIPTIVE in PREREG, so this does
  not touch a graded test, but the matching tolerances below were chosen after this look. Disclosed here.
- From other agents' logs: H4 smoke-test numbers for ES2/DYE (ES2 between-source variance tau² ≈ 0.14 > within sigma² ≈ 0.057),
  and H1's DYE verdict. None of these are H2/H3/H6 statistics; ES2 and DYE are ineligible for H3a anyway.
- No H2 pair difference, no H3 residual, no H6a/H6b RMSE had been computed when the commitments below were written.

## ~11:28 — Interpretations fixed BEFORE running (pre-results commitments)

### Shared out-of-source predictions (`scripts/h3_oof.py`)
1. For each dataset (raw, as loaded), seeds 0–4: folds = `group_folds(ds.group, 10, seed)`; model = `make_model("RF", seed)`.
   Two training conditions on the same folds:
   - `rm` (leak-free): training rows = rows not in the test fold AND not in the union of `leak_mask_for_source(ds, s)`
     over the test-fold sources (the source and its copies held by other sources are excluded).
   - `keep` (plain): training rows = rows not in the test fold (copies of test sources remain in training).
   If a fold's leak union is empty, keep == rm (identical training set and seed), so the fit is reused (not refit).
2. Residual r = y − p_rm(seed 0) is the PREREG H3 "출처 밖 잔차" (GroupKFold 10, RF, leak copies removed); it is the
   same definition H4 uses for SHR. Seeds 1–4 give robustness copies (DESCRIPTIVE only).

### H2 (`scripts/h2_discrepancy.py`)
1. Exact-key pairs (all 7 datasets): drop rows with `copy_mask`; average y per (key, source); all source pairs within a key;
   drop pairs flagged `copy_relation` by `copy_relations(ds)` (computed on the full dataset). Δ = y(s_a) − y(s_b) in the
   loader's y scale (DES_RHO g/cm³, DES_ETA log10 cP, ES log10 nm, DES_MP K, DYE %, IL_CELL wt%).
2. σ_between = median|Δ| / (0.6745·√2); R²_ceiling = 1 − σ²_between / Var(y), Var(y) = sample variance (ddof=1) of the full
   raw y of the dataset; also σ_between / SD(y).
3. ES1 primary = v1 near-condition cross-paper pairs on the ES1 regression rows (stable formations): same polymer, same
   solvent string, same collector_type, |Δconc_wt| <= 1 wt%, |ΔV| <= 2 kV, |ln(Q1/Q2)| <= ln 1.3, |ΔL| <= 2 cm,
   different source (row-level pairs, as v1). Same-paper near pairs = within-lab reference (DESCRIPTIVE). ES1 exact-key
   pairs also reported. ES2 has 0 exact-key pairs → EXPLORATORY near-condition pairs (same solvent AND ratio, same
   tolerances, rows whose V, L or Q was median-imputed by the loader are not allowed to pair).
4. Unit of uncertainty: pairs that come from the same source pair share one offset, so CIs are cluster bootstraps over
   **source pairs** (2000 resamples, seed 0): resample source pairs with replacement, pool their |Δ|, take the median.
5. Predictions (point estimate decides, CI reported as context):
   - P2a DES_RHO median|Δρ| <= 0.010 g/cm³;
   - P2b DES_ETA 10^(median|Δlog10 η|) >= 1.10;
   - P2c σ_between/SD(y): DES_RHO < DES_ETA (CI of the difference from independent bootstraps of the two datasets).
   H2 overall PASS iff >= 2 of 3 hold, else FAIL.
6. RF source-CV R² (for comparison with R²_ceiling): R² of p_rm over all rows, mean over seeds 0–4 (also p_keep).
   Headroom = R²_ceiling − R²_RF. DESCRIPTIVE.
7. Sensitivities (DESCRIPTIVE): (a) source-pair-balanced median = median of per-source-pair medians;
   (b) copies NOT removed (copy rows and copy-relation pairs kept), to show how lineage shrinks the apparent discrepancy.

### H3a (`scripts/h3_offset.py`)
1. Eligible datasets: >= 8 sources with >= 10 rows; units = sources with >= 10 rows; residuals = seed-0 rm residuals.
2. 50 random splits, rng = default_rng([crc32(dataset), b]). Row-random: permute the source's rows, half A = first
   floor(n/2), half B = rest. Material-disjoint (graded): sources with >= 2 materials: permute the source's materials and
   assign each, in that order, to the half with fewer rows so far (tie → A); sources with < 2 materials use the row-random split.
3. Per split b: Pearson r_b across sources of (mean residual of half A, mean residual of half B).
   r̄ = mean_b r_b; R = Spearman–Brown 2r̄/(1+r̄).
4. CI: source bootstrap (2000, seed 0) — resample sources, recompute r̄ with the same 50 splits, apply SB; percentile 95%.
5. Null: 200 permutations of the residual vector across all rows of the eligible sources (ignoring source),
   rng default_rng([crc32(dataset), 999, j]); the same 50 split assignments; null R_j; threshold = 95th percentile.
6. Dataset PASS iff R >= 0.5 AND CI_lo > 0 AND R > null p95 (material-disjoint split). The row-random split gets the same
   rule but is DESCRIPTIVE. Overall H3a: PASS iff >= 4 eligible datasets PASS, else FAIL (PREREG defines no PARTIAL band).
7. EXPLORATORY: (a) strict-only — only sources with >= 2 materials, material-disjoint split;
   (b) lineage-cleaned DES_RHO / DES_ETA (copy_mask rows dropped from the residual set, residuals unchanged);
   (c) residuals from seeds 1–4.

### H3b (`scripts/h3_offset.py`)
1. DES_RHO and DES_ETA (raw), seed-0 rm residuals.
2. Reference rows: one component == ChCl canonical SMILES and the other ∈ {urea, EG, glycerol} canonical SMILES and
   |x_ChCl − 1/3| <= 0.01 (covers 0.33/0.333/0.34 two- and three-decimal roundings; also admits 0.328), any temperature.
3. Eligible sources: >= 1 reference row and >= 1 non-reference row. offset_ref = mean residual of the reference rows,
   offset_other = mean residual of the other rows.
4. Spearman ρ across eligible sources. p = permutation (5000, rng default_rng([crc32(dataset), 5000])) of offset_other
   among sources, **two-sided** (|ρ_perm| >= |ρ_obs|) as the conservative primary; one-sided reported too.
   Dataset PASS iff ρ >= 0.3 AND two-sided p < 0.05. H3b overall PASS iff >= 1 of 2 datasets PASS, else FAIL.
5. DESCRIPTIVE sensitivities: copy_mask rows excluded; >= 3 rows on each side; each reference material separately;
   source-bootstrap CI of ρ.

### H6 (`scripts/h6_lineage.py`)
1. H6a (graded): DES_RHO, DES_ETA raw. "출처 단위 RMSE" = row-pooled RMSE under source GroupKFold(10) (the H1 meaning of
   source-level CV), mean of per-seed RMSE over seeds 0–4. change = RMSE_keep / RMSE_rm − 1 (same test rows, only the
   training set differs). CI: source bootstrap (2000, seed 0) of seed-averaged per-row squared errors,
   change* = sqrt(ΣSE_keep / ΣSE_rm) − 1. Dataset meets the rule iff change <= −0.10 AND CI_hi < 0;
   H6a PASS iff >= 1 of the 2 datasets meets it, else FAIL.
   DESCRIPTIVE extras: the same on DES_MP, IL_CELL, DYE (ES1/ES2 have no copies → identical by construction, reported as 0);
   per-source change averaged over sources that have >= 1 leak row ("affected sources").
2. H6b (DESCRIPTIVE): random 5-fold RF, seeds 0–4, RMSE on raw vs lineage-cleaned (`subset(ds, ~copy_mask(ds))`);
   additionally the raw-trained RMSE restricted to the non-copy rows (same evaluation rows as the cleaned run).
3. H6c (DESCRIPTIVE): ES1 PVDF (all rows, stable + unstable) vs ES2 raw sheet (all rows, incl. missing D).
   - DOI normalisation: lowercase, strip https://doi.org/ / doi: prefixes, strip trailing . , ; and whitespace; exact match.
     Primary set = DOI matches. Sensitivity set adds the 2 visibly-identical papers listed above.
   - Row matching per paper: feasible pair iff |c_ES1,reported − c_ES2| <= 0.5 (reported number, unit label ignored),
     |ΔV| <= 0.5 kV, |ΔL| <= 0.5 cm, |Q1/Q2 − 1| <= 0.10; an ES2 field that is missing ("-") is a wildcard (counted).
     One-to-one assignment (scipy linear_sum_assignment) with lexicographic cost: number of wildcards, then normalised
     condition distance, then solvent-set disagreement, then |Δlog10 D| (last tie-break: only decides among rows whose
     conditions are indistinguishable; the number of such ambiguous matches is reported, and the identical-value rate is
     also reported on unambiguous matches only).
   - Outcomes: matched rows, ES1-only rows, ES2-only rows; among matches with D in both: identical-value rate
     (|D1 − D2| <= max(0.5 nm, 0.1% of D)), |Δlog10 D| median / mean / max; stability agreement (ES1 unstable ↔ ES2 D missing);
     concentration unit-label disagreement (ES1 w/v% vs ES2 "wt%"), solvent-set disagreement; ES1 within-paper exact duplicates.

### Addendum to the commitments (~11:40, written before any H3 or H6 statistic was computed)
- H3 overall row: PREREG gives H3a and H3b separate rules and no combination rule. I fix: H3_overall = PASS if both
  H3a and H3b PASS, PARTIAL if exactly one passes, FAIL if neither. Both sub-verdicts are always shown next to it.
- H6 overall row = the H6a verdict (H6b and H6c are descriptive by PREREG).
- H3a split RNG: `default_rng([crc32(dataset), b])` is created afresh for each split method (row-random and
  material-disjoint draw from independent fresh streams with the same seed).

## 11:29–11:37 — Shared out-of-source predictions (`scripts/h3_oof.py`)

- Ran per dataset with VRR_NJOBS=2, OMP_NUM_THREADS=2. Timings: ES2+DYE+ES1+IL_CELL 92 s total (ES1 21 s, IL_CELL 26 s);
  DES_MP + DES_ETA 204 s (DES_ETA 123 s); DES_RHO 139 s. Output `results/raw/h236_parts/oof_<DS>.csv.gz`.
- Fits are reused when a fold has no leak rows (ES1, ES2: zero leak rows anywhere, so keep == rm by construction).

## 11:37–11:40 — H2 run (`scripts/h2_discrepancy.py`), first H2 numbers seen

- Bug 1 (syntax): a dict key `frac_identical_abs_delta_le_1e-9` is not a valid keyword → renamed `frac_identical`.
- Bug 2 (statistical hygiene, found on reading my own code after the first run): the cluster bootstraps of DES_RHO and
  DES_ETA both used `default_rng(0)`; the P2c difference CI pairs bootstrap draws by index, so the two streams were not
  independent. Fixed to seed = crc32(dataset). Point estimates (which decide P2a–c) are unchanged; CIs moved in the
  4th decimal (e.g. P2a CI [0.0045, 0.0076] → [0.0043, 0.00755]).
- ES1 v1 replication check: 51 cross-paper near-condition pairs, median |Δlog10 D| = 0.1900 (1.55-fold), and 1536
  same-paper pairs with median 0.00094 — **identical to v1's electrospin_summary.json** (51 / 0.19000 / 1536 / 0.00094).
- Surprise (process finding): the v1 numbers are distorted by ES1's within-paper duplicate rows. 26 of the 51 cross-paper
  pairs come from a single pair of distinct values (10.1016/j.mtsust.2022.100275 stores one condition 13 times), and the
  same-paper median of 0.00094 is mostly duplicate rows compared with themselves. POST-HOC, EXPLORATORY: collapsing exact
  within-paper duplicates (same source, conditions and y) → 25 cross-paper pairs (median still 0.190, 1.55-fold) and 434
  same-paper pairs, median 0.057 (1.14-fold). So between-paper scatter (1.55x) really is larger than within-paper scatter
  (1.14x), but v1's "within-paper 1.002x" was an artefact of duplicates. Logged as EXPLORATORY rows in ledger/h2.csv.
- Lineage matters for H2: in DES_RHO, 2407 cross-source same-key pairs exist, but only 353 are independent; 74.9% of all
  pairs are exactly identical values (copies). Without the lineage step, median |Δρ| would be 0 (DES_ETA: 57% identical).

## 11:41–11:45 — H3 run (`scripts/h3_offset.py`), first H3 numbers seen

- Runtime 44–50 s for everything (vectorised bincount half-means; 50 splits × 200 permutations × 2000 bootstraps).
- **H3a (graded, material-disjoint split): PASS in 5/5 eligible datasets → H3a PASS.**
  R = ES1 0.901, DES_RHO 0.773, DES_ETA 0.928, DES_MP 0.950, IL_CELL 0.942; every CI lower bound > 0.33 and every R far
  above its null p95 (0.27–0.48); perm p = 0.005 is the floor of a 200-permutation test (1/201).
  Seeds 1–4 residuals give the same picture (DES_RHO is the least stable: 0.69–0.76).
- **H3b (graded): FAIL in both datasets → H3b FAIL.** DES_RHO ρ = 0.245 (42 sources, two-sided p = 0.121, one-sided 0.060,
  CI [−0.10, 0.53]); DES_ETA ρ = −0.252 (12 sources, p = 0.425). So the offset a lab shows on ChCl:urea/EG/glycerol does
  not detectably predict its offset on its other materials.
- H3 overall (agent's pre-fixed combination rule) = PARTIAL.
- Forking-path warning (not used for any verdict): one DESCRIPTIVE sensitivity of H3b (copy rows excluded, DES_RHO) gives
  ρ = 0.313, two-sided p = 0.044, which would satisfy the rule. It is one of 6 sensitivities × 2 datasets; the
  preregistered primary is the all-rows version, which fails. Per-material and ">= 3 rows each" versions are all weaker
  (ρ 0.10–0.39 in DES_RHO, all negative in DES_ETA). I report the primary FAIL.
- Weakness found (ES1): only 5/26 eligible ES1 sources have >= 2 materials; 21 use the row-random fallback, so ES1's
  "material-disjoint" R (0.901) is mostly a row-random R. On the 5 sources where a truly material-disjoint split exists,
  R = −0.17 (CI undefined/[nan, 1.0], 5 sources: uninformative, but certainly not supportive). EXPLORATORY row in ledger.
- Bug/ugliness: with 5 sources the bootstrap sometimes draws a single source 5 times → zero variance → NaN correlation
  warnings. Now counted (`n_boot_undefined`) and ignored via nanpercentile; only affects that exploratory ES1 row.

### Post-hoc exploration triggered by the H3a-PASS / H3b-FAIL tension (EXPLORATORY; added after seeing results)
1. "System-disjoint" split (halves share no chemical system: DES → component pair A|B with composition ignored,
   IL_CELL → ionic liquid, ES1 → polymer). PREREG's "material" for DES is A|B|x, so its material-disjoint halves can
   still be the same chemistry at another ratio. Results (R, strict = only sources with >= 2 systems):
   DES_RHO 0.680 (strict 0.571, CI [0.34, 0.73]); DES_ETA 0.929 (0.916); DES_MP 0.809 (0.767); IL_CELL 0.938 (0.938);
   ES1 0.957 but only through fallback (strict: < 3 sources, not computed). The stability survives, attenuated for DES_RHO.
2. Offset size vs H2's measured inter-lab disagreement: SD of source mean residuals / σ_between =
   DES_RHO 4.4, DES_ETA 4.1, DES_MP 9.1, IL_CELL 3.4 (σ from only 2 pairs), ES1 1.1 (σ from near-condition pairs, inflated).
   Interpretation: in the DES sets the stable "source offset" is 4–9× larger than what two labs disagree by on the
   *identical* sample. So most of what H3a calls a stable offset is model error tied to the chemistry niche a source works
   on, not a lab measurement bias. This explains why a physical reference sample (H3b) does not transfer: the reference
   sees only the small lab-bias part. Consequence for the concept: anchors (H4) should be presented as
   "local calibration of a source's niche", not as "lab bias correction"; reference-material round-robins would need the
   target chemistry itself, not a generic reference.

## 11:46–11:51 — H6 run (`scripts/h6_lineage.py`), first H6 numbers seen

- H6b runs: DES_RHO + DES_ETA 126 s; DES_MP + IL_CELL + DYE 92 s. H6a and H6c are computed in `aggregate` (3 s).
- Bug: in H6c the boolean columns of the matched rows were `object` dtype (the frame also holds ES1-only/ES2-only rows
  with NaN there), so `~bd.ambiguous_condition_tie` produced −1/−2 integers and a KeyError. Fixed by casting the matched
  subset to bool. No result had been produced before the fix.
- **H6a (graded): DES_RHO change = −24.7 % (CI [−38.6 %, −4.3 %]) → meets the rule; DES_ETA −1.8 % (CI [−4.1 %, −0.4 %])
  → does not. H6a PASS (1 of 2 needed).** Copies left in training make DES_RHO's source-level RMSE look 25 % better
  (0.0399 vs 0.0530 g/cm³). In DES_ETA only 15/114 sources have copies elsewhere; for those 15 the mean per-source
  change is −20.8 % (CI [−37.4 %, −6.9 %]), but they are diluted in the all-rows metric. Descriptive: DES_MP −0.3 %,
  IL_CELL 0.0 %, DYE −1.3 % (affected-source means −15 % to −31 %, few sources); ES1/ES2 have no copies.
- H6b (descriptive): random 5-fold RMSE raw vs lineage-cleaned: DES_RHO −15.8 % (0.01992 vs 0.02365; the 1975 copy rows
  are predicted at 0.0093), DES_ETA −2.0 %, DES_MP/IL_CELL/DYE within ±0.5 %.
- H6c (descriptive), 14 papers by normalised DOI: ES1 141 PVDF rows, ES2 104 raw rows; 97 matched one-to-one,
  **90/90 matched diameters are identical (100 %; 56/56 among matches with no condition tie)**, max |Δlog10 D| = 0;
  all 7 ES1 "unstable" rows match ES2 rows with no diameter. Rows in one DB only: ES1 44 (but only 10 distinct
  conditions — ES1 repeats some conditions 7–8×; one whole 24.1 kV series of memsci.2013.01.023 is absent from ES2),
  ES2 7 (ratio/concentration rows that ES2 lists without V/L/Q/D). Metadata disagreements: 13 matched rows are "w/v%"
  in ES1 but sit in ES2's "wt%" column; 1 solvent-label disagreement (ES1 "DMF-ACETONE" vs ES2 "DMF:Acetone 10:0" =
  pure DMF); 1 corrupted DOI in ES2 (`10.1109/-no...`) and 1 ES2 paper without DOI. Adding the 2 manual identity
  matches: 16 papers, 103/103 identical.
- **Surprise with consequences beyond H6:** value-level identity on every matched row means ES2 is *not* an independent
  curation of these 14 papers (one database very likely derived values from the other, or both copied the same tables;
  the direction cannot be decided from the data). 14 of ES2's 28 sources overlap ES1-PVDF. PREREG §1 calls ES2
  "ES1과 독립 큐레이션"; at the value level that is false for half of ES2's sources. Any claim that ES1 and ES2 results
  "replicate independently" (H1, H4, H9) should be qualified. Conversely, the curation round-robin found no value
  transcription error at all — the curation-level noise is in metadata (units, solvents, DOIs, duplicates), not values.

## 11:52 — Wrap-up: verdicts (as in the ledgers)

| test | dataset | value | verdict |
|---|---|---|---|
| H2_P2a | DES_RHO | median abs Δρ 0.00520 g/cm³ (CI 0.0043–0.0076) | PASS |
| H2_P2b | DES_ETA | median fold 1.368 (CI 1.096–1.620) | PASS |
| H2_P2c | DES_RHO vs DES_ETA | σ/SD 0.036 vs 0.169, diff −0.133 (CI −0.227 to −0.013) | PASS |
| H2_overall | | 3/3 | PASS |
| H3a_matdisjoint | ES1 / DES_RHO / DES_ETA / DES_MP / IL_CELL | R 0.901 / 0.773 / 0.928 / 0.950 / 0.942 | PASS ×5 |
| H3a_matdisjoint | ES2, DYE | ineligible (7 and 3 sources with >= 10 rows) | INCONCLUSIVE |
| H3a_overall | | 5/5 | PASS |
| H3b_reference | DES_RHO | ρ 0.245, p 0.121 (two-sided) | FAIL |
| H3b_reference | DES_ETA | ρ −0.252, p 0.425 | FAIL |
| H3b_overall | | 0/2 | FAIL |
| H3_overall | | H3a PASS, H3b FAIL | PARTIAL |
| H6a_copy_leak | DES_RHO | −24.7 % (CI −38.6 % to −4.3 %) | PASS |
| H6a_copy_leak | DES_ETA | −1.8 % (CI −4.1 % to −0.4 %) | FAIL |
| H6a_overall / H6_overall | | 1/2 | PASS |

### Deviations / agent decisions (all also in ledger notes)
1. No compute-driven scope reductions were needed; all datasets, seeds, splits and permutations ran as committed.
2. PREREG left room for choice; my fixed interpretations: H6a "출처 단위 RMSE" = pooled source-GroupKFold RMSE
   (per-source mean reported too); H3b p two-sided (conservative); H3 and H6 overall combination rules (agent-defined,
   written before running H3/H6); H2 CIs by source-pair cluster bootstrap; reference tolerance |x_ChCl − 1/3| <= 0.01.
3. Post-hoc EXPLORATORY additions after seeing results: ES1 dedup pair sets (H2); system-disjoint split and
   offset-vs-σ_between ratio (H3). None of them changes a graded verdict.
4. H6c matching tolerances were chosen after looking at the shared-paper rows (disclosed above; H6c is descriptive).
5. The ES1 "material-disjoint" H3a result relies on the row-random fallback for 21/26 sources (PREREG rule, but it makes
   ES1's strict test weak); on the 5 sources with a real material-disjoint split R = −0.17 (uninformative n).
