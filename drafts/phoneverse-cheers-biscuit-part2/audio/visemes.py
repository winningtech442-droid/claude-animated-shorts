# Lip-sync tracks for Blender: each spoken word -> Kokoro's own British phonemes (misaki) spread over the word's measured time
# (out/words.json) -> Oculus visemes (the AA_VI_00..14 shape keys on the Rocketbox facial models), sampled at 24 fps per character.
# Also writes a loudness envelope per character (mouth opens wider on louder syllables, closes in silence).
#   python visemes.py      (Kokoro env; reads out/words.json, out/timeline.json, out/stems/voice_<WHO>.wav) -> out/visemes.json
import json
import re
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FPS = 24

# misaki phoneme symbol -> Oculus viseme index
# 0 sil, 1 PP, 2 FF, 3 TH, 4 DD, 5 kk, 6 CH, 7 SS, 8 nn, 9 RR, 10 aa, 11 E, 12 ih, 13 oh, 14 ou
VIS = {}
for ch in "pbm": VIS[ch] = 1
for ch in "fv": VIS[ch] = 2
for ch in "θð": VIS[ch] = 3
for ch in "tdɾ": VIS[ch] = 4
for ch in "kɡŋgh": VIS[ch] = 5
for ch in "ʃʒʧʤ": VIS[ch] = 6
for ch in "sz": VIS[ch] = 7
for ch in "nl": VIS[ch] = 8
for ch in "ɹrw": VIS[ch] = 9
for ch in "aɑæʌɐAIW": VIS[ch] = 10  # A = eɪ, I = aɪ, W = aʊ (misaki diphthong letters)
for ch in "ɛeəɜᵊ": VIS[ch] = 11
for ch in "ɪijY": VIS[ch] = 12  # Y = ɔɪ
for ch in "ɒɔoQO": VIS[ch] = 13  # Q/O = əʊ
for ch in "uʊ": VIS[ch] = 14
SKIP = set("ˈˌːˑ̃ ,.!?;:'\"-—…")


def phonemes(g2p, word):
    ps, _ = g2p(word)
    return [VIS[c] for c in ps if c not in SKIP and c in VIS]


def main():
    sys.path.insert(0, HERE)
    from misaki import en
    g2p = en.G2P(trf=False, british=True, fallback=None)
    words = json.load(open(os.path.join(OUT, "words.json")))
    tl = json.load(open(os.path.join(OUT, "timeline.json")))
    total = max(r["end"] for r in tl) + 2.0
    n = int(total * FPS) + 1
    who_all = sorted({r["who"] for r in tl})
    out = {}
    for who in who_all:
        W = np.zeros((n, 15))
        for w in [x for x in words if x["who"] == who]:
            txt = w["word"].strip()
            if txt == "[bleep]":
                seq = [5, 10, 4]  # the mouth keeps moving under the bleep ("f-u-ck" shapes, the joke)
            elif not txt[:1].isalnum():
                continue
            else:
                base = re.sub(r"([A-Za-z])\1{2,}", r"\1", txt)  # dragged words ("Noooooo!") -> the word; its vowel then fills the drag
                seq = phonemes(g2p, base.replace("123", " one two three")) or [10]
                if base != txt:  # hold the vowel: repeat the vowel visemes so they take most of the dragged time
                    vow = [v for v in seq if v >= 10] or [10]
                    seq = seq[:1] + vow * 4 + seq[-1:] if len(seq) > 1 else vow * 4
            t0, t1 = w["start"], max(w["end"], w["start"] + 0.08)
            dt = (t1 - t0) / len(seq)
            for k, v in enumerate(seq):
                a, b = t0 + k * dt, t0 + (k + 1) * dt
                for f in range(int(a * FPS), int(b * FPS) + 1):
                    if 0 <= f < n:
                        W[f, v] = max(W[f, v], 1.0)
        # smooth (co-articulation): each frame blends with neighbours
        K = np.array([0.25, 0.5, 1.0, 0.5, 0.25])
        Ws = np.stack([np.convolve(W[:, v], K, mode="same") for v in range(15)], 1)
        s = Ws.sum(1, keepdims=True)
        Ws = np.where(s > 0, Ws / np.maximum(s, 1e-6), 0.0)
        # loudness envelope from the character's own voice stem
        env = np.zeros(n)
        p = os.path.join(OUT, "stems", f"voice_{who}.wav")
        if os.path.exists(p):
            x, sr = sf.read(p)
            x = x.mean(1) if x.ndim > 1 else x
            hop = sr // FPS
            rms = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) for i in range(min(n, len(x) // hop))])
            ref = np.percentile(rms[rms > 1e-4], 90) if np.any(rms > 1e-4) else 1.0
            env[: len(rms)] = np.clip(rms / ref, 0, 1.2)
        talk = (Ws.sum(1) > 0).astype(float)
        out[who] = dict(visemes=np.round(Ws, 3).tolist(), env=np.round(env * talk, 3).tolist())
        print(f"{who:8s} {int(talk.sum())} talking frames")
    json.dump(dict(fps=FPS, frames=n, chars=out), open(os.path.join(OUT, "visemes.json"), "w"))
    print("-> out/visemes.json")


if __name__ == "__main__":
    main()
