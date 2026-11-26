You are building one Phoneverse short in format A from this studio folder. Read README.md and BUILD_BRIEF.md first.
Inputs for a new episode: the measured voice take, data/timings.json, captions.json (same tools as the FIX #12 studio) and a topic.
Do, in order: (1) write data/beats_<ep>.json from the line timings: one world, show the mechanism from inside at least once, 2-3 face beats at most,
a hook for the first ~3 s, labels and live readouts where the script gives a number; (2) world.py --test and compose3d.py --test, show me
docs/storyboard_3d.png before rendering; (3) full render (resumable) and compose; (4) assemble one final per audio mix; (5) run tools/qc.py on each
and report every FAIL honestly (read "longest shot" per BUILD_BRIEF.md); (6) tell me what looks wrong at phone size.
Do not alter the audio, the timings or the script wording. Do not post anything.
