# What If UK studio

Remotion + three.js, 1080x1920, 30 fps, plain (no motion blur since 11 Nov; STUDIO-RULES 3a). Built on the 3D Explainer Shorts guide's pipeline, with the page's own cast,
scene library, shot engine, sound and checks. Rules: the project's claude/script-rules.md (one-page checklist) and STUDIO-RULES.md (studio only).

## Making an episode

1. Script -> `src/episodes/<id>/script.txt` (61-80 s; facts sourced first).
1b. Gate on the script: `python3 -I tools/gate.py <ep>` (hook by line 3, one ask, facts.md checked).
2. Voice (house voice E): write `src/episodes/<id>/voice.txt` (one line per row, `speed|pause|text`), then
   `python3 -I tools/house_voice.py src/episodes/<id>/voice.txt out/<id>/vo.mp3` (must be 61-80 s).
3. Word timings: `python3 -I tools/align.py src/episodes/<id>/script.txt out/<id>/vo.mp3 src/episodes/<id>/words.json --peek`
   Numbers and words the aligner doesn't know need one flag each: `--say "1694=sixteen ninety four" --say "covid=cove id"`.
   (no voice yet: `python3 -I tools/placeholder_words.py src/episodes/<id>/script.txt src/episodes/<id>/words.json`)
4. Shot list -> `src/episodes/<id>/episode.ts` (copy `episodes/demo`): one picture per phrase, cut on its words;
   add the episode to `EPISODES` in `src/Root.tsx`.
5. Stills: `T=$(npx tsx tools/starts.mts <id>); node tools/stills.mjs out/<id>/st <CompId> $T; python3 -I tools/sheet.py out/<id>/st out/<id>/sheet.jpg 6`
   Look, fix, look again.
6. Everything else, one command: `tools/build.sh <id> <CompId> out/<id>/vo.mp3`
   (events -> music -> effects -> pace check -> picture -> mix -> final check). Output: `out/<id>.mp4`.

## What's where

| Path | What |
|---|---|
| src/cast/ | The cast (Person.tsx: body, 12 faces, Union Jack pin) and their looks (cast.ts) |
| src/worlds/ | street (eras 1975 / 1988 / 2026), bank, shop, kitchen, floor (trading floor), table (close-ups), committee (the Bank's committee room) |
| src/props/ | Coin, CoinStack, Note (generic, marked ILLUSTRATIVE), PriceTag, Newspaper, ChartScreen, Meter, Barrel, Dial, House, SaleBoard, Trolley, Tea, Phone |
| src/engine/ | The shot engine: types, timing (T/cues), Episode player (camera, fly/whip transitions, number card, captions) |
| audio/ | score.py (original music), sfx.py (effects on events), mix.py (voice on top, -14 LUFS) |
| tools/ | align, placeholder words, starts, stills, sheet, pacecheck, dumpevents, render_chunks, build, qa |

Shot fields: `cue` (the phrase it cuts on), `world`, `cam.from/to` (position, target, fov; `move`: drift | fast | hold),
`enter` (cut | whip | fly), `exitInto` (where the camera dives before a fly), `actors` (who, at, faces and poses over
time), `props` (kind, at, pop-in time, moves (`ease: 'drop'` slams), a growing number (`round: false` for smooth values)),
`number` (the one big-number card), `whatif` (the timeline switch). Episode: `hook` (the opening on-screen question).
Set preview: composition SetPreview shows every new set and prop.
