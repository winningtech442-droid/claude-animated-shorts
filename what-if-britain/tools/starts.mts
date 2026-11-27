// Prints each shot's start, length and a still time at 0.3 and 0.85 of the shot. usage: npx tsx tools/starts.mts demo
import { shotStarts, duration } from '../src/engine/timeline';
const id = process.argv[2];
const mod = await import(`../src/episodes/${id}/episode.ts`);
const ep = Object.values(mod)[0] as any;
const s = shotStarts(ep), end = duration(ep);
const times: string[] = [];
s.forEach((a, i) => { const b = s[i + 1] ?? end; console.error(`${ep.shots[i].id}\t${a.toFixed(2)}\t${(b - a).toFixed(2)} s`); times.push((a + 0.3 * (b - a)).toFixed(2), (a + 0.85 * (b - a)).toFixed(2)); });
console.error(`total ${end.toFixed(2)} s`);
console.log(times.join(' '));
