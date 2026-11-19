#!/usr/bin/env python3
"""Synthesised sound for FIX #12 (all original, no samples): rain-and-bus bed, kitchen tone, effects, a dark pad with a low pulse,
mixed with the directed voice. Reads data/shots.json + data/timings.json. Writes audio/mix_with_pad.wav and audio/mix_voice_fx.wav
(voice + bed + effects, no pad: for adding a TikTok sound by hand). Both are normalised to -14 LUFS, true peak -1.5 dB (two-pass loudnorm).
Music rules (rule book 5): music out under every REVEAL line, on re-hooks, half a beat before the turn; it hits back on the turn."""
import json, os, subprocess, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly
SR = 48000; rng = np.random.default_rng(12)
shots = json.load(open("data/shots.json"))["shots"]; T = json.load(open("data/timings.json"))
END = T["summary"]["take_length_s"]; N = int((END + 0.4) * SR)
voice, vsr = sf.read("audio/voice_take.wav"); voice = np.pad(voice.astype(np.float64), (0, max(0, N - len(voice))))[:N]
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
    return None  # silence / room_tone / bus_hum handled elsewhere

# ---- effects from the shot list
FX = np.zeros(N)
for s in shots:
    for e in s["sfx"]:
        x = fx(e["name"])
        if x is not None: put(FX, x, e["t"], 0.55)

# ---- beds: rain + bus hum (set A, until the kitchen at line 10), kitchen tone after
kit = next(s for s in shots if s["id"] == "10a")["start"]
rain = hp(lp(noise(END + 0.4), 7000), 900) * 0.55; hum = lp(noise(END + 0.4), 90, 2) * 4.0 + np.sin(2 * np.pi * 52 * t(END + 0.4)) * 0.5
bed_a = (rain * 0.5 + hum * 0.5); bed_c = lp(noise(END + 0.4), 400) * 0.25 + np.sin(2 * np.pi * 100 * t(END + 0.4)) * 0.06 + rain * 0.08
sw = np.clip((t(END + 0.4) - kit) / 0.03, 0, 1)
BED = (bed_a * (1 - sw) + bed_c * sw)[:N] * 0.10
# a window-rain lift after the cut keeps the kitchen from feeling dead

# ---- music pad + pulse, gated by the per-shot music state
tt = t(END + 0.4)
def saw(f, ph=0): return 2 * ((tt * f + ph) % 1.0) - 1
pad = sum(saw(f * (1 + dt), ph) * a for f, dt, ph, a in [(55, 0.0, 0.0, 0.5), (55, 0.004, 0.3, 0.4), (82.4, 0.0, 0.1, 0.3), (110, 0.003, 0.7, 0.25), (130.8, 0.002, 0.2, 0.15)])
pad = lp(pad, 700 + 500 * np.sin(2 * np.pi * tt / 14.0) ** 2, 2) if False else lp(pad, 900, 2)
pulse = np.zeros(len(tt))
for k in np.arange(0.5, END, 1.0): put(pulse, fx("thud"), k, 0.35)
MUS = (pad * 0.22 + pulse[: len(pad)] * 0.5)
gate = np.ones(len(tt)) * 0.0
for s in shots:
    st, en = s["start"], s["end"]; m = s["music"]
    g = {"on": 1.0, "dip": 0.45, "out": 0.0, "out_late": 1.0}[m]
    gate[int(st * SR): int(en * SR)] = g
# music out half a beat before the turn, then back hard on 13a
turn = next(s for s in shots if s["id"] == "13a")["start"]
gate[int((turn - 0.45) * SR): int(turn * SR)] = 0.0
# short smoothing so the gate never clicks (40 ms) but the hit still lands hard
k = int(0.04 * SR); gate = np.convolve(gate, np.ones(k) / k, mode="same")
# the pad swells back in with the turn
MUS = MUS[: N] * gate[: N]
MUS = MUS * (0.6 + 0.4 * np.clip((tt[:N] - turn + 0.0) / 1.5, 0, 1) ** 0 )

# ---- mix: relative levels against the voice
def rms(x): return np.sqrt(np.mean(x ** 2) + 1e-12)
vr = rms(voice[voice != 0])
def level(x, db): return x * (vr * 10 ** (db / 20) / (rms(x) + 1e-12))
FXm = FX * 1.0
BEDm = level(BED, -27); MUSm = level(MUS, -21); 
os.makedirs("audio", exist_ok=True)
def master(x, path):
    raw = path.replace(".wav", "_raw.wav"); sf.write(raw, np.stack([x, x], 1).astype(np.float32), SR)
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    j = json.loads(p.stderr[p.stderr.rindex("{"): p.stderr.rindex("}") + 1])
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,alimiter=limit=0.79:attack=2:release=40:level=0")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", af, "-ar", str(SR), "-c:a", "pcm_s16le", path], check=True); os.remove(raw)
master(voice + FXm * 0.9 + BEDm + MUSm, "audio/mix_with_pad.wav")
master(voice + FXm * 0.9 + BEDm, "audio/mix_voice_fx.wav")
print("written audio/mix_with_pad.wav and audio/mix_voice_fx.wav")
