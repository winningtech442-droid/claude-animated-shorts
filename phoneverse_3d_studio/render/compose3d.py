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
FACE_START = dict({"kit_shock": 10}, **B.get("face_start", {}))                       # first frame of the clip worth showing (the snap)

def beat_at(t): return next((b for b in BEATS if b["t0"] <= t < b["t1"]), BEATS[-1])

def label(im, xy, txt, dx=170, dy=-170, alpha=1.0, size=48):
    """Reference style: a small dot on the object, a thin leader line, a dark tag with an orange square."""
    if alpha <= 0: return im
    out = im.convert("RGBA"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); A = int(255 * alpha)
    f = U.font(size); tw = d.textlength(txt, font=f); x, y = xy; tx = max(30, min(W - tw - 90, x + dx)); ty = max(240, min(1180, y + dy))
    d.line([(x, y), (tx + (0 if dx >= 0 else tw + 60), ty + 32)], fill=(255, 255, 255, int(0.85 * A)), width=4)
    d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(255, 255, 255, A), outline=U.ORANGE + (A,), width=4)
    U.rr(d, (tx, ty, tx + tw + 60, ty + 64), 12, fill=(14, 14, 20, int(0.88 * A))); d.rectangle((tx + 16, ty + 24, tx + 32, ty + 40), fill=U.ORANGE + (A,))
    d.text((tx + 44, ty + 32), txt, font=f, fill=(255, 255, 255, A), anchor="lm"); out.alpha_composite(ov); return out.convert("RGB")

def hook(im, t):
    h = B.get("hook")
    if not h or t >= h["until"] or t < h.get("from", 0): return im          # "from": let frame 1 action (the drop) play clean first
    out = im.convert("RGBA"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); A = int(255 * ease(clamp((t - h.get("from", 0)) * 5)))
    U.rr(d, (50, 170, 1030, 470), 40, fill=(10, 10, 16, int(0.9 * A))); f = U.font(70); y = 265
    for line in h["lines"]:
        parts = [(p[1:], U.YELLOW) if p.startswith("*") else (p, (255, 255, 255)) for p in line]; x = (W - sum(d.textlength(p, font=f) for p, _ in parts)) / 2
        for p, c in parts: d.text((x, y), p, font=f, fill=c + (A,), anchor="lm", stroke_width=6, stroke_fill=(0, 0, 0, A)); x += d.textlength(p, font=f)
        y += 110
    out.alpha_composite(ov); return out.convert("RGB")

def hud(im, b, t):
    h = b.get("hud")
    if not h or t < h.get("from", -1): return im
    t0_ = h.get("from", b["t0"])                     # v2 (FIX #14): a count that spans two beats keeps counting across the cut (it reset to 0 before)
    pr = clamp((t - t0_) / max(1e-3, h.get("until", b["t1"]) - t0_))
    if "steps" in h: val = h["steps"][min(len(h["steps"]) - 1, int(pr * len(h["steps"])))]
    elif "count" in h:
        lo, hi, unit = h["count"][:3]; suf = h["count"][3] if len(h["count"]) > 3 else ""
        if unit == "s": val = f"{lo + (hi - lo) * pr:.1f} s"                     # a live timer (linear, it is a clock)
        else:
            v = int(round(lo + (hi - lo) * ease(clamp(pr * (1.4 if unit == "%" else 1.0))))); val = f"{v}%" if unit == "%" else f"{unit}{v:,}{suf}"
    else: val = h["value"]
    return U.hud(im, h["label"], val, COLORS.get(h.get("color", "RED"), U.RED))

def base_frame(g, sub):
    t = g / FPS; b = beat_at(t)
    if b.get("face"):
        clip = b["face"]; f = min(47, FACE_START.get(clip, 14) + int((t - b["t0"]) * FPS)); p = os.path.join(B["faces"], clip, f"{f:04d}.png")
        if not os.path.exists(p):                                     # clip still rendering: nearest existing frame, else a labelled placeholder
            have = sorted(os.listdir(os.path.join(B["faces"], clip))) if os.path.isdir(os.path.join(B["faces"], clip)) else []
            if not have:
                ph = Image.new("RGB", (W, H), (30, 30, 40)); ImageDraw.Draw(ph).text((W // 2, H // 2), f"FACE: {clip}", font=U.font(60), fill=(200, 200, 210), anchor="mm"); return ph, None, b
            p = os.path.join(B["faces"], clip, min(have, key=lambda n: abs(int(n[:4]) - f)))
        im = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS); k = 1 + 0.06 * (t - b["t0"]) / (b["t1"] - b["t0"])
        w, h = int(W / k), int(H / k); return im.crop(((W - w) // 2, int((H - h) * 0.4), (W - w) // 2 + w, int((H - h) * 0.4) + h)).resize((W, H), Image.LANCZOS), None, b
    p = os.path.join(a.build, sub, f"{g:05d}.png"); anc = os.path.join(a.build, "anchors", f"{g:05d}.json")
    return Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS), (json.load(open(anc)) if os.path.exists(anc) else None), b

PARTS = [("cpu", "CPU", 230, -330), ("modem", "MODEM", 210, -150), ("sim", "SIM", -250, -260), ("filter", "FILTER", -260, 60), ("battery", "BATTERY", 200, 120)]
def part_labels(im, anc, b, t):
    """v2 (FIX #13): while the lid is open (>60%), label the board parts automatically, unless the beat already pins that anchor
    or sets "parts": false. Fades in with the lid."""
    lid = anc.get("_lid", 0)
    if lid < 0.6 or b.get("parts") is False or "duo" in B.get("props", []): return im
    have = {L["anchor"] for L in b.get("labels", [])}; al = clamp((lid - 0.6) / 0.3); want = b.get("parts") if isinstance(b.get("parts"), list) else None
    for k, txt, dx, dy in PARTS:
        if k in have or k not in anc or (want is not None and k not in want): continue
        x, y, z = anc[k]
        if z > 0 and 0.03 < x < 0.97 and 0.08 < y < 0.92: im = label(im, (int(x * W), int(y * H)), txt, dx, dy, al, size=44)
    return im

def screen_inset(im, b, t, anc):
    """v2 (FIX #13): the hero phone's screen is unreadable in wide shots. When the beat asks ("inset": true) or the screen is small
    on frame (< 22% of the height) and the beat shows a screen, draw the screen as a crisp card top-right with a leader line."""
    spec = b.get("inner") or ("U.duo_home()" if "duo" in B.get("props", []) else b.get("screen"))
    if not spec or b.get("inset") is False or not anc: return im
    if not (b.get("inset") or anc.get("_screen_px", 1) < 0.22): return im
    p = clamp((t - b["t0"]) / max(1e-3, b["t1"] - b["t0"])); scr = eval(spec, {"U": U, "p": round(p * 48) / 48, "ease": ease, "clamp": clamp}).convert("RGB")
    # v3 (FIX #14): bigger and fully opaque (FIX #13 insets were washed out / too small at phone size)
    cw = 470; ch = int(cw * scr.height / scr.width); x0, y0 = b.get("inset_xy", [W - cw - 40, 200]); al = 1.0
    out = im.convert("RGBA"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); A = int(255 * al)
    if "screen" in anc and anc["screen"][2] > 0:
        sx, sy = int(anc["screen"][0] * W), int(anc["screen"][1] * H); d.line([(sx, sy), (x0 + cw // 2, y0 + ch)], fill=(255, 255, 255, int(0.8 * A)), width=4)
        d.ellipse((sx - 10, sy - 10, sx + 10, sy + 10), fill=(255, 255, 255, A), outline=U.ORANGE + (A,), width=4)
    U.rr(d, (x0 - 12, y0 - 12, x0 + cw + 12, y0 + ch + 12), 34, fill=(14, 14, 20, 255), outline=(255, 255, 255, 255), width=5); out.alpha_composite(ov)
    card = scr.resize((cw, ch), Image.LANCZOS).convert("RGBA"); m = Image.new("L", (cw, ch), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, cw - 1, ch - 1), 26, fill=A)
    out.paste(card, (x0, y0), m); return out.convert("RGB")

def shake(im, t):
    """Camera-shake on impacts: beat sheet "shake": [times]; decays over 0.3 s."""
    for s0 in B.get("shake", []):
        if 0 <= t - s0 < 0.3:
            k = (1 - (t - s0) / 0.3) * 26; dx = int(k * math.sin(t * 97)); dy = int(k * math.cos(t * 71))
            big = im.resize((W + 60, H + 106), Image.LANCZOS); return big.crop((30 - dx, 53 - dy, 30 - dx + W, 53 - dy + H))
    return im

def extras(im, t):
    out = im.convert("RGBA"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    sc = B.get("scorecards")                                              # gymnast scorecards after the bounce (visual joke)
    if sc and sc["t0"] <= t < sc["t1"]:
        for i, v in enumerate(sc["cards"]):
            k = ease(clamp((t - sc["t0"] - i * 0.12) / 0.2)); x = 150 + i * 290; y = int(1180 - 140 * k)
            if k <= 0: continue
            U.rr(d, (x, y, x + 230, y + 150), 18, fill=(255, 255, 255, 255), outline=(20, 20, 28, 255), width=6)
            d.text((x + 115, y + 78), v, font=U.font(86), fill=(20, 20, 28, 255), anchor="mm"); d.rectangle((x + 105, y + 150, x + 125, y + 260), fill=(60, 60, 70, 255))
    for r in B.get("replay", []):                                         # sports-replay tag while the drop is replayed
        if r[0] <= t < r[1]:
            U.rr(d, (50, 200, 420, 300), 22, fill=(235, 50, 60, 255)); d.text((235, 250), "◀◀ REPLAY", font=U.font(52), fill=(255, 255, 255, 255), anchor="mm")
            for y in range(0, H, 8): d.line([(0, y), (W, y)], fill=(0, 0, 0, 40))
    vf = B.get("viewfinder")                                              # photo viewfinder + white flash
    if vf and vf["t0"] <= t < vf["t1"]:
        for (x, y, sx, sy) in ((90, 260, 1, 1), (W - 90, 260, -1, 1), (90, 1240, 1, -1), (W - 90, 1240, -1, -1)):
            d.line([(x, y), (x + sx * 140, y)], fill=(255, 255, 255, 255), width=14); d.line([(x, y), (x, y + sy * 140)], fill=(255, 255, 255, 255), width=14)
        f = clamp(1 - abs(t - vf["flash"]) / 0.18)
        if f > 0: d.rectangle((0, 0, W, H), fill=(255, 255, 255, int(235 * f)))
    out.alpha_composite(ov); return out.convert("RGB")

def frame(g, sub="frames"):
    t = g / FPS; im, anc, b = base_frame(g, sub)
    if anc: im = part_labels(im, anc, b, t); im = screen_inset(im, b, t, anc)
    if anc:
        for L in b.get("labels", []):
            if t < L.get("from", -1) or L["anchor"] not in anc: continue
            x, y, z = anc[L["anchor"]]
            if z <= 0 or not (-0.05 < x < 1.05 and -0.05 < y < 1.05): continue
            al = clamp((t - max(b["t0"], L.get("from", b["t0"]))) / 0.25); im = label(im, (int(x * W), int(y * H)), L["text"], L.get("dx", 170), L.get("dy", -170), al)
    im = shake(im, t); im = extras(im, t); im = hook(im, t); im = hud(im, b, t)
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
