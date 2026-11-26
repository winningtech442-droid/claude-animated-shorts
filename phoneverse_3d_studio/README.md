# Phoneverse 3D studio (format A, from #13 onward)

One 3D world for every episode, built from three reference "how it works" shorts (phone teardown, Spitfire carburetor, optical mouse):
the **object is the star**, the **mechanism is shown from inside**, the **camera moves instead of cutting**, small **labels are pinned to parts**
and **live readouts** count up on screen. FIX #12's script and timings are staged here as the test episode (`data/beats_fix12.json`).

## The world (render/world.py, Blender 5 / bpy, Cycles CPU)
| Object | What it is for | Anchor name for labels |
|---|---|---|
| Hero phone (graphite, lies on the desk) | Shows any pvui screen live on a 3D screen | `screen`, `phone` |
| Phone lid (the screen) | Lifts on a hinge to show the circuit board | - |
| Circuit board: CPU, MODEM, SIM, battery, FILTER switch | "How it works" cutaway; the filter knob slides and glows orange | `cpu`, `modem`, `sim`, `filter` |
| Miniature mast (blinking red) | Where texts/calls come from | `mast` |
| Scammer laptop (red screen glow, no person) | Where stolen data goes | `laptop` |
| Unknown Senders tray (blue) | Where filtered texts land | `tray` |
| Data packets (head + trail) | `text` yellow, `card` red, `call` blue; arc between any two of mast / phone / laptop / tray | `packet` (first active one) |

Camera presets: `hero`, `screen`, `screen_close`, `screen_tilt`, `macro`, `macro_filter`, `mast`, `laptop`, `wide`, `tray`, `top`.
A beat's `cam: [from, to]` is one continuous eased move; a cut only happens where the next beat starts on a different preset.

## An episode = one beat sheet (data/beats_<ep>.json)
Each beat: `t0`/`t1` (from measured voice timings, never re-timed), `cam`, `screen` (a pvui expression, `p` = progress 0..1 in the beat),
`events` (`packet`, `lid`, `filter`, `laptop` glow), `labels` (`anchor`, `text`, optional `from`, `dx`, `dy`), `hud` (`value` or live `count`),
or `face: <clip>` to drop in a rendered 3D face reaction (keep it to 2-3 per episode). Header: `audio` (one final per mix), `captions`, `faces`, `hook`.

## Run order
```
uv venv -p 3.11 .venv && uv pip install -p .venv bpy pillow numpy        # (this checkout links .venv to ../phoneverse_fix12_studio/.venv)
.venv/bin/python render/world.py --beats data/beats_<ep>.json --test --res 432 768 --samples 16     # one still per beat (~2.5 min)
.venv/bin/python render/compose3d.py --beats data/beats_<ep>.json --test                           # docs/storyboard_3d.png: CHECK THIS FIRST
.venv/bin/python render/world.py --beats data/beats_<ep>.json --one 670                            # debug one frame
.venv/bin/python render/world.py --beats data/beats_<ep>.json --frames 0 1666 --res 540 960 --samples 16   # full render (resumable)
.venv/bin/python render/compose3d.py --beats data/beats_<ep>.json --range 0 1667
.venv/bin/python render/compose3d.py --beats data/beats_<ep>.json --assemble                       # final/<episode>_<mix>.mp4
python3 tools/qc.py final/<file>.mp4        # run from the episode's audio studio folder (it reads data/timings.json)
```
Render cost on this 4-core box: about 6 s a frame at 540x960 / 16 samples, so about 2.8 h for a 70 s episode. 720x1280 / 24 samples is about 3x that.

## Status (19 Nov 2026)
- Built and tested: world, packets, lid/cutaway, filter switch, camera moves, anchors, labels, HUD, hook, captions, face beats.
- `docs/storyboard_3d.png`: one frame per beat of FIX #12 re-staged. `docs/proof_first_12s.mp4`: the first 12 s in motion.
- Full showcase rendered: final/fix12_3d_test_mix_{voice_fx,with_pad}.mp4 (gitignored). QC: all PASS except "longest shot" 10.83 s
  (46.8-57.6 s, checked by eye: something changes about every 1.5 s, OK under v8). A frozen laptop shot (26.6-29.5 s) was fixed with the `laptop_close` push-in.
  Phone-size check: docs/phone_size_check_3d.png.
- Fix next: desk grain reads as corduroy stripes in wide shots; no part labels during the lid cutaway; the packet trail clumps into a blob;
  the call screen at 30.5 s is too small to read.
- Not done yet: sound design for packets (whoosh/ding per packet is the obvious next step),
  a richer desk set (lamp, mug) and a stronger laptop look.

## FIX #15 additions (21 Nov 2026)
- render/char_scene.py: character acting clips (beat key `char`), with the lead on a sofa and the hooded figure from behind. Arms use
  an analytic two-bone IK because Biped bones are unconnected; hands are oriented per pose; faces use the approved recipes.
  world.py skips char beats, and compose3d.py reads build/chars/<clip>/NNNN.png.
- world.py prop `wallet`: your bank card (flips to show the number on the back), a glowing copy that flies to the scammer's phone
  (events `ghost`, `freeze`, `cardflip`), and the scammer's phone, whose screen comes from the beat key `scam`. Packet nodes `card`
  and `scamphone`; camera presets card_macro, card_top, path_wide, path_side, scam, scam_close, scam_tilt.
- build_fix15.sh renders the character clips first, then the desk frames, then compose, assemble, QC and the phone-size sheet.
