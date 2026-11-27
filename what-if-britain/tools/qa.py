"""The final check before posting (STUDIO-RULES.md, section 6).

usage: python3 -I tools/qa.py out/<id>.mp4 [--demo]
Measures: length (61-80 s; --demo skips this), black frames, frozen stretches, one-frame pops, loudness and
true peak, then prints the Creator Rewards checklist to tick by hand. Exit code 1 if a measured check fails.
"""
import json, re, subprocess, sys
import numpy as np

path = sys.argv[1]; demo = '--demo' in sys.argv
fails, notes = [], []
run = lambda args: subprocess.run(args, capture_output=True, text=True)

info = json.loads(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height,r_frame_rate,nb_frames',
                       '-of', 'json', path]).stdout)
dur = float(info['format']['duration'])
v = next(s for s in info['streams'] if s['codec_type'] == 'video')
has_audio = any(s['codec_type'] == 'audio' for s in info['streams'])
notes.append(f"{v['width']}x{v['height']}, {dur:.2f} s, audio {'yes' if has_audio else 'NO'}")
if (v['width'], v['height']) not in [(1080, 1920), (1440, 2560)]: fails.append(f"size {v['width']}x{v['height']}: must be vertical 1080x1920 or 1440x2560")
if not demo and not 61 <= dur <= 80: fails.append(f'length {dur:.1f} s: must be 61-80 s (under 60 s earns nothing)')
if not has_audio: fails.append('no audio track')

# black frames and frozen stretches
log = run(['ffmpeg', '-hide_banner', '-i', path, '-vf', 'blackdetect=d=0.1:pix_th=0.06,freezedetect=n=0.002:d=1.2', '-an', '-f', 'null', '-']).stderr
for m in re.finditer(r'black_start:([\d.]+) black_end:([\d.]+)', log): fails.append(f'black frames {float(m[1]):.2f}-{float(m[2]):.2f} s')
for m in re.finditer(r'freeze_start: ([\d.]+)', log): fails.append(f'frozen picture from {float(m[1]):.2f} s (over 1.2 s): the camera must keep moving')

# one-frame pops: a frame unlike both neighbours while the neighbours match each other
p = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vf', 'scale=54:96,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
f = np.frombuffer(p, np.uint8).reshape(-1, 96, 54).astype(float)
d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
fps = 30.0
for i in range(1, len(d)):
    if d[i - 1] > 18 and d[i] > 18 and np.abs(f[i + 1] - f[i - 1]).mean() < 6:
        fails.append(f'one-frame pop at {i / fps:.2f} s')
notes.append(f'{len(f)} frames; held-still share {100 * (d < 0.6).mean():.0f}% (rule: camera always moving)')

# loudness
if has_audio:
    e = run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', e)[-1]); TP = float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', e)[-1])
    notes.append(f'loudness {I:.1f} LUFS, true peak {TP:.1f} dBTP')
    if abs(I + 14) > 1.0: fails.append(f'loudness {I:.1f} LUFS: target -14 (within 1)')
    if TP > -1.0: fails.append(f'true peak {TP:.1f} dBTP: keep under -1.0')

print('\n'.join('  ' + n for n in notes))
print('\n'.join('  FAIL ' + x for x in fails) if fails else '  measured checks: PASS')
print("""
Tick by hand before posting:
  [ ] 100% original: our cast, scripts, sets; no clips, news footage or others' material
  [ ] AI-generated content label switched on
  [ ] framed as hypothetical; every real fact sourced in the caption
  [ ] history, not advice; no real people depicted; no party-political take
  [ ] UK spelling and pounds; posting 6-9 pm UK time
  [ ] every sign, tag and headline fully readable in the stills (none cut off at the frame edge)
  [ ] voice made on a MiniMax plan that allows commercial use
  [ ] the ask matches CTA-BANK.md's rotation log, and the log row is filled in""")
sys.exit(1 if fails else 0)
