"""House voice: Kokoro, British male blend, en-gb, no pitch shift, line by line.

usage: python3 -I tools/house_voice.py src/episodes/<id>/voice.txt out/<id>/vo.mp3 [--voice F|E]
voice.txt: one spoken line per row as  speed|pause|text[|gain]   e.g.  0.85|0.6|Up eighty-nine per cent!|+2
  speed: build-ups 1.05-1.1, normal 1.0, reveals and the hero number 0.8-0.9.
  pause: seconds after the line; 0.1-0.25 normally, 0.3-0.6 before/after reveals, 0 in the first three lines.
  gain (optional, dB, default 0): the emotion knob. +1..+3 on shocks, punches and the hero number,
    -1..-3 on asides, smug or deflated lines. Keep the spread about 5 dB: it survives to the final mix
    (20 Nov: the WW2 loan video measured 1.5 LU loudness range, every line the same level = flat).
  Punctuation is part of the acting: "!" lifts energy, "..." makes a hesitation, "?" rises.
  A plain row (no |) is read at 1.0 with a 0.2 s pause. Numbers as words. Rows starting with # are notes.

Voices:
  E  0.6 bm_george + 0.4 bm_lewis                      (Eps 07-19)
  F  0.4 bm_george + 0.25 bm_lewis + 0.35 bm_fable     (from Ep 20, pending approval): same pitch (126 vs 130 Hz
     median), about 15% more pitch movement (3.76 vs 3.26 semitones sd on the same lines, 20 Nov test).

Loudness: the old single-pass loudnorm (dynamic mode) flattened every line to one level. Now: EQ, then one linear
gain to -14 LUFS, then a peak limiter, so the per-line gains stay audible.
Needs: pip install --break-system-packages kokoro-onnx soundfile pyloudnorm; model files in ~/voice
(kokoro-v1.0.onnx, voices-v1.0.bin from github.com/thewh1teagle/kokoro-onnx releases, model-files-v1.0).
"""
import sys, os, subprocess, tempfile, numpy as np, soundfile as sf, pyloudnorm as pyln
from kokoro_onnx import Kokoro

args = [a for a in sys.argv[1:]]
VOICE = 'E'
if '--voice' in args:
    i = args.index('--voice'); VOICE = args[i + 1].upper(); del args[i:i + 2]
SRC, OUT = args[0], args[1]
V = os.path.expanduser('~/voice')
k = Kokoro(f'{V}/kokoro-v1.0.onnx', f'{V}/voices-v1.0.bin')
g = k.get_voice_style
BLENDS = {'E': lambda: 0.6 * g('bm_george') + 0.4 * g('bm_lewis'),
          'F': lambda: 0.4 * g('bm_george') + 0.25 * g('bm_lewis') + 0.35 * g('bm_fable')}
style = BLENDS[VOICE]()
EQ = 'highpass=f=60,equalizer=f=3000:t=q:w=1:g=1.5'
parts = []
for row in open(SRC):
    row = row.strip()
    if not row or row.startswith('#'): continue
    f = row.split('|') if row.count('|') >= 2 else ['1.0', '0.2', row]
    speed, pause, text = f[0], f[1], f[2]
    gain = float(f[3]) if len(f) > 3 and f[3].strip() else 0.0
    a, sr = k.create(text.replace('*', ''), voice=style, speed=float(speed), lang='en-gb')
    n = int(.008 * sr); a = a.copy(); a[:n] *= np.linspace(0, 1, n); a[-n:] *= np.linspace(1, 0, n)
    parts += [a * 10 ** (gain / 20), np.zeros(int(float(pause) * sr), np.float32)]
raw, eq = tempfile.mktemp(suffix='.wav'), tempfile.mktemp(suffix='.wav')
sf.write(raw, np.concatenate(parts), 24000, subtype='FLOAT')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', EQ, '-ar', '44100', '-c:a', 'pcm_f32le', eq], check=True)
x, sr = sf.read(eq)
gain_db = -14.0 - pyln.Meter(sr).integrated_loudness(x)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', eq, '-af',
                f'volume={gain_db:.2f}dB,alimiter=limit=0.84:attack=3:release=60:level=disabled', '-b:a', '256k', OUT], check=True)
for p in (raw, eq): os.remove(p)
d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', OUT], capture_output=True, text=True).stdout)
e = subprocess.run(['ffmpeg', '-i', OUT, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
lra = e.split('LRA:')[-1].split('LU')[0].strip() if 'LRA:' in e else '?'
print(f'{OUT}: {d:.1f} s, voice {VOICE}, loudness range {lra} LU' + ('' if 61 <= d <= 68 else '  (aim 61-68 s: adjust speeds or pauses)'))
