#!/bin/bash
# FIX #17 pipeline (format A, silicon world). Resumable: finished frames are skipped.
#   ./build_fix17.sh render A B   -> desk frames A..B at 540x960 / 16 samples (run in chunks: one process builds the scene once, ~80 s)
#   ./build_fix17.sh finish       -> compose (4 in parallel), assemble ONE final (mix_with_pad), QC, phone-size sheet
# Character beats are desk stand-ins until char_scene.py has a "yard" set (see data/make_beats_fix17.py, STANDIN).
cd "$(dirname "$0")"
BEATS=data/beats_fix17.json
N=$(python3 -c "import json;print(int(round(json.load(open('$BEATS'))['length_s']*24)))")
if [ "$1" = "render" ]; then
  .venv/bin/python render/world.py --beats $BEATS --frames $2 $3 --res 540 960 --samples 16 2>&1 | grep -E "Error|Traceback|rendered build/frames/0..[05]0\.png"
  echo "RENDER_CHUNK_DONE $2-$3: $(ls build/frames | wc -l)/$N frames $(date +%T)"; exit 0
fi
if [ "$1" = "finish" ]; then
  [ "$(ls build/frames | wc -l)" -ge "$N" ] || { echo "RENDER_INCOMPLETE $(ls build/frames | wc -l)/$N"; exit 1; }
  Q=$(( (N + 3) / 4 ))
  for k in 0 1 2 3; do python3 render/compose3d.py --beats $BEATS --range $((k*Q)) $(((k+1)*Q)) & done; wait
  [ "$(ls build/out | wc -l)" -ge "$N" ] || { echo "COMPOSE_INCOMPLETE $(ls build/out | wc -l)/$N"; exit 1; }
  python3 render/compose3d.py --beats $BEATS --assemble
  cd ../phoneverse_fix17_studio && for f in ../phoneverse_3d_studio/final/phoneverse_fix17_*.mp4; do echo "== $f"; python3 tools/qc.py $f; done
  cd ../phoneverse_3d_studio && python3 tools/phone_size_sheet.py final/phoneverse_fix17_mix_with_pad.mp4 fix17
  echo FIX17_DONE $(date +%T)
fi
