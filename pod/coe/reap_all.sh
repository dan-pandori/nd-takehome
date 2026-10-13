#!/usr/bin/env bash
cd /home/dan/work/create-or-elicit
pod/coe/reap.sh coe-k0 la_ko_s0 post_redo_ko_s0.done topup_ko_s0.done
pod/coe/reap.sh coe-k1 la_ko_s1 ext24_ko_s1.done topup_ko_s1.done
for S in 2 4 5; do pod/coe/reap.sh coe-k$S la_ko_s$S post_ko_s$S.done topup_ko_s$S.done; done
for S in 3 4; do pod/coe/reap.sh coe-f$S la_full_s$S post_full_s$S.done; done
for S in 0 1 2; do pod/coe/reap.sh coe-d$S la_dose1_s$S post_dose1_s$S.done; done
