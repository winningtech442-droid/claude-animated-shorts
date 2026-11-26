# Original background music for the Phoneverse "Cheers, Biscuit" short.
# UK-garage / 2-step feel, F minor, 132 bpm, composed and synthesized here (numpy + scipy, the repo's own DSP kit).
# One theme, four loopable scene beds + three stings, so the editor can fit any voice timing:
#   A_hook     4 bars  muffled beat, "from a passing car" (lowpassed), sits under the hook
#   B_snatch   8 bars  full 2-step: kick, clap, swung hats, bass, organ stabs  (bump -> struggle -> split -> "follow ME")
#   C_journey  8 bars  sneaky: rim + shaker, bass, plucked riff with echo; clap enters bar 5 (phone's journey montage)
#   D_sofa     8 bars  cosy: warm pad, soft hats, round bass, lowpassed (three months later, the sofa)
#   sting_tapestop  the sofa groove slowing to a stop (on Jess: "...bit late for that")
#   sting_biscuit   low drone + dark low note swell (the warehouse, "Cheers, Biscuit")
#   sting_jess      reverse swell into a boom hit (the scream "JESS!")
# Usage: python music_garage.py  -> writes out/*.wav (48 kHz stereo 24-bit) + out/music_preview.wav
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "templates", "audio"))
from dsp import SR, TAU, ns, rng, lp, hp, bp, pan, place, make_ir, convolve_st, integrated, dbg, write_wav  # noqa: E402
import instruments as I  # noqa: E402

BPM = 132.0
BEAT = 60.0 / BPM
STEP = BEAT / 4  # 16th note
BAR = BEAT * 4
SWING = 0.24 * STEP  # 2-step shuffle: every second 16th is late
OUT = os.path.join(HERE, "out")

# one bar per chord: i - VI - iv - V7 in F minor
PROG = [
    dict(name="Fm9", bass=41, stab=[53, 56, 60, 63, 67]),
    dict(name="Dbmaj9", bass=37, stab=[53, 56, 60, 61, 65]),
    dict(name="Bbm9", bass=34, stab=[53, 56, 58, 61, 65]),
    dict(name="C7b9", bass=36, stab=[52, 55, 58, 61, 64]),
]


def t_of(bar, step):
    return bar * BAR + step * STEP + (SWING if step % 2 else 0.0)


def env_exp(n, tau):
    return np.exp(-np.arange(n) / SR / tau)


# ---------------------------------------------------------------- drum voices
def kick(vel=1.0):
    n = ns(0.42)
    t = np.arange(n) / SR
    f = 46 + 120 * np.exp(-t / 0.032)
    ph = np.cumsum(TAU * f / SR)
    body = np.sin(ph) * np.exp(-t / 0.26)
    click = hp(rng(1).standard_normal(n), 3000) * np.exp(-t / 0.0018) * 0.35
    body = body * np.exp(-t / 0.20) / np.exp(-t / 0.26)
    y = np.tanh(1.8 * (body + click)) * vel * 0.55
    y[: ns(0.001)] *= np.linspace(0, 1, ns(0.001))
    return y


def clap(vel=1.0, seed=0):
    r = rng(seed)
    n = ns(0.35)
    t = np.arange(n) / SR
    nz = bp(r.standard_normal(n), 900, 7000, 2)
    e = np.zeros(n)
    for k, d in enumerate([0.0, 0.010, 0.021]):
        i = ns(d)
        e[i:] += np.exp(-(t[: n - i]) / 0.0055) * (0.75 if k < 2 else 1.0)
    i = ns(0.021)
    e[i:] += 0.55 * np.exp(-(t[: n - i]) / 0.085)
    return nz * e * vel * 1.4


def hat(vel=0.5, open_=False, seed=0):
    r = rng(seed)
    n = ns(0.22 if open_ else 0.06)
    t = np.arange(n) / SR
    nz = hp(r.standard_normal(n), 7500, 2) + 0.4 * bp(r.standard_normal(n), 9000, 14000, 1)
    return nz * np.exp(-t / (0.09 if open_ else 0.018)) * vel * 0.9


def shaker(vel=0.4, seed=0):
    r = rng(seed)
    n = ns(0.07)
    t = np.arange(n) / SR
    e = np.sin(np.pi * t / t[-1]) ** 2
    return bp(r.standard_normal(n), 4500, 11000, 2) * e * vel * 0.45


def rim(vel=0.6):
    n = ns(0.08)
    t = np.arange(n) / SR
    y = (np.sin(TAU * 1700 * t) * 0.6 + np.sin(TAU * 820 * t) * 0.4) * np.exp(-t / 0.012)
    return y * vel * 0.6


# ---------------------------------------------------------------- tonal voices
def bass_note(midi, dur, vel=0.9):
    """round sub + saturation so the bass still reads on a phone speaker (harmonics at 100-400 Hz)"""
    f = I.m2f(midi)
    n = ns(dur + 0.03)
    t = np.arange(n) / SR
    y = np.sin(TAU * f * t) + 0.25 * np.sin(TAU * 2 * f * t)
    e = np.minimum(1, t / 0.006) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.012)) * np.exp(-t / 1.6)
    y = np.tanh(2.2 * y * e) / np.tanh(2.2)
    return hp(lp(y, 900, 2), 38, 2) * vel * 0.5


def organ_stab(midis, vel=0.6, dur=0.16):
    n = ns(dur + 0.25)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for m in midis:
        f = I.m2f(m)
        for h, a in [(1, 1.0), (2, 0.55), (3, 0.28), (4, 0.18), (6, 0.08)]:
            y += a * np.sin(TAU * f * h * t + 0.3 * h)
    e = np.minimum(1, t / 0.003) * np.exp(-t / 0.09) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.03))
    return lp(y * e, 5000, 2) * vel * 2.6 / len(midis)


def pluck_note(midi, vel=0.6, seed=0):
    return I.pluck(I.m2f(midi), vel=vel, r=rng(seed), dur=0.6, bright=0.6) * 2.2


# ---------------------------------------------------------------- arrangement helpers
def buf(bars, tail=1.5):
    return np.zeros((2, ns(bars * BAR + tail)))


def drums(b, bars, kick_v=1.0, clap_v=0.8, hats_v=0.5, clap_from=0, rims=False, shakers=False, hats=True, seed=0):
    r = rng(seed)
    for bar in range(bars):
        ksteps = [0, 10] if bar % 4 != 3 else [0, 7, 10]
        for s in ksteps:
            place(b, kick(kick_v * (1.0 if s == 0 else 0.85)), t_of(bar, s))
        if bar >= clap_from and clap_v > 0:
            for s in (4, 12):
                place(b, pan(clap(clap_v, seed=bar * 16 + s), 0.0), t_of(bar, s))
        if hats:
            for s in range(16):
                v = [0.55, 0.22, 0.75, 0.25][s % 4] * hats_v * r.uniform(0.85, 1.1)
                op = s in (2, 10) and bar % 2 == 1
                place(b, pan(hat(v, open_=op, seed=bar * 16 + s), 0.25), t_of(bar, s))
        if shakers:
            for s in range(1, 16, 2):
                place(b, pan(shaker(0.6 * r.uniform(0.8, 1.1), seed=500 + bar * 16 + s), -0.3), t_of(bar, s))
        if rims:
            for s in (7, 13):
                place(b, pan(rim(0.7), -0.2), t_of(bar, s))


def bassline(b, bars, vel=0.9, pattern=((0, 3), (6, 2), (10, 3), (14, 1)), up_last=True):
    for bar in range(bars):
        root = PROG[bar % 4]["bass"]
        for k, (s, ln) in enumerate(pattern):
            m = root + (12 if (up_last and k == len(pattern) - 1) else 0)
            place(b, bass_note(m, ln * STEP * 0.92, vel), t_of(bar, s))


def stabs(b, bars, vel=0.55, steps=(2, 7, 11)):
    for bar in range(bars):
        ch = PROG[bar % 4]["stab"]
        for s in steps:
            place(b, pan(organ_stab(ch, vel), 0.1), t_of(bar, s))


def riff(b, bars, vel=0.55):
    motif = [(0, 65), (3, 68), (6, 72), (8, 70), (11, 68), (14, 65)]
    for bar in range(bars):
        shift = [0, -4, -7, -5][bar % 4] if bar % 2 else 0
        for i, (s, m) in enumerate(motif):
            place(b, pan(pluck_note(m + shift, vel, seed=bar * 10 + i), -0.25), t_of(bar, s))


def echo(x, time, fb=0.35, mix=0.35, n_rep=4, lp_f=3500):
    y = x.copy()
    d = ns(time)
    tap = x.copy()
    for k in range(1, n_rep + 1):
        tap = lp(np.roll(tap, d, axis=-1), lp_f, 1) * fb
        tap[:, :d] = 0
        y += mix * tap * (1 if k % 2 else 0.8)
    return y


def room(x, rt=0.9, amt=0.12, seed=7):
    return x + amt * convolve_st(x.mean(0), make_ir(rt, seed, hf=1.6))


def finish(x, bars, target=-16.0):
    x = x[:, : ns(bars * BAR)] if bars else x
    x = x - x.mean(axis=1, keepdims=True)
    g = dbg(target - integrated(x))
    x = x * g
    pk = np.max(np.abs(x))
    if pk > dbg(-1.5):
        x = np.tanh(x / dbg(-1.5)) * dbg(-1.5)
    return x


# ---------------------------------------------------------------- sections
def sec_hook():
    bars = 4
    b = buf(bars)
    drums(b, bars, kick_v=0.9, clap_v=0.7, hats_v=0.45, seed=1)
    bassline(b, bars, 0.85)
    stabs(b, bars, 0.5)
    b = lp(b, 1100, 2) * 1.4  # muffled, like a car going past with the windows up
    return finish(room(b, 0.6, 0.08), bars)


def sec_snatch():
    bars = 8
    b = buf(bars)
    drums(b, bars, kick_v=1.0, clap_v=0.85, hats_v=0.6, rims=True, seed=2)
    bassline(b, bars, 0.95)
    stabs(b, bars, 0.6)
    for bar in (4, 6):  # extra push in the second half
        place(b, pan(organ_stab(PROG[bar % 4]["stab"], 0.5), -0.1), t_of(bar, 14))
    return finish(room(b, 0.8, 0.1), bars)


def sec_journey():
    bars = 8
    b = buf(bars)
    drums(b, bars, kick_v=0.85, clap_v=0.7, hats_v=0.0, hats=False, rims=True, shakers=True, clap_from=4, seed=3)
    bassline(b, bars, 0.85, pattern=((0, 2), (3, 1), (6, 2), (10, 2), (13, 1)), up_last=False)
    r = buf(bars)
    riff(r, bars, 0.6)
    b += echo(r, BEAT * 0.75, fb=0.4, mix=0.45)
    return finish(room(b, 1.1, 0.12), bars)


def sec_sofa():
    bars = 8
    b = buf(bars)
    drums(b, bars, kick_v=0.6, clap_v=0.0, hats_v=0.35, seed=4)
    for bar in range(bars):
        place(b, pan(rim(0.45), -0.2), t_of(bar, 12))
        ch = PROG[bar % 4]["stab"]
        place(b, I.pad([I.m2f(m + 12) for m in ch[:4]], BAR * 0.98, vel=1.1, r=rng(40 + bar), att=0.25, rel=0.6, warm=1600), t_of(bar, 0))
    bassline(b, bars, 0.7, pattern=((0, 6), (10, 4)), up_last=False)
    b = lp(b, 3800, 1)
    return finish(room(b, 1.4, 0.16), bars)


def sting_tapestop():
    one = sec_sofa()[:, : ns(BAR * 1.0)]
    n = one.shape[1]
    # playback speed falls from 1 to 0 over the bar: read position = integral of speed
    speed = np.cos(np.linspace(0, np.pi / 2, n)) ** 1.5
    pos = np.cumsum(speed)
    pos = pos[pos < n - 1]
    y = np.stack([np.interp(pos, np.arange(n), one[c]) for c in range(2)])
    y *= np.linspace(1, 0.6, y.shape[1])[None, :]
    y = lp(y, 3000, 1)
    return finish(y, 0, -18.0)


def sting_biscuit():
    dur = 4.5
    n = ns(dur)
    t = np.arange(n) / SR
    drone = I.pad([I.m2f(29), I.m2f(41), I.m2f(48)], dur - 0.8, vel=0.8, r=rng(9), att=1.2, rel=0.8, warm=500)[:, :n]
    sub = np.sin(TAU * I.m2f(29) * t) * np.minimum(1, t / 1.5) * np.exp(-np.maximum(t - 3.2, 0) / 0.5) * 0.5
    low = np.zeros(n)
    k = ns(0.9)  # a single dark low "piano" note on the second word
    note = I.pluck(I.m2f(36), vel=0.9, r=rng(11), dur=3.0, bright=0.2)
    low[k: k + len(note)] += note[: n - k]
    y = drone + pan(sub + 0.8 * low, 0.0)
    return finish(room(y, 2.2, 0.25, seed=12), 0, -18.0)


def sting_jess():
    dur = 2.4
    n = ns(dur)
    hit_t = 1.2
    cym = I.cymbal(0.9, rng(13), dur=hit_t)
    rev = cym[::-1] * np.linspace(0, 1, len(cym)) ** 2
    y = np.zeros((2, n))
    place(y, pan(rev, 0.0), 0.0, 0.9)
    place(y, pan(kick(1.0), 0.0), hit_t, 1.2)
    place(y, pan(I.cymbal(0.7, rng(14), dur=1.2), 0.0), hit_t, 0.5)
    place(y, pan(bass_note(29, 0.9, 1.0), 0.0), hit_t)
    return finish(room(y, 1.8, 0.3, seed=15), 0, -16.0)


def main():
    os.makedirs(OUT, exist_ok=True)
    parts = {
        "A_hook": sec_hook(),
        "B_snatch": sec_snatch(),
        "C_journey": sec_journey(),
        "D_sofa": sec_sofa(),
        "sting_tapestop": sting_tapestop(),
        "sting_biscuit": sting_biscuit(),
        "sting_jess": sting_jess(),
    }
    for k, x in parts.items():
        write_wav(os.path.join(OUT, f"{k}.wav"), x, bits=24)
        print(f"{k:16s} {x.shape[1] / SR:6.2f} s  {integrated(x):6.1f} LUFS")
    # preview: the whole score in story order, beds at -16 LUFS (in the real mix they sit 15-18 dB under the voice)
    order = ["A_hook", "B_snatch", "C_journey", "D_sofa", "sting_tapestop", "sting_biscuit", "sting_jess"]
    total = sum(parts[k].shape[1] for k in order)
    pv = np.zeros((2, total))
    i = 0
    for k in order:
        x = parts[k]
        pv[:, i: i + x.shape[1]] += x
        i += x.shape[1]
    write_wav(os.path.join(OUT, "music_preview.wav"), pv, bits=24)
    print(f"preview {total / SR:.1f} s")


if __name__ == "__main__":
    main()
