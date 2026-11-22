# Phoneverse FIX #16: Gold in your iPhone (every upgrade, you throw away real gold): studio package

**Format test** (a treasure/curiosity video, not a threat story). HSERIA + CTA, second person, rule book v8 (format A), with **4 character beats**.
Status: **script locked for a voice take, nothing rendered.** Draft 22 Nov 2026.
20 lines, 198 words. At FIX #15's pace (0.36 s a word including pauses) that comes to about **71 s**: measure the take. If it runs over 70 s, cut line 4 first, then shorten line 19.
Post: Fri 27 Nov (Black Friday), 19:20 UK. **Log this as the one change** for this post: the format, not a threat story.

## Why this topic (daily intel, 22 Nov 2026)
- Source format: another creator's 3D short, "gold from a TV remote" (700k views, 50k likes, 18.4k saves, 6.1k shares, 600 comments).
  Only the format and pacing are borrowed. The structure, every line, the set and every asset are ours. Nothing from the source appears
  in the video, including its green "W" watermark.
- Its weakness was comments (0.09% of views): nothing to argue about. Our answers are the £3 twist and the closing drawer question.
- Timing: Black Friday is 27 Nov, which is upgrade week, when old phones go into drawers.
- Our TikTok numbers, last 30 days: 3 of 22 posts held 50%+ at 3 s (#14 Duo 53%, used Pro 52%, shoulder surfing 56%). The volume rule
  (one post a day until three in a row hold 50%+) is not met.
- vidIQ had no credits, so the outlier and competitor checks were skipped.

## Script decisions
- **Voice:** plain, common-man words, repetition on purpose ("Real gold…", "very, very", "wash it, rinse it, wash it again", "once the
  bubbling stops" said twice). **No chemical names**, so it can't be followed as a how-to.
- **Planted slips (harmless only):** "three simple steps" (there are more); "gold sand, gold dust, whatever". These are there to draw comments.
- **Must be exactly accurate, never slipped:** line 3 (don't try this), line 6 (battery fire), line 19 (erase before you sell or recycle).
- **Hook burned in on frame 1 (beat sheet `hook`):** "YOU'RE BINNING REAL GOLD".
- **Fantasy kept:** the bar is the peak (line 15). The £3 twist (16-17) dips, and line 18 lifts it straight back up.

## Characters (Phoneverse Character Sheet)
On 21 Nov the user noted that the two best-performing Phoneverse videos have characters acting. This episode uses the lead, **You**
(Rocketbox Female_Adult_01), in 4 short beats. Rule book v8 says 2-3; this is one over, on purpose.
| Clip | Line | Face | Pose | Action |
|---|---|---|---|---|
| c01_toss | 1 | smug | hold | Holds the **new** phone (Burgundy, iPhone 18 Pro Max lookalike) in one hand and tosses an **old generic phone** onto the pile with the other. |
| c02_recoil | 6 | shock | recoil | Flinches back as the battery puffs up and flashes. |
| c03_delight | 15 | delight | cheer | The gold bar rises out of the mould. |
| c04_shrug | 16 | smug | shrug | "Honest part?" Three pounds. |

## Set: format A world, dressed as a sunny recycling yard
Keep the one-world desk (render/world.py) and re-dress it as a **workbench in a sunny recycling yard**. A big open roller door behind it shows
a **mountain of old phones** in daylight. This keeps format A (one world, the object is the star, the mechanism shown from inside) without
building a new world, and "recycling plant, not your kitchen" supports the safety framing.

**Reuse:** hero phone, the lid lift and circuit-board cutaway (the "where's the gold" beat), `hud.count`, pinned labels, camera moves.
**New props for world.py:**
- old generic phone (brandless; older notch-style shape, two-lens diagonal camera)
- phone pile and backdrop
- liquid tub with colour states: clear → blue → black mud → sparkle flecks → yellow → brown dust settling
- rinse hose (3 splashes)
- battery puff-and-flash cutaway (red tint)
- crucible and torch flame
- ingot mould and a **polished unbranded 1 kg bar** (stamp "FINE GOLD 999.9 · 1 kg", real reflections)
- drawer full of old phones
- plain white "Hello" erase screen (pvui, not Apple's typeface)

**New phone (hand prop in c01 only):** 163.4 × 78 × 8.75 mm, aluminium unibody, full-width camera bar (three lenses in a triangle on the left,
flash and LiDAR on the right), smaller Dynamic Island, Camera Control button, **Burgundy**. **No Apple logo, wordmark or UI.**

## Beat outline (time it from the measured take; never re-time)
| Lines | Block | What happens on screen | HUD / labels |
|---|---|---|---|
| 1-2 | H | c01: the old phone flies, bounces and lands on the pile (a physical event on frame 1, like #14). Push in on it; an X-ray flash shows gold inside. | hook burned in |
| 3-6 | S | The phone lands on the workbench and the "DON'T TRY THIS AT HOME · toxic fumes & acid" card stamps on. The lid lifts and the battery slides out. c02 cutaway: the battery puffs and flashes. | label `battery` |
| 7-8 | E | Macro inside the cutaway: the pins glow gold, then a chip goes see-through to show gold wires beside a single hair. | `hud.count` 0.000 → 0.034 g; labels `pins`, `gold wire` |
| 9-13 | E | Tub: the liquid turns blue, the board crumbles into mud, flecks sparkle, the hose rinses three times, the liquid turns yellow, brown dust snows down. Change the camera angle on each colour state. | |
| 14-15 | R1 | Macro on the brown dust, then the crucible glows under the torch, the gold pours in slow motion and the 1 kg bar rises out. c03. | `hud` 1,000 g |
| 16-17 | I | c04 shrug. The readout rewinds to **1 phone = 0.034 g ≈ £3**, then **× 30,000**. Big pull-back to the phone mountain. | `hud` £3 → × 30,000 |
| 18 | R2 | Side by side: a pile of phones full of glowing flecks vs a pile of rock with one fleck. | |
| 19-20 | A/CTA | The drawer slides open, full of old phones. One shows photos, then erases to "Hello". Match cut back to the frame-1 toss for a seamless loop. | label `erase first` |

## Facts (check before posting)
- **About 0.034 g of gold per phone** (some sources give 7-34 mg): APMEX "How much gold is in a cell phone"; OnRecycle "How many phones does it take to mine 1g of gold".
- **Gold about £98.31 a gram** (BullionVault, 5 Nov 2026), so 0.034 g ≈ £3.33, said as "about three pounds". **Recheck on 27 Nov**;
  if the price has moved more than about 15%, change line 16.
- **1 kg ÷ 0.034 g ≈ 29,400 phones**, said as "about thirty thousand".
- **Tonne for tonne:** about 140-400 g of gold per tonne of phones vs about 1-20 g per tonne of ore (World Gold Council, "Gold and e-waste";
  press round-ups). No multiplier is quoted on purpose (the "100x/300x" figures are disputed).
- **Damaged lithium batteries can catch fire**: standard battery safety guidance.
- Gold-plated contacts and gold bond wires in **some** chips: standard; "some" is the hedge.

## Files
- data/lines.json (20 lines; presets copied from #15, blocks, starred words, character clips), script.txt (lines only).
- Not built yet: tools/ (copy make_voice.py, build_captions.py, make_sound.py, qc.py from ../phoneverse_fix15_studio), timings.json,
  captions.json, ../phoneverse_3d_studio/data/make_beats_fix16.py, the new world.py props and char_scene.py clips.

## Next steps
1. Voice take (Kokoro af_heart, #15 presets), measure the timings and lock them. Check the length is 60-70 s.
2. Build the props and the yard dressing, then render `--test` stills and check docs/storyboard_3d.png at phone size first.
3. Character clips c01-c04, the full render, QC (-14 LUFS, 1080×1920), phone-size sheet, post caption.
