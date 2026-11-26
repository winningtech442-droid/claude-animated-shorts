#!/bin/bash
# Full FIX #13 pipeline (format A). Resumable: rerun to continue. Run detached: setsid nohup ./build_fix13.sh > build_fix13.log 2>&1 &
cd "$(dirname "$0")"
.venv/bin/python render/world.py --beats data/beats_fix13.json --frames 0 1615 --res 540 960 --samples 16 2>&1 | grep -E "Error|Traceback|rendered build/frames/0..[05]0\.png"
echo "RENDER_DONE $(ls build/frames | wc -l) $(date +%T)"
while ! grep -q FACES_DONE ../phoneverse_fix13_studio/face_render.log; do sleep 30; done; echo "FACES_OK"
for r in "0 404" "404 808" "808 1212" "1212 1616"; do python3 render/compose3d.py --beats data/beats_fix13.json --range $r & done; wait
python3 render/compose3d.py --beats data/beats_fix13.json --assemble
cd ../phoneverse_fix13_studio && for f in ../phoneverse_3d_studio/final/phoneverse_fix13_*.mp4; do echo "== $f"; python3 tools/qc.py $f; done
echo FIX13_DONE $(date +%T)
