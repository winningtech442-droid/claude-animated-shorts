#!/usr/bin/env python3
"""Synthesised sound for FIX #15 (from FIX #14) (adapted from FIX #13 / FIX #12 (all original, no samples): rain-and-bus bed, kitchen tone, effects, a dark pad with a low pulse,
mixed with the directed voice. Reads data/shots.json + data/timings.json. Writes audio/mix_with_pad.wav and audio/mix_voice_fx.wav
(voice + bed + effects, no pad: for adding a TikTok sound by hand). Both are normalised to -14 LUFS, true peak -1.5 dB (two-pass loudnorm).
Music rules (rule book 5): music out under every REVEAL line, on re-hooks, half a beat before the turn; it hits back on the turn."""
import json, os, subprocess, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly
SR = 48000; rng = np.random.default_rng(12)
T = json.load(open("data/timings.json")); BS = json.load(open("../phoneverse_3d_studio/data/beats_fix15.json")); BEATS = BS["beats"]
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
    return None  # silence / room_tone / bus_hum handled elsewhere

# ---- effects: packets from the beat sheet (launch whoosh, arrival ding; a blocked 'bounce' packet gets a dull block) + hand cues
FX = np.zeros(N); cues = []
for b in BEATS:
    for e in b.get("events", []):
        if e["type"] != "packet": continue
        cues.append((e["t0"], "launch", 0.45))
        if e.get("bounce"): cues.append(((e["t0"] + e["t1"]) / 2, "block", 0.6))
        else: cues.append((e["t1"] - 0.05, "ding", 0.5))
cues += [(0.05, "whoosh_soft", 0.7), (0.3, "rise", 0.5), (1.45, "impact", 0.5), (1.5, "confirm", 0.6), (1.9, "pop", 0.5),
         (5.4, "tick_rise", 0.6), (6.1, "pop", 0.4), (7.65, "buzz", 0.6), (8.1, "pop", 0.4), (9.65, "pop", 0.5), (11.3, "pop", 0.5),
         (12.7, "keys", 0.5), (13.4, "keys", 0.5), (14.4, "keys", 0.45), (15.6, "keys", 0.5), (16.3, "keys", 0.5), (17.0, "keys", 0.45),
         (19.3, "keys", 0.5), (20.1, "keys", 0.45), (22.45, "buzz", 0.6), (24.2, "tap", 0.6), (24.6, "tap", 0.5), (25.0, "tap", 0.5),
         (25.95, "ringtone", 0.45), (27.7, "tap", 0.5), (30.55, "whoosh", 0.6), (31.65, "confirm", 0.6), (32.2, "pop", 0.5),
         (34.0, "confirm", 0.45), (34.5, "confirm", 0.45), (35.0, "confirm", 0.45), (37.6, "tick_rise", 0.6), (38.4, "tick_rise", 0.6),
         (39.75, "music_hit", 0.8), (39.75, "stab", 0.6), (42.0, "pop", 0.5), (44.95, "rise", 0.5), (47.4, "slap", 0.9),
         (48.9, "whoosh_soft", 0.4), (50.6, "stab", 0.5), (51.8, "pop", 0.5), (53.2, "buzz", 0.6), (55.05, "card_flip", 0.7), (55.6, "pop", 0.5),
         (56.4, "tap", 0.5), (58.35, "lock_click", 0.8), (59.3, "confirm", 0.6), (60.7, "pop", 0.4), (62.1, "keys", 0.45),
         (63.6, "whoosh", 0.5), (65.1, "card_flip", 0.5), (66.3, "tap", 0.5)]
for at, n, g in cues:
    x = fx(n)
    if x is not None: put(FX, x, at, g)

# ---- bed: Friday night indoors (low room rumble + faint city wash through the window), constant
city = lp(noise(END + 0.4), 140, 2) * 3.0 + hp(lp(noise(END + 0.4), 2500), 300) * 0.25
BED = city[:N] * 0.10

# ---- music pad + pulse, gated per line: out under REVEAL lines and R1, out half a beat before the turn (R2), back hard on it
tt = t(END + 0.4)
def saw(f, ph=0): return 2 * ((tt * f + ph) % 1.0) - 1
pad = sum(saw(f * (1 + dt), ph) * a for f, dt, ph, a in [(55, 0.0, 0.0, 0.5), (55, 0.004, 0.3, 0.4), (82.4, 0.0, 0.1, 0.3), (110, 0.003, 0.7, 0.25), (130.8, 0.002, 0.2, 0.15)])
pad = lp(pad, 900, 2)
pulse = np.zeros(len(tt))
for k in np.arange(0.5, END, 1.0): put(pulse, fx("thud"), k, 0.35)
MUS = (pad * 0.22 + pulse[: len(pad)] * 0.5)
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
