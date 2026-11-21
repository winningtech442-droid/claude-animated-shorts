#!/usr/bin/env python3
"""Builds data/beats_fix15.json + data/chars_fix15.json from the measured FIX #15 take (never re-timed).
FIX #15 'Wallet hijack': one world (the desk: your phone, your bank card, the mast, the scammer's laptop and phone) plus CHARACTER
beats (user, 21 Nov: "the two well performing videos have characters acting"): the lead ("You", pink shirt) acting on a sofa at
night, and the hooded figure from behind at a laptop. Character beats render with render/char_scene.py.
Checks: beats contiguous, none over 2.5 s, a real cut between consecutive desk beats, last beat ends on the take.
  python3 data/make_beats_fix15.py      (run from phoneverse_3d_studio/)"""
import json
T = json.load(open("../phoneverse_fix15_studio/data/timings.json"))
def ev(type_, f, to, t0, t1): return {"type": type_, "from": f, "to": to, "t0": t0, "t1": t1}
def pk(kind, path, t0, t1, arc=0.18, bounce=None):
    e = {"type": "packet", "kind": kind, "path": path, "t0": t0, "t1": t1, "arc": arc}
    if bounce: e["bounce"] = bounce
    return e
SMS = "U.code_sms()"
BEATS = [
 # L1 hook: frame 1 = the glowing copy peels off your card and flies onto the scammer's phone
 dict(t0=0.0, t1=1.55, line=1, cam=["card_macro", "path_wide"], screen="U.lock_plain()", scam="U.scam_wallet('home')", events=[ev("ghost", 0, 1, 0.05, 1.45)]),
 dict(t0=1.55, t1=3.093, line=1, cam=["scam", "scam_close"], scam="U.scam_wallet('ready', p * 2)",
      labels=[{"anchor": "scamphone", "text": "A STRANGER'S PHONE", "dx": -300, "dy": -360, "from": 1.8}]),
 # L2 but it's still in your pocket (the lead, confused) -- the copy goes back for the story, unseen
 dict(t0=3.093, t1=5.285, line=2, char="c02_pocket", events=[ev("ghost", 1, 0, 3.10, 3.11)]),
 # L3 one code
 dict(t0=5.285, t1=7.477, line=3, cam=["screen_close", "screen_tilt"], screen="U.big_code(p * 2)", inset=False,
      labels=[{"anchor": "screen", "text": "THAT'S ALL IT TOOK", "dx": -360, "dy": 330, "from": 6.0}]),
 # L4 the deal text
 dict(t0=7.477, t1=9.6, line=4, char="c04_deal"),
 dict(t0=9.6, t1=11.2, line=4, cam=["hero", "screen"], screen="U.deal_notice(p)"),
 dict(t0=11.2, t1=12.635, line=4, cam=["screen_tilt", "screen_close"], screen="U.deal_page(p)", hud={"label": "BLACK FRIDAY", "value": "-70%", "color": "ORANGE", "from": 11.4}),
 # L5 you type in your card
 dict(t0=12.635, t1=14.3, line=5, cam=["screen", "screen_close"], screen="U.checkout(p * 1.1)"),
 dict(t0=14.3, t1=15.552, line=5, char="c05_type"),
 # L6 at that same moment a scammer types it into a wallet on their phone
 dict(t0=15.552, t1=17.4, line=6, char="c06_hood"),
 dict(t0=17.4, t1=19.2, line=6, cam=["wide", "laptop"], screen="U.checkout(1)", events=[pk("card", "phone>laptop", 17.45, 18.55)],
      labels=[{"anchor": "laptop", "text": "SCAMMER", "dx": -340, "dy": -300, "from": 18.3}]),
 dict(t0=19.2, t1=20.752, line=6, cam=["scam_tilt", "scam_close"], scam="U.scam_wallet('add', p)", events=[pk("card", "laptop>scamphone", 19.0, 19.9, 0.08)],
      labels=[{"anchor": "scamphone", "text": "THEIR PHONE", "dx": -320, "dy": -340, "from": 19.5}]),
 # L7 your bank isn't sure it's you, so it texts you a code
 dict(t0=20.752, t1=22.4, line=7, cam=["mast", "hero"], screen="U.lock_plain()", scam="U.scam_wallet('add', 1)", events=[pk("text", "mast>phone", 20.85, 22.1)],
      labels=[{"anchor": "mast", "text": "YOUR BANK'S TEXT", "dx": 60, "dy": -260, "from": 21.0}]),
 dict(t0=22.4, t1=24.037, line=7, cam=["screen_tilt", "screen_close"], screen=SMS),
 # L8 the page asks for it. Or a fake fraud team calls and asks you to read it out
 dict(t0=24.037, t1=25.9, line=8, cam=["screen", "screen_tilt"], screen="U.otp_page(p)"),
 dict(t0=25.9, t1=27.6, line=8, cam=["hero", "screen_close"], screen="U.call_ring('Fraud Team')", events=[pk("call", "laptop>phone", 25.95, 27.0)],
      labels=[{"anchor": "screen", "text": "FAKE", "dx": 120, "dy": -380, "from": 26.6}]),
 dict(t0=27.6, t1=29.984, line=8, char="c08_call"),
 # L9 you hand it over... and your card goes live on their phone (the jump again, now we know how)
 dict(t0=29.984, t1=31.7, line=9, cam=["screen_tilt", "path_wide"], screen="U.otp_page(1)", scam="U.scam_wallet('add', 1)",
      events=[pk("text", "phone>laptop", 30.0, 30.75), ev("ghost", 0, 1, 30.55, 31.65)], labels=[{"anchor": "packet", "text": "THE CODE", "dx": 120, "dy": -260, "from": 30.1}]),
 dict(t0=31.7, t1=33.888, line=9, cam=["scam", "scam_close"], scam="U.scam_wallet('ready', p * 2)", labels=[{"anchor": "ghost", "text": "LIVE", "dx": 200, "dy": -330, "from": 32.2}]),
 # L10 now they tap to pay, in shops and online
 dict(t0=33.888, t1=35.7, line=10, cam=["scam_tilt", "scam"], scam="U.scam_wallet('paid', p)",
      events=[pk("card", "scamphone>mast", 34.0, 34.9, 0.12), pk("card", "scamphone>mast", 34.5, 35.4, 0.12)],
      hud={"label": "SPENT", "count": [0, 3499, "£"], "color": "RED", "from": 34.0, "until": 37.3}),
 dict(t0=35.7, t1=37.573, line=10, char="c10_hood", hud={"label": "SPENT", "count": [0, 3499, "£"], "color": "RED", "from": 34.0, "until": 37.3}),
 # L11 one man lost over £18,000 in a few hours
 dict(t0=37.573, t1=39.4, line=11, cam=["path_wide", "top"], screen="U.lock_plain()", scam="U.scam_wallet('paid', 1)",
      events=[pk("card", "scamphone>mast", 37.6, 38.4, 0.12), pk("card", "scamphone>mast", 37.9, 38.7, 0.12), pk("card", "scamphone>mast", 38.2, 39.0, 0.12)],
      hud={"label": "ONE MAN LOST", "count": [0, 18000, "£"], "color": "RED", "from": 37.7, "until": 39.2}),
 dict(t0=39.4, t1=41.755, line=11, char="c11_shock", hud={"label": "ONE MAN LOST", "value": "£18,000", "color": "RED"}),
 # L12 here's your shield: read the whole text
 dict(t0=41.755, t1=43.3, line=12, cam=["hero", "screen_close"], screen=SMS, hud={"label": "YOUR SHIELD", "value": "READ IT ALL", "color": "GREEN", "from": 42.0}),
 dict(t0=43.3, t1=44.907, line=12, char="c12_read", hud={"label": "YOUR SHIELD", "value": "READ IT ALL", "color": "GREEN"}),
 # L13 if it mentions adding a card to a wallet and that's not you? Stop.
 dict(t0=44.907, t1=47.0, line=13, cam=["screen_close", "screen"], screen="U.code_sms(hl=p * 1.5)"),
 dict(t0=47.0, t1=48.6, line=13, cam=["screen_tilt", "hero"], screen="U.code_sms(hl=1, stop=clamp((p - 0.25) * 2))"),
 dict(t0=48.6, t1=50.128, line=13, char="c13_stop"),
 # L14 no real bank will ever ask you for that code
 dict(t0=50.128, t1=51.7, line=14, cam=["wide", "screen_tilt"], screen="U.call_ring('Fraud Team', blocked=clamp((p - 0.2) * 1.5))", events=[pk("call", "laptop>phone", 50.15, 51.4, bounce=0.6)]),
 dict(t0=51.7, t1=53.136, line=14, cam=["screen", "screen_close"], screen="U.bank_never(p)"),
 # L15 got an alert that a card was added? call the number on your card
 dict(t0=53.136, t1=55.0, line=15, cam=["screen_tilt", "hero"], screen="U.wallet_alert(p)"),
 dict(t0=55.0, t1=56.3, line=15, cam=["card_top", "card_macro"], screen="U.wallet_alert(1)", events=[ev("cardflip", 0, 1, 55.05, 55.8)],
      labels=[{"anchor": "card", "text": "THIS NUMBER", "dx": 80, "dy": -380, "from": 55.6}]),
 dict(t0=56.3, t1=57.717, line=15, char="c15_callbank"),
 # L16 your bank can switch off their copy
 dict(t0=57.717, t1=59.2, line=16, cam=["scam_tilt", "scam"], scam="U.scam_wallet('ready' if p < 0.45 else 'removed')", events=[pk("call", "mast>scamphone", 57.75, 58.5, 0.12), ev("freeze", 0, 1, 58.35, 59.15)],
      labels=[{"anchor": "scamphone", "text": "SWITCHED OFF", "dx": -320, "dy": -340, "from": 58.6}]),
 dict(t0=59.2, t1=60.571, line=16, cam=["path_side", "path_wide"], screen="U.lock_plain()", scam="U.scam_wallet('removed')", hud={"label": "THEIR COPY", "value": "OFF", "color": "GREEN", "from": 59.3}),
 # L17 would you have read the code out? tell me below
 dict(t0=60.571, t1=62.0, line=17, char="c17_relief"),
 dict(t0=62.0, t1=63.493, line=17, cam=["hero", "screen"], screen="U.ask_dark('Would you have read it out?', p * 1.5)"),
 # L18 send this to anyone shopping this Black Friday
 dict(t0=63.493, t1=65.0, line=18, cam=["screen_close", "screen_tilt"], screen="U.share_dark('Jess', p * 1.4)"),
 dict(t0=65.0, t1=66.544, line=18, cam=["hero", "wide"], screen="U.share_dark('Jess', 1)", events=[ev("cardflip", 1, 0, 65.1, 65.8)]),
]
for b in BEATS:                                     # screen inset only when the hero phone is the subject (not on the card / scam phone / path shots)
    if not b.get("char") and not b["cam"][0].startswith(("hero", "screen")) and not b["cam"][1].startswith(("hero", "screen")): b.setdefault("inset", False)
for a, b in zip(BEATS, BEATS[1:]): assert abs(a["t1"] - b["t0"]) < 1e-6, (a["t0"], b["t0"])
for b in BEATS: assert b["t1"] - b["t0"] <= 2.5, b["t0"]
for a, b in zip(BEATS, BEATS[1:]):
    if not a.get("char") and not b.get("char"): assert a["cam"][1] != b["cam"][0], ("no real cut at", b["t0"])
assert abs(BEATS[-1]["t1"] - T["summary"]["take_length_s"]) < 0.01, (BEATS[-1]["t1"], T["summary"]["take_length_s"])

# ---- character clips (cameras are offsets from the actor's eye point: [cam offset, target offset, lens mm])
MED_PHONE = lambda dx=0.12: {"from": [[dx, -1.0, -0.08], [0, 0, -0.12], 50], "to": [[dx * 0.6, -0.88, -0.06], [0, 0, -0.10], 54], "focus": [0, -0.02, 0]}   # hands at the frame edge (character sheet: no hand close-ups)
CLIPS = [
 {"clip": "c02_pocket", "set": "sofa", "pose": "phone", "notes": "looks down at the phone, then up: confused, it's still in her pocket",
  "expr": [[0, "neutral", 0], [0.5, "dread", 0.6]], "look_down": [[0, 0.6], [0.8, 0.6], [1.3, 0.0]], "head": [[0, [0, 0, 10]], [1.3, [0, -6, 0]]], "cam": MED_PHONE(0.18)},
 {"clip": "c04_deal", "set": "sofa", "pose": "phone", "phone_bob": True, "notes": "the deal text buzzes in; hope",
  "expr": [[0, "neutral", 0], [0.6, "hope", 0.9]], "look_down": [[0, 0.7]], "head": [[0, [0, 0, 12]]],
  "cam": {"from": [[-0.16, -0.98, -0.06], [0, 0, -0.12], 50], "to": [[-0.08, -0.86, -0.05], [0, 0, -0.10], 54], "focus": [0, -0.02, 0]}},
 {"clip": "c05_type", "set": "sofa", "pose": "phone_up", "notes": "typing her card in, concentrating",
  "expr": [[0, "focus", 0.8]], "look_down": [[0, 0.8]], "head": [[0, [0, 0, 14]]], "nod": [0.1, 1.2],
  "cam": {"from": [[0.14, -0.95, 0.04], [0, 0, -0.12], 50], "to": [[0.10, -0.85, 0.02], [0, 0, -0.10], 54], "focus": [0, -0.02, 0]}},
 {"clip": "c06_hood", "set": "den", "pose": "type", "notes": "hooded figure from behind, typing your card into their phone's wallet",
  "cam": {"from": [[0.42, 0.72, 0.20], [0, -0.45, -0.42], 30], "to": [[0.30, 0.56, 0.12], [0, -0.48, -0.45], 34], "focus": [0, -0.42, -0.45]}},
 {"clip": "c08_call", "set": "sofa", "pose": "call", "notes": "on the phone to the 'fraud team', reading the code out",
  "expr": [[0, "dread", 0.55]], "talk": [[0.25, 2.2]], "head": [[0, [0, -8, 4]]],
  "cam": {"from": [[-0.26, -0.86, -0.06], [-0.02, 0, -0.08], 50], "to": [[-0.18, -0.76, -0.05], [-0.02, 0, -0.07], 55], "focus": [0, -0.02, 0]}},
 {"clip": "c10_hood", "set": "den", "pose": "type", "notes": "hooded figure leans back; payments go through",
  "spine": [[0, [0, 0, 0]], [1.2, [0, 0, -7]]],
  "cam": {"from": [[-0.60, 0.85, 0.28], [0, -0.40, -0.40], 28], "to": [[-0.50, 0.72, 0.22], [0, -0.44, -0.42], 30], "focus": [0, -0.30, -0.35]}},
 {"clip": "c11_shock", "set": "sofa", "pose": "phone_up", "notes": "she sees what happened: the snap",
  "expr": [[0, "dread", 0.3], [0.35, "shock", 1.0]], "look_down": [[0, 0.7], [0.35, 0.0]], "head": [[0, [0, 0, 10]], [0.4, [0, -8, -6]], [1.0, [0, -7, -2]]],
  "cam": {"from": [[0.0, -1.1, -0.15], [0, 0, -0.12], 45], "to": [[0.0, -0.80, -0.08], [0, 0, -0.08], 50], "focus": [0, -0.02, 0]}},
 {"clip": "c12_read", "set": "sofa", "pose": "phone_up", "notes": "reading the whole text, slowly",
  "expr": [[0, "focus", 0.8]], "look_down": [[0, 0.8]], "head": [[0, [0, 4, 14]]],
  "cam": {"from": [[-0.30, -0.85, -0.02], [0, 0, -0.12], 50], "to": [[-0.24, -0.76, -0.02], [0, 0, -0.10], 54], "focus": [0, -0.02, 0]}},
 {"clip": "c13_stop", "set": "sofa", "pose": [[0, "phone_up"], [0.7, "phone"]], "notes": "shakes her head and lowers the phone: stop",
  "expr": [[0, "focus", 0.8], [0.5, "dread", 0.4]], "shake": [0.15, 1.3], "look_down": [[0, 0.6], [0.6, 0.0]], "cam": MED_PHONE(0.10)},
 {"clip": "c15_callbank", "set": "sofa", "pose": "call", "notes": "calling the number on her card; steadier now",
  "expr": [[0, "focus", 0.5]], "talk": [[0.15, 1.35]], "nod": [0.2, 1.3], "head": [[0, [0, -6, 2]]],
  "cam": {"from": [[-0.22, -0.88, -0.05], [-0.02, 0, -0.08], 50], "to": [[-0.16, -0.78, -0.05], [-0.02, 0, -0.07], 54], "focus": [0, -0.02, 0]}},
 {"clip": "c17_relief", "set": "sofa", "pose": "phone", "notes": "relief; looks up to us",
  "expr": [[0, "neutral", 0], [0.3, "relief", 0.9]], "look_down": [[0, 0.5], [0.3, 0.0]], "head": [[0, [0, 0, 8]], [0.45, [0, 0, 0]]], "cam": MED_PHONE(0.08)},
]
assert {c["clip"] for c in CLIPS} == {b["char"] for b in BEATS if b.get("char")}
json.dump({"recipes": "../phoneverse_fix15_studio/data/face_recipes.json", "clips": CLIPS}, open("data/chars_fix15.json", "w"), indent=1)
H = {"episode": "phoneverse_fix15",
     "note": "FIX #15 'Wallet hijack' (a texted code lets a scammer add your card to their phone's wallet). Times = measured voice slots from phoneverse_fix15_studio/data/timings.json; nothing re-timed. "
             "Props: wallet (your card, the glowing copy, the scammer's phone; tray hidden). Character beats (char) render with render/char_scene.py (user asked for characters acting).",
     "fps": 24, "length_s": T["summary"]["take_length_s"], "props": ["wallet"], "chars": "data/chars_fix15.json", "char_frames": "build/chars",
     "audio": ["../phoneverse_fix15_studio/audio/mix_with_pad.wav", "../phoneverse_fix15_studio/audio/mix_voice_fx.wav"],
     "captions": "../phoneverse_fix15_studio/data/captions.json",
     "hook": {"lines": [["YOUR ", "*CARD", " JUST JUMPED"], ["ONTO THEIR PHONE"]], "from": 1.45, "until": 3.05},
     "shake": [1.45, 39.75], "beats": BEATS}
json.dump(H, open("data/beats_fix15.json", "w"), indent=1, ensure_ascii=False)
print(len(BEATS), "beats,", sum(1 for b in BEATS if b.get("char")), "character beats (%.1f s); longest %.2f s" % (sum(b["t1"] - b["t0"] for b in BEATS if b.get("char")), max(b["t1"] - b["t0"] for b in BEATS)))
