"""Audition a new guest voice. v3 rule: every guest gets a voice the user approves before any of its lines are voiced.

usage: python3 -I tools/make_voice.py <name> '<kokoro blend json>' <speed> <pitch_semitones> "<line>[|<line>...]" [exaggeration] [cfg]
  e.g. python3 -I tools/make_voice.py shopkeeper '{"bm_george": 0.5, "bm_fable": 0.5}' 0.86 -3 "That's twenty sixteen money, son." 0.5 0.5
Writes out/voices/<name>.wav (the reference clip: Kokoro reading the cast reference text from voices/cast.json) and
out/voices/<name>_audition_N.wav (Chatterbox performing each line in that voice).
Once the user approves: copy out/voices/<name>.wav into voices/ and add the settings to voices/cast.json.
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name, blend, speed, semis = sys.argv[1], json.loads(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
lines = [l.strip() for l in sys.argv[5].split("|") if l.strip()]
exg = float(sys.argv[6]) if len(sys.argv) > 6 else 0.5
cfg = float(sys.argv[7]) if len(sys.argv) > 7 else 0.5
out = os.path.join(ROOT, "out", "voices"); os.makedirs(out, exist_ok=True)

from kokoro_onnx import Kokoro
from pedalboard import Pedalboard, PitchShift
V = "/root/voice"
k = Kokoro(f"{V}/kokoro-v1.0.onnx", f"{V}/voices-v1.0.bin")
style = sum(w * k.get_voice_style(v) for v, w in blend.items())
text = json.load(open(os.path.join(ROOT, "voices", "cast.json")))["cast_reference_text"]
audio, sr = k.create(text, voice=style, speed=speed, lang="en-gb")
if semis:
    audio = Pedalboard([PitchShift(semitones=semis)])(audio.astype(np.float32), sr)
ref = os.path.join(out, f"{name}.wav")
sf.write(ref, audio, sr)
print(f"{ref}: {len(audio) / sr:.1f} s reference ({blend}, speed {speed}, pitch {semis:+})")

jobs = [dict(text=l, ref=ref, exaggeration=exg, cfg=cfg, seed=1000 + i, out=os.path.join(out, f"{name}_audition_{i + 1}.wav")) for i, l in enumerate(lines)]
jf = os.path.join(out, f"{name}_jobs.json"); json.dump(jobs, open(jf, "w"), indent=1)
subprocess.run(["/root/cb-venv/bin/python", os.path.join(ROOT, "tools", "chatterbox_gen.py"), jf], check=True)
print("auditions:", ", ".join(os.path.basename(j["out"]) for j in jobs))
