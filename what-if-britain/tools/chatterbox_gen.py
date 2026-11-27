"""Chatterbox worker: performs lines in a reference voice. Runs inside /root/cb-venv; tools/cast_voice.py calls it.

usage: /root/cb-venv/bin/python tools/chatterbox_gen.py jobs.json
jobs.json: [{"text", "ref", "exaggeration", "cfg", "seed", "out"}, ...]  (out = .wav, 24 kHz mono)
The model loads once per call (~16 s on CPU); each line then takes about 7x its length.
"""
import inspect, json, os, sys, time

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")  # plain HTTPS through the allowed CDN host
import torch, torchaudio
from chatterbox.tts import ChatterboxTTS

jobs = json.load(open(sys.argv[1]))
torch.set_num_threads(os.cpu_count() or 4)
t0 = time.time()
model = ChatterboxTTS.from_pretrained(device="cpu")
known = set(inspect.signature(model.generate).parameters)
print(f"chatterbox loaded in {time.time() - t0:.0f} s; {len(jobs)} line(s) to perform", flush=True)
for j in jobs:
    t = time.time()
    torch.manual_seed(int(j["seed"]))
    kw = dict(audio_prompt_path=j["ref"], exaggeration=float(j["exaggeration"]), cfg_weight=float(j["cfg"]))
    if "temperature" in known and "temperature" in j:
        kw["temperature"] = float(j["temperature"])
    wav = model.generate(j["text"], **kw)
    torchaudio.save(j["out"], wav, model.sr)
    print(f"  {os.path.basename(j['out'])}: {wav.shape[-1] / model.sr:.1f} s in {time.time() - t:.0f} s", flush=True)
