# Phoneverse FIX #14: Crackgate (iPhone Duo inner screen cracking at the fold) — studio package

Threat story, HSERIA + CTA, second person, rule book v8 (format A), **no face beats** (user: no characters this episode).
Rendered in ../phoneverse_3d_studio with data/beats_fix14.json (37 beats; generator data/make_beats_fix14.py).
Take 62.42 s, 21 lines, 163 words, 3.02 w/s speech pace, tail 0.32 s. Kokoro **af_heart** only (voice B; a review said the old
Bella/Nicole narrator read too soft): no whisper preset, no negative gain, reaction lines ("Wait!", "What was that?!",
"Half of two thousand... solid... British pounds!") with their own presets. The voice is compressed (3:1) before the mix.

## Script decisions (made before the take was locked, never re-timed after)
- Hook: the phone drops and bounces (user's idea), then cracks when you open it; the drop pays off at "if Apple thinks you dropped it".
- The user asked to change "£999" to "two thousand pounds". The inner-screen repair really is £999, so the bill stays £999 and the
  "two thousand solid British pounds" line is used for the phone's price (£1,999), which is true. The user can overrule this.
- The 30-day / 6-month lines are the Consumer Rights Act 2015; the right is against the seller (say so in the post caption).

## Files
- data/lines.json (script + per-line presets), data/timings.json (measured, locked), data/captions.json (92 cards, proportional timing).
- audio/voice_take.wav|mp3, audio/lines/, audio/mix_with_pad.wav, audio/mix_voice_fx.wav, audio/auditions/auditions_A_to_E.mp3.
- tools/make_voice.py, build_captions.py (keeps "£1,499" commas), make_sound.py, qc.py.

## Sound (tools/make_sound.py v3)
Mastering is plain gain + a 4x-oversampled (true-peak) limiter, corrected in a loop until the AAC-encoded file measures -14 LUFS (+-0.15)
and <= -2.0 dBTP. FIX #13's loudnorm + sample-peak limiter measured -1.0 / -0.7 dBTP after AAC. Finals: -14.1 LUFS, -2.6 / -3.5 dBTP.

## Setup
Shared tools live in ../phoneverse_3d_studio (gitignored; the environment's setup script installs them):
.venv (bpy 5.0.1, numpy<2), .venv_voice (kokoro-onnx 0.6.1, numpy 2), models/ (Kokoro v1.0), assets/ (Rocketbox, not used this episode).
```
../phoneverse_3d_studio/.venv_voice/bin/python tools/make_voice.py --models ../phoneverse_3d_studio/models
python3 tools/build_captions.py && ../phoneverse_3d_studio/.venv_voice/bin/python tools/make_sound.py
cd ../phoneverse_3d_studio && python3 data/make_beats_fix14.py && setsid nohup ./build_fix14.sh > build_fix14.log 2>&1 &
```
Note: the cloud container is reclaimed when the session goes idle, which kills a detached render. Keep the session busy
(poll the log) until FIX14_DONE; build_fix14.sh resumes from the frames already rendered.

## Facts (check before posting)
- Owners report inner screens cracking along the fold, some within hours (Forbes, 27 Oct 2026).
- The hook theory is Ricky Panesar's (repair expert quoted by Forbes): phrased as "one repair expert thinks".
- Apple: "aware of an issue impacting the inner display on a small number of iPhone Duo units ... contact AppleCare for a replacement."
- UK repair prices (Forbes / Apple): inner screen £999, other damage £1,499 out of warranty; £79 with AppleCare+ (£16.99 a month).
- Consumer Rights Act 2015: 30 days to reject a faulty product for a refund; first 6 months a fault is presumed present from delivery.
