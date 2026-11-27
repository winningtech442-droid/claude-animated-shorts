# audio/sfxcore.py
"""Core of the synthesized SFX kit (numpy + scipy). Extend per episode; every sound is placed on a visual event."""
import numpy as np
from scipy import signal as ss

SR = 48000
rng = np.random.default_rng(7)
n_of = lambda s: int(round(s * SR))
tvec = lambda n: np.arange(n) / SR
db = lambda x: 10 ** (x / 20)
noise = lambda n: rng.standard_normal(n)
def filt(x, kind, f, order=2): return ss.sosfilt(ss.butter(order, f, kind, fs=SR, output="sos"), x)
lpf = lambda x, f: filt(x, "lowpass", f)
hpf = lambda x, f: filt(x, "highpass", f)
bpf = lambda x, lo, hi: filt(x, "bandpass", [lo, hi])
def sweep(f0, f1, dur):  # exponential glide, phase-continuous
    t = tvec(n_of(dur)); return np.sin(2 * np.pi * np.cumsum(f0 * (f1 / f0) ** (t / dur)) / SR)


def ping(f=1318.5, ring=1.4, fifth=True):
    """signature ping: sine dyad a perfect fifth apart, 4 ms attack, long ring. Match it to the chord underneath."""
    t = tvec(n_of(ring)); env = np.minimum(1, t / 0.004) * np.exp(-t / (ring / 4))
    return (np.sin(2 * np.pi * f * t) + (0.7 * np.sin(2 * np.pi * f * 1.5 * t) if fifth else 0)) * env


def riser(dur=1.6, f0=680, f1=940):
    """two sine glides up a 4th-6th, second voice enters late; END it on the reveal frame: place(buf, r, t_reveal - dur)"""
    n = n_of(dur); t = tvec(n)
    a = sweep(f0, f1, dur); b = np.concatenate([np.zeros(n - n_of(dur * 0.6)), sweep(f0 * 0.88, f1 * 0.88, dur * 0.6)])
    return (a + 0.7 * b[:n]) * (t / dur) ** 2


def whoosh(dur=1.8):
    """noise swell 0.3-6 kHz (rise ~55%, fall ~45%) + 90->35 Hz sub drop at the peak. Only on big scale moves."""
    n = n_of(dur); t = tvec(n); u = t / dur
    env = np.where(u < 0.55, (u / 0.55) ** 2, np.exp(-(u - 0.55) * 7))
    air = bpf(noise(n), 300, 6000) * env
    sub = np.concatenate([np.zeros(n_of(dur * 0.55)), sweep(90, 35, dur * 0.45) * np.exp(-tvec(n - n_of(dur * 0.55)) / 0.25)])[:n]
    return 0.6 * air + 0.9 * sub


def sonar(f=1500, dur=1.6):
    t = tvec(n_of(dur))
    return (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.35) + 0.25 * np.sin(3 * np.pi * f * t) * np.exp(-t / 0.15)) * np.minimum(1, t / 0.004)


def wash(dur=3.5):
    """band noise 100 Hz-2 kHz, 1 s in / 1 s out: the 'another problem' beat, through the cut"""
    n = n_of(dur); t = tvec(n)
    return bpf(noise(n), 100, 2000) * np.minimum(1, np.minimum(t, dur - t) / 1.0)


def blip(f=1760, dur=0.07, tau=0.03):
    t = tvec(n_of(dur)); return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t / tau) * np.minimum(1, t / 0.0015)


def place(buf, sig, t, gain=1.0, pan=0.0):
    """add a mono/stereo signal into a stereo buffer at t seconds (equal-power pan -1..1)"""
    i = int(round(t * SR))
    if sig.ndim == 1:
        sig = np.vstack([sig * np.cos((pan + 1) * np.pi / 4), sig * np.sin((pan + 1) * np.pi / 4)]) * 1.414
    if i < 0: sig, i = sig[:, -i:], 0
    n = min(sig.shape[1], buf.shape[1] - i)
    if n > 0: buf[:, i:i + n] += sig[:, :n] * gain
