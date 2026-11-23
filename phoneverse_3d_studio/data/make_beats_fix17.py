#!/usr/bin/env python3
"""Builds data/beats_fix17.json + data/chars_fix17.json from the measured FIX #17 take (locked 23 Nov 2026, never re-timed).
FIX #17 'Your phone is made of sand' (treasure/curiosity series, after #16). One world: #16's sunny-yard workbench, re-dressed (props "silicon"):
the quartz heap behind the bench, an arc furnace, the tub (cleaning), the crucible (melt + the crystal pulled out of it), the saw bed and wafers,
sand vs a quartz lump, the hero phone (sand in the hook, the glowing chip, the case and charger at the end).
Character beats: the lead "You", 3 clips (rule book v8: 2-3). Desk stand-ins until char_scene.py has the "yard" set (STANDIN below).
Checks: beats contiguous, none over 2.5 s, a real cut between consecutive desk beats, last beat ends on the take.
  python3 data/make_beats_fix17.py      (run from phoneverse_3d_studio/)"""
import json
T = json.load(open("../phoneverse_fix17_studio/data/timings.json"))
S = {l["id"]: l["start"] for l in T["lines"]}; END = T["summary"]["take_length_s"]
def ev(type_, f, to, t0, t1): return {"type": type_, "from": f, "to": to, "t0": t0, "t1": t1}
def lab(anchor, text, dx=140, dy=-300, frm=None):
    d = {"anchor": anchor, "text": text, "dx": dx, "dy": dy}
    if frm is not None: d["from"] = frm
    return d
STEPS3 = {"label": "ONLY", "value": "3 STEPS", "color": "YELLOW", "from": S[4] + 0.2}
PURITY = {"label": "CHIP SILICON", "steps": ["99.9999999 %", "99.99999999 %", "99.999999999 %"], "color": "GREEN", "from": 21.3, "until": 23.3}
PULL = {"label": "PULL TIME", "count": [0, 44, "", " HOURS"], "color": "ORANGE", "from": 28.3, "until": 35.9}
FOLLOW = {"label": "TAP", "value": "FOLLOW +", "color": "RED", "from": S[13] + 0.1}
BEATS = [
 # L1 your phone's brain is made of sand (frame 1: sand is already raining onto the phone)
 dict(t0=0.0, t1=1.1, line=1, cam=["g_drop", "g_hero"], screen="U.lock_plain()", events=[ev("sand", 0, 1, -0.3, 2.0)]),
 dict(t0=1.1, t1=S[2], line=1, char="c01_hold"),
 # L2 sand. inside your phone. thinking for you (the lid lifts, the main chip glows)
 dict(t0=S[2], t1=3.6, line=2, cam=["g_open", "g_chip"], events=[ev("lid", 0, 1, 2.2, 3.1), ev("brain", 0, 1, 2.7, 3.4)], labels=[lab("chip", "THE BRAIN", 120, -320, 3.0)]),
 dict(t0=3.6, t1=S[3], line=2, cam=["g_chip_close", "g_open"], labels=[lab("chip", "MADE FROM SAND", -360, -330, 3.8)]),
 # L3 giant factories do this. never at home (warning card)
 dict(t0=S[3], t1=6.6, line=3, cam=["g_wide", "s_furn"], events=[ev("lid", 1, 0, 5.15, 5.6), ev("brain", 1, 0, 5.15, 5.6), ev("furnace", 0, 0.5, 5.2, 6.4)]),
 dict(t0=6.6, t1=S[4], line=3, cam=["g_cru", "g_cru_top"], events=[ev("heat", 0, 0.7, 6.6, 7.6)]),
 # L4 only three steps. I said that last time (planted slip: there are more)
 dict(t0=S[4], t1=9.5, line=4, cam=["g_hero", "g_drop"], screen="U.lock_plain()", hud=STEPS3, events=[ev("heat", 0.7, 0, 8.1, 8.15)]),
 dict(t0=9.5, t1=S[5], line=4, cam=["g_wide", "s_furn"], hud=STEPS3),
 # L5 first, cook it with coal. out comes grey metal (quartz + coal drop in, the furnace roars, metal chunks come out)
 dict(t0=S[5], t1=12.6, line=5, cam=["s_furn_top", "s_furn"], events=[ev("charge", 0, 1, 11.05, 12.3), ev("furnace", 0.5, 1, 11.4, 12.2)],
      labels=[lab("coal", "QUARTZ + COAL", 120, -320, 11.4)]),
 dict(t0=12.6, t1=S[6], line=5, cam=["s_metal_wide", "s_metal"], events=[ev("metal", 0, 1, 12.75, 13.6)], labels=[lab("metal", "SILICON METAL", 120, -320, 13.2)]),
 # L6 still way, way too dirty for a chip
 dict(t0=S[6], t1=15.5, line=6, cam=["s_metal_macro", "s_metal"], labels=[lab("dirt", "DIRT", -320, -320, 14.4)]),
 dict(t0=15.5, t1=S[7], line=6, cam=["g_tub_top", "g_tub_side"], events=[ev("chunks", 0, 1, 15.55, 15.6), ev("liq", 0, 2, 15.6, 16.3), ev("metal", 1, 0, 15.5, 15.55)]),
 # L7 they clean it, clean it, clean it again (three rinses, murky to clear)
 dict(t0=S[7], t1=18.0, line=7, cam=["g_tub", "g_tub_low"], events=[ev("rinse", 0, 1, 16.8, 19.2), ev("liq", 2, 0, 16.9, 19.1), ev("shine", 0, 1, 17.0, 19.2)]),
 dict(t0=18.0, t1=S[8], line=7, cam=["g_tub_macro", "g_tub_top"]),
 # L8 a gold bar? four nines pure. this? nine nines, even eleven (the gold bar from #16, then the clean silicon)
 dict(t0=S[8], t1=21.2, line=8, cam=["g_bar_top", "g_bar_push"], events=[ev("fill", 0, 1, 19.3, 19.32), ev("cool", 0, 1, 19.3, 19.32)],
      hud={"label": "GOLD BAR", "value": "99.99 %", "color": "YELLOW", "from": 19.4}),
 dict(t0=21.2, t1=22.7, line=8, cam=["g_tub_low", "g_tub_macro"], hud=PURITY, events=[ev("fill", 1, 0, 21.2, 21.22), ev("cool", 1, 0, 21.2, 21.22)]),
 dict(t0=22.7, t1=S[9], line=8, cam=["g_tub_top", "g_cru"], hud=PURITY, events=[ev("chunks", 1, 0, 23.9, 23.95)]),
 # L9 now melt it. hotter than lava
 dict(t0=S[9], t1=25.3, line=9, cam=["g_cru_top", "g_cru_in"], events=[ev("heat", 0, 1, 24.15, 25.2)], hud={"label": "MELT", "count": [0, 1414, "", " °C"], "color": "ORANGE", "from": 24.2, "until": 25.4}),
 dict(t0=25.3, t1=S[10], line=9, cam=["s_seed", "g_cru"], hud={"label": "MELT", "value": "1,414 °C", "color": "ORANGE"}, labels=[lab("melt", "HOTTER THAN LAVA", 120, -320, 25.5)]),
 # L10 dip in a tiny seed. pull, slowly, slowly
 dict(t0=S[10], t1=28.0, line=10, cam=["s_seed_high", "s_seed"], events=[ev("dip", 0, 1, 26.5, 27.9)], labels=[lab("seed", "TINY SEED", 140, -300, 26.9)]),
 dict(t0=28.0, t1=S[11], line=10, cam=["g_cru_in", "s_ingot_low"], hud=PULL, events=[ev("grow", 0, 0.12, 28.2, 29.7), ev("hot", 0, 1, 28.2, 28.8)]),
 # L11 spin it one way, the pot the other. or the other way. whatever (planted slip: opposite directions either way)
 dict(t0=S[11], t1=31.5, line=11, cam=["s_ingot", "s_ingot_orbit"], hud=PULL, events=[ev("spin", 0, 1, 29.8, 30.4), ev("grow", 0.12, 0.3, 29.8, 33.6)],
      labels=[lab("crystal_top", "SPINS ONE WAY", 140, -300, 30.1), lab("melt", "POT: THE OTHER", -360, 200, 30.7)]),
 dict(t0=31.5, t1=S[12], line=11, cam=["g_cru_top", "s_seed"], hud=PULL),
 # L12 slower than a snail. about two days
 dict(t0=S[12], t1=35.0, line=12, cam=["s_snail", "s_snail2"], hud=PULL, events=[ev("snail", 0, 1, 33.65, 35.0), ev("grow", 0.3, 0.55, 33.6, 36.3)], labels=[lab("snail", "FASTER", 120, -300, 34.0)]),
 dict(t0=35.0, t1=S[13], line=12, cam=["s_ingot_low", "s_ingot"], hud=PULL, events=[ev("snail", 1, 1, 35.0, 35.01)]),
 # L13 now, press the Follow button to keep watching our videos! (mid-video CTA on the cliffhanger: the melt flares so the crystal stays hidden)
 dict(t0=S[13], t1=38.2, line=13, cam=["g_cru", "g_cru_top"], hud=FOLLOW, events=[ev("glare", 0, 1, 36.4, 36.9), ev("grow", 0.55, 1, 36.4, 39.6)]),
 dict(t0=38.2, t1=S[14], line=13, cam=["g_drop", "g_hero"], screen="U.lock_plain()", hud=FOLLOW, events=[ev("glare", 1, 0, 39.6, 39.9)]),
 # L14 out comes one giant glowing crystal, tall as you (fantasy peak, AWE)
 dict(t0=S[14], t1=41.0, line=14, char="c02_delight", events=[ev("out", 0, 1, 40.0, 41.8)]),
 dict(t0=41.0, t1=42.5, line=14, cam=["s_ingot_low", "s_ingot"], labels=[lab("ingot", "ONE GIANT CRYSTAL", 140, -300, 41.3)]),
 dict(t0=42.5, t1=S[15], line=14, cam=["s_ingot_orbit", "s_ingot"], events=[ev("hot", 1, 0, 42.6, 45.0), ev("cool2", 0, 1, 42.6, 45.0)]),
 # L15 heavy as a piano. perfect all through
 dict(t0=S[15], t1=45.5, line=15, cam=["s_ingot_side", "s_ingot_orbit"], hud={"label": "WEIGHT", "value": "≈ A PIANO", "color": "ORANGE", "from": 44.1}),
 dict(t0=45.5, t1=S[16], line=15, cam=["s_ingot_low", "s_ingot"], hud={"label": "ONE PERFECT CRYSTAL", "value": "ALL THE WAY THROUGH", "color": "GREEN", "from": 45.6}),
 # L16 a wire slices it like cheese, thin as a bank card
 dict(t0=S[16], t1=48.6, line=16, cam=["s_saw_side", "s_saw"], events=[ev("slab", 0, 1, 46.98, 47.0), ev("saw", 0, 1, 47.1, 48.5)], labels=[lab("slices", "WIRE SAW", 140, -300, 47.3)]),
 dict(t0=48.6, t1=S[17], line=16, cam=["s_card", "s_card_close"], events=[ev("fan", 0, 1, 48.6, 49.4)],
      labels=[lab("slices", "WAFER 0.775 mm", -380, -320, 49.0), lab("card", "BANK CARD 0.76 mm", 60, 260, 49.4)]),
 # L17 polish it to a mirror. hundreds of phone brains fit on one
 dict(t0=S[17], t1=52.3, line=17, cam=["s_wafer", "s_wafer_close"], events=[ev("wafer", 0, 1, 50.75, 51.6)], labels=[lab("wafer", "A PERFECT MIRROR", 140, -330, 51.3)]),
 dict(t0=52.3, t1=S[18], line=17, cam=["s_wafer_tilt", "s_wafer"], events=[ev("chips", 0, 1, 52.4, 53.6)], hud={"label": "CHIPS PER WAFER", "value": "HUNDREDS", "color": "GREEN", "from": 52.9}),
 # L18 honest part? not beach sand. pure quartz rock. most sand's too dirty (the honest twist)
 dict(t0=S[18], t1=55.8, line=18, char="c03_shrug"),
 dict(t0=55.8, t1=57.6, line=18, cam=["s_cmp", "s_cmp_close"], labels=[lab("sand", "BEACH SAND", -340, -320, 56.0), lab("quartz", "PURE QUARTZ", 100, -320, 56.6)]),
 dict(t0=57.6, t1=S[19], line=18, cam=["g_wide", "g_pull"], labels=[lab("heap", "QUARTZ ROCK", 100, -300, 57.9)]),
 # L19 rock or sand, mostly the same stuff. still thinking for you
 dict(t0=S[19], t1=61.4, line=19, cam=["s_wafer_close", "s_wafer"]),
 dict(t0=61.4, t1=S[20], line=19, cam=["g_chip_close", "g_open"], events=[ev("lid", 0, 1, 61.4, 61.45), ev("brain", 0, 1, 61.5, 62.2)], labels=[lab("chip", "STILL THINKING", 120, -320, 62.0)]),
 # L20 phone hot while charging? take the case off (Apple's own advice; never slipped)
 dict(t0=S[20], t1=65.2, line=20, cam=["s_case", "g_hero"], screen="U.lock_plain()",
      events=[ev("lid", 1, 0, 63.73, 63.75), ev("brain", 1, 0, 63.73, 63.75), ev("case", 0, 1, 63.73, 63.75), ev("charging", 0, 1, 63.73, 63.75), ev("hot2", 0, 1, 63.9, 64.6)],
      labels=[lab("phone", "HOT WHILE CHARGING", 120, -320, 64.3)]),
 dict(t0=65.2, t1=S[21], line=20, cam=["g_drop", "s_case"], screen="U.lock_plain()", events=[ev("caseoff", 0, 1, 65.3, 66.2), ev("hot2", 1, 0, 65.6, 66.6)],
      hud={"label": "HOT WHILE CHARGING?", "value": "CASE OFF", "color": "GREEN", "from": 65.4}),
 # L21 did you know your phone started as rock? yes or no below -> sand starts raining again: loops into frame 1
 dict(t0=S[21], t1=68.5, line=21, cam=["g_wide", "g_pull"], hud={"label": "YOUR PHONE STARTED AS", "value": "ROCK?", "color": "ORANGE", "from": 66.9},
      events=[ev("charging", 1, 0, 66.72, 66.74), ev("case", 1, 0, 66.72, 66.74), ev("caseoff", 1, 0, 66.72, 66.74)]),
 dict(t0=68.5, t1=END, line=21, cam=["g_hero", "g_drop"], screen="U.lock_plain()", hud={"label": "YES OR NO?", "value": "TELL ME BELOW", "color": "ORANGE", "from": 68.6},
      events=[ev("sand", 0, 0.75, 68.6, END)]),
]
STANDIN = True
STAND = {"c01_hold": ["g_open", "g_hero"], "c02_delight": ["s_ingot_orbit", "s_ingot"], "c03_shrug": ["g_wide", "s_cmp_close"]}
if STANDIN:
    for b in BEATS:
        if b.get("char"): c = b.pop("char"); b["standin_for"] = c; b["cam"] = STAND[c]; b.setdefault("screen", "U.lock_plain()")
for b in BEATS: b.setdefault("inset", False); b["parts"] = False
for a, b in zip(BEATS, BEATS[1:]): assert abs(a["t1"] - b["t0"]) < 1e-6, (a["t0"], b["t0"])
for b in BEATS: assert b["t1"] - b["t0"] <= 2.5, (b["t0"], b["t1"] - b["t0"])
for a, b in zip(BEATS, BEATS[1:]):
    if not a.get("char") and not b.get("char"): assert a["cam"][1] != b["cam"][0], ("no real cut at", b["t0"])
assert abs(BEATS[-1]["t1"] - END) < 0.01

NEWPHONE = "brandless iPhone 18 Pro Max lookalike, Burgundy (same hand prop as #16 c01); no logo"
CLIPS = [
 {"clip": "c01_hold", "set": "yard", "pose": "hold", "prop": NEWPHONE, "notes": "holds the phone up to camera; sand trickles out of the other fist", "expr": [[0, "smug", 0.7]], "face": "smug"},
 {"clip": "c02_delight", "set": "yard", "pose": "cheer", "notes": "looks up as the glowing crystal rises past head height (orange light on the face)", "expr": [[0, "delight", 1.0]], "face": "delight"},
 {"clip": "c03_shrug", "set": "yard", "pose": "shrug", "prop": "a white quartz lump", "notes": "'Honest part?' holds up a lump of quartz instead of sand", "expr": [[0, "smug", 0.6]], "face": "smug"},
]
assert {c["clip"] for c in CLIPS} == {b.get("char") or b.get("standin_for") for b in BEATS if b.get("char") or b.get("standin_for")}
json.dump({"recipes": "../phoneverse_fix15_studio/data/face_recipes.json", "clips": CLIPS, "status": "intent only: needs a 'yard' set in char_scene.py"},
          open("data/chars_fix17.json", "w"), indent=1)
H = {"episode": "phoneverse_fix17",
     "note": "FIX #17 'Your phone is made of sand'. Times = measured voice slots from phoneverse_fix17_studio/data/timings.json (locked); nothing re-timed. "
             "Props: silicon (the #16 yard workbench re-dressed: quartz heap, arc furnace, tub, crucible + crystal, saw bed + wafers, sand vs quartz, case + charger).",
     "fps": 24, "length_s": END, "props": ["silicon"], "chars": "data/chars_fix17.json", "char_frames": "build/chars",
     "audio": ["../phoneverse_fix17_studio/audio/mix_with_pad.wav", "../phoneverse_fix17_studio/audio/mix_voice_fx.wav"],
     "captions": "../phoneverse_fix17_studio/data/captions.json",
     "hook": {"lines": [["YOUR PHONE IS"], ["MADE OF ", "*SAND"]], "from": 0.0, "until": 3.0},
     "cards": [{"t0": S[3] + 0.05, "t1": S[4] - 0.1, "title": "DON'T TRY THIS AT HOME", "sub": "Over 1,400 °C · factories only", "color": "RED"}],
     "shake": [11.5, 40.1], "beats": BEATS}
json.dump(H, open("data/beats_fix17.json", "w"), indent=1, ensure_ascii=False)
print(len(BEATS), "beats,", sum(1 for b in BEATS if b.get("char") or b.get("standin_for")), "character beats; longest %.2f s" % max(b["t1"] - b["t0"] for b in BEATS))
