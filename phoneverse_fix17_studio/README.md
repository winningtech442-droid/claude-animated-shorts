# Phoneverse FIX #17: Your phone is made of sand (the glowing crystal inside your iPhone's brain): studio package

**Treasure/curiosity series, episode 2** (after #16, "Gold in your iPhone"). HSERIA + mid-CTA (follow) + CTA, second person, rule book v8 (format A), **3 character beats**.
Status: **script approved 23 Nov 2026. Voice take 1 recorded: 70.64 s, 191 words, speech pace 3.05 words/s, tail 0.32 s.**
Take 1 is 0.64 s over the 70 s limit (every other make_voice limit passes). **User accepted it as is, 23 Nov: LOCKED.**
Never re-time data/timings.json after this. Captions: 109 cards, one yellow word per line (data/captions.json). Follow line: 36.4-39.5 s.
Fast lines to check by ear: 1 (3.81 wps), 6 (3.64), 7 (3.79), 11 (3.83). Slowest: 8 (2.49, EMPH, the purity payoff), 14 (2.56, AWE peak).
Script: **21 lines, 192 words** (incl. the mid-video follow ask, line 13). At 3.0 words/s that is 64.0 s of speech. #16 measured 185 words /
20 lines = 69.0 s with the same presets and pauses, so expect **about 72 s** for the take (a touch over the 70 s target). If take 1 comes in over 70 s, cut words from lines 2
and 19 first, never from the fact lines, the slips or line 13.

## Why this topic
- **Series continuity:** #16 tested the "treasure inside your phone" format (based on another creator's 700k-view 3D short; only the format and
  pacing are borrowed). #17 keeps the same fantasy shape: an ugly start, a slow process shown from inside, then a glowing treasure at the peak
  (a gold bar in #16, a giant glowing crystal and mirror wafers here). Same set, so it is cheap to build.
- **Demand:** "how it's made" and "from sand to chip" pieces do well across shorts in general. The phone angle ("your phone's brain") keeps it in
  our niche. The iPhone 18 Pro's A20 Pro is Apple's first 2 nm chip (TSMC N2, launched Sept 2026), so chips are in the news this autumn.
- **Supply gap:** most sand-to-chip videos are long factory explainers or narrated stock footage. A 60-70 s, one-world 3D version in plain
  words, with a twist ("it's not beach sand"), is thin on the ground. Not checked with vidIQ this session; this is a judgement call, so log it as such.
- **Comment drivers:** the planted slips (below), the honest "not beach sand" twist, and an easy yes/no question at the end.
- **Follow driver:** a mid-video follow ask (line 13), placed on the cliffhanger just before the crystal comes out.
- Backlog after this one: sapphire camera cover, screen glass cooked in molten salt, Apple's recycling robot, lithium from turquoise lakes, magnets.

## Script decisions
- **Voice:** plain, everyday words; repetition on purpose ("Sand. Inside your phone.", "way, way too dirty", "clean it, clean it, clean it
  again", "slowly, slowly", "Thinking for you" in lines 2 and 19 as a bookend). **No chemical names or process names** in the voice. "Nine nines"
  is the one technical-sounding phrase, and it is the payoff.
- **Hook burned in on frame 1:** "YOUR PHONE IS MADE OF SAND".
- **Mid-video CTA (line 13, block MCTA, PUNCH):** "Now, press the Follow button to keep watching our videos!" (the user's wording, 23 Nov:
  the first draft, "Follow. What comes out is huge.", sounded flat). Goes right after "About two days" and before the reveal,
  so the follow ask rides on the suspense and the payoff comes straight after (no drop in retention). On screen: the melt glows, the crystal is still
  hidden under the glare, and a follow-button sticker pops up and gets a tap. 
  The end CTA stays the comment question; the post copy doesn't ask for a follow again.
- **Honest twist (line 18):** the hook says sand, the twist admits chip silicon comes from lumps of pure quartz rock, not beach sand. This is a
  real correction, not a slip, so it must stay accurate. Line 19 lifts it straight back up ("Rock or sand, mostly the same stuff": most sand is
  mostly quartz).
- **Fantasy kept:** the peak is line 14 (AWE preset): the crystal rises out of the glowing melt. Lines 15-17 keep it going (piano-heavy, sliced
  like cheese, polished to a mirror) before the twist.
- **Safety:** line 3 ("Giant factories do this. Never at home.") goes on while the melt and furnace are on screen. The DON'T-TRY card stamps on with it.
- **Action line (20)** is Apple's own advice, word for word in meaning (see Facts).

## Planted slips (on purpose: do NOT "fix" these)
| Line | Slip | Why it's harmless |
|---|---|---|
| 4 | "Only three steps. I said that last time." | There are more than three (furnace, cleaning, melt, pull, slice, polish, print). A running gag from #16's "three simple steps", so returning viewers catch it. |
| 11 | "Spin it one way, the pot the other. Or the other way. Whatever." | The crystal and the pot turn in **opposite** directions, so either way round is true. The self-correction is only a shrug. |

## Must be exactly accurate (never slip these)
Line 3 (safety), 5 (cooked with coal, grey metal), 8 (four nines vs nine-to-eleven nines), 9 (hotter than lava), 12 (about two days),
14-15 (tall as you, heavy as a piano, single crystal), 16 (thin as a bank card), 17 (hundreds per wafer), 18 (quartz rock,
not beach sand), 20 (case off if hot while charging).

## Characters (Phoneverse Character Sheet)
Lead **You** (Rocketbox Female_Adult_01), 3 beats (rule book v8: 2-3).
| Clip | Line | Face | Pose | Action |
|---|---|---|---|---|
| c01_hold | 1 | smug | hold | Holds the Burgundy hand-prop phone (same as #16 c01) up to camera; sand trickles out of the other fist. |
| c02_delight | 14 | delight | cheer | Looks up as the glowing crystal rises past head height. |
| c03_shrug | 18 | smug | shrug | "Honest part?" Holds a lump of white quartz instead of sand. |

## Set: same yard workbench as #16 (render/world.py, PROPS "gold"), re-dressed for silicon
Keep the one-world bench in the sunny recycling yard; swap the phone mountain backdrop for a **heap of white quartz lumps** with a small sand pile beside it.

**Reuse from #16 (gold props):**
- **crucible on its brick + torch + molten glow** → the melt. Re-tint PV_MOLT from orange-gold to a **white-orange** (molten silicon glows brighter
  and paler than gold); keep the AgX lesson from #16 (dark base, saturated emission) so it doesn't go pastel.
- **"heat" / "torch" tracks** → line 9. **"fill"/"lift" bar logic** → reuse the lift track to raise the crystal out of the crucible (line 14).
- **tub with colour states** → line 7 cleaning: grey lumps → murky → clear (3 rinse pulses, reuse "rinse").
- **mould** → becomes the saw bed for line 16. **drawer** → not used.
- hero phone + lid lift + board cutaway → lines 1-2 and the end (the A-chip lights up, "Still thinking for you").

**New props:**
- quartz lumps (white, translucent, sub-surface) and a sand pile; small arc-furnace pot (can be the crucible scaled up, dark grey) with grey metal chunks.
- **seed rod** on a thin cable; **ingot**: grey-silver cylinder with a cone top and tail, glowing orange at the bottom end where it leaves the melt,
  rotation visible (a faint spiral line on the surface). Spin it one way and the crucible the other.
- **wire saw**: a row of thin glowing wires; wafers drop off like slices.
- **wafer**: mirror disc (metal 1.0, rough 0.02) reflecting the yard; then a grid of hundreds of tiny rainbow chip squares.
- HUD: `hud.count` purity 99.99 → 99.999999999 %, temperature 1,414 °C, pull timer 0 → 44 h.

## Beat outline (time it from the measured take; never re-time)
| Lines | Block | What happens on screen | HUD / labels |
|---|---|---|---|
| 1-2 | H | c01: You holds the phone, sand pours from the other fist. Push in through the screen; X-ray to the main chip, which grains of sand fly into. | hook burned in |
| 3-6 | S | DON'T-TRY card stamps on. Quartz lumps tip into the furnace pot with coal; sparks; grey metal chunks come out. Macro: dark specks in the metal. | label `silicon metal`, `dirt` |
| 7-8 | E | Tub: three rinse pulses, murky to crystal clear. Purity counter races 99.99 → 99.999999999. A gold bar slides in beside it for "four nines". | `hud` 99.99 % (gold) vs 99.999999999 % |
| 9-12 | E | Crucible glows white-orange under the torch. A tiny seed dips in; camera from inside the melt as the crystal starts to grow. Crystal and pot spin opposite ways. A snail crawls past the crucible (faster than the crystal). | `hud` 1,414 °C; timer 0 → 44 h; labels `seed`, `spin` |
| 13 | MCTA | The melt glares white so the crystal stays hidden; the camera holds on the rising cable. A follow-button sticker pops in, You's hand-prop phone taps it, it flips to a tick. | sticker `FOLLOW` |
| 14-15 | R1 | c02: the giant glowing crystal rises past head height. Slow orbit; it cools to silver. | label `one crystal` |
| 16-17 | R1 | Wire saw slices it; wafers fall like cheese slices beside a bank card for thickness. Polish: one wafer turns into a mirror reflecting the yard; chip grid prints across it. | labels `bank card`, `hundreds of chips` |
| 18 | I | c03 shrug with a lump of quartz. Split screen: beach sand (dull, mixed colours) vs white quartz rock. | label `not beach sand` |
| 19 | R2 | Pull back from the wafer into the phone; the main chip glows. | |
| 20-21 | A/CTA | The phone on a charger, warm red tint; the case slides off. Match cut back to the frame-1 sand pour for the loop. | label `case off` |

## Facts (checked 23 Nov 2026)
- **Quartz → silicon metal:** quartz is reduced with carbon (coal, coke, wood chips) in an electric arc furnace at about 1,500-2,000 °C; the
  result is about 98-99% pure silicon metal, shiny grey. PVEducation "Refining silicon"; universitywafer.com "Metallurgical grade silicon";
  SciELO SA (Ali 2018, Egyptian quartz to MG-Si). Line 5 says "cooked with coal": coal/coke is a real reducing agent; "cooked" is the plain-word version.
- **Not beach sand:** smelting uses lumps of high-purity quartz or quartzite, not beach sand (too fine, too many impurities). The purest natural
  quartz (Spruce Pine, North Carolina) is mainly used for the quartz crucibles that hold molten silicon. Wired, "The ultra-pure, super-secret sand
  that makes your phone possible"; Ed Conway, "What's happening at Spruce Pine". That's why line 17 says "pure quartz rock" and "**most** sand's too
  dirty", and makes **no** claim about which town the quartz comes from.
- **Purity:** electronic-grade polysilicon is 9N (99.9999999%) to 11N (99.999999999%): ICIS polysilicon methodology (2013); Tokuyama 11N spec
  (semirai.com); ScienceDirect topic "Purity polysilicon". A fine gold bar is 999.9 = **four nines** (LBMA good delivery is 995 minimum; 999.9 is
  the usual "four nines" fine gold bar, as on #16's bar stamp).
- **Melt:** silicon melts at 1,414 °C (Royal Society of Chemistry via jrsttechnology.com); CZ melts run about 1,420 °C (semiconductorx.com).
  Most lava erupts at about 700-1,200 °C, so "hotter than lava" holds.
- **Czochralski pull:** a seed crystal is dipped into the melt in a quartz crucible, then slowly pulled up while seed and crucible **rotate in
  opposite directions**; about 0.6 mm a minute for a 300 mm crystal, about 44 hours of growth in a run of about three days (semiconductorx.com
  "Crystal growing"; averroes.ai "Czochralski process": "more than a day"). Line 12 says "about two days" (44 h). A snail moves about 1 mm a
  **second**, so the crystal really is far slower than a snail.
- **Ingot size:** a 300 mm ingot body runs about 1.5-2 m and weighs about 264 kg in a worked example; WaferPro says "over 300 kilograms"
  (semiconductorx.com; waferpro.com). "Tall as you" (an adult, about 1.7 m) and "heavy as a piano" (an upright piano is about 200-300 kg) are
  hedged plain-word comparisons. It is one single crystal all the way through: this is the whole point of the method.
- **Slicing / thickness:** diamond wire saws slice the ingot; 300 mm wafers are about 775 µm (0.775 mm) thick (siliconmasters.co; scribd
  fab guide). A bank card is 0.76 mm (ISO/IEC 7810 ID-1), so "thin as a bank card" is within about 2%. Wafers are then polished to a mirror finish.
- **Chips per wafer:** the A18 Pro die is about 105 mm² (Reddit summary of TechInsights/Chipwise; SemiAnalysis ~104 mm²). Gross die per 300 mm wafer
  = π·150²/105 − π·300/√(2·105) ≈ 673 − 65 ≈ **600** (anysilicon.com die-per-wafer formula). The A20 Pro's die size isn't public yet, so the
  line says "**hundreds**", not a number.
- **Your iPhone's chip is made this way:** the A19/A19 Pro (iPhone 17) are made by TSMC on N3P (Wikipedia "Apple A19"); the A20 Pro (iPhone 18
  Pro) is TSMC N2, Apple's first 2 nm iPhone chip (TechInsights; MacRumors 9 Sept 2026). TSMC is **not** named in the voice or post.
- **Line 19:** Apple, "Batteries – Maximizing performance": "Charging your device when it's inside certain styles of cases may generate excess
  heat, which can affect battery capacity. If you notice that your device gets hot when you charge it, take it out of its case first."

## Files
- data/lines.json (21 lines, #16 presets unchanged incl. AWE, blocks, starred caption words, character clips), script.txt (lines only), post.txt.
- Not built yet: tools/ (copy make_voice.py, build_captions.py, qc.py from ../phoneverse_fix16_studio/tools when voicing; make_sound.py needs a
  new #17 cue sheet: sand hiss, furnace roar, rinse ×3, counter ticks, deep melt hum, crystal shimmer, saw whine, wafer clinks, mirror ting, case slide),
  data/timings.json, captions.json, ../phoneverse_3d_studio/data/make_beats_fix17.py, the new world.py props and the char_scene.py clips.

## Build status (23 Nov 2026)
- Beat sheet: ../phoneverse_3d_studio/data/make_beats_fix17.py -> beats_fix17.json (45 beats, longest 2.33 s, 3 character stand-ins), chars_fix17.json.
- world.py: new PROPS "silicon" (builds on "gold"): quartz heap, arc furnace + electrodes, metal chunks with dirt specks, murky-to-clear rinse ("murk"),
  silver crystal grown/spun/lifted from the crucible, snail, saw bed + slices + bank card, mirror wafer with a chip grid, beach sand vs quartz lump,
  phone case + charger. Line 13 (follow) shows pvui.follow_card() on the phone ("Winning.tech" profile, Follow -> Following); the crystal stays off screen.
- Sound: tools/make_sound.py (#17 cue sheet) -> audio/mix_with_pad.wav, -14.1 LUFS, TP -2.6 dB after AAC.
  Remixed 23 Nov after the user said the object sounds drowned the narrator. FX were unscaled, peaking up to 13 dB over the voice.
  They now sit about 18 dB under it during speech (ducked) and about 14 dB under it in the gaps; no frames were re-rendered. LRA is now 2.0 (advisory; see BUILD_BRIEF).
- Full render DONE (1,695 frames; run in chunks of about 550 frames, because a background job stops at 2 h): `build_fix17.sh render A B`, then `finish`.
- Final (gitignored, one output only): ../phoneverse_3d_studio/final/phoneverse_fix17_mix_with_pad.mp4. Phone-size sheet: ../phoneverse_3d_studio/docs/phone_size_check_fix17.png.
- QC (after the remix): 1080×1920/24, −14.1 LUFS, TP −2.6 dB, LRA 2.0 (narrator-forward, accepted), pace 3.05 w/s, tail 0.30 s, 0 black/frozen. Two FAILs, both accepted:
  - Length 70.62 s: the locked take, accepted by the user.
  - "Longest shot 5.04 s": the scene detector misses soft cuts between similar-coloured shots (47–61 s). Frame-difference peaks fall on all 44 planned cuts, and a before/after sheet confirms each one by eye. The real longest shot is 2.33 s.
- Fix after review: the HUD chip at 45.5 s ("ONE PERFECT CRYSTAL / ALL THE WAY THROUGH") ran off both edges of the frame. It now reads "ONE CRYSTAL / NO FLAWS"; frames 1090–1130 were recomposed and the finals reassembled.

## Next steps
1. ~~Script approved~~, ~~voice take 1 locked (70.64 s)~~, ~~captions built~~.
2. ~~Beat sheet, silicon props, test stills~~, ~~full render, QC, phone-size sheet~~.
3. Post after #16 (Fri 27 Nov), once #16's 3 s hold and comments are in; copy in post.txt.
4. Later: real character clips c01–c03 (needs a "yard" set in char_scene.py) to replace the desk stand-ins.
