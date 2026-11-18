import os, subprocess, sys, shutil
from multiprocessing import Pool
import ep3 as ep1

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_ep3"); os.makedirs(OUT, exist_ok=True)

def one(args):
    d, i, gt = args
    svg = ep1.frame(gt).encode()
    subprocess.run(["rsvg-convert", "-o", f"{d}/{i:05d}.png"], input=svg, check=True)

def seg(name, s, dur):
    final = f"{OUT}/{name}.mp4"
    if os.path.exists(final): return
    d = f"{OUT}/fr_{name}"; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    n = round(dur * ep1.FPS)
    with Pool(os.cpu_count()) as p: p.map(one, [(d, i, s + i / ep1.FPS) for i in range(n)], chunksize=8)
    tmp = f"{OUT}/{name}.tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", "30", "-i", f"{d}/%05d.png", "-c:v", "libx264", "-crf", "18",
                    "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", tmp], check=True)
    os.rename(tmp, final); shutil.rmtree(d)
    print("done", name, flush=True)

if __name__ == "__main__":
    only = sys.argv[1:]
    for name, s, d in ep1.SEG:
        if not only or name in only: seg(name, s, d)
    with open(f"{OUT}/list.txt", "w") as f:
        for name, s, d in ep1.SEG: f.write(f"file '{OUT}/{name}.mp4'\n")
    print("ALL DONE", flush=True)
