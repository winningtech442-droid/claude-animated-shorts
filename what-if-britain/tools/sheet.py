# tools/sheet.py
"""usage: python3 -I tools/sheet.py <stillsDir> <out.jpg> [cols=6]  -> labelled contact sheet for review"""
import sys, glob, os
from PIL import Image, ImageDraw
d, out = sys.argv[1], sys.argv[2]; cols = int(sys.argv[3]) if len(sys.argv) > 3 else 6
files = sorted(glob.glob(os.path.join(d, "*.jpg")))
if not files: sys.exit(f"no .jpg stills in {d}")
tw, th = 270, 480
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * (th + 22)), "#111")
dr = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    x, y = (i % cols) * tw, (i // cols) * (th + 22)
    sheet.paste(Image.open(f).convert("RGB").resize((tw, th)), (x, y + 22))
    dr.text((x + 6, y + 5), os.path.basename(f)[:-4], fill="#ddd")
sheet.save(out, quality=85)
print(len(files), "stills ->", out)
