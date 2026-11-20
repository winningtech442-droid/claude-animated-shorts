#!/usr/bin/env python3
"""2D layers for Phoneverse FIX #12 (1080x1920, PIL). Every function returns an RGB or RGBA PIL image; animate by calling with
progress p in 0..1 and compositing over the 3D plates. Props only: invented brand 'ParcelGo', no logos, no real domains, no real card digits.
Safe zone: keep phone content above y=1190 (caption band is at y=1344)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os
W, H = 1920 // 1920 * 1080, 1920
_FONTS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
_REG = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
def font(size, bold=True):
    for p in (_FONTS if bold else _REG):
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()
ORANGE = (255, 150, 30); RED = (235, 50, 60); GREEN = (40, 190, 100); PURPLE = (92, 40, 170); YELLOW = (255, 214, 10)
INK = (20, 20, 28); PAPER = (246, 246, 250); BLUE = (30, 120, 255)
CLOCK = "19:40"                  # one clock on every screen in an episode (FIX #13 showed 22:04 on one screen, 18:42 on the rest)
ease = lambda p: p * p * (3 - 2 * p)
def clamp(p): return max(0.0, min(1.0, p))
def rr(d, box, r, fill=None, outline=None, width=1): d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)
def text(d, xy, s, size, fill=INK, bold=True, anchor="la", stroke=0, stroke_fill=None): d.text(xy, s, font=font(size, bold), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=stroke_fill)
def canvas(bg=PAPER): return Image.new("RGB", (W, H), bg)
def glow_box(im, box, color=ORANGE, width=10, pad=14, r=26, pulse=1.0):
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    b = (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad)
    for k, a in ((18, 40), (10, 80), (4, 140)): d.rounded_rectangle((b[0]-k, b[1]-k, b[2]+k, b[3]+k), r + k, outline=color + (int(a * pulse),), width=6)
    d.rounded_rectangle(b, r, outline=color + (255,), width=width)
    out = im.convert("RGBA"); out.alpha_composite(ov.filter(ImageFilter.GaussianBlur(2))); return out.convert("RGB")
def status_bar(d, dark=False):
    c = (255, 255, 255) if dark else INK
    text(d, (72, 128), CLOCK, 40, c, True, "la"); rr(d, (880, 134, 960, 166), 8, outline=c, width=4); rr(d, (886, 140, 940, 160), 4, fill=c)

def banner(p=1.0, big=True):
    """ParcelGo text banner. p = slam-in progress (0 off-screen, 1 settled). big=True fills the frame (frame 1 / shot 1b)."""
    im = canvas((18, 16, 40)); d = ImageDraw.Draw(im)
    for y in range(0, 1190, 6): d.line([(0, y), (W, y)], fill=(18 + y // 90, 16 + y // 110, 40 + y // 60))
    status_bar(d, True); text(d, (540, 225), CLOCK, 190, (255, 255, 255), True, "ma"); text(d, (540, 415), "Thursday", 44, (200, 200, 230), False, "ma")
    s = 1.0 if p >= 1 else ease(clamp(p)); k = 1.55 if big else 1.0
    cx, cy = 540, int(740 + (1 - s) * -520 * 0 + (1 - s) * 400)
    w, h = int(940 * (0.7 + 0.3 * s) * (1 if not big else 1)), int(330 * k)
    box = (cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2)
    rr(d, (box[0] + 8, box[1] + 14, box[2] + 8, box[3] + 14), 56, fill=(0, 0, 0)); rr(d, box, 56, fill=(255, 255, 255))
    rr(d, (box[0] + 36, box[1] + 36, box[0] + 36 + 96, box[1] + 36 + 96), 24, fill=PURPLE); text(d, (box[0] + 84, box[1] + 84), "P", 66, YELLOW, True, "mm")
    text(d, (box[0] + 160, box[1] + 42), "ParcelGo", 46, INK, True); text(d, (box[2] - 40, box[1] + 50), "now", 36, (120, 120, 130), False, "ra")
    text(d, (box[0] + 40, box[1] + 170), "Missed parcel.", 58 if big else 44, INK, True); text(d, (box[0] + 40, box[1] + 170 + (80 if big else 62)), "Pay £2 to redeliver.", 58 if big else 44, INK, True)
    chip = (box[2] - 250, box[3] - 100, box[2] - 40, box[3] - 36); pulse = 0.5 + 0.5 * math.sin(p * 18)
    rr(d, chip, 32, fill=(int(220 + 30 * pulse), 40, 60)); text(d, ((chip[0] + chip[2]) // 2, (chip[1] + chip[3]) // 2), "£2", 48, (255, 255, 255), True, "mm")
    return im

def parcelgo_page(fill_p=0.0, paid=False):
    """Fake payment page. fill_p 0..1 fills Name, Address, Card number in turn. URL is a truncated prop, never a real lookalike."""
    im = canvas((255, 250, 235)); d = ImageDraw.Draw(im); status_bar(d)
    rr(d, (60, 170, 1020, 250), 40, fill=(235, 235, 240)); text(d, (110, 210), "parcelgo-redeliver…", 38, (90, 90, 100), False, "lm")
    rr(d, (0, 290, W, 470), 0, fill=PURPLE); text(d, (80, 380), "ParcelGo", 82, YELLOW, True, "lm"); text(d, (1000, 380), "Redelivery", 46, (255, 255, 255), True, "rm")
    text(d, (80, 520), "We missed you. Pay £2 to rebook.", 48, INK, True)
    labels = [("Name", "Alex Morgan"), ("Address", "14 Rye Lane, SE15"), ("Card number", "4000 0000 0000 0000")]
    boxes = []
    for i, (lab, val) in enumerate(labels):
        y = 600 + i * 160; text(d, (80, y - 36), lab, 34, (110, 110, 120), False)
        rr(d, (80, y, 1000, y + 110), 22, fill=(255, 255, 255), outline=(200, 200, 210), width=4); boxes.append((80, y, 1000, y + 110))
        seg = clamp(fill_p * 3 - i)
        if seg > 0: text(d, (116, y + 55), val[: max(1, int(len(val) * seg))], 44, INK, True, "lm")
    btn = (80, 1090, 1000, 1200); on = fill_p >= 0.999
    rr(d, btn, 40, fill=(GREEN if on else (180, 180, 190))); text(d, ((btn[0] + btn[2]) // 2, (btn[1] + btn[3]) // 2), "Paid" if paid else "Pay £2", 56, (255, 255, 255), True, "mm")
    im.boxes = boxes; return im

def call_card(name="Fraud Team"):
    im = canvas((14, 18, 30)); d = ImageDraw.Draw(im); status_bar(d, True)
    d.ellipse((400, 330, 680, 610), fill=(60, 80, 130)); rr(d, (490, 400, 590, 540), 12, outline=(255, 255, 255), width=8)  # generic shield-less bank icon
    text(d, (540, 700), name, 84, (255, 255, 255), True, "ma"); text(d, (540, 810), "mobile  •  calling…", 44, (170, 180, 210), False, "ma")
    d.ellipse((220, 1000, 400, 1180), fill=RED); d.ellipse((680, 1000, 860, 1180), fill=GREEN)
    text(d, (310, 1090), "×", 110, (255, 255, 255), True, "mm"); text(d, (770, 1090), "✓", 100, (255, 255, 255), True, "mm"); return im

def bank_screen(balance=4200, hover=False):
    im = canvas((238, 244, 255)); d = ImageDraw.Draw(im); status_bar(d)
    rr(d, (60, 200, 1020, 330), 30, fill=(30, 60, 140)); text(d, (110, 265), "My bank", 54, (255, 255, 255), True, "lm")
    text(d, (540, 470), "Current account", 44, (90, 100, 130), False, "ma"); text(d, (540, 560), f"£{int(balance):,}", 150, INK, True, "ma")
    rr(d, (80, 800, 1000, 960), 40, fill=ORANGE if hover else (255, 255, 255), outline=(30, 60, 140), width=6)
    text(d, (540, 880), "Move £4,200 to SAFE ACCOUNT", 46, INK, True, "mm")
    rr(d, (80, 1010, 1000, 1110), 40, fill=(225, 230, 245)); text(d, (540, 1060), "Cancel", 44, (110, 120, 150), True, "mm")
    return im

def messages_list(filters_glow=0.0):
    im = canvas(); d = ImageDraw.Draw(im); status_bar(d); text(d, (80, 210), "Messages", 90, INK, True, "lm")
    rr(d, (780, 170, 1000, 260), 44, fill=(255, 255, 255), outline=(190, 190, 200), width=4); text(d, (890, 215), "Filters", 42, BLUE, True, "mm")
    for i, (n, m) in enumerate([("Mum", "See you Sunday x"), ("Sam", "Bus is late again"), ("Jo", "Photos from last night")]):
        y = 340 + i * 170; d.ellipse((80, y, 180, y + 100), fill=(200, 205, 230)); text(d, (210, y + 8), n, 46, INK, True); text(d, (210, y + 62), m, 38, (110, 110, 120), False)
    im = glow_box(im, (780, 170, 1000, 260), pulse=filters_glow) if filters_glow > 0 else im
    return im

def panel(title, rows, glow_row=None, tint=(255, 255, 255)):
    im = Image.new("RGB", (900, 330), tint); d = ImageDraw.Draw(im); rr(d, (0, 0, 899, 329), 36, outline=(205, 205, 215), width=4)
    text(d, (40, 16), title, 44, (120, 120, 135), True)
    for i, r in enumerate(rows):
        y = 84 + i * 104; rr(d, (24, y, 876, y + 90), 20, fill=(244, 244, 248)); text(d, (50, y + 45), r, 50 if len(r) < 20 else 44, INK, True, "lm")
    return im

def settings_card(step=3, toggle_on=False):
    """The one 3-4 s shot (16a). step 1..3 reveals the panels top to bottom; the orange box lands on the Screen Unknown Senders toggle."""
    im = canvas((250, 246, 238)); d = ImageDraw.Draw(im); status_bar(d); text(d, (540, 205), "SET IT UP", 56, ORANGE, True, "ma")
    P = [("1  Messages", ["Messages", "Filters  ▸"]), ("2  Filters", ["Manage Filtering  ▸"]), ("3  Unknown Senders", ["Screen Unknown Senders"])]
    for i in range(3):
        if step > i:
            pn = panel(P[i][0], P[i][1], tint=(255, 255, 255)); im.paste(pn, (90, 290 + i * 290))
            if i < 2: text(d, (540, 290 + i * 290 + 300), "▼", 30, ORANGE, True, "mm")
    y0 = 290 + 2 * 290
    if step >= 3:
        tg = (850, y0 + 84 + 18, 960, y0 + 84 + 72); rr(d, tg, 26, fill=(GREEN if toggle_on else (190, 190, 200)))
        kx = tg[2] - 26 if toggle_on else tg[0] + 26; d.ellipse((kx - 22, (tg[1] + tg[3]) // 2 - 22, kx + 22, (tg[1] + tg[3]) // 2 + 22), fill=(255, 255, 255))
        im = glow_box(im, (110, y0 + 84, 970, y0 + 84 + 90))
    return im

def toggle_closeup(p=1.0):
    im = canvas((250, 246, 238)); d = ImageDraw.Draw(im); status_bar(d); text(d, (540, 520), "Screen Unknown Senders", 62, INK, True, "ma")
    tg = (300, 700, 780, 880); on = ease(clamp(p)); rr(d, tg, 90, fill=tuple(int(a + (b - a) * on) for a, b in zip((190, 190, 200), GREEN)))
    kx = int(tg[0] + 90 + (tg[2] - tg[0] - 180) * on); d.ellipse((kx - 78, 790 - 78, kx + 78, 790 + 78), fill=(255, 255, 255))
    return glow_box(im, tg, pad=22, r=100)

def unknown_folder(p=1.0):
    im = canvas(); d = ImageDraw.Draw(im); status_bar(d); text(d, (80, 230), "Messages", 90, INK, True, "lm")
    rr(d, (80, 400, 1000, 600), 40, fill=(228, 233, 250)); rr(d, (130, 450, 230, 520), 12, fill=BLUE); rr(d, (130, 438, 190, 462), 8, fill=BLUE)
    text(d, (260, 500), "Unknown Senders", 56, INK, True, "lm"); text(d, (960, 500), "1", 52, (120, 130, 160), True, "rm")
    s_ = ease(clamp(p)); sc = 1 - 0.45 * s_; bw, bh = int(860 * sc), int(120 * sc); y = int(170 + (500 - 170) * s_ - bh // 2)
    box = (540 - bw // 2, y, 540 + bw // 2, y + bh); rr(d, box, 30, fill=(255, 255, 255), outline=(210, 210, 220), width=3)
    if s_ < 0.85: text(d, (box[0] + 30, y + bh // 2), "ParcelGo: Missed parcel. Pay £2…", max(18, int(38 * sc)), INK, True, "lm")
    return im

def text_card(s, sub=None, p=1.0):
    im = canvas((255, 246, 232)); d = ImageDraw.Draw(im); k = ease(clamp(p)); x = int(540 + (1 - k) * 700)
    rr(d, (x - 440, 520, x + 440, 800), 60, fill=(255, 255, 255), outline=ORANGE, width=10); text(d, (x, 660), s, 150, INK, True, "mm")
    if sub: text(d, (x, 900), sub, 52, (110, 110, 120), True, "mm")
    return im

# Rough Great Britain outline (lon, lat) for the map card; stylised, not survey-accurate.
GB = [(-5.7, 50.1), (-3.5, 50.3), (-1.0, 50.7), (1.4, 51.1), (1.7, 52.7), (0.3, 53.4), (-0.2, 54.1), (-1.5, 55.0), (-2.0, 55.9), (-3.0, 56.2), (-1.8, 57.5), (-2.5, 57.7), (-3.8, 57.6), (-3.2, 58.6), (-5.0, 58.6), (-6.2, 57.5), (-5.6, 56.3), (-4.9, 55.2), (-3.4, 54.9), (-3.0, 53.5), (-4.6, 53.3), (-4.2, 52.4), (-5.2, 51.8), (-3.2, 51.4), (-4.2, 51.1), (-5.7, 50.1)]
def uk_map(p=1.0, ring=0.0, pct=None, dots=24):
    im = canvas((240, 244, 255)); d = ImageDraw.Draw(im); sx, sy = 62, 100; ox, oy = 540 + 2.2 * 62, 1130
    pts = [(ox + lon * sx, oy - (lat - 50) * sy) for lon, lat in GB]
    d.polygon(pts, fill=(205, 214, 245), outline=(80, 100, 190)); d.line(pts + [pts[0]], fill=(80, 100, 190), width=6)
    import random; random.seed(5); k = int(dots * clamp(p))
    for i in range(k):
        x, y = random.uniform(430, 700), random.uniform(420, 1090); r = 14
        d.ellipse((x - r, y - r, x + r, y + r), fill=RED)
    if ring > 0:
        cx, cy, R = 540, 700, 250; d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=(255, 255, 255), width=42)
        d.arc((cx - R, cy - R, cx + R, cy + R), -90, -90 + 360 * (1 / 3) * ease(clamp(ring)), fill=RED, width=42)
        if pct:
            n = int(round(int(pct.rstrip("%")) * ease(clamp(ring)))); text(d, (cx, cy), f"{n}%", 150, INK, True, "mm", stroke=10, stroke_fill=(255, 255, 255))
            if ring >= 1: text(d, (cx, cy + 190), "1 in 3", 70, RED, True, "mm", stroke=8, stroke_fill=(255, 255, 255))
    return im

def card_back(p=1.0, number_glow=True):
    im = canvas((250, 246, 238)); d = ImageDraw.Draw(im); w = int(900 * abs(math.cos(math.pi * (1 - ease(clamp(p))) / 2)) + 8)
    x0 = 540 - w // 2; rr(d, (x0, 560, x0 + w, 960), 40, fill=(40, 52, 96)); d.rectangle((x0, 640, x0 + w, 720), fill=(15, 15, 20))
    if p >= 1:
        rr(d, (x0 + 60, 790, x0 + 560, 870), 12, fill=(235, 235, 240)); text(d, (x0 + 80, 830), "Phone number", 34, INK, True, "lm")
        text(d, (540, 1060), "Call THIS number,", 64, INK, True, "mm"); text(d, (540, 1140), "not the caller's.", 58, RED, True, "mm")
        if number_glow: im = glow_box(im, (x0 + 60, 790, x0 + 560, 870), r=14)
    return im

def comment_box(p=1.0):
    im = canvas((246, 247, 252)); d = ImageDraw.Draw(im); status_bar(d); text(d, (540, 230), "Comments", 66, INK, True, "ma")
    k = ease(clamp(p)); y = int(1000 - 560 * k); rr(d, (60, y, 1020, y + 420), 50, fill=(255, 255, 255), outline=(200, 205, 225), width=5)
    text(d, (110, y + 70), "Did you almost tap one?", 48, (140, 140, 155), False, "lm")
    if int(p * 14) % 2 == 0: d.rectangle((612, y + 40, 620, y + 100), fill=INK)
    return im

def share_to_mum(p=1.0):
    im = canvas((246, 250, 255)); d = ImageDraw.Draw(im); k = ease(clamp(p)); rr(d, (610, 760, 1010, 900), 70, fill=BLUE); text(d, (810, 830), "Mum", 70, (255, 255, 255), True, "mm")
    x = int(110 + (700 - 110) * k); y = int(1000 - (1000 - 840) * k)
    d.polygon([(x, y - 50), (x + 130, y), (x, y + 50), (x + 24, y)], fill=ORANGE); return im

def shop_app(p=1.0):
    im = canvas((246, 247, 250)); d = ImageDraw.Draw(im); status_bar(d); rr(d, (0, 190, W, 330), 0, fill=(255, 255, 255)); text(d, (80, 262), "My orders", 60, INK, True, "lm")
    rr(d, (60, 400, 1020, 760), 40, fill=(255, 255, 255), outline=(215, 215, 225), width=4); text(d, (120, 480), "Order #4471", 46, INK, True, "lm"); text(d, (120, 560), "Out for delivery", 54, GREEN, True, "lm")
    d.ellipse((820, 470, 940, 590), fill=GREEN if p > 0.5 else (200, 200, 210)); text(d, (880, 530), "✓", 80, (255, 255, 255), True, "mm")
    rr(d, (120, 640, 900, 690), 25, fill=(230, 230, 236)); rr(d, (120, 640, 120 + int(780 * clamp(p)), 690), 25, fill=GREEN); return im

def corner_tag(im, label="PHONEVERSE · FIX #12"):
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); f = font(30); bb = d.textbbox((0, 0), label, font=f)
    rr(d, (40, 24, 40 + (bb[2] - bb[0]) + 44, 24 + 56), 28, fill=(15, 15, 20, 175)); d.text((62, 52), label, font=f, fill=(255, 255, 255, 235), anchor="lm")
    out = im.convert("RGBA"); out.alpha_composite(ov); return out.convert("RGB")

def caption(im, words, star, t_in=1.0):
    """words: list of 1-2 strings; star: matching booleans (yellow). Bold white, black stroke, centred at y=0.70H. t_in 0..1 is the pop-in."""
    d = ImageDraw.Draw(im); f = font(int(92 * (0.85 + 0.15 * clamp(t_in * 4)))); parts = [(w.upper(), YELLOW if s else (255, 255, 255)) for w, s in zip(words, star)]
    sizes = [d.textbbox((0, 0), p[0], font=f) for p in parts]; sp = 26; tw = sum(s[2] - s[0] for s in sizes) + sp * (len(parts) - 1); x = (W - tw) // 2; y = int(H * 0.70)
    for (txt, col), s in zip(parts, sizes):
        d.text((x, y), txt, font=f, fill=col, anchor="ls", stroke_width=9, stroke_fill=(0, 0, 0)); x += s[2] - s[0] + sp
    return im

if __name__ == "__main__":      # contact sheet of every prop at phone size, for a quick visual check
    sheet = [("banner", banner(1)), ("parcelgo", parcelgo_page(0.7)), ("call", call_card()), ("bank", bank_screen(3100, True)), ("messages", messages_list(1)),
             ("settings", settings_card(3, True)), ("toggle", toggle_closeup(1)), ("folder", unknown_folder(0.8)), ("ios", text_card("iOS 26+")),
             ("map", uk_map(1, 1, "34%")), ("cardback", card_back(1)), ("comment", comment_box(1)), ("share", share_to_mum(0.7)), ("shop", shop_app(1))]
    cw, ch = 270, 480; cols = 7; rows = 2; S = Image.new("RGB", (cols * (cw + 10) + 10, rows * (ch + 10) + 10), (60, 60, 70))
    for i, (n, im) in enumerate(sheet):
        im = corner_tag(im.convert("RGB")); im = caption(im, ["Check", "this"], [False, True]); S.paste(im.resize((cw, ch)), (10 + (i % cols) * (cw + 10), 10 + (i // cols) * (ch + 10)))
    S.save("docs/props_contact_sheet.png"); print("saved docs/props_contact_sheet.png")


# ---- FIX #12 polish pass (option C) -------------------------------------------------------------------------------------
def chip_closeup(grow=0.0, crack=0.0):
    """5a/5b: the £2 chip alone, filling the frame (replaces the mid-word crops of the banner). crack 0..1 splits it open on a card."""
    im = canvas((18, 16, 40)); d = ImageDraw.Draw(im); g = ImageDraw.Draw(im)
    for r in range(520, 0, -20): g.ellipse((540 - r, 760 - r, 540 + r, 760 + r), fill=(18 + (520 - r) // 14, 16, 40 + (520 - r) // 20))
    k = 0.82 + 0.18 * ease(clamp(grow)); w, h = int(760 * k), int(300 * k); cx, cy = 540, 760; c = ease(clamp(crack))
    if c > 0:                                                     # the card behind the chip
        cw, ch_ = int(620 * (0.7 + 0.3 * c)), int(390 * (0.7 + 0.3 * c)); cb = (cx - cw // 2, cy - ch_ // 2, cx + cw // 2, cy + ch_ // 2)
        rr(d, cb, 36, fill=(40, 52, 96)); rr(d, (cb[0] + 50, cb[1] + 90, cb[0] + 150, cb[1] + 165), 12, fill=YELLOW)
        text(d, (cb[0] + 50, cb[3] - 70), "•••• •••• •••• ••••", 48, (230, 230, 240), True, "lm")
        text(d, (cx, cb[3] + 90), "YOUR CARD", 84, YELLOW, True, "mm", stroke=6, stroke_fill=INK)
    off = int(520 * c)
    for side in (-1, 1):                                          # two halves slide apart
        half = Image.new("RGBA", (w // 2, h), (0, 0, 0, 0)); hd = ImageDraw.Draw(half)
        hd.rounded_rectangle((0 if side < 0 else -w // 2, 0, w // 2 if side < 0 else w // 2 - 1, h - 1), h // 2, fill=(230, 40, 60, 255))
        x = cx - w // 2 + (0 if side < 0 else w // 2) + side * off
        im.paste(half.rotate(side * 8 * c, expand=False), (x, cy - h // 2), half.rotate(side * 8 * c, expand=False))
    if c < 0.35: text(d, (cx, cy), "£2", int(190 * k), (255, 255, 255), True, "mm")
    return im

def hooded_figure(slump=0.0, glow=1.0):
    """8b/14c: a hooded figure behind a laptop, lit only by the screen (replaces the pentagon). No face, no real person."""
    W_, H_ = W, H; im = Image.new("RGB", (W_, H_), (8, 10, 18)); y = int(640 + 70 * clamp(slump))
    gl = Image.new("RGBA", (W_, H_), (0, 0, 0, 0)); g = ImageDraw.Draw(gl)
    g.ellipse((140, y + 120, 940, y + 760), fill=(70, 130, 255, int(150 * glow)))                    # screen glow on the body
    im = Image.alpha_composite(im.convert("RGBA"), gl.filter(ImageFilter.GaussianBlur(90))).convert("RGBA")
    fig = Image.new("RGBA", (W_, H_), (0, 0, 0, 0)); f = ImageDraw.Draw(fig)
    f.ellipse((170, y + 330, 910, y + 900), fill=(14, 16, 26, 255))                                     # shoulders
    f.polygon([(540, y - 40), (700, y + 60), (735, y + 260), (690, y + 420), (390, y + 420), (345, y + 260), (380, y + 60)], fill=(14, 16, 26, 255))
    f.ellipse((345, y + 20, 735, y + 430), fill=(14, 16, 26, 255))                                     # hood
    f.ellipse((420, y + 140, 660, y + 400), fill=(3, 3, 6, 255))                                       # shadowed opening, no face
    rim = Image.new("RGBA", (W_, H_), (0, 0, 0, 0)); ImageDraw.Draw(rim).bitmap((0, 0), fig.split()[3].filter(ImageFilter.FIND_EDGES), fill=(120, 170, 255, int(200 * glow)))
    im = Image.alpha_composite(im, rim.filter(ImageFilter.GaussianBlur(3))); im = Image.alpha_composite(im, fig)
    d = ImageDraw.Draw(im)
    d.polygon([(300, 1060), (780, 1060), (830, 1290), (250, 1290)], fill=(34, 38, 52))                 # laptop lid (back), no logo
    d.line([(300, 1060), (780, 1060)], fill=(120, 170, 255), width=4)
    d.polygon([(200, 1290), (880, 1290), (960, 1340), (120, 1340)], fill=(22, 24, 34))                 # base
    return im.convert("RGB")

def hud(im, label, value, color=RED):
    """Live readout, centred under the caption (in the style of the 'G-force' / 'fuel %' tags in the reference shorts)."""
    out = im.convert("RGBA"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    fv, fl = font(56), font(30); lw = d.textlength(label + "  ", font=fl); vw = d.textlength(value, font=fv)   # one line, centred under the caption
    w = int(lw + vw) + 64; x0 = (W - w) // 2; y0 = 1400
    rr(d, (x0, y0, x0 + w, y0 + 92), 46, fill=(12, 12, 18, 220), outline=color + (255,), width=5)
    d.text((x0 + 32, y0 + 48), label, font=fl, fill=(210, 210, 220, 255), anchor="lm"); d.text((x0 + 32 + lw, y0 + 48), value, font=fv, fill=color + (255,), anchor="lm")
    out.alpha_composite(ov); return out.convert("RGB")

def hook_title(im, p=1.0):
    """On-screen hook for the first 3.3 s (from post/post_file.md). Replaces the hand-added TikTok text."""
    out = im.convert("RGBA"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); a = int(255 * ease(clamp(p * 5)))
    rr(d, (50, 170, 1030, 470), 40, fill=(10, 10, 16, int(0.9 * a)))
    f = font(70); y = 265
    for line in (["THIS ", ("£2", YELLOW), " TEXT CAN"], ["EMPTY YOUR ACCOUNT"]):
        parts = [(t, (255, 255, 255)) if isinstance(t, str) else t for t in line]; tw = sum(d.textlength(t, font=f) for t, _ in parts); x = (W - tw) / 2
        for t, c in parts: d.text((x, y), t, font=f, fill=c + (a,), anchor="lm", stroke_width=6, stroke_fill=(0, 0, 0, a)); x += d.textlength(t, font=f)
        y += 110
    out.alpha_composite(ov); return out.convert("RGB")


# ---- FIX #13 (fake mast / SMS blaster) screens ------------------------------------------------------------------------
# Generic UI only: no real OS look, no logos. Sender names are plain text the way a scam text shows them.
def net_bar(d, net="5G", bars=4, dark=True, warn=False):
    """Status bar with signal bars and the network type, top right. warn=True paints the type red (the downgrade)."""
    c = (255, 255, 255) if dark else INK; text(d, (72, 128), CLOCK, 40, c, True, "la")
    for i in range(5):
        h = 12 + i * 9; x = 700 + i * 22; d.rectangle((x, 166 - h, x + 14, 166), fill=c if i < bars else (c[0] // 3, c[1] // 3, c[2] // 3))
    text(d, (820, 128), net, 40, RED if warn else c, True, "la"); rr(d, (920, 134, 1000, 166), 8, outline=c, width=4); rr(d, (926, 140, 980, 160), 4, fill=c)

def sms_notice(p=1.0, net="5G", bars=4, warn=False, tap=0.0):
    """Lock screen at 18:42 with the fake refund text sliding in. p = slide-in progress, tap 0..1 = orange tap ring on the link."""
    im = canvas((16, 20, 38)); d = ImageDraw.Draw(im)
    for y in range(0, 1190, 6): d.line([(0, y), (W, y)], fill=(16 + y // 100, 20 + y // 120, 38 + y // 70))
    net_bar(d, net, bars, True, warn); text(d, (540, 225), CLOCK, 190, (255, 255, 255), True, "ma"); text(d, (540, 415), "Saturday", 44, (200, 200, 230), False, "ma")
    s = ease(clamp(p)); cy = int(760 + (1 - s) * 420); box = (70, cy - 190, 1010, cy + 190)
    rr(d, (box[0] + 8, box[1] + 14, box[2] + 8, box[3] + 14), 50, fill=(0, 0, 0)); rr(d, box, 50, fill=(255, 255, 255))
    rr(d, (box[0] + 36, box[1] + 36, box[0] + 132, box[1] + 132), 26, fill=GREEN); text(d, (box[0] + 84, box[1] + 84), "✉", 60, (255, 255, 255), True, "mm")
    text(d, (box[0] + 160, box[1] + 50), "HMRC", 50, INK, True); text(d, (box[2] - 40, box[1] + 56), "now", 36, (120, 120, 130), False, "ra")
    text(d, (box[0] + 40, box[1] + 170), "You're owed a tax refund.", 52, INK, True)
    lk = (box[0] + 40, box[1] + 250, box[0] + 640, box[1] + 330); text(d, (lk[0], lk[1] + 40), "Tap to claim: refund-hm…", 46, BLUE, True, "lm")
    if tap > 0: im = glow_box(im, lk, pulse=clamp(tap * 2))
    return im

def network_card(net="5G", bars=4, fake=False, steps=None, p=1.0):
    """Big network readout on the phone: bars + type. steps e.g. ['5G','4G','2G'] ticks through them with p (the downgrade)."""
    if steps: net = steps[min(len(steps) - 1, int(clamp(p) * len(steps)))]; bars = 5 if fake else bars
    im = canvas((14, 16, 26)); d = ImageDraw.Draw(im); net_bar(d, net, bars, True, net == "2G")
    for i in range(5):
        h = 90 + i * 70; x = 230 + i * 130; d.rounded_rectangle((x, 900 - h, x + 96, 900), 14, fill=(RED if fake else (255, 255, 255)) if i < bars else (60, 64, 80))
    text(d, (540, 1040), net, 200, RED if net == "2G" else (255, 255, 255), True, "mm")
    text(d, (540, 1180), "FAKE MAST" if fake else "MOBILE NETWORK", 52, RED if fake else (170, 180, 210), True, "mm")
    return im

def check_card(p=1.0):
    """'Is this mast real?' check: on 4G/5G a green tick, on 2G the check is skipped (grey, crossed)."""
    im = canvas((14, 16, 26)); d = ImageDraw.Draw(im); net_bar(d, "2G", 5, True, True)
    text(d, (540, 360), "Is this mast real?", 70, (255, 255, 255), True, "ma")
    rows = [("5G / 4G", "CHECKED", GREEN), ("2G", "NOT CHECKED", RED)]
    for i, (n, v, c) in enumerate(rows):
        y = 560 + i * 250; on = i == 0 or p > 0.35
        rr(d, (90, y, 990, y + 190), 40, fill=(30, 34, 50)); text(d, (140, y + 95), n, 70, (255, 255, 255), True, "lm")
        if on: text(d, (940, y + 95), v, 54, c, True, "rm")
    return im

def android_2g(step=1, p=0.0):
    """Generic Android-style settings. step 1: search bar types '2G'. step 2: 'Allow 2G' result with the toggle sliding OFF with p."""
    im = canvas((240, 243, 248)); d = ImageDraw.Draw(im); net_bar(d, "5G", 4, False); text(d, (80, 230), "Settings", 86, INK, True, "lm")
    rr(d, (60, 330, 1020, 440), 55, fill=(255, 255, 255), outline=(200, 205, 220), width=4); d.ellipse((112, 360, 152, 400), outline=(110, 110, 130), width=6); d.line([(146, 394), (166, 414)], fill=(110, 110, 130), width=7)
    typed = "2G"[: max(0, min(2, int(p * 3)))] if step == 1 else "2G"; text(d, (200, 385), typed or "Search settings", 50, INK if typed else (150, 150, 165), bool(typed), "lm")
    if step == 1:
        im = glow_box(im, (60, 330, 1020, 440), r=55)
    if step >= 2:
        rr(d, (60, 520, 1020, 760), 40, fill=(255, 255, 255)); text(d, (110, 600), "Allow 2G", 62, INK, True, "lm"); text(d, (110, 680), "Mobile network", 40, (120, 120, 135), False, "lm")
        off = ease(clamp(p)); tg = (790, 600, 970, 690); c = tuple(int(a + (b - a) * off) for a, b in zip(GREEN, (190, 190, 200)))
        rr(d, tg, 45, fill=c); kx = int(tg[2] - 45 - (tg[2] - tg[0] - 90) * off); d.ellipse((kx - 36, 609, kx + 36, 681), fill=(255, 255, 255))
        text(d, (540, 900), "OFF" if off > 0.5 else "ON", 120, GREEN if off > 0.5 else (150, 150, 165), True, "mm")
        if off > 0.5: text(d, (540, 1040), "Fake 2G masts ignored", 50, INK, True, "mm")
        im = glow_box(im, tg, pad=16, r=50)
    return im

def lockdown_card(p=1.0):
    """iPhone: no 2G switch; only Lockdown Mode blocks 2G (heavy: limits many features). Generic look."""
    im = canvas((242, 242, 247)); d = ImageDraw.Draw(im); net_bar(d, "5G", 4, False); text(d, (540, 230), "iPhone", 80, INK, True, "ma")
    rr(d, (80, 360, 1000, 560), 40, fill=(255, 255, 255)); text(d, (130, 460), "2G switch", 60, INK, True, "lm"); text(d, (950, 460), "NONE", 56, RED, True, "rm")
    k = ease(clamp(p * 1.6))
    if k > 0:
        rr(d, (80, 620, 1000, 900), 40, fill=(255, 255, 255)); text(d, (130, 710), "Lockdown Mode", 60, INK, True, "lm"); text(d, (130, 800), "blocks 2G", 46, GREEN, True, "lm")
        rr(d, (680, 770, 960, 840), 35, fill=ORANGE); text(d, (820, 805), "HEAVY", 40, (255, 255, 255), True, "mm")
        text(d, (540, 1000), "Limits a lot of features", 46, (110, 110, 125), True, "mm")
    return im

def forward_7726(p=1.0):
    """Forward the scam text to 7726 (free, UK networks). p: message bubble flies up to the 7726 thread."""
    im = canvas((246, 247, 252)); d = ImageDraw.Draw(im); net_bar(d, "5G", 4, False)
    rr(d, (0, 190, W, 360), 0, fill=(255, 255, 255)); text(d, (540, 250), "To:", 40, (120, 120, 135), False, "ma"); text(d, (540, 300), "7726", 72, INK, True, "ma")
    k = ease(clamp(p)); y = int(1000 - 520 * k); rr(d, (220, y, 1010, y + 230), 46, fill=BLUE)
    text(d, (260, y + 70), "HMRC: You're owed a", 44, (255, 255, 255), True, "lm"); text(d, (260, y + 140), "tax refund. Tap to…", 44, (255, 255, 255), True, "lm")
    if k > 0.9: text(d, (990, y + 270), "Forwarded ✓", 40, GREEN, True, "ra")
    text(d, (540, 1150), "FREE · SPELLS 'SPAM'", 46, ORANGE, True, "mm")
    return im

def ask_box(prompt="Had a refund text?", p=1.0):
    im = comment_box(p); d = ImageDraw.Draw(im); k = ease(clamp(p)); y = int(1000 - 560 * k)
    rr(d, (90, y + 30, 1000, y + 120), 20, fill=(255, 255, 255)); text(d, (110, y + 70), prompt, 48, (140, 140, 155), False, "lm")
    if int(p * 14) % 2 == 0: d.rectangle((110 + int(d.textlength(prompt, font=font(48, False))) + 10, y + 40, 118 + int(d.textlength(prompt, font=font(48, False))) + 10, y + 100), fill=INK)
    return im

def share_to(name="Android friend", p=1.0):
    im = canvas((246, 250, 255)); d = ImageDraw.Draw(im); k = ease(clamp(p)); rr(d, (420, 760, 1030, 900), 70, fill=GREEN); text(d, (725, 830), name, 60, (255, 255, 255), True, "mm")
    x = int(90 + (300 - 90) * k); y = int(1000 - (1000 - 840) * k)
    d.polygon([(x, y - 50), (x + 130, y), (x, y + 50), (x + 24, y)], fill=ORANGE); return im


# ---- FIX #14 (iPhone Duo crackgate) screens: generic foldable UI, dark mode, bold high-contrast text ----------------------
# No real OS look, no logos, no real app icons. The inner screen is near-square (open foldable): IW x IH, split down the middle
# onto the two halves by world.py. The outer screen is a tall strip (OW x OH).
IW, IH = 1440, 1080              # open inner screen is landscape, about 4:3 (Apple's product shot), fold down the middle
OW, OH = 713, 1080
_TILES = [(255, 150, 30), (40, 190, 100), (30, 120, 255), (235, 50, 60), (92, 40, 170), (255, 214, 10), (0, 170, 190), (230, 90, 160)]

def _crack(d, crack, seam_x):
    """A black crack down the fold with pixel bleed either side. crack 0..1 = how far it has run from the top."""
    if crack <= 0: return
    import random; r = random.Random(7); y_end = int(IH * clamp(crack)); x = seam_x; pts = [(x, 0)]
    for y in range(40, y_end + 1, 40): x = seam_x + r.randint(-9, 9); pts.append((x, y))
    for k, (w, c) in enumerate(((34, (0, 230, 120)), (22, (230, 0, 200)), (12, (10, 10, 12)))):     # green/magenta bleed, then the dead line
        d.line(pts, fill=c, width=w)
    for (px, py) in pts[2::3]:                                                                       # little side fractures
        d.line([(px, py), (px + r.choice((-1, 1)) * r.randint(18, 46), py + r.randint(8, 30))], fill=(10, 10, 12), width=5)

def _plaster(d, cx, cy, p):
    """Sticking plaster slapped over the crack (visual joke). p 0..1 = slap-in."""
    if p <= 0: return
    s = 0.6 + 0.4 * ease(clamp(p * 2)); w, h = int(420 * s), int(130 * s)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    g.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=(236, 186, 140, 255), outline=(190, 140, 100, 255), width=4)
    g.rounded_rectangle((w // 3, 10, 2 * w // 3, h - 10), 14, fill=(250, 226, 200, 255))
    for i in range(6):
        for j in range(2): g.ellipse((w // 3 + 18 + i * (w // 3 - 30) // 6, 30 + j * (h - 80), w // 3 + 26 + i * (w // 3 - 30) // 6, 38 + j * (h - 80)), fill=(200, 160, 120, 255))
    im = im.rotate(-28, expand=True, resample=Image.BICUBIC); d._image.paste(im, (cx - im.width // 2, cy - im.height // 2), im)

def duo_home(crack=0.0, press=0.0, plaster=0.0, red=False):
    """Open inner screen (landscape): a big clock widget on the left half, plain app tiles on the right; one continuous screen.
    press 0..1 = orange glow pushing up under the fold; crack 0..1 = the black line running down the fold; plaster = the joke fix."""
    im = Image.new("RGB", (IW, IH), (14, 16, 30)); d = ImageDraw.Draw(im)
    for y in range(0, IH, 6): d.line([(0, y), (IW, y)], fill=(18 + y // 50, 22 + y // 60, 44 + y // 28))
    rr(d, (90, 120, 640, 560), 60, fill=(36, 42, 78)); text(d, (365, 190), CLOCK, 170, (255, 255, 255), True, "ma"); text(d, (365, 410), "Fri 20 Nov", 54, (215, 220, 245), True, "ma")
    rr(d, (90, 620, 640, 960), 60, fill=(48, 36, 80)); text(d, (365, 700), "Sunny", 52, (255, 255, 255), True, "ma"); text(d, (365, 790), "12°", 110, YELLOW, True, "ma")
    for i in range(4):
        for j in range(4):
            x0, y0 = 800 + i * 150, 150 + j * 210; rr(d, (x0, y0, x0 + 116, y0 + 116), 30, fill=_TILES[(i + 3 * j) % 8])
    ov = Image.new("RGBA", (IW, IH), (0, 0, 0, 0)); g = ImageDraw.Draw(ov)                     # no crease line: the real Duo's fold reads as one screen
    if press > 0:
        for k in range(8): g.ellipse((IW // 2 - 40 - k * 22, IH // 2 - 120 - k * 30, IW // 2 + 40 + k * 22, IH // 2 + 120 + k * 30), fill=(255, 140, 20, int(70 * press)))
    im = Image.alpha_composite(im.convert("RGBA"), ov.filter(ImageFilter.GaussianBlur(10))).convert("RGB"); d = ImageDraw.Draw(im)
    if red: d.rectangle((0, 0, IW, IH), outline=RED, width=30)
    _crack(d, crack, IW // 2); _plaster(d, IW // 2, int(IH * 0.42), plaster)
    return im

def duo_card(title, big, sub=None, color=ORANGE, p=1.0, crack=0.0):
    """Dark card on the inner screen: small title, one huge bold value, optional sub line. Readable at phone size."""
    im = Image.new("RGB", (IW, IH), (12, 13, 22)); d = ImageDraw.Draw(im); k = ease(clamp(p * 3))
    rr(d, (70, 90, IW - 70, IH - 90), 60, fill=(26, 28, 44), outline=color, width=10)
    text(d, (IW // 2, 170), title, 72, (235, 236, 245), True, "ma")
    text(d, (IW // 2, 330 + int((1 - k) * 60)), big, 300 if len(big) <= 4 else 230, color, True, "ma")
    if sub: text(d, (IW // 2, 800), sub, 64, (235, 236, 245), True, "ma")
    _crack(d, crack, IW // 2); return im

def duo_camera(flash=0.0, crack=1.0):
    """The camera app pointed at the crack: viewfinder frame + shutter. flash 0..1 = white-out."""
    im = duo_home(crack); d = ImageDraw.Draw(im)
    for (x, y, sx, sy) in ((90, 120, 1, 1), (IW - 90, 120, -1, 1), (90, IH - 260, 1, -1), (IW - 90, IH - 260, -1, -1)):
        d.line([(x, y), (x + sx * 110, y)], fill=(255, 255, 255), width=12); d.line([(x, y), (x, y + sy * 110)], fill=(255, 255, 255), width=12)
    rr(d, (0, IH - 200, IW, IH), 0, fill=(10, 10, 14)); d.ellipse((IW // 2 - 70, IH - 170, IW // 2 + 70, IH - 30), fill=(255, 255, 255), outline=(150, 150, 160), width=10)
    text(d, (IW // 2, 60), "PHOTO", 50, YELLOW, True, "ma")
    if flash > 0: im = Image.blend(im, Image.new("RGB", im.size, (255, 255, 255)), clamp(flash))
    return im

def duo_ask(prompt="Would you fold it every day?", p=1.0):
    """Comment box, dark mode: bold white prompt, light-grey placeholder that reads at phone size (FIX #13 light card read blank)."""
    im = Image.new("RGB", (IW, IH), (12, 13, 22)); d = ImageDraw.Draw(im); text(d, (IW // 2, 150), "Comments", 72, (255, 255, 255), True, "ma")
    k = ease(clamp(p)); y = int(800 - 380 * k); rr(d, (60, y, IW - 60, y + 330), 50, fill=(30, 32, 50), outline=ORANGE, width=8)
    text(d, (110, y + 95), prompt, 60, (255, 255, 255), True, "lm"); text(d, (110, y + 215), "Yes / No - tell me why", 54, (190, 192, 210), True, "lm")
    if int(p * 14) % 2 == 0: d.rectangle((110, y + 250, 118, y + 300), fill=(255, 255, 255))
    return im

def duo_share(p=1.0):
    im = Image.new("RGB", (IW, IH), (12, 13, 22)); d = ImageDraw.Draw(im); k = ease(clamp(p))
    text(d, (IW // 2, 150), "Send to", 72, (255, 255, 255), True, "ma"); rr(d, (760, 460, 1300, 620), 80, fill=BLUE); text(d, (1030, 540), "New Duo owner", 56, (255, 255, 255), True, "mm")
    x = int(150 + (600 - 150) * k); d.polygon([(x, 480), (x + 150, 540), (x, 600), (x + 28, 540)], fill=ORANGE); return im

def duo_outer(alert=False):
    """Outer (cover) screen: lock-screen clock, front-camera pill at the top."""
    im = Image.new("RGB", (OW, OH), (16, 18, 34)); d = ImageDraw.Draw(im)
    for y in range(0, OH, 6): d.line([(0, y), (OW, y)], fill=(18 + y // 50, 22 + y // 60, 44 + y // 28))
    rr(d, (OW // 2 - 90, 34, OW // 2 + 90, 84), 25, fill=(0, 0, 0))
    text(d, (OW // 2, 200), CLOCK, 170, (255, 255, 255), True, "ma"); text(d, (OW // 2, 400), "Fri 20 Nov", 50, (215, 220, 245), True, "ma")
    if alert: rr(d, (60, 760, OW - 60, 940), 40, fill=RED); text(d, (OW // 2, 850), "FAULTY", 70, (255, 255, 255), True, "mm")
    return im

def bezel(im, margin=0.022, radius=0.075):
    """Thin black bezel + rounded corners (applied to a whole screen image before it is split onto the panels)."""
    w, h = im.size; m = int(min(w, h) * margin); r = int(min(w, h) * radius)
    out = Image.new("RGB", (w, h), (0, 0, 0)); inner = im.resize((w - 2 * m, h - 2 * m), Image.LANCZOS)
    mask = Image.new("L", inner.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, inner.width - 1, inner.height - 1), r, fill=255)
    out.paste(inner, (m, m), mask); return out
