# Voices + rough mix for the Phoneverse "Cheers, Biscuit" short.
#
# What it does
#   1. Generates every line with Kokoro (British voices), one WAV per line, with per-line speed, pitch and effects.
#   2. Bleeps the swear word in line 1 (a 1 kHz tone replaces the word; the mouth still moves = the joke).
#   3. Lays all lines on one timeline (small gaps, overlaps where people talk over each other: no dead space).
#   4. Writes per-character stems for lip sync (Rhubarb Lip Sync in Blender), timeline.json, words.json, captions.srt.
#   5. Builds rough_mix.wav: voices + the scene music beds, ducked so the music never fights the voice.
#
# Run (on the PC that has Kokoro):
#   pip install kokoro soundfile scipy numpy        (and ffmpeg on PATH for pitch / echo effects)
#   python music_garage.py                            (makes out/*.wav music, once)
#   python make_audio.py                              (makes out/lines, out/stems, out/rough_mix.wav ...)
#   python make_audio.py --only L06 L21               (regenerate just some lines after you tweak them)
#   python make_audio.py --mock                       (test the whole flow without Kokoro: beeps instead of voices)
#
# Kokoro text rules learned the hard way (checked with Kokoro's British phonemizer):
#   - Never write a word in CAPITALS: "UP" is read "U-P". Use lowercase + "!" and the stress mark [word](+2).
#   - Write numbers as words: "Biscuit123" is read "Biscuit one twenty-three". Use "biscuit one two three".
#   - Unknown names need phonemes: [Hong Kong](/hˌɒŋ kˈɒŋ/).
#   - Kokoro has no emotion setting. Emotion comes from: punctuation (! ?! ... ,), speed per line, short lines,
#     pitch (+1/+2 semitones = panic/excited, -2/-3 = big/menacing), effects, and the human sounds layer
#     (gasps, grunts, breaths) in the SFX track. See SCRIPT.md for the plan B on the five biggest lines.
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "templates", "audio"))
from dsp import SR, ns, dbg, integrated, peq, write_wav, read_wav  # noqa: E402

KSR = 24000  # Kokoro output rate
OUT = os.path.join(HERE, "out")
SPEED = 1.06  # global pace multiplier on top of each line's own speed

# ------------------------------------------------------------------ cast: Kokoro voice + default pitch (semitones)
CAST = {
    "YOU": dict(voice="bf_emma", pitch=0.0),
    "JESS": dict(voice="bf_isabella", pitch=0.5),
    "THIEF_A": dict(voice="bm_george", pitch=-0.5),
    "THIEF_B": dict(voice="bm_lewis", pitch=-3.0),  # the huge one: deep voice, soft words
    "OLD_MAN": dict(voice="bm_daniel", pitch=-1.0),
    "SHOPPER": dict(voice="bf_alice", pitch=0.0),
    "HOODED": dict(voice="bm_fable", pitch=-3.0),
}

# ------------------------------------------------------------------ level presets (target loudness per line, LUFS)
LEVEL = {"normal": -16.0, "shout": -14.5, "aside": -18.5, "distant": -18.0}

# ------------------------------------------------------------------ effect presets (ffmpeg filter chains)
FX = {
    None: "",
    "shout": "highpass=f=110,acompressor=threshold=0.08:ratio=5:attack=4:release=90:makeup=2",
    "away": "lowpass=f=4200,aecho=0.8:0.55:70:0.22",  # shouting at a camera that is leaving her
    "echo": "apad=pad_dur=1.2,aecho=1.0:0.55:380|760|1140:0.35|0.2|0.1",  # "JESS!" then its echo (late, so the J stays crisp)
    "close": "highpass=f=70,lowpass=f=7000,acompressor=threshold=0.1:ratio=3:attack=10:release=150:makeup=1.5",
}

# ------------------------------------------------------------------ the script
# id, who, scene, caption text, Kokoro text, speed, extra pitch, level, fx, gap (s before; negative = overlap),
# lips (ON/OFF for the animator), emotion (direction), bleep (word to bleep), alts (other Kokoro texts to audition)
L = []


def line(id_, who, scene, text, tts, speed=1.0, pitch=0.0, level="normal", fx=None, gap=0.12, lips="ON", emotion="",
         bleep=None, alts=()):
    L.append(dict(id=id_, who=who, scene=scene, text=text, tts=tts, speed=speed, pitch=pitch, level=level, fx=fx,
                  gap=gap, lips=lips, emotion=emotion, bleep=bleep, alts=list(alts)))


# Scene 1: hook
line("L01", "YOU", "hook", "If UK thieves don't really want your phone... why the f*** do they keep nicking it?",
     "if UK thieves don't really want your phone... why the fuck do they keep nicking it?",
     speed=1.05, gap=0.0, emotion="baffled, half-laughing, leaning into camera like telling a mate", bleep="fuck",
     alts=["if UK thieves don't [really](+2) want your phone... why the fuck do they keep [nicking](+2) it?"])
line("L02", "YOU", "hook", "Sounds mad, right? Now you judge this.", "sounds mad, right? now [you](+2) judge this.",
     lips="OFF", emotion="cheeky, a wink (focus shifts to the two thieves behind her)")
line("L03", "YOU", "hook", "So I'm walking down Oxford Street, scrolling, minding my own business, yeah...",
     "so I'm walking down oxford street, scrolling, minding my own business, yeah,", speed=1.12,
     emotion="breezy, carefree")
# Scene 2: the snatch
line("L04", "THIEF_B", "snatch", "Ooh, sorry, love!", "ooh, sorry, love!", speed=1.05, gap=-0.15,
     emotion="huge man, sweet over-friendly voice (the joke is the size vs the voice)")
line("L05", "YOU", "snatch", "Nah, you're alright...", "[nah](/nˈɑː/), you're alright,", speed=1.1, gap=0.0, lips="OFF",
     emotion="polite, distracted, already looking at the bloke")
line("L06", "YOU", "snatch", "Oi! Oi! Get off! Get OFF it!", "oi! oi! get off! get [off](+2) it!", speed=1.22,
     pitch=1.0, level="shout", fx="shout", gap=-0.05, emotion="shock into fury, gripping with both hands, effort",
     alts=["oi! oi! oi! get off it!", "oi!! get off! get off it!!"])
line("L07", "THIEF_A", "snatch", "Let go! Just let go, man!", "let go! just let go, man!", speed=1.08,
     level="shout", fx="shout", gap=-0.2, emotion="strained, through gritted teeth, pulling")
line("L08", "YOU", "snatch", "No, no, no, no!", "no, no, no, no!", speed=1.35, pitch=1.5, level="shout",
     fx="shout", gap=-0.05, lips="OFF", emotion="panic as it rips free (phone spinning in the air)")
line("L09", "YOU", "snatch", "Wait... who's got it? Who's got it?!", "wait, who's got it? who's got it?!",
     speed=1.25, pitch=1.0, level="shout", gap=0.05, emotion="panicking, spinning between them")
line("L10", "OLD_MAN", "snatch", "He went that way!", "he went [that](+2) way!", speed=1.05, level="shout",
     fx="away", gap=0.05, lips="OFF", emotion="helpful, pointing left")
line("L11", "SHOPPER", "snatch", "No, love, THAT way!", "no, love, [that](+2) way!", speed=1.1, level="shout",
     fx="away", gap=-0.25, lips="OFF", emotion="talking over him, pointing right")
line("L12", "YOU", "snatch", "Nah... nah. I am NOT chasing two grown men down Oxford Street.",
     "nah... nah. I am [not](+2) chasing two grown men down oxford street.", speed=0.98, gap=0.15,
     emotion="out of breath, hands on knees, deadpan")
line("L13", "YOU", "snatch", "One of them's the size of a fridge!", "one of them's the size of a [fridge](+2)!",
     speed=1.1, emotion="incredulous")
line("L14", "YOU", "snatch", "Oi, camera! Where are you going? You're meant to follow ME!",
     "oi, camera! where are you going? you're meant to follow [me](+2)!", speed=1.08, level="shout", fx="away", lips="OFF",
     emotion="indignant, shouting after the camera that's leaving her")
# Scene 3: the phone's journey (voice-over)
line("L15", "YOU", "journey", "Fine. Follow my phone then. See if I care.", "fine. follow my phone then. see if I care.",
     speed=1.0, level="aside", fx="close", gap=0.2, lips="OFF", emotion="sulking")
line("L16", "YOU", "journey", "Bike. Van. Some dodgy warehouse near Heathrow. Then a box full of other people's phones... off to Hong Kong.",
     "bike. van. some dodgy warehouse near heathrow. then a box full of other people's phones... off to [Hong Kong](/hˌɒŋ kˈɒŋ/).",
     speed=1.1, fx="close", lips="OFF", emotion="deadpan list, fast")
line("L17", "YOU", "journey", "But joke's on them, innit? It's got Activation Lock. Without my password, it's basically spare parts.",
     "but joke's on them, innit? it's got activation lock. without my password, it's basically spare parts.",
     speed=1.05, fx="close", lips="OFF", emotion="smug")
line("L18", "YOU", "journey", "So they need me to hand it over. And I'm not thick.",
     "so they need [me](+2) to hand it over. and I'm not thick.", speed=1.0, fx="close", lips="OFF",
     emotion="cocky")
# Scene 4: the sofa
line("L19", "YOU", "sofa", "Three months later. New phone, new me...", "three months later. new phone, new me,",
     speed=1.1, fx="close", gap=0.25, lips="OFF", emotion="breezy (text ping lands right after)")
line("L20", "YOU", "sofa", "Hold on. \"Your lost phone has been found. Tap to see where.\"",
     "hold on. your lost phone has been found. tap to see where.", speed=1.0, gap=0.2,
     emotion="surprised, then reading it out flat")
line("L21", "JESS", "sofa", "Shut up! They found it?! Tap it! Tap it, tap it, tap it!",
     "shut [up](+2)! they found it?! tap it! tap it, tap it, tap it!", speed=1.28, pitch=1.0, level="shout",
     gap=-0.1, emotion="squealing, bouncing on the sofa")
line("L22", "YOU", "sofa", "Hang on... how've they even got my number?", "hang on... how've they even got my number?",
     speed=0.92, emotion="suspicious, slow, pulling the phone away")
line("L23", "YOU", "sofa", "Oh, come on... I put it on my lock screen when I marked it lost. They just read it off.",
     "oh, come on... I put it on my lock screen when I marked it lost. they just read it off.", speed=1.05,
     fx="close", lips="OFF", emotion="groan, then the penny drops (warehouse cutaway)")
line("L24", "YOU", "sofa", "Babe. Apple doesn't text you when they find a phone. Ever.",
     "babe. apple doesn't text you when they find a phone. [ever](+2).", speed=0.95, emotion="firm, patient")
line("L25", "YOU", "sofa", "That link's a fake login. I type my password, they unlock it, sell it, done.",
     "that link's a fake login. I type my password, they unlock it, sell it, done.", speed=1.12, lips="OFF",
     emotion="sharp, counting on fingers (over-the-shoulder on the fake login)")
line("L26", "YOU", "sofa", "So I don't tap nothing. I open Find My myself, and I leave the phone on my account. Easy.",
     "so I don't tap nothing. I open find my myself, and I leave the phone on my account. easy.", speed=1.0,
     lips="OFF", emotion="proud, sorted (lips ON only on 'Easy')")
line("L27", "JESS", "sofa", "...Bit late for that.", "...bit late for that.", speed=0.9, level="aside", gap=0.2,
     emotion="tiny, guilty")
line("L28", "YOU", "sofa", "Jess. What did you do?", "jess. what did you do?", speed=0.85, gap=0.15,
     emotion="slow dread")
line("L29", "JESS", "sofa", "Your password's Biscuit123! Everyone knows that!",
     "your password's biscuit one two three! everyone knows that!", speed=1.15, pitch=1.0,
     emotion="proud, bubbly, thinks she helped")
line("L30", "HOODED", "warehouse", "Cheers, Biscuit.", "cheers, biscuit.", speed=0.85, level="aside", fx="close",
     gap=0.3, lips="OFF", emotion="calm, low, amused")
line("L31", "YOU", "warehouse", "JESS!", "jess!", speed=0.85, pitch=0.5, level="shout", fx="echo", gap=0.15,
     lips="OFF", emotion="full scream, from far away")

# music cues: (music file, anchored to line, offset s from that line's start, kind)
MUSIC = [
    ("A_hook", "L01", -0.0, "bed"),
    ("B_snatch", "L04", -0.05, "bed"),
    ("C_journey", "L15", -0.2, "bed"),
    ("D_sofa", "L19", -0.2, "bed"),
    ("sting_tapestop", "L27", -0.35, "sting"),
    ("sting_biscuit", "L30", -0.9, "sting"),  # its low note lands at 0.9 s = on "Cheers"
    ("sting_jess", "L31", -1.2, "sting"),  # its hit lands at 1.2 s = on "JESS!"
]


# ------------------------------------------------------------------ helpers
def ffmpeg_fx(x, sr, chain):
    if not chain or shutil.which("ffmpeg") is None:
        if chain:
            print("  (ffmpeg not found: effect skipped)")
        return x
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "a.wav"), os.path.join(d, "b.wav")
        import soundfile as sf
        sf.write(a, x, sr, subtype="FLOAT")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a, "-af", chain, "-ar", str(sr), "-ac", "1", b], check=True)
        y, _ = sf.read(b, dtype="float64")
    return y


def pitch_chain(semitones, sr):
    if abs(semitones) < 1e-3:
        return ""
    k = 2 ** (semitones / 12)
    tempo = 1 / k  # asetrate shifts pitch and speed; atempo puts the duration back (timestamps stay valid)
    parts = []
    while tempo < 0.5:
        parts.append("atempo=0.5")
        tempo /= 0.5
    while tempo > 2.0:
        parts.append("atempo=2.0")
        tempo /= 2.0
    parts.append(f"atempo={tempo:.6f}")
    return f"asetrate={sr * k:.3f},aresample={sr}," + ",".join(parts)


def loudness(x48):
    y = x48 if len(x48) >= ns(0.8) else np.pad(x48, (0, ns(0.8) - len(x48)))
    v = integrated(y)
    if not np.isfinite(v) or v < -69:
        rms = np.sqrt(np.mean(x48 ** 2)) + 1e-12
        v = 20 * np.log10(rms) - 0.7
    return v


def bleep(x, sr, t0, t1, ref_rms):
    i0, i1 = max(0, int((t0 - 0.02) * sr)), min(len(x), int((t1 + 0.02) * sr))
    n = i1 - i0
    if n <= 0:
        return x
    t = np.arange(n) / sr
    tone = np.sin(2 * np.pi * 1000 * t) * ref_rms * 1.6
    f = min(n // 2, int(0.005 * sr))
    if f > 0:
        tone[:f] *= np.linspace(0, 1, f)
        tone[-f:] *= np.linspace(1, 0, f)
    y = x.copy()
    y[i0:i1] = tone
    return y


class MockPipeline:
    """stand-in for Kokoro: a buzzy tone per word at ~3.6 words/s with word timestamps (flow test only)"""

    class Tok:
        def __init__(self, text, a, b):
            self.text, self.start_ts, self.end_ts = text, a, b

    class Res:
        def __init__(self, audio, tokens):
            self.audio, self.tokens = audio, tokens

    def __call__(self, text, voice=None, speed=1.0):
        words = [w for w in text.replace("[", "").split() if w]
        per = 0.28 / speed
        toks, chunks, t = [], [], 0.0
        f0 = 140 + (hash(voice) % 120)
        for w in words:
            n = int(per * KSR)
            tt = np.arange(n) / KSR
            chunks.append(0.2 * np.sign(np.sin(2 * np.pi * f0 * tt)) * np.hanning(n))
            toks.append(self.Tok(w.strip(".,!?\"'()/").split("](")[0], t, t + per * 0.9))
            t += per
        yield self.Res(np.concatenate(chunks), toks)


def synth(pipe, text, voice, speed):
    audio, toks, off = [], [], 0.0
    for r in pipe(text, voice=voice, speed=speed):
        a = r.audio.detach().cpu().numpy() if hasattr(r.audio, "detach") else np.asarray(r.audio)
        for tk in (r.tokens or []):
            if tk.start_ts is not None and tk.end_ts is not None:
                toks.append(dict(text=tk.text, start=off + tk.start_ts, end=off + tk.end_ts))
        audio.append(a.astype(np.float64))
        off += len(a) / KSR
    return np.concatenate(audio) if audio else np.zeros(1), toks


def make_line(pipe, ln, tts=None):
    c = CAST[ln["who"]]
    x, toks = synth(pipe, tts or ln["tts"], c["voice"], ln["speed"] * SPEED)
    # trim Kokoro's leading/trailing silence (keep 40 ms), shift word times to match
    thr = 0.01 * np.max(np.abs(x))
    nz = np.flatnonzero(np.abs(x) > thr)
    a = max(0, nz[0] - int(0.04 * KSR)) if len(nz) else 0
    b = min(len(x), nz[-1] + int(0.06 * KSR)) if len(nz) else len(x)
    x = x[a:b]
    toks = [dict(t, start=max(0.0, t["start"] - a / KSR), end=max(0.0, t["end"] - a / KSR)) for t in toks]
    if ln["bleep"]:
        hit = [t for t in toks if t["text"].lower().strip(".,!?") == ln["bleep"]]
        if hit:
            x = bleep(x, KSR, hit[0]["start"], hit[0]["end"], np.sqrt(np.mean(x ** 2)))
            hit[0]["text"] = "[bleep]"
        else:
            print(f"  WARNING {ln['id']}: word to bleep not found in timestamps, bleep it by hand")
    chain = ",".join(p for p in [pitch_chain(c["pitch"] + ln["pitch"], KSR), FX[ln["fx"]]] if p)
    x = ffmpeg_fx(x, KSR, chain)
    x48 = resample_poly(x, SR // 1000, KSR // 1000)
    x48 *= dbg(LEVEL[ln["level"]] - loudness(x48))
    return x48, toks


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true", help="no Kokoro: beeps instead of voices (tests the flow)")
    ap.add_argument("--only", nargs="*", help="regenerate only these line ids (others are read back from out/lines)")
    ap.add_argument("--alts", action="store_true", help="also render the alternative takes to out/alts")
    args = ap.parse_args()

    if args.mock:
        pipe = MockPipeline()
    else:
        from kokoro import KPipeline
        pipe = KPipeline(lang_code="b")  # British English

    for d in ("lines", "stems", "alts"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)

    clips, words = {}, {}
    cache = os.path.join(OUT, "lines", "_words.json")
    old_words = json.load(open(cache)) if (args.only and os.path.exists(cache)) else {}
    for ln in L:
        path = os.path.join(OUT, "lines", f"{ln['id']}_{ln['who']}.wav")
        if args.only and ln["id"] not in args.only and os.path.exists(path):
            clips[ln["id"]] = read_wav(path)[0] if read_wav(path)[0].ndim == 1 else read_wav(path)[0].mean(0)
            words[ln["id"]] = old_words.get(ln["id"], [])
            continue
        print(f"{ln['id']} {ln['who']:8s} {ln['text']}")
        x, toks = make_line(pipe, ln)
        clips[ln["id"]], words[ln["id"]] = x, toks
        write_wav(path, x, bits=24)
        if args.alts:
            for k, alt in enumerate(ln["alts"]):
                y, _ = make_line(pipe, ln, tts=alt)
                write_wav(os.path.join(OUT, "alts", f"{ln['id']}_{chr(98 + k)}.wav"), y, bits=24)
    json.dump(words, open(cache, "w"), indent=1)

    # timeline
    t, prev_start, tl = 0.0, -1.0, []
    for ln in L:
        x = clips[ln["id"]]
        start = max(prev_start + 0.15, t + ln["gap"]) if tl else 0.0
        # the line "ends" at its last spoken word: breath and effect tails overlap the next line (no dead air)
        spoken = [w for w in words[ln["id"]] if w["text"][:1].isalnum() or w["text"] == "[bleep]"]
        end = start + (min(len(x) / SR, spoken[-1]["end"] + 0.06) if spoken else len(x) / SR)
        tl.append(dict(id=ln["id"], who=ln["who"], scene=ln["scene"], start=round(start, 3), end=round(end, 3),
                       text=ln["text"], lips=ln["lips"], emotion=ln["emotion"]))
        prev_start, t = start, max(t, end)
    total = max(t, max(r["start"] for r in tl) + len(clips[L[-1]["id"]]) / SR) + 1.2
    N = ns(total)
    voice = np.zeros(N)
    stems = {w: np.zeros(N) for w in CAST}
    for ln, row in zip(L, tl):
        x = clips[ln["id"]]
        i = ns(row["start"])
        voice[i: i + len(x)] += x[: N - i]
        stems[ln["who"]][i: i + len(x)] += x[: N - i]
    write_wav(os.path.join(OUT, "voice_track.wav"), voice, bits=24)
    for w, s in stems.items():
        if np.any(s):
            write_wav(os.path.join(OUT, "stems", f"voice_{w}.wav"), s, bits=24)
            with open(os.path.join(OUT, "stems", f"voice_{w}_dialog.txt"), "w") as f:  # Rhubarb's optional dialog text
                f.write("\n".join(ln["text"].replace("f***", "") for ln in L if ln["who"] == w))
    json.dump(tl, open(os.path.join(OUT, "timeline.json"), "w"), indent=1)
    allw = []
    for ln, row in zip(L, tl):
        for wd in words[ln["id"]]:
            allw.append(dict(line=ln["id"], who=ln["who"], word=wd["text"], start=round(row["start"] + wd["start"], 3),
                             end=round(row["start"] + wd["end"], 3)))
    json.dump(allw, open(os.path.join(OUT, "words.json"), "w"), indent=1)

    def ts(s):
        return f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(round(s % 1 * 1000)) % 1000:03d}"

    with open(os.path.join(OUT, "captions.srt"), "w") as f:
        for k, row in enumerate(tl, 1):
            f.write(f"{k}\n{ts(row['start'])} --> {ts(row['end'])}\n{row['text']}\n\n")

    # music: beds looped/cropped to their scene, stings on their anchors, ducked under the voice
    mus_dir = os.path.join(OUT)
    starts = {r["id"]: r["start"] for r in tl}
    music = np.zeros((2, N))
    beds = [m for m in MUSIC if m[3] == "bed"]
    tapestop_t = starts["L27"] - 0.35
    for k, (name, anchor, off, kind) in enumerate(MUSIC):
        p = os.path.join(mus_dir, f"{name}.wav")
        if not os.path.exists(p):
            print(f"  music file missing: {p} (run music_garage.py first)")
            continue
        x, _ = read_wav(p)
        x = x if x.ndim == 2 else np.stack([x, x])
        t0 = max(0.0, starts[anchor] + off)
        if kind == "bed":
            nxt = [b for b in beds if starts[b[1]] + b[2] > t0]
            t1 = (starts[nxt[1][1]] + nxt[1][2]) if len(nxt) > 1 else tapestop_t
            need = ns(t1 - t0)
            reps = int(np.ceil(need / x.shape[1])) + 1
            y = np.tile(x, reps)[:, :need]
            f = min(ns(0.15), need // 2)
            y[:, :f] *= np.linspace(0, 1, f)[None, :]
            y[:, -f:] *= np.linspace(1, 0, f)[None, :]
        else:
            y = x
        i = ns(t0)
        j = min(N, i + y.shape[1])
        music[:, i:j] += y[:, : j - i]
    # EQ space for the voice, then duck: -14 dB under speech, -8 dB in gaps, smooth
    music = np.stack([peq(music[c], 2200, -4.0, 0.7) for c in range(2)])
    env = np.abs(voice)
    win = ns(0.05)
    env = np.convolve(env, np.ones(win) / win, mode="same")
    speech = (env > dbg(-45)).astype(float)
    att, rel = ns(0.06), ns(0.35)
    g = np.zeros(N)
    for i in range(1, N):  # one-pole attack/release on the "speech" gate
        c = 1 / att if speech[i] > g[i - 1] else 1 / rel
        g[i] = g[i - 1] + (speech[i] - g[i - 1]) * c
    duck_db = -8.0 + (-6.0) * g
    music *= dbg(duck_db)[None, :]
    mix = np.stack([voice, voice]) + music
    mix *= dbg(-14.0 - integrated(mix))
    ceil = dbg(-2.5)
    mix = np.where(np.abs(mix) > ceil, np.sign(mix) * (ceil + (1 - ceil) * np.tanh((np.abs(mix) - ceil) / (1 - ceil))), mix)
    mix = np.clip(mix, -dbg(-1.8), dbg(-1.8))  # leaves room for inter-sample peaks: true peak stays under -1 dBTP
    write_wav(os.path.join(OUT, "music_ducked.wav"), music, bits=24)
    write_wav(os.path.join(OUT, "rough_mix.wav"), mix, bits=24)
    print(f"\nTotal {total:.1f} s | voice {integrated(np.stack([voice, voice])):.1f} LUFS | "
          f"music (ducked) {integrated(music):.1f} LUFS | mix {integrated(mix):.1f} LUFS")
    print("Wrote out/lines, out/stems, out/timeline.json, out/words.json, out/captions.srt, out/rough_mix.wav")


if __name__ == "__main__":
    main()
