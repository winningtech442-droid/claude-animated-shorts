#!/bin/bash
# Full FIX #14 pipeline (format A, no face beats). Resumable: rerun to continue (finished frames are skipped).
# Run detached:  setsid nohup ./build_fix14.sh > build_fix14.log 2>&1 &
cd "$(dirname "$0")"
N=$(python3 -c "import json;print(int(round(json.load(open('data/beats_fix14.json'))['length_s']*24)))")
.venv/bin/python render/world.py --beats data/beats_fix14.json --frames 0 $((N-1)) --res 540 960 --samples 16 2>&1 | grep -E "Error|Traceback|rendered build/frames/0..[05]0\.png"
echo "RENDER_DONE $(ls build/frames | wc -l)/$N $(date +%T)"
[ "$(ls build/frames | wc -l)" -ge "$N" ] || { echo "RENDER_INCOMPLETE"; exit 1; }
Q=$(( (N + 3) / 4 ))
for k in 0 1 2 3; do python3 render/compose3d.py --beats data/beats_fix14.json --range $((k*Q)) $(((k+1)*Q)) & done; wait
python3 render/compose3d.py --beats data/beats_fix14.json --assemble
cd ../phoneverse_fix14_studio && for f in ../phoneverse_3d_studio/final/phoneverse_fix14_*.mp4; do echo "== $f"; python3 tools/qc.py $f; done
cd ../phoneverse_3d_studio && python3 tools/phone_size_sheet.py final/phoneverse_fix14_mix_with_pad.mp4 fix14
echo FIX14_DONE $(date +%T)
