"""The gate: checks an episode against the rules that have bitten us before. Any FAIL stops the build.

usage: python3 -I tools/gate.py <episode folder> [--vo out/<id>/vo.mp3] [--force "reason"]
  Run it three times: after the script (script checks only), after the shot list (adds sets, cameras, pace),
  and build.sh runs it again before rendering (adds the voice length). --force only with a written reason,
  which is printed so it shows in the log.

What it checks, and the mistake each one stops:
  HOOK     the what-if is asked in the first 3 lines / by 4.5 s.     (Ep 03 asked it at 31.8 s)
  ASK      the last line is one natural ask; share every other ep.   (CTA-BANK.md)
  BAIT     no "like if you agree", "share if you're British"...      (TikTok For You rules)
  FACTS    facts.md exists, "Checked on" is no more than 2 days old.  (Ep 02's stale 5.5% fix)
  VOICE    voice file 61-80 s before anything is rendered.           (Ep 03's 83 s MiniMax take)
  PACE     each picture 1.2-4 s (angle change every 2-2.5 s), at most one whip (the timeline switch).
           (9 Nov: 1.2 s cutting felt confusing; 16 Nov one-page checklist)
  SETS     at least one set not used in the previous two episodes.   (Eps 01-03 all used the same 6 sets)
  REPEATS  no camera preset over 6 times, newspaper over 3,
           rate board over 8, one set over 14 shots.                (Ep 03: 6 newspapers, 12 boards)
  TEXT     price tags 7 characters max, headlines 12 max.            (Ep 03: "£20 A YEAR" didn't fit)
 Added 6 Nov 2026 (script-rules 3, 4, 5, 12, 13):
  WORDS    160-200 words, aim 170-190 (house voice E, line by line).  (16 Nov checklist)
  LINELEN  no spoken line over 15 words (the voice goes flat).       (16 Nov voice test)
  BANNED   no AI-tell or template words (delve, crucial, "here's the twist"...).
  NUMBERS  at most 6 different spoken numbers.                       (Eps 03-04 spoke about 20)
  OPENER   line 1 is 12 words max, not a news-reader opener, no "Imagine you", no policy name.
           (Eps 01-04 opened like the news; policy openers lost 50%+ by 3 s)
  DATES    no "yesterday", "tomorrow", "tonight", "this morning".    (Ep 04's "yesterday" broke when the post slipped)
  CAST     narrator only: cast.txt absent or empty; Mate and Nan act on screen. (9 Nov rule)
  TOPICMIX facts.md "Topic family" and "Wallet" differ from the
           previous episode's.                                       (three rate episodes in a row)
  PROVOKE  facts.md logs the closely-wrong line and the planted slip.
  ASK      follow on odd episodes from Ep 05 (except 9, 15, 21...).
  SETS     a set counts as new if its world OR its era is new (worldArgs era: '1975' | '1988' ...).
 Added 20 Nov 2026 (WW2 loan video: 28% watched, most left at 0:01; savings video: 16%, left at 0:02):
  FIRSTWORDS the line-1 pop word (*shock*) is in its first 4 words, so it is heard inside 1 s.
  REPEAT   no line said twice in one script.                      ("But what if X?" twice: filler)
  STOCK    no line copied from the previous two episodes.          (the same guess/number/sum lines every time)
  VOICE    61-70 s (aim 61-68); WPS 2.8+ words a second.           (WW2 loan video: 2.6 w/s, 80 s)
  EMOTION  voice loudness range 2.8 LU or more (voice.txt gain column). (WW2 loan video: 1.5 LU, flat)
"""
import json, re, subprocess, sys, os, datetime

args = sys.argv[1:]
if not args:
    sys.exit(__doc__)
EP = args[0]
VO = args[args.index('--vo') + 1] if '--vo' in args else None
FORCE = args[args.index('--force') + 1] if '--force' in args else None
D = f'src/episodes/{EP}'
fails, warns, oks = [], [], []
def fail(k, m): fails.append(f'{k:9s}{m}')
def ok(k, m): oks.append(f'{k:9s}{m}')

# ---- script ----
lines = [l.strip() for l in open(f'{D}/script.txt') if l.strip()]
plain = lambda s: re.sub(r'[*]', '', s).lower()
hook_line = next((i for i, l in enumerate(lines) if 'what if' in plain(l)), None)
if hook_line is None or hook_line > 2:
    fail('HOOK', f'"what if" first appears in line {"none" if hook_line is None else hook_line + 1}: ask it in line 1-3')
else:
    ok('HOOK', f'what-if asked in line {hook_line + 1}')

last = plain(lines[-1])
ASKS = {'share': r'\b(send (this|it|them)|share)\b', 'save': r'\bsave (this|it)\b|\bsaves\b', 'follow': r'\bfollow\b|stick around',
        'comment': r'\bcomments?\b|tell me|make your case|pick a side|below', 'like': r'\b(a )?like\b'}
found = [k for k, rx in ASKS.items() if re.search(rx, last)]
if not found:
    fail('ASK', f'last line has no ask (share/save/follow/comment/like): "{lines[-1]}"')
elif len(found) > 2:
    fail('ASK', f'last line asks for {", ".join(found)}: one ask, two at most')
else:
    ok('ASK', ' + '.join(found))
order = [l.strip() for l in open('src/episodes/ORDER.txt') if l.strip() and not l.startswith('#')]
if EP in order:
    n = order.index(EP) + 1  # episode number
    if n >= 4 and n % 2 == 0 and 'share' not in found:
        fail('ASK', f'Ep {n:02d} is a share episode (every even episode from Ep 04): end on a share line from CTA-BANK.md')
    if n >= 5 and n % 2 == 1 and not (n >= 9 and n % 6 == 3) and 'follow' not in found:
        fail('ASK', f'Ep {n:02d} is a follow episode (odd episodes from Ep 05): end on a follow line that names a scripted next episode')
    if n >= 4 and n % 2 == 1 and found and found[0] == 'share' and len(found) == 1:
        fail('ASK', f'Ep {n:02d} sits between share episodes: use save, follow, comment or like (a share can ride along as a two-ask line)')
else:
    fail('ASK', f'{EP} is not listed in src/episodes/ORDER.txt: add it so the rotation can be checked')

BAIT = r'like if you agree|comment (yes|no|1|below if)|follow for follow|share (or|if you\'?re)|bad luck|tag \d+ (friends|people)'
bait = [l for l in lines if re.search(BAIT, plain(l))]
if bait: fail('BAIT', f'bait wording: "{bait[0]}"')

# ---- 6 Nov 2026 rules ----
toks = ' '.join(lines).split()
nw = len(toks)
if 160 <= nw <= 200: ok('WORDS', f'{nw} words (aim 170-190; measure the voice take)')
else: fail('WORDS', f'{nw} words: keep to 160-200, aim 170-190 (one-page checklist 5)')
longl = [l for l in lines[:-1] if len(plain(l).split()) > 15]
if longl: fail('LINELEN', f'{len(longl)} line(s) over 15 words, e.g. "{longl[0]}": split it (the voice goes flat on long lines)')
else: ok('LINELEN', 'every line 15 words or fewer')
BANW = r"\b(delve|tapestry|crucial|vital|furthermore|moreover|additionally|in conclusion|unlock|elevate|game-changer|journey)\b|here'?s the twist|here'?s where it gets|but there'?s another problem|it'?s important to note"
bw = [l for l in lines if re.search(BANW, plain(l))]
if bw: fail('BANNED', f'banned wording: "{bw[0]}"')

NUMW = set('two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million billion trillion nought zero half quarter'.split())
JOIN = {'and', 'point', 'a'}
nums, cur = [], []
for t in [re.sub(r"[^\w'£%.-]", '', plain(x)).strip('.,') for x in toks] + ['']:
    parts = [q for q in re.split(r'-', t) if q]
    isnum = bool(parts) and (parts[0] in NUMW or bool(re.fullmatch(r'£?\d[\d,.]*%?', t)))
    if isnum or (cur and t in JOIN and t != ''):
        cur.append(t)
    else:
        while cur and cur[-1] in JOIN: cur.pop()
        if cur: nums.append(' '.join(cur))
        cur = []
distinct = sorted(set(nums))
if len(distinct) > 6: fail('NUMBERS', f'{len(distinct)} different spoken numbers (max 6): {", ".join(distinct)}')
else: ok('NUMBERS', f'{len(distinct)} different numbers: {", ".join(distinct) or "none"}')

l1 = plain(lines[0])
POLICY = r'allowance|threshold|salary sacrifice|national insurance|fiscal|monetary policy|bank rate|base rate|\bisa\b|triple lock|personal savings'
NEWS = r'^(imagine you|this week|the average|yesterday|today|this morning|last week|breaking|on (monday|tuesday|wednesday|thursday|friday)[, ]+the bank)'
if len(l1.split()) > 12: fail('OPENER', f'line 1 is {len(l1.split())} words (max 12)')
elif re.search(NEWS, l1): fail('OPENER', f'line 1 opens like the news or with "Imagine you": "{lines[0]}": lead with a loss or a claim')
elif re.search(POLICY, l1): fail('OPENER', f'line 1 names a policy: "{lines[0]}": use "your" + an everyday thing; name the policy after 5 s')
else: ok('OPENER', 'line 1 leads with a claim, not a news opener')

# ---- 20 Nov 2026: what the WW2 loan and savings videos' retention graphs showed (half gone by 0:01-0:02) ----
# FIRSTWORDS: the starred pop word (the shock) is in the first 4 words of line 1, so it is heard inside 1 s.
w1 = lines[0].split()
star = next((i for i, w in enumerate(w1) if '*' in w), None)
if star is None or star > 3:
    fail('FIRSTWORDS', f'line 1 pop word is {"missing" if star is None else f"word {star + 1}"}: put the shock (*word*) in the first 4 words, e.g. "America *lost* money on..." (WW2 loan video "Your tax was still..." lost half its viewers by 0:01)')
else:
    ok('FIRSTWORDS', f'shock word "{w1[star]}" is word {star + 1}')
# REPEAT: no line said twice ("But what if X?" twice in Ep 19 and the WW2 loan video reads as filler)
norm = lambda s: re.sub(r'[^a-z ]', '', plain(s)).strip()
seen_l = {}
for l in lines:
    for part in re.split(r'(?<=[.?!])\s+', l):
        n_ = norm(part)
        if len(n_.split()) >= 3 and n_ in seen_l: fail('REPEAT', f'"{part}" is said twice: cut the second or say something new')
        seen_l[n_] = 1
# STOCK: no line copied from the previous two episodes ("Wait, hold on. That's just our guess!", "Now the real number.",
# "Our own sum.", "For me?" were in every episode: returning viewers can predict the video)
if EP in order and order.index(EP) > 0:
    prevl = set()
    for p in order[max(0, order.index(EP) - 2):order.index(EP)]:
        if os.path.exists(f'src/episodes/{p}/script.txt'):
            for pl in open(f'src/episodes/{p}/script.txt'):
                for part in re.split(r'(?<=[.?!])\s+', pl.strip()):
                    if len(norm(part).split()) >= 2: prevl.add(norm(part))
    stock = [part for l in lines for part in re.split(r'(?<=[.?!])\s+', l) if norm(part) in prevl]
    if stock: fail('STOCK', f'{len(stock)} line(s) copied from the last two episodes, e.g. "{stock[0]}": keep the honesty (label guesses and sums), change the words')
    else: ok('STOCK', 'no stock lines from the last two episodes')

DATEW = r'\b(yesterday|tomorrow|tonight|this morning|last night)\b'
dl = [l for l in lines[:-1] if re.search(DATEW, plain(l))]  # the ask follows the CTA rule
if dl: fail('DATES', f'"{dl[0]}" breaks if the post slips a day: say "on Thursday" or "on 5 November"')

cp = f'{D}/cast.txt'
cl = [l.strip() for l in open(cp) if l.strip() and not l.startswith('#')] if os.path.exists(cp) else []
if cl: fail('CAST', f'{len(cl)} voiced cast line(s) in cast.txt: narrator only; Mate and Nan act on screen (empty the file)')
else: ok('CAST', 'narrator only')

fp = f'{D}/facts.md'
ff = open(fp).read() if os.path.exists(fp) else ''
def meta(txt, key):
    m = re.search(rf'^{key}:\s*(.+)$', txt, re.M | re.I); return m.group(1).strip().lower() if m else None
fam, wal = meta(ff, 'Topic family'), meta(ff, 'Wallet')
if not fam or not wal:
    fail('TOPICMIX', 'facts.md needs "Topic family: ..." and "Wallet: ..." lines')
elif EP in order and order.index(EP) > 0:
    pf = f'src/episodes/{order[order.index(EP) - 1]}/facts.md'
    pt = open(pf).read() if os.path.exists(pf) else ''
    pfam, pwal = meta(pt, 'Topic family'), meta(pt, 'Wallet')
    if pfam and pfam == fam: fail('TOPICMIX', f'topic family "{fam}" again after {order[order.index(EP) - 1]}: pick another family')
    elif pwal and pwal == wal: fail('TOPICMIX', f'wallet "{wal}" again after {order[order.index(EP) - 1]}: carry the number on another cost')
    else: ok('TOPICMIX', f'{fam} / {wal}' + ('' if pfam else ' (previous episode has no family logged)'))
if not re.search(r'^Closely wrong:', ff, re.M) or not re.search(r'^Slip:', ff, re.M):
    fail('PROVOKE', 'facts.md needs a "Closely wrong:" line (with its pinned comment) and a "Slip:" line (script-rules 12)')
else:
    ok('PROVOKE', 'closely-wrong line and slip logged')

# ---- facts ----
fp = f'{D}/facts.md'
if not os.path.exists(fp):
    fail('FACTS', f'no {fp}: list every "today" number with its source and a "Checked on: YYYY-MM-DD" line')
else:
    m = re.search(r'Checked on:\s*(\d{4}-\d{2}-\d{2})', open(fp).read())
    if not m:
        fail('FACTS', 'facts.md has no "Checked on: YYYY-MM-DD" line')
    else:
        age = (datetime.date.today() - datetime.date.fromisoformat(m.group(1))).days
        if age > 2:
            fail('FACTS', f'"today" numbers last checked {age} days ago: recheck them (rates and prices move) and update the date')
        else:
            ok('FACTS', f'checked {m.group(1)}')

# ---- voice ----
if VO and os.path.exists(VO):
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', VO],
                               capture_output=True, text=True).stdout.strip() or 0)
    if dur > 70:
        fail('VOICE', f'voice is {dur:.1f} s (max 70 since 20 Nov; aim 61-68): raise line speeds in voice.txt (tools/house_voice.py) or trim the script')
    elif dur < 61:
        fail('VOICE', f'voice is {dur:.1f} s (min 61, or Creator Rewards pays nothing): lower line speeds or lengthen pauses in voice.txt, or add a line')
    else:
        ok('VOICE', f'{dur:.1f} s')
    if dur:
        wps = nw / dur
        if wps < 2.8: fail('WPS', f'{wps:.2f} words a second (min 2.8, aim 2.9-3.2): raise line speeds; the WW2 loan video ran 2.6 and averaged 28% watched')
        else: ok('WPS', f'{wps:.2f} words a second')
    e = subprocess.run(['ffmpeg', '-i', VO, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    m = re.findall(r'LRA:\s+([\d.]+) LU', e)
    if m:
        lra = float(m[-1])
        if lra < 2.8: fail('EMOTION', f'voice loudness range {lra} LU (min 2.8): every line at one level sounds flat; use the gain column in voice.txt (+2..+3 shocks, -2..-3 asides)')
        else: ok('EMOTION', f'voice loudness range {lra} LU')

# ---- shot list ----
et = f'{D}/episode.ts'
if os.path.exists(et):
    src = open(et).read()
    shots_src = src[src.index('const S: Shot[]'):] if 'const S: Shot[]' in src else src
    def setids(txt):  # a set = its world, plus its era if the shot gives one (worldArgs: { era: '1988' })
        out = []
        for m in re.finditer(r"world: '(\w+)'(?:, worldArgs: (\{[^}]*\}|[A-Z_]+))?", txt):
            era = re.search(r"era: '(\w+)'", m.group(2) or '')
            out.append(m.group(1) + (f"@{era.group(1)}" if era else ''))
        return out
    worlds = setids(shots_src)
    cams = re.findall(r'cam: ([A-Z_]+)\(', shots_src)
    def count(xs): return {x: xs.count(x) for x in set(xs)}
    for c, k in sorted(count(cams).items(), key=lambda x: -x[1]):
        if k > 6: fail('REPEATS', f'camera {c} used {k} times (max 6): vary the angle')
    for w, k in count(worlds).items():
        if k > 14: fail('REPEATS', f'set {w} used for {k} shots (max 14)')
    np_, nb = len(re.findall(r'\bpaper\(', shots_src)), len(re.findall(r'\bboard\(', shots_src))
    if np_ > 3: fail('REPEATS', f'newspaper shot used {np_} times (max 3)')
    if nb > 8: fail('REPEATS', f'rate board used {nb} times (max 8)')
    for t in re.findall(r"\btag\('([^']*)'", shots_src):
        if len(t) > 7: fail('TEXT', f'price tag "{t}" is {len(t)} characters (max 7): it will not fit')
    for t in re.findall(r"\bpaper\('([^']*)'", shots_src):
        if len(t) > 12: fail('TEXT', f'headline "{t}" is {len(t)} characters (max 12)')
    # new set: compare with the previous two episodes in ORDER.txt
    if EP in order:
        prev = [p for p in order[:order.index(EP)] if os.path.exists(f'src/episodes/{p}/episode.ts')][-2:]
        seen = set()
        for p in prev:
            ps = open(f'src/episodes/{p}/episode.ts').read()
            seen |= set(setids(ps))
        new = sorted(set(worlds) - seen)
        if prev and not new:
            fail('SETS', f'every set was already used in {", ".join(prev)}: build at least one new set for this episode')
        elif new:
            ok('SETS', f'new: {", ".join(new)}')
    if not any(f.startswith(('REPEATS', 'TEXT')) for f in fails):
        ok('REPEATS', f'{len(set(cams))} camera presets, {len(set(worlds))} sets, {np_} newspapers, {nb} boards')
    # pace, on the real (or placeholder) word timings
    r = subprocess.run(['npx', 'tsx', 'tools/dumpevents.mts', EP], capture_output=True, text=True)
    ev = f'out/{EP}/events.json'
    if os.path.exists(ev):
        e = json.load(open(ev))
        sh = [{'id': s['id'], 'start': s['start'], 'end': s['end'], 'move': {'fly': 'fly', 'whip': 'fast'}.get(s['enter'], 'cut' if i else 'drift')}
              for i, s in enumerate(e['shots'])]
        for s in sh[:-1]:  # the end card may run long
            d = s['end'] - s['start']
            if d > 4.0: fail('PACE', f'{s["id"]} stays {d:.2f} s (max 4): change the angle (same location) every 2-2.5 s')
            if d < 1.2: fail('PACE', f'{s["id"]} lasts {d:.2f} s (min 1.2): too fast to read; merge it with a neighbour')
        whips = [s['id'] for s in sh if s['move'] == 'fast']
        if len(whips) > 1: fail('PACE', f'{len(whips)} whips ({", ".join(whips)}): only the timeline switch may whip')
        words = json.load(open(f'{D}/words.json'))
        wi = next((i for i in range(len(words) - 1) if plain(words[i]['text']).strip('.,?!') == 'what' and plain(words[i + 1]['text']).strip('.,?!') == 'if'), None)
        if wi is not None and words[wi]['start'] > 4.5:
            fail('HOOK', f'"what if" is heard at {words[wi]["start"]:.1f} s: it must be by 4.5 s')
        if not any(f.startswith('PACE') for f in fails):
            ok('PACE', f'{len(sh)} pictures, longest {max(s["end"] - s["start"] for s in sh):.1f} s')

print(f'GATE {EP}')
for o in oks: print('  ok   ' + o)
for f in fails: print('  FAIL ' + f)
if fails and FORCE:
    print(f'  forced past {len(fails)} fail(s): {FORCE}')
    sys.exit(0)
if fails:
    print(f'  {len(fails)} fail(s): fix them, then run the gate again.')
    sys.exit(1)
print('  gate passed')
