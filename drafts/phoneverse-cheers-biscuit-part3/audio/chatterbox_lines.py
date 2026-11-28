# Part 3: re-voice the five most emotional lines with Chatterbox (open-source TTS with an emotion "exaggeration" control),
# cloning the same Kokoro voices so the characters stay consistent.
#
#   1. python make_audio.py --refs          (Kokoro env: writes out/chatterbox/ref_YOU.wav, ref_JESS.wav)
#   2. python chatterbox_lines.py           (Chatterbox env: N takes per line, Whisper picks the best)
#   3. python make_audio.py                 (uses out/chatterbox/<id>.wav for lines marked engine="chatterbox")
#
# Every take is kept in out/chatterbox/takes/ so you can swap in another by copying it over <id>.wav.
import argparse
import difflib
import json
import os
import re

import numpy as np
import soundfile as sf
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
CB = os.path.join(HERE, "out", "chatterbox")

# id: (who, text as Chatterbox should say it, exaggeration, cfg_weight, temperature, text Whisper should hear)
LINES = {
    "L01": ("JESS", "A free upgrade? For me?!", 0.8, 0.3, 0.8, "a free upgrade for me"),
    "L16": ("YOU", "Jess, hang up!", 0.95, 0.3, 0.8, "jess hang up"),
    "L22": ("JESS", "My bank?!", 1.0, 0.5, 0.7, "my bank"),
    "L25": ("JESS", "Someone's stolen my number! Block it! Block it!!", 1.05, 0.45, 0.75,
            "someone's stolen my number block it block it"),
    "L30": ("YOU", "Jess! What if that was really them?!", 0.85, 0.3, 0.8, "jess what if that was really them"),
}

def norm(s):
    return re.sub(r"[^a-z' ]", " ", s.lower()).split()


def score(heard, want):
    return difflib.SequenceMatcher(None, norm(heard), norm(want)).ratio()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--takes", type=int, default=4)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--seed", type=int, default=1000)
    args = ap.parse_args()

    from chatterbox.tts import ChatterboxTTS
    from faster_whisper import WhisperModel
    from scipy.signal import resample_poly

    os.makedirs(os.path.join(CB, "takes"), exist_ok=True)
    tts = ChatterboxTTS.from_pretrained(device="cpu")
    asr = WhisperModel("small.en", device="cpu", compute_type="int8")
    report = {}
    for lid, (who, text, exa, cfg, temp, want) in LINES.items():
        if args.only and lid not in args.only:
            continue
        ref = os.path.join(CB, f"ref_{who}.wav")
        best = None
        for k in range(args.takes):
            torch.manual_seed(args.seed + 17 * k)
            wav = tts.generate(text, audio_prompt_path=ref, exaggeration=exa, cfg_weight=cfg, temperature=temp)
            x = wav.squeeze().cpu().numpy().astype(np.float64)
            path = os.path.join(CB, "takes", f"{lid}_take{k + 1}.wav")
            sf.write(path, x, tts.sr, subtype="FLOAT")  # float: Chatterbox peaks can pass 1.0, 16-bit would clip them
            y = resample_poly(x, 16000, tts.sr).astype(np.float32)
            segs, _ = asr.transcribe(y, beam_size=5, language="en", word_timestamps=True)
            segs = list(segs)
            heard = " ".join(s.text.strip() for s in segs)
            words = [dict(text=w.word.strip(), start=float(w.start), end=float(w.end)) for s in segs for w in (s.words or [])]
            dur = len(x) / tts.sr
            # match the script; penalise takes that run long (Chatterbox sometimes adds breaths/repeats)
            sc = score(heard, want) - 0.04 * max(0.0, dur - (0.42 * len(norm(want)) + 0.8))
            peak = float(np.max(np.abs(x)))
            print(f"{lid} take{k + 1}: {dur:4.2f}s peak {peak:.2f} score {sc:.2f} | {heard}")
            # ties: prefer the take Whisper heard as shouted ("!" or CAPS), then the tighter one
            shout = heard.count("!") + sum(w.isupper() and len(w) > 1 for w in re.findall(r"[A-Za-z]+", heard))
            key = (round(sc, 2), shout, -dur)
            if best is None or key > best[6]:
                best = (sc, k + 1, x, words, heard, dur, key)
        sc, k, x, words, heard, dur, _ = best
        sf.write(os.path.join(CB, f"{lid}.wav"), x, tts.sr, subtype="FLOAT")
        json.dump(dict(sr=tts.sr, words=words), open(os.path.join(CB, f"{lid}_words.json"), "w"), indent=1)
        report[lid] = dict(take=k, score=round(sc, 3), heard=heard, seconds=round(dur, 2))
        print(f"  -> {lid}: picked take {k} ({heard})")
    json.dump(report, open(os.path.join(CB, "picked.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
