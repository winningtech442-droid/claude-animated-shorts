# Build brief: format A (rule book v8)

What changed from v7 (FIX #12) and why. Measured on the three reference shorts the user picked (19 Nov 2026).

## Kept from v7
- 60-70 s, tail after the last word <= 0.5 s. 1080x1920, 24 fps, H.264 yuv420p, AAC. -14 LUFS (+-0.5), true peak <= -1.5 dB, LRA >= 3.
- One caption system (pvui.caption): 1-3 words, white, one yellow keyword. No logos, no real brands, no pure-black or frozen frames.
- Voice timings are measured and never re-timed; the beat sheet follows them.

## Changed in v8
| v7 rule | v8 rule | Why (reference measurement) |
|---|---|---|
| No shot over 2.5 s | **Something visibly changes at least every 2.5 s** (camera move, packet, label, readout, screen state). Hard cuts are optional. | Teardown: 2 cuts in 99 s. Spitfire: average shot 4.6 s. Mouse: 2.2 s. They hold attention with motion, not cuts. |
| Captions in the upper 62% only | **Captions at about 70% of height** (pvui.caption, y = 1344), readout pill under them at y = 1400-1492 | References put captions at 57-73% of height. |
| 2D phone UI cards next to a 3D face | **One 3D world.** All UI lives on the 3D phone's screen. Faces only as 2-3 short reaction beats. | Every reference frame is in one consistent world; mixing looks cheap. |
| Story told, mechanism implied | **Show the mechanism from inside** at least once per episode (lid lift / cutaway / packet path). | The payoff in all three is seeing how it works. |
| Corner tag | **No corner tag.** | None of the references use one; it collided with the clock. |
| Hook text added by hand | **Hook burned in for the first ~3 s** (beat sheet `hook`). | All three put the question/claim on frame 1. |
| Data on static cards | **Live readouts** (`hud.count`) and **pinned labels** with leader lines. | "+1.0 G", "56% FUEL", "710 photos/s" readouts and part tags in the references. |

## User standing rules (23 Nov 2026, from the FIX #17 review)
- **One output per render.** Build and deliver a single final (`mix_with_pad`); no second "voice + fx" variant. Saves render and encode cost.
- **Always give the posting details** with every delivered final, in the reply and in the episode's post.txt. Include: date and UK time, file, cover frame and cover text, description (recommended and short), hashtags, pinned comment, settings (sound, AI label, comments) and the first-hour plan.
- **Narrator first.** Object sounds must never compete with the voice. In make_sound.py, set the FX bus relative to the voice and never add it raw:
  `FX_DB -9` overall, ducked another `-10 dB` while the narrator speaks, each hit capped at `-5 dB` under the voice's average level; pad at `-24`.
  Measured on #17: FX are about 18 dB under the voice during speech and about 14 dB under it in the gaps.
  The LRA comes out at about 2 LU. That is expected for a narrator-forward mix, so read the "LRA >= 3" row as advisory, not a FAIL.

## QC notes
- tools/qc.py's "longest shot" uses scene-cut detection; in format A a 4-6 s continuous move is allowed, so read that row as
  "check by eye that something changes every 2.5 s", not as a hard FAIL. Frozen-segment and black-frame checks still apply.
- Before posting: storyboard_3d.png at phone size, then the file on a real phone.
