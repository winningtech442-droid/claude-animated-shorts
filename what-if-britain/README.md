# What If Britain studio (v3)

Animated UK money stories for TikTok: Remotion + three.js, 1080x1920, 30 fps, no motion blur. This folder is the
studio's home in this repo, kept apart from the Phoneverse work on other branches. Imported 27 Nov 2026 from
`wib-studio-20nov-ep20.zip` (the original zip stays in the user's Drive folder "What if Britain" as the backup).

**Rules first:** `STUDIO-RULES.md` (v3) is the one rule book. Scripts use `SCRIPT-TEMPLATE.md`; continuity lives in
`LORE.md`. The user approves every script and a 10-20 s test render before any video is made.

## What's where
| Path | What |
|---|---|
| `src/cast/` | The cast in 3D: `Person.tsx` (body, 12 faces, Union Jack pin; a single `build` number so far) and `cast.ts` (Alfie, Mate, Nan looks) |
| `src/tests/` | `ActingTest.tsx`: the acting and pose system every hand-built episode uses; `PoseLab`, `actingBeats` |
| `src/ep/` | Hand-built episodes (the way Ep 09-20 were made): `kit.tsx` (stage, lights, cast placement, captions) and `ep20.tsx`, the latest reference |
| `src/engine/` + `src/episodes/demo`, `set-preview` | The data-driven shot engine used for Eps 01-08 (shots, camera moves, fly/whip, number card) |
| `src/worlds/`, `src/props/` | The engine's parts library: streets (1975/1988/2026), bank, shop, kitchen, trading floor, committee room, sea; props (coins, notes, price tags, house, meter...). Retired as locations; mined for parts |
| `src/kit/` | Captions, fonts, text helpers, `fitpose` (framing) |
| `src/episodes/ep20/` | Ep 20's script, facts, cast, voice lines and word timings (for `src/ep/ep20.tsx`) |
| `src/episodes/ORDER.txt` | Posting order, read by the gate |
| `voices/` | The approved cast voices: one reference clip per character, settings in `cast.json` |
| `tools/` | `gate.py` (script checks), `house_voice.py` (Kokoro narrator), `align.py` (word timings), `placeholder_words.py`, `starts.mts`, `stills.mjs`, `sheet.py`, `render_chunks.sh`, `build.sh` (engine episodes), `finish.sh`, `qa.py`, `pacecheck.py`, `dumpevents.mts`, `browser.mjs` |
| `audio/` | `ep_sfx.py` (effects and mix for hand-built episodes, one cue function per episode), `acting_sfx.py`, `sfxcore.py`; `score.py`, `sfx.py`, `mix.py` (engine episodes) |
| `voice.json` | House voice E (and proposed F) settings; the narrator's reference clip is built from E |
| `CTA-BANK.md` | Asks and rotation history. v3 has no spoken ask: asks go in the description and pinned comment only |
| `archive/` | v2 rules and README, scripts / facts / cast / voice lines of the 15 earlier episodes, 12 post texts |

## Quick checks
- `npm ci` then `npx tsc --noEmit -p .` (clean as of 27 Nov 2026).
- `npx remotion still src/index.ts CastSheet out/castsheet.png --frame=0 --scale=0.5` renders the cast sheet
  (Chromium comes from `/opt/pw-browsers`, see `remotion.config.ts`).

## Voice engine (Chatterbox) setup notes
Tested 27 Nov 2026 in the "What If Britain studio" cloud environment (4 CPUs, no GPU):
- Installed in its own Python environment: `python3 -m venv /root/cb-venv && /root/cb-venv/bin/pip install chatterbox-tts "setuptools<81"`.
  The `setuptools<81` pin matters: its watermark module still imports `pkg_resources`, which newer setuptools removed
  (symptom: `TypeError: 'NoneType' object is not callable` at `PerthImplicitWatermarker()`).
- Model files come from Hugging Face (`ResembleAI/chatterbox`, MIT licence, ~3 GB). The environment allows
  `huggingface.co` and `us.aws.cdn.hf.co`; set `HF_HUB_DISABLE_XET=1` so downloads use that CDN host.
- Speed on CPU: about 7x slower than real time (7.3 s of speech in 51 s), so ~8 minutes of voice per episode.
- Character voices: a reference clip per character made with Kokoro, then
  `ChatterboxTTS.generate(text, audio_prompt_path=voices/<name>.wav, exaggeration=..., cfg_weight=...)`.
  Exaggeration 1.2 came out about 3.5 LU louder than 0.5, with near-full peaks.

## Status (27 Nov 2026)
Done: v3 rules, script template, lore bible, approved cast voices, studio imported and cleaned (it type-checks and renders).
Done with the EP21 pilot: the Chatterbox voice tool for several speakers (`tools/cast_voice.py`, guests auditioned with
`tools/make_voice.py`), the v3 episode kit (`src/ep/kit3.tsx`: speaker-coloured captions with starred bleeps, lip flap,
the mid-video title card, fact cards, the final cut to black), the body system (heavy-set Mate, tiny stooped Nan,
guests), `qa.py` for v3 (61-68 s, the final black allowed). EP21 went through both approvals (script, 20 s test).
Next: v3 checks in `gate.py`; approvals in `build.sh`; fold the hand-built EP21 pattern (`src/ep/ep21/`) into the
engine so the next episode needs less hand-placing.
