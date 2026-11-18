INK = "#141418"
SW = f'stroke="{INK}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"'
F = "font-family=\"Fredoka\" font-weight=\"700\""


def sprouts():
    s = f'<path d="M-200 60 Q-210 170 -120 180 L120 180 Q210 170 200 60Z" fill="#C98B4A" {SW}/>'  # wooden bowl
    s += f'<path d="M-200 60 L200 60" {SW}/>'
    pos = [(-120, 20), (-40, 0), (40, 10), (120, 25), (-80, -60), (0, -75), (80, -55), (-20, -140), (60, -130)]
    for i, (x, y) in enumerate(pos):
        s += f'<circle cx="{x}" cy="{y}" r="52" fill="#7BB547" {SW}/>'
        s += f'<path d="M{x-34} {y-8} Q{x} {y-40} {x+34} {y-8}" fill="none" stroke="#4E8A2B" stroke-width="6" stroke-linecap="round"/>'
        s += f'<path d="M{x-30} {y+18} Q{x} {y-10} {x+30} {y+18}" fill="none" stroke="#9CCB63" stroke-width="6" stroke-linecap="round"/>'
    return s


def xstamp():
    per = "".join(f'<circle cx="{-150+i*30}" cy="-190" r="11" fill="#FFFDF5"/><circle cx="{-150+i*30}" cy="190" r="11" fill="#FFFDF5"/>' for i in range(11))
    per += "".join(f'<circle cx="-160" cy="{-170+i*30}" r="11" fill="#FFFDF5"/><circle cx="160" cy="{-170+i*30}" r="11" fill="#FFFDF5"/>' for i in range(12))
    tree = (f'<path d="M0 -120 L70 -10 L35 -10 L90 70 L-90 70 L-35 -10 L-70 -10Z" fill="#2E9E5B" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
            f'<rect x="-16" y="70" width="32" height="30" fill="#8A5A2B" stroke="{INK}" stroke-width="5"/>'
            f'<path d="M0 -150 L9 -130 L30 -128 L14 -114 L19 -93 L0 -104 L-19 -93 L-14 -114 L-30 -128 L-9 -130Z" fill="#F2C94C" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="9" fill="{c}" stroke="{INK}" stroke-width="3"/>' for x, y, c in [(-30, 10, "#E5484D"), (35, 40, "#F2C94C"), (-50, 55, "#2F63C9"), (20, -40, "#E5484D")]))
    return (f'<rect x="-160" y="-190" width="320" height="380" fill="#F0F0EA" {SW}/>{per}'
            f'<rect x="-120" y="-150" width="240" height="300" fill="#2B5DA8" stroke="{INK}" stroke-width="5"/>'
            f'<g transform="translate(0 -10)">{tree}</g>'
            f'<text x="0" y="135" text-anchor="middle" {F} font-size="50" fill="#FFF4D6">2nd</text>')


def tv():
    return (f'<rect x="-210" y="-160" width="420" height="300" rx="40" fill="#8A5A34" {SW}/>'
            f'<rect x="-180" y="-130" width="290" height="240" rx="50" fill="#5F8FA8" stroke="{INK}" stroke-width="6"/>'
            f'<path d="M-150 -90 Q-110 -115 -60 -105" stroke="#B8DCEB" stroke-width="14" fill="none" stroke-linecap="round"/>'
            f'<circle cx="155" cy="-80" r="20" fill="#D9B27A" stroke="{INK}" stroke-width="5"/><circle cx="155" cy="-20" r="20" fill="#D9B27A" stroke="{INK}" stroke-width="5"/>'
            + "".join(f'<rect x="135" y="{20+i*20}" width="40" height="8" rx="4" fill="#5A3A20"/>' for i in range(4))
            + f'<path d="M-40 -160 L-110 -250 M40 -160 L110 -250" {SW} fill="none"/><circle cx="-110" cy="-250" r="10" fill="{INK}"/><circle cx="110" cy="-250" r="10" fill="{INK}"/>'
            f'<path d="M-150 140 L-170 190 M150 140 L170 190" {SW}/>')


def handheld():
    return (f'<path d="M-130 -210 L130 -210 L130 150 Q130 210 70 210 L-130 210Z" fill="#CFCBC2" {SW}/>'
            f'<rect x="-100" y="-180" width="200" height="170" rx="14" fill="#6E6B78" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="-70" y="-155" width="140" height="120" fill="#9BB04A" stroke="{INK}" stroke-width="4"/>'
            f'<rect x="-40" y="-80" width="22" height="22" fill="#4E5E22"/><rect x="-18" y="-58" width="22" height="22" fill="#4E5E22"/><rect x="4" y="-80" width="22" height="22" fill="#4E5E22"/>'
            f'<path d="M-90 70 h60 M-60 40 v60" stroke="{INK}" stroke-width="20" stroke-linecap="square"/>'
            f'<circle cx="50" cy="80" r="20" fill="#A8326A" stroke="{INK}" stroke-width="4"/><circle cx="95" cy="50" r="20" fill="#A8326A" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M-40 150 l25 -10 M10 150 l25 -10" stroke="#8B877E" stroke-width="12" stroke-linecap="round"/>')


def tower():  # PS2-style black console standing upright
    return (f'<path d="M-90 -200 L80 -200 L80 190 L-90 190Z" fill="#26272E" {SW}/>'
            + "".join(f'<path d="M-70 {-170+i*34} L60 {-170+i*34}" stroke="#3A3C46" stroke-width="10"/>' for i in range(11))
            + f'<rect x="-90" y="-200" width="40" height="390" fill="#1C1D22" stroke="{INK}" stroke-width="5"/>'
            f'<circle cx="-70" cy="-160" r="7" fill="#2F63C9"/><circle cx="-70" cy="-130" r="7" fill="#2DBE6C"/>'
            f'<rect x="-160" y="150" width="320" height="60" rx="14" fill="#3A3C46" {SW}/>'
            f'<path d="M110 0 Q190 10 180 90 Q170 150 120 140" stroke="{INK}" stroke-width="8" fill="none"/>')


def boxwhite():  # Xbox 360-style white console with grey face
    return (f'<path d="M-220 -110 Q-200 -140 -170 -140 L190 -140 Q215 -140 215 -110 L215 110 Q215 140 190 140 L-170 140 Q-200 140 -220 110Z" fill="#F2F2F4" {SW}/>'
            f'<path d="M-220 -110 Q-160 0 -220 110" fill="#C9CAD2" {SW}/>'
            f'<rect x="-110" y="-60" width="250" height="20" rx="10" fill="#C9CAD2" stroke="{INK}" stroke-width="4"/>'
            f'<circle cx="160" cy="70" r="30" fill="#DCDDE3" stroke="{INK}" stroke-width="5"/><circle cx="160" cy="70" r="16" fill="none" stroke="#6CC24A" stroke-width="7"/>'
            f'<path d="M-170 190 Q-210 200 -200 240 Q-180 270 -130 250 L-40 250 Q10 270 30 240 Q40 200 0 190Z" fill="#F2F2F4" {SW}/>'
            f'<circle cx="-5" cy="215" r="9" fill="#6CC24A"/><circle cx="15" cy="232" r="9" fill="#E5484D"/>')


def slimwhite():  # Wii-style slim console with a remote
    return (f'<g transform="rotate(-8)"><rect x="-70" y="-200" width="110" height="380" rx="20" fill="#FAFAFB" {SW}/>'
            f'<rect x="-50" y="-160" width="16" height="200" rx="8" fill="#9EC9F0" stroke="{INK}" stroke-width="4"/>'
            f'<circle cx="10" cy="140" r="12" fill="#D7D8DE" stroke="{INK}" stroke-width="4"/></g>'
            f'<g transform="translate(120 20) rotate(14)"><rect x="-38" y="-170" width="76" height="320" rx="34" fill="#FAFAFB" {SW}/>'
            f'<path d="M-14 -120 h28 M0 -134 v28" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>'
            f'<circle cx="0" cy="-60" r="18" fill="#D7D8DE" stroke="{INK}" stroke-width="4"/>'
            f'<circle cx="0" cy="40" r="9" fill="#9EC9F0"/><circle cx="0" cy="70" r="9" fill="#9EC9F0"/></g>')


def boxwhite_fit(): return f'<g transform="translate(0 -45) scale(0.82)">{boxwhite()}</g>'

ITEMS = dict(sprouts=sprouts, xstamp=xstamp, tv=tv, handheld=handheld, tower=tower, boxwhite=boxwhite_fit, slimwhite=slimwhite)
