# Phoneverse FIX #15: Wallet hijack (one texted code puts your card on a stranger's phone): studio package

Threat story, HSERIA + CTA, second person, rule book v8 (format A) **plus character beats**. On 21 Nov the user pointed out that the two
best-performing Phoneverse videos have characters acting, and asked for characters in this one.
Rendered in ../phoneverse_3d_studio with data/beats_fix15.json (39 beats, 11 of them character beats, 20 s in total; generator data/make_beats_fix15.py).
Take 66.54 s, 18 lines, 185 words, 3.09 w/s speech pace, tail 0.32 s. Kokoro **af_heart** (voice B), compressed 3:1 before the mix.

## Why this topic (daily intel, 21 Nov 2026)
- FIX #14's drop-and-bounce opening (a physical event on frame 1) held 50% at 3 s, against about 20% for #12 and #13. Keep it: frame 1 here
  is the glowing copy of your card peeling off and flying onto the scammer's phone.
- Demand: Black Friday is 27 Nov. Vodafone (17 Nov 2026) says 37% of Brits are more likely to open a scam message at Christmas.
  Supply: parcel-text scams are crowded (and were our #12), while digital-wallet hijacking is mostly print articles and rarely shown in 3D.
- vidIQ had no credits, so the outlier and competitor checks were skipped.

## Script decisions (made before the take was locked, never re-timed after)
- The first take ran 52.5 s at 3.83 w/s: these lines are mostly one-syllable words, so af_heart reads them fast. The take was locked
  after two changes: (1) slower presets (TELL 0.80, PUNCH 0.87, SHOCK 0.92, RELIEF 0.80, ASK 0.84), with every pause after a line
  capped at 0.4 s; (2) nine words added, in "70% off", "tap the link" and "in shops and online".
- "One man lost over £18,000 in a few hours": from the Which? case below. The scammer is always "they", never "he".
- The bank text in the video ("... is your code to ADD YOUR CARD TO A DIGITAL WALLET") is an invented example. The script only says
  "If it mentions adding a card to a wallet", so the video does not claim that every bank words its codes this way.

## Characters (Phoneverse Character Sheet)
- **You** (the lead, Rocketbox Female_Adult_01, pink shirt) on a sofa at night. Fairy lights and a warm lamp, the phone glow on her face.
  Nine clips: confused, the deal text, typing, on the call reading the code out, the shock, reading the text, shaking her head
  ("stop"), calling the bank, relief.
- **Hooded figure** (Rocketbox Male_Adult_18, hood up), only from behind at a red-lit laptop, face never shown. Two clips.
- New renderer: ../phoneverse_3d_studio/render/char_scene.py. Biped arm bones are not connected, so Blender's IK constraint aimed at
  the wrong point; the arms use an analytic two-bone solver plus a hand-orientation step. Faces use the approved recipes
  (data/face_recipes.json, plus a new "focus" expression).
- Rule book v8 says 2-3 face beats; this episode has 11 character beats because the user asked for characters acting.

## Files
- data/lines.json (script + presets), data/timings.json (measured, locked), data/captions.json (100 cards; the caption tool now keeps "70%").
- audio/voice_take.wav|mp3, audio/lines/, audio/mix_with_pad.wav, audio/mix_voice_fx.wav.
- tools/make_voice.py, build_captions.py, make_sound.py (#15 cues; packet sounds read from the beat sheet), qc.py.

## Run
```
../phoneverse_3d_studio/.venv_voice/bin/python tools/make_voice.py --models ../phoneverse_3d_studio/models
python3 tools/build_captions.py && ../phoneverse_3d_studio/.venv_voice/bin/python tools/make_sound.py
cd ../phoneverse_3d_studio && python3 data/make_beats_fix15.py && setsid nohup ./build_fix15.sh > build_fix15.log 2>&1 &
```
Assets: the environment's setup script fetches Female_Adult_01. Male_Adult_18 is fetched by hand into assets/m18/ (the FBX's textures are
named m023_*). Render time on 4 cores: characters about 11 s a frame, desk about 6 s a frame, about 3.3 h in total.

## Facts (check before posting)
- Which? (15 Jul 2026), "How I lost £18,000 to digital wallet scammers": callers posing as a bank's fraud department got a one-time
  passcode from the victim and used it to add his card to their own Apple Pay wallet; he lost more than £18,000 in a matter of hours.
- Which? (25 Feb 2025): scam texts and ads lead to fake sites that take your card details. The criminals request a one-time passcode
  from your bank, ask you to type it in, and use it to add your card to their own digital wallet (Apple, Google or Samsung Pay).
  Advice: never share a one-time passcode.
- A bank or card issuer can suspend the card in a wallet on another device; removing it from one device does not remove it from others,
  so call the bank (Bitdefender / Apple guidance).
- For the caption: report scam texts to 7726; Report Fraud (reportfraud.police.uk) or 101 in Scotland.

## Result (21 Nov 2026)
- Finals (gitignored): ../phoneverse_3d_studio/final/phoneverse_fix15_mix_with_pad.mp4 and phoneverse_fix15_mix_voice_fx.mp4. 1597 frames, 66.54 s.
- QC, both mixes: every row passes. Length 66.54 s, tail 0.32 s, pace 3.09 w/s, -14.1 LUFS, true peak -2.4 dB (pad mix) / -2.9 dB (voice+fx),
  loudness range 3.9 / 3.0 LU (the voice+fx mix sits exactly on the 3.0 limit), 38 cuts, longest shot 2.38 s, no black or frozen frames.
- Phone-size check: ../phoneverse_3d_studio/docs/phone_size_check_fix15.png. Weak spots:
  - The pinned labels ("THAT'S ALL IT TOOK", "SCAMMER", "THEIR PHONE") and the HUD's small left-hand word are tiny at phone size.
  - 34.5 s: a packet head over the scammer's phone reads as a pink smudge.
  - The wide shot at 60.5 s is small. The two hooded-figure shots are dark (on purpose), but the laptop glow keeps the silhouette.
  - Phone-pose clips (c05, c11, c13): her hands at the bottom edge are soft blobs; they are cropped, but still visible.
- Render took about 4.5 h on this 4-core box (characters ~10 s a frame, desk ~8-12 s a frame at 540x960 / 16 samples).
