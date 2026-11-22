# Phoneverse FIX #12: Black Friday fake delivery text (studio package)

Threat story, HSERIA + CTA, second person. Take 69.45 s, 178 words, 3.01 words/s, tail 0.2 s. Render happens in Claude Code, not here.

## What is already built (verified)
- audio/voice_take.wav|mp3: Kokoro af_bella, directed per line (audio/lines/ = the 21 separate lines).
- audio/mix_with_pad.* (voice + rain/bus bed + SFX) and audio/mix_voice_fx.* (voice + SFX only). Measured -14.2 LUFS, true peak -1.8 dB, LRA 5.3.
- data/: lines.json, timings.json (measured line starts), shots.json/.csv (49 sub-shots), captions.json (105 cards), face_recipes.json, face_clips.json.
- render/pvui.py (2D phone UI props), render/compose.py (frame compositor), render/face_scene.py (Blender face clips, UNTESTED).
- tools/qc.py (measured checks), tools/make_*.py + build_*.py (rebuild voice, shots, captions, sound).
- docs/storyboard_preview.png (all 49 shots, placeholder faces), docs/props_contact_sheet.png.

## What is not built
- The 3D face clips (frames/<clip>/0000..0047.png). Until they exist compose.py draws grey placeholder heads.
- The final video. Nothing was rendered here.

## Run order in Claude Code
1. Read BUILD_BRIEF.md, then paste CLAUDE_CODE_PROMPT.md.
2. `pip install pillow numpy scipy` (voice tools also need kokoro-onnx; skip if you keep audio/ as is).
3. Face clips: `blender -b -P render/face_scene.py` (see brief: download the Rocketbox files first). Check one clip by eye before rendering all.
4. `python render/compose.py --test` then look at docs/storyboard_preview.png.
5. `python render/compose.py --range 0 1667` (resumable), then `python render/compose.py --assemble`.
6. `python tools/qc.py final/phoneverse_fix12_with_pad.mp4`, then look at the file at phone size.
7. Add the TikTok text hook and music by hand; post at the time in the post file.

## Before you render: do these by hand
- Open Messages > Filters > Manage Filtering > Screen Unknown Senders on a real iPhone and confirm the wording (iOS 26 is verified from Apple Support; iOS 27 is not).
- Open Barclays' own page for the 34% figure (checked via press coverage, not the primary page).
