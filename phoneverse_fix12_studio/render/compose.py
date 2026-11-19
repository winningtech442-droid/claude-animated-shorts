#!/usr/bin/env python3
"""compose.py: builds every frame of FIX #12 from data/shots.json + data/captions.json using render/pvui.py (2D props) and the 3D face clips.
  python render/compose.py --test            -> docs/storyboard_preview.png (one mid-frame per shot; placeholder faces if frames/<clip>/ are missing)
  python render/compose.py --range 0 1667    -> out/00000.jpg ... (resumable: skips frames that exist)
  python render/compose.py --assemble        -> final/phoneverse_fix12_with_pad.mp4 and final/phoneverse_fix12_voice_fx.mp4
Face clips: frames/<clip>/0000.png..0047.png from render/face_scene.py (portrait). 2D stand-ins are used for the bus/kitchen wide plates; upgrade
2b, 10a and 10b to 3D plates if there is time (known risk: 2D props next to a photoreal face can look like two worlds)."""
import argparse, json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(__file__)); import pvui as U
W, H, FPS = U.W, U.H, 24
SH = json.load(open("data/shots.json")); SHOTS = SH["shots"]; TOTAL = int(round(SH["take_length_s"] * FPS)); CAPS = json.load(open("data/captions.json"))
ease, clamp = U.ease, U.clamp
START = {"bus_hope": 14, "bus_dread": 12, "kit_dread": 12, "kit_shock": 10, "kit_hope_relief": 6, "kit_soft_relief": 14, "kit_relief": 14, "kit_hope": 14}

def zoom(im, z, cx=0.5, cy=0.5):
    w, h = int(W / z), int(H / z); x = int((W - w) * cx); y = int((H - h) * cy); return im.crop((x, y, x + w, y + h)).resize((W, H), Image.LANCZOS)
def blur_whip(im, k): return im.filter(ImageFilter.BoxBlur(k)) if k > 0 else im
def slide_in(im, p, frm="r"):
    s = 1 - ease(clamp(p * 4)); 
    if s <= 0: return im
    bg = Image.new("RGB", (W, H), (10, 10, 14)); bg.paste(im, (int(W * s * (1 if frm == "r" else -1)), 0)); return blur_whip(bg, int(18 * s))
def plate(kind, t):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im); random.seed(3)
    top, bot = ((10, 16, 34), (34, 30, 52)) if kind == "bus" else ((52, 34, 26), (30, 20, 22))
    for y in range(H): k = y / H; d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * k) for a, b in zip(top, bot)))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o = ImageDraw.Draw(ov)
    for i in range(70 if kind == "bus" else 10):
        x = (random.uniform(-200, W + 200) + t * (260 if kind == "bus" else 0)) % (W + 200) - 100; y = random.uniform(200, 1300); r = random.uniform(18, 60) * (1 if kind == "bus" else 1.8)
        col = random.choice([(255, 170, 70), (255, 210, 140), (120, 160, 255)]) if kind == "bus" else (255, 190, 110)
        o.ellipse((x - r, y - r, x + r, y + r), fill=col + (110,))
    if kind == "bus":
        for i in range(40): x = random.uniform(0, W); y0 = (random.uniform(0, H) + t * 900) % H; o.line([(x, y0), (x - 6, y0 + 60)], fill=(200, 220, 255, 70), width=3)
    im = im.convert("RGBA"); im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(4))); return im.convert("RGB")
def face(clip, t, test=True):
    f = min(47, START[clip] + int(t * FPS)); p = f"frames/{clip}/{f:04d}.png"
    if os.path.exists(p): return Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
    im = plate("bus" if clip.startswith("bus") else "kitchen", t); d = ImageDraw.Draw(im)         # placeholder until the 3D clip exists
    d.ellipse((260, 520, 820, 1240), fill=(224, 170, 140)); d.rectangle((120, 1180, 960, 1920), fill=(236, 90, 150)); U.text(d, (540, 880), clip, 54, (40, 30, 30), True, "mm"); return im
def silhouette(t, slump=0.0, red=0.0):
    im = Image.new("RGB", (W, H), (12, 14, 24)); d = ImageDraw.Draw(im); gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(gl)
    g.polygon([(300, 1000), (780, 1000), (900, 1240), (180, 1240)], fill=(120, 190, 255, 120)); im = Image.alpha_composite(im.convert("RGBA"), gl.filter(ImageFilter.GaussianBlur(40))).convert("RGB"); d = ImageDraw.Draw(im)
    y = int(780 + 90 * slump); d.polygon([(380, y + 420), (700, y + 420), (760, y + 140), (540, y - 40), (320, y + 140)], fill=(6, 6, 10)); d.ellipse((440, y + 20, 640, y + 220), fill=(2, 2, 4))
    d.polygon([(300, 1090), (780, 1090), (860, 1250), (220, 1250)], fill=(36, 44, 66))
    if red > 0:
        pts = [(100, 260), (260, 420), (480, 600), (540, 900)]; n = int(len(pts) * clamp(red))
        for i in range(max(0, n - 1)): d.line([pts[i], pts[i + 1]], fill=U.RED, width=14)
        d.ellipse((60, 220, 150, 310), fill=U.RED)
    return im
def tapring(im, p, xy):
    d = ImageDraw.Draw(im); r = int(40 + 120 * clamp(p)); d.ellipse((xy[0] - r, xy[1] - r, xy[0] + r, xy[1] + r), outline=U.ORANGE, width=14); return im
def dashed(im, pts, color=U.RED, upto=1.0, width=12):
    d = ImageDraw.Draw(im)
    for (a, b) in zip(pts, pts[1:]):
        L = math.dist(a, b); n = int(L / 36); 
        for i in range(n):
            if i / max(1, n) > upto: break
            s, e = i / n, (i + 0.55) / n; d.line([(a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s), (a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e)], fill=color, width=width)
    return im

def shot_frame(s, t, test):
    """Returns the content of shot s at local time t (seconds). p = progress through the shot."""
    i, d_ = s["id"], s["dur"]; p = clamp(t / max(d_, 1e-3))
    if i == "1a": im = U.banner(ease(clamp(t / 0.25)), True); return zoom(im, 1.0 + 0.10 * p, 0.5, 0.6)
    if i == "1b": return zoom(U.banner(1, True), 1.05 + 0.12 * p, 0.78, 0.7)
    if i == "2a": return slide_in(face("bus_hope", t), p * 3, "r")
    if i == "2b":
        im = plate("bus", t + 5); dd = ImageDraw.Draw(im); U.rr(dd, (330, 820, 750, 1180), 40, fill=(30, 30, 50)); U.rr(dd, (350, 840, 730, 1160), 30, fill=(235, 235, 245)); U.text(dd, (540, 1000), "ParcelGo", 54, U.PURPLE, True, "mm"); return zoom(im, 1.0 + 0.04 * p)
    if i == "3a": return U.uk_map(p * 1.2, 0, None, 30)
    if i == "3b": return U.uk_map(1, p * 1.5, "34%", 30)
    if i == "3c": return zoom(face("bus_dread", t), 1.0 + 0.08 * p, 0.5, 0.4)
    if i == "4a": return zoom(face("bus_hope", t + 0.5), 1.0 + 0.05 * p, 0.55, 0.4)
    if i == "4b":
        im = U.banner(1, False); dd = ImageDraw.Draw(im); r = int(70 * (1 - ease(p)) + 16); dd.ellipse((780 - r, 905 - r, 780 + r, 905 + r), fill=U.YELLOW, outline=U.INK, width=4); return zoom(im, 1.0 + 0.1 * p, 0.7, 0.7)
    if i == "5a": return zoom(U.banner(1, False), 1.1 + 0.5 * p, 0.8, 0.72)
    if i == "5b":
        im = zoom(U.banner(1, False), 1.6 + 0.3 * p, 0.8, 0.72); dd = ImageDraw.Draw(im)
        if p > 0.15:
            dd.line([(700, 760), (760, 860), (720, 940), (800, 1040), (760, 1140)], fill=(0, 0, 0), width=10); U.rr(dd, (620, 880, 960, 1060), 28, fill=U.YELLOW); U.text(dd, (790, 970), "CARD", 70, U.INK, True, "mm")
        return im
    if i == "5c":
        im = U.banner(1, False); im = dashed(im, [(780, 905), (900, 700), (1040, 560)], upto=ease(p)); U.text(ImageDraw.Draw(im), (560, 1130), "YOUR CARD", 70, U.RED, True, "mm", stroke=6, stroke_fill=(255, 255, 255)); return zoom(im, 1.0 + 0.1 * p)
    if i == "6a": return tapring(zoom(U.banner(1, False), 1.2 + 0.2 * p, 0.8, 0.72), p, (840, 880))
    if i == "6b": return slide_in(U.parcelgo_page(0), p * 3, "r")
    if i == "7a": return zoom(U.parcelgo_page(p * 0.66), 1.0 + 0.1 * p, 0.5, 0.45)
    if i == "7b":
        im = U.parcelgo_page(0.66 + 0.34 * p); return U.glow_box(im, im.boxes[2], pulse=p) if p > 0.2 else im
    if i == "8a":
        im = U.parcelgo_page(1, paid=True); return zoom(im, 1.0 + 0.2 * p, 0.5, 0.8)
    if i == "8b": return zoom(silhouette(t, 0, ease(p)), 1.25 - 0.25 * p, 0.5, 0.5)
    if i == "8c": return zoom(face("bus_dread", t + 0.3), 1.0 + 0.1 * p, 0.5, 0.4)
    if i in ("9a", "9b"):
        base = Image.new("RGB", (W, H), (12, 12, 18)); f = face("bus_dread", t + 0.4).transpose(Image.FLIP_LEFT_RIGHT).point(lambda v: int(v * 0.35)); im = Image.blend(base, f, 0.6)
        return zoom(im, 1.0 + 0.06 * (p if i == "9b" else p * 0.3))
    if i == "10a":
        im = plate("kitchen", t); dd = ImageDraw.Draw(im); dd.ellipse((780, 300, 1000, 520), fill=(250, 245, 230), outline=(40, 30, 30), width=10); U.text(dd, (890, 410), "10:12", 64, (30, 20, 20), True, "mm"); return zoom(im, 1.0 + 0.05 * p)
    if i == "10b":
        im = plate("kitchen", t + 2); dd = ImageDraw.Draw(im); U.rr(dd, (0, 1000, W, 1250), 0, fill=(70, 50, 40)); cc = U.call_card().resize((380, 676)); im.paste(cc, (350, 520)); return slide_in(im, p * 2, "l")
    if i == "11a": return zoom(face("kit_dread", t), 1.0 + 0.1 * p, 0.5, 0.4)
    if i == "11b":
        im = U.call_card(); im = dashed(im, [(100, 1300), (300, 1050), (540, 760)], upto=ease(p)); U.text(ImageDraw.Draw(im), (540, 940), "•••• •••• ••••", 80, (255, 255, 255), True, "mm"); return zoom(im, 1.0 + 0.1 * p)
    if i == "12a": return zoom(U.bank_screen(4200, p > 0.4), 1.0 + 0.1 * p, 0.5, 0.6)
    if i == "12b": return zoom(face("kit_shock", t), 1.0 + 0.1 * p, 0.5, 0.4)
    if i == "12c": return U.bank_screen(4200 * (1 - ease(p)), True)
    if i == "13a":
        im = U.messages_list(0); dd = ImageDraw.Draw(im); gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(gl)
        g.polygon([(540, 460), (760, 540), (740, 800), (540, 960), (340, 800), (320, 540)], fill=(40, 190, 100, int(200 * ease(clamp(p * 2)))))
        im = Image.alpha_composite(im.convert("RGBA"), gl.filter(ImageFilter.GaussianBlur(6))).convert("RGB"); return zoom(im, 1.0 + 0.12 * p)
    if i == "13b": return zoom(face("kit_hope_relief", t), 1.0 + 0.06 * p, 0.5, 0.4)
    if i == "13c": return zoom(U.messages_list(0), 1.0 + 0.15 * p)
    if i == "14a": return U.unknown_folder(p)
    if i == "14b": return zoom(face("kit_soft_relief", t), 1.0 + 0.04 * p, 0.5, 0.4)
    if i == "14c": return zoom(silhouette(t, p, 0), 1.0 + 0.10 * p, 0.5, 0.55)                                  # QC fix: linear slump + push so the end never freezes
    if i == "15a": return zoom(U.messages_list(0), 1.0 + 0.2 * p, 0.85, 0.15)
    if i == "15b": return zoom(U.messages_list(0.6 + 0.4 * p), 1.7 + 0.25 * p, 0.85, 0.12)                     # QC fix: punch-in so the 15a->15b cut reads
    if i == "16a": return zoom(U.settings_card(1 if t < 0.8 else 2 if t < 1.6 else 3, False), 1.0 + 0.08 * p, 0.5, 0.62)   # QC fix: slow push, no frozen holds
    if i == "16b": return U.toggle_closeup(p * 1.3)
    if i == "17a": return tapring(U.shop_app(0), p, (540, 560))
    if i == "17b":
        im = U.shop_app(p); f = face("kit_relief", t).resize((300, 533)).crop((20, 40, 280, 300)); im.paste(f, (740, 800)); return im
    if i == "18a": return U.text_card("iOS 26+", None, p * 2)
    if i == "18b": return zoom(face("kit_relief", t), 1.0 + 0.05 * p, 0.5, 0.4)
    if i == "19a": return zoom(face("kit_soft_relief", t + 0.4), 1.0 + 0.04 * p, 0.5, 0.4)
    if i == "19b": return U.card_back(p, False)
    if i == "19c": return zoom(U.card_back(1, True), 1.0 + 0.25 * p, 0.45, 0.5)
    if i == "20a": return U.comment_box(p * 1.4)
    if i == "20b": return zoom(face("kit_hope", t), 1.0 + 0.06 * p, 0.5, 0.4)
    if i == "21a": return U.share_to_mum(p)
    if i == "21b": return zoom(U.banner(ease(clamp(t / 0.25)), True), 1.0 + 0.1 * p, 0.5, 0.6)
    raise KeyError(i)

def caption_at(t):
    c = [x for x in CAPS if x["start"] <= t < x["end"]]; return c[-1] if c else None
def frame(g, test=False):
    t = g / FPS; s = next(x for x in SHOTS if x["start"] <= t < x["end"]) if t < SHOTS[-1]["end"] else SHOTS[-1]
    im = shot_frame(s, t - s["start"], test).convert("RGB"); im = U.corner_tag(im); c = caption_at(t)
    if c: im = U.caption(im, c["words"], c["star"], (t - c["start"]) / 0.08)
    return im

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--test", action="store_true"); ap.add_argument("--range", nargs=2, type=int); ap.add_argument("--assemble", action="store_true"); a = ap.parse_args()
    if a.test:
        cw, ch, cols = 216, 384, 10; rows = math.ceil(len(SHOTS) / cols); S = Image.new("RGB", (cols * (cw + 6) + 6, rows * (ch + 24) + 6), (50, 50, 60)); dd = ImageDraw.Draw(S)
        for k, s in enumerate(SHOTS):
            g = int((s["start"] + s["dur"] * 0.55) * FPS); im = frame(g, True).resize((cw, ch)); x, y = 6 + (k % cols) * (cw + 6), 6 + (k // cols) * (ch + 24); S.paste(im, (x, y)); dd.text((x + 4, y + ch + 3), f'{s["id"]}  {s["dur"]:.1f}s', fill=(255, 255, 255))
        os.makedirs("docs", exist_ok=True); S.save("docs/storyboard_preview.png"); print("docs/storyboard_preview.png", len(SHOTS), "shots")
    elif a.range:
        os.makedirs("out", exist_ok=True)
        for g in range(a.range[0], min(a.range[1], TOTAL)):
            p = f"out/{g:05d}.jpg"
            if not os.path.exists(p): frame(g).save(p, quality=92)
        print("composed", a.range)
    elif a.assemble:
        os.makedirs("final", exist_ok=True)
        for name, aud in (("with_pad", "audio/mix_with_pad.wav"), ("voice_fx", "audio/mix_voice_fx.wav")):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "24", "-i", "out/%05d.jpg", "-i", aud, "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", f"final/phoneverse_fix12_{name}.mp4"], check=True)
        print("final/ written")
