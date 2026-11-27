"""EP21 Mattress Money: effects, an original score and the mix (STUDIO-RULES v3, section 8).

usage: python3 -I audio/ep21_sound.py out/ep21/vo.wav src/episodes/ep21/lines.json out/ep21/mix.wav LEN
Every effect sits on something that happens on screen (times match src/ep/ep21/ep21.tsx and act2.tsx, which share
the line anchors in lines.json). The score is synthesized
here: a bouncy explainer bed under the bait that tape-stops at the redirection, a tense pulse in the Booth, an eerie
music-box pad after the switch. A bed runs under everything (no dead air). Master: -14 LUFS, loudness range 5-7 LU,
true peak at or below -1 dBTP; the voice stays clearly on top (music ducks under every line).
"""
import json, subprocess, sys, tempfile, os
import numpy as np, soundfile as sf, pyloudnorm as pyln
sys.path.insert(0, 'audio')
from sfxcore import SR, n_of, tvec, bpf, lpf, hpf, noise, blip, place, sweep, riser

VO, LINES, OUT, LEN = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
_L = json.load(open(LINES))
S = lambda n: _L[n - 1]['start']   # line n's start and end: the same anchors as src/ep/ep21/act2.tsx
E = lambda n: _L[n - 1]['end']
CUT = E(23)                         # the hard cut to black: everything stops here
N = n_of(LEN + 0.5)
sfx = np.zeros((2, N)); mus = np.zeros((2, N))
def cue(sig, t, g=1.0, pan=0.0): place(sfx, sig, t, g, pan)
def mcue(sig, t, g=1.0, pan=0.0): place(mus, sig, t, g, pan)
env = lambda n, a, d: np.minimum(1, tvec(n) / a) * np.exp(-tvec(n) / d)

# ---------- effects kit ----------
def rustle(d=0.4, bright=1.0):
    n = n_of(d); t = tvec(n); e = np.sin(np.pi * t / d) ** 1.5 * (0.6 + 0.4 * np.abs(np.sin(t * 37)))
    return bpf(noise(n), 1200, 5500 * bright) * e
def thump(f=70, d=0.45, body=1.0):
    n = n_of(d); t = tvec(n); fr = np.interp(t, [0, 0.12], [f * 1.8, f])
    return body * np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / 0.14) + 0.35 * lpf(noise(n), 900) * np.exp(-t / 0.05)
def boing(d=0.75):
    n = n_of(d); t = tvec(n); f = 150 + 260 * np.sin(np.pi * np.minimum(1, t / 0.18)) ** 2
    f = f * (1 + 0.06 * np.sin(2 * np.pi * 14 * t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.28) * np.minimum(1, t / 0.005)
def creak(d=0.5, f0=320, f1=190):
    n = n_of(d); t = tvec(n); f = np.interp(t, [0, d], [f0, f1]) * (1 + 0.04 * np.sin(2 * np.pi * 31 * t))
    saw = 2 * ((np.cumsum(f) / SR) % 1) - 1
    return bpf(saw, 250, 2400) * np.sin(np.pi * t / d) ** 2 * 0.6
def whoosh(d=0.5):
    n = n_of(d); t = tvec(n); return bpf(noise(n), 400, 5000) * np.sin(np.pi * t / d) ** 2
def crunch():
    n = n_of(0.14); return sum(bpf(noise(n), 1800, 7000) * env(n, 0.002, 0.012 + 0.006 * k) * (0.6 if k else 1) for k in range(3))
def step(heavy=1.0):
    n = n_of(0.16); t = tvec(n)
    return heavy * (1.2 * np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.035) + 0.5 * bpf(noise(n), 300, 3500) * env(n, 0.004, 0.03))
def clunk(f=180):
    n = n_of(0.35); t = tvec(n); return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.07) + 0.4 * bpf(noise(n), 200, 2500) * np.exp(-t / 0.02)
def clink(f=2900):
    n = n_of(0.5); t = tvec(n); return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.48 * t)) * np.exp(-t / 0.09)
def crack():
    n = n_of(0.5); t = tvec(n)
    return hpf(noise(n), 2500) * np.exp(-t / 0.025) + sum(np.sin(2 * np.pi * f * t) * np.exp(-t / 0.12) for f in (3100, 4270, 5650)) * 0.15
def shimmer(d=1.6):
    n = n_of(d); t = tvec(n)
    return sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate((1318.5, 1975.5, 2637.0, 3136.0))) * np.minimum(1, t / 0.25) * np.exp(-t / 0.6) * 0.25
def whoomph(d=0.9):
    n = n_of(d); t = tvec(n); return lpf(noise(n), 400) * np.exp(-t / 0.3) + np.sin(2 * np.pi * np.cumsum(np.interp(t, [0, d], [90, 40])) / SR) * np.exp(-t / 0.35)
def splash():
    n = n_of(0.6); t = tvec(n); return lpf(noise(n), 2500) * env(n, 0.003, 0.09) + 0.3 * sum(np.sin(2 * np.pi * f * t) * env(n, 0.001, 0.03) for f in (900, 1300))
def squelch():
    n = n_of(0.09); s = 0.5 * bpf(noise(n), 1500, 4000) * env(n, 0.002, 0.03)
    b = blip(2200, 0.05, 0.02); s[:len(b)] += 0.3 * b; return s

# ---------- 0:00 bait: envelope, mattress ----------
cue(thump(95, 0.3, 0.5), 0.0, 0.5)                                 # frame 1: the mattress edge lifts
cue(creak(0.6, 300, 220), 0.25, 0.5, -0.3)
for k in range(5): cue(rustle(0.32, 1.1), 0.35 + 0.42 * k, 0.45, -0.2)   # notes and envelope shoved under
cue(thump(80, 0.35, 0.8), 2.75, 0.6, -0.3)                         # mattress drops back
cue(whoosh(0.35), 3.45, 0.25)                                      # cut
for k in range(6): cue(step(1.25), 4.0 + 0.36 * k, 0.32, 0.5 - 0.1 * k)   # Mate's heavy steps in
for t in (4.3, 5.3): cue(crunch(), t, 0.5, 0.4)                    # toast
cue(rustle(0.35, 0.8), 6.15, 0.35, 0.2)                            # shrug
cue(sweep(180, 520, 0.4) * np.sin(np.pi * tvec(n_of(0.4)) / 0.4) * 0.25, 6.6, 0.5)  # wind-up
# ---------- 0:07.2 the redirection ----------
cue(thump(55, 0.7, 1.3), 7.2, 1.0)                                 # the belly flop
cue(boing(0.75), 7.21, 0.55)                                       # the springs
cue(whoosh(0.32), 7.22, 0.5, -0.5)                                 # Alfie flies
cue(thump(90, 0.5, 1.1), 7.55, 0.95, -0.6)                         # into the wardrobe
for k, f in enumerate((210, 160, 250, 140)): cue(clunk(f), 7.56 + 0.05 * k, 0.45, -0.6)
for k in range(6): cue(clink(2600 + 260 * k), 7.6 + 0.04 * k, 0.12, -0.6)  # coat hangers
for k in range(5): cue(clunk(120 + 15 * k), 7.66 + 0.09 * k, 0.25 * (0.75 ** k), -0.6)  # rattle dying out
cue(rustle(0.9, 1.3), 7.7, 0.22, 0.1)                              # the note flutters down (stillness)
# ---------- 0:09.5 the Booth ----------
cue(whoosh(0.3), 9.38, 0.25)
for t in (9.7, 12.3): cue(squelch(), t, 0.35, 0.5)                 # talkback clicks before the producer
cue(clink(1900), 10.72, 0.35, 0.3); cue(splash(), 10.85, 0.5, 0.3)  # the tea goes over
cue(whoosh(0.3), 12.12, 0.2)
cue(riser(1.0, 600, 900) * 0.6, 13.9, 0.4)                         # the pin wakes up -> crack
cue(whoosh(0.3), 14.5, 0.25)
# ---------- 0:14.9 the switch ----------
cue(crack(), 14.9, 0.8); cue(whoomph(1.0), 14.9, 0.9); cue(shimmer(1.8), 14.92, 0.5)
cue(creak(0.45, 380, 240), 15.3, 0.45, -0.4)                       # wardrobe door
for k in range(3): cue(step(0.4), 15.45 + 0.28 * k, 0.25, -0.4)    # crawling
cue(blip(3520, 0.25, 0.08) * 0.8, 16.3, 0.35); cue(blip(4400, 0.2, 0.06) * 0.6, 16.42, 0.3)  # "tiny" ting
cue(whoosh(0.28), 16.9, 0.18)
cue(creak(0.35, 260, 200), 17.15, 0.25, 0.3)                        # Mate shifts on the bed


# ======================= act 2 (src/ep/ep21/act2.tsx): same anchors as the shots =======================
def flutter(d=1.0):
    n = n_of(d); t = tvec(n); return bpf(noise(n), 900, 4200) * (0.35 + 0.65 * np.abs(np.sin(2 * np.pi * 7 * t))) * np.sin(np.pi * t / d)
def puff(d=0.4):
    n = n_of(d); t = tvec(n); return bpf(noise(n), 500, 2600) * np.sin(np.pi * np.minimum(1, t / d)) ** 0.7 * np.exp(-t / 0.25)
def slap():
    n = n_of(0.3); t = tvec(n); return 1.2 * hpf(noise(n), 900) * np.exp(-t / 0.018) + thump(120, 0.3, 0.7)
def bell(f=1568):
    n = n_of(0.9); t = tvec(n); return sum(np.sin(2 * np.pi * f * r * t) * np.exp(-t / (0.35 / r)) * a for r, a in ((1, 1), (2.76, 0.4), (5.4, 0.2)))
def scrape(d=0.9):
    n = n_of(d); t = tvec(n); return bpf(noise(n), 700, 3000) * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t)) * np.sin(np.pi * t / d)
def printer(d=1.2):
    n = n_of(d); t = tvec(n); m = 2 * ((t * 118) % 1) - 1
    return (0.5 * bpf(m, 200, 1800) + 0.3 * bpf(noise(n), 2000, 6000) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 9 * t)))) * np.minimum(1, np.minimum(t, d - t) / 0.03)
def add(*xs):
    out = np.zeros(max(len(x) for x in xs))
    for x in xs: out[:len(x)] += x
    return out
def bang():
    return add(thump(60, 0.8, 1.4), 0.6 * clunk(140), *[clink(2300 + 400 * k) * 0.15 for k in range(4)])
def squeak(f0=900, f1=500, d=0.25):
    return sweep(f0, f1, d) * np.sin(np.pi * tvec(n_of(d)) / d) * 0.5
def pop():
    n = n_of(0.25); t = tvec(n); return np.sin(2 * np.pi * np.cumsum(np.interp(t, [0, 0.04], [500, 180])) / SR) * np.exp(-t / 0.05) + 0.5 * hpf(noise(n), 1500) * np.exp(-t / 0.01)
def snap():
    n = n_of(0.2); t = tvec(n); return hpf(noise(n), 1800) * np.exp(-t / 0.008) + 0.4 * bpf(noise(n), 2500, 7000) * np.exp(-t / 0.03)
def glitch(d=0.12):
    n = n_of(d); t = tvec(n); return (np.sign(np.sin(2 * np.pi * 60 * t)) * 0.4 + bpf(noise(n), 1000, 8000)) * np.minimum(1, np.minimum(t, d - t) / 0.004)
def buzz(d=0.6):
    n = n_of(d); t = tvec(n); sq = np.sign(np.sin(2 * np.pi * 100 * t))
    return bpf(sq, 200, 4000) * (0.4 + 0.6 * (np.floor(t * 15) % 2)) * np.minimum(1, np.minimum(t, d - t) / 0.01)
def heartbeat():
    return thump(48, 0.35, 1.0) + 0.7 * np.concatenate([np.zeros(n_of(0.18)), thump(44, 0.35, 0.8)])[:n_of(0.35)]
def tick():
    n = n_of(0.03); return bpf(noise(n), 2500, 6000) * np.exp(-tvec(n) / 0.004)

# 0:20 Mate blows the twenty away; Alfie jumps and catches it
T_BLOW, T_JUMP = 20.0, 20.85
cue(puff(0.42), T_BLOW + 0.26, 0.7, 0.2)
cue(flutter(1.1), T_BLOW + 0.32, 0.4, 0.0)
cue(whoosh(0.3), T_JUMP - 0.12, 0.2)
cue(step(0.8), T_JUMP + 0.3, 0.35, -0.3); cue(whoosh(0.35), T_JUMP + 0.38, 0.35, -0.3)   # crouch, spring
cue(snap() * 0.6, T_JUMP + 0.62, 0.5, -0.3); cue(blip(3520, 0.2, 0.06), T_JUMP + 0.63, 0.25, -0.3)  # the catch
cue(thump(75, 0.5, 1.0), T_JUMP + 0.85, 0.85, -0.3); cue(creak(0.35, 240, 180), T_JUMP + 0.9, 0.3, -0.3)  # landing
# 0:22 the title card: a reverse swell into a hit
TITLE = S(8) + 0.36
cue(riser(0.55, 500, 900) * 0.6, TITLE - 0.55, 0.45)
cue(whoomph(1.2), TITLE, 1.0); cue(crack() * 0.5, TITLE, 0.45); cue(shimmer(1.6), TITLE + 0.02, 0.45)
cue(blip(1760, 0.3, 0.1) * 0.7, S(8) + 2.85, 0.3); cue(squeak(1400, 700, 0.2), S(8) + 2.86, 0.35)  # the note shrinks again
# 0:26 the corner shop
T_SHOP = E(8) + 0.15
cue(whoosh(0.3), T_SHOP - 0.12, 0.2)
cue(bell(1568), T_SHOP + 0.05, 0.4, 0.5); cue(bell(1318.5), T_SHOP + 0.2, 0.35, 0.5)       # shop door bell
for k in range(4): cue(step(0.9), T_SHOP + 0.05 + 0.18 * k, 0.3, 0.4 - 0.2 * k)
cue(slap(), T_SHOP + 1.05, 0.9, 0.0)                                                         # the tenner slapped down
cue(clunk(260), T_SHOP + 1.08, 0.5); cue(bell(2093) * 0.6, T_SHOP + 1.1, 0.35)               # till drawer: ka-ching
cue(scrape(1.0), S(9) - 0.05 + 0.9, 0.35, 0.2)                                               # half the shopping slides back
for t in (0.42, 0.86): cue(clunk(420) * 0.5, E(9) + 0.12 + t, 0.3)                           # Alfie jabs the counter
cue(printer(1.2), E(10) + 0.15, 0.4, 0.3)                                                    # the receipt prints
cue(blip(2637, 0.15, 0.05), E(10) + 1.38, 0.2, 0.3)
# 0:34 the Black Friday sale
T_BF, T_HIT = E(11) + 0.85, E(11) + 0.85 + 0.5
cue(whoosh(0.3), T_BF - 0.12, 0.2)
for k in range(4): cue(step(1.4), T_BF + 0.04 + 0.125 * k, 0.4)                              # Mate charges
cue(bang(), T_HIT, 1.0)                                                                      # box meets the door posts
for k in range(7): cue(rustle(0.22, 0.7) + 0.3 * creak(0.22, 300 + 30 * k, 240), S(12) + 0.25 + 0.3 * k, 0.28, 0.1 * (-1) ** k)  # wriggling
cue(rustle(0.25, 1.4), S(13) + 0.86, 0.45, -0.3); cue(blip(1200, 0.08, 0.02), S(13) + 0.9, 0.3, -0.3)  # the tag flicks over
cue(whoosh(0.25), S(14) - 0.95, 0.3, -0.5); cue(slap() * 0.4, S(14) - 0.95 + 0.17, 0.35)    # the fact card slaps in
cue(squeak(700, 420, 0.45), S(14) + 0.1, 0.4)                                                # the box sags
# the deflation: two falling notes
for k, (f0, f1, d) in enumerate(((392, 370, 0.3), (370, 262, 0.75))):
    n = n_of(d); t = tvec(n); sw = sweep(f0, f1, d); saw = lpf(np.sign(sw) * 0.5 + sw, 1400)
    cue(saw * np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.12) * (1 + 0.15 * np.sin(2 * np.pi * 6 * t)), E(14) + 0.05 + 0.32 * k, 0.45)
# 0:40 Nan's kitchen
T_K = E(14) + 0.5
cue(whoosh(0.3), T_K - 0.12, 0.2)
for k in range(4): cue(clink(5200 + 300 * k) * 0.25, T_K + 0.1 + 0.13 * k, 0.25, -0.2)     # butter knife on the tin
cue(pop(), T_K + 0.6, 0.7); cue(clunk(520), T_K + 0.85, 0.4, 0.3); cue(clink(3300), T_K + 0.9, 0.25, 0.3)  # the lid pops off
cue(shimmer(1.0), S(15) + 1.1, 0.25)                                                         # the full-size notes in the jar
for k in range(4): cue(clink(2400) * 0.35, S(16) - 0.05 + 0.35 * (k + 1), 0.2, -0.2)       # Nan pats the jar
cue(rustle(0.3, 1.0), S(16) + 1.55 + 1.2, 0.3)                                               # she takes the tenner
# 0:47 the twist: the grade flickers to the real Britain
T_FLICK = S(17) - 0.55
for k in range(3): cue(step(0.3), E(16) + 0.5 + 0.22 * k, 0.15, 0.3)                        # slippers to the window
cue(glitch(0.1), T_FLICK, 0.6); cue(glitch(0.15), T_FLICK + 0.17, 0.6)
REAL = [(T_FLICK, T_FLICK + 0.1), (T_FLICK + 0.17, T_FLICK + 0.32)]                          # birdsong for a moment
for a, b in REAL:
    n = n_of(b - a); t = tvec(n); cue(np.sin(2 * np.pi * (3200 + 600 * np.sin(2 * np.pi * 18 * t)) * t) * 0.3, a, 0.25, 0.4)
cue(rustle(0.35, 0.8), S(17) + 1.0, 0.2)                                                     # Nan turns
cue(snap(), S(19) + 0.42, 0.75, 0.1)                                                         # the digestive snaps
for k in range(5): cue(crunch(), S(19) + 0.42 + 0.95 + 0.16 * k, 0.35, 0.1)                 # ...and she munches it
cue(whoosh(0.25), S(19) + 0.47 - 0.05, 0.25, -0.5)                                           # fact card in
cue(whoosh(0.3), E(19) + 0.12 + 0.12, 0.3, -0.2)                                             # up comes the magnifier
cue(blip(660, 0.12, 0.05) * 0.8, S(20) + 0.9, 0.35); cue(blip(990, 0.1, 0.04) * 0.6, S(20) + 0.98, 0.3)  # the giant eye blinks
# 0:58 the cliffhanger: the pin, the Booth, Nan
T_PIN = E(21) + 0.1
cue(buzz(S(22) - T_PIN), T_PIN, 0.7); cue(crack() * 0.5, T_PIN, 0.5)
cue(squelch(), S(22) - 0.1, 0.4, 0.5)                                                        # talkback
for t in (S(22) + 0.9, S(22) + 1.45, S(23) + 0.2, S(23) + 0.75, S(23) + 1.25, S(23) + 1.7, S(23) + 2.1, S(23) + 2.45, S(23) + 2.75):
    cue(heartbeat(), t, 0.55)
cue(riser(CUT - T_PIN, 300, 1100) * 0.7, T_PIN, 0.5)

# ---------- room tone under everything ----------
room = lpf(noise(N), 700) * 0.05 + lpf(noise(N), 140) * 0.04
booth = np.where(((tvec(N) > 9.5) & (tvec(N) < 14.62)) | ((tvec(N) > S(22) - 0.02) & (tvec(N) < S(22) + 0.83)), 1.0, 0.0)
room = room * (1 - 0.5 * booth) + booth * (0.03 * np.sin(2 * np.pi * 50 * tvec(N)) + lpf(noise(N), 300) * 0.03)
place(sfx, room, 0, 1.0)
for tt in np.arange(E(14) + 0.5, CUT, 1.0): cue(tick(), tt, 0.12, -0.6)                     # Nan's wall clock

# ---------- the score ----------
BPM = 116; beat = 60 / BPM
def mallet(f, d=0.5, g=1.0):
    n = n_of(d); t = tvec(n)
    return g * (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.22) + 0.25 * np.sin(2 * np.pi * f * 3.9 * t) * np.exp(-t / 0.05)) * np.minimum(1, t / 0.002)
def bass(f, d=0.45):
    n = n_of(d); t = tvec(n); return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.18) * np.minimum(1, t / 0.005)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
bars = [[60, 64, 67, 72], [59, 62, 67, 71], [57, 60, 64, 69], [53, 57, 60, 65]]  # C, G/B, Am, F
bait = np.zeros((2, N))
t = 0.0; i = 0
while t < 7.6:
    ch = bars[int(t / (4 * beat)) % 4]
    pat = [0, 2, 1, 3, 2, 1, 3, 2][i % 8]
    place(bait, mallet(hz(ch[pat] + 12), 0.5, 0.55), t, 1.0, 0.25 if i % 2 else -0.25)
    if i % 2 == 0: place(bait, bass(hz(ch[0] - 24)), t, 0.9)
    if i % 2 == 1: place(bait, hpf(noise(n_of(0.04)), 7000) * env(n_of(0.04), 0.001, 0.01), t, 0.18)
    t += beat / 2; i += 1
# tape stop at the redirection: playback slows to nothing over 0.35 s
T0, TS = 7.2, 0.35
k0 = n_of(T0); kk = np.arange(n_of(TS))
rate = 1 - kk / len(kk)
pos = k0 + np.cumsum(rate)
stop = np.vstack([np.interp(pos, np.arange(N), bait[c]) for c in range(2)]) * np.linspace(1, 0.2, len(kk))
bait[:, k0:] = 0; bait[:, k0:k0 + len(kk)] = stop
mus += bait
# the Booth: a low pulse that tightens toward the pin
for j, tt in enumerate(np.arange(9.5, 14.6, 60 / 72)):
    place(mus, thump(52, 0.5, 0.9) * (0.5 + 0.12 * j), tt, 0.45)
drone_t = tvec(n_of(5.1))
drone = (np.sin(2 * np.pi * 55 * drone_t) + 0.6 * np.sin(2 * np.pi * 82.4 * drone_t)) * np.minimum(1, drone_t / 0.6) * np.minimum(1, (5.1 - drone_t) / 0.3) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.9 * drone_t))
mcue(drone * 0.35, 9.5)
# after the switch: an eerie pad (A minor add 9) and a music box, up to the shop
P0, P1 = 14.95, E(8) + 0.3
pt = tvec(n_of(P1 - P0))
pad = sum(np.sin(2 * np.pi * f * pt) + np.sin(2 * np.pi * f * 1.004 * pt) for f in (220.0, 261.6, 329.6, 493.9)) * np.minimum(1, pt / 0.8) * np.minimum(1, (P1 - P0 - pt) / 0.3) * 0.12
mcue(lpf(pad, 2200), P0, 1.0)
def mbox(m, g=0.3, pan=0.3):
    n = n_of(0.9); t2 = tvec(n)
    return (np.sin(2 * np.pi * hz(m) * t2) + 0.3 * np.sin(2 * np.pi * hz(m) * 2 * t2)) * np.exp(-t2 / 0.35) * np.minimum(1, t2 / 0.002)
for tt, m in ((15.6, 76), (16.5, 72), (17.4, 71), (18.3, 69), (19.2, 72), (20.1, 76), (21.0, 79)):
    mcue(mbox(m), tt, 0.3, 0.3)
# the title: a big A minor add 9 stab, then the pad swells under the rest of the line
st = tvec(n_of(2.4))
stab = sum(np.sin(2 * np.pi * f * st) * a for f, a in ((110, 1.0), (220, 0.8), (261.6, 0.6), (329.6, 0.6), (493.9, 0.4), (659.3, 0.3))) * np.exp(-st / 0.8) * np.minimum(1, st / 0.004)
mcue(lpf(stab, 3000) * 0.5, TITLE)
# the ladder: an A minor groove at 104 bpm that adds a part per beat (shop: bass + music box; sale: + kick and clap;
# kitchen: softer, warm chords). Runs from the shop to Nan's window.
G0, G1 = E(8) + 0.15, E(16) + 0.45
gb = 60 / 104
prog4 = [[57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 55, 59]]                             # Am F G Em
groove = np.zeros((2, N)); tt = G0; i = 0
while tt < G1:
    ch = prog4[int((tt - G0) / (4 * gb)) % 4]
    part = 0 if tt < T_BF else (1 if tt < T_K else 2)
    if i % 2 == 0: place(groove, bass(hz(ch[0] - 12), 0.4) * (0.9 if part < 2 else 0.6), tt, 1.0)
    if part < 2 and i % 2 == 1: place(groove, mallet(hz(ch[(i // 2) % 3] + 24), 0.4, 0.35), tt, 1.0, 0.3 * (-1) ** i)
    if part == 1:
        if i % 4 == 0: place(groove, thump(60, 0.3, 1.0), tt, 0.7)
        if i % 4 == 2: place(groove, bpf(noise(n_of(0.12)), 900, 6000) * env(n_of(0.12), 0.001, 0.035), tt, 0.5)
        place(groove, hpf(noise(n_of(0.04)), 7000) * env(n_of(0.04), 0.001, 0.01), tt + gb / 4, 0.2)
    if part == 2 and i % 4 == 0:
        n = n_of(4 * gb * 0.5); t2 = tvec(n)
        place(groove, sum(np.sin(2 * np.pi * hz(m) * t2) for m in ch) * np.minimum(1, t2 / 0.02) * np.exp(-t2 / 0.9) * 0.25, tt, 1.0)
    tt += gb / 2; i += 1
fade = np.ones(N); a, b = n_of(G1 - 0.25), n_of(G1)
fade[a:b] = np.linspace(1, 0, b - a); fade[b:] = 0; fade[:n_of(G0)] = 0
mus += groove * fade
# the twist: a tender pad (F, then E minor) from Nan's window; it cuts out for the flicker (silence = the real world)
W0, W1 = E(16) + 0.45, E(21) + 0.1
wt = tvec(n_of(W1 - W0))
half = (W1 - W0) / 2
chord = lambda fs: sum(np.sin(2 * np.pi * f * wt) + np.sin(2 * np.pi * f * 1.003 * wt) for f in fs)
tender = np.where(wt < half, chord((174.6, 220.0, 261.6, 329.6)), chord((164.8, 196.0, 246.9, 293.7)))
tender = lpf(tender, 1800) * np.minimum(1, wt / 0.6) * np.minimum(1, (W1 - W0 - wt) / 0.2) * 0.11
for a2, b2 in REAL: tender[n_of(a2 - W0):n_of(b2 - W0)] = 0
mcue(tender, W0)
for tt2, m in ((W0 + 2.2, 72), (W0 + 3.1, 69), (W0 + 4.6, 72), (W0 + 6.4, 71), (W0 + 8.0, 67)):
    mcue(mbox(m), tt2, 0.22, -0.2)
# the cliffhanger: a low pulse that speeds up and a string-like swell, peaking at the cut
C0 = T_PIN
tt3, gap = C0, 0.5
while tt3 < CUT - 0.05:
    place(mus, thump(46, 0.4, 1.0), tt3, 0.55 + 0.45 * (tt3 - C0) / (CUT - C0)); gap = max(0.17, gap * 0.9); tt3 += gap
ct = tvec(n_of(CUT - C0))
swell = sum(lpf(2 * ((np.cumsum(np.full(len(ct), f) * (1 + 0.06 * ct / ct[-1])) / SR) % 1) - 1, 2600) for f in (110.0, 164.8, 220.0, 261.6))
mcue(swell * ((ct / ct[-1]) ** 1.6) * 0.16, C0)

# ---------- mix ----------
vo, vsr = sf.read(VO, always_2d=True)
assert vsr == SR, f"voice must be {SR} Hz"
vo = vo.T
if vo.shape[0] == 1: vo = np.vstack([vo[0], vo[0]])
vo = vo[:, :N] if vo.shape[1] >= N else np.pad(vo, ((0, 0), (0, N - vo.shape[1])))
m = pyln.Meter(SR)
def to_lufs(x, target):
    l = m.integrated_loudness(x.T); return x * 10 ** ((target - l) / 20)
# duck the music under every line (6 dB, 80 ms ramps)
duck = np.ones(N)
for L in json.load(open(LINES)):
    a, b = n_of(L['start'] - 0.08), n_of(L['end'] + 0.12)
    duck[max(0, a):b] = 0.5
from scipy.ndimage import uniform_filter1d
duck = uniform_filter1d(duck, n_of(0.08))
mus = to_lufs(mus, -29.0) * duck
sfx = to_lufs(sfx, -24.0)
mix = vo + mus + sfx
mix[:, n_of(CUT):] = 0          # hard cut to black: silence
mix = to_lufs(mix, -14.0)
tmp = tempfile.mktemp(suffix='.wav')
sf.write(tmp, mix[:, :n_of(LEN)].T.astype(np.float32), SR, subtype='FLOAT')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'alimiter=limit=0.84:attack=2:release=50:level=disabled', '-c:a', 'pcm_f32le', OUT], check=True)
os.remove(tmp)
for name, x in (('voice', vo), ('music', mus), ('effects', sfx)):
    sf.write(OUT.replace('.wav', f'_{name}.wav'), x[:, :n_of(LEN)].T.astype(np.float32), SR, subtype='FLOAT')
e = subprocess.run(['ffmpeg', '-i', OUT, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
summ = e[e.rfind('Summary'):]
grab = lambda k: summ.split(k)[1].split('\n')[0].strip() if k in summ else '?'
print(f"{OUT}: {LEN:.1f} s | integrated {grab('I:')} | range {grab('LRA:')} | true peak {grab('Peak:')}")
