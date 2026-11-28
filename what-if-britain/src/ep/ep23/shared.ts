// EP23 shared timing and motion helpers. S(n) / E(n): line n's start and end from lines.json. Until the real voices
// exist, lines.json comes from tools/placeholder_cast.py; tools/cast_voice.py overwrites it and every shot follows.
import lines from '../../episodes/ep23/lines.json';
import words from '../../episodes/ep23/words.json';
import { lerp } from '../kit3';
import type { Key3, Pose3 } from '../kit3';

const L = lines as { start: number; end: number }[];
export const S = (n: number) => L[n - 1].start;
export const E = (n: number) => L[n - 1].end;
const W = words as { text: string; start: number; line: number }[];
/** Start time of the first caption word in line n that begins with txt. */
export const wordAt = (txt: string, n: number) => W.find((w) => w.line === n && w.text.replace(/[*.…]/g, '').startsWith(txt))!.start;

/** Walking keys from x0 to x1 over [t0, t1] (shot time): legs and the free arm alternate every half stride. */
export const walk = (t0: number, t1: number, x0: number, x1: number, stride = 0.36, base: Pose3 = {}, freeArm: 'L' | 'R' | 'both' | 'none' = 'L'): Key3[] => {
  const out: Key3[] = []; const n = Math.max(1, Math.round((t1 - t0) / stride));
  for (let i = 0; i <= n; i++) {
    const t = t0 + (i * (t1 - t0)) / n, k = i / n, s = i % 2 ? 1 : -1;
    const arms: Pose3 = freeArm === 'none' ? {} : freeArm === 'R' ? { shR: [-14 * s, 6], elR: 18 } : freeArm === 'L' ? { shL: [14 * s, 6], elL: 18 } : { shL: [14 * s, 6], elL: 18, shR: [-14 * s, 6], elR: 18 };
    out.push([t, { ...base, x: lerp(x0, x1, k), hipL: [24 * s, 3], knL: s > 0 ? 8 : 30, hipR: [-24 * s, 3], knR: s > 0 ? 30 : 8, bounce: 0.012 * (i % 2), ...arms }, 'lin']);
  }
  return out;
};
/** The actor's x at shot time ts (linear between keys, as walk uses). */
export const xAt = (keys: Key3[], ts: number) => {
  let px = keys[0][1].x ?? 0, pt = keys[0][0];
  for (const [t, p] of keys) { const nx = p.x ?? px; if (ts <= t) return t === pt ? nx : lerp(px, nx, (ts - pt) / (t - pt)); px = nx; pt = t; }
  return px;
};
export const pinIdle = (ts: number) => 0.15 + 0.1 * Math.sin(ts * 5);
export const pinLive = (ts: number) => 0.65 + 0.35 * Math.sin(ts * 7);

/** Hugging something to the chest: both forearms across the front. */
export const HUG: Pose3 = { shL: [30, -10], elL: 92, twL: 62, shR: [30, -10], elR: 92, twR: 62, handL: 'open', handR: 'open' };
/** Gripping something held out in front at chest height with both hands. */
export const GRIP: Pose3 = { shL: [78, -8], elL: 25, shR: [78, -8], elR: 25, handL: 'fist', handR: 'fist' };
/** Sitting on the floor, legs out, leaning back on the hands (root y about -0.42). */
export const FLOOR_SIT: Pose3 = { sit: true, y: -0.42, hipL: [72, 14], knL: 18, hipR: [72, 10], knR: 22, spine: -14, shL: [-35, 25], elL: 10, shR: [-35, 25], elR: 10, handL: 'open', handR: 'open' };
/** A point in front of an actor standing at (x, z) facing ry, at height y and distance d. */
export const ahead = (x: number, z: number, ry: number, y: number, d: number): [number, number, number] => [x + d * Math.sin(ry), y, z + d * Math.cos(ry)];
