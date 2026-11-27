"""Placeholder word timings until the real voiceover exists (guide ch. 5: 165 words a minute, 0.45 s after sentences).

usage: python3 -I tools/placeholder_words.py script.txt src/episodes/<id>/words.json [--wpm 210]
Everything re-times when align.py runs on the real MP3.
"""
import json, re, sys
src, out = sys.argv[1], sys.argv[2]
wpm = float(sys.argv[sys.argv.index('--wpm') + 1]) if '--wpm' in sys.argv else 210.0
words, t = [], 0.08
for w in open(src).read().split():
    d = 60.0 / wpm * (0.6 + 0.12 * len(re.sub(r'[^A-Za-z0-9]', '', w)))
    words.append({'text': w, 'start': round(t, 3), 'end': round(t + d, 3)})
    t += d + (0.45 if w[-1] in '.?!' else 0.2 if w[-1] in ',:;' else 0.04)
json.dump(words, open(out, 'w'), indent=1)
print(f'{len(words)} words, {words[-1]["end"]:.1f} s')
