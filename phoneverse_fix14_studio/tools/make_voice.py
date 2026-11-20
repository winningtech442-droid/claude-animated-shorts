#!/usr/bin/env python3
"""Directed Kokoro take for Phoneverse Phoneverse (Voice Spec v2.1: line by line, presets, no pitch shift, 12 ms fades).
Usage: python3 tools/make_voice.py [--models DIR] [--out audio]
Needs: pip install kokoro-onnx soundfile numpy scipy ; kokoro.onnx + voices.bin in --models (default: .)
Writes audio/lines/line_NN.wav (24 kHz), audio/voice_take.wav (48 kHz), audio/voice_take.mp3 and data/timings.json.
"""
import argparse, json, os, re, sys
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
from kokoro_onnx import Kokoro

ap = argparse.ArgumentParser()
ap.add_argument("--models", default=".")
ap.add_argument("--out", default="audio")
ap.add_argument("--data", default="data/lines.json")
a = ap.parse_args()

D = json.load(open(a.data))
k = Kokoro(os.path.join(a.models, "kokoro.onnx"), os.path.join(a.models, "voices.bin"))
SR = 24000
os.makedirs(os.path.join(a.out, "lines"), exist_ok=True)

def style(blend):
    return sum(w * k.get_voice_style(n) for n, w in blend.items())

def fade(x, ms=12):
    n = int(SR * ms / 1000)
    x = x.copy(); r = np.linspace(0, 1, n)
    x[:n] *= r; x[-n:] *= r[::-1]
    return x

parts, timings, t = [], [], 0.0
for L in D["lines"]:
    P = D["presets"][L["preset"]]
    y, sr = k.create(L["spoken"], voice=style(P["blend"]), speed=P["speed"], lang="en-us")
    assert sr == SR
    y = fade(y.astype(np.float32) * (10 ** (P["gain_db"] / 20)))
    sf.write(os.path.join(a.out, "lines", f"line_{L['id']:02d}.wav"), y, SR)
    pre = np.zeros(int(SR * P["pause_before"]), dtype=np.float32)
    post = np.zeros(int(SR * P["pause_after"]), dtype=np.float32)
    start = t + P["pause_before"]                      # first audible sample
    dur = len(y) / SR
    words = len(re.findall(r"[A-Za-z0-9£'’-]+", L["text"]))
    timings.append({"id": L["id"], "block": L["block"], "preset": L["preset"], "text": L["text"], "star": L["star"],
                    "face": L["face"], "words": words, "start": round(start, 3), "speech_s": round(dur, 3),
                    "end": round(start + dur, 3), "pause_before": P["pause_before"], "pause_after": P["pause_after"],
                    "slot_start": round(t, 3), "slot_end": round(start + dur + P["pause_after"], 3)})
    parts += [pre, y, post]
    t = start + dur + P["pause_after"]

take = np.concatenate(parts)
peak = np.max(np.abs(take))
if peak > 0.89: take = take * (0.89 / peak)              # about -1 dBFS ceiling, no limiter
take48 = resample_poly(take, 2, 1).astype(np.float32)
sf.write(os.path.join(a.out, "voice_take.wav"), take48, 48000)
os.system(f'ffmpeg -y -loglevel error -i "{os.path.join(a.out, "voice_take.wav")}" -b:a 192k "{os.path.join(a.out, "voice_take.mp3")}"')

total = len(take) / SR
sp = sum(x["speech_s"] for x in timings); words = sum(x["words"] for x in timings)
last = timings[-1]
summary = {"take_length_s": round(total, 2), "speech_seconds": round(sp, 2), "words": words,
           "speech_pace_wps": round(words / sp, 2), "tail_after_last_word_s": round(total - last["end"], 2),
           "limits": {"take_s": [60, 70], "pace_wps": [2.8, 3.2], "tail_max_s": 0.5, "words": [155, 205]}}
json.dump({"summary": summary, "lines": timings}, open("data/timings.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
