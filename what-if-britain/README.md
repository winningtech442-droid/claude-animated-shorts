# What If Britain studio (v3)

Animated UK money stories for TikTok: Remotion + three.js, 1080x1920, 30 fps. This folder is the studio's home
in this repo, kept apart from the Phoneverse work on other branches.

| File | What |
|---|---|
| `STUDIO-RULES.md` | The one rule book: episode format, cast, scenes, voices, sound, QA, pipeline (v3, 27 Nov 2026) |
| `SCRIPT-TEMPLATE.md` | The script layout the user approves before anything is voiced |
| `LORE.md` | Continuity: the pin, the Booth, open threads, episode log |
| `voices/` | The approved cast voices: one reference clip per character, settings in `cast.json` |

## Voice engine (Chatterbox) setup notes
Tested 27 Nov 2026 in the "What If Britain studio" cloud environment (4 CPUs, no GPU):
- Installed in its own Python environment: `python3 -m venv /root/cb-venv && /root/cb-venv/bin/pip install chatterbox-tts "setuptools<81"`.
  The `setuptools<81` pin matters: its watermark module still imports `pkg_resources`, which newer setuptools removed
  (symptom: `TypeError: 'NoneType' object is not callable` at `PerthImplicitWatermarker()`).
- Model files come from Hugging Face (`ResembleAI/chatterbox`, MIT licence, ~3 GB). The environment allows
  `huggingface.co` and `us.aws.cdn.hf.co`; set `HF_HUB_DISABLE_XET=1` so downloads use that CDN host.
- Speed on CPU: about 7x slower than real time (7.3 s of speech in 51 s), so ~8 minutes of voice per episode.
- Character voices: a reference clip per character made with Kokoro (house voice E = 0.6 `bm_george` + 0.4 `bm_lewis`),
  then `ChatterboxTTS.generate(text, audio_prompt_path=ref, exaggeration=..., cfg_weight=...)`.
  Exaggeration 1.2 came out about 3.5 LU louder than 0.5, with near-full peaks.
- Not in the environment's setup script yet: a new container needs the install and the model download again.

**Status (27 Nov 2026):** the v3 rules are agreed. The studio code (src, tools, audio) still has to be copied in
from the user's zip; the v2 originals are also in the user's Drive folder "What if Britain". Then the tools get
updated to v3 (see `STUDIO-RULES.md`, section 10) and a pilot episode goes through both approvals.
