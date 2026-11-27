# Transcribe every rendered line with Whisper and compare it with the script (Chatterbox env: has faster-whisper).
#   python check_lines.py [--only L02 L05]  -> prints a table and writes out/heard.json
import argparse
import difflib
import json
import os
import re

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def norm(s):
    s = s.lower().replace("biscuit124", "biscuit one two four").replace("124", " one two four")
    return re.sub(r"[^a-z' ]", " ", s).split()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()
    from faster_whisper import WhisperModel
    asr = WhisperModel("small.en", device="cpu", compute_type="int8")
    tl = json.load(open(os.path.join(OUT, "timeline.json")))
    res = {}
    for r in tl:
        if args.only and r["id"] not in args.only:
            continue
        x, sr = sf.read(os.path.join(OUT, "lines", f"{r['id']}_{r['who']}.wav"), dtype="float32")
        x = x.mean(1) if x.ndim == 2 else x
        y = resample_poly(x, 16000, sr).astype(np.float32)
        segs, _ = asr.transcribe(y, beam_size=5, language="en")
        heard = " ".join(s.text.strip() for s in segs)
        sc = difflib.SequenceMatcher(None, norm(heard), norm(r["text"])).ratio()
        res[r["id"]] = dict(heard=heard, score=round(sc, 2))
        flag = "" if sc >= 0.85 else "   <-- CHECK"
        print(f"{r['id']} {sc:.2f} | want: {r['text']} | heard: {heard}{flag}")
    json.dump(res, open(os.path.join(OUT, "heard.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
