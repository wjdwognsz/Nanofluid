#!/bin/bash
# Fix round, stream A: H9 within-source-dedup sensitivity, all 7 datasets x 5 seeds, chunked (< 9 min per command)
cd /home/user/Nanofluid/contest_poc/v2/scripts
export VRR_NJOBS=2 OMP_NUM_THREADS=2
L=/home/user/Nanofluid/contest_poc/v2/process/fix_H1H9/logs
run() { ds=$1; seeds=$2; s=$(date +%s); timeout 540 python h9_conformal.py run $ds --seeds $seeds --variant dedup > $L/h9_dedup_${ds}_${seeds//,/-}.log 2>&1; rc=$?; echo "$(date +%H:%M:%S) h9 dedup $ds seeds $seeds rc=$rc $(( $(date +%s)-s ))s" >> $L/streamA.txt; }
run ES1 0,1,2,3,4
run ES2 0,1,2,3,4
run DYE 0,1,2,3,4
run IL_CELL 0,1,2
run IL_CELL 3,4
run DES_MP 0,1
run DES_MP 2,3
run DES_MP 4
for s in 0 1 2 3 4; do run DES_RHO $s; done
for s in 0 1 2 3 4; do run DES_ETA $s; done
echo "$(date +%H:%M:%S) STREAM A DONE" >> $L/streamA.txt
