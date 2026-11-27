"""EP21 Mattress Money: effects, an original score and the mix (STUDIO-RULES v3, section 8).

usage: python3 -I audio/ep21_sound.py out/ep21/vo.wav src/episodes/ep21/lines.json out/ep21/mix.wav LEN
Every effect sits on something that happens on screen (times match src/ep/ep21/ep21.tsx). The score is synthesized
here: a bouncy explainer bed under the bait that tape-stops at the redirection, a tense pulse in the Booth, an eerie
music-box pad after the switch. A bed runs under everything (no dead air). Master: -14 LUFS, loudness range 5-7 LU,
true peak at or below -1 dBTP; the voice stays clearly on top (music ducks under every line).
"""
import json, subprocess, sys, tempfile, os
import numpy as np, soundfile as sf, pyloudnorm as pyln
sys.path.insert(0, 'audio')
from sfxcore import SR, n_of, tvec, bpf, lpf, hpf, noise, blip, place, sweep, riser

VO, LINES, OUT, LEN = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
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

# ---------- room tone under everything ----------
room = lpf(noise(N), 700) * 0.05 + lpf(noise(N), 140) * 0.04
booth = np.where((tvec(N) > 9.5) & (tvec(N) < 14.62), 1.0, 0.0)
room = room * (1 - 0.5 * booth) + booth * (0.03 * np.sin(2 * np.pi * 50 * tvec(N)) + lpf(noise(N), 300) * 0.03)
place(sfx, room, 0, 1.0)

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
# after the switch: an eerie pad (A minor add 9) and a music box
pd = LEN + 0.4 - 14.95
pt = tvec(n_of(pd))
pad = sum(np.sin(2 * np.pi * f * pt) + np.sin(2 * np.pi * f * 1.004 * pt) for f in (220.0, 261.6, 329.6, 493.9)) * np.minimum(1, pt / 0.8) * 0.12
mcue(lpf(pad, 2200), 14.95, 1.0)
for tt, m in ((15.6, 76), (16.5, 72), (17.4, 71), (18.3, 69), (19.2, 72)):
    n = n_of(0.9); t2 = tvec(n)
    mcue((np.sin(2 * np.pi * hz(m) * t2) + 0.3 * np.sin(2 * np.pi * hz(m) * 2 * t2)) * np.exp(-t2 / 0.35) * np.minimum(1, t2 / 0.002), tt, 0.3, 0.3)

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
