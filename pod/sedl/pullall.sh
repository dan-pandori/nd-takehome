#!/usr/bin/env bash
# Pull every result directory from both pods into the worktree, never letting sedl1's placeholder logs (for jobs that ran
# on sedl2) overwrite the real ones, nor sedl2's placeholder for xfit_s2_S_Kal (ran on sedl1).
cd /home/dan/work/style-edl
X1="--exclude edl_s1_S_Kal.* --exclude edl_s2_S_Kal.* --exclude edlfix_s1_S_Kal.* --exclude edlfix_s2_S_Kal.* --exclude xfit_s1_S_Kal.*"
for d in edl edl_x cap lv; do pod/sedl/pull.sh sedl1 artifacts/style_edl/$d >/dev/null 2>&1; done
pod/sedl/pull.sh sedl1 artifacts/style_edl/logs $X1 --exclude 'xfit_s2_S_Kal.*' >/dev/null 2>&1
pod/sedl/pull.sh sedl1 artifacts/style_edl/logs --include '*/' --include 'xfit_s2_S_Kal.*' --exclude '*' >/dev/null 2>&1
for d in edl edl_x cap lv; do pod/sedl/pull.sh sedl2 artifacts/style_edl/$d --exclude 'xfit_s2_S_Kal*' >/dev/null 2>&1; done
pod/sedl/pull.sh sedl2 artifacts/style_edl/logs --exclude 'xfit_s2_S_Kal.*' --include '*/' --include '*S_Kal*' --exclude '*' >/dev/null 2>&1
mkdir -p artifacts/style-edl/registry
pod/sedl/pull.sh sedl1 artifacts/style-edl/registry >/dev/null 2>&1
pod/sedl/pull.sh sedl2 artifacts/style-edl/registry >/dev/null 2>&1
grep -L "placeholder" artifacts/style_edl/logs/*Kal*.log | wc -l
