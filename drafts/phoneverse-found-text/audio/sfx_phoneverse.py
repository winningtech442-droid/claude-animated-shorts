# Sound effects for the Phoneverse "Cheers, Biscuit" short, all synthesized here (numpy + scipy, the repo's DSP kit),
# placed on the voice timeline (out/timeline.json + out/words.json from make_audio.py), then mixed with the voice
# and the ducked music into out/final_mix.wav.
#
# Level rules (the brief: effects never get in the way of the voices):
#   - every event is set relative to the voice: "big" -8 dB, "normal" -12 dB, "subtle" -17 dB (max momentary loudness
#     of the event vs the voice stem's integrated loudness); ambience beds sit 22 dB under the voice (integrated)
#   - the whole effects stem drops another 4 dB while anyone is talking
#   - checked after rendering: effects vs voice loudness while talking, and Whisper on the final mix
#
# Run after make_audio.py:  python sfx_phoneverse.py
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "templates", "audio"))
from dsp import (SR, TAU, ns, tt, rng, dbg, lp, hp, bp, pan, st, place, fades, widen, make_ir, convolve_st,  # noqa: E402
                 integrated, momentary, momentary_max, colored, modal, read_wav, write_wav, phase)
import sfx_gen as G  # noqa: E402

OUT = os.path.join(HERE, "out")
LEVEL = {"big": -8.0, "normal": -12.0, "subtle": -17.0}
BED_DB = -22.0
DUCK_DB = -4.0


# ================================================================ generators (mono unless noted)
def pavement_step(r, a=1.0):
    d = 0.22
    t = tt(d)
    nz = r.standard_normal(len(t))
    heel = lp(nz, 260, 2) * np.exp(-t / 0.018) * 2.2 + np.sin(TAU * r.uniform(85, 110) * t) * np.exp(-t / 0.02) * 0.6
    grit = bp(nz, 1800, 6500, 1) * np.exp(-t / 0.012) * 0.35
    scrape = bp(r.standard_normal(len(t)), 900, 4000, 1) * np.clip(t / 0.03, 0, 1) * np.exp(-t / 0.05) * 0.15
    return fades((heel + grit + scrape) * a, 0.001, 0.03)


def body_thump(r):
    d = 0.35
    t = tt(d)
    thud = np.sin(phase(70 * (1 + 0.4 * np.exp(-t / 0.02)))) * np.exp(-t / 0.07)
    nz = lp(r.standard_normal(len(t)), 700, 2) * np.exp(-t / 0.03) * 0.8
    return fades(thud + nz, 0.001, 0.05)


def rustle(dur, r, density=40.0, bright=1.0):
    """nylon puffer / clothing: band noise + random crinkle bursts"""
    n = ns(dur)
    t = np.arange(n) / SR
    base = bp(r.standard_normal(n), 1200, 7000 * bright, 1) * 0.15
    cr = np.zeros(n)
    for tm in np.sort(r.uniform(0, dur, int(density * dur))):
        i = ns(tm)
        k = min(n - i, ns(0.03))
        cr[i:i + k] += r.standard_normal(k) * np.exp(-np.arange(k) / SR / 0.006) * r.uniform(0.3, 1.0)
    cr = bp(cr, 1500, 9000, 2)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.6
    return (base + cr) * env


def ebike(dur, r, f0=640, f1=980, pass_at=None, recede=False):
    """electric hub-motor whine + tyre hiss; optional Doppler drop at pass_at (s)"""
    n = ns(dur)
    t = np.arange(n) / SR
    f = f0 + (f1 - f0) * np.clip(t / dur, 0, 1)
    if pass_at is not None:
        f = f * np.where(t < pass_at, 1.06, 0.94)
        f = lp(f, 8, 1) if False else f
    ph = phase(f)
    whine = np.sin(ph) * 0.5 + np.sin(2 * ph) * 0.25 + np.sin(3 * ph + 1) * 0.1
    hiss = bp(r.standard_normal(n), 300, 2500, 1) * 0.5
    env = (t / dur) ** 1.6 if not recede else np.exp(-t / (dur * 0.35))
    return fades((whine * 0.6 + hiss) * env, 0.01, 0.08)


def brake_squeak(r):
    d = 0.22
    t = tt(d)
    f = 2350 + 250 * np.sin(TAU * 9 * t)
    return fades(np.sin(phase(f)) * np.exp(-t / 0.08) * 0.5, 0.005, 0.04)


def slap(r):
    d = 0.2
    t = tt(d)
    nz = r.standard_normal(len(t))
    return fades(bp(nz, 700, 4500, 2) * np.exp(-t / 0.008) + np.sin(TAU * 160 * t) * np.exp(-t / 0.025) * 0.4,
                 0.0005, 0.03)


def bus_pass(dur, r):
    """double-decker passing close: diesel harmonics with Doppler + road roar + air whoosh (stereo L -> R)"""
    n = ns(dur)
    t = np.arange(n) / SR
    mid = dur * 0.45
    f = np.where(t < mid, 44.0, 36.0) * (1 + 0.02 * np.sin(TAU * 7 * t))
    f = np.convolve(f, np.ones(ns(0.25)) / ns(0.25), mode="same")
    ph = phase(f)
    eng = sum(np.sin(k * ph + r.uniform(0, TAU)) / k ** 0.8 for k in range(1, 14))
    eng = lp(eng, 900, 2)
    roar = lp(colored(n, r, 1.0), 1400, 1) * 1.4
    env = np.exp(-((t - mid) / (dur * 0.22)) ** 2)
    air = G.whoosh(dur, r, mid, 200, 1800, 0.9, 0.35, 0.1)[:n] * 2.0
    y = (eng * 0.6 + roar) * env + air
    p = np.clip((t - mid) / (dur * 0.35), -1, 1) * 0.8
    L, R = y * np.cos((p + 1) * np.pi / 4), y * np.sin((p + 1) * np.pi / 4)
    return fades(np.stack([L, R]) * np.sqrt(2), 0.05, 0.2)


def breath(r, dur=0.45, inhale=True):
    t = tt(dur)
    e = np.sin(np.pi * t / dur) ** (1.5 if inhale else 0.8)
    return bp(r.standard_normal(len(t)), 500, 3200, 1) * e * 0.5


def door_slam(r):
    d = 0.8
    t = tt(d)
    thud = np.sin(phase(58 * (1 + 0.5 * np.exp(-t / 0.015)))) * np.exp(-t / 0.09)
    ring = modal(d, [(310, 0.5, 0.18), (835, 0.35, 0.09), (1440, 0.25, 0.05), (2210, 0.15, 0.03)], r)
    click = hp(r.standard_normal(len(t)), 2000) * np.exp(-t / 0.004) * 0.5
    return fades(thud + ring * 0.5 + click, 0.0005, 0.1)


def metal_clank(r):
    d = 0.9
    return fades(modal(d, [(r.uniform(400, 520), 0.6, 0.25), (r.uniform(1100, 1300), 0.4, 0.12),
                           (r.uniform(2300, 2700), 0.25, 0.06)], r) + hp(r.standard_normal(ns(d)), 1500) *
                 np.exp(-tt(d) / 0.003) * 0.4, 0.0005, 0.1)


def phones_clatter(r):
    y = np.zeros(ns(0.5))
    for k in range(7):
        tm = r.uniform(0, 0.25) if k else 0.0
        c = modal(0.08, [(r.uniform(1800, 3200), 1.0, 0.012), (r.uniform(4000, 6000), 0.5, 0.006)], r)
        c += bp(r.standard_normal(len(c)), 2000, 8000, 1) * np.exp(-tt(0.08) / 0.003) * 0.6
        i = ns(tm)
        y[i:i + len(c)] += c[: len(y) - i] * (1.0 if k == 0 else r.uniform(0.25, 0.6))
    return y


def cardboard(r, a=1.0):
    d = 0.3
    t = tt(d)
    nz = r.standard_normal(len(t))
    y = lp(nz, 1400, 2) * np.exp(-t / 0.035) + np.sin(TAU * r.uniform(120, 160) * t) * np.exp(-t / 0.04) * 0.6
    return fades(y * a, 0.0008, 0.05)


def stamp(r):
    d = 0.35
    t = tt(d)
    y = modal(d, [(210, 1.0, 0.05), (520, 0.4, 0.02)], r) + lp(r.standard_normal(len(t)), 2500) * np.exp(-t / 0.006)
    return fades(y, 0.0005, 0.05)


def padlock(r):
    y = np.zeros(ns(0.4))
    for tm, f, a in [(0.0, 3400, 1.0), (0.045, 2600, 0.8)]:
        c = hp(r.standard_normal(ns(0.03)), 1800) * np.exp(-tt(0.03) / 0.003) * a
        c += modal(0.03, [(f, 0.6 * a, 0.01)], r)
        i = ns(tm)
        y[i:i + len(c)] += c
    ring = modal(0.3, [(2480, 0.15, 0.12), (5200, 0.06, 0.05)], r)
    y[ns(0.05): ns(0.05) + len(ring)] += ring[: len(y) - ns(0.05)]
    return y


def text_ping(r):
    """generic two-note notification + a short vibration buzz (no brand sound)"""
    d = 0.9
    t = tt(d)
    y = np.zeros(len(t))
    for tm, f in [(0.0, 1318.5), (0.11, 1760.0)]:
        k = ns(tm)
        tk = t[: len(t) - k]
        y[k:] += (np.sin(TAU * f * tk) + 0.25 * np.sin(TAU * 2 * f * tk)) * np.exp(-tk / 0.18) * 0.5
    buzz = np.sin(TAU * 172 * t) * (np.sign(np.sin(TAU * 172 * t)) * 0.3 + 0.7)
    buzz = lp(buzz, 900, 2) * np.where(t < 0.32, 1.0, 0.0) * 0.35
    return fades(y + buzz, 0.002, 0.1)


def sofa_creak(r):
    return G.creak(0.3, r, r.uniform(90, 120), r.uniform(150, 190))


def typing(dur, r, rate=8.0):
    n = ns(dur)
    y = np.zeros(n)
    tm = 0.0
    while tm < dur - 0.05:
        k = ns(0.04)
        i = ns(tm)
        c = bp(r.standard_normal(k), 1500, 5500, 1) * np.exp(-tt(0.04) / 0.004) * r.uniform(0.5, 1.0)
        c += np.sin(TAU * r.uniform(280, 360) * tt(0.04)) * np.exp(-tt(0.04) / 0.008) * 0.3
        y[i:i + k] += c[: n - i]
        tm += r.exponential(1 / rate) + 0.03
    return y


def screen_taps(dur, r, rate=5.0):
    n = ns(dur)
    y = np.zeros(n)
    tm = 0.0
    while tm < dur - 0.05:
        k = ns(0.02)
        i = ns(tm)
        y[i:i + k] += bp(r.standard_normal(k), 2500, 7000, 1) * np.exp(-tt(0.02) / 0.002) * r.uniform(0.4, 1.0)
        tm += r.exponential(1 / rate) + 0.06
    return y


def low_boom(r):
    d = 1.2
    t = tt(d)
    return fades(np.sin(phase(48 * (1 + 0.3 * np.exp(-t / 0.05)))) * np.exp(-t / 0.35) +
                 lp(r.standard_normal(len(t)), 200) * np.exp(-t / 0.1) * 0.3, 0.002, 0.2)


def setup_chime(r):
    """a generic warm 3-note 'setup' chime, muffled (it is inside a box in the warehouse)"""
    d = 1.0
    t = tt(d)
    y = np.zeros(len(t))
    for k, (tm, f) in enumerate([(0.0, 523.3), (0.12, 659.3), (0.24, 784.0)]):
        i = ns(tm)
        tk = t[: len(t) - i]
        y[i:] += (np.sin(TAU * f * tk) + 0.3 * np.sin(TAU * 2 * f * tk)) * np.exp(-tk / 0.35) * 0.4
    return fades(lp(y, 2500, 2), 0.002, 0.15)


def whip(r, dur=0.4, bright=True):
    return G.whoosh(dur, r, dur * 0.3, 500 if bright else 250, 4500 if bright else 1600, 0.9, dur * 0.35,
                    0.35 if bright else 0.1)


# ---------------------------------------------------------------- beds (stereo)
def street_bed(dur, r):
    n = ns(dur)
    t = np.arange(n) / SR
    traffic = lp(colored(n, r, 1.0), 380, 2) * (1 + 0.35 * np.sin(TAU * 0.07 * t + 1.0))
    out = widen(traffic * 1.6, r, 13, 0.9)
    for v in range(9):  # far crowd chatter
        base, scale = (r.uniform(100, 140), 1.0) if v % 2 else (r.uniform(185, 235), 1.15)
        y = G.babble(dur, r, base, scale, r.uniform(3.6, 4.8), r.uniform(0.5, 0.8), fmax=3200)
        out += pan(lp(y, r.uniform(1800, 2800), 1) * r.uniform(0.15, 0.4), r.uniform(-0.9, 0.9))
    for k in range(int(dur / 3)):  # distant car passes
        tm = r.uniform(0, dur - 2.5)
        car = G.whoosh(2.4, r, 1.2, 120, 700, 0.8, 0.6, 0.0) * 0.6
        place(out, pan(car, r.uniform(-0.9, 0.9)), tm)
    return fades(out, 0.3, 1.2)


def room_tone(dur, r, warehouse=False):
    n = ns(dur)
    t = np.arange(n) / SR
    if warehouse:
        hum = (np.sin(TAU * 50 * t) * 0.5 + np.sin(TAU * 100 * t) * 0.3 + np.sin(TAU * 150 * t) * 0.1)
        air = bp(colored(n, r, 0.6), 150, 1500, 1) * 0.6
        return fades(widen(hum * 0.4 + air, r, 15, 0.8), 0.15, 0.4)
    air = lp(colored(n, r, 0.8), 1200, 1)
    return fades(widen(air, r, 11, 0.9), 0.3, 0.6)


# ================================================================ cue list
def build_cues(tl, words):
    S = {r["id"]: r["start"] for r in tl}
    E = {r["id"]: r["end"] for r in tl}

    def word(lid, w):
        for x in words:
            if x["line"] == lid and w.lower() in x["word"].lower():
                return x["start"]
        raise KeyError((lid, w))

    r = rng(2026)
    C = []  # (time, name, generator -> mono/stereo, level kind, pan, room)

    def ev(t, name, fn, lvl="normal", p=0.0, room=None):
        C.append(dict(t=t, name=name, x=fn(), lvl=lvl, p=p, room=room, bed=False))

    def bed(t0, t1, name, fn, extra=0.0, room=None):
        C.append(dict(t=t0, name=name, x=fn(t1 - t0), lvl="bed", extra=extra, p=0.0, room=room, bed=True))

    # ---- Scene 1-2: Oxford Street
    bed(0.0, E["L14"] + 0.8, "street ambience (traffic + far crowd + passing cars)", lambda d: street_bed(d, r))
    for k, tm in enumerate(np.arange(0.15, S["L04"] - 0.1, 0.52)):  # her footsteps while she walks
        ev(tm, "footstep (her)", lambda: pavement_step(r, 0.8 + 0.2 * (k % 2)), "subtle", p=0.05 * (-1) ** k)
    ev(S["L02"] + 0.75, "focus-pull swish (to the thieves)", lambda: whip(r, 0.5, bright=False), "subtle")
    ev(S["L04"] - 0.06, "bump: body thump", lambda: body_thump(r), "normal")
    ev(S["L04"] + 0.35, "bump: puffer jacket rustle", lambda: rustle(0.4, r, 40), "subtle", p=0.1)  # after "Ooh", not on it
    ev(S["L05"] + 0.05, "e-bike rolls in (motor whine)", lambda: ebike(S["L06"] - S["L05"] - 0.05, r), "normal", p=0.45)
    ev(S["L06"] - 0.1, "e-bike brake squeak", lambda: brake_squeak(r), "subtle", p=0.3)
    ev(S["L06"] + 0.05, "struggle: clothing / grip", lambda: rustle(E["L07"] - S["L06"], r, 70, 1.1), "normal")
    ev(S["L07"] + 0.1, "crowd gasp", lambda: _gasps(r), "subtle")
    ev(S["L08"] - 0.12, "phone ripped free (fast swish)", lambda: whip(r, 0.35), "normal")
    ev(S["L08"] + 0.25, "slow-motion spin (low whoosh)", lambda: whip(r, 0.7, bright=False), "subtle")
    ev(S["L08"] + 0.75, "catch (hand slap)", lambda: slap(r), "normal", p=-0.2)
    ev(E["L08"] - 1.0, "red bus passes in front of camera", lambda: bus_pass(2.4, r), "big")
    ev(S["L09"] + 0.2, "thief A bikes off right", lambda: ebike(2.6, r, 980, 760, recede=True), "subtle", p=0.8)
    for k in range(7):
        ev(S["L09"] + 0.25 + k * 0.3, "thief B running off left", lambda: pavement_step(r, 1.0 - 0.12 * k), "subtle",
           p=-0.75)
    ev(S["L12"] - 0.45, "her catching her breath", lambda: breath(r, 0.4, True), "subtle")
    ev(S["L14"] - 0.1, "camera whips away from her", lambda: whip(r, 0.45), "normal")
    # ---- Scene 3: the journey montage (one whoosh per stop)
    ev(S["L15"] - 0.15, "into the montage", lambda: whip(r, 0.6, bright=False), "subtle")
    ev(word("L16", "bike") - 0.05, "bike whooshes past", lambda: ebike(0.7, r, 900, 700, pass_at=0.35), "subtle", p=0.3)
    ev(word("L16", "van") + 0.25, "van door slams", lambda: door_slam(r), "normal", room="street")
    ev(word("L16", "warehouse") + 0.35, "warehouse: metal shelf clank", lambda: metal_clank(r), "subtle", room="warehouse")
    bed(word("L16", "warehouse"), S["L18"], "warehouse room tone", lambda d: room_tone(d, r, True), extra=-2, room=None)
    ev(word("L16", "box") + 0.15, "phone drops onto the other phones", lambda: phones_clatter(r), "normal", room="warehouse")
    ev(word("L16", "box") + 0.85, "box flaps close", lambda: cardboard(r), "subtle", room="warehouse")
    ev(word("L16", "box") + 1.05, "box flaps close", lambda: cardboard(r, 0.8), "subtle", room="warehouse")
    ev(word("L16", "Hong") + 0.05, "HONG KONG stamp", lambda: stamp(r), "normal", room="warehouse")
    ev(word("L17", "lock") + 0.15, "padlock clicks shut", lambda: padlock(r), "normal")
    # ---- Scene 4: the sofa
    ev(S["L19"] - 0.15, "whip out of the box into the flat", lambda: whip(r, 0.5), "normal")
    bed(S["L19"], S["L30"] - 0.3, "flat room tone", lambda d: room_tone(d, r, False), extra=-4)
    ev(E["L19"] + 0.03, "text ping + buzz", lambda: text_ping(r), "normal", p=0.1)
    for k, dt in enumerate([0.25, 0.85, 1.45, 2.1]):
        ev(S["L21"] + dt, "sofa creaks (Jess bouncing)", lambda: sofa_creak(r), "subtle", p=0.3)
    ev(S["L22"] + 0.1, "phone pulled away (swish)", lambda: whip(r, 0.3, bright=False), "subtle")
    bed(S["L23"], E["L23"], "warehouse room tone (cutaway)", lambda d: room_tone(d, r, True), extra=-2)
    ev(S["L23"] + 0.3, "hooded figure typing on a laptop", lambda: typing(E["L23"] - S["L23"] - 0.5, r), "subtle",
       room="warehouse")
    ev(S["L26"] + 0.3, "Jess quietly tapping in the background (rewatch detail)",
       lambda: screen_taps(E["L26"] - S["L26"] - 0.6, r), "subtle", p=0.35)
    ev(S["L28"] - 0.1, "low boom (slow turn)", lambda: low_boom(r), "normal")
    # ---- Cliffhanger: warehouse
    bed(S["L30"] - 0.4, E["L31"] + 1.5, "warehouse room tone (ending)", lambda d: room_tone(d, r, True), extra=-1)
    ev(S["L30"] - 0.32, "old phone's setup chime (unlocked)", lambda: setup_chime(r), "subtle", room="warehouse")
    return C


def _gasps(r):
    out = np.zeros((2, ns(0.8)))
    for v in range(7):
        w = G.whoa(r, dur=r.uniform(0.3, 0.45))
        place(out, pan(lp(w, 3000, 1) * r.uniform(0.4, 1.0), r.uniform(-0.85, 0.85)), r.uniform(0.0, 0.2))
    return out


# ================================================================ render + mix
def main():
    tl = json.load(open(os.path.join(OUT, "timeline.json")))
    words = json.load(open(os.path.join(OUT, "words.json")))
    voice, _ = read_wav(os.path.join(OUT, "voice_track.wav"))
    music, _ = read_wav(os.path.join(OUT, "music_ducked.wav"))
    voice, music = st(voice), st(music)
    N = voice.shape[1]
    v_ref = integrated(voice)
    rooms = {"street": make_ir(0.6, 31, hf=1.8), "warehouse": make_ir(1.7, 32, hf=1.3)}
    sfx = np.zeros((2, N))
    log = []
    for c in build_cues(tl, words):
        x = c["x"]
        x = pan(x, c["p"]) if x.ndim == 1 else x
        if c["room"]:
            x = x + 0.35 * convolve_st(np.pad(x, ((0, 0), (0, ns(1.2)))).mean(0), rooms[c["room"]])[:, : x.shape[1] + ns(1.2)][:, : x.shape[1]]
        if c["bed"]:
            g = v_ref + BED_DB + c.get("extra", 0.0) - integrated(x)
        else:
            m = momentary_max(np.pad(x, ((0, 0), (0, ns(0.5)))))
            g = v_ref + LEVEL[c["lvl"]] - m
        x = x * dbg(g)
        place(sfx, x, c["t"])
        log.append((round(c["t"], 2), c["name"], c["lvl"]))
    # duck the whole effects stem under speech
    env = np.abs(voice.mean(0))
    win = ns(0.05)
    env = np.convolve(env, np.ones(win) / win, mode="same")
    speech = (env > dbg(-45)).astype(float)
    a_, r_ = 1 / ns(0.05), 1 / ns(0.3)
    g = np.zeros(N)
    for i in range(1, N):
        g[i] = g[i - 1] + (speech[i] - g[i - 1]) * (a_ if speech[i] > g[i - 1] else r_)
    sfx *= dbg(DUCK_DB * g)[None, :]
    write_wav(os.path.join(OUT, "sfx_stem.wav"), sfx, bits=24)

    mix = voice + music[:, :N] + sfx
    mix *= dbg(-14.0 - integrated(mix))
    ceil = dbg(-2.5)
    mix = np.where(np.abs(mix) > ceil, np.sign(mix) * (ceil + (1 - ceil) * np.tanh((np.abs(mix) - ceil) / (1 - ceil))), mix)
    mix = np.clip(mix, -dbg(-1.8), dbg(-1.8))
    write_wav(os.path.join(OUT, "final_mix.wav"), mix, bits=24)

    # ---- checks: how far under the voice are the effects while someone is talking?
    mv, ms = momentary(voice), momentary(sfx)
    k = min(len(mv), len(ms))
    talking = mv[:k] > v_ref - 10
    diff = (mv[:k] - ms[:k])[talking]
    print(f"voice {v_ref:.1f} LUFS | effects stem {integrated(sfx):.1f} LUFS | music {integrated(music):.1f} LUFS | "
          f"final {integrated(mix):.1f} LUFS")
    print(f"while talking: effects are {np.median(diff):.1f} dB under the voice (median), "
          f"{np.percentile(diff, 5):.1f} dB at the closest 5% of moments")
    with open(os.path.join(OUT, "sfx_cues.txt"), "w") as f:
        for t, name, lvl in log:
            f.write(f"{t:7.2f}  {lvl:7s} {name}\n")
    print(f"{len(log)} cues -> out/sfx_cues.txt, out/sfx_stem.wav, out/final_mix.wav")


if __name__ == "__main__":
    main()
