# EP23 guest voice auditions (28 Nov 2026)

Reference clips made with Kokoro (kokoro-onnx, /root/voice/kokoro-v1.0.onnx + voices-v1.0.bin) reading
`cast_reference_text` from `voices/cast.json`, then pitch-shifted with pedalboard, as in `tools/make_voice.py`.
The `lang` column is new: candidate Rep 2 uses an American Kokoro voice (en-us) for the global edition.

**Chatterbox was not run.** This session's network blocks huggingface.co, so the model could not download.
The acted takes (`tools/make_voice.py` / `tools/cast_voice.py`) have to run in the "What If Britain studio"
environment, which allows huggingface.co and us.aws.cdn.hf.co (see README). The user approves the voice from the
reference clip; Chatterbox then copies that voice.

Similarity: speaker-embedding cosine (resemblyzer 0.1.4, bundled weights) against every approved clip in `voices/`.
The closest existing pair in the cast is Mate and Shopkeeper at 0.86. EP22's rejected Manager candidate was 0.91 to Mate.

| Candidate | Kokoro settings | Closest approved voices | Sent |
|---|---|---|---|
| Rep 1 (British) | bm_daniel 1.0, speed 1.18, pitch +3 | manager 0.79, builder 0.77 | yes |
| Rep 2 (American) | am_puck 0.5 + am_michael 0.5, speed 1.12, pitch 0, lang en-us | alfie 0.72, manager 0.72 | yes |
| Owner 1 | bm_lewis 1.0, speed 0.84, pitch -4 | shopkeeper 0.80, mate 0.77 | yes |
| Owner 2 | bm_george 1.0, speed 0.80, pitch -3.5 | shopkeeper 0.83, mate 0.82 | yes |
| (dropped) Rep | bm_fable 0.6 + bm_daniel 0.4, speed 1.15, pitch +1.5 | builder 0.91, alfie 0.89 | no: too close to the Builder |
| (dropped) Rep | bm_george 0.5 + bm_daniel 0.5, speed 1.2, pitch +2.5 | manager 0.84 | no: 0.95 to Rep 1 |
| (dropped) Owner | bm_daniel 0.5 + bm_george 0.5, speed 0.84, pitch -2 | mate 0.95 | no: sounds like Mate |
| (dropped) Owner | bm_george 0.7 + bm_daniel 0.3, speed 0.78, pitch -4.5 | shopkeeper 0.82 | no: 0.98 to Owner 2 |

Each audition clip the user got: the candidate's EP23 lines read flat by Kokoro, then its 10-16 s reference clip.
Once one per guest is approved: rebuild its reference into `voices/rep.wav` / `voices/owner.wav` and add it to
`voices/cast.json` under "guests".
