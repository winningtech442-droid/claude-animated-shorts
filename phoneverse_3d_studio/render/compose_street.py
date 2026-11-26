"""compose_street.py: rendered street frames -> 1080x1920 frames with ONE caption system -> mp4 with the final mix.
Caption rules (studio standards): one line of 1-3 words (16 characters max), Inter Black ~88 px, white with a black outline and
shadow, the line's key word in yellow, the word being spoken pops slightly; centred at 70% of the height. The swear is shown as
"%@#!" (never typed out), matching the bleep.
  .venv/bin/python render/compose_street.py --frames 0 718      # caption every frame -> build/street_out/
  .venv/bin/python render/compose_street.py --encode 0 718      # -> final/cheers_biscuit_0-30s.mp4 (audio = final mix)
"""
import argparse, json, os, re, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
EP = os.path.join(ROOT, "..", "drafts", "phoneverse-found-text", "audio", "out")
ap = argparse.ArgumentParser(); ap.add_argument("--frames", nargs=2, type=int); ap.add_argument("--encode", nargs=2, type=int)
ap.add_argument("--src", default="build/street"); ap.add_argument("--dst", default="build/street_out")
a = ap.parse_args()
FPS, W, H = 24, 1080, 1920
FONT = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", 88)
KEY = {"L01": "nicking", "L02": "judge", "L03": "Oxford", "L04": "sorry", "L05": "alright", "L06": "OFF", "L07": "go",
       "L08": "no", "L09": "got", "L10": "that", "L11": "THAT", "L12": "NOT", "L13": "fridge", "L14": "ME", "L15": "Fine",
       "L16": "Hong", "L17": "spare", "L18": "thick"}

def chunks():
    words = json.load(open(os.path.join(EP, "words.json"))); tl = {r["id"]: r for r in json.load(open(os.path.join(EP, "timeline.json")))}
    out = []
    for lid, r in tl.items():
        # display words come from the caption text (keeps capitals/punctuation); timings from the measured words
        disp = r["text"].replace("f***", "%@#!").replace('"', "").split()
        ws = [w for w in words if w["line"] == lid and (w["word"][:1].isalnum() or w["word"] == "[bleep]")]
        n = min(len(disp), len(ws))
        if n == 0: continue
        if len(disp) != len(ws):  # fall back to spreading the display words over the line's time
            t0, t1 = r["start"], r["end"]; ws = [dict(start=t0 + (t1 - t0) * i / len(disp), end=t0 + (t1 - t0) * (i + 1) / len(disp)) for i in range(len(disp))]; n = len(disp)
        i = 0
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
    key = KEY.get(c["line"], "").lower()
    d = ImageDraw.Draw(img); sizes = []
    for k, w in enumerate(c["words"]):
        speaking = c["times"][k][0] <= t < c["times"][k][1] + 0.05
        f = ImageFont.truetype(FONT.path, 96 if speaking else 88); sizes.append((w, f, speaking))
    gap = 22; total = sum(d.textlength(w, font=f) for w, f, _ in sizes) + gap * (len(sizes) - 1)
    x = (W - total) / 2; y = int(H * 0.70)
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(shadow)
    for w, f, _ in sizes:
        sd.text((x + 5, y + 7), w, font=f, fill=(0, 0, 0, 170), anchor="lm"); x += d.textlength(w, font=f) + gap
    img = Image.alpha_composite(img.convert("RGBA"), shadow.filter(ImageFilter.GaussianBlur(5))); d = ImageDraw.Draw(img)
    x = (W - total) / 2
    for w, f, speaking in sizes:
        bare = re.sub(r"[^A-Za-z']", "", w).lower()
        col = (255, 214, 0) if key and bare == key.lower() else (255, 255, 255)
        d.text((x, y), w, font=f, fill=col, anchor="lm", stroke_width=7, stroke_fill=(0, 0, 0)); x += d.textlength(w, font=f) + gap
    return img.convert("RGB")

if a.frames:
    os.makedirs(a.dst, exist_ok=True)
    for f in range(*a.frames):
        src = os.path.join(a.src, f"{f:04d}.png"); dst = os.path.join(a.dst, f"{f:04d}.png")
        if not os.path.exists(src) or os.path.exists(dst): continue
        img = Image.open(src).convert("RGB").resize((W, H), Image.LANCZOS)
        caption(img, f / FPS).save(dst)
if a.encode:
    f0, f1 = a.encode; os.makedirs("final", exist_ok=True); out = f"final/cheers_biscuit_{f0 / FPS:.0f}-{f1 / FPS:.0f}s.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-start_number", str(f0), "-i", os.path.join(a.dst, "%04d.png"),
                    "-ss", f"{f0 / FPS:.3f}", "-t", f"{(f1 - f0) / FPS:.3f}", "-i", os.path.join(EP, "final_mix.wav"),
                    "-frames:v", str(f1 - f0), "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                    "-af", "volume=-0.6dB",  # AAC overshoots ~0.5 dB: keeps the true peak under -1 dBTP
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    print("->", out)
