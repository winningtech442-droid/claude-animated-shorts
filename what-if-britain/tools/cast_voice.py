"""Cast voices (v3): every line performed by Chatterbox in the character's approved voice (voices/<speaker>.wav).

usage: python3 -I tools/cast_voice.py src/episodes/<id>/voice.txt out/<id> [--upto N]
  --upto N  only the first N lines (e.g. the cold open for the 10-20 s test render)

voice.txt, one line per row:   speaker|exaggeration|cfg|pause|text[|fx]
  speaker       narrator, alfie, mate, nan, producer, or a guest with an approved voices/<guest>.wav
  exaggeration  0.4-0.5 calm, 0.6-0.8 lively, 0.9-1.3 panic or shouting
  cfg           about 0.5 normally, about 0.3 for dramatic lines (stops excited lines rushing)
  pause         seconds of silence after the line (negative overlaps the next line)
  text          *word* = the caption pop word; {2016|twenty sixteen} = shown as 2016, spoken as words
  fx            comma list: talkback (Booth, phones), muffle, tempo=1.1, gain=+2, take=2 (another performance),
                bleep=WORD (tone over the word, caption shows it starred), cut=WORD@0.55 (cut the line that far into
                the last WORD: write a few words past it so the voice keeps going up, e.g. "...know that it really")
Rows starting with # are notes.

Writes:  out/<id>/vo.wav (48 kHz, whole voice at -16 LUFS, limiter at -1.5 dBFS), out/<id>/voice/NN_<speaker>.wav,
         src/episodes/<id>/lines.json (each line's start/end) and src/episodes/<id>/words.json (every caption word with
         start, end and speaker; same shape as before, plus "speaker").
Performances are cached in out/<id>/voice/raw/ by speaker, text, settings and take, so a retake only redoes that line.
"""
import hashlib, json, math, os, re, subprocess, sys, tempfile
import numpy as np, soundfile as sf, pyloudnorm as pyln

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CB_PY = "/root/cb-venv/bin/python"
SR = 48000
FILTERS = {
    "talkback": "highpass=f=320,lowpass=f=3300,acompressor=threshold=0.08:ratio=4:attack=5:release=60,volume=3dB,asoftclip=type=tanh",
    "muffle": "lowpass=f=650,lowpass=f=650,volume=-3dB",
}


def parse(path, upto):
    rows = []
    for raw in open(path, encoding="utf-8"):
        raw = raw.rstrip("\n")
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        f = re.split(r"\|(?![^{]*\})", raw)  # a | inside {display|spoken} is not a column
        if len(f) < 5:
            sys.exit(f"bad row (needs speaker|exaggeration|cfg|pause|text[|fx]): {raw}")
        fx = {}
        for item in (f[5].split(",") if len(f) > 5 else []):
            item = item.strip()
            if item:
                k, _, v = item.partition("=")
                fx[k.strip()] = v.strip() or True
        rows.append(dict(speaker=f[0].strip().lower(), exaggeration=float(f[1]), cfg=float(f[2]), pause=float(f[3]),
                         text=f[4].strip(), fx=fx))
    return rows[:upto] if upto else rows


def tokens(text):
    """[(display, [spoken words])] for every caption token of a line."""
    out = []
    for tok in re.findall(r"\{[^}]*\}\S*|\S+", text):
        m = re.match(r"\{([^|}]*)\|([^}]*)\}(\S*)", tok)
        if m:
            out.append((m.group(1) + m.group(3), m.group(2).lower().split()))
        else:
            words = [w for w in re.split(r"[-–—/]", re.sub(r"[^\w'\-–—/]", "", tok.replace("*", ""))) if w.strip("'")]
            out.append((tok, [w.strip("'").lower() for w in words]))
    return out


def spoken_text(text):
    return re.sub(r"\{[^|}]*\|([^}]*)\}", r"\1", text).replace("*", "")


def load(path, sr=SR):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def ffx(x, chain):
    if not chain:
        return x
    a, b = tempfile.mktemp(suffix=".wav"), tempfile.mktemp(suffix=".wav")
    sf.write(a, x, SR, subtype="FLOAT")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a, "-af", chain, "-ar", str(SR), "-c:a", "pcm_f32le", b], check=True)
    y = load(b)
    os.remove(a); os.remove(b)
    return y


def trim(x, pre=0.04, post=0.08):
    hop = SR // 100
    n = len(x) // hop
    db = 10 * np.log10(np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    on = np.where(db > max(-50.0, db.max() - 40))[0]
    if not len(on):
        return x
    a, b = max(0, on[0] * hop - int(pre * SR)), min(len(x), (on[-1] + 1) * hop + int(post * SR))
    return x[a:b]


def align(x, toks):
    """Word times (s) within a line: pocketsphinx forced alignment, else spread by syllables over the voiced part."""
    words = [(i, w) for i, (_, ws) in enumerate(toks) for w in ws]
    times = None
    try:
        from pocketsphinx import Decoder
        dec = Decoder(samprate=16000, bestpath=False)
        say = []
        for _, w in words:
            say.append(w if dec.lookup_word(w) is not None else " ".join(re.sub(r"[^a-z]", "", w)) or "a")
        pcm = (np.clip(x[:: SR // 16000], -1, 1) * 32767).astype(np.int16)
        dec.set_align_text(" ".join(say))
        dec.start_utt(); dec.process_raw(pcm.tobytes(), full_utt=True); dec.end_utt()
        segs = [(g.start_frame / 100, (g.end_frame + 1) / 100) for g in (dec.seg() or [])
                if g.word not in ("<s>", "</s>", "<sil>", "(NULL)") and not g.word.startswith(("[", "+"))]
        n_expected = sum(len(s.split()) for s in say)
        if len(segs) == n_expected:
            it, times = iter(segs), []
            for s in say:
                parts = [next(it) for _ in s.split()]
                times.append((parts[0][0], parts[-1][1]))
    except Exception as e:  # noqa: BLE001
        print(f"    (alignment fallback: {e})")
    if times is None:
        hop = SR // 100
        n = len(x) // hop
        db = 10 * np.log10(np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
        on = np.where(db > db.max() - 35)[0]
        t0, t1 = (on[0] / 100, (on[-1] + 1) / 100) if len(on) else (0, len(x) / SR)
        syl = [max(1, len(re.findall(r"[aeiouy]+", w))) for _, w in words]
        tot, acc, times = sum(syl), 0, []
        for s in syl:
            times.append((t0 + (t1 - t0) * acc / tot, t0 + (t1 - t0) * (acc + s) / tot)); acc += s
    per_tok = {}
    for (i, _), t in zip(words, times):
        a, b = per_tok.get(i, (t[0], t[1]))
        per_tok[i] = (min(a, t[0]), max(b, t[1]))
    return per_tok


def main():
    args = sys.argv[1:]
    upto = 0
    if "--upto" in args:
        i = args.index("--upto"); upto = int(args[i + 1]); del args[i:i + 2]
    src, out = args[0], args[1]
    ep_dir = os.path.dirname(os.path.abspath(src))
    vdir, rdir = os.path.join(out, "voice"), os.path.join(out, "voice", "raw")
    os.makedirs(rdir, exist_ok=True)
    rows = parse(src, upto)

    missing = sorted({r["speaker"] for r in rows if not os.path.exists(os.path.join(ROOT, "voices", r["speaker"] + ".wav"))})
    if missing:
        sys.exit(f"no approved voice for: {', '.join(missing)}. Make voices/<name>.wav and get the user's OK first.")

    jobs = []
    for r in rows:
        key = f"{r['speaker']}|{spoken_text(r['text'])}|{r['exaggeration']}|{r['cfg']}|{r['fx'].get('take', 1)}"
        h = hashlib.sha1(key.encode()).hexdigest()[:12]
        r["raw"] = os.path.join(rdir, f"{r['speaker']}_{h}.wav")
        if not os.path.exists(r["raw"]):
            jobs.append(dict(text=spoken_text(r["text"]), ref=os.path.join(ROOT, "voices", r["speaker"] + ".wav"),
                             exaggeration=r["exaggeration"], cfg=r["cfg"], seed=int(h[:8], 16), out=r["raw"]))
    if jobs:
        jf = os.path.join(vdir, "jobs.json")
        json.dump(jobs, open(jf, "w"), indent=1)
        subprocess.run([CB_PY, os.path.join(ROOT, "tools", "chatterbox_gen.py"), jf], check=True)
    print(f"{len(rows)} line(s), {len(jobs)} newly performed, {len(rows) - len(jobs)} from cache")

    lines, words, t, parts = [], [], 0.0, []
    for n, r in enumerate(rows, 1):
        x = trim(load(r["raw"]))
        if "tempo" in r["fx"]:
            x = ffx(x, f"atempo={float(r['fx']['tempo'])}")
        toks = tokens(r["text"])
        wt = align(x, toks)
        disp = [d for d, _ in toks]
        if "cut" in r["fx"]:
            word, _, frac = str(r["fx"]["cut"]).partition("@")
            frac = float(frac or 0.5)
            hits = [i for i, (_, ws) in enumerate(toks) if word.lower() in ws and i in wt]
            if not hits:
                sys.exit(f"line {n}: cut word {word!r} not found in {r['text']!r}")
            i = hits[-1]
            a, b = wt[i]
            cut_t = a + frac * (b - a)
            x = x[: int(cut_t * SR)].copy()
            k = int(0.008 * SR); x[-k:] *= np.linspace(1, 0, k)
            base = re.sub(r"[^\w']", "", disp[i].replace("*", ""))
            shown = base if frac >= 0.5 else base[: max(1, math.ceil(len(base) * frac))]
            disp = disp[:i] + [shown + "–"]
            wt = {j: v for j, v in wt.items() if j < i} | {i: (a, cut_t)}
        if "bleep" in r["fx"]:
            bw = str(r["fx"]["bleep"]).lower()
            for i, (_, ws) in enumerate(toks):
                if bw in ws and i in wt and i < len(disp):
                    a, b = wt[i]
                    s, e = max(0, int((a - 0.02) * SR)), min(len(x), int((b + 0.02) * SR))
                    rms = float(np.sqrt(np.mean(x[s:e] ** 2))) if e > s else 0.1
                    tt = np.arange(e - s) / SR
                    tone = np.sin(2 * np.pi * 1000 * tt) * min(0.5, rms * 1.4)
                    f = min(len(tone) // 2, int(0.01 * SR))
                    if f:
                        tone[:f] *= np.linspace(0, 1, f); tone[-f:] *= np.linspace(1, 0, f)
                    x[s:e] = tone
                    d = disp[i]
                    core = re.search(r"[A-Za-z']+", d.replace("*", "")).group(0)
                    disp[i] = d.replace(core, core[0] + "*" * (len(core) - 1), 1)
        chain = ",".join([FILTERS[k] for k in ("talkback", "muffle") if k in r["fx"]] +
                         ([f"volume={float(r['fx']['gain']):+.1f}dB"] if "gain" in r["fx"] else []))
        x = ffx(x, chain)
        fn = os.path.join(vdir, f"{n:02d}_{r['speaker']}.wav")
        sf.write(fn, x, SR, subtype="FLOAT")
        start, dur = t, len(x) / SR
        parts.append((start, x))
        lines.append(dict(i=n, speaker=r["speaker"], text=" ".join(disp), start=round(start, 3), end=round(start + dur, 3),
                          exaggeration=r["exaggeration"], cfg=r["cfg"], fx=r["fx"], file=os.path.relpath(fn, out)))
        for i, d in enumerate(disp):
            if i in wt:
                a, b = wt[i]
                words.append(dict(text=d, start=round(start + a, 3), end=round(start + min(b, dur), 3), speaker=r["speaker"], line=n))
        t = start + dur + r["pause"]

    total = max(s + len(x) / SR for s, x in parts)
    vo = np.zeros(int(math.ceil(total * SR)) + SR // 10, np.float32)
    for s, x in parts:
        i = int(round(s * SR)); vo[i:i + len(x)] += x
    gain = -16.0 - pyln.Meter(SR).integrated_loudness(vo)
    raw_path = os.path.join(out, "vo_raw.wav")
    sf.write(raw_path, vo * 10 ** (gain / 20), SR, subtype="FLOAT")
    vo_path = os.path.join(out, "vo.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw_path, "-af", "alimiter=limit=0.84:attack=3:release=60:level=disabled",
                    "-c:a", "pcm_f32le", vo_path], check=True)
    os.remove(raw_path)
    json.dump(lines, open(os.path.join(ep_dir, "lines.json"), "w"), indent=1)
    json.dump(words, open(os.path.join(ep_dir, "words.json"), "w"), indent=0)
    e = subprocess.run(["ffmpeg", "-i", vo_path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    lra = e.split("LRA:")[-1].split("LU")[0].strip() if "LRA:" in e else "?"
    print(f"{vo_path}: {total:.2f} s, {len(lines)} lines, {len(words)} caption words, loudness range {lra} LU")
    for L in lines:
        print(f"  {L['i']:2d} {L['start']:6.2f}-{L['end']:6.2f}  {L['speaker']:9s} {L['text']}")


if __name__ == "__main__":
    main()
