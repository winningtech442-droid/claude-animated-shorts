#!/usr/bin/env python3
"""compose3d.py: puts the crisp 2D layer over the Blender frames (format A): labels pinned to 3D objects with a leader line,
live readouts (HUD), the hook title and the one caption system (pvui.caption). Face beats take the rendered 3D face clip instead.
  python render/compose3d.py --beats data/beats_fix12.json --test        -> docs/storyboard_3d.png (build/test frames + overlays)
  python render/compose3d.py --beats data/beats_fix12.json --range 0 1667 -> build/out/00000.jpg ... (resumable)
  python render/compose3d.py --beats data/beats_fix12.json --assemble    -> final/<episode>_<mix>.mp4 (one per audio mix)"""
import argparse, json, math, os, subprocess, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pvui as U
W, H = U.W, U.H
ap = argparse.ArgumentParser(); ap.add_argument("--beats", required=True); ap.add_argument("--test", action="store_true"); ap.add_argument("--range", nargs=2, type=int)
ap.add_argument("--assemble", action="store_true"); ap.add_argument("--build", default="build"); a = ap.parse_args()
B = json.load(open(a.beats)); FPS = B.get("fps", 24); BEATS = B["beats"]; TOTAL = int(round(B["length_s"] * FPS))
CAPS = json.load(open(B["captions"])) if B.get("captions") else []
COLORS = {"RED": U.RED, "GREEN": U.GREEN, "ORANGE": U.ORANGE, "YELLOW": U.YELLOW, "BLUE": U.BLUE}
ease, clamp = U.ease, U.clamp
FACE_START = {"kit_shock": 10}                       # first frame of the clip worth showing (the snap)

def beat_at(t): return next((b for b in BEATS if b["t0"] <= t < b["t1"]), BEATS[-1])

def label(im, xy, txt, dx=170, dy=-170, alpha=1.0):
    """Reference style: a small dot on the object, a thin leader line, a dark tag with an orange square."""
    if alpha <= 0: return im
    out = im.convert("RGBA"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); A = int(255 * alpha)
    f = U.font(38); tw = d.textlength(txt, font=f); x, y = xy; tx = max(30, min(W - tw - 90, x + dx)); ty = max(240, min(1180, y + dy))
    d.line([(x, y), (tx + (0 if dx >= 0 else tw + 60), ty + 32)], fill=(255, 255, 255, int(0.85 * A)), width=4)
    d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(255, 255, 255, A), outline=U.ORANGE + (A,), width=4)
    U.rr(d, (tx, ty, tx + tw + 60, ty + 64), 12, fill=(14, 14, 20, int(0.88 * A))); d.rectangle((tx + 16, ty + 24, tx + 32, ty + 40), fill=U.ORANGE + (A,))
    d.text((tx + 44, ty + 32), txt, font=f, fill=(255, 255, 255, A), anchor="lm"); out.alpha_composite(ov); return out.convert("RGB")

def hook(im, t):
    h = B.get("hook")
    if not h or t >= h["until"]: return im
    out = im.convert("RGBA"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); A = int(255 * ease(clamp(t * 5)))
    U.rr(d, (50, 170, 1030, 470), 40, fill=(10, 10, 16, int(0.9 * A))); f = U.font(70); y = 265
    for line in h["lines"]:
        parts = [(p[1:], U.YELLOW) if p.startswith("*") else (p, (255, 255, 255)) for p in line]; x = (W - sum(d.textlength(p, font=f) for p, _ in parts)) / 2
        for p, c in parts: d.text((x, y), p, font=f, fill=c + (A,), anchor="lm", stroke_width=6, stroke_fill=(0, 0, 0, A)); x += d.textlength(p, font=f)
        y += 110
    out.alpha_composite(ov); return out.convert("RGB")

def hud(im, b, t):
    h = b.get("hud")
    if not h or t < h.get("from", -1): return im
    if "count" in h:
        lo, hi, unit = h["count"]; v = int(round(lo + (hi - lo) * ease(clamp((t - b["t0"]) / (b["t1"] - b["t0"]) * (1.4 if unit == "%" else 1.0)))))
        val = f"{v}%" if unit == "%" else f"{unit}{v:,}"
    else: val = h["value"]
    return U.hud(im, h["label"], val, COLORS.get(h.get("color", "RED"), U.RED))

def base_frame(g, sub):
    t = g / FPS; b = beat_at(t)
    if b.get("face"):
        clip = b["face"]; f = min(47, FACE_START.get(clip, 14) + int((t - b["t0"]) * FPS)); p = os.path.join(B["faces"], clip, f"{f:04d}.png")
        im = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS); k = 1 + 0.06 * (t - b["t0"]) / (b["t1"] - b["t0"])
        w, h = int(W / k), int(H / k); return im.crop(((W - w) // 2, int((H - h) * 0.4), (W - w) // 2 + w, int((H - h) * 0.4) + h)).resize((W, H), Image.LANCZOS), None, b
    p = os.path.join(a.build, sub, f"{g:05d}.png"); anc = os.path.join(a.build, "anchors", f"{g:05d}.json")
    return Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS), (json.load(open(anc)) if os.path.exists(anc) else None), b

def frame(g, sub="frames"):
    t = g / FPS; im, anc, b = base_frame(g, sub)
    if anc:
        for L in b.get("labels", []):
            if t < L.get("from", -1) or L["anchor"] not in anc: continue
            x, y, z = anc[L["anchor"]]
            if z <= 0 or not (-0.05 < x < 1.05 and -0.05 < y < 1.05): continue
            al = clamp((t - max(b["t0"], L.get("from", b["t0"]))) / 0.25); im = label(im, (int(x * W), int(y * H)), L["text"], L.get("dx", 170), L.get("dy", -170), al)
    im = hook(im, t); im = hud(im, b, t)
    c = [x for x in CAPS if x["start"] <= t < x["end"]]
    if c: c = c[-1]; im = U.caption(im, c["words"], c["star"], (t - c["start"]) / 0.08)
    return im

if __name__ == "__main__":
    if a.test:
        gs = [int(((b["t0"] + b["t1"]) / 2) * FPS) for b in BEATS]; cw, ch, cols = 216, 384, 9; rows = math.ceil(len(gs) / cols)
        S = Image.new("RGB", (cols * (cw + 6) + 6, rows * (ch + 24) + 6), (40, 40, 48)); dd = ImageDraw.Draw(S)
        for k, (g, b) in enumerate(zip(gs, BEATS)):
            x, y = 6 + (k % cols) * (cw + 6), 6 + (k // cols) * (ch + 24); S.paste(frame(g, "test").resize((cw, ch)), (x, y))
            dd.text((x + 4, y + ch + 4), f'L{b["line"]}  {b["t0"]:.1f}-{b["t1"]:.1f}s  {"face" if b.get("face") else "->".join(b["cam"]) if isinstance(b["cam"], list) else b["cam"]}', fill=(255, 255, 255))
        os.makedirs("docs", exist_ok=True); S.save("docs/storyboard_3d.png"); print("docs/storyboard_3d.png", len(gs), "beats")
    elif a.range:
        os.makedirs(os.path.join(a.build, "out"), exist_ok=True)
        for g in range(a.range[0], min(a.range[1], TOTAL)):
            p = os.path.join(a.build, "out", f"{g:05d}.jpg")
            if not os.path.exists(p): frame(g).save(p, quality=92)
        print("composed", a.range)
    elif a.assemble:
        os.makedirs("final", exist_ok=True); n = len(os.listdir(os.path.join(a.build, "out")))
        for aud in B["audio"]:
            name = f'final/{B["episode"]}_{os.path.splitext(os.path.basename(aud))[0]}.mp4'
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(a.build, "out", "%05d.jpg"), "-i", aud, "-c:v", "libx264", "-preset", "veryfast",
                            "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", name], check=True); print(name, n, "frames")
