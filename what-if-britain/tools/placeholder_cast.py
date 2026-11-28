"""Placeholder line and word timings for a v3 episode, from its voice.txt, until the real voices exist.

usage: python3 -I tools/placeholder_cast.py src/episodes/<id>/voice.txt [--wps 2.75]
Writes src/episodes/<id>/lines.json and words.json in the same shape tools/cast_voice.py writes, with "placeholder": true
on every line, so the episode's shots (timed off lines.json) can be built and stilled before Chatterbox has run.
cast_voice.py overwrites both files with the real timings; shots timed with S(n) / E(n) follow automatically.
Estimate: wps words a second (2.75 matches EP22's real Chatterbox lines on average, ends within 1 s) (the narrator's tempo fx speeds it up), longer words take longer, and the cut and bleep fx
are shown the way cast_voice.py shows them (the cut word truncated with a dash, the bleeped word starred).
"""
import json, math, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cast_voice import parse, tokens  # noqa: E402

src = sys.argv[1]
wps = float(sys.argv[sys.argv.index("--wps") + 1]) if "--wps" in sys.argv else 2.75
rows = parse(src, None)
lines, words, t = [], [], 0.0
for n, r in enumerate(rows, 1):
    toks = tokens(r["text"])
    disp = [d for d, _ in toks]
    rate = wps * float(r["fx"].get("tempo", 1.0)) * (1.1 if r["speaker"] == "narrator" else 1.0)
    dur_of = lambda d: max(0.1, (0.42 + 0.075 * len(re.sub(r"[^A-Za-z0-9]", "", d))) / rate)
    wt, x = {}, 0.06
    for i, d in enumerate(disp):
        a = x; b = a + dur_of(d); wt[i] = (a, b)
        x = b + (0.22 if re.search(r"[.?!]\**$", d) else 0.1 if re.search(r"[,;:]\**$", d) else 0.015)
        if d.endswith("..."): x += 0.25
    dur = wt[len(disp) - 1][1] + 0.08
    if "cut" in r["fx"]:
        word, _, frac = str(r["fx"]["cut"]).partition("@"); frac = float(frac or 0.5)
        hits = [i for i, (_, ws) in enumerate(toks) if word.lower() in ws]
        i = hits[-1]; a, b = wt[i]; cut_t = a + frac * (b - a)
        base = re.sub(r"[^\w']", "", disp[i].replace("*", ""))
        disp = disp[:i] + [(base if frac >= 0.5 else base[: max(1, math.ceil(len(base) * frac))]) + "–"]
        wt = {j: v for j, v in wt.items() if j < i} | {i: (a, cut_t)}; dur = cut_t
    if "bleep" in r["fx"]:
        bw = str(r["fx"]["bleep"]).lower()
        for i, (_, ws) in enumerate(toks):
            if bw in ws and i < len(disp):
                core = re.search(r"[A-Za-z']+", disp[i].replace("*", "")).group(0)
                disp[i] = disp[i].replace(core, core[0] + "*" * (len(core) - 1), 1)
    lines.append(dict(i=n, speaker=r["speaker"], text=" ".join(disp), start=round(t, 3), end=round(t + dur, 3),
                      exaggeration=r["exaggeration"], cfg=r["cfg"], fx=r["fx"], placeholder=True))
    for i, d in enumerate(disp):
        if i in wt:
            words.append(dict(text=d, start=round(t + wt[i][0], 3), end=round(t + wt[i][1], 3), speaker=r["speaker"], line=n))
    t = t + dur + r["pause"]

d = os.path.dirname(src)
json.dump(lines, open(os.path.join(d, "lines.json"), "w"), indent=1)
json.dump(words, open(os.path.join(d, "words.json"), "w"), indent=1)
for L in lines:
    print(f"  {L['i']:2d} {L['start']:6.2f}-{L['end']:6.2f}  {L['speaker']:9s} {L['text']}")
print(f"{len(lines)} lines, {len(words)} words, voice ends at {lines[-1]['end']:.1f} s (placeholder)")
