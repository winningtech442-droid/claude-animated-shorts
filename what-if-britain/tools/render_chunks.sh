#!/bin/bash
# tools/render_chunks.sh
# usage: tools/render_chunks.sh <CompositionId> <totalFrames> [chunks=4]
# Renders the video (muted) in N resumable chunks: a chunk that already exists is skipped, so an
# interrupted session only loses the chunk in progress. Run in the background and poll the log.
#
# No motion blur (STUDIO-RULES v3: 30 fps, MB=0): each chunk renders the plain 30 fps composition.
# The old motion-blur path stays for reference: MB=8 renders an <id>-mb twin at 240 fps and averages every
# 8 sub-frames, but Root.tsx no longer registers any -mb twins.
set -e
ID=$1; TOTAL=$2; N=${3:-4}; MB=${MB:-0}
HS=$(node -e "import('./tools/browser.mjs').then(m => console.log(m.findBrowser() ?? ''))")
[ -n "$HS" ] && BX="--browser-executable=$HS"
OUT=${OUT:-out/chunks}
mkdir -p $OUT
npx remotion bundle src/index.ts --out-dir=out/bundle --log=error
PER=$(( (TOTAL + N - 1) / N ))
RFLAGS="--muted --gl=swangle $BX --concurrency=2 --image-format=jpeg --jpeg-quality=92 --timeout=120000 --log=error"
for i in $(seq 0 $((N - 1))); do
  A=$((i * PER)); B=$(( (i + 1) * PER - 1 )); [ $B -ge $TOTAL ] && B=$((TOTAL - 1))
  [ $A -gt $B ] && continue
  F=$OUT/c$i.mp4
  if [ -s $F ]; then echo "skip $F"; continue; fi
  echo "chunk $i: frames $A-$B  $(date +%T)  (motion blur: ${MB:-0} sub-frames)"
  if [ "$MB" -le 1 ]; then
    npx remotion render out/bundle $ID $OUT/tmp$i.mp4 --frames=$A-$B --crf=15 $RFLAGS
  else
    H=$((MB / 2))                       # frame k averages sub-frames MB*k-H ... MB*k+H-1
    S=$((MB * A - H)); E=$((MB * B + H - 1)); LAST=$((MB * TOTAL - 1))
    S0=$S; E0=$E; [ $S0 -lt 0 ] && S0=0; [ $E0 -gt $LAST ] && E0=$LAST
    PADS=$((S0 - S)); PADE=$((E - E0))  # repeat the first/last sub-frame where the window runs off the ends
    npx remotion render out/bundle $ID-mb $OUT/sub$i.mp4 --frames=$S0-$E0 --crf=10 $RFLAGS
    ffmpeg -v error -y -i $OUT/sub$i.mp4 -vf "tpad=start=$PADS:stop=$PADE:start_mode=clone:stop_mode=clone,tmix=frames=$MB,select='eq(mod(n\,$MB)\,$((MB - 1)))',setpts=N/30/TB" \
      -r 30 -frames:v $((B - A + 1)) -c:v libx264 -preset veryfast -crf 15 -pix_fmt yuv420p $OUT/tmp$i.mp4
    rm -f $OUT/sub$i.mp4
  fi
  mv $OUT/tmp$i.mp4 $F
done
(cd $OUT && for i in $(seq 0 $((N - 1))); do [ -s c$i.mp4 ] && echo "file 'c$i.mp4'"; done > list.txt)
echo "all chunks done $(date +%T)"
