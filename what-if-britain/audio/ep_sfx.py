"""Effects-only sound for the 11 Nov episodes (Ep 09, Ep 10): every sound sits on something that happens on screen. No music
(the user adds a library track inside TikTok at 5-8%). The effects stem is mixed far below the narrator.
usage: python3 -I audio/ep_sfx.py ep09 out/ep09/vo.mp3 out/ep09/mix.wav [len_seconds]"""
import subprocess, sys
import numpy as np, soundfile as sf, pyloudnorm as pyln
sys.path.insert(0, 'audio')
from sfxcore import SR, n_of, tvec, bpf, lpf, hpf, noise, blip, ping, place, sweep

EP, VO, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
LEN = float(sys.argv[4]) if len(sys.argv) > 4 else 64.2
buf = np.zeros((2, n_of(LEN + 1)))
def cue(sig, t, g=1.0, pan=0.0): place(buf, sig, t, g, pan)

# ---------- the kit ----------
def env_ad(n, a, d): t = tvec(n); return np.minimum(1, t / a) * np.exp(-t / d)
def step(heavy=1.0):
    n = n_of(0.16); t = tvec(n)
    return heavy * (1.2 * np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.035) + 0.5 * bpf(noise(n), 300, 3500) * env_ad(n, 0.004, 0.03))
def rustle(d=0.4, bright=1.0):
    n = n_of(d); t = tvec(n); e = np.sin(np.pi * t / d) ** 1.5 * (0.6 + 0.4 * np.abs(np.sin(t * 37)))
    return bpf(noise(n), 1200, 5500 * bright) * e
def breath(d, lo, hi, rise):
    n = n_of(d); t = tvec(n); u = t / d
    return bpf(noise(n), lo, hi) * (np.sin(np.pi * u) ** 1.2) * ((0.3 + 0.7 * u) if rise else (1.0 - 0.6 * u))
def thunk(f0=120, f1=55, d=0.6):
    n = n_of(d); t = tvec(n); fr = np.interp(t, [0, 0.15], [f0, f1])
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / 0.18) + 0.25 * bpf(noise(n), 60, 400) * np.exp(-t / 0.05)
def bubble(f=880):
    n = n_of(0.18); t = tvec(n); fr = f * (1 + 0.35 * np.minimum(1, t / 0.05))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * env_ad(n, 0.006, 0.05)
def crack():
    n = n_of(0.5); t = tvec(n)
    return hpf(noise(n), 2500) * np.exp(-t / 0.025) + sum(np.sin(2 * np.pi * f * t) * np.exp(-t / 0.12) for f in (3100, 4270, 5650)) * 0.15
def shimmer(d=1.6):
    n = n_of(d); t = tvec(n)
    return sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate((1318.5, 1975.5, 2637.0, 3136.0))) * np.minimum(1, t / 0.25) * np.exp(-t / 0.6) * 0.25
def whoomph(d=0.9):
    n = n_of(d); t = tvec(n); return (lpf(noise(n), 400) * np.exp(-t / 0.3) + np.sin(2 * np.pi * np.cumsum(np.interp(t, [0, d], [90, 40])) / SR) * np.exp(-t / 0.35))
def sand(d):
    n = n_of(d); return hpf(noise(n), 3500) * 0.5 * np.minimum(1, np.minimum(tvec(n), d - tvec(n)) / 0.2)
def clunk(f=180):
    n = n_of(0.35); t = tvec(n); return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.07) + 0.4 * bpf(noise(n), 200, 2500) * np.exp(-t / 0.02)
def clink():
    n = n_of(0.5); t = tvec(n); return (np.sin(2 * np.pi * 2900 * t) + 0.5 * np.sin(2 * np.pi * 4300 * t)) * np.exp(-t / 0.09)
def hum(d, f=96):
    n = n_of(d); t = tvec(n); return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t)) * np.minimum(1, np.minimum(t, d - t) / 0.15) * (0.7 + 0.3 * np.sin(2 * np.pi * 7 * t))
def whoosh(d=0.7):
    n = n_of(d); t = tvec(n); return bpf(noise(n), 500, 4500) * np.sin(np.pi * t / d) ** 2
def tick(f=1500): return blip(f, 0.03, 0.012)
def fps(t0, t1, hz, heavy=0.8, pan=0.0, g=0.5):  # footsteps at a rate
    t = t0; i = 0
    while t < t1:
        cue(step(heavy), t, g, pan=-0.25 if i % 2 == 0 else 0.25); t += 1 / hz; i += 1

# ---------- the cue lists (absolute seconds = shot start + local time) ----------
def ep09():
    fps(0.15, 4.1, 3.6, 0.6, g=0.42)                       # s1 Nan sprints
    cue(rustle(0.5, 0.9), 0.8, 0.2); cue(rustle(0.5, 0.9), 2.6, 0.2)
    cue(whoosh(1.2), 1.6, 0.12)                              # tape sliding away
    cue(breath(0.7, 700, 3800, True), 4.5, 0.4); cue(breath(0.9, 250, 1800, False), 5.3, 0.4)   # s2 panting
    cue(rustle(0.45, 0.8), 4.7, 0.2); cue(bubble(740), 5.9, 0.12)
    fps(7.5, 9.9, 2.4, 0.5, g=0.3)                          # s3 stroll
    cue(clink(), 8.45, 0.25); cue(rustle(0.3, 1.4), 8.5, 0.15)   # the 2010 card flips
    cue(shimmer(1.0), 9.05, 0.16); cue(whoosh(0.5), 9.1, 0.14)     # through the tape
    for t in (11.88, 12.88, 13.58): cue(thunk(140, 60), t, 0.8); cue(rustle(0.3, 0.8), t + 0.1, 0.22)   # s4: the line moves
    cue(rustle(0.7, 0.6), 15.0, 0.22); cue(bubble(988), 15.3, 0.28)       # s5 thought
    cue(breath(1.2, 250, 1800, False), 16.8, 0.45)
    fps(18.2, 22.6, 3.2, 0.4, g=0.3); cue(bubble(1400), 19.2, 0.1); cue(bubble(1500), 20.8, 0.1)   # c1 stuck jogging; kids
    cue(step(0.5), 23.4, 0.3); cue(breath(0.5, 500, 3000, True), 23.9, 0.4); cue(clunk(260), 24.4, 0.25)   # c2 knees
    cue(rustle(0.6, 0.5), 24.9, 0.2)
    cue(rustle(0.8, 1.6), 27.8, 0.18); cue(rustle(0.8, 1.6), 29.2, 0.18)                    # c3 ticket flutter
    cue(rustle(0.4, 1.0), 30.0, 0.3); cue(whoosh(0.5), 30.1, 0.18); cue(breath(0.9, 250, 1800, False), 30.9, 0.35)
    cue(sand(2.8), 32.2, 0.4); cue(tick(), 35.0, 0.3)                              # c4a hourglass
    cue(hum(1.7, 96), 35.25, 0.35); [cue(tick(1100), 35.4 + i * 0.22, 0.12) for i in range(7)]   # c4b the press
    cue(clunk(120), 36.9, 0.6)
    cue(crack(), 37.85, 0.6)                                                                # the crack
    cue(shimmer(), 38.27, 0.55); cue(whoomph(), 38.25, 0.5)                                 # the flash
    fps(38.5, 39.4, 3.6, 0.7, g=0.35); cue(crack(), 39.2, 0.3); cue(rustle(0.5, 1.0), 39.5, 0.3)   # w1 bursts through
    for i in range(7): cue(ping(880 * 2 ** (i / 12), 0.7), 41.0 + i * 0.27, 0.16, pan=-0.3 + i * 0.1)   # w2: seven years
    for i in range(14): cue(blip(1900 + 40 * i, 0.05, 0.02), 41.9 + i * 0.09, 0.14)
    for i in range(14): cue(blip(2300 + 30 * i, 0.05, 0.02), 43.3 + i * 0.07, 0.16, pan=-0.4)
    cue(rustle(0.5, 1.3), 43.9, 0.2); cue(thunk(100, 50), 44.3, 0.35)
    for t in np.arange(45.8, 48.4, 0.3): cue(rustle(0.22, 1.5), t, 0.1, pan=np.sin(t * 5) * 0.6)    # w3 pages
    cue(clink(), 47.9, 0.2)
    cue(ping(1046.5, 1.4), 49.7, 0.22)                                                   # w4: most of those
    fps(50.4, 51.5, 3.0, 0.6, g=0.3); cue(rustle(0.6, 0.8), 51.7, 0.3)
    cue(shimmer(1.0), 53.5, 0.16); cue(rustle(0.4, 0.8), 53.9, 0.2)                       # w5
    cue(clunk(200), 56.55, 0.3); cue(rustle(0.4, 1.4), 56.6, 0.2)                          # w6 wallet
    cue(clink(), 59.2, 0.25); cue(breath(0.5, 500, 2500, False), 59.6, 0.15)               # w7
    cue(whoosh(0.6), 61.2, 0.15); cue(blip(1200, 0.12, 0.05), 61.25, 0.4); cue(whoosh(0.7), 61.6, 0.2)   # end card + phone
    cue(blip(1600, 0.1, 0.04), 62.5, 0.3)
    # silence: the world stops before the crack (room tone drops out 37.0-38.3)
    return [(37.0, 38.3)]


def ep10():
    fps(0.1, 3.3, 3.0, 0.5, g=0.35); fps(0.0, 3.4, 3.8, 0.5, g=0.22, pan=-0.3); cue(hum(3.4, 70), 0.0, 0.18)   # s1 belt hum, walk off, Mate runs
    cue(rustle(0.5, 0.9), 1.0, 0.18)
    cue(rustle(0.45, 1.0), 4.0, 0.25); cue(rustle(0.4, 1.0), 4.7, 0.25); cue(breath(0.6, 500, 3000, False), 5.4, 0.3)   # s2 sleeves, brow
    for t in (4.8, 5.1, 5.45, 5.7): cue(clunk(150 + 20 * (t % 3)), t, 0.35)               # machine coughs
    cue(clunk(90), 6.3, 0.7); cue(whoomph(0.7), 6.3, 0.25)                                 # light off
    cue(bubble(988), 7.4, 0.3); cue(breath(1.0, 250, 1800, False), 7.8, 0.35)             # s3 thought
    for t in np.arange(9.1, 11.2, 0.12): cue(blip(180 + 40 * (t % 0.5), 0.02, 0.01), t, 0.15)   # s4 desk rattle
    cue(sand(2.4), 11.5, 0.35); cue(tick(), 11.4, 0.25)                                   # hourglass pour
    for i in range(10): cue(clink(), 14.7 + i * 0.4, 0.14, pan=0.3)                        # s5 coins pile on the boss
    cue(tick(1100), 17.6, 0.4)                                                              # one tiny tick
    for i in range(22): cue(blip(1500 + 25 * i, 0.03, 0.012), 19.2 + i * 0.1, 0.1)         # s6 line draws
    cue(thunk(110, 55), 20.45, 0.7)                                                         # 2008 marker
    for i in range(14): cue(ping(900 + 40 * i, 0.5), 24.0 + i * 0.18, 0.13, pan=(i % 3 - 1) * 0.3)   # s7 coins
    cue(sand(0.6), 25.0, 0.1)
    cue(rustle(0.4, 1.0), 27.7, 0.2); cue(bubble(660), 28.3, 0.2); cue(rustle(0.7, 1.6), 28.8, 0.22)   # s8 mug sip, shrug
    for t in (30.4, 31.6, 32.9): cue(blip(260, 0.14, 0.05), t, 0.22); cue(blip(330, 0.1, 0.04), t + 0.1, 0.18)   # s9 stiff laugh
    for t in (30.2, 30.55, 30.9, 31.25, 31.6, 31.95, 32.3, 32.65): cue(tick(1200), t, 0.1)   # HUSTLE flashes
    fps(33.9, 35.5, 3.6, 0.6, g=0.3); cue(whoosh(0.5), 35.6, 0.2)                           # s10 chase
    for i in range(24): cue(rustle(0.25, 1.5), 35.9 + i * 0.07, 0.09, pan=np.sin(i) * 0.5)  # email flood
    cue(thunk(100, 50), 37.3, 0.4)
    cue(crack(), 37.1, 0.6)                                                                  # the crack in the pause
    cue(shimmer(), 38.15, 0.55); cue(whoomph(), 38.1, 0.5)                                   # flash
    cue(hum(1.5, 110), 38.3, 0.3); cue(bubble(1200), 38.9, 0.2); cue(clink(), 39.1, 0.2)   # s11 machine whirrs
    for i in range(12): cue(ping(660 * 2 ** (i / 12), 0.6), 40.0 + i * 0.22, 0.12, pan=-0.3 + i * 0.05)   # s12 rising
    for i in range(18): cue(clink(), 42.9 + i * 0.05, 0.12, pan=(i % 3 - 1) * 0.3)         # s13 coins land
    cue(ping(1046.5, 1.2), 43.8, 0.22)
    cue(clink(), 45.9, 0.25); cue(rustle(0.4, 1.4), 46.1, 0.25); cue(blip(1000, 0.08, 0.03), 46.5, 0.25)   # s14 envelope closes
    cue(rustle(0.8, 0.5), 47.4, 0.2); cue(clunk(160), 47.5, 0.2); fps(48.1, 48.8, 4.0, 0.6, g=0.25, pan=0.2)   # s15 deckchair, Mate runs past
    cue(bubble(500), 48.9, 0.2)
    cue(crack(), 49.65, 0.3); cue(shimmer(1.0), 49.75, 0.16)                                  # reverse flash
    for a, b in ((50.0, 51.8), (51.2, 53.0), (52.4, 54.2)): fps(a, b, 2.6, 0.4, g=0.2, pan=0.2)
    for t in (51.9, 53.1, 54.3): cue(thunk(90, 50), t, 0.3); cue(rustle(0.3, 0.6), t, 0.15)    # briefcases drop
    cue(bubble(740), 55.8, 0.25); fps(55.9, 57.5, 1.6, 0.3, g=0.22)                           # s17 off the board
    fps(58.0, 59.8, 3.5, 0.5, g=0.3); cue(clunk(100), 60.15, 0.5); cue(breath(0.9, 250, 1800, False), 60.3, 0.3)   # s18 hollow
    cue(bubble(880), 61.4, 0.2); cue(bubble(1010), 61.9, 0.18); cue(rustle(0.4, 1.0), 61.5, 0.15)   # s19 kettle
    cue(clunk(200), 63.5, 0.35); cue(shimmer(1.0), 64.1, 0.2); fps(64.4, 65.6, 2.8, 0.4, g=0.25)   # s20 bar clunk, pin
    cue(whoosh(0.6), 66.2, 0.15); cue(blip(1200, 0.12, 0.05), 66.25, 0.4); cue(whoosh(0.7), 66.7, 0.2)   # end card
    cue(blip(1600, 0.1, 0.04), 67.6, 0.3)
    return [(37.35, 38.1)]

def ep11():
    cue(crack(), 0.35, 0.35)                                                                 # the what-if crack
    cue(hum(3.4, 60), 0.0, 0.14); cue(clunk(110), 4.0, 0.22)                                  # lid hovers, creaks
    for t in np.arange(0.3, 21.4, 0.21): cue(clink(), t + 0.07 * np.sin(t * 9), 0.05 + 0.03 * (t > 12), pan=np.sin(t * 5) * 0.4)   # coin rain into the jar
    cue(breath(1.0, 400, 2500, False), 5.75, 0.22); cue(bubble(500), 6.85, 0.2); cue(clink(), 7.35, 0.2)   # Mate: milk first, then tea
    cue(ping(1046.5, 0.8), 8.6, 0.28); cue(shimmer(1.0), 8.62, 0.2)                          # TAX-FREE sign lights
    cue(shimmer(1.4), 10.0, 0.25); cue(whoosh(1.5), 12.9, 0.1)                                # shield coin, crane up
    for i in range(5): cue(tick(1500 + 120 * i), 14.9 + 0.3 * i, 0.1)                        # neighbours' jars
    cue(hum(2.4, 55), 19.3, 0.22)                                                             # tension under the lid
    for i in range(14): cue(tick(1200 + 40 * i), 19.4 + 2.2 * (i / 14) ** 0.7, 0.14)         # accelerating ticks
    cue(clunk(70), 21.7, 0.9); cue(thunk(100, 45, 0.8), 21.7, 0.8); cue(ping(300, 1.2), 21.72, 0.35)   # THE SLAM
    for k in range(34): cue(clink(), 22.55 + 0.19 * k, 0.11, pan=(hash(k) % 3 - 1) * 0.3 if False else ((k % 3) - 1) * 0.3)   # extra coins land on the lid
    cue(whoosh(0.8), 28.1, 0.08); cue(whoomph(0.7), 30.0, 0.18)                               # they roll away, out of the light
    cue(sand(1.0), 32.3, 0.2); cue(clunk(160), 33.4, 0.3)                                     # Mate shoves
    cue(bubble(420), 33.85, 0.5); cue(bubble(630), 33.95, 0.3)                                # boing: it doesn't fit
    for i in range(5): cue(tick(1800), 37.5 + 0.12 * i, 0.16)                                # CASH ISA stickers pop
    for i in range(5): cue(ping(660 * 2 ** (i * 2 / 12), 0.5), 40.2 + 0.5 * i, 0.26, pan=-0.4 + 0.2 * i)   # five jars light up
    cue(hum(0.6, 150), 42.7, 0.35); cue(ping(880, 0.8), 42.7, 0.3)                            # stuck + 1 IN 5
    cue(tick(1400), 48.4, 0.25)
    cue(shimmer(1.4), 53.0, 0.5); cue(whoomph(1.0), 53.0, 0.3)                                # back to warm daylight
    cue(hum(1.8, 70), 54.9, 0.3)
    for i in range(16): cue(tick(1000 + 60 * i), 54.9 + 1.8 * (i / 16) ** 0.8, 0.12)         # the lid shudders
    cue(whoosh(1.6), 56.7, 0.5); cue(whoomph(1.2), 56.7, 0.4); cue(breath(1.8, 300, 3000, False), 56.8, 0.2)   # blast off
    cue(ping(1318.5, 0.4), 58.9, 0.16); cue(rustle(0.4, 1.0), 61.5, 0.18)
    cue(whoosh(0.6), 65.3, 0.15); cue(blip(1200, 0.12, 0.05), 65.35, 0.4); cue(whoosh(0.7), 65.8, 0.2); cue(blip(1600, 0.1, 0.04), 66.8, 0.3)   # end card
    return [(21.76, 22.25)]

def ep13():
    cue(crack(), 0.35, 0.35); cue(whoosh(0.6), 0.1, 0.18); cue(hum(3.3, 60), 0.0, 0.14)          # the what-if crack; Alfie trips over the wire
    for k in range(11): cue(clink(), 0.35 + 0.2 * k, 0.1, pan=((k % 3) - 1) * 0.3)                # coins spill from his pockets
    cue(hum(2.5, 110), 3.4, 0.1)                                                                  # the wire runs across the floor
    for i in range(5): cue(tick(1500 + 100 * i), 6.1 + 0.4 * i, 0.12, pan=-0.5 + 0.25 * i)         # five savers, five wires
    for t in np.arange(8.5, 10.3, 0.07): cue(clink(), t + 0.02 * np.sin(t * 9), 0.06, pan=np.sin(t * 5) * 0.4)   # the interest piles up
    cue(ping(1046.5, 0.8), 10.6, 0.28); cue(shimmer(1.2), 10.62, 0.2)                              # under the wire is yours
    cue(ping(880, 0.7), 12.85, 0.3); cue(tick(1200), 12.9, 0.2)                                    # the GBP1,000 plate
    cue(sand(1.4), 16.0, 0.14); cue(rustle(0.5, 1.4), 16.4, 0.3); cue(ping(660, 0.5), 16.65, 0.2)   # 2016 page tears, dust gathers
    for i in range(12): cue(tick(1000 + 70 * i), 19.4 + 2.2 * (i / 12) ** 0.7, 0.13)               # rates start to rise
    cue(whoosh(0.9), 21.5, 0.12)
    for t in np.arange(22.7, 26.0, 0.55): cue(tick(800), t, 0.07)                                  # slow clock: rates were so low
    cue(breath(1.4, 250, 1500, False), 23.5, 0.16)                                                 # the clerk yawns
    cue(thunk(100, 55, 0.6), 26.9, 0.5); cue(whoosh(1.3), 26.9, 0.2)                               # needle slams up
    for t in np.arange(27.0, 28.9, 0.045): cue(clink(), t, 0.05, pan=np.sin(t * 7) * 0.4)          # the pile grows taller
    cue(hum(3.2, 55), 29.5, 0.2); cue(clunk(90), 30.2, 0.2)                                        # the wire holds, the pile pokes through
    cue(thunk(110, 50, 0.6), 33.85, 0.55); cue(clink(), 33.9, 0.2)                                 # the money bag lands
    for i in range(14): cue(tick(1100 + 50 * i), 36.0 + 2.1 * (i / 14) ** 0.7, 0.13)               # tension
    cue(ping(196, 1.2), 39.97, 0.5); cue(crack(), 39.97, 0.35); cue(whoosh(0.9), 40.0, 0.2)         # the wire snaps taut and slices
    cue(clunk(70), 40.85, 0.8); cue(thunk(100, 45, 0.8), 40.85, 0.7); cue(ping(300, 1.0), 40.88, 0.3)   # the slice drops into TAX
    cue(ping(880, 0.6), 41.4, 0.22); cue(tick(1800), 41.35, 0.2)                                   # the 100-coin board
    cue(rustle(0.35, 1.2), 44.0, 0.25); cue(ping(1318.5, 0.5), 44.05, 0.2)                         # APRIL 2027 page flips in
    cue(ping(784, 0.8), 45.85, 0.3); cue(hum(0.6, 150), 45.85, 0.3)                                # 24p
    for c in range(4):
        for i in range(24): cue(clink(), 45.85 + 1.8 * c + 0.5 + 0.03 * i + 0.6, 0.05, pan=-0.3 + 0.02 * i)   # coins march into the slot
        cue(thunk(110, 70, 0.4), 45.85 + 1.8 * c + 1.3, 0.2)
    cue(shimmer(1.4), 53.6, 0.5); cue(whoomph(1.0), 53.6, 0.3)                                     # back to warm daylight
    cue(hum(3.0, 70), 54.9, 0.18)
    cue(clunk(120), 58.7, 0.2); cue(whoosh(1.0), 58.7, 0.14)                                       # Alfie lifts the wire
    for t in np.arange(58.7, 60.3, 0.08): cue(clink(), t, 0.05, pan=np.sin(t * 6) * 0.4)
    cue(ping(1318.5, 0.6), 60.25, 0.2); cue(shimmer(1.0), 60.3, 0.15)
    cue(rustle(0.4, 1.0), 61.3, 0.16)
    cue(whoosh(0.6), 62.8, 0.15); cue(blip(1200, 0.12, 0.05), 62.85, 0.4); cue(whoosh(0.7), 63.3, 0.2); cue(blip(1600, 0.1, 0.04), 64.3, 0.3)   # end card
    return []


def ep14():
    def rumble(a, b, g=0.35):
        for t in np.arange(a, b, 0.17): cue(thunk(80, 45, 0.3), t, g, pan=-0.2 + 0.4 * ((t * 7) % 1))
    cue(crack(), 0.35, 0.35); cue(whoosh(0.6), 0.1, 0.18); cue(hum(3.0, 60), 0.0, 0.14)         # the what-if crack; the pot bursts in
    rumble(0.0, 1.45, 0.4); cue(thunk(110, 50, 0.6), 1.35, 0.7); cue(rustle(0.4, 1.2), 1.4, 0.25)  # it bumps Alfie
    for k in range(9): cue(clink(), 1.4 + 0.12 * k, 0.1, pan=((k % 3) - 1) * 0.3)                  # coins spill
    rumble(3.2, 4.7, 0.3); cue(clunk(120), 5.7, 0.5)                                                # parks on the mat; the door swings shut
    cue(clunk(160), 6.35, 0.3); cue(tick(1500), 6.6, 0.15); cue(tick(1700), 6.9, 0.15)            # the HOME and SAVINGS crates
    cue(whoosh(0.8), 8.6, 0.12); rumble(9.0, 10.4, 0.3)                                             # the door opens; the pot rolls out
    cue(ping(880, 0.7), 11.85, 0.3); cue(tick(1200), 11.9, 0.2)                                     # the 325,000 plate
    cue(hum(2.5, 90), 16.4, 0.22)                                                                   # the pot hums on the doorstep
    cue(tick(1800), 18.95, 0.25); cue(rustle(0.3, 1.4), 19.0, 0.2)                                  # the child's drawing is pinned
    cue(whoosh(1.4), 21.0, 0.14); cue(ping(1046.5, 0.9), 22.6, 0.3); cue(shimmer(1.0), 22.62, 0.15) # the line stretches to 500,000
    for i in range(12): cue(tick(900 + 60 * i), 23.9 + 1.6 * (i / 12), 0.12)                        # the crates grow
    cue(clunk(140), 25.5, 0.35)
    cue(rustle(0.35, 1.2), 27.1, 0.25); cue(ping(1318.5, 0.5), 27.15, 0.2); rumble(27.1, 28.9, 0.32)   # April 2027; the pot rolls in
    cue(clunk(120), 29.8, 0.5)                                                                      # the door shuts
    cue(whoosh(1.0), 32.9, 0.18); cue(thunk(110, 45, 0.8), 35.0, 0.8); cue(clunk(70), 35.05, 0.6); cue(ping(300, 1.0), 35.1, 0.25)   # the pot lands on the pile
    cue(hum(2.2, 55), 36.1, 0.22)                                                                   # violet zone
    for i in range(4): cue(clink(), 38.9 + 0.28 * i + 0.6, 0.2); cue(thunk(110, 70, 0.4), 38.9 + 0.28 * i + 0.65, 0.3)   # four bars into the letterbox
    cue(ping(784, 0.8), 38.45, 0.3)                                                                 # 40p
    for k in range(8): cue(clink(), 41.6 + 0.3 * k + 0.1, 0.1, pan=-0.3 + 0.1 * k)                  # coins clink out
    cue(thunk(110, 50, 0.6), 44.85, 0.6); cue(clink(), 44.9, 0.2)                                   # the bag lands
    cue(clunk(90), 49.5, 0.4); cue(ping(880, 0.6), 49.55, 0.2)                                      # the line drops back to 325,000
    cue(whoosh(0.8), 52.9, 0.15); cue(thunk(110, 50, 0.6), 53.9, 0.4)                               # the pot hops down
    cue(shimmer(1.4), 55.1, 0.5); cue(whoomph(1.0), 55.1, 0.3)                                      # back to warm daylight
    cue(hum(3.0, 70), 55.2, 0.14)
    cue(ping(1318.5, 0.6), 59.2, 0.2); cue(shimmer(1.0), 59.25, 0.15); cue(rustle(0.4, 1.0), 61.5, 0.16)
    cue(whoosh(0.6), 63.0, 0.15); cue(blip(1200, 0.12, 0.05), 63.05, 0.4); cue(whoosh(0.7), 63.5, 0.2); cue(blip(1600, 0.1, 0.04), 64.5, 0.3)   # end card
    return []

def ep15():
    def pop(t, g=0.3, f=700): cue(blip(f, 0.1, 0.05), t, g); cue(bubble(f), t + 0.01, g * 0.5)
    def coins(a, b, step=0.22, g=0.1):
        for k, t in enumerate(np.arange(a, b, step)): cue(clink(), t, g, pan=((k % 3) - 1) * 0.3)
    pop(0.15); coins(0.4, 1.4, 0.2); cue(thunk(110, 50, 0.6), 1.55, 0.7); cue(rustle(0.4, 1.0), 1.0, 0.18); pop(0.5, 0.2, 500)   # chute, barrier slam
    pop(3.6, 0.3, 500); cue(rustle(0.3, 1.2), 4.6, 0.25); cue(clink(), 5.7, 0.35); pop(5.35, 0.2, 800)                         # boss, slice, pot
    pop(7.4, 0.25, 900); cue(hum(1.8, 90), 7.5, 0.16)                                                                         # label
    pop(9.4, 0.3, 450); cue(clunk(120), 10.95, 0.5); cue(clink(), 10.9, 0.2); pop(11.05, 0.2, 300)                            # claw
    pop(12.05, 0.3, 500); pop(12.2, 0.15, 900); cue(rustle(0.35, 1.0), 12.4, 0.2); cue(rustle(0.35, 1.0), 13.0, 0.2)          # you / boss
    pop(14.5, 0.3, 500); coins(14.7, 15.9, 0.25, 0.1); cue(rustle(0.4, 1.0), 16.1, 0.25)                                       # saved jar
    cue(sweep(0.9, 200, 900) if False else whoosh(0.9), 17.4, 0.15); cue(crack(), 19.0, 0.4); cue(shimmer(1.0), 19.5, 0.3); cue(thunk(100, 45, 0.7), 19.52, 0.8)  # barrier drop, crack, flash
    pop(19.75, 0.3, 1000); cue(rustle(0.3, 1.2), 19.8, 0.2); coins(21.6, 23.5, 0.17, 0.1)
    for i in range(10): cue(tick(1000 + 90 * i), 21.7 + 0.18 * i, 0.12)
    cue(ping(1318.5, 0.6), 23.55, 0.35); pop(24.1, 0.25, 450); pop(24.6, 0.2, 900)                                            # lock chime, claw, SKIPS NI
    pop(26.75, 0.25, 600); cue(whoosh(0.5), 27.6, 0.15); cue(whoosh(0.5), 28.9, 0.12); pop(27.2, 0.2, 900); cue(rustle(0.4, 1.0), 29.3, 0.25)   # Mate and the barrier
    pop(31.1, 0.3, 900); pop(33.2, 0.3, 800); cue(whoosh(0.4), 33.25, 0.2); cue(thunk(110, 55, 0.5), 33.6, 0.5)               # fifty, five
    cue(whoosh(0.7), 34.6, 0.18); cue(ping(880, 0.6), 35.3, 0.2); cue(clink(), 36.4, 0.35); cue(ping(1046.5, 0.6), 36.45, 0.3)  # sails through
    cue(whoosh(0.3), 37.0, 0.2); cue(thunk(120, 40, 0.6), 37.35, 0.8); cue(hum(1.2, 400), 37.4, 0.12); pop(37.9, 0.25, 500)     # slam, red
    pop(39.4, 0.3, 450)
    for t in (39.9, 40.4, 40.9): cue(clunk(110), t + 0.2, 0.45); cue(rustle(0.2, 0.6), t, 0.2)                                 # chomps
    cue(bubble(180), 41.9, 0.5); cue(whoosh(0.7), 42.8, 0.2); pop(43.4, 0.4, 700); cue(thunk(100, 50, 0.4), 43.42, 0.5)       # burp, 240
    cue(whoosh(0.5), 45.4, 0.2); pop(45.6, 0.3, 800); cue(tick(700), 46.05, 0.3); pop(47.0, 0.3, 450); cue(clunk(160), 47.75, 0.5)   # bar, lock snaps
    pop(49.1, 0.3, 500); cue(rustle(0.3, 1.0), 49.7, 0.2); cue(clink(), 50.05, 0.3); pop(50.3, 0.3, 700); cue(breath(0.6, 300, 1500, False), 51.0, 0.2)  # boss, pinch, 450
    cue(whoosh(1.0), 51.5, 0.2); cue(shimmer(0.9), 51.6, 0.15); pop(53.1, 0.3, 500); cue(thunk(110, 50, 0.6), 53.5, 0.9); cue(sand(0.3) if False else rustle(0.3, 1.5), 53.55, 0.2)   # drain, stamp
    pop(55.4, 0.3, 500); cue(whoosh(0.6), 56.3, 0.18); pop(57.0, 0.25, 800); coins(57.15, 58.0, 0.12, 0.12); cue(hum(1.4, 130), 57.2, 0.2)   # jar to pot
    cue(rustle(0.4, 1.0), 59.1, 0.25); cue(rustle(0.4, 1.0), 59.6, 0.2); cue(tick(1500), 60.5, 0.3)                           # tug, freeze
    cue(whoosh(0.6), 62.2, 0.15); cue(blip(1200, 0.12, 0.05), 62.3, 0.4); cue(whoosh(0.7), 62.7, 0.2); pop(63.4, 0.3, 900)   # end card
    return []


def ep16():
    def pop(t, g=0.3, f=700): cue(blip(f, 0.1, 0.05), t, g); cue(bubble(f), t + 0.01, g * 0.5)
    cue(whoosh(0.5), 0.0, 0.2); cue(thunk(110, 50, 0.6), 0.55, 0.7); cue(rustle(0.4, 1.0), 0.1, 0.2); cue(clink(), 0.6, 0.25)             # s1 tag drops
    pop(5.0, 0.3, 600); cue(rustle(0.4, 1.6), 5.7, 0.25); cue(clink(), 6.1, 0.2); cue(whoosh(1.0), 6.0, 0.2); cue(sand(0.5), 6.4, 0.1)    # s2 calendar flips, tag slides away
    cue(clunk(150), 8.3, 0.4)                                                                                                                 # s3 jar tips
    for i in range(8): cue(clink(), 8.5 + i * 0.12, 0.2, pan=-0.4 + i * 0.05)
    cue(breath(0.8, 300, 1800, False), 9.0, 0.25)
    pop(10.25, 0.25, 500); pop(11.2, 0.25, 800); pop(12.6, 0.3, 900); cue(hum(1.4, 110), 12.6, 0.12)                                       # s4 line, 2017, £1,000
    for k, t in enumerate((14.8, 15.45, 16.1, 16.75)): cue(rustle(0.5, 0.9), t, 0.25); cue(whoosh(0.5), t, 0.1); cue(tick(1400 + 100 * k), t + 0.6, 0.35); pop(t + 0.55, 0.15, 1000)   # s5 parcels, stickers
    pop(16.9, 0.35, 450); cue(clunk(120), 16.95, 0.3)
    cue(sand(2.2), 18.6, 0.3); cue(tick(900), 19.8, 0.2)
    for i in range(6): cue(tick(1100 + 40 * i), 20.0 + i * 0.22, 0.1)                                                                         # s6 cobweb, spider drops
    cue(clunk(160), 21.3, 0.25)
    cue(whoosh(0.8), 22.5, 0.25); cue(hum(1.6, 90), 23.0, 0.18)                                                                               # s7 the hand stretches the tape
    for i in range(10): cue(tick(900 + 50 * i), 23.0 + i * 0.16, 0.1)
    cue(thunk(110, 50, 0.5), 25.7, 0.8); pop(25.6, 0.25, 700); pop(27.0, 0.3, 600); cue(shimmer(0.9), 27.05, 0.12)                           # s8 far line lands, APRIL 2027
    cue(crack(), 29.4, 0.6); cue(shimmer(), 29.45, 0.5); cue(whoomph(), 29.4, 0.5); cue(whoosh(0.8), 30.3, 0.25); cue(clink(), 30.55, 0.3)  # s9 switch
    cue(whoomph(1.2), 31.9, 0.4); cue(rustle(0.6, 0.5), 32.1, 0.2)                                                                            # s10 shelves rise
    for i in range(4): cue(bubble(500 + 40 * i), 32.35 + i * 0.15, 0.22)                                                                      # milk first
    for i in range(4): cue(bubble(420 + 30 * i), 33.05 + i * 0.15, 0.2)                                                                       # then tea
    cue(clink(), 33.7, 0.3)
    for t in np.arange(34.5, 36.0, 0.18): cue(rustle(0.2, 1.4), t, 0.14, pan=np.sin(t * 5) * 0.4)                                            # s11 wrapping
    pop(35.95, 0.3, 500); cue(clunk(130), 36.2, 0.3); pop(36.3, 0.3, 700)
    for i in range(9): cue(tick(1500), 37.8 + i * 0.28, 0.16, pan=0.2); cue(whoosh(0.3), 37.85 + i * 0.28, 0.06)                              # s12 knitting
    pop(38.8, 0.25, 450); cue(whoosh(0.5), 39.5, 0.1)
    pop(40.7, 0.25, 600); cue(rustle(0.5, 0.8), 41.2, 0.2); pop(42.0, 0.3, 450); cue(clunk(100), 42.2, 0.4)                                  # s13 trolley to van
    for t in (42.4, 42.8): cue(clunk(80), t, 0.3)
    pop(43.5, 0.3, 400)
    for t in (44.2, 44.6, 45.0, 45.4): cue(tick(1800), t, 0.4); cue(rustle(0.2, 1.4), t, 0.15)                                               # s14 ticks
    cue(shimmer(0.9), 46.0, 0.35); cue(whoosh(1.0), 46.1, 0.25); cue(whoomph(0.9), 46.4, 0.3)                                                # s15 drains, room shrinks
    pop(49.0, 0.3, 800); cue(rustle(0.4, 1.0), 49.1, 0.15)                                                                                    # s16 £3,000
    cue(whoosh(0.6), 51.7, 0.2); cue(clunk(140), 52.3, 0.4); pop(52.2, 0.3, 450); cue(hum(0.8, 300), 52.25, 0.15); pop(52.3, 0.2, 1000)
    cue(rustle(0.5, 1.2), 54.7, 0.2); pop(54.9, 0.4, 350); cue(thunk(100, 50, 0.4), 54.92, 0.5); pop(56.3, 0.25, 700); cue(whoosh(0.8), 56.6, 0.25)   # s17 £400
    pop(58.0, 0.3, 600); cue(rustle(0.4, 1.6), 58.6, 0.25); cue(clink(), 59.0, 0.2)                                                           # s18
    cue(shimmer(1.2), 59.9, 0.25); cue(whoomph(0.8), 59.9, 0.2); pop(60.0, 0.35, 900); cue(ping(1046.5, 1.2), 60.1, 0.25)
    pop(62.3, 0.3, 600); cue(clunk(160), 62.6, 0.3); cue(clunk(160), 63.2, 0.25)                                                              # s19 taps
    cue(whoosh(0.4), 66.0, 0.2); cue(thunk(120, 55, 0.5), 66.4, 0.8); cue(rustle(0.3, 1.5), 66.42, 0.2)                                       # s20 slap
    cue(whoosh(0.6), 70.2, 0.15); cue(blip(1200, 0.12, 0.05), 70.3, 0.4); cue(whoosh(0.7), 70.7, 0.2); pop(71.4, 0.3, 900)                   # end card
    return []


def ep17():
    def pop(t, g=0.3, f=700): cue(blip(f, 0.1, 0.05), t, g); cue(bubble(f), t + 0.01, g * 0.5)
    cue(whoosh(0.9), 0.0, 0.2); cue(rustle(0.8, 1.3), 0.1, 0.25); cue(rustle(0.3, 1.6), 1.0, 0.2)                                       # s1 note flutters into hands
    pop(3.8, 0.3, 600); cue(rustle(0.4, 1.6), 4.6, 0.25); cue(clink(), 5.0, 0.15)                                                         # s2 card flips
    cue(whoosh(0.5), 5.99, 0.25); pop(6.3, 0.3, 500)
    for i in range(6): cue(rustle(0.15, 1.8), 6.6 + i * 0.18, 0.15)                                                                      # s3 note eaten away
    cue(breath(0.7, 300, 1800, True), 7.4, 0.25)
    for i in range(4): pop(8.6 + i * 0.3, 0.25, 600 + 80 * i)                                                                             # s4 houses A-D light
    pop(10.0, 0.25, 450)
    pop(11.3, 0.25, 900); cue(tick(1500), 12.0, 0.3); cue(ping(1318.5, 0.8), 13.3, 0.3); pop(13.3, 0.25, 1100)                           # s5 phone, +£100
    for i in range(24): cue(blip(500 + 30 * (i % 8), 0.05, 0.03), 14.6 + i * 0.06, 0.08, pan=-0.6 + (i % 7) * 0.2)                       # s6 town lights up
    cue(whoosh(1.2), 14.6, 0.15)
    pop(17.7, 0.25, 500); cue(rustle(0.4, 1.0), 19.9, 0.2); pop(19.9, 0.3, 700)                                                          # s7 2022, £150
    cue(whoosh(0.4), 22.4, 0.25); cue(thunk(110, 50, 0.6), 22.8, 0.8); cue(rustle(0.3, 1.2), 22.82, 0.25); pop(23.4, 0.25, 500)          # s8 £400 slams
    cue(sand(0.5), 25.1, 0.15); cue(whoosh(0.5), 25.15, 0.15); pop(25.9, 0.25, 450)                                                       # s9 stack vanishes
    pop(28.0, 0.25, 600)
    cue(sweep(200, 1400, 0.3), 29.15, 0.35); cue(clunk(160), 29.2, 0.3)                                                                    # s10 cap springs
    for i in range(6): cue(tick(1100 + 90 * i), 30.8 + i * 0.12, 0.15)                                                                   # s11 bars
    cue(sweep(300, 1800, 0.5), 32.2, 0.3); cue(thunk(140, 60, 0.4), 32.75, 0.5)
    cue(crack(), 33.85, 0.6); cue(shimmer(), 33.9, 0.5); cue(whoomph(), 33.85, 0.5)                                                       # s12 switch
    for i in range(5): cue(crack(), 34.2 + i * 0.33, 0.15, pan=-0.5 + i * 0.25); cue(shimmer(0.6), 34.25 + i * 0.33, 0.1)                  # fireworks
    pop(36.1, 0.3, 900); cue(ping(1568, 0.8), 36.15, 0.3); cue(whoosh(0.6), 36.6, 0.2)                                                   # s13 ping, note flies
    pop(38.0, 0.25, 700)
    for t in np.arange(38.4, 40.3, 0.11): cue(step(0.35), t, 0.18, pan=-0.3)                                                             # s14 meter sprints
    for t in np.arange(38.2, 40.3, 0.09): cue(tick(2000), t, 0.07, pan=-0.3)
    cue(whoomph(1.0), 40.6, 0.35); cue(hum(2.4, 70), 40.7, 0.15)                                                                         # s15 radiator on
    for i in range(5): cue(rustle(0.15, 1.8), 41.9 + i * 0.25, 0.15)
    cue(hum(1.6, 180), 44.0, 0.12); cue(sand(1.6), 44.4, 0.12); cue(blip(2200, 0.4, 0.2), 45.6, 0.08)                                    # s16 kettle
    cue(thunk(200, 120, 0.2), 45.4, 0.5); cue(rustle(0.2, 2.0), 45.42, 0.3)                                                              # bite
    pop(46.7, 0.25, 500); cue(rustle(0.2, 2.0), 47.0, 0.15)                                                                               # s17 crumb
    pop(48.5, 0.25, 400); cue(sand(0.8), 49.0, 0.25); cue(breath(0.8, 200, 1400, False), 49.2, 0.2)                                       # s18 puff
    cue(shimmer(0.9), 50.4, 0.3); cue(whoosh(1.0), 50.45, 0.2); pop(51.7, 0.25, 600)                                                      # s19 back to real
    for i in range(4): cue(tick(1700), 51.9 + i * 0.18, 0.2)
    pop(54.6, 0.4, 350); cue(thunk(100, 50, 0.4), 54.62, 0.6); pop(56.8, 0.2, 800)                                                         # s20 £120
    cue(clunk(120), 58.7, 0.35); cue(thunk(90, 45, 0.5), 59.3, 0.6)                                                                         # s21 scales tip
    pop(61.2, 0.25, 600); pop(61.9, 0.25, 900); cue(sweep(400, 700, 0.4), 62.6, 0.2)                                                       # s22 card, ring
    cue(rustle(0.3, 1.4), 65.0, 0.2); pop(65.9, 0.3, 800); pop(66.3, 0.25, 450); cue(thunk(150, 70, 0.3), 67.65, 0.5)                    # s23 PAY, house, cross
    cue(whoosh(0.4), 68.9, 0.15); pop(70.6, 0.3, 700)                                                                                      # s24
    cue(whoosh(0.6), 72.0, 0.15); cue(blip(1200, 0.12, 0.05), 72.1, 0.4); cue(whoosh(0.7), 72.6, 0.2); pop(73.3, 0.3, 900)                # end card
    return []

def ep18():
    def pop(t, g=0.3, f=700): cue(blip(f, 0.1, 0.05), t, g); cue(bubble(f), t + 0.01, g * 0.5)
    cue(whoosh(0.9), 0.0, 0.2); cue(sweep(200, 1600, 1.4), 0.1, 0.3); cue(sweep(200, 900, 2.0), 0.3, 0.15)                              # s1 columns race up
    cue(shimmer(0.8), 1.5, 0.25)
    cue(rustle(0.8, 0.8), 4.0, 0.2); cue(clink(), 5.2, 0.2); pop(4.6, 0.3, 600)                                                        # s2 padlock slides, card
    pop(6.4, 0.3, 500); cue(whoosh(0.4), 8.0, 0.2); cue(thunk(130, 55, 0.6), 8.6, 0.8); cue(clunk(160), 8.62, 0.4); pop(8.65, 0.25, 900) # s3 lock slams on
    pop(9.9, 0.3, 550)
    for i in range(3): cue(sweep(250 + 80 * i, 900 + 200 * i, 0.6), 10.8 + i * 0.25, 0.2)                                            # s4 three rises
    pop(13.0, 0.3, 600); pop(13.85, 0.3, 750); pop(14.55, 0.3, 900)                                                                   # s5 labels
    cue(shimmer(0.9), 16.9, 0.3); cue(whoosh(0.4), 17.1, 0.2); cue(clink(), 17.45, 0.35)                                               # s6 crown
    cue(sweep(200, 1400, 2.0), 19.0, 0.3); pop(20.85, 0.4, 400); cue(thunk(100, 50, 0.4), 20.9, 0.5)                                    # s7 +89%
    cue(sweep(200, 700, 1.2), 22.6, 0.2); pop(23.6, 0.3, 350); cue(breath(0.8, 200, 1400, False), 23.9, 0.2)                            # s8 +66%, deflate
    cue(whoosh(0.4), 25.3, 0.2); cue(shimmer(0.8), 25.6, 0.3)                                                                          # s9 trophy
    cue(rustle(1.5, 0.6), 27.6, 0.2); cue(sweep(900, 300, 1.6), 27.7, 0.15)                                                            # s10 lock slides out
    for i in range(6): cue(rustle(0.12, 1.4), 30.0 + i * 0.15, 0.15)                                                                   # s11 hand rub
    pop(30.0, 0.2, 1000)
    cue(crack(), 31.53, 0.6); cue(shimmer(), 31.6, 0.5); cue(whoomph(), 31.53, 0.5)                                                   # s12 switch
    cue(clunk(160), 32.55, 0.4); pop(32.6, 0.25, 800)
    pop(33.9, 0.3, 550); cue(sweep(300, 1200, 0.6), 35.0, 0.3); pop(34.9, 0.25, 700)                                                  # s13 prices up
    cue(sweep(300, 1400, 0.6), 37.3, 0.3); pop(37.3, 0.25, 850)                                                                         # s14 wages up
    cue(sand(2.4), 38.9, 0.12); cue(hum(1.2, 70), 39.0, 0.1); cue(sweep(300, 900, 0.5), 40.4, 0.25); pop(40.0, 0.25, 650)               # s15 rain, 2.5%
    cue(clink(), 41.6, 0.2); cue(rustle(0.4, 1.2), 42.2, 0.25)                                                                          # s16 plate
    cue(sweep(3000, 800, 0.3), 44.6, 0.3); cue(thunk(200, 120, 0.3), 44.85, 0.4); pop(44.6, 0.2, 1200)                                 # s17 ice
    cue(hum(0.5, 220), 45.9, 0.15); cue(crack(), 46.45, 0.5); cue(sand(0.6), 46.5, 0.3); cue(thunk(150, 70, 0.3), 46.5, 0.5)           # shatter, NO
    cue(sweep(800, 300, 0.4), 47.35, 0.2)
    for i in range(3): cue(tick(1600), 47.9 + i * 0.06, 0.4)                                                                            # s18 ratchet click
    cue(sweep(200, 1500, 2.0), 49.2, 0.3); cue(clink(), 51.2, 0.3); cue(shimmer(0.8), 51.25, 0.25)                                     # s19 climb, high five
    cue(shimmer(0.9), 52.7, 0.3); cue(whoosh(1.0), 52.75, 0.2); pop(53.9, 0.25, 600)                                                   # s20 back to reality
    for i in range(4): cue(tick(1700), 54.1 + i * 0.18, 0.2)
    pop(57.6, 0.4, 350); cue(thunk(100, 50, 0.4), 57.62, 0.6); pop(60.2, 0.2, 800)                                                       # s21 £5,500
    for i in range(6): cue(rustle(0.3, 1.3), 61.6 + i * 0.42 + 0.3, 0.25); cue(thunk(220, 140, 0.15), 61.95 + i * 0.42, 0.25)          # s22 notes land
    pop(63.9, 0.25, 600)
    cue(rustle(0.6, 0.8), 65.6, 0.2); cue(clink(), 66.4, 0.25)                                                                         # s23 lock back to Nan
    pop(68.0, 0.3, 800); cue(whoosh(0.4), 69.4, 0.15)                                                                                  # s24 share
    cue(whoosh(0.6), 70.2, 0.15); cue(blip(1200, 0.12, 0.05), 70.3, 0.4); cue(whoosh(0.7), 70.8, 0.2); pop(71.5, 0.3, 900)              # end card
    return []


def ep19():
    def pop(t, g=0.3, f=700): cue(blip(f, 0.1, 0.05), t, g); cue(bubble(f), t + 0.01, g * 0.5)
    cue(whoosh(0.5), 0.0, 0.2); cue(thunk(120, 60, 0.4), 0.9, 0.5); pop(0.95, 0.3, 500)                                  # s1 SHUT! pop
    pop(2.5, 0.3, 450); cue(thunk(100, 50, 0.4), 2.55, 0.4)                                                              # s2 1-2 a day
    cue(shimmer(0.8), 4.3, 0.3); cue(sweep(900, 300, 1.2), 4.5, 0.2); pop(4.4, 0.25, 700)                                # s3 big pub fades
    pop(6.9, 0.3, 800); cue(whoosh(0.5), 6.4, 0.25)                                                                       # s4 every high street
    cue(clink(), 8.9, 0.25); cue(sweep(300, 900, 0.5), 9.0, 0.2)                                                         # s5 coin
    pop(11.1, 0.25, 1000); cue(clink(), 11.6, 0.3); pop(11.2, 0.3, 700)                                                  # s6 5p
    cue(sweep(200, 1400, 1.5), 12.6, 0.3); pop(14.5, 0.35, 500)                                                          # s7-8 stack, over a billion
    pop(16.4, 0.25, 600); cue(hum(1.0, 110), 17.0, 0.1)                                                                  # s9 price to beat
    cue(rustle(0.6, 1.0), 18.2, 0.2)                                                                                     # s10 chalk
    for i in range(6): cue(rustle(0.12, 1.4), 21.9 + i * 0.15, 0.15)                                                     # s12 hand rub
    cue(crack(), 23.95, 0.6); cue(shimmer(), 24.0, 0.5); cue(whoosh(0.9), 23.95, 0.5)                                    # s13 switch
    pop(28.9, 0.25, 600); cue(sweep(300, 900, 0.5), 28.8, 0.25)                                                          # s15 chalk up
    for i in range(3): cue(clink(), 30.8 + i * 0.3, 0.3)                                                                 # s16 pennies
    for i in range(6): cue(clink(), 32.2 + i * 0.12, 0.25)                                                               # s17 more pennies
    cue(clink(), 35.8, 0.3); cue(rustle(0.4, 1.0), 35.5, 0.2)                                                            # s19 hands over coins
    cue(rustle(0.8, 0.7), 38.1, 0.25); pop(38.9, 0.3, 450)                                                               # s21 bill
    pop(40.9, 0.3, 700); cue(thunk(180, 100, 0.3), 40.95, 0.3)                                                           # s22 nan shock
    cue(shimmer(0.9), 42.5, 0.35); cue(whoosh(0.9), 42.55, 0.25); pop(43.4, 0.3, 800)                                    # s23 back to reality
    cue(blip(1500, 0.05, 0.03), 45.9, 0.4); cue(clink(), 46.0, 0.2)                                                      # s24 snap
    pop(48.0, 0.4, 400); cue(thunk(100, 50, 0.4), 48.05, 0.5)                                                            # s25 £5.34
    cue(clunk(160), 49.4, 0.3)                                                                                           # s26 hoist
    for i in range(13): cue(clunk(260 + 8 * i), 51.2 + i * 0.1, 0.1)                                                     # s27 pints land
    pop(53.3, 0.3, 600); pop(54.9, 0.45, 350); cue(thunk(100, 50, 0.5), 54.95, 0.6)                                      # s28-29 big number
    pop(56.7, 0.2, 800)                                                                                                  # s30 our own sum
    cue(rustle(0.6, 0.8), 60.0, 0.2)
    pop(64.4, 0.3, 900); cue(whoosh(0.4), 63.9, 0.15)                                                                    # s33 follow
    pop(66.5, 0.25, 800)
    cue(whoosh(0.6), 68.1, 0.15); cue(blip(1200, 0.12, 0.05), 68.2, 0.4); cue(whoosh(0.7), 68.7, 0.2); pop(69.4, 0.3, 900)  # end card
    return []


def ep20():
    def pop(t, g=0.3, f=700): cue(blip(f, 0.1, 0.05), t, g); cue(bubble(f), t + 0.01, g * 0.5)
    def clap(t, g=0.18): cue(hpf(noise(n_of(0.06)), 900) * np.exp(-tvec(n_of(0.06)) / 0.012), t, g)
    cue(whoosh(0.3), 0.0, 0.3); cue(thunk(140, 55, 0.5), 0.22, 0.7); pop(0.25, 0.35, 450)                               # s1 cheque slam on frame 1, LOST!
    cue(sweep(250, 1200, 1.1), 2.5, 0.25); pop(3.4, 0.35, 600); cue(thunk(110, 55, 0.4), 3.45, 0.4)                       # s2 BACK stack shoots up, NEARLY x2
    pop(5.85, 0.3, 800)                                                                                                  # s3 DAY ONE?
    cue(sweep(500, 220, 0.6), 7.9, 0.15); pop(8.25, 0.3, 380)                                                            # s4 SKINT
    pop(9.45, 0.25, 900); pop(10.45, 0.3, 750)                                                                           # s5 gift appears, A GIFT?
    for i in range(3): cue(rustle(0.12, 1.2), 11.5 + i * 0.17, 0.15)                                                     # s6 head shake
    cue(whoosh(0.5), 11.6, 0.25); cue(thunk(160, 70, 0.35), 12.72, 0.55); pop(12.6, 0.3, 500)                            # gift pushed away, LOAN slapped down
    cue(sweep(250, 1100, 1.1), 14.1, 0.25); pop(14.2, 0.35, 450); pop(16.1, 0.3, 800)                                     # s7 $4.3BN, 2%
    cue(sand(0.6), 17.4, 0.25); cue(whoosh(0.6), 18.4, 0.2)                                                              # s8 tea pours, cheque slides
    for i in range(3): cue(tick(1700), 18.3 + i * 0.6, 0.25)                                                             # calendar flips
    cue(crack(), 19.85, 0.6); cue(shimmer(), 19.9, 0.5); cue(whoosh(0.9), 19.85, 0.5)                                    # s9 timeline switch
    cue(whoosh(0.8), 23.0, 0.3); cue(clunk(170), 23.9, 0.35)                                                             # s10 hand it straight back
    cue(shimmer(1.2), 24.5, 0.35); pop(26.7, 0.3, 900)                                                                   # s11 FULL VALUE
    cue(blip(1500, 0.05, 0.03), 27.4, 0.4); cue(whoosh(0.6), 27.4, 0.3)                                                  # s12 back to what happened
    for i in range(5): cue(whoosh(0.35), 29.6 + i * 0.45, 0.12)                                                          # s13 cheque after cheque
    for i in range(14): cue(tick(1500 + 20 * i), 29.6 + i * 0.15, 0.18)                                                  # calendar races
    pop(31.0, 0.25, 600)
    cue(sweep(300, 900, 1.5), 32.7, 0.25); pop(33.7, 0.3, 500)                                                           # s14 PRICES up
    cue(sweep(500, 1200, 0.35), 34.6, 0.3); cue(sweep(700, 1800, 0.35), 35.3, 0.35); pop(35.3, 0.4, 450)                 # s15 rose... ROSE!
    cue(sweep(1100, 200, 1.1), 37.0, 0.3); pop(37.75, 0.35, 650)                                                         # s16 the dollar shrinks, 1/10
    cue(whoosh(0.5), 39.3, 0.15); pop(41.4, 0.3, 400)                                                                    # s17 WORTH LESS
    cue(sweep(200, 1300, 2.7), 42.6, 0.25); pop(44.6, 0.4, 450); cue(thunk(110, 50, 0.5), 44.65, 0.55)                   # s18 $7.5BN
    pop(46.3, 0.2, 900)                                                                                                  # s19 smug
    pop(48.7, 0.25, 700); cue(sweep(800, 500, 1.2), 49.0, 0.2)                                                           # s20 IN 1946 DOLLARS
    cue(sweep(900, 180, 1.8), 50.4, 0.35); pop(52.15, 0.45, 380); cue(thunk(100, 45, 0.6), 52.2, 0.6)                    # s21 hero: $2.5BN
    pop(53.5, 0.2, 800); pop(54.95, 0.3, 600)                                                                            # s22 rough sum, just over half
    pop(56.4, 0.25, 900)                                                                                                 # s23 cheap loan
    cue(sweep(700, 300, 1.0), 58.3, 0.2)                                                                                 # s24 shrinking dollars
    for i in range(10): clap(59.75 + i * 0.22)                                                                           # s25 Nan claps
    pop(61.3, 0.3, 700); pop(62.3, 0.3, 500); cue(whoosh(0.4), 63.6, 0.2)                                                # s26-27
    cue(whoosh(0.6), 65.9, 0.15); cue(blip(1200, 0.12, 0.05), 66.0, 0.4); cue(whoosh(0.7), 66.5, 0.2); pop(67.2, 0.3, 900)  # end card
    return []


EPISODES = {'ep20': ep20, 'ep19': ep19, 'ep18': ep18, 'ep17': ep17, 'ep16': ep16, 'ep15': ep15, 'ep14': ep14, 'ep09': ep09, 'ep10': ep10, 'ep11': ep11, 'ep13': ep13}
gaps = EPISODES[EP]()
# room tone bed, ducked out through the silences
bed = (lpf(noise(n_of(LEN + 1)), 500) * 0.08 + lpf(noise(n_of(LEN + 1)), 120) * 0.05)
g = np.ones(n_of(LEN + 1))
for a, b in gaps:
    i, j = n_of(a), n_of(b); g[i:j] = 0; g[i - 4800:i] = np.linspace(1, 0, 4800); g[j:j + 4800] = np.linspace(0, 1, 4800)
cue(bed * g, 0, 1.0)
for a, b in gaps:  # the freeze also pulls the other effects out: clear anything but the crack
    pass

# ---------- mix: narrator on top, effects far below ----------
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', VO, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], check=True, capture_output=True).stdout
vo = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).T
n = n_of(LEN)
sfx = buf[:, :n].copy()
m = pyln.Meter(SR)
sl = m.integrated_loudness(sfx.T)
sfx *= 10 ** ((-34 - sl) / 20)                       # effects stem at about -34 LUFS (voice is about -15)
mix = np.zeros((2, n)); mix[:, :min(n, vo.shape[1])] += vo[:, :n]; mix += sfx
mix *= 10 ** ((-14.0 - m.integrated_loudness(mix.T)) / 20)
pk = np.abs(mix).max()
if pk > 0.89: mix *= 0.89 / pk
sf.write(OUT, mix.T.astype(np.float32), SR)
vl = m.integrated_loudness(vo.T); ml = m.integrated_loudness(mix.T)
print(f'{OUT}: voice {vl:.1f} LUFS, effects stem -34 LUFS, mix {ml:.1f} LUFS, peak {20*np.log10(np.abs(mix).max()):.1f} dBFS')
