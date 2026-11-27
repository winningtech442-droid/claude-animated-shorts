"""An original music bed for an episode, from out/<id>/events.json (no samples, nothing to license).

usage: python3 -I audio/score.py out/<id>/events.json out/<id>/music.wav
Minimal electronic, 116 BPM, A minor (Am F C G): sub bass, plucked arpeggio, soft pad, hats.
Builds through the episode, drops out for 0.55 s before each number card, a riser lands on the card.
"""
import json, sys
import numpy as np, soundfile as sf
sys.path.insert(0, 'audio')
from sfxcore import SR, n_of, tvec, lpf, hpf, noise, riser, place

ev = json.load(open(sys.argv[1])); out = sys.argv[2]
N = n_of(ev['total']); buf = np.zeros((2, N))
BPM = 116; beat = 60 / BPM; bar = 4 * beat
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G (MIDI)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
drops = [(n['t'] - 0.55, n['t']) for n in ev['numbers']]
in_drop = lambda t: any(a <= t < b for a, b in drops)
build = lambda t: min(1.0, 0.45 + 0.55 * t / max(1, ev['total']))

def note(f, dur, kind):
    t = tvec(n_of(dur))
    if kind == 'bass': return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t / 0.35) * np.minimum(1, t / 0.005)
    if kind == 'pluck': return (np.sin(2 * np.pi * f * t) + 0.4 * np.sign(np.sin(2 * np.pi * f * t)) * 0.3) * np.exp(-t / 0.18) * np.minimum(1, t / 0.002)
    if kind == 'pad': return sum(np.sin(2 * np.pi * f * d * t) for d in (1, 1.004, 0.996)) / 3 * np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.4)

b = 0
while b * bar < ev['total']:
    ch = CH[b % 4]; t0 = b * bar
    place(buf, lpf(note(hz(ch[0]) / 2, bar, 'pad') + note(hz(ch[1]) / 2, bar, 'pad') + note(hz(ch[2]) / 2, bar, 'pad'), 1800) * 0.16, t0)
    for k in range(8):  # 8th-note bass and arpeggio
        t = t0 + k * beat / 2
        if t >= ev['total'] or in_drop(t): continue
        g = build(t)
        place(buf, note(hz(ch[0] - 24), beat / 2, 'bass') * 0.5 * g, t)
        place(buf, lpf(note(hz(ch[k % 3] + 12), beat / 2, 'pluck'), 3500) * 0.18 * g, t, pan=0.35 if k % 2 else -0.35)
        if t > ev['shots'][0]['end']:  # hats after the first shot
            place(buf, hpf(noise(n_of(0.03)), 7000) * np.exp(-tvec(n_of(0.03)) / 0.008) * 0.12 * g, t + beat / 4)
        if k % 4 == 0:  # half-time kick
            kt = tvec(n_of(0.25)); place(buf, np.sin(2 * np.pi * (50 + 80 * np.exp(-kt / 0.03)) * kt) * np.exp(-kt / 0.12) * 0.7 * g, t)
    b += 1
for n in ev['numbers']:
    r = riser(1.2); place(buf, r * 0.18, n['t'] - 1.2)
buf = hpf(buf, 28)
sf.write(out, (buf / max(1e-9, np.abs(buf).max()) * 0.8).T.astype(np.float32), SR)
print(f'{out}: {ev["total"]:.1f} s, {len(drops)} dropouts')
