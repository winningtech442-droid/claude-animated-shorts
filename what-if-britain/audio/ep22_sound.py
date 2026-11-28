"""EP22 Typed Money: effects, an original score and the mix (STUDIO-RULES v3, section 8).

usage: python3 -I audio/ep22_sound.py out/ep22/vo.wav src/episodes/ep22/lines.json out/ep22/mix.wav LEN [--test]
Every effect sits on something that happens on screen: the times below are the same anchors as src/ep/ep22/ep22.tsx
(line starts and ends from lines.json, plus the shot constants copied here). --test ends on a short fade instead of the
cut to black (the cold-open test render). The score is synthesized here (no stock music): a bright explainer bed in
D major under the bait that tape-stops on the smash, a tight pulse in the Booth, an eerie pad and music box after the
switch. A bed runs under everything. Master: -14 LUFS, loudness range 5-7 LU, true peak at or below -1 dBTP; the voice
stays on top (music ducks 6 dB under every line).
"""
import json, subprocess, sys, tempfile, os
import numpy as np, soundfile as sf, pyloudnorm as pyln
sys.path.insert(0, 'audio')
from sfxcore import SR, n_of, tvec, bpf, lpf, hpf, noise, blip, place, sweep, riser

VO, LINES, OUT, LEN = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
TEST = '--test' in sys.argv
_L = json.load(open(LINES))
S = lambda n: _L[n - 1]['start']
E = lambda n: _L[n - 1]['end']
N = n_of(LEN + 0.5)
sfx = np.zeros((2, N)); mus = np.zeros((2, N))
def cue(sig, t, g=1.0, pan=0.0): place(sfx, sig, t, g, pan)
def mcue(sig, t, g=1.0, pan=0.0): place(mus, sig, t, g, pan)
env = lambda n, a, d: np.minimum(1, tvec(n) / a) * np.exp(-tvec(n) / d)

# ---------- shot anchors (keep in step with src/ep/ep22/ep22.tsx) ----------
A_T1, B_T1 = 1.9, 3.9
SHOVE, C_T1, SPIT, LAND = 5.05, 5.4, 6.22, E(1)
F_T1 = S(2) - 0.05
G_T1 = S(3) - 0.1; H_T1 = S(4) - 0.15; I_T1 = S(5) - 0.15; J_T1 = E(5) + 0.25
CRACK = J_T1 + 0.42
K_T1 = S(6) - 0.05; M_T1 = S(7) - 0.1; N_T1 = E(7) + 0.3; O_T1 = S(8) - 0.05
def spin_at(t):
    if t < SHOVE: return 0.25 * t
    u = t - SHOVE; return 0.25 * SHOVE + 2.2 * u + 9.5 * u * u

# ---------- effects kit ----------
def thump(f=70, d=0.45, body=1.0):
    n = n_of(d); t = tvec(n); fr = np.interp(t, [0, 0.12], [f * 1.8, f])
    return body * np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / 0.14) + 0.35 * lpf(noise(n), 900) * np.exp(-t / 0.05)
def step(heavy=1.0):
    n = n_of(0.16); t = tvec(n)
    return heavy * (1.2 * np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.035) + 0.5 * bpf(noise(n), 300, 3500) * env(n, 0.004, 0.03))
def clink(f=2900, d=0.5):
    n = n_of(d); t = tvec(n); return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.48 * t)) * np.exp(-t / 0.09)
def jingle(k=5, spread=0.07, seed=0):
    """a handful of coins shifting in the jar"""
    out = np.zeros(n_of(0.6)); r = np.random.default_rng(seed)
    for i in range(k):
        c = clink(2400 + 1700 * r.random(), 0.4) * (0.4 + 0.6 * r.random()); a = n_of(spread * r.random() * 2)
        out[a:a + len(c)] += c[:len(out) - a]
    return lpf(out, 7000)
def whoosh(d=0.5, lo=400, hi=5000):
    n = n_of(d); t = tvec(n); return bpf(noise(n), lo, hi) * np.sin(np.pi * t / d) ** 2
def creak(d=0.5, f0=320, f1=190):
    n = n_of(d); t = tvec(n); f = np.interp(t, [0, d], [f0, f1]) * (1 + 0.04 * np.sin(2 * np.pi * 31 * t))
    saw = 2 * ((np.cumsum(f) / SR) % 1) - 1
    return bpf(saw, 250, 2400) * np.sin(np.pi * t / d) ** 2 * 0.6
def glass_smash():
    n = n_of(1.2); t = tvec(n)
    body = hpf(noise(n), 1800) * np.exp(-t / 0.06) * 1.2 + bpf(noise(n), 3000, 9000) * np.exp(-t / 0.25) * 0.5
    tines = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / (0.08 + 0.05 * i)) for i, f in enumerate((3300, 4150, 5230, 6100, 7400))) * 0.18
    return body + tines
def coin_spray(d=1.1, k=38, seed=3):
    out = np.zeros(n_of(d)); r = np.random.default_rng(seed)
    for i in range(k):
        tt = (r.random() ** 1.8) * d * 0.85; c = clink(2100 + 2600 * r.random(), 0.35) * (1 - tt / d) * (0.35 + 0.65 * r.random())
        a = n_of(tt); out[a:a + len(c)] += c[:len(out) - a]
    return out
def coin_spin(d, t_fall):
    """the coin rolling round on its edge, then the wobble speeding up as it falls flat (the classic 'waaang')"""
    n = n_of(d); t = tvec(n)
    ring = np.sin(2 * np.pi * 3150 * t) + 0.4 * np.sin(2 * np.pi * 4870 * t)
    rate = np.where(t < t_fall, 6 + 4 * t / t_fall, 10 + 60 * np.maximum(0, (t - t_fall) / (d - t_fall)) ** 1.5)
    am = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * np.cumsum(rate) / SR))
    roll = bpf(noise(n), 1500, 6000) * 0.25
    e = np.minimum(1, t / 0.05) * np.where(t < t_fall, 0.35, 0.35 + 0.65 * (t - t_fall) / (d - t_fall))
    return (ring * 0.25 + roll) * am * e
def crack():
    n = n_of(0.5); t = tvec(n)
    return hpf(noise(n), 2500) * np.exp(-t / 0.025) + sum(np.sin(2 * np.pi * f * t) * np.exp(-t / 0.12) for f in (3100, 4270, 5650)) * 0.15
def shimmer(d=1.6):
    n = n_of(d); t = tvec(n)
    return sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate((1174.7, 1760.0, 2349.3, 2960.0))) * np.minimum(1, t / 0.25) * np.exp(-t / 0.6) * 0.25
def whoomph(d=0.9):
    n = n_of(d); t = tvec(n); return lpf(noise(n), 400) * np.exp(-t / 0.3) + np.sin(2 * np.pi * np.cumsum(np.interp(t, [0, d], [90, 40])) / SR) * np.exp(-t / 0.35)
def squelch():
    n = n_of(0.09); s = 0.5 * bpf(noise(n), 1500, 4000) * env(n, 0.002, 0.03)
    b = blip(2200, 0.05, 0.02); s[:len(b)] += 0.3 * b; return s
def rustle(d=0.35):
    n = n_of(d); t = tvec(n); return bpf(noise(n), 1200, 5500) * np.sin(np.pi * t / d) ** 1.5

# ---------- 0:00 bait: Alfie's steps, the jar clinking on every one ----------
for k in range(int(A_T1 / 0.34) + 1):
    t = 0.0 + 0.34 * k; cue(step(0.55), t, 0.35, -0.1 + 0.05 * k); cue(jingle(5, 0.05, k), t + 0.02, 0.32, 0.25)
cue(whoosh(0.3), A_T1 - 0.15, 0.2)
for k in range(int((B_T1 - A_T1) / 0.36) + 1):
    t = A_T1 + 0.36 * k; cue(step(0.5), t, 0.28, -0.4); cue(jingle(4, 0.05, 40 + k), t + 0.02, 0.26, -0.3)
for k in range(5): cue(step(1.25), A_T1 + 0.05 + 0.27 * k, 0.3, 0.4)            # Mate jogs ahead
for t in np.arange(0.4, SHOVE, 1.3): cue(creak(0.6, 260, 230), t, 0.12, 0.2)     # the door drifting round
cue(whoosh(0.3), B_T1 - 0.15, 0.2)
# ---------- 0:03.9 the wind-up and the shove ----------
cue(sweep(160, 480, 0.5) * np.sin(np.pi * tvec(n_of(0.5)) / 0.5) * 0.3, SHOVE - 0.5, 0.5, 0.3)
cue(thump(85, 0.4, 1.0), SHOVE, 0.75, 0.3); cue(creak(0.35, 420, 300), SHOVE + 0.02, 0.4, 0.2)
# every time a wing passes the front, a whoosh: they bunch up as the door speeds up
k = int(spin_at(SHOVE) / (np.pi / 2)) + 1
for t in np.arange(SHOVE, SPIT, 0.004):
    if spin_at(t) >= k * np.pi / 2:
        cue(whoosh(0.22, 500, 6000), t - 0.08, 0.32 + 0.25 * (t - SHOVE) / (SPIT - SHOVE), 0.6 * np.sin(k)); k += 1
for t in np.arange(C_T1, SPIT, 0.12): cue(jingle(3, 0.03, int(t * 100)), t, 0.2, 0.0)  # coins rattling round with him
cue(whoosh(0.45, 300, 4000), SPIT - 0.05, 0.7, -0.4)                                  # spat out
# ---------- 0:06.6 the smash on "that-" (the redirection) and the stillness ----------
cue(glass_smash(), LAND, 1.0, -0.2); cue(thump(60, 0.6, 1.2), LAND, 0.9, -0.4)         # jar and Alfie hit the pavement
cue(coin_spray(1.1), LAND + 0.02, 0.6, -0.1)
ROLL0, ROLL1 = LAND + 0.05, F_T1 - 0.05
cue(coin_spin(ROLL1 - ROLL0 + 0.1, 0.8 * (ROLL1 - ROLL0)), ROLL0, 0.55, 0.2)
cue(clink(3000, 0.3), ROLL1 + 0.04, 0.35, 0.2)                                          # it settles flat
# ---------- 0:07.8 Mate ----------
cue(rustle(0.4), G_T1 - 0.9, 0.3, 0.3)                                                   # hand to the back of his head
cue(whoosh(0.3), G_T1 - 0.12, 0.2)
# ---------- the Booth ----------
for t in (S(3) - 0.12, S(5) - 0.12): cue(squelch(), t, 0.35, 0.5)
cue(whoosh(0.3), H_T1 - 0.12, 0.18); cue(whoosh(0.3), I_T1 - 0.12, 0.18)
cue(riser(1.1, 600, 950) * 0.6, CRACK - 1.1, 0.45)                                       # the pin wakes up
cue(whoosh(0.3), J_T1 - 0.12, 0.22)
# ---------- 0:14.8 the switch ----------
cue(crack(), CRACK, 0.85); cue(whoomph(1.0), CRACK, 0.9); cue(shimmer(1.8), CRACK + 0.02, 0.5)
cue(whoosh(0.3), K_T1 - 0.12, 0.22)
# ---------- 0:15.3 the what-if bank hall: scooping coins back into the taped jar ----------
for i, t in enumerate(np.arange(K_T1 + 0.2, M_T1, 0.4)): cue(jingle(6, 0.06, 90 + i), t, 0.4, -0.2)
cue(whoosh(0.3), M_T1 - 0.12, 0.2)
for k in range(2): cue(step(1.2), M_T1 + 0.1 + 0.3 * k, 0.25, 0.3)                       # Mate steps up to look
cue(whoosh(0.3), N_T1 - 0.12, 0.2)
cue(blip(2637, 0.3, 0.1) * 0.7, N_T1 + 0.35, 0.3); cue(blip(3520, 0.25, 0.08) * 0.5, N_T1 + 0.47, 0.25)  # the NAN label 'ting'


# ======================= act 2 (src/ep/ep22/act2.tsx): same anchors as the shots =======================
W = json.load(open(LINES.replace('lines.json', 'words.json')))
word_at = lambda txt, after=0: next(w['start'] for w in W if w['text'].replace('*', '').startswith(txt) and w['start'] >= after)
TITLE = word_at("Britain's", 22)
P2_T1 = S(9) - 1.7; Q1_T0 = P2_T1; SLAP = Q1_T0 + 0.95
Q2_T1 = S(10) - 0.05; Q3_T1 = S(11) - 0.1; Q4_T1 = S(12) - 0.2
R1_T0 = Q4_T1; R1_T1 = 34.3; R2_T1 = S(13) - 0.05; R4_T1 = S(14) - 0.1; R5_T1 = S(15) - 1.0
S1_T1 = S(15) - 0.05; S2_T1 = S(16) - 0.1; S4_T1 = 47.0
T1_T1 = 48.6; TYPE0, TYPE1 = 48.95, 49.4; REAL = (TYPE1 - 0.05, TYPE1 + 0.3)
T5_T1 = S(22) - 0.1; DEL0 = word_at('vanishes', 54) - 0.25; DEL1 = word_at('vanishes', 54) + 0.1; T6_T1 = DEL0 - 0.35
T7_T1 = S(23) - 0.05; CUT = E(24)
def key_click():
    n = n_of(0.05); return bpf(noise(n), 1800, 6500) * env(n, 0.001, 0.008)
def clang():
    n = n_of(1.6); t = tvec(n)
    body = np.zeros(n); th = thump(55, 0.8, 1.2); body[:len(th)] = th
    return sum(np.sin(2 * np.pi * f * t) * np.exp(-t / (0.5 / (i + 1))) * (0.6 ** i) for i, f in enumerate((180, 297, 431, 612, 845))) + 0.6 * body
def rattle(d=0.45):
    n = n_of(d); t = tvec(n); return bpf(noise(n), 300, 3000) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 38 * t))) * np.minimum(1, t / 0.02)
def thunder(d=2.5):
    n = n_of(d); t = tvec(n); return lpf(noise(n), 160) * np.exp(-t / 0.9) * (1 + 0.6 * np.sin(2 * np.pi * 2.3 * t)) * np.minimum(1, t / 0.08)
def knock():
    n = n_of(0.25); t = tvec(n); return np.sin(2 * np.pi * 820 * t) * np.exp(-t / 0.04) + bpf(noise(n), 900, 5000) * np.exp(-t / 0.015)
def poof():
    n = n_of(0.6); t = tvec(n); return sweep(1400, 220, 0.6) * np.exp(-t / 0.25) * 0.5 + bpf(noise(n), 600, 4000) * np.exp(-t / 0.12) * 0.4
def ding():
    n = n_of(0.8); t = tvec(n); return (np.sin(2 * np.pi * 1760 * t) + 0.4 * np.sin(2 * np.pi * 2640 * t)) * np.exp(-t / 0.3)
def zap(d=0.35):
    n = n_of(d); t = tvec(n); return (bpf(noise(n), 2000, 9000) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 60 * t))) + 0.3 * np.sign(np.sin(2 * np.pi * 120 * t))) * np.minimum(1, np.minimum(t, d - t) / 0.01)

if not TEST:
    # the title slam
    cue(thump(50, 0.9, 1.4), TITLE, 0.9); cue(whoomph(0.8), TITLE, 0.6)
    cue(whoosh(0.3), 23.95 - 0.12, 0.2); cue(whoosh(0.3), P2_T1 - 0.12, 0.2)
    # beat 1: the jar lands on the counter, the label slapped on, slid along, the Builder off with it
    cue(thump(110, 0.35, 0.9), Q1_T0 + 0.35, 0.6); cue(jingle(7, 0.05, 200), Q1_T0 + 0.36, 0.5)
    cue(hpf(noise(n_of(0.12)), 1500) * env(n_of(0.12), 0.001, 0.02), SLAP, 0.7); cue(rustle(0.25), SLAP + 0.02, 0.4)
    cue(whoosh(0.3), S(9) - 0.12, 0.2)
    cue(bpf(noise(n_of(0.8)), 400, 3000) * np.sin(np.pi * tvec(n_of(0.8)) / 0.8), S(9) + 0.1, 0.45, 0.4)   # the jar sliding along the counter
    cue(jingle(5, 0.05, 210), S(9) + 0.9, 0.4, 0.5)
    for t in (Q2_T1 - 0.12, Q3_T1 - 0.12): cue(whoosh(0.3), t, 0.2)
    cue(jingle(8, 0.06, 220), Q3_T1 + 0.15, 0.5, 0.3)                                     # the hug
    for k in range(5): cue(step(0.8), Q3_T1 + 1.15 + 0.3 * k, 0.32, 0.4 + 0.1 * k); cue(jingle(3, 0.03, 230 + k), Q3_T1 + 1.17 + 0.3 * k, 0.25, 0.5)
    # beat 2: the vault wheel, the door swinging, Mate flattened; the echo inside
    cue(whoosh(0.3), R1_T0 - 0.12, 0.2)
    cue(creak(0.6, 200, 140), R1_T0 + 0.05, 0.6); cue(creak(0.5, 150, 110), R1_T0 + 0.35, 0.5)
    cue(clang(), R1_T0 + 0.7, 0.8, 0.4); cue(thump(70, 0.5, 1.0), R1_T0 + 0.72, 0.6, 0.4)
    cue(whoosh(0.3), R1_T1 - 0.12, 0.2)
    cue(whoosh(0.3), R2_T1 - 0.12, 0.15); cue(ding() * 0.6, R2_T1 + 0.1, 0.3)             # the board
    cue(squelch(), R4_T1 + 0.45, 0.5, 0.4); cue(rustle(0.4), R4_T1 + 0.5, 0.4, 0.4)       # Mate peels off the wall
    # beat 3: rain, thunder, Nan's stick on the glass, the shutter slammed
    cue(whoosh(0.3), R5_T1 - 0.12, 0.25); cue(thunder(2.6), R5_T1 + 0.05, 0.7)
    for k, t in enumerate((0.25, 0.75, 1.3)): cue(knock(), S1_T1 + t, 0.6, -0.1)
    cue(rattle(0.42), S2_T1 + 0.15, 0.7); cue(thump(65, 0.6, 1.3), S2_T1 + 0.55, 1.0); cue(clang() * 0.4, S2_T1 + 0.56, 0.5)
    # the twist: keys, the £20,000 appearing, the split second of the real Britain, the deletion
    cue(whoosh(0.3), S4_T1 - 0.12, 0.2)
    for t in np.arange(S4_T1 + 1.1, S4_T1 + 1.6, 0.12): cue(key_click(), t, 0.5, 0.2)
    for t in np.arange(T1_T1 + 0.1, TYPE1 + 0.05, 0.12): cue(key_click(), t, 0.55, 0.2)
    cue(ding(), TYPE1, 0.45)
    for t in np.arange(T5_T1 + 0.5, T6_T1, 0.12): cue(key_click(), t, 0.45, 0.2)
    for t in np.arange(DEL0, DEL1, 0.06): cue(key_click(), t, 0.55, 0.2)
    cue(poof(), DEL1, 0.6)
    for t in (T1_T1, 50.3, S(20) - 0.05, S(21) - 0.1, T5_T1, T6_T1): cue(whoosh(0.25), t - 0.1, 0.15)
    # the cliffhanger: the pin crackles; heartbeat into the cut
    cue(whoosh(0.3), T7_T1 - 0.12, 0.25)
    for t in (T7_T1 + 0.2, T7_T1 + 0.7, T7_T1 + 1.2): cue(zap(0.3), t, 0.5)
    cue(riser(CUT - T7_T1, 300, 1200) * 0.7, T7_T1, 0.5)

# ---------- room tone under everything (street, booth, hall, vault, rain) ----------
tt_ = tvec(N)
if TEST: R1_T0, R5_T1, S4_T1 = 1e9, 1e9, 1e9
street = (tt_ < G_T1) | ((tt_ >= J_T1) & (tt_ < K_T1))
booth = (tt_ >= G_T1) & (tt_ < J_T1)
vault = (tt_ >= R1_T0) & (tt_ < R5_T1)
rain_ = (tt_ >= R5_T1) & (tt_ < S4_T1)
hall = (tt_ >= K_T1) & ~vault & ~rain_
room = (street * (lpf(noise(N), 900) * 0.06 + lpf(noise(N), 160) * 0.05)
        + booth * (0.03 * np.sin(2 * np.pi * 50 * tt_) + lpf(noise(N), 300) * 0.03)
        + hall * (bpf(noise(N), 200, 1400) * 0.045 * (0.8 + 0.2 * np.sin(2 * np.pi * 0.3 * tt_)))
        + vault * (lpf(noise(N), 220) * 0.06 + 0.02 * np.sin(2 * np.pi * 60 * tt_))
        + rain_ * (bpf(noise(N), 1500, 9000) * 0.09 + lpf(noise(N), 400) * 0.04))
if not TEST:
    real = (tt_ >= REAL[0]) & (tt_ < REAL[1])                     # the real Britain: a bright street for a split second
    room = room * ~real + real * (lpf(noise(N), 900) * 0.06)
    room[n_of(CUT):] = 0
place(sfx, room, 0, 1.0)
for t in np.arange(0.8, LAND, 2.3): cue(bpf(noise(n_of(1.2)), 300, 2000) * np.sin(np.pi * tvec(n_of(1.2)) / 1.2) ** 2, t, 0.12, 0.7)  # passing traffic

# ---------- the score ----------
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
BPM = 120; beat = 60 / BPM
def mallet(f, d=0.5, g=1.0):
    n = n_of(d); t = tvec(n)
    return g * (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.2) + 0.25 * np.sin(2 * np.pi * f * 3.9 * t) * np.exp(-t / 0.05)) * np.minimum(1, t / 0.002)
def pluck(f, d=0.35):
    n = n_of(d); t = tvec(n); return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t / 0.09) * np.minimum(1, t / 0.002)
def bass(f, d=0.45):
    n = n_of(d); t = tvec(n); return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.18) * np.minimum(1, t / 0.005)
# bait: D major explainer bed, D - Bm - G - A, a skipping mallet line with plucked offbeats
bars = [[62, 66, 69, 74], [59, 62, 66, 71], [55, 59, 62, 67], [57, 61, 64, 69]]
bait = np.zeros((2, N)); t = 0.0; i = 0
while t < LAND + 0.4:
    ch = bars[int(t / (4 * beat)) % 4]
    pat = [0, 2, 3, 1, 2, 3, 1, 2][i % 8]
    place(bait, mallet(hz(ch[pat] + 12), 0.45, 0.5), t, 1.0, 0.25 if i % 2 else -0.25)
    if i % 2 == 0: place(bait, bass(hz(ch[0] - 24)), t, 0.9)
    if i % 4 == 3: place(bait, pluck(hz(ch[2] + 24)), t, 0.45, 0.4)
    if i % 2 == 1: place(bait, hpf(noise(n_of(0.04)), 7000) * env(n_of(0.04), 0.001, 0.01), t, 0.18)
    t += beat / 2; i += 1
# tape stop on the smash: playback slows to nothing over 0.4 s
T0, TS = LAND, 0.4
k0 = n_of(T0); kk = np.arange(n_of(TS)); rate = 1 - kk / len(kk); pos = k0 + np.cumsum(rate)
stop = np.vstack([np.interp(pos, np.arange(N), bait[c]) for c in range(2)]) * np.linspace(1, 0.2, len(kk))
bait[:, k0:] = 0; bait[:, k0:k0 + len(kk)] = stop
mus += bait
# the stillness bed: one low held note under the rolling coin, so there is never dead air
ht = tvec(n_of(F_T1 - LAND + 0.4)); hold = np.sin(2 * np.pi * hz(38) * ht) * np.minimum(1, ht / 0.3) * np.minimum(1, (ht[-1] - ht) / 0.3)
mcue(hold * 0.4, LAND + 0.1)
# the Booth: a low pulse that tightens toward the pin, over a drone
B0, B1 = G_T1, J_T1
gap = 60 / 76; tt = B0; j = 0
while tt < B1:
    place(mus, thump(50, 0.5, 0.9) * (0.5 + 0.1 * j), tt, 0.45); gap = max(0.42, gap * 0.95); tt += gap; j += 1
dt = tvec(n_of(B1 - B0))
drone = (np.sin(2 * np.pi * 58.3 * dt) + 0.6 * np.sin(2 * np.pi * 87.3 * dt)) * np.minimum(1, dt / 0.6) * np.minimum(1, (B1 - B0 - dt) / 0.3) * (0.75 + 0.25 * np.sin(2 * np.pi * 1.1 * dt))
mcue(drone * 0.35, B0)
# after the switch: an eerie pad (B minor add 9) and a music box line, through Nan's jar
P0, P1 = CRACK + 0.05, (LEN + 0.4 if TEST else TITLE + 0.1)
pt = tvec(n_of(P1 - P0))
pad = sum(np.sin(2 * np.pi * f * pt) + np.sin(2 * np.pi * f * 1.004 * pt) for f in (246.9, 293.7, 370.0, 554.4)) * np.minimum(1, pt / 0.8) * np.minimum(1, (P1 - P0 - pt) / 0.3) * 0.12
mcue(lpf(pad, 2200), P0, 1.0)
def mbox(m):
    n = n_of(0.9); t2 = tvec(n)
    return (np.sin(2 * np.pi * hz(m) * t2) + 0.3 * np.sin(2 * np.pi * hz(m) * 2 * t2)) * np.exp(-t2 / 0.35) * np.minimum(1, t2 / 0.002)
for k, m in enumerate((83, 78, 81, 74, 76, 78, 81, 83, 86)):
    mcue(mbox(m), CRACK + 0.8 + 0.85 * k, 0.3, 0.3 * (-1) ** k)
# into the title (full episode) / end of the test: a riser from the NAN jar
R0 = N_T1 + 0.2
mcue(riser(max(0.5, O_T1 - R0), 400, 900) * 0.5, R0, 0.6)

if not TEST:
    # the title: a big B minor add 9 stab
    st = tvec(n_of(2.4))
    stab = sum(np.sin(2 * np.pi * f * st) * a_ for f, a_ in ((123.5, 1.0), (246.9, 0.8), (293.7, 0.6), (370.0, 0.6), (554.4, 0.4), (740.0, 0.3))) * np.exp(-st / 0.8) * np.minimum(1, st / 0.004)
    mcue(lpf(stab, 3000) * 0.5, TITLE)
    # the ladder: a B minor groove at 108 bpm from the counter through the vault; the vault adds a kick and a clap
    G0, G1 = TITLE + 1.4, R5_T1 + 0.05
    gb = 60 / 108
    prog4 = [[59, 62, 66], [55, 59, 62], [57, 61, 64], [54, 57, 61]]                # Bm G A F#m
    groove = np.zeros((2, N)); tt = G0; i = 0
    while tt < G1:
        ch = prog4[int((tt - G0) / (4 * gb)) % 4]; vault_part = tt >= R1_T0
        if i % 2 == 0: place(groove, bass(hz(ch[0] - 12), 0.4) * 0.9, tt, 1.0)
        if i % 2 == 1: place(groove, mallet(hz(ch[(i // 2) % 3] + 24), 0.4, 0.35), tt, 1.0, 0.3 * (-1) ** i)
        if i % 4 == 3: place(groove, pluck(hz(ch[1] + 12)), tt, 0.35, -0.3)
        if vault_part:
            if i % 4 == 0: place(groove, thump(60, 0.3, 1.0), tt, 0.7)
            if i % 4 == 2: place(groove, bpf(noise(n_of(0.12)), 900, 6000) * env(n_of(0.12), 0.001, 0.035), tt, 0.5)
        tt += gb / 2; i += 1
    fade = np.ones(N); a_, b_ = n_of(G1 - 0.3), n_of(G1); fade[a_:b_] = np.linspace(1, 0, b_ - a_); fade[b_:] = 0; fade[:n_of(G0)] = 0
    mus += groove * fade
    # the run on the bank: a driving low pulse with a timpani hit on every bar, under the rain
    D0, D1 = R5_T1, S4_T1 + 0.2
    db = 60 / 132; tt = D0; i = 0
    while tt < D1:
        place(mus, thump(48, 0.35, 1.0), tt, 0.45 + (0.25 if i % 4 == 0 else 0))
        if i % 2 == 1: place(mus, pluck(hz(47 + (i // 8) % 2 * 2) * 2, 0.25), tt, 0.3, 0.2)
        tt += db / 2; i += 1
    dt = tvec(n_of(D1 - D0)); mcue(lpf(sum(np.sin(2 * np.pi * f * dt) for f in (61.7, 92.5)) * np.minimum(1, dt / 0.3) * np.minimum(1, (D1 - D0 - dt) / 0.2) * 0.3, 500), D0)
    # the dropout: no music from the shutter's echo until "...that we don't lend out your money"
    # the twist: a tender pad (G, then E minor) with a music box; it cuts out for the split second of the real Britain
    W0, W1 = S(18) - 0.05, T7_T1
    wt = tvec(n_of(W1 - W0)); half = (W1 - W0) / 2
    chord = lambda fs: sum(np.sin(2 * np.pi * f * wt) + np.sin(2 * np.pi * f * 1.003 * wt) for f in fs)
    tender = np.where(wt < half, chord((196.0, 246.9, 293.7, 370.0)), chord((164.8, 196.0, 246.9, 293.7)))
    tender = lpf(tender, 1800) * np.minimum(1, wt / 0.5) * np.minimum(1, (W1 - W0 - wt) / 0.2) * 0.11
    tender[n_of(REAL[0] - W0):n_of(REAL[1] - W0)] = 0
    mcue(tender, W0)
    for t2, m_ in ((W0 + 0.6, 79), (W0 + 3.3, 74), (W0 + 4.6, 76), (W0 + 6.4, 71), (W0 + 8.1, 74)):
        if not (REAL[0] - 0.5 < t2 < REAL[1]): mcue(mbox(m_), t2, 0.22, -0.2)
    # the cliffhanger: a low pulse that speeds up and a string-like swell, peaking at the cut
    tt3, gap = T7_T1, 0.5
    while tt3 < CUT - 0.05:
        place(mus, thump(46, 0.4, 1.0), tt3, 0.55 + 0.45 * (tt3 - T7_T1) / (CUT - T7_T1)); gap = max(0.17, gap * 0.9); tt3 += gap
    ct = tvec(n_of(CUT - T7_T1))
    swell = sum(lpf(2 * ((np.cumsum(np.full(len(ct), f) * (1 + 0.06 * ct / ct[-1])) / SR) % 1) - 1, 2600) for f in (123.5, 185.0, 246.9, 293.7))
    mcue(swell * ((ct / ct[-1]) ** 1.6) * 0.16, T7_T1)

# ---------- mix ----------
vo, vsr = sf.read(VO, always_2d=True)
assert vsr == SR, f"voice must be {SR} Hz"
vo = vo.T
if vo.shape[0] == 1: vo = np.vstack([vo[0], vo[0]])
vo = vo[:, :N] if vo.shape[1] >= N else np.pad(vo, ((0, 0), (0, N - vo.shape[1])))
m = pyln.Meter(SR)
def to_lufs(x, target):
    l = m.integrated_loudness(x.T); return x * 10 ** ((target - l) / 20)
duck = np.ones(N)
for L in _L:
    a, b = n_of(L['start'] - 0.08), n_of(L['end'] + 0.12)
    duck[max(0, a):b] = 0.5
from scipy.ndimage import uniform_filter1d
duck = uniform_filter1d(duck, n_of(0.08))
mus = to_lufs(mus, -29.0) * duck
sfx = to_lufs(sfx, -24.0)
mix = vo + mus + sfx
if not TEST:   # dynamics that follow the story: the keyboard twist is hushed, the cliffhanger is the loudest moment
    ride = np.zeros(N)
    def seg(t0, t1, db, ramp=0.4):
        k = np.clip(np.minimum((tvec(N) - t0) / ramp, (t1 - tvec(N)) / ramp), 0, 1); return k * db
    ride += seg(S(18) - 0.3, T7_T1, -2.5) + seg(T7_T1 - 0.1, CUT + 0.3, 3.0, 0.8) + seg(LAND + 0.2, S(2) - 0.1, -2.0, 0.2)
    mix = mix * 10 ** (ride / 20)
if TEST:
    a = n_of(LEN - 0.35); mix[:, a:n_of(LEN)] *= np.linspace(1, 0, n_of(LEN) - a); mix[:, n_of(LEN):] = 0
else:
    mix[:, n_of(CUT):] = 0          # the hard cut to black: silence
mix = to_lufs(mix[:, :n_of(LEN)], -14.0)
tmp = tempfile.mktemp(suffix='.wav')
sf.write(tmp, mix.T.astype(np.float32), SR, subtype='FLOAT')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'alimiter=limit=0.79:attack=2:release=50:level=disabled', '-c:a', 'pcm_f32le', OUT], check=True)
os.remove(tmp)
e = subprocess.run(['ffmpeg', '-i', OUT, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
summ = e[e.rfind('Summary'):]
grab = lambda k: summ.split(k)[1].split('\n')[0].strip() if k in summ else '?'
print(f"{OUT}: {LEN:.2f} s | integrated {grab('I:')} | range {grab('LRA:')} | true peak {grab('Peak:')}")
