# Voices + rough mix for Phoneverse "Cheers, Biscuit" Part 3, "Free Upgrade". Same engine as Parts 1-2.
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
    "BANK": dict(voice="bf_alice", pitch=0.0),
}

# ------------------------------------------------------------------ level presets (target loudness per line, LUFS)
LEVEL = {"normal": -16.0, "shout": -14.5, "aside": -18.5, "distant": -18.0, "phone": -16.0}

# ------------------------------------------------------------------ effect presets (ffmpeg filter chains)
FX = {
    None: "",
    "shout": "highpass=f=110,acompressor=threshold=0.08:ratio=5:attack=4:release=90:makeup=2",
    "away": "lowpass=f=4200,aecho=0.8:0.55:70:0.22",  # shouting at a camera that is leaving her
    "echo": "apad=pad_dur=1.4,aecho=1.0:0.45:520|1040:0.28|0.14",  # "JESS!" then its echo (late + soft, so the J stays crisp)
    "close": "highpass=f=70,lowpass=f=7000,acompressor=threshold=0.1:ratio=3:attack=10:release=150:makeup=1.5",
    # a phone line: 300-3,400 Hz band, a little mid honk, squashed (the caller and the "bank")
    "phone": "highpass=f=300,highpass=f=300,lowpass=f=3400,lowpass=f=3400,equalizer=f=1600:t=q:w=1.2:g=4,acompressor=threshold=0.08:ratio=6:attack=3:release=60:makeup=2.5",
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



# Part 1's music beds and stings are reused (re-arranged); Part 2's 140 BPM race bed is in out/B_race.wav
P1 = os.path.join(HERE, "..", "..", "phoneverse-found-text", "audio", "out")
PRE = 0.35  # street noise and swinging bags, then straight into Jess's squeal

# The hooded figure's "call-centre" voice: same man, pitched up (net +2 semitones), faster, through a phone line.
CALL = dict(pitch=5.0, fx="phone", level="phone", lips="OFF")

# Beat 1: cold open, Oxford Street on Black Friday
line("L01", "JESS", "street", "A free upgrade? For me?!", "a [free](+2) upgrade? for me?!", speed=1.12, pitch=1.0, gap=0.0,
     emotion="squealing, delighted, phone at her ear, bags swinging: the hook", engine="chatterbox")
line("L02", "HOODED", "street", "Hiya, is that Jess? This is a Black Friday loyalty offer. And you're one of our favourites.",
     "[hiya](/hˈaɪjə/), is that jess? this is a black friday loyalty offer. and you're one of our [favourites](+2).", speed=1.08,
     gap=0.15, emotion="polished, official-sounding, warm, over the phone", **CALL)
line("L03", "YOU", "street", "Keep walking. Eyes on the cyclists.", "keep walking. eyes on the [cyclists](+2).", speed=1.05,
     gap=0.1, emotion="paranoid, phone clamped to her chest, scanning the crowd, not listening")
# Beat 2: the code
line("L04", "HOODED", "street", "I've just sent you a little code there. Read it back for me?",
     "I've just sent you a little [code](+2) there. read it back for me?", speed=1.05, gap=0.25,
     emotion="routine and official, like it's nothing", **CALL)
line("L05", "JESS", "street", "Four... eight...", "four... [eight](+2)...", speed=0.95, gap=0.6, pauses={"four": 0.3},
     emotion="reading slowly off the screen, juggling bags (after the text buzz)")
line("L06", "JESS", "street", "Ooh, it says \"never share this code\".", "ooh, it says... never share this [code](+2).",
     speed=1.05, pitch=0.5, gap=0.35, emotion="mildly puzzled, almost catching it")
line("L07", "HOODED", "street", "That's for strangers, Jess. I'm your network.",
     "that's for [strangers](+2), jess. I'm your network.", speed=1.0, gap=0.1, emotion="warm, a tiny laugh, smooth",
     **CALL)
line("L08", "JESS", "street", "Aww, bless. Two...", "aww, bless. [two](+2)...", speed=1.0, gap=0.2, emotion="reassured, charmed")
# Beat 3: the tell
line("L09", "JESS", "street", "Can I ring you back, actually? My hands are full.",
     "can I ring you [back](+2), actually? my hands are full.", speed=1.1, gap=0.35, emotion="breezy, bags slipping")
line("L10", "HOODED", "street", "That wouldn't be good. The offer expires in two minutes!",
     "that wouldn't be good. the offer expires in two [minutes](+2)!", speed=1.2, gap=0.05,
     emotion="the mask slips: still polite, but pushy and a bit too quick", **CALL)
line("L11", "JESS", "street", "Okay, okay! Nine...", "okay, okay! [nine](+2)...", speed=1.15, pitch=1.0, gap=0.15,
     emotion="flustered, rushing")
# Beat 4: You clocks it
line("L12", "YOU", "street", "Jess. What code?!", "jess. what code?", speed=1.0, gap=0.1, emotion="spinning round, ice-cold dread")
line("L13", "YOU", "street", "Oi, camera. Who is that?", "oi, camera! who [is](+2) that?", speed=0.95, gap=0.3,
     emotion="an order, glaring down the lens")
# Beat 5: the dive and the den
line("L14", "HOODED", "den", "Two more digits, and her number's mine.", "two more digits, and her [number's](+2) mine.",
     speed=0.88, level="aside", fx="close", gap=1.2, lips="OFF", emotion="low and flat, MUTE pressed (after the 1.2 s dive)")
line("L15", "HOODED", "den", "Still there, Jess?", "still there, [jess](+2)?", speed=1.05, gap=0.3,
     emotion="unmuted, sugary again", **CALL)
# Beat 6: too late
line("L16", "YOU", "street", "Jess, hang up!", "jess, hang [up](+2)!", speed=1.15, pitch=1.0, level="shout", gap=0.6,
     emotion="shouting, lunging for the phone", engine="chatterbox")
line("L17", "JESS", "street", "One... three! Done!", "one... [three](+2)! done!", speed=1.1, pitch=1.0, gap=0.0,
     pauses={"one": 0.25}, emotion="twirling away from You with her bags, proud")
line("L18", "HOODED", "street", "Lovely. Enjoy your upgrade.", "lovely. enjoy your [upgrade](+2).", speed=1.0, gap=0.15,
     emotion="satisfied, then click", **CALL)
# Beat 7: No Service
line("L19", "JESS", "street", "...Why's it saying No Service?", "why's it saying... no [service](+2)?", speed=0.95, gap=1.2,
     emotion="small, confused (after the click, the bars drain, the boxes crumble)")
# Beat 8: the reveal
line("L20", "YOU", "street", "That wasn't an upgrade, Jess. You just gave him your number.",
     "that wasn't an upgrade, jess. you just gave him your [number](+2).", speed=0.95, gap=0.4, emotion="quiet, deadly calm")
line("L21", "YOU", "street", "Every code your bank texts you goes to him now.",
     "every code your bank texts you goes to [him](+2) now.", speed=1.0, gap=0.15, emotion="spelling it out")
line("L22", "JESS", "street", "My BANK?!", "my [bank](+2)?!", speed=1.1, pitch=1.5, level="shout", gap=0.1,
     emotion="full shriek, pigeons scatter", engine="chatterbox")
# Beat 9: the fix
line("L23", "YOU", "street", "Ring your network. From my phone.", "ring your network. from [my](+2) phone.", speed=1.1,
     gap=0.45, emotion="taking charge, handing it over")
line("L24", "YOU", "street", "Number from their website. Not from a text.", "number from their website. not from a [text](+2).",
     speed=1.12, gap=0.15, lips="OFF", emotion="fast, firm (screen insert)")
line("L25", "JESS", "street", "Someone's stolen my number! Block it! Block it!",
     "someone's stolen my [number](+2)! block it! block it!", speed=1.2, pitch=1.0, level="shout", gap=0.6,
     emotion="frantic into You's phone", engine="chatterbox")
line("L26", "YOU", "street", "Now your bank.", "now your [bank](+2).", speed=1.05, gap=0.3, emotion="already dialling")
line("L27", "HOODED", "den", "...No service?", "no... [service](+2)?", speed=0.88, level="aside", fx="close", gap=0.7,
     lips="OFF", emotion="shaking his dead phone, flat, deflated (after the whoomp)")
# Beat 10: the payoff
line("L28", "BANK", "street", "Hi Jess, it's your bank...", "hi jess, it's your [bank](+2)...", speed=1.0, gap=1.2,
     fx="phone", level="phone", lips="OFF", emotion="neutral, polite. Is it real? We never find out (after the ring)")
line("L29", "JESS", "street", "Lovely! I'll ring you back on the number on my card.",
     "lovely! I'll ring you back on the number on my [card](+2).", speed=1.08, pitch=0.5, gap=0.2,
     emotion="bright, breezy, hangs up")
line("L30", "YOU", "street", "Jess! What if that was really them?!", "jess! what if that was [really](+2) them?!", speed=1.12,
     pitch=1.0, gap=0.3, emotion="horrified", engine="chatterbox")
line("L31", "JESS", "street", "Then they won't mind, will they?", "then they won't [mind](+2), will they?", speed=0.95,
     gap=0.3, emotion="smug for the first time in the series. Hard cut")
END_HOLD = 0.7  # a beat on her smug face, then the hard cut

REFS = {}  # Part 3 clones the same Kokoro samples as Parts 1-2 (out/chatterbox/ref_*.wav are copied from Part 2)

# music: (file, start (line, offset s), end (line, offset s) or None for a one-shot sting)
MUSIC = [
    ("B_snatch", ("L01", -0.35), ("L10", 0.05)),      # the street 2-step under the "deal"; drops out on "That wouldn't be good"
    ("C_journey", ("L11", 0.2), ("L18", 1.3)),        # creeps back, sneaky, through the code and the den; ends on the click
    ("sting_biscuit", ("L19", -1.0), None),            # dark low note: No Service
    ("B_race", ("L23", -0.15), ("L27", 1.0)),          # the fix: the 140 BPM groove lifts back in
    ("D_sofa", ("L28", -0.6), ("L31@mind", 0.0)),      # cosy for the payoff; stops dead on "mind"
    ("sting_tapestop", ("L31@mind", -0.35), None),
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
    from scipy.signal import butter, sosfiltfilt
    x = sosfiltfilt(butter(6, 10500, "lp", fs=KSR, output="sos"), x)  # no near-Nyquist fizz: it overshoots the true peak
    x48 = resample_poly(x, SR // 1000, KSR // 1000)
    x48 *= dbg(LEVEL[ln["level"]] - loudness(x48))
    return x48, toks


def tp_limit(mix, ceiling_db=-1.5):
    """true-peak limiter: finds the 4x-oversampled peaks, holds the gain down 2 ms either side, releases over 60 ms"""
    from scipy.ndimage import maximum_filter1d
    up = resample_poly(mix, 4, 1, axis=1)
    pk = np.abs(up).max(0)
    pk = pk[: (len(pk) // 4) * 4].reshape(-1, 4).max(1)
    pk = np.pad(pk, (0, mix.shape[1] - len(pk)), mode="edge")
    need = maximum_filter1d(np.maximum(1.0, pk / dbg(ceiling_db)), size=2 * ns(0.002) + 1)
    g = np.ones_like(need)
    cur, rel = 1.0, 1.0 / ns(0.06)
    for i in range(len(need)):
        cur = max(cur, need[i]) if need[i] > cur else cur + (need[i] - cur) * rel
        g[i] = cur
    return mix / g[None, :]


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
    mix = tp_limit(mix, -1.5)  # true peak stays under -1 dBTP after encoding
    write_wav(os.path.join(OUT, "music_ducked.wav"), music, bits=24)
    write_wav(os.path.join(OUT, "rough_mix.wav"), mix, bits=24)
    print(f"\nTotal {total:.1f} s | voice {integrated(np.stack([voice, voice])):.1f} LUFS | "
          f"music (ducked) {integrated(music):.1f} LUFS | mix {integrated(mix):.1f} LUFS")
    print("Wrote out/lines, out/stems, out/timeline.json, out/words.json, out/captions.srt, out/rough_mix.wav")


if __name__ == "__main__":
    main()
