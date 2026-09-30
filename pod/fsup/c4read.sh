#!/usr/bin/env bash
# The C s4 read-out (OOM'd at 10:18 beside other read-outs): fetch its r8 checkpoint and read it alone.
source pod/fsup/env.sh
CK=ckpts/fsup/ladder/la_C_s4_r8.pt; until [ -s $CK ]; do hf buckets cp $BK/$CK $CK >/dev/null 2>&1 || sleep 30; done
md5sum $CK; bash pod/fsup/reread.sh $CK la_C_s4
