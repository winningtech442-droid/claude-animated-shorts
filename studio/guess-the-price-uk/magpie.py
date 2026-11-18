INK="#141418"; BLK="#1B1C24"; WHITE="#F8F6F1"; BLUE="#2F63C9"; TEAL="#1A9C93"; CAP="#9A7247"; CAPD="#6E4F2E"; GOLD="#F2B731"; GOLDD="#C88A12"; BEAK="#3B3D48"
SW='stroke="%s" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"'%INK

def coin(x,y,r=22):
    import math
    pts=" ".join(f"{x+r*math.cos(math.pi*2*i/12+0.26):.1f},{y+r*math.sin(math.pi*2*i/12+0.26):.1f}" for i in range(12))
    return f'<polygon points="{pts}" fill="{GOLD}" {SW}/><circle cx="{x}" cy="{y}" r="{r*0.62:.1f}" fill="none" stroke="{GOLDD}" stroke-width="3"/><text x="{x}" y="{y+r*0.38:.1f}" text-anchor="middle" font-family="Arial Black,Arial" font-weight="900" font-size="{r*1.0:.0f}" fill="{GOLDD}">£</text>'

def eyes(mode):
    L,R=(127,104),(173,104)
    out=""
    def white(c,rx=17,ry=20): return f'<ellipse cx="{c[0]}" cy="{c[1]}" rx="{rx}" ry="{ry}" fill="{WHITE}" {SW}/>'
    def pupil(c,dx=0,dy=0,r=8): return f'<circle cx="{c[0]+dx}" cy="{c[1]+dy}" r="{r}" fill="{INK}"/><circle cx="{c[0]+dx+3}" cy="{c[1]+dy-3}" r="2.6" fill="#fff"/>'
    if mode=="cheeky":
        out+=white(L)+pupil(L,3,1)+white(R)+pupil(R,3,1)
        out+=f'<path d="M156 92 Q173 84 190 94 L190 100 Q173 92 156 100Z" fill="{BLK}" {SW}/>'  # half lid right
        out+=f'<path d="M110 80 Q125 72 142 80" fill="none" {SW}/><path d="M158 82 Q175 70 192 78" fill="none" {SW}/>'
    elif mode=="smug":
        for c in (L,R):
            out+=white(c)+pupil(c,0,5)
            out+=f'<path d="M{c[0]-18} {c[1]+1} Q{c[0]} {c[1]-26} {c[0]+18} {c[1]+1} L{c[0]+18} {c[1]-22} L{c[0]-18} {c[1]-22}Z" fill="{BLK}" />'
            out+=f'<path d="M{c[0]-18} {c[1]+1} Q{c[0]} {c[1]-6} {c[0]+18} {c[1]+1}" fill="none" {SW}/>'
        out+=f'<path d="M158 70 Q176 58 192 68" fill="none" {SW}/>'
    elif mode=="shock":
        for c in (L,R): out+=white(c,20,24)+pupil(c,0,0,5)
        out+=f'<path d="M106 70 Q124 56 142 66" fill="none" {SW}/><path d="M158 66 Q176 56 194 70" fill="none" {SW}/>'
    elif mode=="happy":
        for c in (L,R): out+=f'<path d="M{c[0]-15} {c[1]+6} Q{c[0]} {c[1]-14} {c[0]+15} {c[1]+6}" fill="none" stroke="{WHITE}" stroke-width="7" stroke-linecap="round"/>'
    elif mode=="cry":
        for c in (L,R): out+=f'<path d="M{c[0]-15} {c[1]} L{c[0]+2} {c[1]+6} L{c[0]-13} {c[1]+12}" fill="none" stroke="{WHITE}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
        out=f'<path d="M110 106 L129 106 L127 104Z"/>'+eyes_cry()
    elif mode=="side":
        for c in (L,R): out+=white(c,17,13)+pupil(c,-9,1,7)
        out+=f'<path d="M110 86 L144 92" fill="none" {SW}/><path d="M156 92 L190 86" fill="none" {SW}/>'
    return out

def eyes_cry():
    o=""
    for (x,y),s in (((127,104),1),((173,104),-1)):
        o+=f'<path d="M{x-14} {y-4} L{x+12*s if s>0 else x-2} {y+4} L{x-14} {y+12}" fill="none" stroke="{WHITE}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>' if s>0 else f'<path d="M{x+14} {y-4} L{x+2} {y+4} L{x+14} {y+12}" fill="none" stroke="{WHITE}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
    o+=f'<path d="M112 120 Q104 150 112 170 Q120 150 112 120Z" fill="#7CC8F2" {SW}/><path d="M190 120 Q182 150 190 172 Q198 150 190 120Z" fill="#7CC8F2" {SW}/>'
    return o

def beak(mode):
    if mode=="smirk":
        return f'<path d="M130 124 Q150 116 170 124 L166 140 L178 170 L150 146 Z" fill="{BEAK}" {SW}/><path d="M150 146 Q162 150 172 160" fill="none" stroke="#6b6e7c" stroke-width="3"/>'
    if mode=="closed":
        return f'<path d="M131 124 Q150 116 169 124 L152 172 Z" fill="{BEAK}" {SW}/><path d="M150 130 L151 160" stroke="#6b6e7c" stroke-width="3"/>'
    if mode=="open":
        return f'<path d="M128 122 Q150 112 172 122 L150 146 Z" fill="{BEAK}" {SW}/><path d="M136 148 Q150 196 164 148 Z" fill="#C2414B" {SW}/><path d="M134 146 L166 146 L150 158Z" fill="{BEAK}" {SW}/>'
    if mode=="wobble":
        return f'<path d="M131 124 Q150 116 169 124 L150 160 Z" fill="{BEAK}" {SW}/><path d="M136 168 Q143 162 150 168 Q157 174 164 168" fill="none" {SW}/>'

def wing(side,pose):
    s=1 if side=="L" else -1
    cx=150-s*66
    if pose=="down":
        d=f"M{150-s*48} 168 Q{150-s*96} 200 {150-s*86} 268 Q{150-s*66} 262 {150-s*44} 236 Z"
        patch=f"M{150-s*56} 180 Q{150-s*84} 205 {150-s*80} 234 Q{150-s*64} 222 {150-s*50} 200 Z"
        tip=f"M{150-s*86} 268 Q{150-s*80} 246 {150-s*66} 252 Q{150-s*66} 262 {150-s*86} 268Z"
    elif pose=="up":
        d=f"M{150-s*52} 176 Q{150-s*110} 140 {150-s*118} 70 Q{150-s*90} 96 {150-s*62} 150 Z"
        patch=f"M{150-s*60} 168 Q{150-s*96} 140 {150-s*104} 104 Q{150-s*84} 124 {150-s*64} 158 Z"
        tip=f"M{150-s*118} 70 Q{150-s*104} 82 {150-s*110} 96 Q{150-s*116} 84 {150-s*118} 70Z"
    elif pose=="hip":
        d=f"M{150-s*50} 168 Q{150-s*104} 196 {150-s*92} 236 Q{150-s*70} 236 {150-s*58} 214 Q{150-s*80} 210 {150-s*76} 200 Z"
        patch=f"M{150-s*60} 182 Q{150-s*88} 196 {150-s*86} 220 Q{150-s*74} 212 {150-s*62} 196 Z"
        tip=f"M{150-s*92} 236 Q{150-s*80} 226 {150-s*70} 234 Q{150-s*80} 240 {150-s*92} 236Z"
    elif pose=="hold":
        d=f"M{150-s*48} 170 Q{150-s*86} 186 {150-s*70} 236 Q{150-s*40} 238 {150-s*24} 222 Q{150-s*44} 212 {150-s*52} 200 Z"
        patch=f"M{150-s*56} 184 Q{150-s*76} 196 {150-s*66} 224 Q{150-s*54} 214 {150-s*54} 196 Z"
        tip=f"M{150-s*24} 222 Q{150-s*34} 214 {150-s*44} 226 Q{150-s*34} 232 {150-s*24} 222Z"
    return f'<path d="{d}" fill="{BLK}" {SW}/><path d="{patch}" fill="{WHITE}" stroke="{INK}" stroke-width="3"/><path d="{tip}" fill="{BLUE}" stroke="{INK}" stroke-width="3"/>'

def magpie(eye="cheeky",bk="smirk",wl="down",wr="down",extra="",spikes=False,cap_tilt=-8):
    tail=f'<path d="M168 238 L262 300 Q300 322 296 338 Q280 348 248 326 L156 262 Z" fill="{TEAL}" {SW}/><path d="M186 258 L274 322" stroke="{BLUE}" stroke-width="9" stroke-linecap="round"/><path d="M200 262 L282 316" stroke="#7FE0D2" stroke-width="3" stroke-linecap="round" opacity=".7"/>'
    legs=f'<path d="M132 296 L128 322 M128 322 L116 330 M128 322 L132 332 M128 322 L140 330 M168 296 L172 322 M172 322 L160 330 M172 322 L176 332 M172 322 L184 330" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
    body=f'<ellipse cx="150" cy="222" rx="68" ry="84" fill="{BLK}" {SW}/><path d="M92 200 Q88 240 104 276" stroke="{BLUE}" stroke-width="5" fill="none" stroke-linecap="round" opacity=".6"/><path d="M208 200 Q212 240 196 276" stroke="#3FB7C9" stroke-width="5" fill="none" stroke-linecap="round" opacity=".6"/><path d="M104 214 Q150 150 196 214 Q200 284 150 296 Q100 284 104 214Z" fill="{WHITE}" stroke="{INK}" stroke-width="3"/>'
    sp=""
    if spikes: sp=f'<path d="M118 56 L112 30 L132 50 L140 22 L152 48 L166 22 L170 50 L190 30 L184 58Z" fill="{BLK}" {SW}/>'
    head=f'<circle cx="150" cy="112" r="64" fill="{BLK}" {SW}/><path d="M104 74 Q120 64 136 70" stroke="{BLUE}" stroke-width="5" fill="none" stroke-linecap="round" opacity=".8"/><path d="M168 60 Q192 66 204 86" stroke="#3FB7C9" stroke-width="5" fill="none" stroke-linecap="round" opacity=".75"/><path d="M98 120 Q96 140 104 154" stroke="{BLUE}" stroke-width="4" fill="none" stroke-linecap="round" opacity=".7"/>'
    cap=f'<g transform="rotate({cap_tilt} 150 70)"><path d="M90 78 Q96 30 152 28 Q206 30 212 74 Q150 60 90 78Z" fill="{CAP}" {SW}/><path d="M90 78 Q150 58 212 74 Q232 82 222 92 Q150 76 84 92 Q76 84 90 78Z" fill="{CAPD}" {SW}/><path d="M118 40 L126 66 M150 32 L152 60 M182 38 L178 64" stroke="{CAPD}" stroke-width="3"/><circle cx="152" cy="30" r="5" fill="{CAPD}" {SW}/></g>'
    if spikes: cap=""
    blush=f'<ellipse cx="112" cy="126" rx="9" ry="5" fill="#E86F7E" opacity=".55"/><ellipse cx="188" cy="126" rx="9" ry="5" fill="#E86F7E" opacity=".55"/>' if eye in("happy","cheeky","smug") else ""
    return f'<g>{tail}{legs}{body}{wing("L",wl)}{wing("R",wr)}{head}{sp}{eyes(eye)}{blush}{beak(bk)}{cap}{extra}</g>'

POSES={
 "hero":dict(eye="cheeky",bk="smirk",wl="down",wr="hold",extra=coin(186,222,24)),
 "smug":dict(eye="smug",bk="smirk",wl="hip",wr="hip",cap_tilt=-14),
 "shock":dict(eye="shock",bk="open",wl="up",wr="up",spikes=True),
 "happy":dict(eye="happy",bk="open",wl="up",wr="up",extra=coin(40,64,18)+coin(262,58,18),cap_tilt=10),
 "cry":dict(eye="cry",bk="wobble",wl="down",wr="down",cap_tilt=4),
 "sneaky":dict(eye="side",bk="closed",wl="down",wr="hold",extra=coin(186,222,24)+f'<path d="M224 196 l8 -8 M232 216 l12 -2 M226 240 l10 6" stroke="{GOLDD}" stroke-width="4" stroke-linecap="round"/>'),
}
RIM="#FFF4D6"
def svg(name,w=300,h=350,label="",rim=True):
    fid="rim_"+name
    f=f'<defs><filter id="{fid}" x="-10%" y="-10%" width="120%" height="120%"><feMorphology in="SourceAlpha" operator="dilate" radius="7" result="d"/><feFlood flood-color="{RIM}"/><feComposite in2="d" operator="in" result="r"/><feMerge><feMergeNode in="r"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>' if rim else ""
    g=f'<g filter="url(#{fid})">' if rim else '<g>'
    return f'<svg viewBox="-20 0 340 360" width="{w}" height="{h}" role="img" aria-label="{label}" xmlns="http://www.w3.org/2000/svg">{f}{g}{magpie(**POSES[name])}</g></svg>'
