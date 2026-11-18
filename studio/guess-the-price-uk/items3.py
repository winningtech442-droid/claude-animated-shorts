"""Item drawings for Ep 3 (New Year edition). Each item fits roughly in a 440x440 box centred on 0,0."""
INK = "#141418"
SW = f'stroke="{INK}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"'
F = "font-family=\"Fredoka\" font-weight=\"700\""


def lotto():  # 1994 lottery play slip with crossed fingers mascot-free design
    s = f'<rect x="-150" y="-200" width="300" height="400" rx="18" fill="#FFF7E8" {SW}/>'
    s += f'<rect x="-150" y="-200" width="300" height="90" rx="18" fill="#E5484D" {SW}/>'
    s += f'<text x="0" y="-138" text-anchor="middle" {F} font-size="56" fill="#FFF4D6">LOTTO</text>'
    picked = {3, 9, 17, 22, 31, 40}
    for i in range(49):
        x = -120 + (i % 7) * 40; y = -80 + (i // 7) * 40
        n = i + 1
        fill = "#2F63C9" if n in picked else "#FFFFFF"
        s += f'<rect x="{x}" y="{y}" width="32" height="30" rx="6" fill="{fill}" stroke="#D9A6A6" stroke-width="3"/>'
        if n in picked:
            s += f'<path d="M{x+6} {y+6} L{x+26} {y+24} M{x+26} {y+6} L{x+6} {y+24}" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/>'
    return s


def dome():  # Millennium Dome: white canopy with yellow masts
    s = ""
    for x in (-170, -100, -35, 35, 100, 170):
        s += f'<path d="M{x} 140 L{x*1.15:.0f} -190" stroke="#F2C94C" stroke-width="12" stroke-linecap="round"/>'
    s += f'<path d="M-230 140 Q-230 -110 0 -120 Q230 -110 230 140Z" fill="#F6F3EC" {SW}/>'
    for x in (-150, -75, 0, 75, 150):
        s += f'<path d="M{x} 140 Q{x*0.85:.0f} -40 0 -118" stroke="#D6D0C2" stroke-width="5" fill="none"/>'
    s += f'<path d="M-230 70 Q0 30 230 70" stroke="#D6D0C2" stroke-width="5" fill="none"/>'
    for x in (-170, -100, -35, 35, 100, 170):
        s += f'<path d="M{x*0.9:.0f} 40 L{x*1.15:.0f} -190" stroke="#F2C94C" stroke-width="12" stroke-linecap="round"/><path d="M{x*0.9:.0f} 40 L{x*1.15:.0f} -190" stroke="{INK}" stroke-width="3" fill="none" opacity=".5"/>'
    s += f'<rect x="-250" y="140" width="500" height="34" rx="10" fill="#5F8FA8" {SW}/>'
    s += f'<text x="0" y="110" text-anchor="middle" {F} font-size="54" fill="{INK}">2000</text>'
    return s


def fwticket():  # NYE fireworks ticket
    s = (f'<path d="M-210 -120 L210 -120 L210 -40 Q180 -30 180 0 Q180 30 210 40 L210 120 L-210 120 L-210 40 Q-180 30 -180 0 Q-180 -30 -210 -40Z" fill="#1E2A5E" {SW}/>'
         f'<path d="M90 -110 L90 110" stroke="#FFF4D6" stroke-width="5" stroke-dasharray="14 12"/>')
    for cx, cy, r, c in [(-90, -30, 62, "#F2B731"), (10, 20, 44, "#E5484D"), (-130, 55, 30, "#8FD3FF")]:
        for k in range(12):
            import math
            a = k * math.pi / 6
            s += f'<path d="M{cx+math.cos(a)*r*0.3:.0f} {cy+math.sin(a)*r*0.3:.0f} L{cx+math.cos(a)*r:.0f} {cy+math.sin(a)*r:.0f}" stroke="{c}" stroke-width="7" stroke-linecap="round"/>'
    s += f'<text x="150" y="-20" text-anchor="middle" {F} font-size="36" fill="#FFF4D6">NYE</text>'
    s += f'<text x="150" y="30" text-anchor="middle" {F} font-size="30" fill="#F2B731">ADMIT</text>'
    s += f'<text x="150" y="68" text-anchor="middle" {F} font-size="30" fill="#F2B731">ONE</text>'
    return s


def ds():  # original chunky dual-screen handheld, opened
    return (f'<rect x="-200" y="-210" width="400" height="200" rx="34" fill="#D8D9DE" {SW}/>'
            f'<rect x="-110" y="-185" width="220" height="150" rx="8" fill="#2A2C36" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="-95" y="-172" width="190" height="124" fill="#8FB4E6"/>'
            f'<circle cx="-155" cy="-110" r="10" fill="#9C9CA6"/><circle cx="155" cy="-110" r="10" fill="#9C9CA6"/>'
            f'<rect x="-150" y="-12" width="300" height="24" rx="10" fill="#B8B9C0" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="-200" y="10" width="400" height="200" rx="34" fill="#D8D9DE" {SW}/>'
            f'<rect x="-95" y="35" width="190" height="140" rx="6" fill="#2A2C36" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="-82" y="47" width="164" height="116" fill="#BFD6F2"/>'
            f'<path d="M-170 110 h50 M-145 85 v50" stroke="{INK}" stroke-width="18" stroke-linecap="square"/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="13" fill="{c}" stroke="{INK}" stroke-width="4"/>' for x, y, c in [(145, 80, "#E5484D"), (170, 108, "#2F63C9"), (120, 108, "#2DBE6C"), (145, 136, "#F2B731")])
            + f'<path d="M100 -40 L130 30" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>')  # stylus


def iphone():  # 2007 first-gen phone: aluminium back peeking, black glass front, one home button
    return (f'<rect x="-120" y="-215" width="240" height="430" rx="42" fill="#B9BCC2" {SW}/>'
            f'<rect x="-110" y="-205" width="220" height="410" rx="36" fill="#17181E"/>'
            f'<rect x="-92" y="-160" width="184" height="290" rx="6" fill="#3B6FD0"/>'
            + "".join(f'<rect x="{-78+(i%4)*44}" y="{-146+(i//4)*52}" width="32" height="32" rx="8" fill="{c}"/>'
                      for i, c in enumerate(["#2DBE6C", "#F2B731", "#E5484D", "#8FD3FF", "#FFFFFF", "#F28C38", "#9B59D0", "#2DBE6C",
                                             "#8FD3FF", "#E5484D", "#F2B731", "#FFFFFF"]))
            + f'<rect x="-92" y="90" width="184" height="40" fill="#5E6B85" opacity=".7"/>'
            f'<rect x="-30" y="-188" width="60" height="8" rx="4" fill="#3A3B44"/>'
            f'<circle cx="0" cy="170" r="22" fill="#17181E" stroke="#5A5C66" stroke-width="4"/><rect x="-8" y="162" width="16" height="16" rx="3" fill="none" stroke="#5A5C66" stroke-width="3"/>')


def ps3():  # glossy black curved console ("George Foreman grill" shape)
    return (f'<path d="M-220 -40 Q-220 -150 -60 -150 L180 -150 Q225 -150 225 -100 L225 110 Q225 140 195 140 L-180 140 Q-220 140 -220 100Z" fill="#17181E" {SW}/>'
            f'<path d="M-200 -50 Q-195 -130 -60 -132 L170 -132" stroke="#4A4C58" stroke-width="10" fill="none" stroke-linecap="round"/>'
            f'<path d="M-220 40 L225 40" stroke="#2B2D36" stroke-width="6"/>'
            f'<rect x="-120" y="70" width="220" height="10" rx="5" fill="#3A3C46"/>'
            f'<rect x="-205" y="-20" width="30" height="40" rx="6" fill="#C0C2CA" opacity=".9"/>'
            f'<text x="10" y="-40" text-anchor="middle" font-family="Inter" font-weight="700" font-size="44" fill="#8C8E98" letter-spacing="6">PS3</text>'
            f'<circle cx="190" cy="100" r="7" fill="#2DBE6C"/>')


def ps4():  # angular black console with blue light strip
    return (f'<path d="M-210 -40 L190 -90 L215 70 L-185 120Z" fill="#1E2028" {SW}/>'
            f'<path d="M-200 30 L200 -15" stroke="#5B9BFF" stroke-width="9" stroke-linecap="round"/>'
            f'<path d="M-195 45 L-185 120 M200 -10 L215 70" stroke="{INK}" stroke-width="5"/>'
            f'<path d="M-205 -40 L190 -90" stroke="#4A4C58" stroke-width="6" stroke-linecap="round"/>'
            f'<text x="0" y="-2" transform="rotate(-7)" text-anchor="middle" font-family="Inter" font-weight="700" font-size="40" fill="#8C8E98" letter-spacing="6">PS4</text>'
            # controller
            f'<g transform="translate(20 175) scale(0.7)"><path d="M-150 -40 Q-150 -70 -110 -70 L110 -70 Q150 -70 150 -40 L180 60 Q190 110 140 100 L90 40 L-90 40 L-140 100 Q-190 110 -180 60Z" fill="#2A2C36" {SW}/>'
            f'<circle cx="-40" cy="10" r="22" fill="#3A3C46"/><circle cx="40" cy="10" r="22" fill="#3A3C46"/><rect x="-40" y="-60" width="80" height="40" rx="8" fill="#3A3C46"/></g>')


ITEMS = {"lotto": lotto, "dome": dome, "fwticket": fwticket, "ds": ds, "iphone": iphone, "ps3": ps3, "ps4": lambda: f'<g transform="translate(0 -60) scale(0.88)">{ps4()}</g>'}
