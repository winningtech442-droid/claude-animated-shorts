# Sound effects for "Cheers, Biscuit" Part 2: same rules and generators as Part 1 (sfx_phoneverse.py), plus the new
# sounds this episode needs (counter ticks, trackpad clicks, the crack, the error buzz, the screenshot shutter, the dives).
# Placed on the voice timeline (out/timeline.json + out/words.json), mixed with the voice and the ducked music into
# out/final_mix.wav.
#
# Level rules (effects never get in the way of the voices): events are set relative to the voice ("big" -8 dB,
# "normal" -12 dB, "subtle" -17 dB), ambience beds sit 22 dB under it, and the whole stem drops 4 dB while anyone talks.
#   python sfx_part2.py        (after make_audio.py)
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "templates", "audio"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "phoneverse-found-text", "audio"))
from dsp import (SR, TAU, ns, tt, rng, dbg, lp, hp, bp, pan, st, place, fades, make_ir, convolve_st,  # noqa: E402
                 integrated, momentary, momentary_max, modal, read_wav, write_wav, phase)
import sfx_gen as G  # noqa: E402
from sfx_phoneverse import whip, text_ping, sofa_creak, typing, screen_taps, low_boom, room_tone  # noqa: E402

OUT = os.path.join(HERE, "out")
LEVEL = {"big": -8.0, "normal": -12.0, "subtle": -17.0}
BED_DB = -22.0
DUCK_DB = -4.0


# ================================================================ new generators (mono)
def heartbeat(r, beats=2, gap=0.78):
    """lub-dub thuds under the penny-drop line"""
    y = np.zeros(ns(beats * gap + 0.4))
    for b in range(beats):
        for dt, a in ((0.0, 1.0), (0.17, 0.7)):
            t = tt(0.25)
            th = np.sin(phase(52 * (1 + 0.6 * np.exp(-t / 0.012)))) * np.exp(-t / 0.06) * a
            G._place_mono(y, th, b * gap + dt)
    return fades(lp(y, 220, 2), 0.001, 0.08)


def trackpad_click(r, a=1.0):
    """a laptop trackpad click: tight plastic tick + a tiny low thock"""
    t = tt(0.06)
    y = bp(r.standard_normal(len(t)), 2200, 7500, 2) * np.exp(-t / 0.0025)
    y += modal(0.06, [(r.uniform(1900, 2300), 0.4, 0.01)], r) + np.sin(TAU * 180 * t) * np.exp(-t / 0.008) * 0.5
    return fades(y * a, 0.0003, 0.01)


def counter_tick(r, heavy=False):
    """the CLICKS TO ERASE counter changing: a mechanical flip-digit clack with a low knock (heavier at 1)"""
    d = 0.35
    t = tt(d)
    clack = bp(r.standard_normal(len(t)), 900, 5200, 2) * np.exp(-t / 0.006)
    knock = np.sin(phase((95 if heavy else 140) * (1 + 0.5 * np.exp(-t / 0.01)))) * np.exp(-t / (0.09 if heavy else 0.05))
    ring = modal(d, [(620, 0.25, 0.08), (1480, 0.12, 0.04)], r)
    return fades(clack * 0.8 + knock * (1.4 if heavy else 0.9) + ring * 0.5, 0.0005, 0.05)


def pop(r):
    """the counter appearing: a short upward blip"""
    t = tt(0.12)
    return fades(np.sin(phase(380 + 900 * (t / 0.12) ** 0.6)) * np.exp(-t / 0.05) * 0.8, 0.002, 0.03)


def glitch(r, dur=0.35):
    """data glitch as the camera bursts out of a screen: gated digital noise + stepped tones"""
    n = ns(dur)
    y = np.zeros(n)
    tm = 0.0
    while tm < dur - 0.02:
        k = ns(r.uniform(0.012, 0.04))
        i = ns(tm)
        seg = (np.sign(np.sin(TAU * r.uniform(300, 2400) * tt(k / SR))) * 0.5 if r.random() < 0.5
               else bp(r.standard_normal(k), 1500, 9000, 1))
        y[i:i + k] += seg[: n - i] * r.uniform(0.3, 1.0)
        tm += k / SR + r.uniform(0.0, 0.02)
    return fades(y * np.linspace(1, 0.4, n), 0.002, 0.04)


def screen_crack(r):
    """the counter freezing and cracking: a sharp glassy snap + splinters"""
    d = 0.7
    t = tt(d)
    snap = hp(r.standard_normal(len(t)), 2500) * np.exp(-t / 0.004) * 1.4
    glass = modal(d, [(r.uniform(2800, 3200), 0.5, 0.09), (r.uniform(4300, 4900), 0.35, 0.06),
                      (r.uniform(6100, 6900), 0.25, 0.04)], r)
    spl = np.zeros(len(t))
    for _ in range(9):
        i = ns(r.uniform(0.01, 0.18))
        k = ns(0.01)
        spl[i:i + k] += hp(r.standard_normal(k), 3000) * np.exp(-np.arange(k) / SR / 0.002) * r.uniform(0.2, 0.6)
    return fades(snap + glass * 0.6 + spl, 0.0003, 0.1)


def error_buzz(r):
    """'Incorrect password': two short low buzzes (generic, no brand sound) + the field shaking"""
    y = np.zeros(ns(0.5))
    for tm in (0.0, 0.16):
        t = tt(0.12)
        b = np.sign(np.sin(TAU * 150 * t)) * 0.4 + np.sin(TAU * 300 * t) * 0.3
        G._place_mono(y, lp(b, 1800, 2) * fades(np.ones(len(t)), 0.004, 0.02), tm)
    return y


def shutter(r):
    """screenshot: a soft two-part camera shutter"""
    y = np.zeros(ns(0.25))
    for tm, f, a in ((0.0, 2600, 1.0), (0.07, 1900, 0.8)):
        k = ns(0.05)
        c = bp(r.standard_normal(k), 1200, 6000, 2) * np.exp(-tt(0.05) / 0.006) * a
        c += modal(0.05, [(f, 0.3 * a, 0.012)], r)
        G._place_mono(y, c, tm)
    return y


def riser(dur, r):
    """the tension drone under the last click: low pulsing tone + filtered noise, both rising"""
    n = ns(dur)
    t = np.arange(n) / SR
    k = t / dur
    f = 55 * (1 + 0.5 * k)
    tone = (np.sin(phase(f)) + 0.4 * np.sin(phase(2.01 * f))) * (0.6 + 0.4 * np.sin(TAU * (2 + 6 * k) * t))
    air = bp(r.standard_normal(n), 400, 3000, 1)
    air = lp(air * (k ** 2), 600 + 5000 * k[-1], 1)
    return fades((tone * 0.6 + air * 0.5) * (0.25 + 0.75 * k ** 1.5), 0.2, 0.02)


def whoomp(r):
    """the other devices vanishing off her list: a soft downward suck"""
    return G.whoosh(0.45, r, 0.12, 900, 200, 0.9, 0.2, 0.05)


# ================================================================ cue list
def build_cues(tl, words):
    S = {r["id"]: r["start"] for r in tl}
    E = {r["id"]: r["end"] for r in tl}

    def word(lid, w, nth=0):
        hits = [x["start"] for x in words if x["line"] == lid and w.lower() in x["word"].lower()]
        if len(hits) <= nth:
            raise KeyError((lid, w, nth))
        return hits[nth]

    r = rng(2027)
    C = []

    def ev(t, name, fn, lvl="normal", p=0.0, room=None):
        C.append(dict(t=t, name=name, x=fn(), lvl=lvl, p=p, room=room, bed=False))

    def bed(t0, t1, name, fn, extra=0.0, room=None):
        C.append(dict(t=t0, name=name, x=fn(t1 - t0), lvl="bed", extra=extra, p=0.0, room=room, bed=True))

    T_END = E["L27"] + 1.6
    DEN1 = (E["L07"] + 0.6, S["L10"] - 0.4)          # the camera is in the den (after dive 1, until the dive back)
    DEN2 = (E["L19"] + 0.4, S["L24"] - 0.1)          # dive 2 ... the race ... kicked out
    # ---- beds
    bed(0.0, T_END, "flat room tone", lambda d: room_tone(d, r, False), extra=-4)
    bed(DEN1[0], DEN1[1], "warehouse room tone + laptop hum (den 1)", lambda d: room_tone(d, r, True), extra=-2)
    bed(DEN2[0], DEN2[1], "warehouse room tone + laptop hum (den 2 + race)", lambda d: room_tone(d, r, True), extra=-3)
    # ---- beat 1: cold open
    ev(S["L01"] + 0.15, "sofa creak (Jess shrinking back, hands up)", lambda: sofa_creak(r), "subtle", p=0.3)
    # ---- beat 2: the penny drops
    ev(S["L04"] + 0.05, "heartbeat thuds (the penny drops)", lambda: heartbeat(r, 3), "subtle")
    ev(S["L05"] - 0.1, "sofa creak (Jess bounces up, outraged)", lambda: sofa_creak(r), "subtle", p=0.3)
    ev(S["L06"] + 0.1, "she stands up fast (whoosh)", lambda: whip(r, 0.45, bright=False), "subtle")
    # ---- beat 3: dive 1 into the phone, out of his laptop
    ev(E["L07"] + 0.02, "dive 1: big whoosh into the screen", lambda: whip(r, 1.2), "normal")
    ev(E["L07"] + 0.35, "dive 1: map zoom swish (London -> Heathrow)", lambda: whip(r, 0.55), "subtle")
    ev(S["L08"] - 0.45, "dive 1: data glitch, out of his laptop", lambda: glitch(r), "subtle", room="warehouse")
    # ---- beat 4: the den
    ev(S["L08"] - 0.12, "trackpad click: Find Devices (no code)", lambda: trackpad_click(r), "normal", room="warehouse")
    ev(E["L08"] + 0.1, "counter appears (pop)", lambda: pop(r), "subtle")
    ev(E["L08"] + 0.16, "counter shows 3 (tick)", lambda: counter_tick(r), "subtle")
    ev(word("L09", "parts") + 0.25, "trackpad click: Erase This Device", lambda: trackpad_click(r), "normal", room="warehouse")
    ev(word("L09", "parts") + 0.32, "counter 3 -> 2 (tick)", lambda: counter_tick(r), "normal")
    # ---- beat 5: dive back
    ev(E["L09"] + 0.22, "dive back: whoosh through the map pin", lambda: whip(r, 0.7, bright=False), "normal")
    # ---- beat 6: panic
    ev(S["L11"] + 0.1, "Jess flapping (swish)", lambda: whip(r, 0.3, bright=False), "subtle", p=0.35)
    ev(S["L11"] + 0.85, "Jess flapping (swish)", lambda: whip(r, 0.3, bright=False), "subtle", p=0.35)
    ev(S["L12"] + 0.1, "her thumbs on the screen", lambda: screen_taps(E["L14"] - S["L12"] - 0.2, r, 6.0), "subtle", p=-0.1)
    ev(S["L13"] - 0.12, "Jess grabs her own phone (swish)", lambda: whip(r, 0.25), "subtle", p=0.4)
    # ---- beat 7: the fix
    ev(S["L16"] + 0.05, "typing the new long password", lambda: screen_taps(E["L16"] - S["L16"], r, 11.0), "subtle", p=-0.1)
    ev(word("L17", "gone") - 0.28, "tap: Remove Other Devices", lambda: pop(r), "subtle")
    ev(word("L17", "gone") - 0.2, "the other devices vanish (whoomp)", lambda: whoomp(r), "subtle")
    # ---- beat 8: dive 2
    ev(E["L19"] + 0.02, "dive 2: faster whoosh", lambda: whip(r, 0.8), "normal")
    ev(S["L20"] - 0.3, "dive 2: data glitch", lambda: glitch(r, 0.25), "subtle", room="warehouse")
    # ---- beat 9: the last click
    ev(word("L20", "sure", 1) - 0.05, "trackpad click: 'Are you sure?' -> yes", lambda: trackpad_click(r), "normal",
       room="warehouse")
    ev(word("L20", "sure", 1) + 0.03, "counter 2 -> 1 (heavy tick)", lambda: counter_tick(r, heavy=True), "normal")
    ev(word("L20", "last") - 0.1, "cursor glides to the red Erase button", lambda: whip(r, 0.35, bright=False), "subtle")
    T_PRESS = E["L22"] + 0.2
    ev(E["L20"] - 0.2, "tension riser under the race", lambda: riser(T_PRESS - E["L20"] + 0.2, r), "normal")
    # ---- beat 10: the race (cross-cuts speed up)
    for k, tm in enumerate((S["L21"] + 0.1, S["L21"] + 0.75, S["L21"] + 1.3, S["L21"] + 1.7, E["L21"] + 0.25, S["L22"] + 0.45)):
        ev(tm, "race cross-cut swish", lambda: whip(r, 0.18), "subtle", p=0.25 * (-1) ** k)
    ev(T_PRESS, "her thumb: Sign Out Of All Browsers", lambda: pop(r), "normal")
    ev(T_PRESS + 0.04, "his click: Erase (a frame too late)", lambda: trackpad_click(r, 1.2), "normal", room="warehouse")
    # ---- beat 11: kicked out
    T_KICK = T_PRESS + 0.15
    ev(T_KICK, "counter freezes on 1 and cracks", lambda: screen_crack(r), "big")
    ev(T_KICK, "low hit under the crack", lambda: low_boom(r), "normal")
    ev(E["L23"] + 0.1, "he types the old password", lambda: typing(0.75, r, 11.0), "subtle", room="warehouse")
    ev(E["L23"] + 0.95, "Incorrect password (error buzz + shake)", lambda: error_buzz(r), "normal", room="warehouse")
    # ---- beat 12: the sting
    ev(S["L25"] - 0.5, "his text lands on her phone (ping + buzz)", lambda: text_ping(r), "normal", p=0.1)
    ev(word("L26", "screenshot") + 0.35, "screenshot shutter", lambda: shutter(r), "normal")
    # ---- beat 13: the payoff, the slow turn (silence otherwise)
    ev(E["L27"] + 0.25, "slow head turn: a long sofa creak", lambda: G.creak(0.9, r, 70, 95), "subtle", p=-0.1)
    return C


# ================================================================ render + mix (same as Part 1)
def main():
    tl = json.load(open(os.path.join(OUT, "timeline.json")))
    words = json.load(open(os.path.join(OUT, "words.json")))
    voice, _ = read_wav(os.path.join(OUT, "voice_track.wav"))
    music, _ = read_wav(os.path.join(OUT, "music_ducked.wav"))
    voice, music = st(voice), st(music)
    N = voice.shape[1]
    v_ref = integrated(voice)
    rooms = {"warehouse": make_ir(1.7, 32, hf=1.3)}
    sfx = np.zeros((2, N))
    log = []
    for c in build_cues(tl, words):
        x = c["x"]
        x = pan(x, c["p"]) if x.ndim == 1 else x
        if c["room"]:
            x = x + 0.35 * convolve_st(np.pad(x, ((0, 0), (0, ns(1.2)))).mean(0), rooms[c["room"]])[:, : x.shape[1]]
        if c["bed"]:
            g = v_ref + BED_DB + c.get("extra", 0.0) - integrated(x)
        else:
            g = v_ref + LEVEL[c["lvl"]] - momentary_max(np.pad(x, ((0, 0), (0, ns(0.5)))))
        place(sfx, x * dbg(g), c["t"])
        log.append((round(c["t"], 2), c["name"], c["lvl"]))
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
