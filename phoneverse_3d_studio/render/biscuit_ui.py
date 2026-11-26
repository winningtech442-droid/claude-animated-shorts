"""biscuit_ui.py: phone and laptop screens for "Cheers, Biscuit" (PIL, 1080x1920 portrait unless noted).
Props only: no logos, no real brands or domains, and her number is from Ofcom's drama range (07700 900xxx).
Each function returns an RGB PIL image; animated ones take progress values in 0..1."""
import math
from PIL import Image, ImageDraw, ImageFilter
from pvui import font, rr, text, clamp, ease, INK, PAPER, BLUE, GREEN, RED, YELLOW

W, H = 1080, 1920
CLOCK = "21:14"
NUMBER = "07700 900461"
LINK = "locate-my-device-…"


def _grad(c0, c1):
    im = Image.new("RGB", (W, H), c0); d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        k = y / H; d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * k) for a, b in zip(c0, c1)))
    return im, d


def _status(d, dark=True):
    c = (255, 255, 255) if dark else INK
    text(d, (72, 128), CLOCK, 40, c, True, "la")
    for i in range(4):
        h = 12 + i * 9; x = 760 + i * 22; d.rectangle((x, 166 - h, x + 14, 166), fill=c)
    rr(d, (900, 134, 980, 166), 8, outline=c, width=4); rr(d, (906, 140, 960, 160), 4, fill=c)


def _lock(c0=(18, 60, 70), c1=(40, 150, 140), day="Tuesday"):
    im, d = _grad(c0, c1); _status(d)
    text(d, (540, 225), CLOCK, 190, (255, 255, 255), True, "ma"); text(d, (540, 415), day, 44, (225, 240, 240), False, "ma")
    return im, d


def new_lock():
    """her NEW phone (mint case), plain lock screen"""
    return _lock()[0]


def found_text(p=1.0, tap=0.0):
    """the fake 'your lost phone has been found' text slides onto her new phone's lock screen"""
    im, d = _lock(); s = ease(clamp(p)); cy = int(800 + (1 - s) * 900); box = (60, cy - 230, 1020, cy + 230)
    rr(d, (box[0] + 8, box[1] + 14, box[2] + 8, box[3] + 14), 50, fill=(0, 0, 0)); rr(d, box, 50, fill=(255, 255, 255))
    rr(d, (box[0] + 36, box[1] + 36, box[0] + 132, box[1] + 132), 26, fill=GREEN); text(d, (box[0] + 84, box[1] + 84), "✉", 60, (255, 255, 255), True, "mm")
    text(d, (box[0] + 160, box[1] + 50), "+44 7700 900118", 46, INK, True); text(d, (box[2] - 40, box[1] + 56), "now", 36, (120, 120, 130), False, "ra")
    text(d, (box[0] + 40, box[1] + 175), "Your lost phone has been", 54, INK, True)
    text(d, (box[0] + 40, box[1] + 245), "found. Tap to see where:", 54, INK, True)
    lk = (box[0] + 40, box[1] + 330, box[0] + 700, box[1] + 410); text(d, (lk[0], lk[1] + 40), LINK, 48, BLUE, True, "lm")
    if tap > 0:
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rounded_rectangle((lk[0] - 20, lk[1] - 10, lk[2] + 20, lk[3] + 10), 30, outline=(255, 150, 30, int(255 * clamp(tap))), width=10)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    return im


def fake_login(typed=0.0, signed=0.0):
    """the fake sign-in page the link opens (generic, no logo). typed: password dots fill in; signed: green 'Signed in' card"""
    im = Image.new("RGB", (W, H), (250, 250, 252)); d = ImageDraw.Draw(im); _status(d, False)
    rr(d, (60, 170, 1020, 250), 40, fill=(232, 232, 238)); text(d, (110, 210), LINK, 38, (90, 90, 100), False, "lm")
    d.ellipse((440, 330, 640, 530), fill=(225, 228, 236)); rr(d, (500, 420, 580, 490), 10, fill=(120, 124, 140)); d.arc((505, 370, 575, 450), 180, 360, fill=(120, 124, 140), width=14)
    text(d, (540, 600), "Sign in to see", 66, INK, True, "ma"); text(d, (540, 680), "where your phone is", 66, INK, True, "ma")
    rr(d, (110, 820, 970, 930), 24, outline=(200, 200, 210), width=4, fill=(255, 255, 255)); text(d, (150, 875), "Email", 44, (150, 150, 160), False, "lm")
    rr(d, (110, 970, 970, 1080), 24, outline=(30, 120, 255) if typed > 0 else (200, 200, 210), width=4, fill=(255, 255, 255))
    n = int(round(10 * clamp(typed)))
    text(d, (150, 1025), "•" * n if n else "Password", 54 if n else 44, INK if n else (150, 150, 160), n > 0, "lm")
    rr(d, (110, 1130, 970, 1240), 55, fill=BLUE); text(d, (540, 1185), "Sign in", 54, (255, 255, 255), True, "mm")
    if signed > 0:
        s = ease(clamp(signed)); box = (120, int(1500 - 60 * s), 960, int(1660 - 60 * s))
        rr(d, box, 40, fill=GREEN); text(d, ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2), "✓  Signed in", 64, (255, 255, 255), True, "mm")
    return im


def lost_lock(flash=0.0):
    """her OLD phone in Lost Mode: the lock screen shows her number (that's how the scammers got it)"""
    im, d = _lock((30, 12, 30), (110, 40, 80), "Saturday")
    box = (80, 640, 1000, 1080); rr(d, box, 46, fill=(255, 255, 255))
    text(d, (540, 720), "This phone has been lost.", 54, INK, True, "ma")
    text(d, (540, 810), "Please call:", 50, (90, 90, 100), False, "ma")
    nb = (170, 880, 910, 990)
    if flash > 0:
        rr(d, (nb[0] - 14, nb[1] - 10, nb[2] + 14, nb[3] + 10), 30, fill=(255, int(214 - 40 * flash), 10))
    text(d, (540, 935), NUMBER, 76, INK, True, "mm")
    return im


def activation_lock(p=1.0):
    """locked to its owner: a padlock and 'needs the owner's password' (shown as an outcome only)"""
    im = Image.new("RGB", (W, H), (8, 8, 14)); d = ImageDraw.Draw(im); s = ease(clamp(p))
    cx, cy, r = 540, 760, int(170 * (0.8 + 0.2 * s))
    g = Image.new("RGBA", im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(g); gd.ellipse((cx - 330, cy - 330, cx + 330, cy + 330), fill=(255, 70, 70, int(90 * s)))
    im = Image.alpha_composite(im.convert("RGBA"), g.filter(ImageFilter.GaussianBlur(60))).convert("RGB"); d = ImageDraw.Draw(im)
    d.arc((cx - r * 0.75, cy - r * 1.55, cx + r * 0.75, cy), 180, 360, fill=(255, 255, 255), width=int(r * 0.2))
    rr(d, (cx - r, cy - r * 0.35, cx + r, cy + r * 1.1), int(r * 0.22), fill=(255, 255, 255)); d.ellipse((cx - 28, cy + 70, cx + 28, cy + 126), fill=(8, 8, 14))
    text(d, (540, 1090), "Locked to its owner", 66, (255, 255, 255), True, "ma")
    text(d, (540, 1180), "Owner's password needed", 46, (200, 200, 210), False, "ma")
    return im


def hello(p=0.0):
    """the setup screen of a wiped, unlocked phone (outcome only): 'Hello' fading through a few languages"""
    im = Image.new("RGB", (W, H), (250, 250, 252)); d = ImageDraw.Draw(im)
    words = ["Hello", "Hola", "Bonjour", "Hallo", "Ciao", "Hello"]
    x = clamp(p) * (len(words) - 1); i = int(min(x, len(words) - 2)); k = x - i
    for j, a in ((i, 1 - k), (i + 1, k)):
        if a > 0.02:
            ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(ov).text((540, 820), words[j], font=font(170, False), fill=(20, 20, 28, int(255 * a)), anchor="mm")
            im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(im); text(d, (540, 1500), "Swipe up to set up", 44, (120, 120, 130), False, "ma")
    return im


def laptop(p=0.0):
    """the scammer's laptop (1600x1000): a dark list of phone entries, one row highlighted red (outcome only, no how-to)"""
    im = Image.new("RGB", (1600, 1000), (14, 10, 16)); d = ImageDraw.Draw(im)
    rr(d, (0, 0, 1600, 80), 0, fill=(40, 12, 16)); text(d, (40, 40), "DEVICES  ·  LOT 47", 40, (255, 120, 110), True, "lm")
    for i in range(9):
        y = 120 + i * 95; hot = i == 3
        rr(d, (40, y, 1560, y + 80), 14, fill=(120, 20, 24) if hot else (30, 24, 30))
        text(d, (80, y + 40), f"#{4710 + i * 7}", 36, (255, 255, 255) if hot else (170, 160, 170), True, "lm")
        text(d, (330, y + 40), ["locked", "locked", "texted", "TEXT SENT", "locked", "texted", "locked", "locked", "texted"][i], 36,
             (255, 230, 120) if hot else (150, 140, 150), hot, "lm")
        text(d, (1520, y + 40), "07700 900461" if hot else "07700 900···", 34, (255, 255, 255) if hot else (120, 110, 120), False, "rm")
    return im


def box_label():
    """the cardboard box's shipping label + the red HONG KONG stamp (1024x640)"""
    im = Image.new("RGB", (1024, 640), (176, 132, 86)); d = ImageDraw.Draw(im)
    for y in range(0, 640, 7): d.line([(0, y), (1024, y)], fill=(170 + (y * 13) % 11, 127 + (y * 7) % 9, 82))
    rr(d, (60, 60, 560, 330), 10, fill=(245, 242, 232)); text(d, (90, 110), "FRAGILE", 52, (40, 40, 40), True, "lm")
    text(d, (90, 190), "ELECTRONICS", 40, (60, 60, 60), False, "lm"); text(d, (90, 255), "QTY 212", 40, (60, 60, 60), False, "lm")
    st = Image.new("RGBA", (900, 260), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rounded_rectangle((10, 10, 890, 250), 24, outline=(200, 25, 30, 235), width=16)
    sd.text((450, 130), "HONG KONG", font=font(112, True), fill=(200, 25, 30, 235), anchor="mm")
    st = st.rotate(-8, expand=True, resample=Image.BICUBIC)
    im = im.convert("RGBA"); im.alpha_composite(st, (40, 330)); return im.convert("RGB")


if __name__ == "__main__":  # write a preview sheet of every screen
    import os, sys
    out = sys.argv[1] if len(sys.argv) > 1 else "build/ui_preview.png"
    shots = [new_lock(), found_text(1.0, 0.6), fake_login(0.6), fake_login(1.0, 1.0), lost_lock(1.0), activation_lock(), hello(0.4)]
    sheet = Image.new("RGB", (len(shots) * 270, 480), (0, 0, 0))
    for i, s in enumerate(shots): sheet.paste(s.resize((270, 480)), (i * 270, 0))
    lap = laptop().resize((480, 300)); lab = box_label().resize((480, 300))
    full = Image.new("RGB", (sheet.width, 480 + 300), (30, 30, 30)); full.paste(sheet, (0, 0)); full.paste(lap, (0, 480)); full.paste(lab, (500, 480))
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True); full.save(out); print("->", out)
