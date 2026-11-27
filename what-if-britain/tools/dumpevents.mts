// Writes out/<id>/events.json from an episode: shot cuts and how they enter, the number card, prop pop-ins, words.
// The sound scripts read only this file. usage: npx tsx tools/dumpevents.mts demo
import fs from 'node:fs';
import { shotStarts, duration } from '../src/engine/timeline';
const id = process.argv[2];
const mod = await import(`../src/episodes/${id}/episode.ts`);
const ep = Object.values(mod)[0] as any;
const s = shotStarts(ep), end = duration(ep);
const shots = ep.shots.map((sh: any, i: number) => ({ id: sh.id, start: s[i], end: s[i + 1] ?? end, enter: sh.enter ?? 'cut', world: sh.world }));
const numbers = ep.shots.flatMap((sh: any, i: number) => (sh.number ? [{ t: s[i] + (sh.number.at ?? 0.2), text: sh.number.text }] : []));
const pops = ep.shots.flatMap((sh: any, i: number) => (sh.props ?? []).flatMap((p: any) => [
  ...(p.from !== undefined ? [{ t: s[i] + p.from, kind: p.kind, type: 'pop' }] : []),
  ...(p.grow ? [{ t: s[i] + p.grow.t0, t1: s[i] + p.grow.t1, kind: p.kind, type: 'grow', from: p.grow.from, to: p.grow.to }] : []),
]));
fs.mkdirSync(`out/${id}`, { recursive: true });
fs.writeFileSync(`out/${id}/events.json`, JSON.stringify({ id: ep.id, total: end, shots, numbers, pops, words: ep.words }, null, 1));
console.log(`out/${id}/events.json: ${shots.length} shots, ${numbers.length} number cards, ${pops.length} prop events, ${end.toFixed(2)} s`);
