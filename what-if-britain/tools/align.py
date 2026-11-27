# tools/align.py
"""Sentence-chunked forced alignment of a script to a voiceover (pocketsphinx 5, offline).

usage: python3 -I tools/align.py script.txt vo.mp3 src/data/words.json [--say 911="nine one one" ...] [--peek]

Writes [{text, start, end}] for every display word of the script (punctuation kept, so captions can
page on . ? ! ,). Whole-file alignment drifts on ~95 s files, so the audio is cut at silences that
match sentence ends (DP on expected sentence length) and each chunk is aligned on its own.
--say adds spoken forms for numbers/brands the aligner can't read. --peek prints free ASR of two chunks
so you can confirm the MP3 is the right recording before building anything on it.
"""
import json, re, subprocess, sys
import numpy as np
from pocketsphinx import Decoder

SAY = {"gps": "g p s", "airtag": "air tag", "airtags": "air tags", "iphone": "i phone", "iphones": "i phones",
       "wi-fi": "wi fi", "wifi": "wi fi", "uwb": "u w b", "911": "nine one one", "sos": "s o s", "ok": "okay",
       "mph": "miles per hour", "earbud": "ear bud", "earbuds": "ear buds", "eartip": "ear tip", "wideband": "wide band", "ultra-wideband": "ultra wide band"}
ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def num_words(n):
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000: return ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + num_words(n % 100))
    if n < 1_000_000: return num_words(n // 1000) + " thousand" + ("" if n % 1000 == 0 else " " + num_words(n % 1000))
    return num_words(n // 1_000_000) + " million" + ("" if n % 1_000_000 == 0 else " " + num_words(n % 1_000_000))


def main():
    args = sys.argv[1:]
    peek = "--peek" in args
    args = [a for a in args if a != "--peek"]
    while "--say" in args:
        i = args.index("--say"); k, v = args[i + 1].split("=", 1); SAY[k.lower()] = v.strip('"'); del args[i:i + 2]
    script_path, audio_path, out_path = args[:3]
    tokens = open(script_path).read().split()
    dec = Decoder(samprate=16000, bestpath=False)

    def spoken(tok):
        core = re.sub(r"[^\w',.\-$%]", "", tok).lower().strip(",.'")
        if core in SAY: return SAY[core].split()
        m = re.fullmatch(r"\$?([\d,]+)(?:\.(\d+))?(%?)", core)
        if m:
            w = num_words(int(m.group(1).replace(",", "")))
            if m.group(2): w += " point " + " ".join(ONES[int(d)] for d in m.group(2))
            if m.group(3): w += " percent"
            if core.startswith("$"): w += " dollars"
            return w.split()
        out = []
        for part in re.split(r"[-–—/]", core):
            p = part.strip("'.,")
            if not p: continue
            if dec.lookup_word(p) is not None: out.append(p)
            elif p.endswith("'s") and dec.lookup_word(p[:-2]) is not None: out.append(p[:-2])
            elif re.fullmatch(r"\d+", p): out += num_words(int(p)).split()
            else:
                print(f"  not in dictionary: {p!r} -> spelled as letters (add --say {p}=\"...\" if it's read as a word)", file=sys.stderr)
                out += list(re.sub(r"[^a-z]", "", p))
        return out

    sp = [spoken(t) for t in tokens]
    # sentences = token ranges ending in . ? !
    sents, s0 = [], 0
    for i, t in enumerate(tokens):
        if re.search(r"[.?!][\"'”’)]*$", t) or i == len(tokens) - 1:
            sents.append((s0, i + 1)); s0 = i + 1
    syl = [sum(max(1, len(re.findall(r"[aeiouy]+", w))) for i in range(a, b) for w in sp[i]) for a, b in sents]

    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", audio_path, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    pcm = np.frombuffer(raw, dtype=np.int16)
    x = pcm.astype(np.float64) / 32768
    hop = 160  # 10 ms
    nf = len(x) // hop
    db = 10 * np.log10(np.mean(x[:nf * hop].reshape(nf, hop) ** 2, axis=1) + 1e-12)
    thr = max(-42.0, np.percentile(db, 95) - 32)
    quiet = db < thr
    loud = np.where(~quiet)[0]
    t0, t1 = loud[0] / 100, (loud[-1] + 1) / 100
    cands, i = [], 0
    while i < nf:
        if quiet[i]:
            j = i
            while j < nf and quiet[j]: j += 1
            if j - i >= 25 and i / 100 > t0 and j / 100 < t1:  # >= 0.25 s, inside the speech
                cands.append(((i + j) / 200, (j - i) / 100))
            i = j
        else:
            i += 1
    # DP: assign sentence ends to silences so chunk lengths match syllable-based expectations
    S = len(sents)
    total_sil = sum(d for _, d in cands)
    rate = (t1 - t0 - 0.6 * total_sil) / max(1, sum(syl))
    pts = [(t0, 0.0)] + cands + [(t1, 0.0)]
    C = len(pts)
    INF = 1e18
    best = {(0, 0): (0.0, None)}
    for k in range(1, S + 1):
        for j in range(1, C):
            if (k == S) != (j == C - 1): continue
            bc, bp = INF, None
            for kk in range(max(0, k - 8), k):
                exp_syl = sum(syl[kk:k])
                for jj in range(0, j):
                    if (kk, jj) not in best: continue
                    d = pts[j][0] - pts[jj][0]
                    e = exp_syl * rate + 0.35 * (k - kk - 1)
                    c = best[(kk, jj)][0] + ((d - e) / (0.18 * e + 0.4)) ** 2 + 4.0 * (k - kk - 1) - 0.5 * min(pts[j][1], 1.0)
                    if c < bc: bc, bp = c, (kk, jj)
            if bp: best[(k, j)] = (bc, bp)
    node, cuts = (S, C - 1), []
    while node:
        cuts.append(node); node = best[node][1]
    cuts = cuts[::-1]  # [(sentence_idx, point_idx)], first is (0,0)
    chunks = []
    for (ka, ja), (kb, jb) in zip(cuts, cuts[1:]):
        chunks.append([sents[ka][0], sents[kb - 1][1], pts[ja][0] - (0.25 if ja == 0 else 0), pts[jb][0] + (0.3 if jb == C - 1 else 0)])

    def align(a, b, ta, tb):
        words = [(i, w) for i in range(a, b) for w in sp[i]]
        s, e = max(0, int(ta * 16000)), min(len(pcm), int(tb * 16000))
        dec.set_align_text(" ".join(w for _, w in words))
        dec.start_utt(); dec.process_raw(pcm[s:e].tobytes(), full_utt=True); dec.end_utt()
        segs = [(re.sub(r"\(\d+\)$", "", g.word), ta + g.start_frame / 100, ta + (g.end_frame + 1) / 100) for g in (dec.seg() or [])]
        segs = [g for g in segs if g[0] not in ("<s>", "</s>", "<sil>", "(NULL)") and not g[0].startswith("[")]
        if len(segs) != len(words): return None
        return [(i, st, en) for (i, _), (_, st, en) in zip(words, segs)]

    done, k, fails = [], 0, 0  # done = [(first_chunk, last_chunk, result)]
    while k < len(chunks):
        r = align(*chunks[k])
        if r is None:  # a cut landed on a comma pause: re-align together with neighbours
            fails += 1
            for back, fwd in [(1, 0), (0, 1), (1, 1), (0, 2), (1, 2), (0, 3), (1, 3)]:
                if (back and not done) or k + fwd >= len(chunks): continue
                c0 = done[-1][0] if back else k
                r = align(chunks[c0][0], chunks[k + fwd][1], chunks[c0][2], chunks[k + fwd][3])
                if r is not None:
                    if back: done.pop()
                    k += fwd; break
            if r is None:
                sys.exit(f"alignment failed near '{' '.join(tokens[chunks[k][0]:chunks[k][0] + 8])}…' "
                         f"({chunks[k][2]:.1f} s): wrong recording, or a word read differently from the script?")
            done.append((c0, k, r))
        else:
            done.append((k, k, r))
        k += 1
    res = [x for _, _, r in done for x in r]
    out = []
    for i, t in enumerate(tokens):
        g = [(st, en) for j, st, en in res if j == i]
        if g: out.append({"text": t, "start": round(g[0][0], 3), "end": round(g[-1][1], 3)})
    json.dump(out, open(out_path, "w"), indent=0)
    gaps = [b["start"] - a["end"] for a, b in zip(out, out[1:])]
    print(f"{len(sents)} sentences -> {len(chunks)} chunks ({fails} re-merged), {len(out)}/{len(tokens)} words, "
          f"speech {t0:.2f}-{t1:.2f} s, last word ends {out[-1]['end']:.2f} s, longest gap {max(gaps):.2f} s -> {out_path}")
    if peek:
        free = Decoder(samprate=16000)
        mid = max(chunks[len(chunks) // 4: 3 * len(chunks) // 4] or chunks, key=lambda c: c[1] - c[0])
        for a, b, ta, tb in [chunks[0], mid]:
            free.start_utt(); free.process_raw(pcm[max(0, int(ta * 16000)):int(tb * 16000)].tobytes(), full_utt=True); free.end_utt()
            print(f"  heard  {max(0, ta):6.2f}s: {free.hyp().hypstr if free.hyp() else ''}")
            print(f"  script        : {' '.join(tokens[a:b])}")


if __name__ == "__main__":
    main()
