#!/bin/bash
# tools/build.sh — the whole episode after the shot list is written, in one command.
# usage: tools/build.sh <episode folder> <CompositionId> [voice.mp3] [--demo]
#   The gate (tools/gate.py) runs first and stops the build on any FAIL. To go past it, set
#   FORCE="reason" in front of the command; the reason is printed in the log.
#   e.g. tools/build.sh north-sea NorthSea out/north-sea/vo.mp3
# Steps: events -> music -> effects -> pace check -> picture (resumable chunks) -> mix -> finish -> final check.
set -e
EP=$1; ID=$2; VO=${3:-}; DEMO=""; [ "$4" == "--demo" ] || [ "$3" == "--demo" ] && DEMO="--demo"
[ "$VO" == "--demo" ] && VO=""
D=out/$EP; mkdir -p $D
if [ -n "$FORCE" ]; then python3 -I tools/gate.py $EP ${VO:+--vo $VO} --force "$FORCE"; else python3 -I tools/gate.py $EP ${VO:+--vo $VO}; fi
npx tsx tools/dumpevents.mts $EP
python3 -I audio/score.py $D/events.json $D/music.wav
python3 -I audio/sfx.py $D/events.json $D/sfx.wav | head -1
python3 -I -c "
import json; e=json.load(open('$D/events.json'))
json.dump([{'id':s['id'],'start':s['start'],'end':s['end'],'move':{'fly':'fly','whip':'fast'}.get(s['enter'],'cut' if i else 'drift')} for i,s in enumerate(e['shots'])], open('$D/shots.json','w'))"
python3 -I tools/pacecheck.py $D/shots.json
LEN=$(python3 -I -c "import json; print(json.load(open('$D/events.json'))['total'])")
FRAMES=$(python3 -I -c "import math; print(math.ceil($LEN*30))")
OUT=$D/chunks bash tools/render_chunks.sh $ID $FRAMES 4
if [ -z "$VO" ]; then  # no voiceover yet: a silent track so the mix still runs
  ffmpeg -v error -y -f lavfi -i anullsrc=r=48000:cl=mono -t $LEN $D/silence.wav; VO=$D/silence.wav
fi
python3 -I audio/mix.py --vo $VO --music $D/music.wav --sfx $D/sfx.wav --len $LEN --out $D/mix.wav
ffmpeg -v error -y -f concat -safe 0 -i $D/chunks/list.txt -c copy $D/video.mp4
ffmpeg -v error -y -i $D/video.mp4 -i $D/mix.wav -map 0:v -map 1:a -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p \
  -af apad -c:a aac -b:a 192k -shortest -movflags +faststart out/$EP.mp4
python3 -I tools/qa.py out/$EP.mp4 $DEMO
[ -s $D/post.txt ] && echo "post file: $D/post.txt ($(wc -c < $D/post.txt) chars)" || echo "  ! no $D/post.txt: write the description and hashtags before delivering"
