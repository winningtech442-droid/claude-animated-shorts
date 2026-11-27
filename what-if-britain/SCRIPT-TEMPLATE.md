# EP<nn>: <working title>

Status: script DRAFT / APPROVED <date> · test render PENDING / APPROVED <date>

This is the layout the user reviews before anything is voiced (STUDIO-RULES section 0). It reads top to bottom on a
phone: the card first, then the facts, then the script as it plays. The build notes come only after approval.

## The card (read this first)
- **Premise:** <one line a friend would answer with "wait, then what?">
- **Opener myth, then the real fact:** <"you might think..."> / <the fact the twist pays off>
- **Mid-video line:** "What if Britain <...>?" at <time> (35-55 % of the runtime)
- **Twist:** <one line, and which fact it carries>
- **Cliffhanger:** <the last line, cut at "...">
- **Swear (bleeped):** <word> at <time> (must be before 0:15) / none
- **New scenes (3-5):** <1. place> · <2. place> · <3. place> (+ the Booth, 6 s at most)
- **Guests:** <role: build, look, voice>
- **Lore:** <thread added or advanced>
- **Checks:** <words> words · ~<seconds> s · lines after the redirection average <n> words · <n> % questions

## Facts (checked on <date>)
| Fact | Where it shows up | Source |
|---|---|---|
| <fact> | <spoken by X at 0:42 / on the price board at 0:31 / in the twist> | <source, link> |

## Script
Format: `SPEAKER (tone, exaggeration): line`. `SEE:` is what the viewer watches happen. `*word*` turns red in the captions.

### 0:00 BAIT · Scene 1: <place>, <time of day>
SEE: <the stunt, already happening on frame 1>
HOOK LINE ON SCREEN (0-3 s): <4 words max, with a money word>
NARRATOR (bright, fast, 0.5): If you <money stunt>, you might think <money myth>, but you might be surprised to know that-

### 0:07 REDIRECTION
SEE: <how the stunt goes wrong and cuts him off>
SFX: <impact>, then 0.5-1 s of stillness, the bed still playing

### 0:08 REVEAL · The Booth
PRODUCER (off-mic, 0.7): <short line>
NARRATOR (rattled, 0.8): <short line>

### 0:15 DROP · Scene 2: <place>
SEE: <the pin fires; where Alfie wakes up>
ALFIE (confused, 0.7): <short question>

### 0:<xx> WHAT IF BRITAIN
NARRATOR (recovering, 0.6): <...what if Britain ...?>
SEE: title card slams in

### 0:<xx> ACTIVE LADDER
Beat 1 · Scene <n>: <place>. SEE: <physical task with a money object>. FACT: <how it shows>
Beat 2 · ...
Beat 3 · ...

### 0:<xx> TWIST
SEE: <what turns>
<SPEAKER> (<tone>): <the line that completes the narrator's cut-off sentence>

### 0:<xx> CLIFFHANGER
SEE: <the loudest moment>
<SPEAKER> (shouting, 1.2): <last line, cut mid-wo->
CUT TO BLACK

## Voice sheet (after the script is approved)
`speaker|exaggeration|cfg|pause|text`, one line per row, saved as `src/episodes/<id>/voice.txt`.

## Build notes (after approval; skim only)
| # | Shot | Camera | Who (face + pose) | Props / text on screen | SFX |
|---|---|---|---|---|---|
