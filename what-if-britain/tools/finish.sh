#!/bin/bash
# tools/finish.sh
# usage: tools/finish.sh <mix.wav> <name>
# -> out/<name>-master.mp4 (CRF 15 video + AAC 256k) and out/<name>.mp4 (2-pass, sized under 29 MB for chat)
set -e
MIX=$1; NAME=$2
ffmpeg -v error -y -f concat -safe 0 -i out/chunks/list.txt -c copy out/video_noaudio.mp4
ffmpeg -v error -y -i out/video_noaudio.mp4 -i "$MIX" -map 0:v -map 1:a -c:v copy -af apad -c:a aac -b:a 256k -shortest \
  -movflags +faststart out/$NAME-master.mp4
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 out/$NAME-master.mp4)
VBR=$(python3 -c "print(min(2000, int((29 * 8 * 1024 * 1024 / $DUR - 192000) / 1000)))")
ffmpeg -v error -y -i out/$NAME-master.mp4 -c:v libx264 -preset medium -b:v ${VBR}k -pass 1 -passlogfile out/x264 -an -f null /dev/null
ffmpeg -v error -y -i out/$NAME-master.mp4 -c:v libx264 -preset medium -b:v ${VBR}k -pass 2 -passlogfile out/x264 \
  -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart out/$NAME.mp4
rm -f out/x264*
ls -l out/$NAME-master.mp4 out/$NAME.mp4
ffmpeg -hide_banner -i out/$NAME.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -A12 Summary | grep -E "I:|LRA:|Peak:"
