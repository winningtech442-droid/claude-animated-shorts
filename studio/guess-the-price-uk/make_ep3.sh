#!/usr/bin/env bash
# Build Ep 3 (New Year): frames -> segments, audio, then mux with loudness boost.
set -e
cd "$(dirname "$0")"
python3 render_ep3.py
python3 audio_ep3.py
cd out_ep3
ffmpeg -v error -y -f concat -safe 0 -i list.txt -i sound.wav -c:v copy \
  -af "volume=10dB,alimiter=limit=0.7:attack=1:release=50:level=disabled,aresample=176400,alimiter=limit=0.8:level=disabled,aresample=44100" \
  -c:a aac -b:a 192k -shortest ep3_new_year.mp4
echo "built out_ep3/ep3_new_year.mp4"
