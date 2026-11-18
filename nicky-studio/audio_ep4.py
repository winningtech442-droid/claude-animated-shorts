import numpy as np, wave, sys
import os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ep4 as ep1

SR = 44100; T = ep1.TOTAL
L = int(SR * (T + 0.5)); mix = np.zeros(L); music = np.zeros(L)
rng = np.random.default_rng(7)

def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR; e = np.minimum(1, t / a) * np.exp(-t / r); return e
def add(buf, t0, sig, g=1.0):
    i = int(t0 * SR)
    if i >= L: return
    j = min(L, i + len(sig)); buf[i:j] += g * sig[: j - i]
def tone(f, dur, wav="sine"):
    t = np.arange(int(dur * SR)) / SR
    if wav == "sine": return np.sin(2 * np.pi * f * t)
    if wav == "tri": return 2 / np.pi * np.arcsin(np.sin(2 * np.pi * f * t))
    if wav == "sq": return np.sign(np.sin(2 * np.pi * f * t)) * 0.5
def note(m): return 440 * 2 ** ((m - 69) / 12)

# ---- music bed: 120 bpm, C G Am F ----
bpm = 120; beat = 60 / bpm
chords = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
bars = int(T / (4 * beat)) + 1
for b in range(bars):
    ch = chords[b % 4]; t0 = b * 4 * beat
    for k in range(4):  # kick
        n = int(0.25 * SR); t = np.arange(n) / SR
        add(music, t0 + k * beat, np.sin(2 * np.pi * (50 + 90 * np.exp(-t * 30)) * t) * env(n, 0.002, 0.12), 0.55)
        hh = rng.standard_normal(int(0.05 * SR)) * env(int(0.05 * SR), 0.001, 0.015)
        add(music, t0 + k * beat + beat / 2, np.diff(hh, prepend=0), 0.18)
    for k in (1, 3):  # clap
        cl = rng.standard_normal(int(0.12 * SR)) * env(int(0.12 * SR), 0.001, 0.04)
        add(music, t0 + k * beat, cl, 0.12)
    bass = ch[0] - 24
    for k in range(8):
        add(music, t0 + k * beat / 2, tone(note(bass), beat / 2, "tri") * env(int(beat / 2 * SR), 0.005, 0.12), 0.32)
    for k in range(8):  # plucky arp
        m = ch[k % 3] + (12 if k % 4 == 3 else 0)
        add(music, t0 + k * beat / 2, tone(note(m), 0.3, "tri") * env(int(0.3 * SR), 0.003, 0.08), 0.12)
# fade
music[: int(SR * 0.3)] *= np.linspace(0, 1, int(SR * 0.3)); music[int(SR * (T - 1.5)):] *= np.linspace(1, 0, L - int(SR * (T - 1.5)))

# ---- sfx ----
def whoosh(d=0.35):
    n = int(d * SR); x = rng.standard_normal(n); t = np.arange(n) / SR
    x = np.convolve(x, np.ones(20) / 20, "same"); return x * np.sin(np.pi * t / d) ** 2
def pop(f=900):
    n = int(0.09 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * (f + 600 * np.exp(-t * 60)) * t) * env(n, 0.001, 0.03)
def tick(f=1400): return tone(f, 0.07, "sq") * env(int(0.07 * SR), 0.001, 0.02)
def ding():
    s = 0
    for f, g in ((note(84), 1), (note(88), .6), (note(91), .5), (note(96), .3)): s = s + g * tone(f, 1.2)
    return s * env(int(1.2 * SR), 0.002, 0.35)
def chaching():
    s = np.concatenate([tone(note(88), 0.08, "sq") * env(int(.08 * SR), .001, .03), tone(note(95), 0.6, "sine") * env(int(.6 * SR), .001, .2)])
    return s
def slide(f0, f1, d):
    t = np.arange(int(d * SR)) / SR; f = f0 + (f1 - f0) * t / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d)
def crackle(d=1.0):
    n = int(d * SR); x = np.zeros(n); idx = rng.integers(0, n, 120); x[idx] = rng.uniform(-1, 1, 120)
    return np.convolve(x, np.hanning(60), "same") * np.linspace(1, 0, n)

S = {n: s for n, s, d in ep1.SEG}
for n, s, d in ep1.SEG[1:]: add(mix, s - 0.1, whoosh(), 0.35)
add(mix, 0.0, pop(500), 0.6); add(mix, 0.35, pop(1100), 0.5); add(mix, 1.1, pop(800), 0.4)
for i in range(7):
    s = S[f"q{i+1}"]
    for k in range(3): add(mix, s + 0.35 + k * 0.12, pop(700 + k * 200), 0.35)
    for k in range(3): add(mix, s + 1.0 + k, tick(1300 if k < 2 else 1900), 0.4)
    add(mix, s + 4.0, ding(), 0.35); add(mix, s + 4.0, crackle(1.2), 0.25)
c = S["cta"]; add(mix, c + 0.5, pop(900), 0.5); add(mix, c + 2.6, chaching(), 0.4); add(mix, c + 2.6, crackle(1.0), 0.25)
o = S["outro"]
for k in range(3): add(mix, o + 0.3 + k * 0.35, pop(700 + 150 * k), 0.4)
add(mix, o + 1.6, pop(1200), 0.4); add(mix, o + 4.0, pop(1000), 0.4)
add(mix, o + 5.8, slide(500, 1400, 0.8), 0.25); add(mix, o + 6.6, chaching(), 0.45); add(mix, o + 6.6, slide(1400, 400, 0.9), 0.2)

out = 0.5 * music + mix
out = out / np.max(np.abs(out)) * 0.9
pcm = (out * 32767).astype(np.int16)
with wave.open(os.path.join(HERE, "out_ep4", "sound.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("ok", T)
