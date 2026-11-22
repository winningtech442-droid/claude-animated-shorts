#!/usr/bin/env python3
"""data/captions.json: 1-2 words at a time, one yellow starred word per line, timed inside each measured line.
Timing is proportional to word length inside the spoken line (±0.25 s). For exact timing run a forced aligner
(for example faster-whisper word timestamps on audio/lines/line_NN.wav) and overwrite the 'start'/'end' values."""
import json, re
T = json.load(open("data/timings.json")); out = []
for l in T["lines"]:
    toks = l["text"].replace("...", " … ").split()
    toks = [t for t in toks if t != "…"]
    # weight = letters + a small bonus when the word ends a sentence/clause (the voice breathes there)
    wts = []
    for t in toks:
        core = re.sub(r"[^A-Za-z0-9£']", "", t)
        bonus = 3 if re.search(r"[.?!,]$", t) else 0
        wts.append(max(2, len(core)) + bonus)
    tot = sum(wts); t0 = l["start"]; span = l["speech_s"]
    # greedy grouping: pairs unless a word is long (>7 letters) or ends a sentence
    groups, i = [], 0
    while i < len(toks):
        core = re.sub(r"[^A-Za-z0-9£']", "", toks[i])
        if i + 1 < len(toks) and len(core) <= 7 and not re.search(r"[.?!]$", toks[i]) and len(re.sub(r"[^A-Za-z0-9£']", "", toks[i+1])) <= 8:
            groups.append([i, i + 1]); i += 2
        else:
            groups.append([i]); i += 1
    acc = 0.0
    for g in groups:
        w = sum(wts[k] for k in g); a = t0 + span * acc / tot; acc += w; b = t0 + span * acc / tot
        words = [re.sub(r"(?<=\d),(?=\d)", "\x00", toks[k]) for k in g]; words = [re.sub(r"[^A-Za-z0-9£%'\x00-]", "", w_).replace("\x00", ",") for w_ in words]   # keep "£1,499"
        star = [w_.lower() == l["star"].lower() for w_ in words]
        out.append({"line": l["id"], "start": round(a, 3), "end": round(b, 3), "words": words, "star": star})
json.dump(out, open("data/captions.json", "w"), indent=1)
print(len(out), "caption cards;", sum(any(c["star"]) for c in out), "with a yellow word")
miss = [l["id"] for l in T["lines"] if not any(any(c["star"]) for c in out if c["line"] == l["id"])]
print("lines without a starred word:", miss or "none")
