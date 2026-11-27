"""Sound effects placed on what happens on screen, from out/<id>/events.json.

usage: python3 -I audio/sfx.py out/<id>/events.json out/<id>/sfx.wav
fly-through: whoosh + sub drop peaking on the cut · whip: a short swish across the cut · number card: ping
prop pop-in: a soft pop · a growing stack: coin clinks. Logs every cue.
"""
import json, sys
import numpy as np, soundfile as sf
sys.path.insert(0, 'audio')
from sfxcore import SR, n_of, tvec, bpf, noise, whoosh, ping, blip, place

ev = json.load(open(sys.argv[1])); out = sys.argv[2]
buf = np.zeros((2, n_of(ev['total']))); log = []
def cue(sig, t, gain, name, pan=0.0):
    place(buf, sig, t, gain, pan); log.append((round(t, 2), name, gain))

def swish(d=0.3):
    n = n_of(d); t = tvec(n); env = np.sin(np.pi * t / d) ** 2
    return bpf(noise(n), 900, 7000) * env
def clink(f):
    t = tvec(n_of(0.12)); return sum(np.sin(2 * np.pi * f * m * t) * np.exp(-t / (0.05 / m)) for m in (1, 2.7, 5.1)) * np.minimum(1, t / 0.001)

for s in ev['shots'][1:]:
    if s['enter'] == 'fly': cue(whoosh(1.0), s['start'] - 0.55, 0.55, 'whoosh')
    if s['enter'] == 'whip': cue(swish(0.32), s['start'] - 0.16, 0.5, 'swish', pan=-0.3)
for n in ev['numbers']:
    cue(ping(), n['t'], 0.35, 'ping')
for p in ev['pops']:
    if p['type'] == 'pop': cue(blip(520, 0.12, 0.05), p['t'], 0.35, 'pop')
    if p['type'] == 'grow':
        if p.get('kind') in ('Dial', 'House'):  # smooth values: a few dry ticks, not a coin per unit
            k = 6 if p.get('kind') == 'Dial' else 3
            for i in range(k):
                cue(blip(1800 if p.get('kind') == 'Dial' else 300, 0.03, 0.02), p['t'] + (p['t1'] - p['t']) * i / k, 0.22, 'tick')
            continue
        k = max(1, min(24, int(round(abs(p['to'] - p['from'])))))
        for i in range(k):
            cue(clink(2600 + 400 * np.sin(i * 1.7)), p['t'] + (p['t1'] - p['t']) * i / k, 0.18, 'clink', pan=0.2 * np.sin(i))
sf.write(out, buf.T.astype(np.float32), SR)
print(f'{out}: {len(log)} cues')
for t, name, g in log[:40]: print(f'  {t:6.2f}  {name:7s} {g}')
