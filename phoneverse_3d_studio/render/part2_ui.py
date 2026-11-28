"""part2_ui.py: the phone and laptop screens for "Cheers, Biscuit" Part 2 (PIL). Same rules as biscuit_ui.py: props only,
generic look, no logos, no real brands or domains. Phone screens are 1080x1920 portrait; laptop screens are 1600x1000.
Animated screens take progress values in 0..1; the laptop ones also take the cursor position (x, y) in screen pixels."""
import math
from PIL import Image, ImageDraw, ImageFilter
from pvui import font, rr, text, clamp, ease, INK, BLUE, GREEN, RED
from biscuit_ui import _status, _lock, W, H

LW, LH = 1600, 1000
FLAT = (1900, 1500)        # Jess's flat (central London) on the world map
HEATH = (700, 1650)        # the den, near Heathrow
_WORLD = None


# ------------------------------------------------------------------ the map (one big world image, cropped per zoom)
def world():
    global _WORLD
    if _WORLD is not None:
        return _WORLD
    import random
    r = random.Random(7)
    S = 3000
    im = Image.new("RGB", (S, S), (232, 230, 222)); d = ImageDraw.Draw(im)
    for _ in range(46):   # parks
        x, y = r.uniform(0, S), r.uniform(0, S); w, h = r.uniform(60, 220), r.uniform(50, 180)
        d.rounded_rectangle((x, y, x + w, y + h), 30, fill=(196, 222, 182))
    pts = []   # the river: west to east through the middle, with big bends
    for i in range(61):
        x = i * S / 60; y = 1650 + 160 * math.sin(i / 6.0) + 90 * math.sin(i / 2.3 + 1)
        pts.append((x, y))
    d.line(pts, fill=(160, 196, 226), width=46, joint="curve")
    for _ in range(140):  # minor roads
        x, y = r.uniform(0, S), r.uniform(0, S); a = r.uniform(0, math.pi); L = r.uniform(150, 600)
        d.line((x, y, x + L * math.cos(a), y + L * math.sin(a)), fill=(255, 255, 255), width=9)
    for k in range(9):    # main roads radiating from the centre
        a = k * math.pi / 4.5 + 0.2
        d.line((FLAT[0], FLAT[1], FLAT[0] + 2600 * math.cos(a), FLAT[1] + 2600 * math.sin(a)), fill=(250, 214, 140), width=20)
    d.line((FLAT[0], FLAT[1], HEATH[0], HEATH[1]), fill=(250, 214, 140), width=24)   # the motorway out west
    hx, hy = HEATH   # the airport: two runways + terminals, the den is a shed just north of it
    for dy in (-70, 70):
        d.rectangle((hx - 320, hy + 160 + dy - 14, hx + 320, hy + 160 + dy + 14), fill=(150, 150, 158))
    d.rectangle((hx - 120, hy + 180, hx + 120, hy + 216), fill=(185, 185, 195))
    d.rectangle((hx - 26, hy - 18, hx + 26, hy + 18), fill=(170, 160, 150))
    text(d, (hx, hy + 290), "HEATHROW", 64, (110, 110, 120), True, "mm")
    text(d, (FLAT[0] + 40, FLAT[1] + 260), "LONDON", 90, (120, 120, 130), True, "mm")
    _WORLD = im
    return im


def map_crop(center, half_w, out_w, out_h):
    """a crop of the world map centred on `center`, `half_w` world pixels either side, resized to out_w x out_h"""
    hw = half_w; hh = half_w * out_h / out_w; cx, cy = center
    return world().crop((int(cx - hw), int(cy - hh), int(cx + hw), int(cy + hh))).resize((out_w, out_h), Image.LANCZOS)


def _pin(d, x, y, color, s=1.0, ring=0.0):
    if ring > 0:
        rad = 40 + 90 * ring
        d.ellipse((x - rad, y - rad, x + rad, y + rad), outline=color, width=max(2, int(8 * (1 - ring))))
    d.ellipse((x - 34 * s, y - 34 * s, x + 34 * s, y + 34 * s), fill=(255, 255, 255))
    d.ellipse((x - 24 * s, y - 24 * s, x + 24 * s, y + 24 * s), fill=color)


def map_dive(z=0.0, pulse=0.0):
    """her phone during dive 1: the map zooms from all of London to the shed near Heathrow (z 0 -> 1)"""
    k = ease(clamp(z))
    c0 = ((FLAT[0] + HEATH[0]) / 2, (FLAT[1] + HEATH[1]) / 2); half0 = 720
    half = half0 * (80 / half0) ** k                         # log zoom: 720 -> 80 world px
    s0 = W / (2 * half0); sx = W / (2 * half)
    p0 = (W / 2 + (HEATH[0] - c0[0]) * s0, H / 2 + (HEATH[1] - c0[1]) * s0)    # the pin's place on screen at z=0
    px, py = p0[0] + (W / 2 - p0[0]) * k, p0[1] + (H * 0.45 - p0[1]) * k       # ... glides to the middle as we zoom in on it
    c = (HEATH[0] - (px - W / 2) / sx, HEATH[1] - (py - H / 2) / sx)
    im = map_crop(c, half, W, H); d = ImageDraw.Draw(im)
    _pin(d, px, py, RED, 1.0 + 1.2 * k, pulse)
    if k < 0.5:
        fx, fy = W / 2 + (FLAT[0] - c[0]) * sx, H / 2 + (FLAT[1] - c[1]) * sx
        _pin(d, fx, fy, BLUE, 0.8)
    _status(d, False)
    return im


def phone_map(pulse=0.0):
    """her phone held up to the camera on 'Oi, camera': the London map, a red pin out west"""
    return map_dive(0.0, pulse)


# ------------------------------------------------------------------ her phone
def _settings_page(title):
    im = Image.new("RGB", (W, H), (242, 242, 247)); d = ImageDraw.Draw(im); _status(d, False)
    text(d, (70, 250), "‹ Back", 44, BLUE, False, "lm"); text(d, (540, 360), title, 74, INK, True, "mm")
    return im, d


def change_password(typed=0.0, done=0.0):
    """Settings > Sign-In & Security > Change Password: a long new password fills in as dots"""
    im, d = _settings_page("Change Password")
    n = int(round(18 * clamp(typed)))
    for k, (lab, y) in enumerate((("New password", 560), ("Verify", 760))):
        rr(d, (70, y, 1010, y + 150), 30, fill=(255, 255, 255), outline=(30, 120, 255) if (k == 0 and 0 < typed < 1) else None, width=6)
        text(d, (110, y + 42), lab, 36, (130, 130, 140), False, "lm")
        m = n if k == 0 else max(0, n - 6)
        if m: text(d, (110, y + 102), "•" * m, 56, INK, True, "lm")
    rr(d, (70, 1000, 1010, 1140), 70, fill=BLUE if n >= 18 else (170, 190, 230))
    text(d, (540, 1070), "Change", 54, (255, 255, 255), True, "mm")
    return im


def remove_devices(gone=0.0, tap=0.0):
    """after the change: 'Remove Other Devices' - her other sign-ins vanish off the list"""
    im, d = _settings_page("Password changed")
    rows = [("Old iPhone", "offline"), ("Web browser", "signed in · just now"), ("Laptop", "last week")]
    for i, (a, b) in enumerate(rows):
        k = clamp(gone * 3 - i * 0.6)
        if k >= 1:
            continue
        y = 520 + i * 170; x = int(70 - 900 * ease(k))
        rr(d, (x, y, x + 940, y + 140), 30, fill=(255, 255, 255)); text(d, (x + 50, y + 50), a, 46, INK, True, "lm")
        text(d, (x + 50, y + 104), b, 32, (140, 140, 150), False, "lm")
    if gone >= 0.98:
        text(d, (540, 700), "✓  Other devices signed out", 46, GREEN, True, "mm")
    rr(d, (70, 1150, 1010, 1290), 70, fill=(255, 90, 80) if tap > 0 else RED)
    if tap > 0:
        rr(d, (60, 1140, 1020, 1300), 76, outline=(255, 200, 80), width=10)
    text(d, (540, 1220), "Remove Other Devices", 50, (255, 255, 255), True, "mm")
    return im


def signout_all(hover=0.0, press=0.0):
    """the account settings page (in her browser): 'Sign Out Of All Browsers' - her thumb hovers, then presses"""
    im = Image.new("RGB", (W, H), (250, 250, 252)); d = ImageDraw.Draw(im); _status(d, False)
    rr(d, (60, 170, 1020, 250), 40, fill=(232, 232, 238)); text(d, (110, 210), "account settings", 38, (90, 90, 100), False, "lm")
    text(d, (90, 380), "Settings", 80, INK, True, "lm")
    for i, lab in enumerate(("Storage", "Your devices", "Data recovery")):
        y = 500 + i * 140; rr(d, (60, y, 1020, y + 120), 26, fill=(255, 255, 255)); text(d, (110, y + 60), lab, 44, INK, False, "lm")
    b = (60, 1020, 1020, 1180)
    if hover > 0:
        g = Image.new("RGBA", im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        gd.rounded_rectangle((b[0] - 30, b[1] - 30, b[2] + 30, b[3] + 30), 90, fill=(255, 60, 60, int(110 * hover)))
        im = Image.alpha_composite(im.convert("RGBA"), g.filter(ImageFilter.GaussianBlur(24))).convert("RGB"); d = ImageDraw.Draw(im)
    s = 1 - 0.04 * clamp(press)
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2; hw, hh = (b[2] - b[0]) / 2 * s, (b[3] - b[1]) / 2 * s
    rr(d, (cx - hw, cy - hh, cx + hw, cy + hh), 80, fill=(200, 30, 40) if press > 0 else RED)
    text(d, (cx, cy), "Sign Out Of All Browsers", 52, (255, 255, 255), True, "mm")
    if press >= 1:
        text(d, (540, 1300), "✓  Signed out everywhere", 46, GREEN, True, "mm")
    return im


def threat_text(p=1.0):
    """his text lands on her lock screen"""
    im, d = _lock(); s = ease(clamp(p)); cy = int(760 + (1 - s) * 700); box = (60, cy - 190, 1020, cy + 190)
    rr(d, (box[0] + 8, box[1] + 14, box[2] + 8, box[3] + 14), 50, fill=(0, 0, 0)); rr(d, box, 50, fill=(255, 255, 255))
    rr(d, (box[0] + 36, box[1] + 36, box[0] + 132, box[1] + 132), 26, fill=GREEN); text(d, (box[0] + 84, box[1] + 84), "✉", 60, (255, 255, 255), True, "mm")
    text(d, (box[0] + 160, box[1] + 50), "Unknown", 46, INK, True); text(d, (box[2] - 40, box[1] + 56), "now", 36, (120, 120, 130), False, "ra")
    text(d, (box[0] + 40, box[1] + 190), "Nice try.", 56, INK, True)
    text(d, (box[0] + 40, box[1] + 270), "We know where Jess lives.", 56, INK, True)
    return im


# ------------------------------------------------------------------ his laptop
def _cursor(d, xy):
    if xy is None:
        return
    x, y = xy
    pts = [(x, y), (x, y + 46), (x + 12, y + 35), (x + 21, y + 55), (x + 29, y + 51), (x + 20, y + 32), (x + 36, y + 32)]
    d.polygon(pts, fill=(255, 255, 255), outline=(0, 0, 0))


def _lap(title=None):
    im = Image.new("RGB", (LW, LH), (24, 24, 30)); d = ImageDraw.Draw(im)
    rr(d, (0, 0, LW, 64), 0, fill=(40, 40, 48)); rr(d, (200, 14, 1400, 50), 18, fill=(60, 60, 70))
    text(d, (240, 32), "find devices", 26, (170, 170, 180), False, "lm")
    if title:
        text(d, (LW / 2, 150), title, 56, (240, 240, 245), True, "mm")
    return im, d


def lap_signin(click=0.0, cursor=None):
    """sign-in page: password already in (thanks, Jess), and a 'Find Devices' button that skips the code"""
    im, d = _lap("Sign in")
    for i, (lab, val) in enumerate((("Email", "you@mail.co.uk"), ("Password", "•••••••••••"))):
        y = 260 + i * 150; rr(d, (500, y, 1100, y + 110), 22, fill=(44, 44, 54))
        text(d, (530, y + 30), lab, 24, (150, 150, 160), False, "lm"); text(d, (530, y + 74), val, 34, (235, 235, 240), False, "lm")
    rr(d, (500, 600, 1100, 690), 45, fill=(60, 60, 72)); text(d, (800, 645), "Sign In", 34, (200, 200, 210), True, "mm")
    b = (560, 800, 1040, 890)
    rr(d, b, 45, fill=(30, 120, 255) if click <= 0 else (90, 160, 255))
    if click > 0:
        rr(d, (b[0] - 10, b[1] - 10, b[2] + 10, b[3] + 10), 52, outline=(255, 255, 255), width=6)
    text(d, (800, 845), "Find Devices", 36, (255, 255, 255), True, "mm")
    _cursor(d, cursor)
    return im


def lap_list(erase_hl=0.0, cursor=None, pulse=0.0):
    """Find Devices: her new phone on the map at Jess's flat; 'Erase This Device' button"""
    im, d = _lap()
    m = map_crop(FLAT, 260, 1040, 900); im.paste(m, (540, 80)); d = ImageDraw.Draw(im)
    _pin(d, 540 + 520, 80 + 450, GREEN, 1.1, pulse)
    text(d, (540 + 520, 80 + 520), "Jess's flat", 30, INK, True, "mm")
    rr(d, (20, 80, 520, 980), 24, fill=(36, 36, 44)); text(d, (50, 130), "All Devices", 38, (240, 240, 245), True, "lm")
    rr(d, (40, 180, 500, 300), 20, fill=(60, 70, 100))
    text(d, (70, 220), "iPhone", 34, (255, 255, 255), True, "lm"); text(d, (70, 266), "Jess's flat · now", 26, (180, 200, 230), False, "lm")
    rr(d, (40, 320, 500, 440), 20, fill=(44, 44, 54))
    text(d, (70, 360), "Old iPhone", 34, (200, 200, 205), True, "lm"); text(d, (70, 406), "erased", 26, (150, 150, 160), False, "lm")
    for i, (lab, col) in enumerate((("Play Sound", (60, 60, 72)), ("Mark As Lost", (60, 60, 72)), ("Erase This Device", (150, 30, 36)))):
        y = 560 + i * 120; hl = erase_hl if i == 2 else 0
        rr(d, (40, y, 500, y + 96), 48, fill=tuple(int(c + (255 - c) * 0.25 * hl) for c in col))
        if hl > 0:
            rr(d, (32, y - 8, 508, y + 104), 54, outline=(255, 255, 255), width=5)
        text(d, (270, y + 48), lab, 32, (255, 255, 255), True, "mm")
    _cursor(d, cursor)
    return im


def lap_confirm(click=0.0, cursor=None):
    """'Are you sure?' box"""
    im = lap_list(0.0, None); ov = Image.new("RGBA", im.size, (0, 0, 0, 150)); im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(im); rr(d, (450, 300, 1150, 700), 36, fill=(44, 44, 54))
    text(d, (800, 380), "Erase this iPhone?", 46, (245, 245, 250), True, "mm")
    text(d, (800, 450), "Are you sure?", 34, (190, 190, 200), False, "mm")
    rr(d, (500, 560, 780, 650), 45, fill=(70, 70, 82)); text(d, (640, 605), "Cancel", 32, (230, 230, 235), True, "mm")
    rr(d, (820, 560, 1100, 650), 45, fill=(220, 50, 60) if click <= 0 else (255, 110, 110)); text(d, (960, 605), "Next", 32, (255, 255, 255), True, "mm")
    if click > 0:
        rr(d, (812, 552, 1108, 658), 50, outline=(255, 255, 255), width=5)
    _cursor(d, cursor)
    return im


def lap_erase(click=0.0, cursor=None):
    """the last step: one big red Erase button"""
    im, d = _lap("Erase iPhone")
    text(d, (800, 260), "Everything on it will be deleted.", 34, (190, 190, 200), False, "mm")
    b = (560, 440, 1040, 580)
    rr(d, b, 70, fill=(230, 40, 50) if click <= 0 else (255, 120, 120))
    text(d, (800, 510), "Erase", 64, (255, 255, 255), True, "mm")
    _cursor(d, cursor)
    return im


def lap_out(typed=0.0, wrong=0.0, cursor=None):
    """kicked out: back to the sign-in page. He types the old password -> 'Incorrect password' (the field shakes)"""
    im, d = _lap("You've been signed out")
    sh = int(26 * math.sin(wrong * math.pi * 6) * (1 - wrong)) if 0 < wrong < 1 else 0
    y = 330; rr(d, (500 + sh, y, 1100 + sh, y + 110), 22, fill=(44, 44, 54), outline=(235, 60, 60) if wrong > 0 else None, width=4)
    text(d, (530 + sh, y + 30), "Password", 24, (150, 150, 160), False, "lm")
    n = int(round(10 * clamp(typed)))
    if n: text(d, (530 + sh, y + 74), "•" * n, 40, (235, 235, 240), True, "lm")
    if wrong > 0:
        text(d, (800, 500), "Incorrect password", 38, (255, 90, 90), True, "mm")
    rr(d, (560, 800, 1040, 890), 45, fill=(30, 120, 255)); text(d, (800, 845), "Find Devices", 36, (255, 255, 255), True, "mm")
    _cursor(d, cursor)
    return im


if __name__ == "__main__":   # preview sheet of every screen
    import os, sys
    out = sys.argv[1] if len(sys.argv) > 1 else "build/p2_ui_preview.png"
    ph = [phone_map(0.5), map_dive(0.5), map_dive(1.0, 0.4), change_password(0.6), remove_devices(0.0, 1.0), remove_devices(1.0),
          signout_all(1.0, 0.0), signout_all(1.0, 1.0), threat_text(1.0)]
    lp = [lap_signin(1.0, (800, 845)), lap_list(1.0, (270, 800)), lap_confirm(1.0, (960, 605)), lap_erase(0.0, (700, 470)), lap_out(1.0, 0.5)]
    sheet = Image.new("RGB", (len(ph) * 240, 427 + 2 * 300), (20, 20, 20))
    for i, s in enumerate(ph): sheet.paste(s.resize((240, 427)), (i * 240, 0))
    for i, s in enumerate(lp): sheet.paste(s.resize((480, 300)), ((i % 4) * 500, 437 + (i // 4) * 300))
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True); sheet.save(out); print("->", out)
