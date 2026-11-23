# Phoneverse FIX #17: Your phone is made of sand (the glowing crystal inside your iPhone's brain): studio package

**Treasure/curiosity series, episode 2** (after #16, "Gold in your iPhone"). HSERIA + CTA, second person, rule book v8 (format A), **3 character beats**.
Status: **script drafted 23 Nov 2026, waiting for user approval. Nothing is voiced or rendered yet.**
Script: **20 lines, 188 words.** At 3.0 words/s that is 62.7 s of speech. #16 measured 185 words / 20 lines = 69.0 s with the same presets
and pauses, so expect **about 69-70 s** for the take. If take 1 comes in over 70 s, cut words from lines 11 and 17 first, not from the fact lines.

## Why this topic
- **Series continuity:** #16 tested the "treasure inside your phone" format (based on another creator's 700k-view 3D short; only the format and
  pacing are borrowed). #17 keeps the same fantasy shape: an ugly start, a slow process shown from inside, then a glowing treasure at the peak
  (a gold bar in #16, a giant glowing crystal and mirror wafers here). Same set, so it is cheap to build.
- **Demand:** "how it's made" and "from sand to chip" pieces do well across shorts in general. The phone angle ("your phone's brain") keeps it in
  our niche. The iPhone 18 Pro's A20 Pro is Apple's first 2 nm chip (TSMC N2, launched Sept 2026), so chips are in the news this autumn.
- **Supply gap:** most sand-to-chip videos are long factory explainers or narrated stock footage. A 60-70 s, one-world 3D version in plain
  words, with a twist ("it's not beach sand"), is thin on the ground. Not checked with vidIQ this session; this is a judgement call, so log it as such.
- **Comment drivers:** the planted slips (below), the honest "not beach sand" twist, and an easy yes/no question at the end.
- Backlog after this one: sapphire camera cover, screen glass cooked in molten salt, Apple's recycling robot, lithium from turquoise lakes, magnets.

## Script decisions
- **Voice:** plain, everyday words; repetition on purpose ("Sand. Inside your phone.", "way, way too dirty", "clean it, clean it, and clean it
  again", "slowly, slowly", "Thinking for you" in lines 2 and 18 as a bookend). **No chemical names or process names** in the voice. "Nine nines"
  is the one technical-sounding phrase, and it is the payoff.
- **Hook burned in on frame 1:** "YOUR PHONE IS MADE OF SAND".
- **Honest twist (line 17):** the hook says sand, the twist admits chip silicon comes from lumps of pure quartz rock, not beach sand. This is a
  real correction, not a slip, so it must stay accurate. Line 18 lifts it straight back up ("Rock or sand, mostly the same stuff": most sand is
  mostly quartz).
- **Fantasy kept:** the peak is line 13 (AWE preset): the crystal rises out of the glowing melt. Lines 14-16 keep it going (piano-heavy, sliced
  like cheese, polished to a mirror) before the twist.
- **Safety:** line 3 ("Giant factories do this. Never at home.") goes on while the melt and furnace are on screen. The DON'T-TRY card stamps on with it.
- **Action line (19)** is Apple's own advice, word for word in meaning (see Facts).

## Planted slips (on purpose: do NOT "fix" these)
| Line | Slip | Why it's harmless |
|---|---|---|
| 4 | "Only three steps. I said that last time." | There are more than three (furnace, cleaning, melt, pull, slice, polish, print). A running gag from #16's "three simple steps", so returning viewers catch it. |
| 11 | "Spin it one way, the pot the other. Or the other way. Whatever." | The crystal and the pot turn in **opposite** directions, so either way round is true. The self-correction is only a shrug. |

## Must be exactly accurate (never slip these)
Line 3 (safety), 5 (cooked with coal, grey metal), 8 (four nines vs nine-to-eleven nines), 9 (hotter than lava), 12 (about two days),
13-14 (tall as you, heavy as a piano, single crystal), 15 (thin as a bank card), 16 (hundreds per wafer), 17 (quartz rock, not beach sand),
19 (case off if hot while charging).

## Characters (Phoneverse Character Sheet)
Lead **You** (Rocketbox Female_Adult_01), 3 beats (rule book v8: 2-3).
| Clip | Line | Face | Pose | Action |
|---|---|---|---|---|
| c01_hold | 1 | smug | hold | Holds the Burgundy hand-prop phone (same as #16 c01) up to camera; sand trickles out of the other fist. |
| c02_delight | 13 | delight | cheer | Looks up as the glowing crystal rises past head height. |
| c03_shrug | 17 | smug | shrug | "Honest part?" Holds a lump of white quartz instead of sand. |

## Set: same yard workbench as #16 (render/world.py, PROPS "gold"), re-dressed for silicon
Keep the one-world bench in the sunny recycling yard; swap the phone mountain backdrop for a **heap of white quartz lumps** with a small sand pile beside it.

**Reuse from #16 (gold props):**
- **crucible on its brick + torch + molten glow** → the melt. Re-tint PV_MOLT from orange-gold to a **white-orange** (molten silicon glows brighter
  and paler than gold); keep the AgX lesson from #16 (dark base, saturated emission) so it doesn't go pastel.
- **"heat" / "torch" tracks** → line 9. **"fill"/"lift" bar logic** → reuse the lift track to raise the crystal out of the crucible (line 13).
- **tub with colour states** → line 7 cleaning: grey lumps → murky → clear (3 rinse pulses, reuse "rinse").
- **mould** → becomes the saw bed for line 15. **drawer** → not used.
- hero phone + lid lift + board cutaway → line 1-2 and the end (the A-chip lights up, "Still thinking for you").

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
| 13-14 | R1 | c02: the giant glowing crystal rises past head height. Slow orbit; it cools to silver. | label `one crystal` |
| 15-16 | R1 | Wire saw slices it; wafers fall like cheese slices beside a bank card for thickness. Polish: one wafer turns into a mirror reflecting the yard; chip grid prints across it. | labels `bank card`, `hundreds of chips` |
| 17 | I | c03 shrug with a lump of quartz. Split screen: beach sand (dull, mixed colours) vs white quartz rock. | label `not beach sand` |
| 18 | R2 | Pull back from the wafer into the phone; the main chip glows. | |
| 19-20 | A/CTA | The phone on a charger, warm red tint; the case slides off. Match cut back to the frame-1 sand pour for the loop. | label `case off` |

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
- data/lines.json (20 lines, #16 presets unchanged incl. AWE, blocks, starred caption words, character clips), script.txt (lines only), post.txt.
- Not built yet: tools/ (copy make_voice.py, build_captions.py, qc.py from ../phoneverse_fix16_studio/tools when voicing; make_sound.py needs a
  new #17 cue sheet: sand hiss, furnace roar, rinse ×3, counter ticks, deep melt hum, crystal shimmer, saw whine, wafer clinks, mirror ting, case slide),
  data/timings.json, captions.json, ../phoneverse_3d_studio/data/make_beats_fix17.py, the new world.py props and the char_scene.py clips.

## Next steps
1. **User approves the script** (or asks for changes).
2. Voice take 1 with #16's make_voice.py (Kokoro af_heart, the same presets). Target 60-70 s; lock timings.json, then never re-time.
3. Captions (one yellow word per line, first match only), beat sheet make_beats_fix17.py, silicon props in world.py (a new PROPS "silicon"
   reusing the gold crucible, torch, tub and lift code), `--test` stills checked at phone size.
4. Character clips c01-c03, sound, full render, QC (-14 LUFS, 1080×1920), phone-size sheet, post.
