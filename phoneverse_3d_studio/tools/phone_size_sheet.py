#!/usr/bin/env python3
"""Phone-size check sheet: one frame every 2 s from a final MP4, shown at about real phone size (1080x1920 -> 180x320 at
roughly 1/6 scale, which is how a 6.1" phone at arm's length reads on a laptop screen). Writes docs/phone_size_check_<ep>.png.
  python3 tools/phone_size_sheet.py final/phoneverse_fix13_mix_with_pad.mp4 fix13"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
v, ep = sys.argv[1], sys.argv[2]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", v], capture_output=True, text=True).stdout)
ts = [round(t * 2.0 + 0.5, 2) for t in range(int(dur // 2))]
cw, ch, cols = 180, 320, 12; rows = (len(ts) + cols - 1) // cols
S = Image.new("RGB", (cols * (cw + 8) + 8, rows * (ch + 26) + 8), (34, 34, 40)); d = ImageDraw.Draw(S)
with tempfile.TemporaryDirectory() as tmp:
    for i, t in enumerate(ts):
        p = os.path.join(tmp, f"{i}.png")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(t), "-i", v, "-frames:v", "1", "-vf", f"scale={cw}:{ch}:flags=area", p], check=True)
        x, y = 8 + (i % cols) * (cw + 8), 8 + (i // cols) * (ch + 26); S.paste(Image.open(p), (x, y)); d.text((x + 2, y + ch + 6), f"{t:.1f}s", fill=(220, 220, 230))
os.makedirs("docs", exist_ok=True); out = f"docs/phone_size_check_{ep}.png"; S.save(out); print(out, len(ts), "frames")
