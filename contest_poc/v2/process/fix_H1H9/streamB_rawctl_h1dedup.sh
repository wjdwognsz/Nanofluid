#!/bin/bash
# Fix round, stream B: (1) H9 raw seed-0 re-run with exploratory controls (+ regression check vs original parts)
#                      (2) H1 within-source-dedup sensitivity, all 7 datasets (cv RF/GB/KNN x 5 seeds + 20 pseudo seeds)
cd /home/user/Nanofluid/contest_poc/v2/scripts
export VRR_NJOBS=2 OMP_NUM_THREADS=2
L=/home/user/Nanofluid/contest_poc/v2/process/fix_H1H9/logs
t() { s=$(date +%s); timeout ${TO:-600} "$@" > $L/$LOGN.log 2>&1; rc=$?; echo "$(date +%H:%M:%S) $LOGN rc=$rc $(( $(date +%s)-s ))s" >> $L/streamB.txt; }
for ds in ES2 DYE IL_CELL DES_MP DES_RHO DES_ETA; do
  LOGN=h9_rawctl_${ds}_s0 t python h9_conformal.py run $ds --seeds 0 --parts-dir ../results/raw/h9_parts_rawctl
done
for ds in ES1 ES2 DYE IL_CELL DES_MP; do
  LOGN=h1_dedup_cv_${ds} t python h1_cv.py cv $ds --variant dedup
  LOGN=h1_dedup_pseudo_${ds} t python h1_cv.py pseudo $ds --variant dedup
done
for ds in DES_RHO DES_ETA; do
  LOGN=h1_dedup_cvRF_${ds} TO=900 t python h1_cv.py cv $ds --variant dedup --models RF
  LOGN=h1_dedup_cvGBKNN_${ds} TO=900 t python h1_cv.py cv $ds --variant dedup --models GB,KNN
  LOGN=h1_dedup_pseudo_${ds} TO=900 t python h1_cv.py pseudo $ds --variant dedup
done
echo "$(date +%H:%M:%S) STREAM B DONE" >> $L/streamB.txt
