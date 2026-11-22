#!/usr/bin/env python3
"""Synthesised sound for FIX #16 "Gold in your iPhone" (adapted from FIX #15; all original, no samples): a daytime recycling-yard bed (wind, distant birds),
workbench effects (clatter, shimmer, battery hiss/whoomph, fizz, sparkle, splashes, dust hush, torch roar, pour sizzle, bar clink, drawer slide), a bright pad with a soft pulse,
mixed with the directed voice. Reads ../phoneverse_3d_studio/data/beats_fix16.json + data/timings.json. Writes audio/mix_with_pad.wav and audio/mix_voice_fx.wav
(voice + bed + effects, no pad: for adding a TikTok sound by hand). Both are normalised to -14 LUFS, true peak -1.5 dB (two-pass loudnorm).
Music rules (rule book 5): music out under every REVEAL line, on re-hooks, half a beat before the turn; it hits back on the turn."""
import json, os, subprocess, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly
SR = 48000; rng = np.random.default_rng(12)
T = json.load(open("data/timings.json")); BS = json.load(open("../phoneverse_3d_studio/data/beats_fix16.json")); BEATS = BS["beats"]
END = T["summary"]["take_length_s"]; N = int((END + 0.4) * SR)
# voice presence (review: the narrator read too soft): gentle 3:1 compression + a small presence lift, before the mix
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "audio/voice_take.wav", "-af", "acompressor=threshold=-22dB:ratio=3:attack=4:release=90:makeup=2,equalizer=f=3200:t=q:w=1.2:g=2.5", "audio/voice_comp.wav"], check=True)
voice, vsr = sf.read("audio/voice_comp.wav"); os.remove("audio/voice_comp.wav"); voice = np.pad(voice.astype(np.float64), (0, max(0, N - len(voice))))[:N]
t = lambda d: np.arange(int(d * SR)) / SR
def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], "band", fs=SR, output="sos"), x)
def env(n, a=0.005, d=0.1):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na); e *= np.exp(-np.arange(n) / (SR * d)); return e
def noise(d): return rng.standard_normal(int(d * SR))
def put(buf, x, at, g=1.0):
    i = int(at * SR); j = min(len(buf), i + len(x))
    if i < len(buf) and j > i: buf[i:j] += x[: j - i] * g

def fx(name):
    if name == "buzz":
        d = 0.9; x = np.zeros(int(d * SR)); tt = t(d)
        gate = ((tt % 0.45) < 0.28).astype(float); x = np.sin(2 * np.pi * 160 * tt) * gate + 0.4 * np.sin(2 * np.pi * 320 * tt) * gate
        return lp(x, 900) * 0.8
    if name == "whoosh": d = 0.5; return bp(noise(d), 300, 5000) * np.sin(np.pi * t(d) / d) ** 2 * 0.7
    if name == "whoosh_soft": d = 0.7; return bp(noise(d), 200, 2500) * np.sin(np.pi * t(d) / d) ** 2 * 0.4
    if name == "rise": d = 1.2; return bp(noise(d), 400, 4000) * (t(d) / d) ** 2 * 0.3
    if name == "tick": d = 0.06; return np.sin(2 * np.pi * 1500 * t(d)) * env(int(d * SR), 0.001, 0.015) * 0.7
    if name == "alarm_tick": d = 0.08; return np.sin(2 * np.pi * 2100 * t(d)) * env(int(d * SR), 0.001, 0.02) * 0.8
    if name == "tick_rise":
        d = 1.5; x = np.zeros(int(d * SR))
        for k in range(14):
            put(x, fx("tick"), 0.08 + k * (d - 0.2) / 14 * (1 - 0.35 * k / 14), 0.4 + 0.04 * k)
        return x
    if name == "pop": d = 0.15; f = 900 - 500 * t(d) / d; return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(int(d * SR), 0.002, 0.04) * 0.8
    if name == "crack": d = 0.4; return (hp(noise(d), 800) * env(int(d * SR), 0.0005, 0.03) + np.sin(2 * np.pi * 70 * t(d)) * env(int(d * SR), 0.001, 0.12)) * 0.9
    if name == "tap": d = 0.1; return (np.sin(2 * np.pi * 220 * t(d)) * env(int(d * SR), 0.001, 0.025) + hp(noise(d), 2000) * env(int(d * SR), 0.0005, 0.01) * 0.3) * 0.9
    if name == "keys":
        x = np.zeros(int(0.7 * SR))
        for k in range(3): put(x, fx("tap"), 0.05 + k * 0.2, 0.7)
        return x
    if name == "confirm":
        d = 0.5; tt = t(d); return (np.sin(2 * np.pi * 880 * tt) * env(len(tt), 0.002, 0.12) + np.sin(2 * np.pi * 1320 * tt) * np.where(tt > 0.12, 1, 0) * env(len(tt), 0.002, 0.15)) * 0.5
    if name == "thud": d = 0.7; tt = t(d); return np.sin(2 * np.pi * (55 - 15 * tt / d) * tt) * env(len(tt), 0.002, 0.2) * 1.1
    if name == "pulse":
        d = 3.0; x = np.zeros(int(d * SR))
        for k in range(4): put(x, fx("thud"), k * 0.8, 0.45 + 0.1 * k)
        return x
    if name == "ringtone":
        d = 2.6; tt = t(d); gate = (((tt % 1.3) < 0.4) | (((tt % 1.3) > 0.5) & ((tt % 1.3) < 0.9))).astype(float)
        return (np.sin(2 * np.pi * 440 * tt) + np.sin(2 * np.pi * 480 * tt)) * 0.3 * gate * (np.sin(2 * np.pi * 20 * tt) > -0.2)
    if name == "stab": d = 0.45; tt = t(d); return (bp(noise(d), 500, 4000) * env(len(tt), 0.001, 0.08) + np.sin(2 * np.pi * (600 - 350 * tt / d) * tt) * env(len(tt), 0.001, 0.15)) * 0.9
    if name == "lock_click":
        x = np.zeros(int(0.8 * SR)); put(x, fx("tap"), 0.0, 1.0); put(x, fx("tick"), 0.12, 0.9)
        put(x, np.sin(2 * np.pi * 2400 * t(0.5)) * env(int(0.5 * SR), 0.001, 0.2) * 0.25, 0.14); return x
    if name == "music_hit":
        d = 1.4; tt = t(d); return (np.sin(2 * np.pi * (48 - 12 * tt / d) * tt) * env(len(tt), 0.002, 0.45) * 1.1 + bp(noise(d), 100, 3000) * env(len(tt), 0.001, 0.18) * 0.6) * 1.0
    if name == "toggle_click": d = 0.15; return (hp(noise(d), 1500) * env(int(d * SR), 0.0005, 0.02) + np.sin(2 * np.pi * 1100 * t(d)) * env(int(d * SR), 0.001, 0.03) * 0.6) * 0.8
    if name == "card_flip": d = 0.35; return bp(noise(d), 800, 7000) * np.sin(np.pi * t(d) / d) ** 3 * 0.6
    if name == "ding":                                   # packet arrival: soft two-note bell
        d = 0.45; tt = t(d); return (np.sin(2 * np.pi * 1568 * tt) * env(len(tt), 0.002, 0.12) + 0.5 * np.sin(2 * np.pi * 2093 * tt) * np.where(tt > 0.06, 1, 0) * env(len(tt), 0.002, 0.14)) * 0.35
    if name == "launch": d = 0.35; return bp(noise(d), 600, 6000) * (t(d) / d) ** 1.5 * np.exp(-((t(d) - d * 0.8) ** 2) / 0.004) * 0.6   # packet launch whoosh
    if name == "block": d = 0.3; tt = t(d); return (np.sin(2 * np.pi * 130 * tt) * env(len(tt), 0.001, 0.06) + lp(noise(d), 600) * env(len(tt), 0.001, 0.04)) * 0.8
    if name == "coin":                                   # pound coin landing: bright metallic ping
        d = 0.5; tt = t(d); f0 = rng.uniform(2500, 3300); return (np.sin(2 * np.pi * f0 * tt) + 0.6 * np.sin(2 * np.pi * f0 * 1.47 * tt) + 0.3 * np.sin(2 * np.pi * f0 * 2.09 * tt)) * env(len(tt), 0.0005, 0.09) * 0.32
    if name == "shutter":                                # camera shutter: two clicks + a short noise burst
        x = np.zeros(int(0.3 * SR)); put(x, hp(noise(0.03), 2000) * env(int(0.03 * SR), 0.0005, 0.008), 0.0, 0.9); put(x, hp(noise(0.05), 1500) * env(int(0.05 * SR), 0.0005, 0.015), 0.09, 0.8); return x
    if name == "slap":                                   # plaster slapped on
        d = 0.25; tt = t(d); return (lp(noise(d), 1800) * env(len(tt), 0.0008, 0.03) + np.sin(2 * np.pi * 180 * tt) * env(len(tt), 0.001, 0.05)) * 0.9
    if name == "impact":                                 # phone hits the desk: low thump + hard click
        d = 0.5; tt = t(d); return (np.sin(2 * np.pi * (90 - 40 * tt / d) * tt) * env(len(tt), 0.001, 0.09) + hp(noise(d), 2500) * env(len(tt), 0.0003, 0.01) * 0.8) * 1.0
    if name == "rewind":                                 # replay rewind: falling warble
        d = 0.6; tt = t(d); f = 1800 - 1400 * tt / d; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(2 * np.pi * 14 * tt) ** 2 * np.sin(np.pi * tt / d) * 0.35
    # ---- FIX #16 workbench sounds
    if name == "clatter":                                # the old phone skitters to rest: a few hard little clicks
        x = np.zeros(int(0.45 * SR))
        for k, g in enumerate((1.0, 0.6, 0.45, 0.3)): put(x, hp(noise(0.03), 1800) * env(int(0.03 * SR), 0.0003, 0.007), 0.05 * k + 0.02 * k * k, g)
        return x * 0.9
    if name == "shimmer":                                # gold glints: a rising cluster of soft bells
        d = 1.0; x = np.zeros(int(d * SR))
        for k, f0 in enumerate((1760, 2217, 2637, 3136, 3520)): put(x, np.sin(2 * np.pi * f0 * t(0.6)) * env(int(0.6 * SR), 0.002, 0.18), 0.09 * k, 0.22)
        return x
    if name == "sparkle":                                # flecks catching the light: scattered high pings
        d = 1.0; x = np.zeros(int(d * SR))
        for k in range(9): put(x, np.sin(2 * np.pi * rng.uniform(2800, 5200) * t(0.25)) * env(int(0.25 * SR), 0.001, 0.05), rng.uniform(0, 0.8), 0.2)
        return x
    if name == "hiss": d = 0.9; return hp(noise(d), 2500) * (t(d) / d) ** 1.5 * 0.45                       # the battery venting
    if name == "whoomph": d = 0.8; tt = t(d); return (lp(noise(d), 500) * env(len(tt), 0.004, 0.25) * 1.6 + np.sin(2 * np.pi * (70 - 30 * tt / d) * tt) * env(len(tt), 0.003, 0.3)) * 0.9
    if name == "fizz":                                   # bubbling in the tub: dense tiny crackle
        d = 2.0; x = bp(noise(d), 2500, 9000) * 0.12; tt = t(d)
        for k in range(70): put(x, hp(noise(0.004), 3000) * env(int(0.004 * SR), 0.0002, 0.001), rng.uniform(0, d - 0.01), rng.uniform(0.2, 0.6))
        return x * np.minimum(1, np.minimum(tt / 0.2, (d - tt) / 0.4))
    if name == "plop": d = 0.4; tt = t(d); f = 320 - 200 * tt / d; return (np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(tt), 0.002, 0.08) + lp(noise(d), 2500) * env(len(tt), 0.001, 0.05) * 0.5) * 0.8
    if name == "splash": d = 0.45; tt = t(d); return (bp(noise(d), 400, 6000) * env(len(tt), 0.003, 0.12) + lp(noise(d), 300) * env(len(tt), 0.002, 0.08) * 0.6) * 0.75
    if name == "snow": d = 1.4; return hp(noise(d), 1500) * np.sin(np.pi * t(d) / d) ** 2 * 0.16                # dust drifting down
    if name == "roar":                                   # gas torch: steady breathy roar with a little flutter
        d = 1.8; tt = t(d); return bp(noise(d), 180, 3200) * (1 + 0.15 * np.sin(2 * np.pi * 9 * tt)) * np.minimum(1, np.minimum(tt / 0.08, (d - tt) / 0.25)) * 0.55
    if name == "sizzle": d = 1.1; tt = t(d); return hp(noise(d), 3500) * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * tt) ** 2) * np.sin(np.pi * tt / d) * 0.35
    if name == "clink":                                  # the bar: a weighty metallic ring
        d = 1.2; tt = t(d); return (np.sin(2 * np.pi * 1180 * tt) + 0.7 * np.sin(2 * np.pi * 1180 * 2.76 * tt) + 0.4 * np.sin(2 * np.pi * 1180 * 5.4 * tt)) * env(len(tt), 0.0005, 0.35) * 0.3
    if name == "drawer": d = 0.6; tt = t(d); return (lp(noise(d), 900) * 0.9 + np.sin(2 * np.pi * 95 * tt) * 0.2) * np.sin(np.pi * tt / d) * 0.6
    if name == "stamp":
        x = np.zeros(int(0.6 * SR)); put(x, fx("thud"), 0.0, 0.8); put(x, fx("slap"), 0.0, 0.7); return x
    return None  # silence handled elsewhere

# ---- effects: cues from the beat sheet's events + a few hand cues (times in seconds on the locked take)
FX = np.zeros(N)
def evs(kind): return [e for b in BEATS for e in b.get("events", []) if e["type"] == kind]
cues = [(0.0, "whoosh_soft", 0.7), (0.6, "impact", 0.9), (1.04, "clatter", 0.6), (1.3, "tick", 0.35), (1.5, "pop", 0.45),          # toss, bounces, hook title
        (4.1, "whoosh_soft", 0.45), (4.6, "shimmer", 0.8), (5.7, "pop", 0.4), (6.75, "stamp", 0.8), (10.0, "pop", 0.5),            # lid, glow, label, warning card, 3 steps
        (12.4, "whoosh_soft", 0.5), (13.9, "tap", 0.6), (14.3, "pop", 0.45), (15.9, "hiss", 0.8), (16.25, "whoomph", 0.9),          # battery out, battery fire
        (19.3, "shimmer", 0.6), (19.7, "pop", 0.4), (21.2, "tick", 0.4), (21.5, "pop", 0.4), (22.9, "pop", 0.4),                    # pins, chip, hair
        (24.0, "whoosh", 0.45), (25.25, "plop", 0.8), (25.7, "fizz", 0.35), (28.1, "fizz", 0.6), (29.1, "fizz", 0.55),              # dunk, blue, mud
        (32.0, "sparkle", 0.8), (32.7, "pop", 0.4), (33.9, "splash", 0.6), (34.57, "splash", 0.6), (35.23, "splash", 0.6),          # sparkle, wash rinse wash
        (36.1, "fizz", 0.55), (37.0, "fizz", 0.45), (38.6, "snow", 0.6), (40.1, "snow", 0.9), (42.6, "pop", 0.45), (44.4, "pop", 0.45), (45.7, "pop", 0.4),
        (46.75, "roar", 0.7), (48.15, "sizzle", 0.7), (49.45, "sizzle", 0.4), (49.55, "rise", 0.4), (49.7, "clink", 1.0), (49.7, "music_hit", 0.7), (49.8, "shimmer", 0.6),
        (52.6, "coin", 0.9), (52.9, "pop", 0.4), (54.9, "tick_rise", 0.6), (56.0, "whoosh", 0.55), (56.5, "pop", 0.4),
        (57.6, "pop", 0.45), (58.2, "pop", 0.4), (58.5, "pop", 0.4), (59.3, "confirm", 0.6),
        (60.9, "drawer", 0.8), (61.2, "pop", 0.3), (62.9, "pop", 0.4), (64.1, "tick_rise", 0.45), (64.94, "confirm", 0.6), (65.8, "pop", 0.45),
        (67.45, "drawer", 0.6), (67.6, "whoosh_soft", 0.6)]
for e in evs("dust"): pass                                              # (dust, powder and fizz are placed by hand above, on the event times)
for at, n, g in cues:
    x = fx(n)
    if x is not None: put(FX, x, at, g)

# ---- bed: a daytime yard (soft wind with slow gusts + a distant bird now and then), constant
tt_ = t(END + 0.4); wind = lp(noise(END + 0.4), 380, 2) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.11 * tt_) * np.sin(2 * np.pi * 0.047 * tt_ + 1))
BIRDS = np.zeros(len(tt_))
for at in np.arange(2.3, END, 6.7):
    for k in range(3):
        d = 0.09; f = np.linspace(3600, 4600, int(d * SR)) if k % 2 == 0 else np.linspace(4400, 3500, int(d * SR))
        put(BIRDS, np.sin(2 * np.pi * np.cumsum(f) / SR) * env(int(d * SR), 0.004, 0.04), at + k * 0.13 + rng.uniform(0, 0.4), 0.35)
BED = (wind * 2.2 + BIRDS * 0.06)[:N] * 0.10

# ---- music: a bright major pad + soft pulse, gated per line: out under REVEAL lines and R1, out half a beat before the turn (R2), back hard on it
tt = t(END + 0.4)
def saw(f, ph=0): return 2 * ((tt * f + ph) % 1.0) - 1
pad = sum(saw(f * (1 + dt), ph) * a for f, dt, ph, a in [(110, 0.0, 0.0, 0.45), (110, 0.004, 0.3, 0.35), (138.6, 0.0, 0.1, 0.3), (164.8, 0.003, 0.7, 0.28), (220, 0.002, 0.2, 0.15)])
pad = lp(pad, 1400, 2)
pulse = np.zeros(len(tt))
for k in np.arange(0.5, END, 1.0): put(pulse, fx("thud"), k, 0.25)
MUS = (pad * 0.22 + pulse[: len(pad)] * 0.4)
gate = np.ones(len(tt))
for l in T["lines"]:
    g = 0.0 if l["preset"] == "REVEAL" or l["block"] == "R1" else (0.45 if l["block"] in ("A",) else 1.0)
    gate[int(l["slot_start"] * SR): int(l["slot_end"] * SR)] = g
turn = next(l for l in T["lines"] if l["block"] == "R2")["slot_start"]
gate[int((turn - 0.5) * SR): int(turn * SR)] = 0.0
k = int(0.04 * SR); gate = np.convolve(gate, np.ones(k) / k, mode="same")
MUS = MUS[: N] * gate[: N]
# ---- mix: relative levels against the voice
def rms(x): return np.sqrt(np.mean(x ** 2) + 1e-12)
vr = rms(voice[voice != 0])
def level(x, db): return x * (vr * 10 ** (db / 20) / (rms(x) + 1e-12))
FXm = FX * 1.0
BEDm = level(BED, -27); MUSm = level(MUS, -21); 
os.makedirs("audio", exist_ok=True)
def measure(path, aac=False):
    """(integrated LUFS, true peak dBTP), optionally after the same AAC 192k encode the final uses (that is what QC measures)."""
    import re
    src = path
    if aac: src = path.replace(".wav", "_tp.m4a"); subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-c:a", "aac", "-b:a", "192k", src], check=True)
    e = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", src, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr.split("Summary:")[-1]
    if aac: os.remove(src)
    return float(re.findall(r"I:\s+(-?[\d.]+)", e)[0]), float(re.findall(r"Peak:\s+(-?[\d.]+)", e)[0])

def master(x, path, target_i=-14.0, target_tp=-2.0):
    """v3 (FIX #14): plain gain + a 4x-oversampled (true-peak) limiter, corrected until the AAC-encoded file measures
    -14 LUFS (+-0.15) and <= -2.0 dBTP. FIX #13 finals measured -1.0 / -0.7 dBTP after AAC (the old limiter saw sample peaks only,
    and loudnorm silently falls back to dynamic mode when headroom runs out)."""
    raw = path.replace(".wav", "_raw.wav"); sf.write(raw, np.stack([x, x], 1).astype(np.float32), SR)
    i0, _ = measure(raw); gain = target_i - i0; ceil = -3.0
    for _ in range(10):
        af = f"volume={gain:.2f}dB,aresample=192000,alimiter=limit={10 ** (ceil / 20):.4f}:attack=1:release=60:level=0,aresample=48000"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", af, "-ar", str(SR), "-c:a", "pcm_s16le", path], check=True)
        i_, tp = measure(path, aac=True); print(f"  {os.path.basename(path)}: gain {gain:+.2f} dB, ceiling {ceil:.1f} dB -> {i_:.1f} LUFS, {tp:.1f} dBTP after AAC")
        if abs(i_ - target_i) <= 0.15 and tp <= target_tp: break
        gain += target_i - i_
        if tp > target_tp: ceil -= (tp - target_tp) + 0.1
    os.remove(raw)
master(voice + FXm * 0.9 + BEDm + MUSm, "audio/mix_with_pad.wav")
master(voice + FXm * 0.9 + BEDm, "audio/mix_voice_fx.wav")
print("written audio/mix_with_pad.wav and audio/mix_voice_fx.wav")
