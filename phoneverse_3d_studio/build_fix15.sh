#!/bin/bash
# Full FIX #15 pipeline (format A + character beats). Resumable: rerun to continue (finished frames are skipped).
# Run detached:  setsid nohup ./build_fix15.sh > build_fix15.log 2>&1 &
cd "$(dirname "$0")"
BEATS=data/beats_fix15.json
N=$(python3 -c "import json;print(int(round(json.load(open('$BEATS'))['length_s']*24)))")
for c in $(python3 -c "import json;print(' '.join(b['char'] for b in json.load(open('$BEATS'))['beats'] if b.get('char')))"); do
  .venv/bin/python render/char_scene.py --beats $BEATS --clip $c --res 540 960 --samples 14 2>&1 | grep -E "Error|Traceback" ; echo "CHAR $c done $(date +%T)"
done
.venv/bin/python render/world.py --beats $BEATS --frames 0 $((N-1)) --res 540 960 --samples 16 2>&1 | grep -E "Error|Traceback|rendered build/frames/0..[05]0\.png"
echo "RENDER_DONE $(ls build/frames | wc -l) desk frames $(date +%T)"
Q=$(( (N + 3) / 4 ))
for k in 0 1 2 3; do python3 render/compose3d.py --beats $BEATS --range $((k*Q)) $(((k+1)*Q)) & done; wait
[ "$(ls build/out | wc -l)" -ge "$N" ] || { echo "COMPOSE_INCOMPLETE $(ls build/out | wc -l)/$N"; exit 1; }
python3 render/compose3d.py --beats $BEATS --assemble
cd ../phoneverse_fix15_studio && for f in ../phoneverse_3d_studio/final/phoneverse_fix15_*.mp4; do echo "== $f"; python3 tools/qc.py $f; done
cd ../phoneverse_3d_studio && python3 tools/phone_size_sheet.py final/phoneverse_fix15_mix_with_pad.mp4 fix15
echo FIX15_DONE $(date +%T)
