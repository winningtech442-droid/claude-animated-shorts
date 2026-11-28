# Sound effects for "Cheers, Biscuit" Part 3, "Free Upgrade": same rules and generators as Parts 1-2, plus the sounds
# this episode needs (keypad blips for the code digits, the call ending, the signal bars draining, the counter
# crumbling into NO SERVICE, the earpiece dive, a bike bell, pigeons, an original ringtone, his SIM dying).
# Placed on the voice timeline (out/timeline.json + out/words.json), mixed with the voice and the ducked music into
# out/final_mix.wav.
#
# Level rules (your Part 2 note: effects never louder than the voices): events are set relative to the voice
# ("big" -13 dB, "normal" -17 dB, "subtle" -22 dB), ambience beds sit 27 dB under it, and the whole stem drops 4 dB
# while anyone talks.
#   python sfx_part3.py        (after make_audio.py)
import json
import os
import sys

import numpy as np
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "templates", "audio"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "phoneverse-found-text", "audio"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "phoneverse-cheers-biscuit-part2", "audio"))
from dsp import (SR, TAU, ns, tt, rng, dbg, lp, hp, bp, pan, st, place, fades, make_ir, convolve_st,  # noqa: E402
                 integrated, momentary, momentary_max, modal, read_wav, write_wav, phase)
import sfx_gen as G  # noqa: E402
from sfx_phoneverse import (whip, text_ping, low_boom, room_tone, street_bed, ebike, bus_pass, rustle,  # noqa: E402
                            setup_chime, screen_taps)
from sfx_part2 import heartbeat, trackpad_click, counter_tick, pop, whoomp  # noqa: E402

OUT = os.path.join(HERE, "out")
LEVEL = {"big": -13.0, "normal": -17.0, "subtle": -22.0}
BED_DB = -27.0
DUCK_DB = -4.0


# ================================================================ new generators (mono)
DIGIT_F = {"4": 1209.0, "8": 1336.0, "2": 1477.0, "9": 1336.0, "1": 1209.0, "3": 1477.0}


def keypad_blip(r, digit):
    """a code digit popping into its box: a short soft keypad pip (pitch per digit, generic, no brand sound)"""
    t = tt(0.09)
    f = DIGIT_F.get(digit, 1300.0)
    y = (np.sin(TAU * f * t) + 0.35 * np.sin(TAU * 0.5 * f * t)) * np.exp(-t / 0.03)
    return fades(y * 0.8, 0.002, 0.02)


def call_end(r):
    """the call ends: two falling beeps"""
    y = np.zeros(ns(0.32))
    for tm, f in ((0.0, 620.0), (0.14, 470.0)):
        t = tt(0.1)
        G._place_mono(y, np.sin(TAU * f * t) * fades(np.ones(len(t)), 0.004, 0.02) * 0.6, tm)
    return y


def bars_drain(r):
    """her signal bars dropping one by one: four falling blips, each quieter"""
    y = np.zeros(ns(0.7))
    for k, f in enumerate((1180.0, 990.0, 820.0, 660.0)):
        t = tt(0.07)
        G._place_mono(y, np.sin(TAU * f * t) * np.exp(-t / 0.03) * (0.7 - 0.12 * k), 0.13 * k)
    return fades(y, 0.002, 0.04)


def bars_return(r):
    """the bars coming back: three rising blips"""
    y = np.zeros(ns(0.5))
    for k, f in enumerate((660.0, 880.0, 1175.0)):
        t = tt(0.07)
        G._place_mono(y, np.sin(TAU * f * t) * np.exp(-t / 0.03) * (0.45 + 0.1 * k), 0.11 * k)
    return fades(y, 0.002, 0.04)


def crumble(r):
    """the six red code boxes breaking apart into NO SERVICE: a scatter of small clacks over a low thud"""
    d = 0.7
    y = np.zeros(ns(d))
    t = tt(0.25)
    G._place_mono(y, np.sin(phase(90 * (1 + 0.6 * np.exp(-t / 0.015)))) * np.exp(-t / 0.08) * 1.0, 0.0)
    for _ in range(14):
        k = ns(0.03)
        c = bp(r.standard_normal(k), 1200, 7000, 2) * np.exp(-np.arange(k) / SR / 0.004) * r.uniform(0.2, 0.7)
        G._place_mono(y, c, r.uniform(0.0, 0.45) ** 1.3)
    return fades(y, 0.0005, 0.12)


def dead_line(dur, r):
    """a dead line: a soft, steady low tone with faint static (no service)"""
    n = ns(dur)
    t = np.arange(n) / SR
    tone = np.sin(TAU * 400 * t) * 0.35
    hiss = bp(r.standard_normal(n), 800, 3000, 1) * 0.06
    return fades(lp(tone + hiss, 2500, 1), 0.05, 0.25)


def line_static(dur, r):
    """the inside of a phone line: gated, band-limited static and data burble (the earpiece dive)"""
    n = ns(dur)
    y = bp(r.standard_normal(n), 400, 3400, 2) * 0.35
    gate = np.repeat(r.uniform(0.2, 1.0, n // ns(0.03) + 1), ns(0.03))[:n]
    burble = np.sign(np.sin(TAU * r.uniform(700, 1400) * np.arange(n) / SR)) * 0.08
    return fades((y + burble) * lp(gate, 40, 1), 0.08, 0.15)


def bike_bell(r):
    """a bicycle bell: two quick dings"""
    y = np.zeros(ns(0.8))
    for tm in (0.0, 0.16):
        G._place_mono(y, modal(0.6, [(3150, 0.6, 0.35), (4890, 0.35, 0.2), (7300, 0.15, 0.08)], r), tm)
    return fades(y, 0.0005, 0.1)


def pigeons(r, birds=4):
    """pigeons scattering off the pavement: wing-flap bursts (~11 per second per bird), stereo"""
    d = 1.4
    out = np.zeros((2, ns(d)))
    for b in range(birds):
        y = np.zeros(ns(d))
        t0 = r.uniform(0.0, 0.15)
        rate = r.uniform(9.5, 12.5)
        nflaps = int(r.uniform(8, 13))
        for k in range(nflaps):
            m = ns(0.05)
            flap = bp(r.standard_normal(m), 250, 2200, 2) * np.hanning(m) * (1.0 - k / (nflaps + 2))
            G._place_mono(y, flap, t0 + k / rate)
        place(out, pan(y, r.uniform(-0.8, 0.8)), 0.0)
    return out


def ringtone(r, dur=1.6):
    """an original ringtone: a little four-note marimba figure, repeated (not any phone maker's tune)"""
    y = np.zeros(ns(dur))
    notes = (1318.5, 987.8, 1318.5, 1661.2)
    tm = 0.0
    while tm < dur - 0.5:
        for k, f in enumerate(notes):
            t = tt(0.22)
            n_ = (np.sin(TAU * f * t) + 0.3 * np.sin(TAU * 4 * f * t) * np.exp(-t / 0.01)) * np.exp(-t / 0.07) * 0.5
            G._place_mono(y, n_, tm + 0.11 * k)
        tm += 0.7
    return fades(lp(y, 6000, 1), 0.002, 0.05)


def hangup(r):
    """a hang-up blip"""
    t = tt(0.08)
    return fades(np.sin(TAU * 520 * t) * np.exp(-t / 0.03) * 0.6, 0.002, 0.02)


def power_down(r):
    """his phone losing the SIM: a falling tone and a soft click"""
    d = 0.55
    t = tt(d)
    f = 620 * np.exp(-t / 0.18) + 70
    y = np.sin(phase(f)) * np.exp(-t / 0.25) * 0.5
    y[: ns(0.02)] += bp(r.standard_normal(ns(0.02)), 1500, 6000, 2) * 0.4
    return fades(y, 0.002, 0.08)


# ================================================================ cue list
def build_cues(tl, words):
    S = {r["id"]: r["start"] for r in tl}
    E = {r["id"]: r["end"] for r in tl}

    def word(lid, w, nth=0):
        hits = [x["start"] for x in words if x["line"] == lid and w.lower() in x["word"].lower()]
        if len(hits) <= nth:
            raise KeyError((lid, w, nth))
        return hits[nth]

    r = rng(2028)
    C = []

    def ev(t, name, fn, lvl="normal", p=0.0, room=None):
        C.append(dict(t=t, name=name, x=fn(), lvl=lvl, p=p, room=room, bed=False))

    def bed(t0, t1, name, fn, extra=0.0, room=None):
        C.append(dict(t=t0, name=name, x=fn(t1 - t0), lvl="bed", extra=extra, p=0.0, room=room, bed=True))

    T_END = E["L31"] + 0.7
    DIVE = E["L13"] + 0.05                    # the camera flies into Jess's earpiece (1.2 s)
    DEN1 = (DIVE + 0.9, S["L16"] - 0.5)       # the den, until the hard cut back to the street
    DEN2 = (S["L27"] - 0.6, E["L27"] + 0.25)  # his SIM dies (insert)
    # ---- beds: Oxford Street on Black Friday, cut out while we are in the den
    for a, b in ((0.0, DIVE + 0.5), (DEN1[1] - 0.1, DEN2[0] + 0.1), (DEN2[1] - 0.1, T_END)):
        bed(a, b, "Oxford Street: crowd, traffic", lambda d: street_bed(d, r), extra=-1)
    bed(DEN1[0], DEN1[1], "den: warehouse room tone + laptop hum", lambda d: room_tone(d, r, True), extra=-2)
    bed(DEN2[0], DEN2[1], "den insert: room tone", lambda d: room_tone(d, r, True), extra=-3)
    # ---- beat 1: cold open
    ev(max(0.0, S["L01"] - 0.3), "shopping bags swinging", lambda: rustle(0.9, r, 30.0, 0.8), "subtle", p=-0.2)
    ev(S["L03"] - 0.75, "cyclist whizzes past (bell + e-bike)", lambda: bike_bell(r), "subtle", p=0.5)
    ev(S["L03"] - 0.6, "cyclist whizzes past", lambda: ebike(1.3, r, pass_at=0.55, recede=True), "subtle", p=0.3)
    ev(S["L04"] - 0.2, "a bus goes by", lambda: bus_pass(2.6, r), "subtle")
    # ---- beat 2: the code
    ev(S["L05"] - 0.55, "the code text lands (buzz + ping)", lambda: text_ping(r), "normal", p=-0.1)
    ev(S["L05"] - 0.3, "counter appears: CODE READ OUT (pop)", lambda: pop(r), "subtle")
    for lid, w, d in (("L05", "four", "4"), ("L05", "eight", "8"), ("L08", "two", "2"), ("L11", "nine", "9"),
                      ("L17", "one", "1"), ("L17", "three", "3")):
        ev(word(lid, w) + 0.06, f"digit {d} pops into its box", lambda d=d: keypad_blip(r, d), "subtle")
    # ---- beat 3: the tell
    ev(S["L10"] - 0.08, "snap push-in on her ear", lambda: whip(r, 0.25), "subtle")
    # ---- beat 4: You clocks it
    ev(S["L12"] - 0.15, "You spins round", lambda: whip(r, 0.35, bright=False), "subtle", p=0.2)
    ev(S["L12"] + 0.1, "heartbeat thuds", lambda: heartbeat(r, 2), "subtle")
    # ---- beat 5: the earpiece dive and the den
    ev(DIVE, "dive: whoosh into her earpiece", lambda: whip(r, 1.2), "normal")
    ev(DIVE + 0.3, "dive: inside the phone line (static)", lambda: line_static(0.8, r), "subtle")
    ev(S["L14"] - 0.2, "MUTE button on his headset", lambda: trackpad_click(r, 0.8), "subtle", room="warehouse")
    ev(S["L15"] - 0.12, "unmute", lambda: trackpad_click(r, 0.8), "subtle", room="warehouse")
    # ---- beat 6: too late
    ev(S["L16"] - 0.08, "hard cut back to the street (swish)", lambda: whip(r, 0.2), "subtle")
    ev(S["L16"] + 0.1, "You lunges", lambda: whip(r, 0.3, bright=False), "subtle", p=0.3)
    ev(S["L17"] - 0.05, "Jess twirls away with her bags", lambda: rustle(0.7, r, 40.0, 0.9), "subtle", p=-0.3)
    ev(word("L17", "three") + 0.3, "all six boxes flash red", lambda: counter_tick(r, heavy=True), "normal")
    # ---- beat 7: No Service
    ev(E["L18"] + 0.1, "the call ends (two beeps)", lambda: call_end(r), "subtle")
    ev(E["L18"] + 0.45, "signal bars drain", lambda: bars_drain(r), "subtle")
    ev(E["L18"] + 0.95, "the boxes crumble into NO SERVICE", lambda: crumble(r), "normal")
    ev(E["L18"] + 1.0, "dead line", lambda: dead_line(max(0.5, S["L19"] - E["L18"] - 0.8), r), "subtle")
    # ---- beat 8: the reveal
    ev(E["L19"] + 0.08, "den insert: SIM activated (chime)", lambda: setup_chime(r), "subtle", room="warehouse")
    ev(word("L20", "number"), "low hit on 'number'", lambda: low_boom(r), "normal")
    ev(S["L22"] + 0.15, "pigeons scatter", lambda: pigeons(r), "normal")
    # ---- beat 9: the fix
    ev(S["L23"] + 0.3, "You hands over her phone", lambda: whip(r, 0.25, bright=False), "subtle", p=-0.2)
    ev(S["L24"] + 0.05, "taps on the network's website", lambda: screen_taps(E["L24"] - S["L24"], r, 6.0), "subtle")
    ev(S["L26"] + 0.25, "dialling the bank", lambda: screen_taps(0.8, r, 9.0), "subtle")
    ev(S["L27"] - 0.5, "den insert: his SIM dies (whoomp)", lambda: whoomp(r), "normal", room="warehouse")
    ev(S["L27"] - 0.45, "his phone powers down", lambda: power_down(r), "subtle", room="warehouse")
    # ---- beat 10: the payoff
    ev(E["L27"] + 0.25, "Jess's bars come back", lambda: bars_return(r), "subtle")
    ev(S["L28"] - 0.95, "her phone rings (original ringtone)", lambda: ringtone(r, 1.05), "normal", p=-0.1)
    ev(E["L29"] + 0.05, "she hangs up", lambda: hangup(r), "subtle")
    return C


def tp_limit(mix, ceiling_db=-1.5):
    """true-peak limiter: finds the 4x-oversampled peaks, holds the gain down 2 ms either side, releases over 60 ms"""
    from scipy.ndimage import maximum_filter1d
    up = resample_poly(mix, 4, 1, axis=1)
    pk = np.abs(up).max(0)
    pk = pk[: (len(pk) // 4) * 4].reshape(-1, 4).max(1)
    pk = np.pad(pk, (0, mix.shape[1] - len(pk)), mode="edge")
    need = maximum_filter1d(np.maximum(1.0, pk / dbg(ceiling_db)), size=2 * ns(0.002) + 1)
    g = np.ones_like(need)
    cur, rel = 1.0, 1.0 / ns(0.06)
    for i in range(len(need)):
        cur = max(cur, need[i]) if need[i] > cur else cur + (need[i] - cur) * rel
        g[i] = cur
    return mix / g[None, :]


# ================================================================ render + mix (same as Parts 1-2)
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
    mix = tp_limit(mix, -1.5)  # true peak stays under -1 dBTP after encoding
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
