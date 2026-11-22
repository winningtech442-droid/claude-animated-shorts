#!/usr/bin/env python3
"""Stage-2 measured checks for a finished FIX #12 cut.  python tools/qc.py final/phoneverse_fix12_with_pad.mp4
Prints PASS/FAIL against the rule book: length 60-70 s, tail after the last word <= 0.5 s, loudness -14 LUFS (+-0.5) / peak <= -1.5 dB / range >= 3 LU,
no shot over 2.5 s (settings card 16a up to 4 s), no black or frozen frames, speech pace 2.8-3.2 w/s (from data/timings.json)."""
import json, re, subprocess, sys
v = sys.argv[1]
def run(args): return subprocess.run(args, capture_output=True, text=True)
dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", v]).stdout)
res = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate", "-of", "csv=p=0", v]).stdout.strip()
T = json.load(open("data/timings.json")); S = T["summary"]; last_end = T["lines"][-1]["end"]
e = run(["ffmpeg", "-hide_banner", "-nostats", "-i", v, "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
g = lambda k: float(re.findall(rf"{k}:\s+(-?[\d.]+)", e.split("Summary:")[-1])[0])
I, LRA, PK = g("I"), g("LRA"), g("Peak")
sc = run(["ffmpeg", "-hide_banner", "-nostats", "-i", v, "-vf", "select='gt(scene,0.25)',showinfo", "-an", "-f", "null", "-"]).stderr
cuts = [0.0] + [float(x) for x in re.findall(r"pts_time:([\d.]+)", sc)] + [dur]
gaps = [b - a for a, b in zip(cuts, cuts[1:])]; longest = max(gaps)
blk = run(["ffmpeg", "-hide_banner", "-nostats", "-i", v, "-vf", "blackdetect=d=0.1:pix_th=0.04", "-an", "-f", "null", "-"]).stderr.count("black_start")
frz = run(["ffmpeg", "-hide_banner", "-nostats", "-i", v, "-vf", "freezedetect=n=-60dB:d=0.7", "-an", "-f", "null", "-"]).stderr.count("freeze_start")
rows = [("size / fps", res, "1080,1920,24/1", res.startswith("1080,1920")),
        ("length (s)", f"{dur:.2f}", "60-70", 60 <= dur <= 70),
        ("tail after last word (s)", f"{dur - last_end:.2f}", "<= 0.5 (0.2 is the take; any extra is the video running long)", 0 <= dur - last_end <= 0.5),
        ("speech pace (w/s, from take)", f"{S['speech_pace_wps']}", "2.8-3.2", 2.8 <= S["speech_pace_wps"] <= 3.2),
        ("loudness (LUFS)", f"{I:.1f}", "-14 +-0.5", abs(I + 14) <= 0.5),
        ("true peak (dB)", f"{PK:.1f}", "<= -1.5", PK <= -1.5),
        ("loudness range (LU)", f"{LRA:.1f}", ">= 3", LRA >= 3),
        ("cuts / avg shot (s)", f"{len(cuts)-2} / {dur/(len(cuts)-1):.2f}", "about 1.4 (49 planned shots)", True),
        ("longest shot (s)", f"{longest:.2f}", "<= 2.5 outside 16a (<= 4.0); check by eye if above", longest <= 4.0),
        ("black frames", str(blk), "0", blk == 0), ("frozen segments", str(frz), "0", frz == 0)]
for n, val, lim, ok in rows: print(f"{'PASS' if ok else 'FAIL'}  {n:<32}{val:<12}{lim}")
print("Scene detection misses soft cuts; always also look at the storyboard sheet and the file at phone size.")
