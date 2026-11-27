# What If Britain: studio rules (v20 Nov 2026)

The writing, hook, topic and posting rules live in ONE place: the project's **claude/script-rules.md** (the one-page
checklist, 16 Nov 2026). This file keeps only what the studio code needs. Change a rule on purpose, never by drift,
and change one thing per episode.

## 1. Format
Today (0-5 s, what-if heard by 4.5 s) / Then (5-20 s) / What if (20-50 s) / Your wallet (50-70 s) / Ask (last 5 s).
61-70 s (aim 61-68), 160-200 words at 2.9-3.2 words a second, no line over 15 words, no line said twice, no line
copied from the last two episodes, narrator only. The gate checks it.
(20 Nov: the WW2 loan video ran 80 s at 2.6 words/s with "But what if...?" said twice: 28% watched on average.)

## 2. Picture
- **Frame 1:** bright daylight, a familiar UK place, Alfie big and central (head at least a third of the frame width),
  already moving; one red pop word by 1 s; the `hook` question card for the first 3 s only. Never night, a void,
  spotlights on black, paperwork or an empty room.
- **The first second (20 Nov 2026).** Both retention graphs we have lost about half the viewers by 0:01-0:02
  (WW2 loan: 270 views, 28% watched; savings: 714 views, 16%). So:
  - The shock word is *spoken* inside 1 s: it is the line-1 pop word and sits in the first 4 words (gate: FIRSTWORDS).
  - Frame 1 shows the consequence already happening (the cheque slams, the pint price flips, the jar cracks) with an
    impact sound on frame 1. Never a wave, a hello or a character standing still.
  - At most two text layers in the first 3 s: the caption and ONE big word. The `hook` card replaces the pop word
    rather than stacking with it, and it never asks a question the voice answers in the same breath.
  - Judge every post at 24 h by the share still watching at 3 s (aim 65%+), then average watch time (aim 40%+).
- **One location per episode, a new angle every 2-2.5 s** (each picture 1.2-4 s), one slow move inside each shot,
  push in on every reaction. Only the timeline switch may whip.
- **Real objects only** (payslip, pint, meter, house, jar, price board); no abstract blocks, barriers or capsules.
- **Motion with weight:** ease in and out, anticipation, overshoot and settle; an impact sound when a thing lands.
- **Grade:** warm daylight plus the navy / red / cream brand colours; soft rim light and contact shadows; no neon cyan.
- **Captions on every video:** bold white word by word with a black outline in the lower third, one red pop word per
  beat. Signs and tags short and fully readable (tags 7 characters, headlines 12).
- A prop or shot at most twice per episode; camera preset at most 6 times; one set at most 14 shots.
- **30 fps, no motion blur** (`MB=0`). A shot whose point is a sign or number holds or drifts once the text is in frame.

## 3. The set plan (LOCKED 6 Nov 2026)

Build a library once and rotate it, rather than a new set from scratch every episode. Four rules came with it:

1. **No set opens an episode on an empty room or on paperwork.** The committee room and the Treasury are never frame 1,
   and something always moves in them (the chairs swivel or shake, the dial swings). Frame 1 is an impossible picture.
2. **Consequence props that move and transform** carry the story: House (squash, grow), SaleBoard (slams in),
   Trolley (fills), Dial (needle). Papers, letters and boards only support them.
3. **Every era is period-checked** before a still is approved (table below). Notes stay generic and marked
   ILLUSTRATIVE: no monarch's face, no real banknote design. A planted slip is never a money or period mistake.
4. **The timeline switch** marks every what-if shot (`whatif: true`): a cooler violet-teal grade with a vignette,
   a white crack across the frame on the first what-if shot of a run, Alfie's pin glowing. Real history keeps
   the normal look, even inside a what-if episode (Ep 04: Nan's 1988 street).

Era dressing counts as a new set for the gate: write `era` inline in worldArgs, e.g. `worldArgs: { era: '1988' }`.

| Era | Fits | Never |
|---|---|---|
| 1975 (street) | pound notes, no street lights in a power cut, candles | £1 coins (from 1983), mobiles (from 1985), modern cars |
| 1988 (street) | £1 coins, brick phones, sodium-orange lamps, estate agents' boards, boxy hatchbacks | flat screens, smartphones, satellite dishes everywhere |
| 2026 | contactless, smart meters, today's prices from facts.md | anything period |
(Prop guidance, not voiced facts: check a date before a script says it.)

**Built (6 Nov):** committee room (`committee`), street eras 1975 and 1988, props Dial, House, SaleBoard, Trolley,
Tea (the milk-first slip), Phone; the timeline switch; the opening question card (`hook` on the episode); 23 camera
presets in Ep 04. **Still to build, a few per session:** a 1980s estate agent's, a Treasury office inside, a 1990s
bank branch, a pub, a North Sea rig, a factory floor, a living room with a TV (invented channel, no real logos or
presenters), a station platform, a car interior, a seaside street; hero props: ballot box, red box, ration book,
a phone through the decades. Pick topics partly for their pictures.

## 2b. Variety (checked by the gate)

- **One new set every episode**: at least one set not used in the previous two episodes (an era street, a 1988
  estate agent's, a Treasury office...). Build it before blocking the shots.
- Per episode, max: the same camera preset 6 times, newspaper shot 3, rate board 8, one set 14 shots.
- Text on props must fit: price tags 7 characters max, newspaper headlines 12 max. In the stills, every sign
  and tag must be fully readable; nothing cut off at the frame edge.

## 4. The cast (3D, built in code: src/cast/)

- **Alfie (the lead)**: the viewer's stand-in. Navy Harrington jacket with red trim, cream tee, stone chinos, white trainers,
  brown quiff. **Always wears the Union Jack pin** on the left chest.
- **Mate**: the sceptic who asks "but how?". Olive jacket, grey top, black joggers.
- **Nan**: remembers the old prices. Plum cardigan, grey bun, glasses.
- Expressions are never skipped: every key number and every turn gets a face reaction, held long enough to read.
  Faces: neutral, happy, laugh, shock, scream, worried, angry, smug, sad, disbelief, thinking, holding.
- Real people (chancellors, governors, PMs) are never shown or impersonated: "the Chancellor", generic figures,
  no invented quotes.

## 5. Voice and sound
- **Voice F (proposed 20 Nov, pending approval):** 0.4 bm_george + 0.25 bm_lewis + 0.35 bm_fable, about 15% more pitch
  movement at the same pitch. `--voice F` on tools/house_voice.py. voice.txt gets a 4th column, gain in dB, the emotion
  knob (+2..+4 shocks and the hero number, -2..-3 asides); the voice keeps a 2.8+ LU loudness range (gate: EMOTION).
- **House voice E** (voice.json, tools/house_voice.py): Kokoro, 0.6 bm_george + 0.4 bm_lewis, no pitch shift, written
  line by line in `src/episodes/<id>/voice.txt` as `speed|pause|text`. Narrator only; no cast clips.
- Word timings from the voice (tools/align.py) drive every cut, picture and sound.
- Sound effects are made by the studio (audio/); the user adds very quiet TikTok-library music when posting.
- Voice clear above everything; master to -14 LUFS.

## 6. QA before every post
- [ ] 61-80 s; gate passed with no FORCE (or the reason given to the user)
- [ ] Frame 1 is bright with Alfie big and central; the pop word lands by 1 s
- [ ] 100% original; AI-generated label on; framed as hypothetical; every real fact sourced
- [ ] History, not advice; no party politics; no real people; no brand logos
- [ ] No black, frozen or popping frames; every sign and face readable; loudness on target
- [ ] Post file: ~150-word prose description, 5-6 hashtags, pinned comment, best time (Wed/Thu 10:00, weekdays 18:00 or 12:00)

## 7. Pipeline (commands in README.md)
1. Script and facts.md (checked within 2 days) -> `python3 -I tools/gate.py <ep>`.
2. voice.txt -> `python3 -I tools/house_voice.py src/episodes/<ep>/voice.txt out/<ep>/vo.mp3` (61-80 s) -> align.py.
3. Shot list (episode.ts) -> `python3 -I tools/gate.py <ep> --vo out/<ep>/vo.mp3`.
4. Stills and contact sheets; fix; look again.
5. `tools/build.sh <id> <CompId> out/<id>/vo.mp3` (stops on any FAIL; `FORCE="reason"` only with the reason told to the user).
6. Post file `out/<id>/post.txt`, delivered with the video and the latest studio zip.
