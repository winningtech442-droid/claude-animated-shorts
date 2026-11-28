"""compose_part2.py: Part 2 frames -> 1080x1920 with the episode's overlays -> mp4 with the final mix.
  - captions: the same one-line system as Part 1 (compose_street.py): Inter Black 88 px, key word yellow, at 70% height
  - "PART 2" tag top-left for the first 2 s (same style as Part 1's "3 MONTHS LATER")
  - the CLICKS TO ERASE counter in the top third: appears at 3, ticks 3 -> 2 -> 1, freezes on 1 and cracks when he's kicked out
  - a short glitch over each dive cut (her phone <-> his laptop), and a white flash on the screenshot
Times come from the same anchors as part2_scene.py and sfx_part2.py (the voice timeline + word times).
  .venv/bin/python render/compose_part2.py --frames 0 1700
  .venv/bin/python render/compose_part2.py --encode 0 1700 --name final/cheers_biscuit_part2.mp4
"""
import argparse, json, math, os, random, re, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
EP = os.path.join(ROOT, "..", "drafts", "phoneverse-cheers-biscuit-part2", "audio", "out")
ap = argparse.ArgumentParser(); ap.add_argument("--frames", nargs=2, type=int); ap.add_argument("--encode", nargs=2, type=int)
ap.add_argument("--src", default="build/p2"); ap.add_argument("--dst", default="build/p2_out"); ap.add_argument("--name", default=None)
ap.add_argument("--redo", action="store_true", help="overwrite frames already composed")
a = ap.parse_args()
FPS, W, H = 24, 1080, 1920
BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FONT = ImageFont.truetype(BLACK, 88); SMALL = ImageFont.truetype(BLACK, 52)
KEY = {"L01": "sorry", "L02": "code", "L03": "point", "L04": "devices", "L05": "do", "L06": "nicked", "L07": "camera", "L08": "problem",
       "L09": "spare", "L10": "new", "L11": "off", "L12": "on", "L13": "apple", "L14": "clicks", "L15": "in", "L16": "biscuit", "L17": "gone",
       "L18": "out", "L19": "website", "L20": "sure", "L21": "browsers", "L22": "press", "L23": "what", "L24": "biscuit", "L25": "jess",
       "L26": "screenshot", "L27": "biscuit"}
TL = {r["id"]: r for r in json.load(open(os.path.join(EP, "timeline.json")))}
S = {k: v["start"] for k, v in TL.items()}; E = {k: v["end"] for k, v in TL.items()}
WORDS = json.load(open(os.path.join(EP, "words.json")))
def Wd(line, word, nth=0):
    hits = [x for x in WORDS if x["line"] == line and x["word"].lower().strip(".,!?'\"…") == word]
    return hits[nth]["start"]
# the same anchors as part2_scene.py
T_DEN1, T_FLAT2, T_DEN2 = S["L08"] - 0.25, S["L10"] - 0.3, S["L20"] - 0.3
T_CNT, T_CLICK2, T_CLICK3 = E["L08"] + 0.16, Wd("L09", "parts") + 0.25, Wd("L20", "sure", 1) - 0.05
T_PRESS = E["L22"] + 0.2; T_KICK = T_PRESS + 0.15; T_TEXT = S["L25"] - 0.5; T_SHOT = Wd("L26", "screenshot") + 0.35
T_END = E["L27"] + 1.6
GLITCH = [T_DEN1, T_FLAT2, T_DEN2]
TAG = (0.0, 2.0, "PART 2")


def chunks():
    out = []
    for lid, r in TL.items():
        disp = r["text"].replace('"', "").split()
        ws = [w for w in WORDS if w["line"] == lid and w["word"][:1].isalnum()]
        if not disp: continue
        if len(disp) != len(ws):
            t0, t1 = r["start"], r["end"]; ws = [dict(start=t0 + (t1 - t0) * i / len(disp), end=t0 + (t1 - t0) * (i + 1) / len(disp)) for i in range(len(disp))]
        n = len(disp); i = 0
        while i < n:
            grp = [disp[i]]; j = i + 1
            while j < n and len(grp) < 3 and len(" ".join(grp + [disp[j]])) <= 16 and not re.search(r"[.!?…]$", grp[-1]): grp.append(disp[j]); j += 1
            out.append(dict(line=lid, words=grp, times=[(ws[k]["start"], ws[k]["end"]) for k in range(i, j)], t0=ws[i]["start"], t1=ws[j - 1]["end"] + 0.18))
            i = j
    out.sort(key=lambda c: c["t0"])
    for c, nx in zip(out, out[1:]): c["t1"] = min(c["t1"], nx["t0"])
    return out
CH = chunks()


def caption(img, t):
    c = next((c for c in CH if c["t0"] - 0.03 <= t < c["t1"]), None)
    if not c: return img
    key = KEY.get(c["line"], "")
    d = ImageDraw.Draw(img); sizes = []
    for k, w in enumerate(c["words"]):
        speaking = c["times"][k][0] <= t < c["times"][k][1] + 0.05
        sizes.append((w, ImageFont.truetype(BLACK, 96 if speaking else 88)))
    gap = 22; total = sum(d.textlength(w, font=f) for w, f in sizes) + gap * (len(sizes) - 1)
    x = (W - total) / 2; y = int(H * 0.70)
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(shadow)
    for w, f in sizes:
        sd.text((x + 5, y + 7), w, font=f, fill=(0, 0, 0, 170), anchor="lm"); x += d.textlength(w, font=f) + gap
    img = Image.alpha_composite(img.convert("RGBA"), shadow.filter(ImageFilter.GaussianBlur(5))); d = ImageDraw.Draw(img)
    x = (W - total) / 2
    for w, f in sizes:
        bare = re.sub(r"[^A-Za-z']", "", w).lower()
        col = (255, 214, 0) if key and bare == key else (255, 255, 255)
        d.text((x, y), w, font=f, fill=col, anchor="lm", stroke_width=7, stroke_fill=(0, 0, 0)); x += d.textlength(w, font=f) + gap
    return img.convert("RGB")


def tag(img, t):
    if not (TAG[0] <= t < TAG[1]): return img
    k = min(1.0, (t - TAG[0]) / 0.2 + 1.0 if TAG[0] == 0 else (t - TAG[0]) / 0.2, (TAG[1] - t) / 0.2)
    img = img.convert("RGBA"); ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    w = d.textlength(TAG[2], font=SMALL); x, y = 60, int(H * 0.115)
    d.rounded_rectangle((x - 26, y - 20, x + w + 26, y + 74), 22, fill=(0, 0, 0, int(170 * k))); d.text((x, y), TAG[2], font=SMALL, fill=(255, 255, 255, int(255 * k)))
    return Image.alpha_composite(img, ov).convert("RGB")


CRACK = None
def _crack_lines(cx, cy):
    r = random.Random(5); lines = []
    for k in range(9):
        a_ = k * 2 * math.pi / 9 + r.uniform(-0.25, 0.25); pts = [(cx, cy)]; x, y = cx, cy
        for s in range(r.randint(3, 5)):
            L = r.uniform(30, 75); a_ += r.uniform(-0.45, 0.45); x += L * math.cos(a_); y += L * math.sin(a_); pts.append((x, y))
        lines.append(pts)
    return lines


def counter(img, t):
    """CLICKS TO ERASE: big flip-digit in a dark rounded card, top third (below the app UI band)"""
    if not (T_CNT <= t < T_TEXT): return img
    global CRACK
    n = 3 if t < T_CLICK2 + 0.07 else 2 if t < T_CLICK3 + 0.08 else 1
    since = t - max([x for x in (T_CNT, T_CLICK2 + 0.07, T_CLICK3 + 0.08) if x <= t])
    pop = 1.0 + 0.18 * math.exp(-since / 0.08) * (since >= 0)
    cracked = t >= T_KICK; shake = 10 * math.exp(-(t - T_KICK) / 0.1) * math.sin((t - T_KICK) * 90) if cracked else 0.0
    fade = min(1.0, (t - T_CNT) / 0.12, (T_TEXT - t) / 0.2)
    cw, ch = 360, 330; cx, cy = W / 2 + shake, int(H * 0.215)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    red = n == 1
    d.rounded_rectangle((cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2), 40, fill=(140, 10, 20, int(215 * fade)) if red else (10, 10, 16, int(200 * fade)),
                        outline=(255, 255, 255, int(90 * fade)), width=4)
    lab = ImageFont.truetype(BLACK, 34); d.text((cx, cy - ch / 2 + 46), "CLICKS TO ERASE", font=lab, fill=(255, 255, 255, int(230 * fade)), anchor="mm")
    big = ImageFont.truetype(BLACK, int(210 * pop)); d.text((cx, cy + 34), str(n), font=big, fill=(255, 214, 0, int(255 * fade)) if not red else (255, 255, 255, int(255 * fade)),
                                                          anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, int(255 * fade)))
    if cracked:
        if CRACK is None: CRACK = _crack_lines(cx + 40, cy + 10)
        grow = min(1.0, (t - T_KICK) / 0.08)
        for pts in CRACK:
            m = max(2, int(len(pts) * grow + 0.999)); seg = [(x + shake, y) for x, y in pts[:m]]
            d.line(seg, fill=(255, 255, 255, int(235 * fade)), width=5); d.line(seg, fill=(0, 0, 0, int(160 * fade)), width=2)
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def glitch(img, t):
    g = max([1 - abs(t - tc) / 0.13 for tc in GLITCH] + [0.0])
    if g <= 0: return img
    r = random.Random(int(t * 1000)); im = img.copy()
    R, G_, B = im.split(); dx = int(28 * g)
    im = Image.merge("RGB", (ImageChops.offset(R, dx, 0), G_, ImageChops.offset(B, -dx, 0)))
    for _ in range(int(14 * g)):    # sliced bands pushed sideways
        y0 = r.randint(0, H - 40); hgt = r.randint(8, 90); band = im.crop((0, y0, W, y0 + hgt))
        im.paste(ImageChops.offset(band, r.randint(-120, 120), 0), (0, y0))
    if g > 0.75:   # the frame right on the cut: mostly static
        nz = Image.effect_noise((W // 4, H // 4), 90).resize((W, H)).convert("RGB")
        im = Image.blend(im, nz, 0.35 * g)
    return im


def flash(img, t):
    if not (T_SHOT <= t < T_SHOT + 0.3): return img
    k = 0.85 * (1 - (t - T_SHOT) / 0.3) ** 1.5
    return Image.blend(img, Image.new("RGB", img.size, (255, 255, 255)), k)


def compose(img, t):
    img = glitch(img, t); img = flash(img, t); img = counter(img, t); img = tag(img, t); return caption(img, t)


if a.frames:
    os.makedirs(a.dst, exist_ok=True)
    for f in range(*a.frames):
        src = os.path.join(a.src, f"{f:04d}.png"); dst = os.path.join(a.dst, f"{f:04d}.png")
        if not os.path.exists(src) or (os.path.exists(dst) and not a.redo): continue
        img = Image.open(src).convert("RGB").resize((W, H), Image.LANCZOS)
        compose(img, f / FPS).save(dst)
if a.encode:
    f0, f1 = a.encode; os.makedirs("final", exist_ok=True); out = a.name or "final/cheers_biscuit_part2.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-start_number", str(f0), "-i", os.path.join(a.dst, "%04d.png"),
                    "-ss", f"{f0 / FPS:.3f}", "-t", f"{(f1 - f0) / FPS:.3f}", "-i", os.path.join(EP, "final_mix.wav"),
                    "-frames:v", str(f1 - f0), "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                    "-af", "volume=-0.6dB",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    print("->", out)
