"""Checks a shot list against the pace rules (claude/script-rules.md, the one-page checklist of 16 Nov 2026, section 6).

usage: python3 -I tools/pacecheck.py src/data/shots.json
shots.json: [{"id": "S1", "start": 0.0, "end": 2.3, "move": "drift" | "fast" | "hold" | "cut" | "fly", "line": "..."}]
Rules: 61-80 s; every picture 1.2-4 s (aim: a new angle every 2-2.5 s, same location); one slow move inside each shot;
at most one whip ("fast"), the timeline switch. The last shot (end card) may run long.
"""
import json, sys, os

shots = json.load(open(sys.argv[1]))
end = max(s['end'] for s in shots)
problems = []
if not 61 <= end <= 80:
    problems.append(f'length {end:.1f} s: must be 61-80 s')
for s in shots[:-1]:
    d = s['end'] - s['start']
    if d > 4.0:
        problems.append(f'{s["id"]} shows one picture for {d:.1f} s: change the angle every 2-2.5 s (max 4)')
    if d < 1.2:
        problems.append(f'{s["id"]} lasts {d:.1f} s: too fast to read (min 1.2)')
fast = [s['id'] for s in shots if s.get('move') == 'fast']
if len(fast) > 1:
    problems.append(f'{len(fast)} whips ({", ".join(fast)}): only the timeline switch may whip')
avg = end / len(shots)
print(f'{len(shots)} pictures in {end:.1f} s: one every {avg:.2f} s (aim 2-2.5); {len(fast)} whip(s)')
print('\n'.join('  ! ' + p for p in problems) if problems else '  pace OK')
if problems and not os.environ.get('FORCE'):
    sys.exit(1)
