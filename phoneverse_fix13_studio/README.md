# Phoneverse FIX #13: The fake mast in a van (SMS blaster) — studio package

Threat story, HSERIA + CTA, second person, rule book v8 (format A). Rendered in ../phoneverse_3d_studio with data/beats_fix13.json.
Take 67.28 s, 18 lines, 164 words, 2.83 w/s speech pace, tail 0.2 s. Kokoro af_bella, directed per line (same presets as FIX #12).

## Script changes from the approved draft (made before the take was locked, never re-timed after)
The first take ran 80.3 s. To land inside 60-70 s without speeding the voice: cut "Your network blocks scam texts, right? Not this one.",
cut "One drove round London sending fake HMRC and bank texts.", cut "Emergency calls still work." (put it in the post caption instead),
and shortened the iPhone line to "iPhones have no 2G switch, only heavy Lockdown Mode."

## Files
- data/lines.json (script + direction), data/timings.json (measured, locked), data/captions.json (91 cards, proportional timing ±0.25 s:
  the Whisper aligner model could not be downloaded here because the network blocks Hugging Face).
- audio/voice_take.wav|mp3, audio/lines/, audio/mix_with_pad.wav, audio/mix_voice_fx.wav (both -14 LUFS, TP -1.5 dB).
- tools/make_voice.py, build_captions.py, make_sound.py (packet SFX read from the beat sheet: launch whoosh, arrival ding, 'block' on a bounced packet), qc.py.
- data/face_clips.json: 3 reaction clips (st_hope, st_shock, st_relief), street-night set. render/face_scene.py renders them.

## Setup (gitignored: models/, assets/, frames/, .venv/)
```
uv venv -p 3.11 .venv && uv pip install -p .venv kokoro-onnx soundfile scipy numpy pillow      # voice venv (numpy 2)
# bpy lives in ../phoneverse_3d_studio/.venv with numpy<2 (bpy 5.0 breaks on numpy 2)
curl -L -o models/kokoro.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -L -o models/voices.bin  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
# Rocketbox Female_Adult_01: see ../phoneverse_fix12_studio/BUILD_BRIEF.md (fbx -> assets/, tga -> assets/tex/)
.venv/bin/python tools/make_voice.py --models models && python3 tools/build_captions.py && .venv/bin/python tools/make_sound.py
for c in st_hope st_shock st_relief; do ../phoneverse_3d_studio/.venv/bin/python render/face_scene.py --clip $c --frames 0 47 --out frames/$c; done
```

## Facts (check before posting)
- Fake mast pulls phones onto a fake 4G signal, forces 2G (no mutual authentication), sends the text, releases: under 10 s (Enea researcher, via TechSpot/Futurism).
- Texts never pass the operator's filters (City of London Police). UK cases: car boot (London), van (Lancashire, ISPreview Sept 2026); convictions 2025-26.
- Android "Allow 2G" off fully mitigates (Google security blog, Aug 2024); Pixel has it, Samsung depends on model/software. 2G stays available for emergency calls.
- iPhone: no 2G switch; Lockdown Mode disables 2G (iOS 17+). 7726 is the free UK spam-forwarding number.
