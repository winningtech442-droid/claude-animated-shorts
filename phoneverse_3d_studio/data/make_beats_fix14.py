#!/usr/bin/env python3
"""Builds data/beats_fix14.json from the measured FIX #14 take (never re-timed). Checks: beats are contiguous, none over 2.5 s,
and every beat starts on a different camera preset from the one the previous beat ended on (a real cut, FIX #13 weak spot 2).
  python3 data/make_beats_fix14.py      (run from phoneverse_3d_studio/)"""
import json
T = json.load(open("../phoneverse_fix14_studio/data/timings.json"))
CR = "U.duo_home(crack=1)"
def ev(type_, f, to, t0, t1): return {"type": type_, "from": f, "to": to, "t0": t0, "t1": t1}
folds, t = [], 20.2                                  # "fold after fold": close to 35% and back, every 0.6 s
while t + 0.6 <= 23.0: folds += [ev("open", 1, 0.35, t, t + 0.3), ev("open", 0.35, 1, t + 0.3, t + 0.6)]; t += 0.6
BEATS = [
 # L1 hook: the drop + two bounces, then "not a scratch" (scorecards)
 dict(t0=0.0, t1=1.45, line=1, cam=["drop", "drop"], events=[ev("open", 0, 0, 0, 0.01), ev("drop", 0, 1, 0.0, 1.45)]),
 dict(t0=1.45, t1=3.136, line=1, cam=["drop_low", "duo_side"], labels=[{"anchor": "phone", "text": "NOT A SCRATCH", "dx": 60, "dy": -330, "from": 2.0}]),
 # L2 open it
 dict(t0=3.136, t1=4.604, line=2, cam=["duo_hero", "duo_tilt"], events=[ev("open", 0, 1, 3.2, 4.35)]),
 # L3 "Wait!" the crack runs
 dict(t0=4.604, t1=6.372, line=3, cam=["duo_seam", "duo_crack"], inner="U.duo_home(crack=ease(clamp((p - 0.05) * 2.2)))"),
 # L4 "What was that?!"
 dict(t0=6.372, t1=7.747, line=4, cam=["duo_tilt", "duo_top"], inner=CR),
 # L5 owners report a click, then a black line down the fold
 dict(t0=7.747, t1=9.4, line=5, cam=["duo_crack", "duo_seam"], inner=CR, labels=[{"anchor": "seam", "text": "BLACK LINE", "dx": 120, "dy": -380, "from": 8.4}]),
 dict(t0=9.4, t1=11.071, line=5, cam=["duo_side", "duo_hero"], inner=CR, events=[ev("open", 1, 0.45, 9.5, 10.15), ev("open", 0.45, 1, 10.3, 10.95)],
      labels=[{"anchor": "hinge", "text": "THE FOLD", "dx": -330, "dy": -300, "from": 9.6}]),
 # L6 within hours
 dict(t0=11.071, t1=13.033, line=6, cam=["duo_top", "duo_tilt"], inner=CR, hud={"label": "AFTER BUYING", "count": [0, 6, "", " HOURS"], "color": "RED", "from": 11.2, "until": 12.6}),
 # L7 look inside the hinge: the screen lifts
 dict(t0=13.033, t1=14.4, line=7, cam=["duo_hero", "hinge"], inner=CR, events=[ev("lid", 0, 1, 13.4, 14.6)]),
 dict(t0=14.4, t1=15.611, line=7, cam=["hinge_low", "duo_side"], inner=CR, labels=[{"anchor": "hinge", "text": "HINGE", "dx": -300, "dy": -330, "from": 14.5}]),
 # L8 a tiny hook catches
 dict(t0=15.611, t1=17.5, line=8, cam=["hinge", "hook_macro"], inner=CR, events=[ev("hook", 0, 1, 16.4, 16.9)],
      labels=[{"anchor": "hook", "text": "HOOK", "dx": 150, "dy": -380, "from": 16.7}]),
 dict(t0=17.5, t1=19.489, line=8, cam=["hinge_low", "hinge"], inner=CR, labels=[{"anchor": "hook", "text": "CATCHES", "dx": -360, "dy": -360, "from": 17.6}]),
 # L9 fold after fold, pushes from below (screen back down, folds over and over, orange push glow under the fold)
 dict(t0=19.489, t1=21.2, line=9, cam=["duo_side", "duo_hero"], inner="U.duo_home(press=0.5 + 0.5 * p)", events=[ev("lid", 1, 0, 19.5, 20.1), ev("hook", 1, 0.6, 19.5, 20.1)] + folds,
      hud={"label": "FOLDS", "count": [0, 50, ""], "color": "ORANGE", "from": 20.2, "until": 22.9}),
 dict(t0=21.2, t1=23.048, line=9, cam=["duo_top", "duo_tilt"], inner="U.duo_home(press=1)", hud={"label": "FOLDS", "count": [0, 50, ""], "color": "ORANGE", "from": 20.2, "until": 22.9}),
 # L10 until... snap
 dict(t0=23.048, t1=24.2, line=10, cam=["duo_hero", "duo_seam"], inner="U.duo_home(press=1)"),
 dict(t0=24.2, t1=25.587, line=10, cam=["duo_crack", "duo_top"], inner="U.duo_home(crack=ease(clamp(p * 3)))"),
 # L11 Apple: a small number (the fleet, one red)
 dict(t0=25.587, t1=28.036, line=11, cam=["fleet", "fleet_red"], labels=[{"anchor": "fleetred", "text": "FAULTY", "dx": -360, "dy": -300, "from": 26.6}],
      hud={"label": "APPLE SAYS", "value": "A SMALL NUMBER", "color": "ORANGE", "from": 25.9}),
 # L12 but if Apple thinks you dropped it (REPLAY of the drop) ... £999
 dict(t0=28.036, t1=29.75, line=12, cam=["drop", "drop"], events=[ev("open", 1, 0, 28.04, 28.06), ev("drop", 0, 1, 28.15, 29.6)]),
 dict(t0=29.75, t1=31.4, line=12, cam=["duo_hero", "duo_top"], inner=CR, events=[ev("open", 0, 1, 29.8, 30.5)]),
 dict(t0=31.4, t1=33.092, line=12, cam=["duo_tilt", "duo_top"], inner="U.duo_card('INNER SCREEN', '£999', 'if it is ruled your fault', U.RED, crack=1)",
      hud={"label": "REPAIR BILL", "count": [0, 999, "£"], "color": "RED", "from": 31.5, "until": 32.7}),
 # L13 half of two thousand solid British pounds (coin rain)
 dict(t0=33.092, t1=35.0, line=13, cam=["duo_hero", "duo_top"], inner="U.duo_card('ONE SCREEN =', 'HALF', 'of a £1,999 phone', U.RED, crack=1)",
      hud={"label": "REPAIR BILL", "value": "£999", "color": "RED"}),
 dict(t0=35.0, t1=37.113, line=13, cam=["duo_wide", "duo_side"], inner=CR, events=[ev("coins", 0, 1, 34.9, 36.6)], hud={"label": "REPAIR BILL", "value": "£999", "color": "RED"}),
 # L14 frame damage £1,499 (the phone flinches shut)
 dict(t0=37.113, t1=38.9, line=14, cam=["duo_hero", "hinge_low"], inner=CR, events=[ev("open", 1, 0.15, 37.25, 37.45), ev("open", 0.15, 1, 38.35, 38.85)],
      labels=[{"anchor": "hinge", "text": "FRAME", "dx": -320, "dy": -320, "from": 37.5}], hud={"label": "REPAIR BILL", "count": [999, 1499, "£"], "color": "RED", "from": 38.0, "until": 38.8}),
 dict(t0=38.9, t1=40.697, line=14, cam=["duo_top", "duo_tilt"], inner="U.duo_card('FRAME DAMAGE', '£1,499', 'out of warranty', U.RED, crack=1)",
      hud={"label": "REPAIR BILL", "value": "£1,499", "color": "RED"}),
 # L15 with AppleCare+ £79
 dict(t0=40.697, t1=42.6, line=15, cam=["duo_side", "duo_hero"], inner=CR, hud={"label": "APPLECARE+", "value": "£16.99 / MONTH", "color": "GREEN", "from": 40.9}),
 dict(t0=42.6, t1=44.723, line=15, cam=["duo_tilt", "duo_top"], inner="U.duo_card('WITH APPLECARE+', '£79', 'inner screen repair', U.GREEN, crack=1)",
      hud={"label": "REPAIR BILL", "count": [999, 79, "£"], "color": "GREEN", "from": 43.0, "until": 43.9}),
 # L16 that's the difference (the plaster)
 dict(t0=44.723, t1=46.067, line=16, cam=["duo_seam", "duo_crack"], inner="U.duo_home(crack=1, plaster=ease(clamp(p * 2.5)))", hud={"label": "£999", "value": "vs £79", "color": "GREEN"}),
 # L17 cracked already? photograph it (viewfinder + flash)
 dict(t0=46.067, t1=47.6, line=17, cam=["duo_hero", "duo_side"], inner=CR, hud={"label": "CRACKED?", "value": "PHOTOGRAPH IT", "color": "ORANGE", "from": 46.6}),
 dict(t0=47.6, t1=49.178, line=17, cam=["duo_top", "duo_seam"], inner=CR, events=[ev("flash", 0, 1, 48.15, 48.2), ev("flash", 1, 0, 48.2, 48.5)],
      hud={"label": "BEFORE YOU", "value": "HAND IT IN", "color": "ORANGE"}),
 # L18 30 days: reject for a refund
 dict(t0=49.178, t1=51.0, line=18, cam=["duo_tilt", "duo_top"], inner="U.duo_card('BOUGHT IT IN', '30', 'days or less?', U.ORANGE, crack=1)",
      hud={"label": "UK LAW", "value": "CONSUMER RIGHTS ACT", "color": "ORANGE", "from": 49.4}),
 dict(t0=51.0, t1=53.014, line=18, cam=["duo_hero", "duo_side"], inner="U.duo_card('YOU CAN REJECT IT', 'REFUND', 'from the seller', U.GREEN, crack=1)"),
 # L19 six months: presumed from the start
 dict(t0=53.014, t1=54.9, line=19, cam=["duo_top", "duo_tilt"], inner="U.duo_card('FIRST', '6', 'months: fault presumed', U.ORANGE, crack=1)"),
 dict(t0=54.9, t1=56.679, line=19, cam=["duo_side", "duo_hero"], inner="U.duo_card('FIRST', '6', 'months: fault presumed', U.ORANGE, crack=1)",
      labels=[{"anchor": "phone", "text": "FROM DAY ONE", "dx": 40, "dy": -420, "from": 55.2}]),
 # L20 would you fold it every day?
 dict(t0=56.679, t1=58.4, line=20, cam=["duo_wide", "duo_tilt"], inner="U.duo_home(crack=1, plaster=1)", events=[ev("open", 1, 0.4, 56.9, 57.6), ev("open", 0.4, 1, 57.7, 58.35)]),
 dict(t0=58.4, t1=60.007, line=20, cam=["duo_hero", "duo_top"], inner="U.duo_ask('Would you fold it every day?', p * 1.5)"),
 # L21 send this
 dict(t0=60.007, t1=61.3, line=21, cam=["duo_tilt", "duo_seam"], inner="U.duo_share(p * 1.4)"),
 dict(t0=61.3, t1=62.42, line=21, cam=["duo_hero", "duo_wide"], inner="U.duo_share(1)", events=[ev("open", 1, 0, 61.45, 62.25)]),
]
for b in BEATS: b.setdefault("inset", False)
for a, b in zip(BEATS, BEATS[1:]): assert abs(a["t1"] - b["t0"]) < 1e-6, (a["t0"], b["t0"])
for b in BEATS: assert b["t1"] - b["t0"] <= 2.5, b["t0"]
for a, b in zip(BEATS, BEATS[1:]): assert a["cam"][1] != b["cam"][0], ("no real cut at", b["t0"])
assert abs(BEATS[-1]["t1"] - T["summary"]["take_length_s"]) < 0.01
H = {"episode": "phoneverse_fix14",
     "note": "FIX #14 'Crackgate' (iPhone Duo inner screen cracking along the fold). Times = measured voice slots from phoneverse_fix14_studio/data/timings.json; nothing re-timed. "
             "Props: duo (book-style foldable replaces the hero phone; mast/laptop/tray hidden), fleet (8 closed Duos, one red). No face beats (user: no characters this episode).",
     "fps": 24, "length_s": T["summary"]["take_length_s"], "props": ["duo", "fleet"],
     "audio": ["../phoneverse_fix14_studio/audio/mix_with_pad.wav", "../phoneverse_fix14_studio/audio/mix_voice_fx.wav"],
     "captions": "../phoneverse_fix14_studio/data/captions.json", "faces": "../phoneverse_fix14_studio/frames",
     "hook": {"lines": [["YOUR ", "*£1,999", " IPHONE"], ["JUST BOUNCED"]], "from": 0.55, "until": 3.0},
     "shake": [0.55, 0.99, 24.2, 28.7, 29.15], "scorecards": {"t0": 1.9, "t1": 3.1, "cards": ["10", "10", "9.9"]},
     "replay": [[28.036, 29.75]], "viewfinder": {"t0": 47.6, "t1": 48.9, "flash": 48.18}, "beats": BEATS}
json.dump(H, open("data/beats_fix14.json", "w"), indent=1, ensure_ascii=False)
print(len(BEATS), "beats; longest %.2f s" % max(b["t1"] - b["t0"] for b in BEATS))
