#!/bin/bash
# Full showcase pipeline for the FIX #12 format-A test episode. Resumable: rerun to continue.
cd "$(dirname "$0")"
.venv/bin/python render/world.py --beats data/beats_fix12.json --frames 0 1666 --res 540 960 --samples 16 2>&1 | grep -E "Error|Traceback"
echo "RENDER_DONE $(ls build/frames | wc -l)"
for r in "0 417" "417 834" "834 1251" "1251 1667"; do .venv/bin/python render/compose3d.py --beats data/beats_fix12.json --range $r & done; wait
.venv/bin/python render/compose3d.py --beats data/beats_fix12.json --assemble
cd ../phoneverse_fix12_studio && for f in ../phoneverse_3d_studio/final/*.mp4; do echo "== $f"; python3 tools/qc.py $f; done
echo SHOWCASE_DONE
