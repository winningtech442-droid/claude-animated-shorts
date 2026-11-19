#!/usr/bin/env python3
"""Builds data/shots.json + data/shots.csv from the measured voice take (data/timings.json).
Every sub-shot is 2.5 s or less, except 16a (the settings card, allowed 3-4 s). Re-run after any new voice take."""
import json, csv
T = json.load(open("data/timings.json")); L = {x["id"]: x for x in T["lines"]}
END = T["summary"]["take_length_s"]
# slot of shot k = from the previous slot end to this line's slot end (the pause-before silence belongs to the shot it leads into)
bounds = {}; prev = 0.0
for i in range(1, 22):
    bounds[i] = (prev, L[i]["slot_end"]); prev = L[i]["slot_end"]
bounds[21] = (bounds[21][0], END)

# (offset_s inside slot, id, set, what the viewer SEES (verb), face clip, camera, overlay, [(sfx offset, sfx)], music)
S = {
1: [(0.0, "1a", "B/A", "Her hands grip the phone; the ParcelGo banner SLAMS in and fills the screen, a £2 chip pulses (frame 1 is mid-slam)", "-", "Close-up, fast push-in", "Corner tag PHONEVERSE · FIX #12", [(0.0, "buzz"), (0.0, "bus_hum")], "on"),
    (1.6, "1b", "B", "Banner text 'Missed parcel. Pay £2 to redeliver.' fills the frame; the £2 chip swells and glows red", "-", "Slow push on the chip", "£2 chip glow", [(1.7, "tick_rise")], "on")],
2: [(0.0, "2a", "A", "Whip pan from the phone to her face as the buzz hits; amber lights streak behind the wet window", "bus_hope", "Whip pan, then hold under 1 s", "Starred caption 'buzzes'", [(0.1, "buzz"), (0.1, "whoosh")], "on"),
    (1.2, "2b", "A", "Over-the-shoulder: her thumb lifts the phone; the bus rocks, rain runs down the glass", "-", "Over-the-shoulder drift", "-", [], "on")],
3: [(0.0, "3a", "D", "A UK map fills the frame; red dots spread over it city by city", "-", "Fast push", "UK map, red dots", [(0.0, "tick_rise")], "dip"),
    (1.8, "3b", "D", "A ring climbs from 0 to one third; '34%' lands in the middle; the sound cuts just before the number", "-", "Ring fills fast, number holds under 1 s", "'1 in 3' ring, 34%", [(3.0, "tick")], "dip"),
    (3.3, "3c", "A", "Cut to her face: the grimace as the caption 'targeted' lands", "bus_dread", "Push-in", "-", [], "dip")],
4: [(0.0, "4a", "A", "Her thumb hovers over the banner; she smirks, sure she would spot a fake", "bus_hope", "Over-the-shoulder drift", "-", [], "on"),
    (1.4, "4b", "B", "The '£2' on the banner shrinks to a tiny coin", "-", "Slow push", "Coin icon", [(1.5, "pop")], "on")],
5: [(0.0, "5a", "B", "MUSIC DROPS OUT. Slow push into the £2 chip", "-", "Slow push", "-", [(0.0, "silence")], "out"),
    (1.6, "5b", "B", "The £2 chip cracks open; a card icon sits behind it", "-", "Slow push, tiny shake on the crack", "Card icon", [(1.7, "crack")], "out"),
    (3.2, "5c", "B", "A red dashed line starts from the card icon and runs off the screen edge", "-", "Slow pull", "Red dashed line, 'your card' tag", [], "out")],
6: [(0.0, "6a", "B", "An orange tap ring hits the 'Pay £2' link", "-", "Close-up on the thumb, fast", "Orange tap ring", [(0.2, "tap")], "on"),
    (1.2, "6b", "B", "The ParcelGo page loads full-frame (purple and yellow, no real courier look)", "-", "Whip into the screen", "-", [(1.2, "whoosh")], "on")],
7: [(0.0, "7a", "B", "Fields fill one by one: Name, then Address", "-", "Fly-through the fields", "Orange boxes", [(0.1, "keys")], "on"),
    (1.2, "7b", "B", "Card number fills; the Done button lights", "-", "Fly-through, then push", "Orange box on Card number", [(1.2, "keys"), (2.1, "confirm")], "on")],
8: [(0.0, "8a", "B", "MUSIC OUT. '£2' ticks over to 'Paid'", "-", "Hard push", "'Paid' stamp", [(0.0, "silence"), (0.3, "thud")], "out"),
    (1.2, "8b", "B/D", "The red path runs from the card to a hooded silhouette at a glowing laptop (no face, no real person)", "-", "Pull back to reveal the silhouette", "Red path", [], "out"),
    (2.4, "8c", "A", "Cut to her face as it lands: dread", "bus_dread", "Push-in", "-", [(2.4, "thud")], "out")],
9: [(0.0, "9a", "A", "R1 HARD CUT: her phone screen goes dark and her dread face is reflected in it (no pure-black frame)", "bus_dread", "Hard cut, locked-off, tiny drift", "-", [(0.0, "silence")], "out"),
    (1.4, "9b", "A", "Slow push into the reflection; a low pulse starts", "-", "Slow push", "-", [(1.4, "pulse")], "out")],
10: [(0.0, "10a", "C", "NEW SET: her kitchen, the clock reads 10:12, warm lamp, dark window", "-", "Wide drift", "Clock '10:12'", [(0.0, "room_tone")], "on"),
     (1.2, "10b", "C", "Whip pan to the counter: the phone rings, 'Fraud Team' on the screen", "-", "Whip pan", "Call card 'Fraud Team'", [(1.2, "ringtone")], "on")],
11: [(0.0, "11a", "C", "She answers; dread on her face as the voice starts", "kit_dread", "Push-in, 65-75 mm", "-", [(0.0, "pulse")], "on"),
     (1.5, "11b", "B", "A dashed path from the fake page connects to the caller card; a masked card number scrolls past", "-", "Fast push", "Dashed path, masked digits", [], "on")],
12: [(0.0, "12a", "B", "Bank screen: the 'SAFE ACCOUNT' button hovers under 'Move £4,200'", "-", "Fast push", "Generic bank screen", [(0.3, "alarm_tick")], "on"),
     (1.3, "12b", "C", "Cut to her face: the shock snap (start the clip at frame 10); hold under 1 s", "kit_shock", "Fast push, hold under 1 s", "-", [(1.3, "stab")], "on"),
     (2.4, "12c", "B", "The balance counter falls from £4,200 toward £0. MUSIC OUT half a beat before the turn", "-", "Push", "Balance counter", [(2.4, "alarm_tick")], "out_late")],
13: [(0.0, "13a", "B", "THE TURN: music hits back; a shield glows over the Messages icon; the call card fades out", "-", "Push into the phone", "Shield glow", [(0.0, "lock_click"), (0.0, "music_hit")], "on"),
     (1.3, "13b", "C", "Her face goes from hope to the open grin", "kit_hope_relief", "Slow push", "-", [], "on"),
     (2.3, "13c", "B", "Push into the phone; the Messages icon glows", "-", "Push-in", "-", [], "on")],
14: [(0.0, "14a", "B", "MUSIC OUT. The scam banner slides into a folder labelled 'Unknown Senders'", "-", "Slow drift", "Folder label", [(0.1, "whoosh_soft")], "out"),
     (1.4, "14b", "C", "The phone stays dark and silent on the counter; she watches, soft relief", "kit_soft_relief", "Slow drift", "-", [], "out"),
     (2.9, "14c", "D", "The hooded silhouette at the laptop slumps", "-", "Slow push", "-", [], "out")],
15: [(0.0, "15a", "B", "Push into her phone, Messages open", "-", "Push-in", "-", [(0.0, "rise")], "on"),
     (1.3, "15b", "B", "The Filters button glows with an orange box (the path starts here)", "-", "Push-in", "Orange box on Filters", [], "on")],
16: [(0.0, "16a", "B", "SETTINGS CARD: three panels tick through Messages > Filters > Manage Filtering > Screen Unknown Senders, orange box on each", "-", "Hold 3.6 s, tiny drift only", "Orange boxes", [(0.8, "tick"), (1.6, "tick"), (2.4, "tick")], "on"),
     (3.6, "16b", "B", "Close-up: the Screen Unknown Senders toggle slides on", "-", "Push-in", "Orange box on the toggle", [(4.2, "toggle_click")], "on")],
17: [(0.0, "17a", "B", "Her thumb opens the shop's own app (generic icon, no logo)", "-", "Over-the-shoulder", "-", [(0.2, "tap")], "on"),
     (1.7, "17b", "B/C", "A real order status loads with a green tick; relief on her face in the corner", "kit_relief", "Push-in", "'Track it here' label", [(1.9, "tick")], "on")],
18: [(0.0, "18a", "D", "A text card 'iOS 26+' slides in", "-", "Static card, under 2.5 s", "'iOS 26+'", [(0.0, "whoosh")], "on"),
     (1.4, "18b", "C", "Cut to her nodding with the phone in her hand", "kit_relief", "Push-in", "-", [], "on")],
19: [(0.0, "19a", "C", "Her face, soft relief and steady, as she says 'Already tapped?'", "kit_soft_relief", "Push-in", "-", [], "on"),
     (1.5, "19b", "D", "The back of a bank card flips into view", "-", "Flip, push-in", "-", [(1.5, "card_flip")], "on"),
     (3.0, "19c", "D", "An orange box lights the phone-number strip on the card back", "-", "Push-in", "Orange box on the number", [], "on")],
20: [(0.0, "20a", "D", "A comment box opens and a cursor blinks", "-", "Fast push to the box", "Comment box", [(0.1, "pop")], "on"),
     (1.4, "20b", "C", "Her face: hope, waiting for an answer", "kit_hope", "Push-in", "-", [], "on")],
21: [(0.0, "21a", "D", "A share arrow flies to a 'Mum' bubble", "-", "Fast push", "'Mum' bubble", [(0.1, "whoosh")], "on"),
     (1.9, "21b", "B", "LOOP: hard cut back to frame 1, the banner slams in", "-", "Cut to frame 1", "-", [(1.9, "buzz")], "on")],
}
rows, flat = [], []
for lid, subs in S.items():
    a, b = bounds[lid]
    for j, s in enumerate(subs):
        off = s[0]; nxt = subs[j + 1][0] if j + 1 < len(subs) else (b - a)
        st, en = round(a + off, 3), round(a + nxt, 3)
        d = round(en - st, 3)
        lim = 4.0 if s[1] == "16a" else 2.5
        flat.append({"id": s[1], "line": lid, "start": st, "end": en, "dur": d, "set": s[2], "action": s[3], "face_clip": s[4],
                     "camera": s[5], "overlay": s[6], "sfx": [{"t": round(a + o, 3), "name": n} for o, n in s[7]], "music": s[8],
                     "limit_s": lim, "over_limit": d > lim + 1e-6})
json.dump({"take_length_s": END, "shots": flat}, open("data/shots.json", "w"), indent=1)
with open("data/shots.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["shot", "line", "start_s", "end_s", "dur_s", "set", "what_you_see", "face_clip", "camera", "overlay", "sfx", "music"])
    for x in flat:
        w.writerow([x["id"], x["line"], x["start"], x["end"], x["dur"], x["set"], x["action"], x["face_clip"], x["camera"], x["overlay"], "; ".join(f'{e["name"]}@{e["t"]}' for e in x["sfx"]), x["music"]])
over = [x["id"] for x in flat if x["over_limit"]]
print(len(flat), "shots; longest", max(x["dur"] for x in flat), "; over limit:", over or "none")
print("avg shot", round(END / len(flat), 2), "s")
