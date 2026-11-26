#!/usr/bin/env python3
"""Builds data/beats_fix16.json + data/chars_fix16.json from the measured FIX #16 take (never re-timed).
FIX #16 'Gold in your iPhone' (format test: treasure/curiosity). One world: the desk dressed as a workbench in a sunny recycling yard
(props "gold": the old generic phone, the tub, crucible + mould + bar, the drawer, the phone mountain, the phone-vs-rock piles).
Character beats: the lead "You" holds the NEW phone (brandless, reads as an iPhone 18 Pro Max, Burgundy) and tosses the OLD one;
4 clips (rule book v8 says 2-3; one over on purpose). Character clips need a "yard" set in render/char_scene.py (not built yet).
Checks: beats contiguous, none over 2.5 s, a real cut between consecutive desk beats, last beat ends on the take.
  python3 data/make_beats_fix16.py      (run from phoneverse_3d_studio/)"""
import json
T = json.load(open("../phoneverse_fix16_studio/data/timings.json"))
def ev(type_, f, to, t0, t1): return {"type": type_, "from": f, "to": to, "t0": t0, "t1": t1}
GRAMS = {"label": "GOLD FOUND", "steps": ["0.000 g", "0.008 g", "0.017 g", "0.026 g", "0.034 g"], "color": "YELLOW", "from": 19.4, "until": 23.6}
STEPS3 = {"label": "ONLY", "value": "3 SIMPLE STEPS", "color": "YELLOW", "from": 10.0}
PHONES = {"label": "PHONES NEEDED", "count": [0, 30000, ""], "color": "ORANGE", "from": 54.9, "until": 57.2}
BEATS = [
 # L1 every time you upgrade your iPhone, you throw away real gold (frame 1: the old phone is already flying in, tumbling, then bounces)
 dict(t0=0.0, t1=1.6, line=1, cam=["g_drop", "g_hero"], screen="U.lock_plain()", events=[ev("toss", 0, 1, 0.0, 1.5)]),
 dict(t0=1.6, t1=2.9, line=1, char="c01_toss"),
 dict(t0=2.9, t1=4.032, line=1, cam=["g_hero", "g_wide"], screen="U.lock_plain()"),
 # L2 real gold. inside your old phone (the lid lifts, the gold glows)
 dict(t0=4.032, t1=5.5, line=2, cam=["g_drop", "g_open"], parts=False, events=[ev("lid", 0, 1, 4.1, 5.1), ev("goldglow", 0, 1, 4.6, 5.4)]),
 dict(t0=5.5, t1=6.699, line=2, cam=["g_pins", "g_hero"], parts=False, labels=[{"anchor": "pins", "text": "REAL GOLD", "dx": 140, "dy": -300, "from": 5.7}]),
 # L3 recycling plants do this. don't try it at home (warning card over the yard)
 dict(t0=6.699, t1=8.3, line=3, cam=["g_wide", "g_tub"], parts=False),
 dict(t0=8.3, t1=9.877, line=3, cam=["g_pour", "g_cru"], parts=False),
 # L4 it only takes three simple steps (planted slip: there are more)
 dict(t0=9.877, t1=11.1, line=4, cam=["g_hero", "g_open"], parts=False, hud=STEPS3),
 dict(t0=11.1, t1=12.203, line=4, cam=["g_drop", "g_hero"], parts=False, hud=STEPS3),
 # L5 first, the battery comes out. very, very important
 dict(t0=12.203, t1=14.2, line=5, cam=["g_open", "g_batt"], parts=False, events=[ev("battout", 0, 1, 12.4, 13.9)],
      labels=[{"anchor": "battery", "text": "BATTERY", "dx": 120, "dy": -300, "from": 12.6}]),
 dict(t0=14.2, t1=15.723, line=5, cam=["g_batt_close", "g_batt"], parts=False, hud={"label": "STEP 1", "value": "BATTERY OUT", "color": "ORANGE", "from": 14.3}),
 # L6 if it gets crushed or punctured, it can catch fire (cutaway: the loose battery swells and flames)
 dict(t0=15.723, t1=17.2, line=6, cam=["g_hero", "g_batt_close"], parts=False, events=[ev("battfire", 0, 1, 15.9, 16.8)],
      labels=[{"anchor": "battery", "text": "FIRE RISK", "dx": -360, "dy": -320, "from": 16.3}]),
 dict(t0=17.2, t1=19.024, line=6, char="c02_recoil", events=[ev("battfire", 1, 0, 19.0, 19.02)]),
 # L7 these shiny pins? gold
 dict(t0=19.024, t1=21.093, line=7, cam=["g_open", "g_pins"], parts=False, hud=GRAMS, labels=[{"anchor": "pins", "text": "GOLD-PLATED PINS", "dx": -330, "dy": -330, "from": 19.7}]),
 # L8 some chips have gold wires thinner than a hair
 dict(t0=21.093, t1=22.6, line=8, cam=["g_chip", "g_chip_close"], parts=False, hud=GRAMS, events=[ev("hair", 0, 1, 21.2, 21.25)],
      labels=[{"anchor": "chip", "text": "GOLD WIRES", "dx": -340, "dy": -330, "from": 21.5}]),
 dict(t0=22.6, t1=23.995, line=8, cam=["g_hero", "g_chip"], parts=False, hud=GRAMS, labels=[{"anchor": "hair", "text": "A HAIR", "dx": 150, "dy": 260, "from": 22.9}]),
 # L9 the board goes in a liquid. slowly, slowly, it turns blue  (the phone is cleared away; a board drops into the tub)
 dict(t0=23.995, t1=25.6, line=9, cam=["g_tub_top", "g_tub"], events=[ev("gone", 0, 1, 24.0, 24.05), ev("dunk", 0, 1, 24.1, 25.3)]),
 dict(t0=25.6, t1=28.091, line=9, cam=["g_tub_low", "g_tub_macro"], events=[ev("liq", 0, 1, 25.7, 27.9)]),
 # L10 it falls apart into ugly mud
 dict(t0=28.091, t1=30.373, line=10, cam=["g_tub", "g_tub_side"],
      events=[ev("bubble", 0, 1, 28.1, 28.5), ev("dissolve", 0, 1, 28.2, 30.0), ev("liq", 1, 2, 28.2, 29.8), ev("mud", 0, 1, 28.4, 30.1)]),
 # L11 once the bubbling stops, the mud starts to sparkle
 dict(t0=30.373, t1=32.0, line=11, cam=["g_tub", "g_tub_low"], events=[ev("bubble", 1, 0, 30.5, 31.3)]),
 dict(t0=32.0, t1=33.846, line=11, cam=["g_tub_top", "g_tub_macro"], events=[ev("sparkle", 0, 1, 32.0, 32.8)],
      labels=[{"anchor": "mud", "text": "THAT'S GOLD", "dx": 120, "dy": -330, "from": 32.7}]),
 # L12 wash it, rinse it, wash it again. a stronger acid turns it yellow
 dict(t0=33.846, t1=36.0, line=12, cam=["g_tub_side", "g_tub"], events=[ev("rinse", 0, 1, 33.9, 35.9)]),
 dict(t0=36.0, t1=38.39, line=12, cam=["g_tub_low", "g_tub_macro"],
      events=[ev("bubble", 0, 1, 36.1, 36.5), ev("liq", 2, 3, 36.1, 37.9), ev("mud", 1, 0, 36.1, 37.6), ev("sparkle", 1, 0, 36.1, 37.2)]),
 # L13 once the bubbling stops again, brown dust falls down
 dict(t0=38.39, t1=40.1, line=13, cam=["g_tub_top", "g_tub"], events=[ev("bubble", 1, 0, 38.4, 39.0), ev("powder", 0, 1, 38.6, 39.9)]),
 dict(t0=40.1, t1=41.974, line=13, cam=["g_tub_macro", "g_tub_low"], events=[ev("dust", 0, 1, 40.1, 41.9)]),
 # L14 this brown dust? pure gold. gold sand, gold dust, whatever  (planted slip: "gold sand")
 dict(t0=41.974, t1=44.0, line=14, cam=["g_tub", "g_tub_macro"], labels=[{"anchor": "mud", "text": "PURE GOLD", "dx": 120, "dy": -330, "from": 42.6}]),
 dict(t0=44.0, t1=45.4, line=14, cam=["g_tub_side", "g_tub_top"], labels=[{"anchor": "mud", "text": "GOLD SAND? GOLD DUST?", "dx": -330, "dy": -360, "from": 44.4}]),
 dict(t0=45.4, t1=46.698, line=14, cam=["g_wide", "g_cru"], labels=[{"anchor": "crucible", "text": "INTO THE POT", "dx": -330, "dy": -330, "from": 45.7}]),
 # L15 heat it, pour it, and there it is. a real gold bar  (fantasy peak)
 dict(t0=46.698, t1=48.1, line=15, cam=["g_cru_top", "g_cru_in"], events=[ev("torch", 0, 1, 46.75, 47.05), ev("heat", 0, 1, 46.8, 47.9)]),
 dict(t0=48.1, t1=49.4, line=15, cam=["g_pour", "g_bar"], events=[ev("pour", 0, 1, 48.15, 49.1), ev("fill", 0, 1, 48.4, 49.3), ev("torch", 1, 0, 48.2, 48.5)]),
 dict(t0=49.4, t1=50.4, line=15, cam=["g_bar_top", "g_bar"], events=[ev("pour", 1, 0, 49.45, 49.9), ev("cool", 0, 1, 49.45, 49.9), ev("lift", 0, 1, 49.55, 50.35)],
      hud={"label": "REAL GOLD BAR", "value": "1 kg", "color": "YELLOW", "from": 49.8}),
 dict(t0=50.4, t1=51.3, line=15, char="c03_delight"),
 # L16 honest part? one phone gives about three pounds of gold
 dict(t0=51.3, t1=52.6, line=16, char="c04_shrug"),
 dict(t0=52.6, t1=54.496, line=16, cam=["g_bar_top", "g_pour"], hud={"label": "GOLD IN 1 PHONE", "value": "≈ £3", "color": "YELLOW", "from": 52.6},
      labels=[{"anchor": "bar", "text": "1 kg", "dx": 140, "dy": -300, "from": 52.9}]),
 # L17 for this bar? about thirty thousand more phones (big pull-back to the mountain)
 dict(t0=54.496, t1=56.0, line=17, cam=["g_bar_top", "g_bar_push"], hud=PHONES),
 dict(t0=56.0, t1=57.483, line=17, cam=["g_wide", "g_pull"], hud=PHONES, labels=[{"anchor": "heap", "text": "≈ 30,000 PHONES", "dx": 100, "dy": -300, "from": 56.5}]),
 # L18 tonne for tonne, old phones still beat a gold mine
 dict(t0=57.483, t1=59.2, line=18, cam=["g_hero", "g_cmp"], events=[ev("piles", 0, 1, 57.5, 58.3)],
      labels=[{"anchor": "phonepile", "text": "OLD PHONES", "dx": -330, "dy": -330, "from": 58.2}, {"anchor": "rockpile", "text": "MINE ROCK", "dx": 80, "dy": -330, "from": 58.5}]),
 dict(t0=59.2, t1=60.869, line=18, cam=["g_wide", "g_cmp"], hud={"label": "TONNE FOR TONNE", "value": "PHONES WIN", "color": "GREEN", "from": 59.3},
      labels=[{"anchor": "phonepile", "text": "OLD PHONES", "dx": -330, "dy": -330}, {"anchor": "rockpile", "text": "MINE ROCK", "dx": 80, "dy": -330}]),
 # L19 erase it before you recycle. your photos and bank apps are still inside  (accurate; never slipped)
 dict(t0=60.869, t1=62.6, line=19, cam=["g_drawer", "g_drawer_close"], dscreen="U.photo_gallery(p * 1.2)", events=[ev("piles", 1, 0, 60.9, 61.1), ev("drawer", 0, 1, 60.9, 61.7)]),
 dict(t0=62.6, t1=64.1, line=19, cam=["g_drawer", "g_drawer_close"], dscreen="U.photo_gallery(1)", labels=[{"anchor": "dphone", "text": "PHOTOS · BANK APPS", "dx": -360, "dy": -340, "from": 62.9}]),
 dict(t0=64.1, t1=65.627, line=19, cam=["g_wide", "g_drawer_close"], dscreen="U.erase_hello(p)", hud={"label": "BEFORE YOU RECYCLE", "value": "ERASE IT", "color": "GREEN", "from": 64.2}),
 # L20 how many old phones are in your drawer? tell me below  -> the old phone lifts back out to the left: loops into frame 1
 dict(t0=65.627, t1=67.4, line=20, cam=["g_drawer", "g_wide"], dscreen="U.erase_hello(1)", hud={"label": "YOUR DRAWER", "value": "HOW MANY?", "color": "ORANGE", "from": 65.8}),
 dict(t0=67.4, t1=69.019, line=20, cam=["g_hero", "g_drop"], screen="U.lock_plain()", dscreen="U.erase_hello(1)",
      events=[ev("drawer", 1, 0, 67.45, 68.2), ev("gone", 1, 0, 67.4, 67.42), ev("lid", 1, 0, 67.4, 67.42), ev("goldglow", 1, 0, 67.4, 67.42),
              ev("battout", 1, 0, 67.4, 67.42), ev("hair", 1, 0, 67.4, 67.42), ev("toss", 1, 0.0, 67.6, 69.0)]),
]
# STAND-INS: the character clips need the Rocketbox assets + a "yard" set in char_scene.py, neither available yet. Until they exist, each
# character beat renders as a desk shot of the same moment (flagged "standin_for"); set STANDIN = False and re-render those frames to swap them in.
STANDIN = True
STAND = {"c01_toss": ["g_wide", "g_drop"], "c02_recoil": ["g_batt", "g_hero"], "c03_delight": ["g_pour", "g_bar_top"], "c04_shrug": ["g_bar", "g_pour"]}
if STANDIN:
    for b in BEATS:
        if b.get("char"): c = b.pop("char"); b["standin_for"] = c; b["cam"] = STAND[c]; b.setdefault("screen", "U.lock_plain()")
for b in BEATS: b.setdefault("inset", False); b["parts"] = False   # no auto part tags (CPU/BATTERY) in this episode       # no screen insets: the old phone's lock screen is not the story here
for a, b in zip(BEATS, BEATS[1:]): assert abs(a["t1"] - b["t0"]) < 1e-6, (a["t0"], b["t0"])
for b in BEATS: assert b["t1"] - b["t0"] <= 2.5, b["t0"]
for a, b in zip(BEATS, BEATS[1:]):
    if not a.get("char") and not b.get("char"): assert a["cam"][1] != b["cam"][0], ("no real cut at", b["t0"])
assert abs(BEATS[-1]["t1"] - T["summary"]["take_length_s"]) < 0.01, (BEATS[-1]["t1"], T["summary"]["take_length_s"])

# ---- character clips: intent only until char_scene.py has a "yard" set (sunny workbench, phone mountain behind) and a new-phone hand prop
NEWPHONE = "brandless iPhone 18 Pro Max lookalike, Burgundy: 163.4 x 78 x 8.75 mm, full-width camera bar, 3 lenses in a triangle on the left; no logo"
CLIPS = [
 {"clip": "c01_toss", "set": "yard", "pose": "hold", "prop": NEWPHONE, "notes": "holds the NEW phone in her left hand; right hand follows through from tossing the old one (off-frame left)",
  "expr": [[0, "smug", 0.7]], "face": "smug"},
 {"clip": "c02_recoil", "set": "yard", "pose": "recoil", "notes": "flinches back from the battery flash (orange light on her face)", "expr": [[0, "shock", 1.0]], "face": "shock"},
 {"clip": "c03_delight", "set": "yard", "pose": "cheer", "notes": "the gold bar rises: delight", "expr": [[0, "delight", 1.0]], "face": "delight"},
 {"clip": "c04_shrug", "set": "yard", "pose": "shrug", "notes": "'Honest part?' three pounds: a shrug, half a smile", "expr": [[0, "smug", 0.6]], "face": "smug"},
]
assert {c["clip"] for c in CLIPS} == {b.get("char") or b.get("standin_for") for b in BEATS if b.get("char") or b.get("standin_for")}
json.dump({"recipes": "../phoneverse_fix15_studio/data/face_recipes.json", "clips": CLIPS, "status": "intent only: needs a 'yard' set in char_scene.py"},
          open("data/chars_fix16.json", "w"), indent=1)
H = {"episode": "phoneverse_fix16",
     "note": "FIX #16 'Gold in your iPhone' (format test). Times = measured voice slots from phoneverse_fix16_studio/data/timings.json; nothing re-timed. "
             "Props: gold (workbench in a sunny recycling yard, old generic phone, tub, crucible, mould and bar, drawer, phone mountain, comparison piles).",
     "fps": 24, "length_s": T["summary"]["take_length_s"], "props": ["gold"], "chars": "data/chars_fix16.json", "char_frames": "build/chars",
     "audio": ["../phoneverse_fix16_studio/audio/mix_with_pad.wav", "../phoneverse_fix16_studio/audio/mix_voice_fx.wav"],
     "captions": "../phoneverse_fix16_studio/data/captions.json",
     "hook": {"lines": [["YOU'RE BINNING"], ["REAL ", "*GOLD"]], "from": 1.5, "until": 3.95},
     "cards": [{"t0": 6.75, "t1": 9.8, "title": "DON'T TRY THIS AT HOME", "sub": "Toxic fumes & acid · recycling plants only", "color": "RED"}],
     "shake": [0.6, 16.1, 49.7], "beats": BEATS}
json.dump(H, open("data/beats_fix16.json", "w"), indent=1, ensure_ascii=False)
print(len(BEATS), "beats,", sum(1 for b in BEATS if b.get("char") or b.get("standin_for")), "character beats (%.1f s); longest %.2f s" % (sum(b["t1"] - b["t0"] for b in BEATS if b.get("char") or b.get("standin_for")), max(b["t1"] - b["t0"] for b in BEATS)))
