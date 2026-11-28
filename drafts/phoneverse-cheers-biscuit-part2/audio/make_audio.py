# Voices + rough mix for Phoneverse "Cheers, Biscuit" Part 2 (the finale). Same engine as Part 1's make_audio.py.
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
    "echo": "apad=pad_dur=1.4,aecho=1.0:0.45:520|1040:0.28|0.14",  # "JESS!" then its echo (late + soft, so the J stays crisp)
    "close": "highpass=f=70,lowpass=f=7000,acompressor=threshold=0.1:ratio=3:attack=10:release=150:makeup=1.5",
}

# ------------------------------------------------------------------ the script
# id, who, scene, caption text, Kokoro text, speed, extra pitch, level, fx, gap (s before; negative = overlap),
# lips (ON/OFF for the animator), emotion (direction), bleep (word to bleep), alts (other Kokoro texts to audition)
L = []


def line(id_, who, scene, text, tts, speed=1.0, pitch=0.0, level="normal", fx=None, gap=0.12, lips="ON", emotion="",
         bleep=None, alts=(), engine="kokoro", pauses=None):
    # pauses: {word: seconds} = a deliberate silence inserted right after that word (house rule: 1 s after the hook's
    # questions). engine="chatterbox": the take comes from chatterbox_lines.py or drag_lines.py (out/chatterbox/<id>.wav)
    L.append(dict(id=id_, who=who, scene=scene, text=text, tts=tts, speed=speed, pitch=pitch, level=level, fx=fx,
                  gap=gap, lips=lips, emotion=emotion, bleep=bleep, alts=list(alts), engine=engine, pauses=pauses or {}))



# Part 1's music beds and stings are reused (re-arranged); its last line's echo is the cold open
P1 = os.path.join(HERE, "..", "..", "phoneverse-found-text", "audio", "out")
PRE = 1.15  # Part 1's full "JESS!" scream + first echo play alone for this long before the first line

# Beat 1: cold open, the flat
line("L01", "JESS", "flat", "I'm so sorry, I didn't mean to!", "I'm so [sorry](+2), I didn't mean to!", speed=1.12,
     pitch=0.5, gap=0.0, emotion="wincing, guilty, hands up (overlaps the echo)", engine="chatterbox")
line("L02", "YOU", "flat", "Okay. He's got my password... but he still needs my code. Right?",
     "okay. he's got my password... but he still needs my [code](+2). right?", speed=1.0, gap=0.15,
     emotion="breathless, forcing herself calm: the hook question")
line("L03", "JESS", "flat", "Course he does! Codes are the whole point of codes!",
     "course he does! codes are the whole [point](+2) of codes!", speed=1.15, pitch=0.5, gap=0.3,
     emotion="totally confident, totally wrong")
line("L04", "YOU", "flat", "...Unless he goes through Find Devices. That one doesn't ask for a code.",
     "unless he goes through... find devices. that one doesn't ask for a code.", speed=0.95, gap=0.35,
     emotion="the penny drops, quiet horror")
line("L05", "JESS", "flat", "Why would Apple DO that?!", "why would apple [do](+2) that?!", speed=1.12, pitch=1.0,
     emotion="outraged squeak")
line("L06", "YOU", "flat", "So you can find your phone when the phone that gets the codes is nicked.",
     "so you can find your phone when the phone that gets the codes is [nicked](+2).", speed=1.15, lips="OFF",
     emotion="fast, explaining while she stands up")
line("L07", "YOU", "flat", "Oi, camera. Heathrow. Now.", "oi, camera! [heathrow](/hˈiːθɹəʊ/)! now!", speed=0.95, gap=0.35,
     emotion="commanding, phone held up to the lens")
# Beat 2: dive 1, the den
line("L08", "HOODED", "den", "No code. No problem.", "no code. no [problem](+2).", speed=0.85, level="aside", fx="close",
     gap=1.2, lips="OFF", emotion="low, amused (after the 1.2 s dive)")
line("L09", "HOODED", "den", "New phone, is it? Let's make it spare parts.", "new phone, is it? let's make it spare parts.",
     speed=0.88, level="aside", fx="close", gap=0.3, lips="OFF", emotion="mocking, calls back her Part 1 line")
# Beat 3: panic and the fix, the flat
line("L10", "YOU", "flat", "He's wiping my NEW phone. From a shed near Heathrow!",
     "he's wiping my [new](+2) phone. from a shed near heathrow!", speed=1.2, pitch=1.0, level="shout", gap=0.8,
     emotion="panic into fury (after the dive back)", engine="chatterbox")
line("L11", "JESS", "flat", "Turn it off! Turn it OFF!", "turn it off! turn it [off](+2)!", speed=1.25, pitch=1.0,
     level="shout", gap=-0.05, emotion="flapping, squealing", engine="chatterbox")
line("L12", "YOU", "flat", "Doesn't help. It wipes the second it comes back on.",
     "doesn't help. it wipes the second it comes back [on](+2).", speed=1.15, gap=0.05, lips="OFF",
     emotion="snapping, thumbs already moving")
line("L13", "JESS", "flat", "Just ring Apple!", "just ring apple!", speed=1.15, pitch=1.0, gap=0.05,
     emotion="grabbing her own phone")
line("L14", "YOU", "flat", "He's two clicks away, Jess!", "he's two [clicks](+2) away, jess!", speed=1.12, gap=0.0,
     emotion="sharp")
line("L15", "YOU", "flat", "Password first, so he can't get back in.", "password first, so he can't get back [in](+2).",
     speed=1.1, level="aside", fx="close", gap=0.2, lips="OFF", emotion="focused, under her breath")
line("L16", "YOU", "flat", "New one. Long one. Not a biscuit.", "new one. long one. not a [biscuit](+2).", speed=1.0,
     level="aside", fx="close", gap=0.15, lips="OFF", emotion="typing through gritted teeth")
line("L17", "YOU", "flat", "Remove other devices... gone.", "remove other devices... gone.", speed=1.0, level="aside",
     fx="close", gap=0.2, lips="OFF", emotion="a tiny grim smile")
line("L18", "JESS", "flat", "Is he out?!", "is he [out](+2)?!", speed=1.15, pitch=1.0, gap=0.1, emotion="hopeful")
line("L19", "YOU", "flat", "Not yet. He's still on the website. Camera!", "not yet. he's still on the [website](+2). camera!",
     speed=1.15, gap=0.05, emotion="urgent, points and the camera dives", engine="chatterbox")
# Beat 4: the race
line("L20", "HOODED", "den", "\"Are you sure?\" Oh, I'm sure. Last click, Biscuit.",
     "are you sure? oh, I'm [sure](+2). last click, biscuit.", speed=0.85, level="aside", fx="close", gap=0.8,
     lips="OFF", emotion="reading the confirm box, savouring it (after the dive)")
line("L21", "YOU", "flat", "Settings... \"Sign out of all browsers\"...", "settings... sign out of all browsers...", speed=1.15,
     level="aside", fx="close", gap=0.15, lips="OFF", emotion="reading fast under her breath")
line("L22", "JESS", "flat", "PRESS IT!", "press it!", speed=1.1, pitch=1.5, level="shout", gap=0.05,
     emotion="full scream", engine="chatterbox")
line("L23", "HOODED", "den", "...What?", "what?", speed=0.9, level="aside", fx="close", gap=0.55, lips="OFF",
     emotion="his screen bounced him out (after the two clicks)")
line("L24", "YOU", "flat", "Cheers, Biscuit.", "cheers, biscuit.", speed=1.04, gap=1.4,
     emotion="smug, straight down the lens (after he types the old password: Incorrect)")
# Beat 5: the sting and the payoff
line("L25", "HOODED", "flat", "Nice try. We know where Jess lives.", "nice try. we know where [jess](+2) lives.", speed=0.85,
     level="aside", fx="close", gap=0.7, lips="OFF", emotion="flat, cold voice-over as the text lands")
line("L26", "YOU", "flat", "Lovely. Screenshot. That's going straight to the police.",
     "lovely. screenshot. that's going straight to the police.", speed=1.0, gap=0.3,
     emotion="unbothered, shutter click")
line("L27", "JESS", "flat", "Good job I changed mine too... It's Biscuit124 now.",
     "good job I changed mine too... it's biscuit one two four now.", speed=1.1, pitch=1.0, gap=0.25,
     emotion="beaming, proud of herself (then You slow-turns to camera, hard cut)")
END_HOLD = 1.6  # the slow turn to camera after the last word, then the hard cut

REFS = {}  # Part 2 clones Part 1's Kokoro samples (out/chatterbox/ref_*.wav are copied from Part 1)

# music: (file, start (line, offset s), end (line, offset s) or None for a one-shot sting)
MUSIC = [
    ("C_journey", ("L02", -0.2), ("L07", -0.1)),    # sneaky, nervous: "he still needs my code, right?"
    ("B_race", ("L08", -1.25), ("L21", 0.4)),       # the full 2-step at 140 BPM drops in on dive 1 ... dropout before the press
    ("D_sofa", ("L24", -0.05), ("L27@biscuit", 0.0)),  # the lift on "Cheers, Biscuit"; stops dead on "Biscuit124"
    ("sting_biscuit", ("L25", -0.9), None),         # dark low note under the threat text
    ("sting_tapestop", ("L27@biscuit", -0.35), None),
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
    cb = os.path.join(OUT, "chatterbox", f"{ln['id']}.wav")
    use_cb = ln["engine"] == "chatterbox" and tts is None and os.path.exists(cb)
    if use_cb:  # emotional take from chatterbox_lines.py (same voice, cloned from a Kokoro sample)
        import soundfile as sf
        x, sr = sf.read(cb, dtype="float64")
        x = resample_poly(x, KSR // 1000, sr // 1000) if sr != KSR else x
        toks = json.load(open(cb.replace(".wav", "_words.json")))["words"]
    else:
        x, toks = synth(pipe, tts or ln["tts"], c["voice"], ln["speed"] * SPEED)
    # trim Kokoro's leading/trailing silence (keep 40 ms), shift word times to match
    thr = 0.01 * np.max(np.abs(x))
    nz = np.flatnonzero(np.abs(x) > thr)
    a = max(0, nz[0] - int(0.04 * KSR)) if len(nz) else 0
    b = min(len(x), nz[-1] + int(0.06 * KSR)) if len(nz) else len(x)
    x = x[a:b]
    toks = [dict(t, start=max(0.0, t["start"] - a / KSR), end=max(0.0, t["end"] - a / KSR)) for t in toks]
    for word, secs in ln["pauses"].items():  # a deliberate silence right after `word`, later words shift with it
        k = next((i for i, t in enumerate(toks) if t["text"].lower().strip(".,!?") == word), None)
        if k is None:
            print(f"  WARNING {ln['id']}: pause word '{word}' not found")
            continue
        nxt = next((t["start"] for t in toks[k + 1:] if t["text"][:1].isalnum()), toks[k]["end"] + 0.1)
        cut = int(min(toks[k]["end"] + 0.12, (toks[k]["end"] + nxt) / 2 + 0.03) * KSR)
        f = int(0.01 * KSR)
        x = x.copy(); x[cut - f:cut] *= np.linspace(1, 0, f)
        x = np.concatenate([x[:cut], np.zeros(int(secs * KSR)), x[cut:]])
        toks = [dict(t, start=t["start"] + secs, end=t["end"] + secs) if i > k else t for i, t in enumerate(toks)]
    if ln["bleep"]:
        hit = [t for t in toks if t["text"].lower().strip(".,!?") == ln["bleep"]]
        if hit:
            x = bleep(x, KSR, hit[0]["start"], hit[0]["end"], np.sqrt(np.mean(x ** 2)))
            hit[0]["text"] = "[bleep]"
        else:
            print(f"  WARNING {ln['id']}: word to bleep not found in timestamps, bleep it by hand")
    extra = 0.0 if use_cb else ln["pitch"]  # the Kokoro pitch lift faked panic; Chatterbox has the real thing
    chain = ",".join(p for p in [pitch_chain(c["pitch"] + extra, KSR), FX[ln["fx"]]] if p)
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
    ap.add_argument("--refs", action="store_true", help="only write the Kokoro voice samples Chatterbox clones")
    args = ap.parse_args()

    if args.mock:
        pipe = MockPipeline()
    else:
        from kokoro import KPipeline
        pipe = KPipeline(lang_code="b")  # British English

    for d in ("lines", "stems", "alts", "chatterbox"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    if args.refs:
        import soundfile as sf
        for who, txt in REFS.items():
            x, _ = synth(pipe, txt, CAST[who]["voice"], 1.0)
            sf.write(os.path.join(OUT, "chatterbox", f"ref_{who}.wav"), x / (np.max(np.abs(x)) + 1e-9) * 0.9, KSR)
            print(f"ref_{who}.wav {len(x) / KSR:.1f} s")
        return

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
        start = max(prev_start + 0.15, t + ln["gap"]) if tl else PRE
        # the line "ends" at its last spoken word: breath and effect tails overlap the next line (no dead air)
        spoken = [w for w in words[ln["id"]] if w["text"][:1].isalnum() or w["text"] == "[bleep]"]
        end = start + (min(len(x) / SR, spoken[-1]["end"] + 0.06) if spoken else len(x) / SR)
        tl.append(dict(id=ln["id"], who=ln["who"], scene=ln["scene"], start=round(start, 3), end=round(end, 3),
                       text=ln["text"], lips=ln["lips"], emotion=ln["emotion"]))
        prev_start, t = start, max(t, end)
    total = max(t, max(r["start"] for r in tl) + len(clips[L[-1]["id"]]) / SR) + END_HOLD
    N = ns(total)
    voice = np.zeros(N)
    stems = {w: np.zeros(N) for w in CAST}
    for ln, row in zip(L, tl):
        x = clips[ln["id"]]
        i = ns(row["start"])
        voice[i: i + len(x)] += x[: N - i]
        stems[ln["who"]][i: i + len(x)] += x[: N - i]
    echo = read_wav(os.path.join(P1, "lines", "L31_YOU.wav"))[0]
    echo = echo if echo.ndim == 1 else echo.mean(0)
    w31 = json.load(open(os.path.join(P1, "lines", "_words.json")))["L31"]
    e0 = 0  # the whole scream and its echoes (the cold open)
    tail_ = echo[e0:].copy(); f = ns(0.004); tail_[:f] *= np.linspace(0, 1, f)
    voice[: len(tail_)] += tail_[:N]
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

    # music: segments looped/cropped between their anchors, stings one-shot, ducked under the voice
    starts = {r["id"]: r["start"] for r in tl}

    def at(a):
        lid, off = a
        if "@" in lid:
            lid, wd = lid.split("@")
            hit = [w for w in words[lid] if w["text"].lower().strip(".,!?") == wd]
            return starts[lid] + (hit[0]["start"] if hit else 0.0) + off
        return starts[lid] + off

    music = np.zeros((2, N))
    for name, a, b in MUSIC:
        p = os.path.join(OUT, f"{name}.wav") if os.path.exists(os.path.join(OUT, f"{name}.wav")) else os.path.join(P1, f"{name}.wav")
        x, _ = read_wav(p)
        x = x if x.ndim == 2 else np.stack([x, x])
        t0 = at(a)
        skip = ns(max(0.0, -t0))  # a sting that starts before 0 s: only its tail plays
        t0 = max(0.0, t0)
        if b is not None:
            need = ns(at(b) - t0)
            y = np.tile(x, int(np.ceil(need / x.shape[1])) + 1)[:, :need]
            f = min(ns(0.15), need // 2)
            g = ns(0.03) if name == "D_sofa" else f  # D_sofa stops dead: the tape-stop sting carries the slowdown
            y[:, :f] *= np.linspace(0, 1, f)[None, :]
            y[:, -g:] *= np.linspace(1, 0, g)[None, :]
        else:
            y = x[:, skip:]
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
