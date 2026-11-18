# EP4 food items. Generic drawings (no brand logos), same ink-outline style as items2.py.
INK = "#141418"
SW = f'stroke="{INK}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"'
S5 = f'stroke="{INK}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"'
F = "font-family=\"Fredoka\" font-weight=\"700\""


def chocbar():  # chocolate bar in a dark wrapper, one end unwrapped with a bite out of it
    crimp = "".join(f'<path d="M{x} -70 L{x+9} -84 L{x+18} -70" fill="none" stroke="{INK}" stroke-width="4"/>' for x in range(-200, -110, 18))
    s = (f'<g transform="rotate(-12)">'
         # unwrapped end: chocolate with caramel + nougat layers, bite cut
         f'<path d="M80 -62 L190 -62 Q215 -50 200 -25 Q225 -5 205 20 Q220 45 190 62 L80 62Z" fill="#6B3A1F" {SW}/>'
         f'<path d="M86 -18 L196 -18 Q212 -10 203 4 L86 4Z" fill="#E09A3A" stroke="#4E2812" stroke-width="4"/>'
         f'<path d="M86 4 L203 4 Q214 18 204 34 L86 34Z" fill="#F3E1BE" stroke="#4E2812" stroke-width="4"/>'
         f'<path d="M110 -46 Q140 -54 170 -46" stroke="#8E5532" stroke-width="7" fill="none" stroke-linecap="round"/>'
         # wrapper
         f'<path d="M-200 -70 L100 -70 L120 -58 L100 -40 L122 -22 L100 0 L122 22 L100 40 L120 58 L100 70 L-200 70 Q-214 0 -200 -70Z" fill="#1C1C22" {SW}/>'
         f'<path d="M-170 10 Q-110 -40 -40 0 Q20 34 80 -6" stroke="#E5484D" stroke-width="26" fill="none" stroke-linecap="round"/>'
         f'<path d="M-170 10 Q-110 -40 -40 0 Q20 34 80 -6" stroke="#F2C94C" stroke-width="7" fill="none" stroke-linecap="round"/>'
         f'<path d="M-180 -50 L60 -50" stroke="#3A3A46" stroke-width="10" stroke-linecap="round"/>'
         + crimp + "".join(f'<path d="M{x} 70 L{x+9} 84 L{x+18} 70" fill="none" stroke="{INK}" stroke-width="4"/>' for x in range(-200, -110, 18)) + '</g>')
    return s


def beans():  # tin of value beans, lid peeled back
    stripes = "".join(f'<rect x="-130" y="{-60+i*30}" width="260" height="14" fill="#3E7BD6"/>' for i in range(5))
    beans_ = "".join(f'<ellipse cx="{x}" cy="{y}" rx="16" ry="11" fill="#E0662B" stroke="#9A3A12" stroke-width="3" transform="rotate({r} {x} {y})"/>'
                     for x, y, r in [(-70, -150, 20), (-30, -160, -10), (10, -148, 30), (50, -158, -25), (85, -146, 10), (-50, -132, -30), (30, -130, 15), (70, -128, -5), (-90, -132, 40)])
    return (f'<rect x="-140" y="-150" width="280" height="330" rx="18" fill="#D9DCE2" {SW}/>'
            f'<rect x="-140" y="-90" width="280" height="210" fill="#FFFFFF" stroke="{INK}" stroke-width="6"/>{stripes}'
            f'<rect x="-110" y="-20" width="220" height="86" rx="16" fill="#FFFFFF" stroke="{INK}" stroke-width="5"/>'
            f'<text x="0" y="40" text-anchor="middle" {F} font-size="56" fill="#2B5DA8">VALUE</text>'
            f'<text x="0" y="104" text-anchor="middle" {F} font-size="34" fill="#141418">BAKED BEANS</text>'
            f'<path d="M-140 150 L140 150" stroke="#A9AEB8" stroke-width="6"/><path d="M-140 -120 L140 -120" stroke="#A9AEB8" stroke-width="6"/>'
            f'<ellipse cx="0" cy="-150" rx="140" ry="34" fill="#C95420" {SW}/>{beans_}'
            # peeled lid
            f'<g transform="translate(110 -180) rotate(-55)"><ellipse cx="-60" cy="0" rx="120" ry="30" fill="#E6E8EC" {SW}/>'
            f'<ellipse cx="-60" cy="0" rx="90" ry="20" fill="none" stroke="#B9BDC6" stroke-width="5"/></g>'
            f'<path d="M30 -186 q26 -20 40 0" stroke="#C3C7CF" stroke-width="12" fill="none" stroke-linecap="round"/>')


def noodlepot():  # instant noodle pot with steam and a fork
    steam = "".join(f'<path d="M{x} -200 q-22 -30 0 -60 q22 -30 0 -60" stroke="#FFFFFF" stroke-width="12" fill="none" stroke-linecap="round" opacity=".85"/>' for x in (-60, 0, 60))
    return (f'{steam}'
            f'<path d="M-150 -150 L150 -150 L110 190 Q108 205 92 205 L-92 205 Q-108 205 -110 190Z" fill="#F2B731" {SW}/>'
            f'<path d="M-140 -70 L140 -70 L128 30 L-128 30Z" fill="#E5484D" stroke="{INK}" stroke-width="5"/>'
            f'<text x="0" y="-6" text-anchor="middle" {F} font-size="64" fill="#FFF4D6">NOODLE</text>'
            f'<path d="M-118 90 Q0 120 118 90" stroke="#C88A12" stroke-width="8" fill="none" stroke-linecap="round"/>'
            f'<ellipse cx="0" cy="-150" rx="152" ry="34" fill="#F6E7B5" {SW}/>'
            + "".join(f'<path d="M{x} -160 q15 -14 30 0 t30 0" stroke="#E7C46E" stroke-width="8" fill="none" stroke-linecap="round"/>' for x in (-110, -50, 10, 50))
            + f'<g transform="translate(70 -200) rotate(20)"><rect x="-10" y="-30" width="20" height="200" rx="8" fill="#E9EAEE" {S5}/>'
            f'<path d="M-24 -30 L-24 -100 M-8 -30 L-8 -100 M8 -30 L8 -100 M24 -30 L24 -100" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
            f'<path d="M-24 -30 Q0 -10 24 -30" fill="none" stroke="{INK}" stroke-width="7"/></g>'
            # foil lid peeled up at the back
            f'<path d="M-150 -150 Q-170 -250 -60 -260 L40 -250 Q-40 -200 -40 -150Z" fill="#D0D4DB" {SW}/>')


def crisps():  # puffy crisp packet with a window
    teeth = lambda y: "".join(f'<path d="M{x} {y} l10 {(-12 if y < 0 else 12)} l10 {(12 if y < 0 else -12)}" fill="none" stroke="{INK}" stroke-width="4"/>' for x in range(-150, 150, 20))
    chips = "".join(f'<ellipse cx="{x}" cy="{y}" rx="34" ry="24" fill="#F6CF63" stroke="#B5862A" stroke-width="4" transform="rotate({r} {x} {y})"/>'
                    for x, y, r in [(-50, 40, -20), (10, 30, 15), (60, 50, -10), (-20, 80, 30), (40, 90, -25)])
    return (f'<path d="M-160 -200 L160 -200 Q190 0 160 200 L-160 200 Q-190 0 -160 -200Z" fill="#2F63C9" {SW}/>'
            f'<rect x="-160" y="-200" width="320" height="36" fill="#E5484D" {SW}/><rect x="-160" y="164" width="320" height="36" fill="#E5484D" {SW}/>'
            + teeth(-200) + teeth(200)
            + f'<text x="0" y="-96" text-anchor="middle" {F} font-size="74" fill="#FFF4D6">CRISPS</text>'
            f'<text x="0" y="-48" text-anchor="middle" {F} font-size="32" fill="#F2C94C">READY SALTED</text>'
            f'<ellipse cx="5" cy="60" rx="120" ry="78" fill="#FFF4D6" stroke="{INK}" stroke-width="6"/>{chips}'
            f'<path d="M-140 -150 Q-160 0 -140 150" stroke="#6E95E0" stroke-width="12" fill="none" stroke-linecap="round"/>')


def burger():  # double-decker burger with a middle bun
    seeds = "".join(f'<ellipse cx="{x}" cy="{y}" rx="9" ry="5" fill="#FFF4D6" transform="rotate({r} {x} {y})"/>' for x, y, r in
                    [(-90, -150, -20), (-40, -175, 10), (10, -182, -10), (60, -170, 25), (100, -140, -15), (-60, -125, 30), (30, -140, 0), (-120, -110, 10)])
    patty = lambda y: f'<rect x="-175" y="{y}" width="350" height="46" rx="22" fill="#5A3220" {SW}/>' + "".join(f'<path d="M{x} {y+14} l18 0" stroke="#3D2014" stroke-width="5" stroke-linecap="round"/>' for x in (-130, -60, 10, 80))
    cheese = lambda y: f'<path d="M-170 {y} L170 {y} L150 {y+18} L120 {y+44} L95 {y+18} L-170 {y+18}Z" fill="#F2B731" {S5}/>'
    lettuce = lambda y: f'<path d="M-185 {y} q20 -18 40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 l0 16 l-370 0Z" fill="#7BC24A" {S5}/>'
    return (f'<path d="M-180 160 L180 160 Q180 205 140 205 L-140 205 Q-180 205 -180 160Z" fill="#D9963F" {SW}/>'
            + patty(112) + lettuce(108) + cheese(94)
            + f'<rect x="-178" y="40" width="356" height="50" rx="20" fill="#E3A552" {SW}/>'
            + patty(-6) + lettuce(-10) + cheese(-24)
            + f'<path d="M-185 -30 Q-190 -200 0 -205 Q190 -200 185 -30Z" fill="#E3A552" {SW}/>'
            f'<path d="M-140 -80 Q-130 -150 -60 -175" stroke="#F3C27A" stroke-width="14" fill="none" stroke-linecap="round"/>' + seeds)


def sausageroll():  # flaky sausage roll on a paper bag
    flakes = "".join(f'<path d="M{x} -40 q14 -18 28 0" stroke="#C8792B" stroke-width="5" fill="none" stroke-linecap="round"/>' for x in range(-150, 120, 40))
    return (f'<path d="M-190 -170 L190 -170 L170 190 L-170 190Z" fill="#F4EBDD" {SW}/>'
            f'<path d="M-190 -170 L-160 -140 L-130 -170 L-100 -140 L-70 -170 L-40 -140 L-10 -170 L20 -140 L50 -170 L80 -140 L110 -170 L140 -140 L170 -170 L190 -170" fill="none" stroke="{INK}" stroke-width="5"/>'
            f'<g transform="translate(0 40) rotate(-6)">'
            f'<path d="M-200 -70 Q-200 -100 -170 -100 L170 -100 Q200 -100 200 -60 L200 60 Q200 90 170 90 L-170 90 Q-200 90 -200 60Z" fill="#E7A24A" {SW}/>'
            f'<path d="M-200 -10 Q0 -30 200 -10" stroke="#C8792B" stroke-width="6" fill="none"/>{flakes}'
            f'<path d="M-170 -80 L150 -80" stroke="#F7CB7E" stroke-width="12" stroke-linecap="round"/>'
            f'<ellipse cx="200" cy="0" rx="34" ry="86" fill="#F1C27A" {SW}/><ellipse cx="200" cy="2" rx="22" ry="54" fill="#C77B6A" stroke="#8C4A3C" stroke-width="5"/>'
            f'<path d="M193 -20 l10 6 M195 18 l10 -4" stroke="#A55A4A" stroke-width="4"/></g>')


def fishchips():  # battered fish and chips in a paper cone with a wooden fork
    chips = "".join(f'<rect x="{x}" y="{y}" width="26" height="120" rx="8" fill="#F6CF63" stroke="{INK}" stroke-width="4" transform="rotate({r} {x+13} {y+60})"/>'
                    for x, y, r in [(-150, -130, -20), (-120, -150, -10), (-90, -160, 0), (-60, -150, 12), (-30, -160, 22), (0, -140, -5)])
    return (f'{chips}'
            f'<g transform="rotate(-25 40 -60)"><path d="M-40 -110 Q-60 -40 0 -20 L160 -40 Q210 -60 220 -100 Q200 -150 150 -150 L0 -160 Q-30 -150 -40 -110Z" fill="#E09A3A" {SW}/>'
            + "".join(f'<path d="M{x} -130 q10 14 0 28" stroke="#B66E1E" stroke-width="5" fill="none" stroke-linecap="round"/>' for x in (20, 60, 100, 140))
            + '</g>'
            f'<path d="M-200 -40 L200 -40 L60 210 L-60 210Z" fill="#FFFDF5" {SW}/>'
            f'<path d="M-200 -40 L200 -40 L176 4 L-176 4Z" fill="#E5E1D5" stroke="{INK}" stroke-width="5"/>'
            + "".join(f'<path d="M{-140+i*18} {30+i*0} L{140-i*18} {30}" stroke="#BDB6A6" stroke-width="5"/>'.replace(f"{30+i*0} L{140-i*18} {30}", f"{30+i*34} L{140-i*18} {30+i*34}") for i in range(5))
            + f'<g transform="translate(150 -150) rotate(30)"><rect x="-10" y="0" width="20" height="150" rx="6" fill="#D9B27A" {S5}/>'
            f'<path d="M-16 0 L-16 -40 L-5 -40 L-5 -8 M5 -8 L5 -40 L16 -40 L16 0Z" fill="#D9B27A" {S5}/></g>'
            f'<g transform="translate(-160 30)"><circle r="36" fill="#F7E55A" {S5}/><path d="M-22 0 L22 0 M0 -22 L0 22 M-15 -15 L15 15 M-15 15 L15 -15" stroke="#E4C93A" stroke-width="4"/></g>')


def fit(fn, sc, dy=0): return lambda: f'<g transform="translate(0 {dy}) scale({sc})">{fn()}</g>'


ITEMS = dict(chocbar=fit(chocbar, 1.15), beans=fit(beans, 0.85, 25), noodlepot=fit(noodlepot, 0.72, 55), crisps=crisps, burger=burger, sausageroll=sausageroll, fishchips=fishchips)
