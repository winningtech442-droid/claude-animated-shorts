import math, random, sys
sys.path.insert(0, '/home/claude/gen'); sys.path.insert(0, '/home/claude/ep2')
import items2
import magpie as M

W, H, FPS = 1080, 1920, 30
F = "font-family=\"Fredoka\" font-weight=\"700\""
FI = "font-family=\"Inter\" font-weight=\"700\""
INK = "#141418"; CREAM = "#FFF4D6"; RED = "#E5484D"; GREEN = "#2DBE6C"; GREY = "#BDB6A6"
SW = f'stroke="{INK}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"'

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eob(x):  # ease out back
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ---------------- items ----------------
def item(kind):
    if kind in items2.ITEMS: return items2.ITEMS[kind]()
    if kind == "choc":
        return (f'<rect x="-170" y="-80" width="340" height="160" rx="26" fill="#6B3A1F" {SW}/>'
                + "".join(f'<rect x="{-150+i*76}" y="-60" width="62" height="120" rx="12" fill="#7E4626" stroke="#4E2812" stroke-width="5"/>' for i in range(4))
                + f'<path d="M-170 -80 L-60 -80 L-110 80 L-170 80Z" fill="#E9B949" {SW}/><path d="M-150 -40 L-110 -40" stroke="#B5862A" stroke-width="6"/>')
    if kind == "milk":
        return (f'<path d="M-70 -170 L70 -170 L70 -120 Q110 -80 110 0 L110 150 Q110 180 80 180 L-80 180 Q-110 180 -110 150 L-110 0 Q-110 -80 -70 -120Z" fill="#F7FBFF" {SW}/>'
                f'<path d="M-100 0 L100 0 L100 150 Q100 168 80 168 L-80 168 Q-100 168 -100 150Z" fill="#FFFFFF"/>'
                f'<rect x="-82" y="-200" width="164" height="44" rx="14" fill="#C9CED6" {SW}/><path d="M-60 -60 Q-70 40 -60 140" stroke="#DCE6F0" stroke-width="14" stroke-linecap="round" fill="none"/>')
    if kind == "bread":
        return (f'<path d="M-180 40 Q-200 -120 -90 -150 Q0 -190 90 -150 Q200 -120 180 40 L170 150 Q170 170 150 170 L-150 170 Q-170 170 -170 150Z" fill="#D9963F" {SW}/>'
                f'<path d="M-140 30 Q-150 -90 -70 -110 Q0 -140 70 -110 Q150 -90 140 30 L134 140 L-134 140Z" fill="#FBE6B8" stroke="#C88A3A" stroke-width="5"/>'
                + "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="#E8C98A"/>' for x, y in [(-60, -40), (20, -60), (60, 10), (-30, 60), (40, 90), (-90, 30)]))
    if kind == "stamp":
        per = "".join(f'<circle cx="{-150+i*30}" cy="-190" r="11" fill="#FFFDF5"/><circle cx="{-150+i*30}" cy="190" r="11" fill="#FFFDF5"/>' for i in range(11))
        per += "".join(f'<circle cx="-160" cy="{-170+i*30}" r="11" fill="#FFFDF5"/><circle cx="160" cy="{-170+i*30}" r="11" fill="#FFFDF5"/>' for i in range(12))
        return (f'<rect x="-160" y="-190" width="320" height="380" fill="#F0F0EA" {SW}/>{per}'
                f'<rect x="-120" y="-150" width="240" height="300" fill="#B82B3A" stroke="{INK}" stroke-width="5"/>'
                f'<path d="M-50 20 L-60 -40 L-25 -10 L0 -60 L25 -10 L60 -40 L50 20Z" fill="#F2C94C" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
                f'<rect x="-55" y="20" width="110" height="24" rx="6" fill="#F2C94C" stroke="{INK}" stroke-width="5"/>'
                f'<text x="0" y="118" text-anchor="middle" {F} font-size="64" fill="#FFF4D6">1st</text>')
    if kind == "pint":
        return (f'<path d="M-110 -150 L110 -150 L92 170 Q90 185 75 185 L-75 185 Q-90 185 -92 170Z" fill="#D7871F" {SW}/>'
                f'<path d="M-118 -150 Q-130 -200 -80 -205 Q-60 -240 -10 -225 Q30 -250 70 -220 Q125 -220 118 -150Z" fill="#FFF8E7" {SW}/>'
                f'<path d="M-70 -110 L-58 140" stroke="#F3B755" stroke-width="16" stroke-linecap="round"/>'
                + "".join(f'<circle cx="{x}" cy="{y}" r="6" fill="#F8C66A"/>' for x, y in [(20, 0), (40, 60), (0, 100), (50, -60)]))
    if kind == "console":
        return (f'<rect x="-200" y="-110" width="400" height="190" rx="22" fill="#C9C9CF" {SW}/>'
                f'<circle cx="-40" cy="-20" r="80" fill="#B6B6BE" stroke="{INK}" stroke-width="5"/><circle cx="-40" cy="-20" r="18" fill="#9C9CA6" stroke="{INK}" stroke-width="4"/>'
                f'<rect x="80" y="-60" width="90" height="30" rx="10" fill="#9C9CA6" stroke="{INK}" stroke-width="4"/><rect x="80" y="-10" width="90" height="30" rx="10" fill="#9C9CA6" stroke="{INK}" stroke-width="4"/>'
                f'<path d="M-170 110 Q-200 120 -190 160 Q-170 200 -120 175 L-40 175 Q10 200 30 160 Q40 120 10 110Z" fill="#C9C9CF" {SW}/>'
                f'<circle cx="-5" cy="140" r="9" fill="#2F63C9"/><circle cx="15" cy="155" r="9" fill="#E5484D"/><path d="M-165 140 h30 M-150 125 v30" stroke="{INK}" stroke-width="7"/>')
    if kind == "player":
        return (f'<rect x="-120" y="-200" width="240" height="390" rx="34" fill="#F6F6F8" {SW}/>'
                f'<rect x="-90" y="-170" width="180" height="140" rx="12" fill="#8FB4E6" stroke="{INK}" stroke-width="5"/>'
                f'<path d="M-70 -120 h90 M-70 -90 h120 M-70 -60 h70" stroke="#2C4A80" stroke-width="10" stroke-linecap="round"/>'
                f'<circle cx="0" cy="80" r="82" fill="#E7E7EC" stroke="{INK}" stroke-width="5"/><circle cx="0" cy="80" r="30" fill="#F6F6F8" stroke="{INK}" stroke-width="5"/>')
    return ""

# ---------------- episode data ----------------
QS = [
    dict(kind="sprouts", name="A kilo of Brussels sprouts", year="1990", opts=["35p", "79p", "£1.60"], ans=1, pose="smug", line="79p! Still not eating 'em."),
    dict(kind="xstamp", name="2nd-class Christmas stamp", year="1990", opts=["9p", "28p", "17p"], ans=2, pose="happy", line="17p to post a Christmas card!"),
    dict(kind="tv", name="A colour TV licence", year="1990", opts=["£71", "£39", "£109"], ans=0, pose="cry", line="£71! It's £180 now..."),
    dict(kind="handheld", name="The original Game Boy", year="1990", opts=["£39.99", "£109.99", "£69.99"], ans=2, pose="happy", line="£69.99 and worth every penny!"),
    dict(kind="tower", name="The PlayStation 2", year="2000", opts=["£299", "£199", "£399"], ans=0, pose="shock", line="£299. SAME as the PS1!"),
    dict(kind="boxwhite", name="The Xbox 360", year="2005", opts=["£179.99", "£279.99", "£349.99"], ans=1, pose="shock", line="£279.99, and sold out in hours!"),
    dict(kind="slimwhite", name="The Nintendo Wii", year="2006", opts=["£129", "£249", "£179"], ans=2, pose="smug", line="£179 with Wii Sports. Bargain!"),
]
QLEN = 6.5
HOOK = 3.5; CTA = 4.0; OUT = 11.0
# segments: (name, start, dur)
SEG = [("hook", 0, HOOK)]
t = HOOK
for i in range(5): SEG.append((f"q{i+1}", t, QLEN)); t += QLEN
SEG.append(("cta", t, CTA)); t += CTA
for i in range(5, 7): SEG.append((f"q{i+1}", t, QLEN)); t += QLEN
SEG.append(("outro", t, OUT)); t += OUT
TOTAL = t

# ---------------- building blocks ----------------
def bg(t, col1="#1E7A4C", col2="#24905A"):
    cx, cy = 540, 760; n = 16; rot = t * 6
    rays = ""
    for i in range(n):
        a0 = math.radians(rot + i * 360 / n); a1 = math.radians(rot + (i + 0.5) * 360 / n)
        rays += f'<path d="M{cx} {cy} L{cx+2400*math.cos(a0):.0f} {cy+2400*math.sin(a0):.0f} L{cx+2400*math.cos(a1):.0f} {cy+2400*math.sin(a1):.0f}Z" fill="{col2}"/>'
    dots = "".join(f'<circle cx="{((i*137)+30*math.sin(t*1.3+i))%1080:.0f}" cy="{(i*251+t*(60+(i%4)*25))%1920:.0f}" r="{5+(i%3)*3}" fill="#FFFFFF" opacity="{.55+(i%3)*.15:.2f}"/>' for i in range(55))
    return f'<rect width="{W}" height="{H}" fill="{col1}"/>{rays}{dots}'

def header(t, sub="CHRISTMAS SPECIAL", coin=True, qn=None):
    if qn: sub = f"QUESTION {qn} · CHRISTMAS"
    s = f'<g transform="translate(500 150)"><rect x="-400" y="-70" width="800" height="120" rx="60" fill="{RED}" {SW}/>' \
        f'<text x="0" y="12" text-anchor="middle" {F} font-size="62" fill="#FFF4D6" letter-spacing="2">GUESS THE PRICE: UK</text>' \
        f'<rect x="-330" y="58" width="660" height="56" rx="28" fill="{INK}"/><text x="0" y="98" text-anchor="middle" {FI} font-size="28" fill="{CREAM}" letter-spacing="3">{sub}</text>'
    s += '</g>'
    if coin: s += f'<g transform="translate(985 150) rotate({math.sin(t*2)*10:.1f})">{M.coin(0,0,42)}</g>'
    return s

def nicky(pose, x, y, s=1.0, t=0, bob=True, flip=False):
    dy = math.sin(t * 5) * 8 if bob else 0
    sx = -s if flip else s
    p = dict(M.POSES[pose])
    return f'<g transform="translate({x} {y+dy:.1f}) scale({sx} {s}) translate(-150 -350)" filter="url(#rim)">{M.magpie(**p)}</g>'

def bubble(text, x, y, w, size=46, tail="left", k=1.0):
    if k <= 0: return ""
    lines = wrap(text, int(w / (size * 0.52)))
    h = 40 + len(lines) * size * 1.15
    tx = x + 40 if tail == "left" else x + w - 40
    tl = f'<path d="M{tx} {y+h-4} L{tx-50 if tail=="left" else tx+50} {y+h+50} L{tx+40 if tail=="left" else tx-40} {y+h-4}Z" fill="#FFFFFF" {SW}/>'
    body = f'<rect x="{x}" y="{y}" width="{w}" height="{h:.0f}" rx="34" fill="#FFFFFF" {SW}/>'
    cover = f'<path d="M{tx-4 if tail=="left" else tx+4} {y+h-8} L{tx+36 if tail=="left" else tx-36} {y+h-8}" stroke="#FFFFFF" stroke-width="10"/>'
    txt = "".join(f'<text x="{x+w/2}" y="{y+20+size*0.95+i*size*1.15:.0f}" text-anchor="middle" {F} font-size="{size}" fill="{INK}">{esc(l)}</text>' for i, l in enumerate(lines))
    cx, cy = x + w / 2, y + h / 2
    return f'<g transform="translate({cx} {cy}) scale({k:.3f}) translate({-cx} {-cy})">{tl}{body}{cover}{txt}</g>'

def wrap(text, n):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        if len(cur) + len(w_) + 1 > n and cur: lines.append(cur); cur = w_
        else: cur = (cur + " " + w_).strip()
    lines.append(cur); return lines

def confetti(t0, t, cx=540, cy=700, n=60, seed=1):
    if t < t0 or t > t0 + 2.2: return ""
    r = random.Random(seed); out = ""; dt = t - t0
    cols = [RED, "#2F63C9", GREEN, "#F2B731", "#FFFFFF", "#1A9C93"]
    for i in range(n):
        a = r.uniform(-math.pi, 0); v = r.uniform(500, 1300)
        x = cx + math.cos(a) * v * dt; y = cy + math.sin(a) * v * dt + 900 * dt * dt
        rot = r.uniform(0, 360) + dt * 400
        op = clamp(1.6 - dt * 0.8)
        out += f'<rect x="-9" y="-5" width="18" height="10" fill="{r.choice(cols)}" opacity="{op:.2f}" transform="translate({x:.0f} {y:.0f}) rotate({rot:.0f})"/>'
    return out

def ring(t, t0, dur=3.0, x=880, y=360):
    if t < t0 - 0.3 or t > t0 + dur + 0.25: return ""
    p = clamp((t - t0) / dur); n = 3 - int(clamp(t - t0, 0, 2.999))
    R = 66; C = 2 * math.pi * R
    pop = 1 + 0.18 * max(0, 1 - ((t - t0) % 1) * 4)
    return (f'<g transform="translate({x} {y}) scale({pop:.3f})"><circle r="{R+16}" fill="{INK}"/><circle r="{R}" fill="none" stroke="#3a3a46" stroke-width="18"/>'
            f'<circle r="{R}" fill="none" stroke="{RED if n==1 else "#F2B731"}" stroke-width="18" stroke-dasharray="{C*(1-p):.1f} {C:.1f}" transform="rotate(-90)" stroke-linecap="round"/>'
            f'<text y="30" text-anchor="middle" {F} font-size="86" fill="{CREAM}">{n}</text></g>')

def defs():
    return ('<defs><filter id="rim" x="-15%" y="-15%" width="130%" height="130%"><feMorphology in="SourceAlpha" operator="dilate" radius="7" result="d"/>'
            f'<feFlood flood-color="{CREAM}"/><feComposite in2="d" operator="in" result="r"/><feMerge><feMergeNode in="r"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            '<filter id="sh" x="-10%" y="-10%" width="120%" height="130%"><feOffset dy="12"/><feComponentTransfer><feFuncA type="linear" slope=".25"/></feComponentTransfer><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')

# ---------------- scenes ----------------
def scene_q(qi, lt, gt):
    q = QS[qi]; out = bg(gt)
    out += header(gt, qn=f"{qi+1} OF 7")
    # card
    k = eob(lt / 0.45); dx = (1 - k) * 1100
    card = (f'<g transform="translate({dx:.0f} 0)" filter="url(#sh)"><rect x="70" y="270" width="760" height="640" rx="48" fill="#FFFDF5" {SW}/>'
            f'<rect x="110" y="300" width="220" height="86" rx="43" fill="{INK}"/><text x="220" y="360" text-anchor="middle" {F} font-size="56" fill="#F2B731">{q["year"]}</text>'
            f'<g transform="translate(450 600) scale(1.05)">{item(q["kind"])}</g>'
            f'<text x="450" y="870" text-anchor="middle" {F} font-size="50" fill="{INK}">{esc(q["name"])}</text></g>')
    out += card
    out += ring(lt, 1.0, 3.0, 900, 330) if lt < 4.2 else ""
    # options
    reveal = lt >= 4.0; rk = eob((lt - 4.0) / 0.35)
    for i, o in enumerate(q["opts"]):
        ok = eob((lt - 0.35 - i * 0.12) / 0.4)
        if ok <= 0: continue
        y = 960 + i * 150; letter = "ABC"[i]
        fill = "#FFFFFF"; tcol = INK; sc = 1.0; extra = ""
        if reveal:
            if i == q["ans"]:
                fill = GREEN; tcol = "#FFFFFF"; sc = 1 + 0.08 * math.sin(clamp(rk) * math.pi) + 0.04 * clamp(rk)
                extra = f'<g transform="translate(790 {y+60})"><circle r="40" fill="#FFFFFF" {SW}/><path d="M-18 2 L-4 16 L20 -14" fill="none" stroke="{GREEN}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></g>'
            else:
                fill = GREY; tcol = "#6F6A5E"
        cx, cy = 450, y + 60
        out += (f'<g transform="translate({cx} {cy}) scale({ok*sc:.3f}) translate({-cx} {-cy})"><rect x="90" y="{y}" width="720" height="120" rx="60" fill="{fill}" {SW}/>'
                f'<circle cx="160" cy="{y+60}" r="42" fill="{INK}"/><text x="160" y="{y+77}" text-anchor="middle" {F} font-size="48" fill="{CREAM}">{letter}</text>'
                f'<text x="470" y="{y+80}" text-anchor="middle" {F} font-size="64" fill="{tcol}">{esc(o)}</text>{extra}</g>')
    # nicky
    if not reveal:
        pose = "sneaky" if lt < 1.0 else ("cheeky_nc" if False else "smug")
        out += nicky("hero" if lt < 1.0 else "sneaky", 210, 1820, 0.95, gt)
        if lt > 1.0:
            out += bubble("Lock it in!" if qi % 2 == 0 else "Comment your guess!", 400, 1440, 560, 46, "left", eob((lt - 1.0) / 0.3) if lt < 3.6 else 0)
    else:
        out += nicky(q["pose"], 210, 1820, 0.95, gt)
        out += bubble(q["line"], 380, 1420, 600, 46, "left", rk)
        out += confetti(4.0, lt, 450, 1000 + q["ans"] * 150, 70, qi + 3)
    return out

def scene_hook(lt, gt):
    out = bg(gt)
    k = eob(lt / 0.5)
    out += f'<g transform="translate(540 330) scale({k:.3f})"><rect x="-460" y="-150" width="920" height="300" rx="60" fill="{RED}" {SW}/>' \
           f'<text y="-20" text-anchor="middle" {F} font-size="118" fill="{CREAM}">GUESS THE</text><text y="105" text-anchor="middle" {F} font-size="118" fill="{CREAM}">PRICE: UK</text></g>'
    k2 = eob((lt - 0.35) / 0.4)
    out += f'<g transform="translate(540 560) scale({k2:.3f})"><rect x="-300" y="-46" width="600" height="92" rx="46" fill="{INK}"/><text y="16" text-anchor="middle" {FI} font-size="40" fill="#F2B731" letter-spacing="4">CHRISTMAS SPECIAL</text></g>'
    k3 = eob((lt - 0.6) / 0.5)
    out += f'<g transform="translate(0 {(1-k3)*900:.0f})">{nicky("hero", 300, 1560, 1.6, gt)}</g>'
    out += bubble("7 prices. No Googling. Can you beat a magpie?", 470, 760, 540, 50, "left", eob((lt - 1.1) / 0.35))
    return out

def scene_cta(lt, gt):
    out = bg(gt, "#8FD3FF", "#6FC2F5")
    out += header(gt, "BONUS ROUND")
    k = eob(lt / 0.4)
    out += f'<g transform="translate(540 520) scale({k:.3f})"><rect x="-420" y="-170" width="840" height="340" rx="56" fill="#FFFDF5" {SW}/>' \
           f'<text y="-60" text-anchor="middle" {F} font-size="70" fill="{INK}">BONUS POINT</text><text y="20" text-anchor="middle" {F} font-size="54" fill="{INK}">Follow if you’re 5/5</text><text y="94" text-anchor="middle" {F} font-size="54" fill="{INK}">so far. Honest!</text></g>'
    # follow button press
    p = (lt - 1.2) % 1.4; press = 1 - 0.1 * math.sin(clamp(p / 0.3) * math.pi) if lt > 1.2 else 1
    k2 = eob((lt - 0.5) / 0.4)
    done = lt > 2.6
    col = GREY if done else RED; label = "FOLLOWING" if done else "+ FOLLOW"
    out += f'<g transform="translate(540 870) scale({k2*press:.3f})"><rect x="-260" y="-70" width="520" height="140" rx="70" fill="{col}" {SW}/><text y="24" text-anchor="middle" {F} font-size="66" fill="#FFFFFF">{label}</text></g>'
    if done: out += f'<g transform="translate(540 1010) scale({eob((lt-2.6)/0.3):.3f})"><text text-anchor="middle" {F} font-size="64" fill="{INK}">+1 point!</text></g>'
    out += nicky("happy" if done else "hero", 260, 1820, 1.0, gt)
    out += bubble("2 left... the hardest ones!" if lt > 2.6 else "Go on, I won't tell.", 440, 1400, 540, 48, "left", eob((lt - 0.8) / 0.3))
    out += confetti(2.6, lt, 540, 870, 60, 99)
    return out

def scene_outro(lt, gt):
    out = bg(gt)
    out += header(gt, "YOUR SCORE?", coin=(lt < 6.6))
    tiers = [("0-2", "Coal in your stocking", "#FFFFFF"), ("3-5", "Not bad, guv'nor", "#FFFFFF"), ("6-7", "MAGPIE GENIUS", "#F2B731")]
    for i, (s, txt, col) in enumerate(tiers):
        k = eob((lt - 0.3 - i * 0.35) / 0.4)
        if k <= 0: continue
        y = 330 + i * 190; cx, cy = 540, y + 75
        out += (f'<g transform="translate({cx} {cy}) scale({k:.3f}) translate({-cx} {-cy})"><rect x="90" y="{y}" width="900" height="150" rx="40" fill="{col}" {SW}/>'
                f'<rect x="90" y="{y}" width="230" height="150" rx="40" fill="{INK}"/><text x="205" y="{y+98}" text-anchor="middle" {F} font-size="72" fill="{CREAM}">{s}</text>'
                f'<text x="650" y="{y+96}" text-anchor="middle" {F} font-size="54" fill="{INK}">{esc(txt)}</text></g>')
    k = eob((lt - 1.6) / 0.4)
    out += f'<g transform="translate(540 1000) scale({k:.3f})"><rect x="-380" y="-60" width="760" height="120" rx="60" fill="{RED}" {SW}/><text y="22" text-anchor="middle" {F} font-size="62" fill="{CREAM}">Comment your score!</text></g>'
    if lt > 4.0:
        k = eob((lt - 4.0) / 0.4)
        out += f'<g transform="translate(540 1170) scale({k:.3f})"><rect x="-400" y="-56" width="800" height="112" rx="56" fill="{INK}"/><text y="20" text-anchor="middle" {F} font-size="52" fill="#F2B731">Next round: NEW YEAR edition</text></g>'
    # running gag: nicky nicks the header coin
    if lt < 5.8:
        out += nicky("smug" if lt < 3.5 else "sneaky", 260, 1820, 1.0, gt)
        out += bubble("Be honest. I'll know." if lt < 3.5 else "Ooh... what's that shiny thing?", 440, 1390, 560, 48, "left", eob((lt - 0.6) / 0.3))
    elif lt < 6.6:
        p = eo((lt - 5.8) / 0.8)
        x = 260 + (960 - 260) * p; y = 1820 - (1820 - 470) * math.sin(p * math.pi / 2)
        out += nicky("sneaky", x, y, 1.0 - 0.3 * p, gt, bob=False)
    else:
        p = eo((lt - 6.6) / 1.0)
        x = 960 - (960 - 300) * p; y = 470 + (1820 - 470) * p
        out += nicky("hero", x, y, 0.7 + 0.3 * p, gt, bob=lt > 7.6)
        if lt > 7.6:
            out += bubble("Oi! That's MY quid. Follow for round 3!", 440, 1380, 560, 48, "left", eob((lt - 7.6) / 0.3))
    return out

def frame(gt):
    for name, s, d in SEG:
        if s <= gt < s + d or (name == "outro" and gt >= s):
            lt = gt - s
            if name == "hook": body = scene_hook(lt, gt)
            elif name == "cta": body = scene_cta(lt, gt)
            elif name == "outro": body = scene_outro(lt, gt)
            else: body = scene_q(int(name[1:]) - 1, lt, gt)
            break
    # quick white flash on segment change
    fl = ""
    for name, s, d in SEG[1:]:
        if 0 <= gt - s < 0.12: fl = f'<rect width="{W}" height="{H}" fill="#FFFFFF" opacity="{0.6*(1-(gt-s)/0.12):.2f}"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{defs()}{body}{fl}</svg>'

if __name__ == "__main__":
    print(TOTAL, SEG)
