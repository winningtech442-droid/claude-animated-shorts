# audio/mix.py
"""Mix voice + music + SFX (+ beds) and master to -14 LUFS.

usage: python3 -I audio/mix.py --vo vo.mp3 --music out/audio/music.wav --sfx out/audio/sfx.wav \
         [--beds out/audio/beds.wav] --len 104.4 --out out/audio/mix.wav

Levels that worked on every episode: VO -16 LUFS (HPF 80, +1.5 dB @170 Hz, +2 dB @3.2 kHz, 3:1),
music -23.5 LUFS ducked 6 dB under speech, SFX -27.5 ducked 3.5 dB, beds -31, master -14 LUFS with an
ffmpeg alimiter at -1.5 dBFS (pedalboard's Limiter normalizes to 0 dBFS, don't use it).
"""
import argparse, json, subprocess, tempfile, os
import numpy as np, soundfile as sf, pyloudnorm as pyln, pedalboard as pb

SR = 48000
ap = argparse.ArgumentParser()
ap.add_argument("--vo", required=True); ap.add_argument("--music", required=True); ap.add_argument("--sfx", required=True)
ap.add_argument("--beds"); ap.add_argument("--len", type=float, required=True); ap.add_argument("--out", required=True)
ap.add_argument("--music-lufs", type=float, default=-23.5); ap.add_argument("--sfx-lufs", type=float, default=-27.5)
ap.add_argument("--beds-lufs", type=float, default=-31.0); ap.add_argument("--target", type=float, default=-14.0)
a = ap.parse_args()
N = int(a.len * SR)
meter = pyln.Meter(SR)


def load(path, stereo=True):
    tmp = tempfile.mktemp(suffix=".wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-ar", str(SR), "-ac", "2" if stereo else "1", "-c:a", "pcm_f32le", tmp], check=True)
    x, _ = sf.read(tmp, always_2d=True); os.remove(tmp)
    x = x.T
    return np.pad(x, ((0, 0), (0, max(0, N - x.shape[1]))))[:, :N]


def to_lufs(x, target):
    l = meter.integrated_loudness(x.T)
    return x * 10 ** ((target - l) / 20) if np.isfinite(l) else x  # silence stays silence


vo = load(a.vo, stereo=False)
vo = pb.Pedalboard([pb.HighpassFilter(80), pb.PeakFilter(170, 1.5, 0.8), pb.PeakFilter(3200, 2.0, 0.8),
                    pb.Compressor(threshold_db=-24, ratio=3, attack_ms=5, release_ms=120)])(vo.astype(np.float32), SR).astype(np.float64)
vo = to_lufs(vo, -16.0)
mus = to_lufs(pb.Pedalboard([pb.HighpassFilter(28)])(load(a.music).astype(np.float32), SR).astype(np.float64), a.music_lufs)
sfx = to_lufs(load(a.sfx), a.sfx_lufs)
beds = to_lufs(load(a.beds), a.beds_lufs) if a.beds else np.zeros_like(sfx)

# speech envelope -> ducking gain (40 ms attack, 350 ms release)
w = int(0.02 * SR)
rdb = 20 * np.log10(np.sqrt(np.convolve(vo[0] ** 2, np.ones(w) / w, mode="same")) + 1e-9)
env = np.clip((rdb + 48) / 16, 0, 1)
k = int(0.01 * SR)
blocks = env[: len(env) // k * k].reshape(-1, k).max(axis=1)
sm, v = np.zeros_like(blocks), 0.0
aa, ar = np.exp(-0.01 / 0.04), np.exp(-0.01 / 0.35)
for i, e in enumerate(blocks):
    c = aa if e > v else ar
    v = c * v + (1 - c) * e; sm[i] = v
sm = np.interp(np.arange(N), np.arange(len(sm)) * k + k / 2, sm)
mix = np.vstack([vo[0], vo[0]]) + mus * 10 ** (-6.0 * sm / 20) + sfx * 10 ** (-3.5 * sm / 20) + beds

pre = tempfile.mktemp(suffix=".wav")
gain_db = a.target - meter.integrated_loudness(mix.T)
for _ in range(3):  # gain -> limiter -> re-measure (limiting eats a little loudness)
    sf.write(pre, (mix * 10 ** (gain_db / 20)).T.astype(np.float32), SR, subtype="FLOAT")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", pre, "-af",
                    "alimiter=limit=0.84:attack=3:release=60:level=disabled", "-c:a", "pcm_s24le", a.out], check=True)
    out, _ = sf.read(a.out, always_2d=True)
    lufs = meter.integrated_loudness(out)
    if abs(lufs - a.target) < 0.15: break
    gain_db += a.target - lufs
os.remove(pre)
speech = sm > 0.6
def lvl(x): return meter.integrated_loudness(np.atleast_2d(x)[:, speech].T)  # K-weighted, speech only
print(json.dumps({"lufs": round(lufs, 2), "peak_dbfs": round(20 * np.log10(np.abs(out).max()), 2),
                  "voice_over_music_db": round(lvl(vo[0]) - lvl(mus * 10 ** (-6.0 * sm / 20)), 1),
                  "voice_over_sfx_db": round(lvl(vo[0]) - lvl(sfx * 10 ** (-3.5 * sm / 20)), 1), "out": a.out}))
