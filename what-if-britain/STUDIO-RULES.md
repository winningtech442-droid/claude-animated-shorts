# What If Britain: studio rules (v3, 27 Nov 2026)

This is the one rule book for the format and the studio. It replaces v20 Nov 2026 (the old file gets archived when
the studio code lands in this folder). Where `claude/script-rules.md` (16 Nov), `CTA-BANK.md`, the faceless-shorts
skills or the old build guide disagree with this file, **this file wins**. `script-rules.md` is due a rewrite to match.
Change a rule on purpose, never by drift.

Why v3 exists: the v2 videos sounded like the news (a narrator explaining over pictures, the same sets every week).
v3 tells each money story as a scene: a viral "broken explainer" structure, a cast that acts, sets built for the
story, and character voices. The facts stay; they move inside the story.

## 0. Two approvals before any video is made
1. **Script.** The user reads and approves every script, written in the `SCRIPT-TEMPLATE.md` layout, facts and sources
   included. Nothing is voiced until it is approved.
2. **Test render.** A 10-20 s test clip, normally the cold open (bait, redirection, reveal), made at final quality:
   Chatterbox voices, music and effects, captions, cast and sets. The user approves it before the full episode is built.
- A change asked for at a gate goes back through that gate.
- Approvals are written to `src/episodes/<id>/approvals.txt` (date and what was approved). The build refuses to run
  without both (tool update pending, see section 10).

## 1. The episode shape (61-68 s)
| Time | Beat | What happens |
|---|---|---|
| 0 to 6-9 s | **Bait** | The narrator's confident explainer sentence: "If you [money stunt], you might think [money myth], but you might be surprised to know that-". First word on frame 1, the stunt already happening in bright daylight, an impact sound on frame 1. |
| 6-9 s | **Redirection** | The stunt physically goes wrong and cuts the narrator off mid-word. 0.5-1 s of stillness while the bed keeps playing. |
| to ~15 s | **Reveal** | The Booth (6 s at most): "Is he okay?" "That wasn't in the script." The viewer learns the explainer is a show. The bleeped swear lands here or on the redirection. |
| ~15-25 s | **Drop** | Alfie's pin fires (the timeline switch) and he wakes up in another Britain. Short, confused questions. |
| 35-55 % of the runtime | **"What if Britain...?"** | The line is said when the new world is revealed, and the WHAT IF BRITAIN title card slams in. Never in the first sentence. |
| ~25-50 s | **Active ladder** | 3-4 beats, each in a new scene with a physical task around a money object. Each beat raises the stakes and shows one fact. |
| 75-90 % of the runtime | **Twist** | A turn that changes what we thought. It carries the key fact, ideally by completing the narrator's cut-off sentence. |
| last 4-8 s | **Cliffhanger** | The loudest moment. The last line is cut mid-word, hard cut to black. No ask, no "follow for Part 2", no outro. |

## 2. The opening (finance version)
- **Why it differs from the viral original.** Borrowed openers are pure spectacle (machine guns, physics). Ours must
  also carry money words and money objects in the first seconds, so TikTok files the video under money and the
  right viewers stay. So:
  - the stunt is physical and absurd, done with an everyday money object (coins, notes, a payslip, a meter, a mortgage letter);
  - "you might think..." is a common money myth that is wrong;
  - the answer is a real, sourced fact, withheld by the redirection and paid off by the twist.
- **Opener:** one sentence, 20-30 words, spoken at 3.6-4.2 words a second, cut off mid-word between 6 and 9 s.
  Example (check the facts before use): "If you paid a whole month's rent in 1p coins, you might think your landlord
  *had* to take it, but you might be surprised to know that-" (payoff: 1p and 2p coins are only legal tender up to 20p).
- **Frame 1:** bright daylight, a familiar UK place, Alfie big and central (head at least a third of the frame width),
  already moving. Never night, a void, spotlights on black, an empty room or paperwork.
- **Hook line:** one on-screen line for the first 3 s, 4 words or fewer, with a money word ("Rent in 1p coins?").
  At most two text layers in the first 3 s: the caption and the hook line.
- **Borrowing any other viral format later:** keep its timing and its turns, swap its opener for a money stunt plus a
  money myth, turn its stakes into money stakes, and make sure the fact still lands.

## 3. Writing
- **Length:** 61-68 s (aim 62-66; TikTok Creator Rewards only pays on videos over 1 minute), about 140-190 words.
- **After the redirection, lines are short:** 6 words on average, 12 at most, and at least a third are questions.
  (Measured on the reference: 15 lines, 4.4 words on average, 6 of them questions.)
- **Nobody explains what the viewer can already see.** Facts arrive three ways: a character discovers them by doing
  something, a prop shows them for at least 1.5 s (price board, letter, scale, receipt), or the twist reveals them.
- **Facts:** 2-4 real facts per episode, each in `facts.md` with a source checked within 2 days. The opener's fact is
  completed before the end. Framed as hypothetical; history and explainer, never advice.
- **Characters always do something:** carry, chase, queue, haggle, hide, fix, escape. No standing and talking.
- The narrator never repeats a line. A character may repeat one on purpose (twice at most).
  No line copied from the last two episodes.
- **Swearing:** one at most per episode, bleeped, inside the first 15 s (on the redirection or in the reveal).
  Mild or moderate words only; never slurs or sexual terms. Captions show the word starred (s***).
- **No weapons or violence.** The stakes are money: eviction, bailiffs, a declined card, a run on the bank, a debt.
- **No real people** (chancellors, governors, PMs: "the Chancellor", generic figures, no invented quotes),
  no brand names or logos, no party politics.
- **Lore:** never contradict `LORE.md`. Every episode stands alone (a new viewer follows it without the lore), and
  each cliffhanger adds or advances one thread.

## 4. The cast (3D, built in code: src/cast/)
- **Alfie (the lead, the viewer's stand-in):** average build. Navy Harrington jacket with red trim, cream tee, stone
  chinos, white trainers, brown quiff. Always wears the Union Jack pin on the left chest; **the pin is the timeline switch**.
- **Mate (the sceptic who asks "but how?"):** now **heavy-set**: big round belly, broad shoulders, smallish head.
  Olive jacket, grey top, black joggers. The physical-comedy foil.
- **Nan (remembers the old prices):** now **tiny and stooped**, big glasses, a walking stick (a prop for gags),
  plum cardigan, grey bun.
- **The Booth (recurring):** the Narrator (the house voice; heard, seen at most from behind at the mic) and the
  Producer (seen; headset, clipboard). Names get fixed in the pilot and logged in `LORE.md`.
- **Guests:** new for each episode, built for its story from the body system and pushed about 1.5x
  (the bloated landlord, the beanpole bank manager, the sweaty bailiff, the tiny inspector...).
- **Body system** (being built): builds slim, average, heavy, bloated belly on thin legs, tall and lanky, tiny,
  elderly stoop; features jowls, double chin, bald or comb-over, big nose, wrinkles, sweat. Every guest is a new silhouette.
- **Acting:** faces neutral, happy, laugh, shock, scream, worried, angry, smug, sad, disbelief, thinking, holding.
  Body poses to add: run, carry, push, fall, crawl, stuck, wobble, slump, double take, faint. Every line gets a body
  action as well as a face; every key number and every turn gets a reaction, held long enough to read.
- Real people are never shown or impersonated.

## 5. Scenes
- **3-5 locations per episode, built for that story.** A location is used in one episode, then retired.
  The only set that repeats is the Booth (6 s at most per episode).
- **Relatable UK places:** chippy, launderette, corner shop, Post Office queue, bus, council-flat kitchen, pub, car boot
  sale, allotment, school gate, rainy high street, station platform, seaside front. Invented names and signs only.
- **Built fast from a kit of parts** (walls, windows, counters, shelves, signs, street furniture, lighting presets),
  plus at least one hero prop made for the story. The parts repeat; the places never do.
- **Real objects only** (payslip, pint, meter, house, jar, price board); no abstract blocks, barriers or capsules.
- **Grade:** warm daylight with the navy / red / cream brand colours, soft rim light, contact shadows, no neon cyan.
  After the redirection the story may go dark (a blackout, night) if it needs to, never on frame 1.
- **The timeline switch look** on what-if shots: a cooler violet-teal grade with a vignette, a white crack across the
  frame on the first what-if shot, Alfie's pin glowing. Real history keeps the normal look.
- **Period scenes are era-checked** before a still is approved. Notes stay generic and marked ILLUSTRATIVE
  (no monarch's face, no real banknote design).

| Era | Fits | Never |
|---|---|---|
| 1975 | pound notes, no street lights in a power cut, candles | £1 coins (from 1983), mobiles (from 1985), modern cars |
| 1988 | £1 coins, brick phones, sodium-orange lamps, estate agents' boards, boxy hatchbacks | flat screens, smartphones, satellite dishes everywhere |
| 2026 | contactless, smart meters, today's prices from facts.md | anything period |
(Prop guidance, not voiced facts: check a date before a script says it.)

## 6. Picture and editing
- **A cut or new angle every ~2 s** (25-35 shots), one slow move inside each shot, a push-in on every reaction.
  The redirection holds still for 0.5-1 s.
- **Motion with weight:** ease in and out, anticipation, overshoot and settle; an impact sound when a thing lands.
- **WHAT IF BRITAIN title card** slams in mid-video with an impact.
- **Captions on every video:** bold, word by word, black outline, lower third, coloured by speaker (narrator white,
  each character their own colour, off-screen voices in italics); one red pop word per beat; a bleeped word shows starred.
- Signs and tags short and fully readable (tags 7 characters, headlines 12), nothing cut off at the frame edge.
  At most one label per beat.
- **The ending:** the last line is cut mid-word, then a hard cut to black (the only black frames allowed).
- **30 fps, no motion blur** (`MB=0`). A shot whose point is a sign or number holds or drifts once the text is in frame.

## 7. Voices (Chatterbox)
- **Narrator plus a fixed voice for every character.** Each character has a reference clip `voices/<name>.wav`
  (10-15 s), made once and approved by the user. The narrator's comes from the house voice (Kokoro, voice E in
  `voice.json`; voice F still pending). Chatterbox copies the reference voice and performs each line with feeling.
- **voice.txt:** one line per row, `speaker|exaggeration|cfg|pause|text`.
  - exaggeration: 0.4-0.5 calm, 0.6-0.8 lively, 0.9-1.3 panic or shouting;
  - cfg: about 0.5 normally, about 0.3 for dramatic lines (keeps excited lines from rushing).
- Off-screen voices (the Booth, phones, tannoys) get a talkback filter.
- Any line that drifts out of a British accent, slurs or clips is regenerated.
- The narrator's opener may stay on plain Kokoro (the polished explainer that gets interrupted); decide at the first test render.
- Kokoro alone is the fallback only, and the user is told when it is used.
- **Approved cast voices (27 Nov 2026)**, reference clips in `voices/`, settings in `voices/cast.json`:

| Character | Built from (Kokoro) | Feel |
|---|---|---|
| Narrator | 0.6 bm_george + 0.4 bm_lewis (house voice E) | the polished explainer |
| Alfie | bm_fable, speed 1.05 | younger, slightly quick |
| Mate | 0.7 bm_daniel + 0.3 bm_lewis, speed 0.92, pitch -1.5 | deeper, slower |
| Nan | bf_alice, speed 0.86, pitch -1 | older, slower |
| Producer | bf_emma, speed 1.1 | quick, easily panicked |
- A new guest gets a new reference clip, approved by the user before its lines are voiced.

## 8. Sound
- The studio makes the sound (`audio/`): effects placed on what happens on screen (`ep_sfx.py` for hand-built episodes)
  and an original score where it helps; no stock or shared music beds. The user may add very quiet TikTok-library
  music when posting.
- **A bed under everything:** no dead silence until the final cut.
- An effect on every beat change and every on-screen action; a hit on the redirection and on the title card;
  a dropout before the twist; the loudest peak on the cliffhanger.
- **Bleep:** a tone exactly over the swear word, at voice level.
- **Master:** -14 LUFS integrated (plus or minus 1), true peak -1 dBTP or lower, **loudness range 5-7 LU**
  (the reference measures 5.8); the voice clear above everything.

## 9. QA before every post
- [ ] Script approved and 10-20 s test render approved (`approvals.txt`)
- [ ] 61-68 s; gate passed with no FORCE (or the reason given to the user)
- [ ] Frame 1 bright, Alfie big and central, first word on frame 1, hook line with a money word
- [ ] Redirection by 9 s; "What if Britain" at 35-55 %; the twist carries the key fact; last line cut mid-word
- [ ] Swear (if any) bleeped and inside the first 15 s
- [ ] 100 % original; AI-generated label on; framed as hypothetical; every real fact sourced
- [ ] History, not advice; no party politics, real people, brand logos or weapons
- [ ] No frozen or popping frames, no black frames except the final cut; every sign and face readable; loudness on target
- [ ] Post file: ~150-word prose description, 5-6 hashtags, pinned comment (the cliffhanger question),
      best time (Wed/Thu 10:00, weekdays 18:00 or 12:00)
- Judge every post at 24 h by the share still watching at 3 s (aim 65 %+), then average watch time (aim 40 %+).

## 10. Pipeline (v3) and tool status
1. Topic and `facts.md` (checked within 2 days), script in the `SCRIPT-TEMPLATE.md` layout, gate, **the user approves the script**.
2. Reference clips for any new character, then `voice.txt`, Chatterbox voices, word timings (`tools/align.py`).
3. Build the episode's scenes and guests, then the shot list (`episode.ts`), stills and contact sheets.
4. **10-20 s test render** of the cold open, **the user approves it**.
5. Full build, QA, post file; deliver the video and the post file.

**Tool status (27 Nov 2026):** v3 episodes are hand-built in `src/ep/<id>/` on the v3 kit (`src/ep/kit3.tsx`:
actors with whole-body stunts, shots, the timeline switch, speaker-coloured captions with starred bleeps, lip flap,
the mid-video title card, fact cards, the final cut to black) with `audio/<id>_sound.py`. Voices: `tools/cast_voice.py`
(Chatterbox, several speakers, per-line timings) and `tools/make_voice.py` (guest auditions). `qa.py` checks v3
(61-68 s, the final black allowed). EP21 is the worked example. Still v2: `gate.py` (needs v3 checks), `build.sh`
(should refuse without `approvals.txt`) and the data-driven engine (`src/engine/`, Eps 01-08).

## 11. What v3 removed from v20 Nov
- The Today / Then / What if / Your wallet / Ask format, and "the what-if heard by 4.5 s" (gate FIRSTWORDS).
- The locked set library (6 Nov), set rotation and "one location per episode".
- "Narrator only, no cast clips", and the 2.8 LU voice range.
- The spoken ask in the last 5 s: `CTA-BANK.md` no longer applies to the video. Its asks move to the post description
  and pinned comment, and its no-bait rules still apply there. The gate's share/follow checks go.
- 160-200 words at 2.9-3.2 words a second, and "no line said twice" for characters.
