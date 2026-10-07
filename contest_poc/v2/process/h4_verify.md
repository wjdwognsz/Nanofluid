# H4 adversarial verification

## Verifier findings

Verifier: independent adversarial check of family H4 (anchor join), 2026-10-07 13:10–13:45. No H4 file was edited.
Throwaway scripts and their raw outputs: `process/verify_H4/` (v1–v7 *.py, *.csv, *.csv.gz).

### Checks that PASSED
1. **PREREG frozen**: `git diff c92451f` shows PREREG.md, vrr_common.py and vrr_data.py unchanged since the pre-registration commit (09:42).
2. **Verdicts recomputed from the raw draw file** (`v1_recompute_verdicts.py`, own rel. change from sse0/ssek, own bootstrap):
   all six graded verdicts and both overall verdicts reproduce exactly (ES1/ES2/DES_ETA/DES_MP/IL_CELL PASS, DES_RHO FAIL; 5/6 → PASS;
   secondary 5/6 → PASS). Also under the looser reading of the rule (any method's mean + any method's CI). Draw counts are as specified
   (k=0: 1, OFF/SHR/FAKE: 30, RET: 5), n_test = n_rows − k everywhere, FAKE never drew the held-out source.
3. **Bootstrap seed**: CI upper bounds with bootstrap seeds 1–5 move by ≤ 0.5 pp; no verdict is near the CI<0 boundary.
   Jackknife (drop any one source): the dataset rule still holds for 100% of drops in all five passing datasets, 0% in DES_RHO.
4. **Leakage, held-out source**: an independent merge-based copy detector reproduces `n_leak_rows_removed` and `n_train_rows` for every
   eligible source of all 7 datasets (0 mismatches). No held-out row has an exact (X, y) duplicate in its training set except 16 rows in
   DES_RHO. FAKE sources never have a copy relation with the held-out source (0 of 12,120 DES_RHO and 0 of 9,480 DES_ETA draws).
   GroupKFold folds are grouped by source (`group_folds`). SHR weights vary only slightly across held-out sources (e.g. ES1 w3 0.77–0.84),
   so the logged caveat (training-source OOF models may contain s) has negligible influence.
5. **Stability, different seeds + independent re-implementation** (`v4_rerun_seed.py`: RF seed 1, GroupKFold seed 1, new anchor rng,
   own leak code, own τ²/σ²): every verdict reproduces. k=3 means (seed 1 vs original): ES1 OFF −31.0 vs −30.0, SHR −31.1 vs −29.9;
   ES2 OFF −33.2 vs −34.4, SHR −34.7 vs −34.8; DES_ETA OFF −14.7 vs −14.9, SHR −16.8 vs −17.1; DES_MP OFF −15.6 vs −14.5, SHR −17.9 vs −17.1;
   IL_CELL OFF −16.7 vs −18.3, SHR −17.9 vs −18.4; DES_RHO OFF +9.0 vs +8.7, SHR −0.1 vs −0.4 (FAIL again). Secondary SHR k1 also reproduces.
6. **Other model class** (HistGB base, not required by PREREG H4): rule PASS in ES1, ES2, DES_ETA, DES_MP, IL_CELL (DES_RHO not run).
   IL_CELL passes only through SHR with GB (SHR −11.9% [−18.9, −5.6]; OFF −6.9% [−18.0, +2.7] would fail).
7. **RET** re-fitted for ES1 (33 sources) and DES_MP (30-source subset) with the same draws: max |diff| to the file 5e-7.
8. **Gap closure** (pooled) recomputed from per-source SSE and prep.npz random-CV predictions: identical to h4_curves.csv
   (ES1 SHR 0.371, ES2 0.654, DES_ETA 0.452, DES_MP 0.355, IL_CELL 0.194, DES_RHO 0.031).
9. **CI units** are sources (per-source mean of 30 draws, then bootstrap over sources); draws are not treated as units.

### Problems found
**[MAJOR, numbers not verdicts] Within-source exact duplicates leave each anchor's twin in the evaluation set.**
- ES1: Cogni-e-SpinDB contains fully identical repeated rows (162 redundant rows). Three "eligible" sources are a single measurement
  repeated 9, 13 and 13 times (10.1016/j.jmrt.2023.01.007, 10.1016/j.mtsust.2022.100275, 10.1016/j.polymer.2020.123366); for them OFF k3 = −100%
  and SHR ≈ −79% by construction, and their within-source SD is 0 (the SNR diagnostic becomes inf). A 4th source has 55 rows / 6 unique (OFF −79%).
- DES_MP: the source file lists many DES twice with the component order swapped (choline chloride+thymol / thymol+choline chloride); the loader
  canonicalises the order, so 1,209 of 3,390 rows (36%) are exact within-source duplicates and 64% of rows have a twin.
- Effect (k=3, cached LOPO residuals, same draws; `v3_dedup.py`). "twin-disjoint" = drop evaluation rows identical in (X, y) to an anchor;
  "dedup" = collapse duplicates inside each source and redraw (sources with ≥ 8 unique rows):

| dataset | OFF main | OFF twin-disjoint | OFF dedup | SHR main | SHR twin-disjoint | SHR dedup |
|---|---|---|---|---|---|---|
| ES1 | −30.0 [−42.3, −18.6] | −21.5 [−31.9, −11.4] (30 src) | −19.4 [−29.8, −9.2] (28) | −29.9 [−39.7, −20.3] | −23.9 [−33.0, −15.0] | −22.2 [−31.4, −12.9] |
| DES_MP | −14.5 [−21.3, −8.0] | **−9.0 [−17.8, +0.7]** | −12.8 [−19.4, −6.7] (64) | −17.1 [−23.0, −11.5] | −13.0 [−20.3, −5.1] | −15.7 [−21.5, −10.2] |
| ES2, IL_CELL, DES_ETA, DES_RHO | twin-disjoint changes ≤ 0.3 pp; dedup (fresh redraw) ≤ 2.0 pp | | | | | |

  RET k3 (re-fitted): ES1 −36.3 → −28.4 [−37.0, −19.9] twin-disjoint; DES_MP −27.7 → −24.4 [−32.3, −16.7].
  Without the 3 all-duplicate sources, ES1 main OFF k3 is −23.0% (SHR −25.0%).
- **Verdicts do not change** (every passing dataset still passes via SHR; DES_MP via OFF alone would fail under twin-disjoint;
  secondary SHR k1 still ≤ 0 everywhere it held). But the headline ES1 "−30%" and DES_MP "−14.5/−17.1%" are inflated by 6–10 pp
  and 2–5 pp. Suggested fix: keep the preregistered numbers, add twin-disjoint/dedup rows to the ledger as robustness (EXPLORATORY), quote the
  de-duplicated effect sizes next to the headline numbers, and flag the 3 single-measurement ES1 sources.

**[minor] Bootstrap units are not fully independent in DES_RHO.** 64 copy-related pairs among the 101 eligible sources form only 39 clusters;
a cluster bootstrap widens OFF k3 to [+4.2, +22.7] and SHR k3 to [−3.8, +7.6]. FAIL unchanged. Other datasets: ES1/ES2 33/10 clusters,
IL_CELL 18, DES_MP 70, DES_ETA 75; CIs change ≤ 0.8 pp.

**[minor] Single RF seed and RF only.** The PREREG common protocol lists 5 seeds and GB/kNN robustness models; H4 used RF seed 0 and its log says
"no deviation". The seed-1 and GB re-runs above show the verdicts are stable; IL_CELL is the most model-sensitive (passes only via SHR with GB).

**[minor] Medians are seed-sensitive.** The quoted per-dataset medians move by up to ~5 pp with another seed (DES_ETA SHR k3 median −10.9% → −6.0%;
SHR k1 median −3.1% → +0.1%). Means and verdicts are stable.

**[minor] DES_RHO near-copies.** 479 held-out rows have a same-key value within 1e-4–1e-2 relative difference in training (missed by the
prereg 1e-4 rule); their LOPO residuals are about 4× smaller. Removing them from evaluation does not rescue DES_RHO (OFF k3 +10.1%, SHR +0.6%).

**[minor] Pseudo-sources from the loader.** The largest DES_ETA "source" is `http://pubs.acs.org/journal/acscii` (1,461 rows, a journal URL, likely
several papers in one unit). It is one of 79 units, so the H4 effect is small; it is a loader issue to report to its owner.

**[minor] Wording.** The summary says "No deviation", but RET uses RF150 instead of the shared RF300 configuration (stated in the same sentence).
Loader-level median imputation (ES1/ES2/DYE) uses all rows, including the held-out source; this affects every family and is negligible.

Bottom line: the H4 verdicts (5/6 PASS, DES_RHO FAIL, secondary 5/6) survive every check. The ES1 and DES_MP effect sizes are overstated because of
within-source duplicate rows, which should be disclosed and quoted alongside the de-duplicated numbers.
