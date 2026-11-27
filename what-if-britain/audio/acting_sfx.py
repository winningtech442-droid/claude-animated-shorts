"""Sound for the acting test: effects placed on what happens on screen. No music.
usage: python3 -I audio/acting_sfx.py src/tests/actingBeats.ts out/act/sfx.wav"""
import re, sys
import numpy as np, soundfile as sf, pyloudnorm as pyln
sys.path.insert(0, 'audio')
from sfxcore import SR, n_of, tvec, bpf, lpf, hpf, noise, blip, ping, place, sweep

src = open(sys.argv[1]).read()
B = {k: float(v) for k, v in re.findall(r'(\w+): ([\d.]+)', src.split('export const LEN')[0])}
LEN = float(re.search(r'LEN = ([\d.]+)', src).group(1))
TH = [(w, float(a)) for w, a in re.findall(r"who: '(\w+)'.*?t0: ([\d.]+)", src)]
buf = np.zeros((2, n_of(LEN))); log = []
def cue(sig, t, g, name, pan=0.0): place(buf, sig, t, g, pan); log.append((round(t, 2), name))
io = lambda u: 2 * u * u if u < .5 else 1 - (-2 * u + 2) ** 2 / 2

def env_ad(n, a, d):
    t = tvec(n); return np.minimum(1, t / a) * np.exp(-t / d)
def step(heavy=1.0):
    n = n_of(0.16); t = tvec(n)
    thump = np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.035)
    scuff = bpf(noise(n), 300, 3500) * env_ad(n, 0.004, 0.03)
    return heavy * (1.2 * thump + 0.5 * scuff)
def rustle(d=0.4, bright=1.0):
    n = n_of(d); t = tvec(n); e = np.sin(np.pi * t / d) ** 1.5 * (0.6 + 0.4 * np.abs(np.sin(t * 37)))
    return bpf(noise(n), 1200, 5500 * bright) * e
def breath(d, lo, hi, rise):
    n = n_of(d); t = tvec(n); u = t / d
    e = (np.sin(np.pi * u) ** 1.2) * ((0.3 + 0.7 * u) if rise else (1.0 - 0.6 * u))
    return bpf(noise(n), lo, hi) * e
def thunk():
    n = n_of(0.6); t = tvec(n)
    return np.sin(2 * np.pi * sweep_f(t)) * np.exp(-t / 0.18) + 0.25 * bpf(noise(n), 60, 400) * np.exp(-t / 0.05)
def sweep_f(t): return np.cumsum(np.interp(t, [0, 0.15], [120, 55])) / SR
def bubble(f=880):
    n = n_of(0.18); t = tvec(n); fr = f * (1 + 0.35 * np.minimum(1, t / 0.05))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * env_ad(n, 0.006, 0.05)
def crack():
    n = n_of(0.5); t = tvec(n)
    snap = hpf(noise(n), 2500) * np.exp(-t / 0.025)
    splinter = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / 0.12) for f in (3100, 4270, 5650)) * 0.15
    return snap + splinter
def shimmer(d=1.6):
    n = n_of(d); t = tvec(n)
    return sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate((1318.5, 1975.5, 2637.0, 3136.0))) * np.minimum(1, t / 0.25) * np.exp(-t / 0.6) * 0.25

# room tone: a quiet air bed under everything (keeps silence from sounding dead)
bed = lpf(noise(n_of(LEN)), 500) * 0.08 + lpf(noise(n_of(LEN)), 120) * 0.05
cue(bed, 0, 1, 'room tone')

# dots: one soft pop per dot, pitch climbing; past Nan's 3.6 they turn tense
def dots(t0, t1, total, ease, base, tense_from=None):
    for i in range(1, int(round(total * 10)) + 1):
        lo, hi = 0.0, 1.0
        for _ in range(30):  # when does value reach i/10?
            m = (lo + hi) / 2
            (lo, hi) = (m, hi) if total * ease(m) * 10 < i - 0.5 else (lo, m)
        t = t0 + (t1 - t0) * hi
        f = base * 2 ** (i / 40)
        g = 0.22
        if tense_from and i > tense_from * 10: f *= 0.94; g = 0.28
        cue(blip(f, 0.05, 0.016), t, g, 'dot', pan=-0.3 + 0.6 * (i % 10) / 10)
dots(B['nanFill0'], B['nanLand'], 3.6, io, 700)
cue(ping(1046.5, 1.2), B['nanLand'], 0.35, 'land ping (Nan)')
cue(rustle(0.4, 0.7), B['nanLand'] - 0.1, 0.22, 'Nan settles')

cue(bpf(noise(n_of(1.2)), 250, 3000) * np.sin(np.pi * tvec(n_of(1.2)) / 1.2) ** 2, B['glide1'], 0.12, 'camera glide air')
dots(B['alfFill0'], B['alfLand'], 7.6, lambda u: u, 620, tense_from=3.6)
cue(rustle(0.5, 0.8), B['alfPass'] - 0.2, 0.18, 'lean in')
cue(thunk(), B['alfLand'], 0.9, 'land thunk (7.6)')
cue(ping(784, 1.6), B['alfLand'], 0.28, 'land ping')
# recoil: grab head, step back
cue(rustle(0.35, 1.2), B['alfLand'] + 0.3, 0.35, 'arms up')
cue(step(0.9), B['alfLand'] + 0.45, 0.55, 'step back')
cue(step(0.7), B['alfLand'] + 0.62, 0.45, 'step back')
# the sigh: in through the nose... and out
cue(breath(0.75, 900, 4200, True), B['sigh'] + 0.05, 0.35, 'breath in')
cue(breath(1.25, 250, 1800, False), B['slump'] - 0.1, 0.42, 'sigh out')
cue(rustle(0.6, 0.6), B['slump'] + 0.05, 0.25, 'slump')
# Mate walks in
for i, dt in enumerate((0.15, 0.48, 0.8)):
    cue(step(0.8), B['mateIn'] + dt, 0.45, 'Mate step', pan=0.5)
cue(rustle(0.45, 0.9), B['mateIn'] + 1.0, 0.3, 'arms cross', pan=0.5)
# thoughts: a soft bubble as each one appears
for who, t in TH:
    cue(bubble(1175 if who == 'lead' else 988 if who == 'nan' else 880), t - 0.05, 0.25, f'thought ({who})', pan=-0.2 if who == 'nan' else 0.3 if who == 'mate' else 0)
# the timeline switch
cue(crack(), B['switch'], 0.6, 'crack')
cue(shimmer(), B['switch'] + 0.05, 0.5, 'shimmer')
cue(bpf(noise(n_of(1.0)), 150, 900) * np.exp(-tvec(n_of(1.0)) / 0.35), B['switch'], 0.3, 'air drop')
# hope: chest opens, dip, step forward
cue(breath(0.6, 900, 4000, True), B['hope'] + 0.2, 0.3, 'hopeful breath')
cue(rustle(0.4, 1.0), B['hope'] + 0.85, 0.3, 'arms open')
cue(step(1.0), B['hope'] + 1.15, 0.55, 'step forward'); cue(step(0.8), B['hope'] + 1.4, 0.45, 'step')
cue(rustle(0.35, 1.1), B['hope'] + 1.4, 0.3, 'Mate hands to mouth', pan=0.5)

# master: -14 LUFS with headroom
m = pyln.Meter(SR); lufs = m.integrated_loudness(buf.T)
buf *= 10 ** ((-16 - lufs) / 20); pk = np.abs(buf).max()
if pk > 0.89: buf *= 0.89 / pk
sf.write(sys.argv[2], buf.T.astype(np.float32), SR)
print(f'{sys.argv[2]}: {len(log)} cues, {m.integrated_loudness(buf.T):.1f} LUFS, peak {20*np.log10(np.abs(buf).max()):.1f} dBFS')
