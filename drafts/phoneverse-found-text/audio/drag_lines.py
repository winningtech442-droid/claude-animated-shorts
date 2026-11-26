# Lines with a repeated word, said the house way: TWICE, the first short, the second dragged ("Oi! Oiiiiii!"),
# with set pauses between the pieces. Each line is built from pieces voiced separately by Chatterbox (same cloned
# voices as chatterbox_lines.py), so every pause and every drag length is exact.
#   - "say"  piece: N takes, Whisper picks the one that matches the text
#   - "drag" piece: N takes of the elongated spelling; the vowel is then time-stretched (pitch kept) to the target length
#   - "pause": silence of a set length
# Output (same format chatterbox_lines.py writes, so make_audio.py picks it up): out/chatterbox/<id>.wav + <id>_words.json
#   python drag_lines.py [--only L06 L08]      (Chatterbox env)
import argparse
import difflib
import json
import os
import re
import subprocess
import tempfile

import numpy as np
import soundfile as sf
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
CB = os.path.join(HERE, "out", "chatterbox")

# piece kinds: ("say", text, exaggeration, words Whisper should hear)
#              ("drag", text, exaggeration, caption word, target seconds, stretch region (start, end) as fractions)
#              ("pause", seconds)
LINES = {
    "L06": ("YOU", [("say", "Oi!", 0.9, "oi"), ("pause", 0.5),
                    ("drag", ["OI!!", "Oiii!"], 1.0, "Oiiiii!", 1.05, (0.45, 0.88)), ("pause", 0.5),
                    ("say", "Get off! Get OFF it!", 0.95, "get off get off it")]),
    "L08": ("YOU", [("say", "No!", 0.95, "no"), ("pause", 0.14),
                    ("drag", ["Noooooo!", "NO!!"], 1.05, "Noooooo!", 1.15, (0.25, 0.85))]),
    "L09": ("YOU", [("say", "Wait!", 0.85, "wait"), ("pause", 0.12),
                    ("drag", ["WAIT!!", "Waaait!"], 0.9, "Waaait!", 0.75, (0.2, 0.62)), ("pause", 0.12),
                    ("say", "Who's got it? Who's GOT it?!", 0.85, "who's got it who's got it")]),
    "L12": ("YOU", [("say", "Nah...", 0.5, "nah"), ("pause", 0.28),
                    ("drag", ["Nahhh.", "Naah."], 0.55, "naaaah.", 0.85, (0.3, 0.85)), ("pause", 0.3),
                    ("say", "I am NOT chasing two grown men down Oxford Street.", 0.6,
                     "i am not chasing two grown men down oxford street")]),
    "L21": ("JESS", [("say", "Shut UP! They found it?! Tap it!", 0.95, "shut up they found it tap it"), ("pause", 0.12),
                     ("drag", ["Tap it!", "Tap it!!"], 0.95, "Taaap it!", 0.95, (0.12, 0.55))]),
}


def norm(s):
    return re.sub(r"[^a-z' ]", " ", s.lower()).split()


def score(heard, want):
    return difflib.SequenceMatcher(None, norm(heard), norm(want)).ratio()


def trim(x, sr, keep=0.03):
    thr = 0.02 * np.max(np.abs(x))
    nz = np.flatnonzero(np.abs(x) > thr)
    if not len(nz):
        return x
    return x[max(0, nz[0] - int(keep * sr)): min(len(x), nz[-1] + int(0.05 * sr))]


def atempo(x, sr, factor):
    """time-stretch by `factor` (>1 = longer), pitch kept (ffmpeg's WSOLA atempo, chained for big factors)"""
    tempo, parts = 1.0 / factor, []
    while tempo < 0.5:
        parts.append("atempo=0.5")
        tempo /= 0.5
    parts.append(f"atempo={tempo:.5f}")
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "a.wav"), os.path.join(d, "b.wav")
        sf.write(a, x, sr, subtype="FLOAT")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a, "-af", ",".join(parts), b], check=True)
        y, _ = sf.read(b, dtype="float64")
    return y


def vibrato(x, sr):
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "a.wav"), os.path.join(d, "b.wav")
        sf.write(a, x, sr, subtype="FLOAT")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a, "-af", "vibrato=f=5.5:d=0.06", b], check=True)
        y, _ = sf.read(b, dtype="float64")
    return y[: len(x)] if len(y) >= len(x) else np.pad(y, (0, len(x) - len(y)))


def stretch_region(x, sr, frac, target):
    """lengthen only the vowel (frac = its start/end as fractions of the word) so the whole word lasts `target` s"""
    n = len(x)
    if n / sr >= target:
        return x
    a, b = int(frac[0] * n), int(frac[1] * n)
    seg = x[a:b]
    want = target - (n - (b - a)) / sr
    y = atempo(seg, sr, want / ((b - a) / sr))
    y = vibrato(y, sr)
    f = int(0.012 * sr)  # 12 ms crossfades at both joins
    head, tail = x[:a], x[b:]
    y = y.copy()
    y[:f] = y[:f] * np.linspace(0, 1, f) + head[-f:] * np.linspace(1, 0, f)
    y[-f:] = y[-f:] * np.linspace(1, 0, f) + tail[:f] * np.linspace(0, 1, f)
    out = np.concatenate([head[:-f], y, tail[f:]])
    # a drawn-out shout sags at the end: gentle level fall over the stretched part
    g = np.ones(len(out))
    s0, s1 = len(head) - f, len(head) - f + len(y)
    g[s0:s1] = np.linspace(1.0, 0.82, s1 - s0)
    g[s1:] = 0.82
    return out * g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--takes", type=int, default=3)
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()

    from chatterbox.tts import ChatterboxTTS
    from faster_whisper import WhisperModel
    from scipy.signal import resample_poly

    os.makedirs(os.path.join(CB, "takes"), exist_ok=True)
    tts = ChatterboxTTS.from_pretrained(device="cpu")
    asr = WhisperModel("small.en", device="cpu", compute_type="int8")
    sr = tts.sr

    def hear(x):
        y = resample_poly(x, 16000, sr).astype(np.float32)
        segs, _ = asr.transcribe(y, beam_size=5, language="en", word_timestamps=True)
        segs = list(segs)
        return (" ".join(s.text.strip() for s in segs),
                [dict(text=w.word.strip(), start=float(w.start), end=float(w.end)) for s in segs for w in (s.words or [])])

    report = json.load(open(os.path.join(CB, "picked.json"))) if os.path.exists(os.path.join(CB, "picked.json")) else {}
    for lid, (who, pieces) in LINES.items():
        if args.only and lid not in args.only:
            continue
        ref = os.path.join(CB, f"ref_{who}.wav")
        audio, words, t = [], [], 0.0
        for p_i, pc in enumerate(pieces):
            if pc[0] == "pause":
                audio.append(np.zeros(int(pc[1] * sr)))
                t += pc[1]
                continue
            kind, exa = pc[0], pc[2]
            texts = [pc[1]] * args.takes if kind == "say" else [tx_ for tx_ in pc[1] for _ in range(args.takes)]
            best = None
            for k, text in enumerate(texts):
                torch.manual_seed(2000 + 31 * k + 7 * p_i)
                x = tts.generate(text, audio_prompt_path=ref, exaggeration=exa, cfg_weight=0.3, temperature=0.8)
                x = trim(x.squeeze().cpu().numpy().astype(np.float64), sr)
                heard, ws = hear(x)
                dur = len(x) / sr
                if kind == "say":
                    want = pc[3]
                    sc = score(heard, want) - 0.05 * max(0.0, dur - (0.42 * len(norm(want)) + 0.6))
                    key = (round(sc, 2), -dur)
                else:  # drag: Whisper must hear exactly the word once (letters collapsed: "noooo" = "no"), then the longest wins
                    squash = lambda ws: [re.sub(r"(.)\1+", r"\1", w_) for w_ in ws]
                    want_ = squash(norm(pc[3])); got = squash(norm(heard))
                    ok = got == want_ or (len(got) == len(want_) and all(difflib.SequenceMatcher(None, g_, w_).ratio() >= 0.75 for g_, w_ in zip(got, want_)))
                    key = (ok, min(dur, pc[4]))
                sf.write(os.path.join(CB, "takes", f"{lid}_p{p_i}_take{k + 1}.wav"), x, sr, subtype="FLOAT")
                print(f"{lid} piece {p_i} take{k + 1} [{text}]: {dur:4.2f}s | {heard}" + (f" ok={key[0]}" if kind == "drag" else ""))
                if best is None or key > best[0]:
                    best = (key, x, ws, heard)
            _, x, ws, heard = best
            if kind == "drag":
                x = stretch_region(x, sr, pc[5], pc[4])
                cw, a0, a1 = pc[3].split(), t + 0.02, t + len(x) / sr - 0.05
                if len(cw) == 1:
                    words.append(dict(text=cw[0], start=a0, end=a1))
                else:  # "Taaap it!": the dragged word takes 70%, the tail word the rest
                    m = a0 + 0.7 * (a1 - a0)
                    words += [dict(text=cw[0], start=a0, end=m), dict(text=cw[1], start=m, end=a1)]
            else:
                words += [dict(w, start=t + w["start"], end=t + w["end"]) for w in ws]
            audio.append(x)
            t += len(x) / sr
        x = np.concatenate(audio)
        heard, _ = hear(x)
        sf.write(os.path.join(CB, f"{lid}.wav"), x, sr, subtype="FLOAT")
        json.dump(dict(sr=sr, words=words), open(os.path.join(CB, f"{lid}_words.json"), "w"), indent=1)
        report[lid] = dict(take="pieces", heard=heard, seconds=round(len(x) / sr, 2),
                           words=[w["text"] for w in words])
        print(f"  -> {lid}: {len(x) / sr:.2f}s | heard: {heard} | words: {[w['text'] for w in words]}")
        json.dump(report, open(os.path.join(CB, "picked.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
