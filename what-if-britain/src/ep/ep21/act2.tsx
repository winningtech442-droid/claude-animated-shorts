// EP21 Mattress Money, 0:20 to the end: the blown-away note, "What if Britain...?", the ladder (corner shop, the
// Black Friday sale, Nan's kitchen), the twist at Nan's window and the cliffhanger on Grandad's pin.
// Shot windows are tied to the voice track (src/episodes/ep21/lines.json), so a retake only nudges them.
import React from 'react';
import lines from '../../episodes/ep21/lines.json';
import { cam, Shot, Actor, Key3, prog, lerp, clamp, FactCard } from '../kit3';
import { Bedroom, Booth, Clipboard } from './sets';
import { CornerShop, SaleShop, NanKitchen, TVBox, BiscuitTin, SavingsJar, Magnifier, Placard, ButterKnife, Biscuit, BigEyeGlass, Teacup, SHOPKEEPER, ASSISTANT, DOOR } from './sets2';
import { Note } from '../../props';

const PI = Math.PI;
const LN = lines as { start: number; end: number }[];
export const S = (n: number) => LN[n - 1].start;
export const E = (n: number) => LN[n - 1].end;

const Tenner: React.FC<{ s?: number }> = ({ s = 0.22 }) => <Note value="10" tint="#C97D46" s={s} />;
const Twenty: React.FC<{ s?: number }> = ({ s = 0.22 }) => <Note s={s} />;
/** a note standing up, facing +z (Note lies flat by default) */
const Up: React.FC<{ children: React.ReactNode; p: [number, number, number]; r?: [number, number, number] }> = ({ children, p, r = [0, 0, 0] }) => (
  <group position={p} rotation={r}><group rotation={[PI / 2, 0, 0]}>{children}</group></group>
);
const SKIN = '#E6B896';
const Finger: React.FC<{ p: [number, number, number]; r: [number, number, number]; L?: number }> = ({ p, r, L = 0.07 }) => (
  <mesh position={p} rotation={r}><capsuleGeometry args={[0.0105, L, 8, 16]} /><meshStandardMaterial color={SKIN} roughness={0.6} /></mesh>
);
/** a walk from (x0, z0) to (x1, z1) between shot times t0 and t1: legs and arms swing in turn, `steps` steps */
const walk = (t0: number, t1: number, steps: number, from: [number, number], to: [number, number], swing = 24): Key3[] => {
  const out: Key3[] = [];
  for (let i = 0; i <= steps; i++) {
    const s = i % 2 ? 1 : -1, k = i / steps, t = lerp(t0, t1, k);
    const legs = i === steps ? { hipL: [0, 4] as [number, number], hipR: [0, 4] as [number, number], knL: 0, knR: 0 }
      : { hipL: [swing * s, 4] as [number, number], hipR: [-swing * s, 4] as [number, number], knL: s > 0 ? 8 : 22, knR: s > 0 ? 22 : 8, shL: [-14 * s, 8] as [number, number], shR: [14 * s, 8] as [number, number] };
    out.push([t, { x: lerp(from[0], to[0], k), z: lerp(from[1], to[1], k), ...legs }, 'lin']);
  }
  return out;
};

// ===================================== 0:20 the gag: Mate blows the twenty away, Alfie jumps for it =====================================
const MATE_BED = { x: 0.18, y: 0.2, z: 0.42, ry: -0.25, sit: true, hipL: [90, 10] as [number, number], knL: 88, hipR: [90, 10] as [number, number], knR: 88 };
const NOTE0: [number, number, number] = [0.335, 1.385, 0.61];
const T_BLOW = 20.0, T_JUMP = 20.85;
const noteFlight = (t: number): [number, number, number] => {
  // from Mate's fist, up and over to where Alfie's hand meets it at the top of his jump
  const u = prog(t, T_BLOW + 0.3, T_JUMP + 0.62, 'lin');
  const a = NOTE0, b: [number, number, number] = [-0.84, 2.3, -0.95];
  return [lerp(a[0], b[0], u) + 0.05 * Math.sin(u * 14), lerp(a[1], b[1], Math.sin(u * PI / 2)) + 0.35 * Math.sin(u * PI), lerp(a[2], b[2], u)];
};
const FlyingNote: React.FC<{ t: number }> = ({ t }) => {
  const p = noteFlight(t), u = prog(t, T_BLOW + 0.3, T_JUMP + 0.62, 'lin');
  return <group position={p} rotation={[0.8 * Math.sin(u * 17), u * 9, 0.6 * Math.cos(u * 13)]}><Twenty s={0.34} /></group>;
};
const mateBlow: Actor = {
  who: 'mate', seed: 2.2,
  keys: [
    [0, { ...MATE_BED, spine: 5, face: 'disbelief', shR: [80, 30], elR: 125, twR: 25, handR: 'fist', shL: [15, 12], elL: 35, headTilt: 6, headNod: 2 }],
    [0.14, { face: 'holding', spine: 11, headNod: 8, headTilt: 0 }],
    [0.3, { face: 'holding', spine: 12 }],
    [0.4, { face: 'shock', spine: 0, headNod: -14, shR: [70, 30], elR: 100 }, 'out'],
    [0.85, { headNod: -22, headTurn: 25 }],
  ],
};
const blow: Shot = {
  id: 'blow', t0: T_BLOW, t1: T_JUMP,
  cam: [[0, cam([-0.32, 1.5, 1.6], [0.22, 1.42, 0.46], 36)], [0.85, cam([-0.38, 1.52, 1.5], [0.18, 1.48, 0.46], 36), 'lin']],
  sw: 1,
  set: (c) => (
    <Bedroom sw={1}>
      {c.t < T_BLOW + 0.3 ? <group position={NOTE0} rotation={[PI / 2 + 0.12, 0.1, 0.18]}><Twenty s={0.34} /></group> : <FlyingNote t={c.t} />}
    </Bedroom>
  ),
  cast: [mateBlow],
};
const ALF_SPOT = { x: -1.0, z: -0.85 };
const alfJump: Actor = {
  who: 'lead', seed: 0.3, pin: (ts) => 0.6 + 0.3 * Math.sin(ts * 7),
  keys: [
    [0, { x: ALF_SPOT.x, y: 0, z: ALF_SPOT.z, ry: 0.5, crouch: 0.15, spine: 8, face: 'shock', headNod: -22, shR: [40, 10], elR: 30, shL: [30, 10], elL: 30, handR: 'open' }],
    [0.3, { crouch: 0.5, spine: 18, shR: [20, 18], shL: [20, 18], face: 'worried', headNod: -26 }],
    [0.5, { y: 0.42, crouch: 0, spine: -5, shR: [178, 8], elR: 0, shL: [40, 35], elL: 20, face: 'scream', headNod: -32, hipL: [10, 6], knL: 30, hipR: [-5, 6], knR: 45 }, 'out'],
    [0.62, { y: 0.47, handR: 'fist' }],
    [0.85, { y: 0, crouch: 0.55, spine: 22, shR: [150, 10], elR: 10, face: 'shock', headNod: -10, hipL: [0, 4], knL: 0, hipR: [0, 4], knR: 0 }, 'in'],
    [1.05, { crouch: 0.22, spine: 6 }],
    [1.3, { crouch: 0.05, spine: 0, shR: [140, 10], elR: 15, face: 'happy', headNod: -12 }],
  ],
  heldR: (ts) => (ts >= 0.62 ? <group position={[0.01, -0.09, 0.04]} rotation={[PI / 2, 0, 0.2]}><Twenty s={0.34} /></group> : null),
};
const mateWatch = (face: string, turn = 35): Actor => ({
  who: 'mate', seed: 2.2,
  keys: [[0, { ...MATE_BED, spine: 4, face: face as any, headTurn: turn, shR: [20, 15], elR: 40, shL: [15, 12], elL: 35, handR: 'open' }]],
});
const jump: Shot = {
  id: 'jump', t0: T_JUMP, t1: S(8),
  cam: [[0, cam([0.78, 1.3, 2.25], [-0.72, 1.45, -0.8], 50)], [0.62, cam([0.74, 1.32, 2.15], [-0.76, 1.62, -0.82], 50), 'out'], [S(8) - T_JUMP, cam([0.72, 1.3, 2.05], [-0.78, 1.5, -0.82], 50), 'io']],
  shake: [[0.85, 0.9]],
  sw: 1,
  set: (c) => <Bedroom sw={1}>{c.ts < 0.62 ? <FlyingNote t={c.t} /> : null}</Bedroom>,
  cast: [alfJump, mateWatch('shock')],
};

// ===================================== 0:22 "What if Britain's money shrank as fast as its prices rise?" + title card =====================================
// Framing rule for the title: heads sit below the WHAT IF BRITAIN card (upper third), captions sit below the faces.
const alfHero: Actor = {
  who: 'lead', seed: 0.3, pin: (ts) => 0.75 + 0.25 * Math.sin(ts * 6),
  keys: [
    [0, { x: ALF_SPOT.x, y: 0, z: ALF_SPOT.z, ry: 0.35, spine: 0, face: 'happy', headNod: 2, headTurn: -6, shR: [96, 8], elR: 78, handR: 'fist', shL: [10, 10], elL: 20 }],
    [0.8, { face: 'smug', headTilt: 6 }],
    [1.95, { shR: [98, 8] }],
  ],
  heldR: () => <group position={[0.01, -0.095, 0.035]} rotation={[PI / 2 - 0.3, 0, 0.15]}><Twenty s={0.34} /></group>,
};
const hero: Shot = {
  id: 'hero', t0: S(8), t1: S(8) + 1.95,
  cam: [[0, cam([-0.62, 1.5, 1.05], [-0.98, 1.74, -0.85], 44)], [1.95, cam([-0.66, 1.5, 0.82], [-0.98, 1.74, -0.85], 44), 'lin']],
  sw: 1,
  set: () => <Bedroom sw={1} />,
  cast: [alfHero, mateWatch('disbelief', 30)],
};
const T_SHRINK = S(8) + 2.85; // on "prices rise?" the twenty shrinks another notch
const shrinkS = (t: number) => lerp(0.34, 0.19, prog(t, T_SHRINK, T_SHRINK + 0.25, 'back'));
const shrink: Shot = {
  id: 'shrink', t0: S(8) + 1.95, t1: E(8) + 0.15,
  cam: [[0, cam([-0.5, 1.72, 0.25], [-0.8, 1.64, -0.72], 32)], [E(8) + 0.15 - (S(8) + 1.95), cam([-0.53, 1.71, 0.12], [-0.8, 1.64, -0.72], 32), 'lin']],
  sw: 1,
  set: () => <Bedroom sw={1} />,
  cast: [{
    who: 'lead', seed: 0.3, pin: () => 0.6,
    keys: [
      [0, { x: ALF_SPOT.x, y: 0, z: ALF_SPOT.z, ry: 0.35, face: 'disbelief', headNod: -4, shR: [100, 4], elR: 92, handR: 'open', shL: [10, 10], elL: 20 }],
      [T_SHRINK - (S(8) + 1.95), { face: 'disbelief' }],
      [T_SHRINK - (S(8) + 1.95) + 0.18, { face: 'shock' }],
    ],
    heldR: (ts) => <group position={[0.0, -0.125, -0.032]} rotation={[-PI / 2 - 0.15, 0, -0.1]}><Twenty s={shrinkS(ts + S(8) + 1.95)} /></group>,
  }],
};

// ===================================== 0:26 ladder beat 1: the corner shop =====================================
const NOTE_ON_COUNTER: [number, number, number] = [0.32, 1.036, -0.5];
const T_SLAP = 1.05;
const keeper = (keys: Key3[]): Actor => ({ who: 'shopkeeper', look: SHOPKEEPER, seed: 4.1, keys });
const KEEP_BASE = { x: 0.78, y: 0, z: -1.32, ry: 0, face: 'bored' as const, shL: [22, 14] as [number, number], elL: 112, twL: 65, shR: [22, 14] as [number, number], elR: 112, twR: 65, headNod: 6 };
const shopIn: Shot = {
  id: 'shop-in', t0: E(8) + 0.15, t1: S(9) - 0.05,
  cam: [[0, cam([-1.15, 1.6, 1.8], [0.45, 1.25, -0.75], 46)], [1.7, cam([-1.02, 1.55, 1.52], [0.45, 1.26, -0.75], 46), 'lin']],
  shake: [[T_SLAP, 0.8]],
  sw: 1,
  set: (c) => (
    <CornerShop drawer={prog(c.ts, T_SLAP + 0.02, T_SLAP + 0.12, 'out')}>
      {c.ts >= T_SLAP ? <group position={NOTE_ON_COUNTER} rotation={[0, 0.3, 0]}><Tenner /></group> : null}
    </CornerShop>
  ),
  cast: [
    keeper([[0, { ...KEEP_BASE }], [T_SLAP + 0.08, { ...KEEP_BASE }], [T_SLAP + 0.55, { spine: 24, headNod: 26, face: 'disbelief' }]]),
    {
      who: 'lead', seed: 0.3, pin: () => 0.5,
      keys: [
        [0, { x: 1.75, y: 0, z: 0.95, ry: -2.12, face: 'angry', spine: 6, headNod: 0 }],
        ...walk(0, 0.72, 4, [1.75, 0.95], [0.3, 0.05]),
        [0.8, { ry: PI, shL: [10, 8], shR: [40, 10], elR: 40 }],
        [0.9, { shR: [150, 10], elR: 35, spine: -4, handR: 'open' }, 'out'],
        [T_SLAP, { shR: [58, 4], elR: 14, spine: 22, headNod: 10 }, 'in'],
        [1.7, { spine: 18, shR: [55, 4], elR: 16 }],
      ],
    },
  ],
};
const shopKeeper: Shot = {
  id: 'shop-keeper', t0: S(9) - 0.05, t1: E(9) + 0.12,
  cam: [[0, cam([0.36, 1.32, -0.08], [0.74, 1.74, -1.32], 42)], [E(9) + 0.12 - (S(9) - 0.05), cam([0.42, 1.36, -0.3], [0.75, 1.74, -1.32], 42), 'lin']],
  sw: 1,
  set: (c) => (
    <CornerShop drawer={1} slide={prog(c.ts, 0.9, 1.9, 'io')}>
      <group position={NOTE_ON_COUNTER} rotation={[0, 0.3, 0]}><Tenner /></group>
    </CornerShop>
  ),
  cast: [keeper([
    [0, { ...KEEP_BASE, spine: 24, headNod: 26, face: 'disbelief' }],
    [0.45, { spine: 6, headNod: 12, face: 'bored', shR: [50, -4], elR: 30, twR: 0 }],
    [0.9, { shR: [62, -6], elR: 18, spine: 12 }],
    [1.9, { shR: [44, -2], elR: 36, spine: 8 }],
    [2.3, { headTilt: 5 }],
  ])],
};
const shopAlfie: Shot = {
  id: 'shop-alfie', t0: E(9) + 0.12, t1: E(10) + 0.1,
  cam: [[0, cam([1.38, 1.95, -1.68], [0.3, 1.52, 0.02], 36)], [E(10) + 0.1 - (E(9) + 0.12), cam([1.3, 1.92, -1.55], [0.3, 1.53, 0.02], 36), 'lin']],
  sw: 1,
  set: () => (
    <CornerShop drawer={1} slide={1}>
      <group position={NOTE_ON_COUNTER} rotation={[0, 0.3, 0]}><Tenner /></group>
    </CornerShop>
  ),
  cast: [
    keeper([[0, { ...KEEP_BASE, shR: [44, -2], elR: 36, twR: 0, spine: 8 }]]),
    {
      who: 'lead', seed: 0.3, pin: () => 0.5,
      keys: [
        [0, { x: 0.3, y: 0, z: 0.05, ry: PI, face: 'angry', spine: 14, headNod: -8, shR: [52, 6], elR: 6, handR: 'point', shL: [12, 10], elL: 25 }],
        [0.42, { shR: [74, 6] }], [0.62, { shR: [52, 6] }], [0.86, { shR: [76, 6], spine: 18 }], [1.08, { shR: [54, 6] }],
        [1.6, { shL: [40, 30], elL: 60, face: 'angry' }],
      ],
    },
  ],
};
// the receipt prints over "Not in here it isn't." and holds long enough to read (it sits in the top half, above the captions)
const shopReceipt: Shot = {
  id: 'shop-receipt', t0: E(10) + 0.1, t1: E(11) + 0.85,
  cam: [[0, cam([1.43, 1.42, 0.12], [1.42, 1.3, -0.66], 34)], [E(11) + 0.85 - (E(10) + 0.1), cam([1.43, 1.42, 0.06], [1.42, 1.3, -0.66], 34), 'lin']],
  sw: 1,
  set: (c) => <CornerShop drawer={1} slide={1} receipt={prog(c.ts, 0.05, 1.25, 'lin')} />,
  cast: [],
};

// ===================================== 0:34 ladder beat 2: the Black Friday sale, Mate wedged in the doorway =====================================
const T_HIT = 0.5; // shot time the box hits the door posts
const BOX = { x: 0.05, y: 0.34, z: DOOR.z - 0.19 };
const TAG_X = -0.3;
const TAG_W: [number, number, number] = [BOX.x + TAG_X * Math.cos(0.07) - 1.02 * Math.sin(0.07) + 0.008, BOX.y + 1.02 * Math.cos(0.07) + TAG_X * Math.sin(0.07) - 0.115, DOOR.z - 0.05];
const mateRun: Actor = {
  who: 'mate', seed: 2.2,
  keys: [
    [0, { x: 0.02, y: 0, z: -1.35, ry: 0, spine: 10, face: 'happy', shL: [62, 28], elL: 70, shR: [62, 28], elR: 70 }],
    ...walk(0, T_HIT, 4, [0.02, -1.35], [0.02, 0.47], 30).map(([t, p, e]): Key3 => [t, { ...p, shL: [62, 28], shR: [62, 28] }, e]),
    [T_HIT + 0.01, { spine: 14, face: 'shock' }],
    [T_HIT + 0.08, { z: 0.52, spine: -6 }, 'out'],
    [T_HIT + 0.25, { z: 0.44, spine: 4, face: 'holding' }],
  ],
};
const boxAt = (mateZ: number) => Math.min(mateZ + 0.37, BOX.z);
const assistantIdle: Actor = {
  who: 'assistant', look: ASSISTANT, seed: 3.3,
  keys: [[0, { x: -1.5, y: 0, z: 1.7, ry: 0.55, face: 'bored', shL: [28, 12], elL: 100, twL: 20, handL: 'fist', shR: [8, 10], elR: 15, headTilt: 8 }]],
  heldL: () => <Placard />,
};
const bfRun: Shot = {
  id: 'bf-run', t0: E(11) + 0.85, t1: S(12) + 0.2,
  cam: [[0, cam([0.35, 1.55, 4.9], [0.0, 1.45, 0.6], 46)], [S(12) + 0.2 - (E(11) + 0.85), cam([0.3, 1.54, 4.6], [0.0, 1.45, 0.6], 46), 'lin']],
  shake: [[T_HIT, 1.2]],
  sw: 1,
  set: (c) => {
    const mz = c.ts < T_HIT ? lerp(-1.35, 0.47, c.ts / T_HIT) : 0.47;
    const hit = c.ts > T_HIT ? Math.exp(-(c.ts - T_HIT) * 7) * Math.sin((c.ts - T_HIT) * 60) : 0;
    return (
      <SaleShop shake={hit}>
        <group position={[BOX.x, BOX.y, boxAt(mz)]} rotation={[0, 0, 0.06 * hit]}><TVBox tagX={TAG_X} /></group>
      </SaleShop>
    );
  },
  cast: [mateRun, assistantIdle],
};
const mateWedged = (keys: Key3[]): Actor => ({ who: 'mate', seed: 2.2, keys: [[0, { x: 0.02, y: 0, z: 0.44, ry: 0, spine: 4, shL: [62, 28], elL: 70, shR: [62, 28], elR: 70, face: 'holding' }], ...keys] });
const wriggle = (t: number) => Math.sin(t * 19) * (0.5 + 0.5 * Math.sin(t * 3.1));
const bfWedge: Shot = {
  id: 'bf-wedge', t0: S(12) + 0.2, t1: E(12) + 0.1,
  cam: [[0, cam([0.3, 1.66, 2.75], [0.0, 1.4, 0.72], 38)], [E(12) + 0.1 - (S(12) + 0.2), cam([0.25, 1.64, 2.45], [0.0, 1.42, 0.72], 38), 'lin']],
  sw: 1,
  set: (c) => (
    <SaleShop shake={0.35 * wriggle(c.ts)}>
      <group position={[BOX.x, BOX.y, BOX.z]} rotation={[0, 0, 0.07 + 0.025 * wriggle(c.ts)]}><TVBox tagX={TAG_X} /></group>
    </SaleShop>
  ),
  cast: [
    mateWedged([[0.25, { face: 'happy', spine: 8, x: 0.05 }], [0.55, { x: -0.01 }], [0.8, { face: 'laugh', x: 0.05, headTilt: 8 }], [1.1, { x: -0.01, headTilt: -6 }], [1.45, { x: 0.05, face: 'happy' }], [1.8, { x: 0.0 }]]),
    assistantIdle,
  ],
};
// the swing tag flips on "July" (driven by episode time, so it carries across the cut into the macro)
const T_FLIP = S(13) + 0.86;
const flipAt = (t: number) => {
  const k = prog(t, T_FLIP, T_FLIP + 0.38, 'out');
  return k + (k >= 1 ? 0.06 * Math.exp(-(t - T_FLIP - 0.38) * 6) * Math.sin((t - T_FLIP) * 30) : 0);
};
const ASSIST_AT = { x: -0.55, y: 0, z: 1.25, ry: 1.2 };
const bfAssistant: Shot = {
  id: 'bf-assistant', t0: E(12) + 0.1, t1: E(13) - 0.25,
  cam: [[0, cam([0.2, 1.3, 2.55], [-0.4, 1.15, 1.2], 40)], [E(13) - 0.25 - (E(12) + 0.1), cam([0.15, 1.3, 2.38], [-0.4, 1.16, 1.2], 40), 'lin']],
  sw: 1,
  set: (c) => (
    <SaleShop>
      <group position={[BOX.x, BOX.y, BOX.z]} rotation={[0, 0, 0.07]}><TVBox tagX={TAG_X} flip={flipAt(c.t)} /></group>
    </SaleShop>
  ),
  cast: [
    mateWedged([[0, { face: 'happy' }]]),
    {
      who: 'assistant', look: ASSISTANT, seed: 3.3,
      keys: [
        [0, { ...ASSIST_AT, face: 'bored', shL: [28, 12], elL: 100, twL: 20, handL: 'fist', shR: [8, 10], elR: 15, headTilt: 4, headNod: -4, headTurn: 30 }],
        [T_FLIP - (E(12) + 0.1) - 0.3, { shR: [122, 48], elR: 12, handR: 'point', y: 0.04, spine: 4, headNod: -6, headTurn: 0 }],
        [T_FLIP - (E(12) + 0.1) + 0.05, { shR: [130, 54], elR: 4 }, 'out'],
        [T_FLIP - (E(12) + 0.1) + 0.3, { shR: [118, 46], elR: 15, headTurn: 25 }],
      ],
      heldL: () => <Placard />,
    },
  ],
};
const bfTag: Shot = {
  id: 'bf-tag', t0: E(13) - 0.25, t1: S(14) - 0.05,
  cam: [[0, cam([TAG_W[0] + 0.02, TAG_W[1] + 0.06, TAG_W[2] + 1.05], [TAG_W[0], TAG_W[1] + 0.06, TAG_W[2]], 34)], [S(14) - 0.05 - (E(13) - 0.25), cam([TAG_W[0] + 0.02, TAG_W[1] + 0.06, TAG_W[2] + 0.95], [TAG_W[0], TAG_W[1] + 0.06, TAG_W[2]], 34), 'lin']],
  sw: 1,
  set: (c) => (
    <SaleShop>
      <group position={[BOX.x, BOX.y, BOX.z]} rotation={[0, 0, 0.07]}><TVBox tagX={TAG_X} flip={flipAt(c.t)} /></group>
    </SaleShop>
  ),
  cast: [],
};
const FACT_BF = { at: S(14) - 0.95, until: E(14) + 0.5 };
const factBF = (t: number) => (
  <FactCard t={t} at={FACT_BF.at} until={FACT_BF.until} source="Which?, Nov 2026">4 in 5 Black Friday “deals”: same price or cheaper other times</FactCard>
);
bfTag.overlay = (c) => factBF(c.t);
const bfMate: Shot = {
  id: 'bf-mate', t0: S(14) - 0.05, t1: E(14) + 0.5,
  cam: [[0, cam([0.12, 1.5, 2.15], [0.0, 1.36, 0.6], 38)], [E(14) + 0.5 - (S(14) - 0.05), cam([0.1, 1.5, 2.0], [0.0, 1.36, 0.6], 38), 'lin']],
  sw: 1,
  overlay: (c) => factBF(c.t),
  set: (c) => {
    const sag = prog(c.ts, 0.15, 0.9, 'io');
    return (
      <SaleShop>
        <group position={[BOX.x, BOX.y - 0.08 * sag, BOX.z]} rotation={[0, 0, 0.07 + 0.08 * sag]}><TVBox tagX={TAG_X} flip={1} /></group>
      </SaleShop>
    );
  },
  cast: [mateWedged([[0, { face: 'disbelief' }], [0.3, { face: 'sad', shrug: -0.7, spine: 10, headNod: 10, y: -0.04 }], [1.2, { headNod: 14 }]])],
};

// ===================================== 0:40 ladder beat 3: Nan's kitchen =====================================
// Nan stoops: her head is ~0.3 m in front of her feet at ~1.3 m (see Person: stoop bends the spine 25 degrees).
const nanHead = (p: { x: number; z: number; ry: number }): [number, number, number] => [p.x + 0.3 * Math.sin(p.ry), 1.3, p.z + 0.3 * Math.cos(p.ry)];
const NAN_TABLE = { x: -0.15, y: 0, z: -1.38, ry: 0.25 };
const NH_T = nanHead(NAN_TABLE);
const ALF_TABLE = { x: 0.52, y: 0, z: -0.33, ry: -2.6 };
const TIN: [number, number, number] = [0.14, 0.77, -0.82];
const JAR: [number, number, number] = [-0.26, 0.77, -0.98];
const CUP: [number, number, number] = [0.42, 0.77, -1.05];
const T_POP = 0.6;
const TableTop: React.FC<{ open: number; tenner?: boolean }> = ({ open, tenner = true }) => (
  <>
    <group position={TIN}><BiscuitTin open={open} /></group>
    <group position={JAR}><SavingsJar /></group>
    <group position={CUP}><Teacup /></group>
    {tenner ? <group position={[0.3, 0.772, -0.55]} rotation={[0, 0.5, 0]}><Tenner /></group> : null}
  </>
);
const nanAt = (keys: Key3[], held?: Actor['heldR'], heldL?: Actor['heldL']): Actor => ({ who: 'nan', seed: 1.1, keys, heldR: held, heldL });
const alfTable = (keys: Key3[]): Actor => ({ who: 'lead', seed: 0.3, pin: () => 0.5, keys: [[0, { ...ALF_TABLE, spine: 8, face: 'neutral', shL: [10, 8], elL: 20, shR: [10, 8], elR: 20, headNod: 10 }], ...keys] });
const kitchenTins: Shot = {
  id: 'kitchen-tins', t0: E(14) + 0.5, t1: S(15) + 1.05,
  cam: [[0, cam([0.26, 1.62, 2.05], [0.18, 1.2, -0.8], 46)], [S(15) + 1.05 - (E(14) + 0.5), cam([0.24, 1.6, 1.8], [0.18, 1.2, -0.8], 46), 'lin']],
  shake: [[T_POP, 0.5]],
  sw: 1,
  set: (c) => <NanKitchen><TableTop open={prog(c.ts, T_POP, T_POP + 0.3, 'out')} /></NanKitchen>,
  cast: [
    nanAt([
      [0, { ...NAN_TABLE, spine: 10, face: 'thinking', shR: [62, -16], elR: 40, handR: 'fist', shL: [56, 18], elL: 44, handL: 'open', headNod: 12 }],
      [0.2, { elR: 54 }], [0.32, { elR: 36 }], [0.45, { elR: 56 }],
      [T_POP, { elR: 78, shR: [70, -16], face: 'happy' }, 'out'],
      [0.95, { face: 'warm', spine: 6, elR: 50 }],
    ], () => <ButterKnife />),
    alfTable([
      [T_POP + 0.1, { face: 'shock', spine: 2 }],
      [S(15) - (E(14) + 0.5) + 0.35, { shR: [78, 4], elR: 8, handR: 'point', face: 'disbelief', spine: 10 }],
    ]),
  ],
};
const kitchenJar: Shot = {
  id: 'kitchen-jar', t0: S(15) + 1.05, t1: S(16) - 0.05,
  cam: [[0, cam([JAR[0] + 0.06, 1.16, JAR[2] + 0.88], [JAR[0], 0.96, JAR[2]], 36)], [S(16) - 0.05 - (S(15) + 1.05), cam([JAR[0] + 0.06, 1.14, JAR[2] + 0.76], [JAR[0], 0.96, JAR[2]], 36), 'lin']],
  sw: 1, onScreen: ['alfie'],
  set: () => <NanKitchen><TableTop open={1} /></NanKitchen>,
  cast: [],
};
const kitchenNan: Shot = {
  id: 'kitchen-nan', t0: S(16) - 0.05, t1: S(16) + 1.55,
  cam: [[0, cam([NH_T[0] + 0.3, 1.42, NH_T[2] + 1.3], [NH_T[0] - 0.06, 1.1, NH_T[2]], 40)], [1.6, cam([NH_T[0] + 0.27, 1.4, NH_T[2] + 1.15], [NH_T[0] - 0.06, 1.1, NH_T[2]], 40), 'lin']],
  sw: 1,
  set: () => <NanKitchen><TableTop open={1} /></NanKitchen>,
  cast: [nanAt([
    [0, { ...NAN_TABLE, spine: 10, face: 'warm', shL: [70, -6], elL: 30, handL: 'open', shR: [20, 10], elR: 30, headNod: 0, headTurn: 6 }],
    ...[0.35, 0.7, 1.05, 1.4].map((t, i): Key3 => [t, { elL: i % 2 ? 30 : 46 }]),
  ])],
};
const kitchenTwo: Shot = {
  id: 'kitchen-two', t0: S(16) + 1.55, t1: E(16) + 0.45,
  cam: [[0, cam([-0.32, 1.66, -1.6], [0.52, 1.42, -0.33], 42)], [E(16) + 0.45 - (S(16) + 1.55), cam([-0.27, 1.65, -1.52], [0.52, 1.43, -0.33], 42), 'lin']],
  sw: 1,
  set: (c) => <NanKitchen><TableTop open={1} tenner={c.ts < 1.2} /></NanKitchen>,
  cast: [
    nanAt([
      [0, { ...NAN_TABLE, spine: 10, face: 'warm', shL: [60, -6], elL: 40, handL: 'open', headTurn: 14 }],
      [1.0, { shR: [62, -24], elR: 20, handR: 'fist', spine: 16 }],
      [1.25, { shR: [40, -10], elR: 60 }],
    ], (ts) => (ts > 1.2 ? <group position={[0.01, -0.09, 0.04]} rotation={[PI / 2, 0, 0.3]}><Tenner /></group> : null)),
    alfTable([[0, { face: 'happy', headNod: 6 }], [0.6, { headNod: 14 }], [0.9, { headNod: 4 }], [1.3, { face: 'disbelief' }]]),
  ],
};

// ===================================== 0:47 the twist: Nan's magnifying glass at the window =====================================
const WIN_NAN = { x: 0.74, y: 0, z: -1.46 };
const ALF_WIN = { x: 0.0, y: 0, z: -1.05, ry: 2.07 };
const NAN_TO_ALF = -1.065; // Nan's facing when she turns from the window to Alfie
const NH_W = nanHead({ ...WIN_NAN, ry: NAN_TO_ALF });       // her head once she has turned
const AH_W: [number, number, number] = [ALF_WIN.x, 1.59, ALF_WIN.z]; // Alfie's head
const FWD_A: [number, number] = [Math.sin(ALF_WIN.ry), Math.cos(ALF_WIN.ry)];
const FWD_N: [number, number] = [Math.sin(NAN_TO_ALF), Math.cos(NAN_TO_ALF)];
const RIGHT_N: [number, number] = [Math.cos(NAN_TO_ALF), -Math.sin(NAN_TO_ALF)];
const T_FLICK = S(17) - 0.55; // the grade flickers to the real Britain, the note shows full size
const realAt = (t: number) => (t >= T_FLICK && t < T_FLICK + 0.1) || (t >= T_FLICK + 0.17 && t < T_FLICK + 0.32);
const NOTE_WIN: [number, number, number] = [0.66, 1.53, -2.04];
const glass: Shot = {
  id: 'glass', t0: E(16) + 0.45, t1: S(17) + 1.0,
  cam: [[0, cam([1.08, 1.66, -1.3], [0.67, 1.5, -2.03], 34)], [S(17) + 1.0 - (E(16) + 0.45), cam([1.02, 1.65, -1.4], [0.67, 1.5, -2.03], 34), 'lin']],
  sw: (ts) => (realAt(ts + E(16) + 0.45) ? 0 : 1),
  set: (c) => {
    const real = realAt(c.t);
    return (
      <NanKitchen sw={c.sw}>
        <TableTop open={1} tenner={false} />
        <Up p={NOTE_WIN} r={[-0.1, 0.25, 0.04]}><Tenner s={real ? 1.0 : 0.22} /></Up>
        <group position={[0.7, 1.43, -1.94]} rotation={[-0.2, 0.25, 0]}><Magnifier /></group>
        {real ? <pointLight position={[0.9, 1.7, -1.6]} intensity={1.5} distance={2} color="#FFF4DA" /> : null}
      </NanKitchen>
    );
  },
  cast: [nanAt([[0, { ...WIN_NAN, ry: PI, spine: 2, face: 'thinking', shR: [155, -18], elR: 22, handR: 'fist', shL: [140, -16], elL: 40, handL: 'fist', headNod: -6 }], [1.2, { headNod: -2 }]])],
};
const nanReal: Shot = {
  id: 'nan-real', t0: S(17) + 1.0, t1: E(17) + 0.12,
  cam: [[0, cam([NH_W[0] + 1.05 * FWD_N[0] + 0.55 * RIGHT_N[0], 1.4, NH_W[2] + 1.05 * FWD_N[1] + 0.55 * RIGHT_N[1]], [NH_W[0], 1.2, NH_W[2]], 38)],
        [E(17) + 0.12 - (S(17) + 1.0), cam([NH_W[0] + 0.95 * FWD_N[0] + 0.5 * RIGHT_N[0], 1.39, NH_W[2] + 0.95 * FWD_N[1] + 0.5 * RIGHT_N[1]], [NH_W[0], 1.2, NH_W[2]], 38), 'lin']],
  sw: 1,
  set: () => <NanKitchen><TableTop open={1} tenner={false} /></NanKitchen>,
  cast: [nanAt([
    [0, { ...WIN_NAN, ry: PI - 0.5, spine: 2, face: 'thinking', shR: [110, 12], elR: 40, handR: 'fist', shL: [70, 5], elL: 60, handL: 'fist' }],
    [0.42, { ry: NAN_TO_ALF + 2 * PI, face: 'warm', shR: [45, 10], elR: 70 }, 'io'],
    [1.37, { face: 'sad' }],
  ], () => <group position={[0.01, -0.09, 0.04]} rotation={[PI / 2, 0, 0.3]}><Tenner /></group>, () => <group position={[0, -0.15, 0.02]} rotation={[0, 0, PI]}><Magnifier /></group>)],
};
const NAN_FACING = { ...WIN_NAN, ry: NAN_TO_ALF, spine: 2 };
const alfWin = (keys: Key3[], held?: Actor['heldR']): Actor => ({ who: 'lead', seed: 0.3, pin: () => 0.55, keys: [[0, { ...ALF_WIN, shL: [10, 8], elL: 20, shR: [10, 8], elR: 20 }], ...keys], heldR: held });
const alfieMuch: Shot = {
  id: 'alfie-much', t0: E(17) + 0.12, t1: E(18) + 0.1,
  cam: [[0, cam([AH_W[0] + 1.05 * FWD_A[0], 1.6, AH_W[2] + 1.05 * FWD_A[1]], [AH_W[0], 1.52, AH_W[2]], 36)], [E(18) + 0.1 - (E(17) + 0.12), cam([AH_W[0] + 0.95 * FWD_A[0], 1.6, AH_W[2] + 0.95 * FWD_A[1]], [AH_W[0], 1.52, AH_W[2]], 36), 'lin']],
  sw: 1,
  set: () => <NanKitchen><TableTop open={1} tenner={false} /></NanKitchen>,
  cast: [alfWin([[0.05, { face: 'worried', shrug: 0.4, headTilt: -6 }], [0.6, { headNod: 4 }]])],
};
// "More than a quarter": Nan snaps more than a quarter off a digestive and pops it in her mouth
const T_SNAP = S(19) + 0.42;
const nanCam = (d: number, side: number, y = 1.34): [number, number, number] => [NH_W[0] + d * FWD_N[0] + side * RIGHT_N[0], y, NH_W[2] + d * FWD_N[1] + side * RIGHT_N[1]];
const nanQuarter: Shot = {
  id: 'nan-quarter', t0: E(18) + 0.1, t1: E(19) + 0.12,
  cam: [[0, cam(nanCam(1.3, 0.3, 1.36), [NH_W[0], 1.08, NH_W[2]], 40)], [E(19) + 0.12 - (E(18) + 0.1), cam(nanCam(1.18, 0.27, 1.35), [NH_W[0], 1.08, NH_W[2]], 40), 'lin']],
  sw: 1,
  overlay: (c) => <FactCard t={c.t} at={T_SNAP + 0.05} until={E(19) + 0.12} source="ONS price data, 2016 to 2026">£1,000 kept since 2016 now buys what about £720 did</FactCard>,
  set: () => <NanKitchen><TableTop open={1} tenner={false} /></NanKitchen>,
  cast: [nanAt([
    [0, { ...NAN_FACING, face: 'warm', shR: [98, 8], elR: 84, handR: 'fist', shL: [98, -8], elL: 84, handL: 'fist', twL: 10, twR: 10 }],
    [T_SNAP - (E(18) + 0.1), { shR: [100, 16], shL: [100, -16], elR: 86, elL: 86, face: 'neutral' }],
    [T_SNAP - (E(18) + 0.1) + 0.12, { shR: [98, 28], shL: [98, -30], elR: 80, elL: 80 }, 'out'],
    [T_SNAP - (E(18) + 0.1) + 0.75, { shL: [118, -18], elL: 118, face: 'happy' }],
    [T_SNAP - (E(18) + 0.1) + 0.95, { face: 'holding' }],
    [T_SNAP - (E(18) + 0.1) + 1.25, { shL: [40, -10], elL: 70, face: 'warm' }],
  ],
  (ts) => <group position={[0.012, -0.085, 0.03]}><Biscuit snap={ts >= T_SNAP - (E(18) + 0.1) ? 1 : 0} to={[0, 0, 0]} gone /></group>,
  (ts) => (ts >= T_SNAP - (E(18) + 0.1) && ts < T_SNAP - (E(18) + 0.1) + 0.92
    ? <group position={[-0.012, -0.085, 0.03]}><group rotation={[PI / 2, 0, 0]}><mesh rotation={[0, 0.3 * PI, 0]}><cylinderGeometry args={[0.036, 0.036, 0.008, 12, 1, false, PI * 2 * 0.7, PI * 2 * 0.3]} /><meshStandardMaterial color="#C99A5B" roughness={0.95} /></mesh></group></group>
    : null))],
};
const T_BLINK = S(20) + 0.9;
const RIGHT_A: [number, number] = [Math.cos(ALF_WIN.ry), -Math.sin(ALF_WIN.ry)];
const EYE_GLASS: [number, number, number] = [AH_W[0] + 0.035 * RIGHT_A[0] + 0.19 * FWD_A[0], 1.615, AH_W[2] + 0.035 * RIGHT_A[1] + 0.19 * FWD_A[1]];
const alfieSee: Shot = {
  id: 'alfie-see', t0: E(19) + 0.12, t1: E(20) + 0.1,
  cam: [[0, cam([AH_W[0] + 0.95 * FWD_A[0], 1.62, AH_W[2] + 0.95 * FWD_A[1]], [AH_W[0], 1.56, AH_W[2]], 34)], [E(20) + 0.1 - (E(19) + 0.12), cam([AH_W[0] + 0.86 * FWD_A[0], 1.62, AH_W[2] + 0.86 * FWD_A[1]], [AH_W[0], 1.56, AH_W[2]], 34), 'lin']],
  sw: 1,
  set: (c) => {
    const up = prog(c.ts, 0.12, 0.36, 'out');
    const blink = c.t > T_BLINK && c.t < T_BLINK + 0.12 ? 1 : 0;
    return (
      <NanKitchen>
        <TableTop open={1} tenner={false} />
        {up > 0 ? <group position={[EYE_GLASS[0], lerp(1.25, EYE_GLASS[1], up), EYE_GLASS[2]]} rotation={[0, ALF_WIN.ry, 0]}><BigEyeGlass blink={blink} /></group> : null}
      </NanKitchen>
    );
  },
  cast: [alfWin([
    [0, { face: 'worried', shR: [30, 10], elR: 60, handR: 'fist' }],
    [0.3, { shR: [72, -8], elR: 112, twR: -10, face: 'disbelief', headNod: 2 }, 'out'],
    [1.7, { shR: [74, -8] }],
  ])],
};
const nanPrint: Shot = {
  id: 'nan-print', t0: E(20) + 0.1, t1: E(21) + 0.1,
  cam: [[0, cam([1.3, 1.5, 0.45], [0.37, 1.38, -1.2], 40)], [E(21) + 0.1 - (E(20) + 0.1), cam([1.2, 1.48, 0.25], [0.37, 1.38, -1.2], 40), 'lin']],
  sw: 1,
  set: () => <NanKitchen><TableTop open={1} tenner={false} /></NanKitchen>,
  cast: [
    nanAt([[0, { ...NAN_FACING, face: 'warm', shR: [30, 10], elR: 60, shL: [25, 5], elL: 50 }], [0.5, { shR: [104, 10], elR: 40, handR: 'open' }], [1.0, { shR: [100, 10], elR: 46 }], [1.6, { shR: [40, 10], elR: 50 }]]),
    alfWin([[0, { face: 'sad', shR: [70, -10], elR: 90, handR: 'fist' }], [0.6, { shR: [20, 8], elR: 30, face: 'worried' }]], () => <group position={[0, -0.15, 0.02]} rotation={[0, 0, PI]}><Magnifier /></group>),
  ],
};

// ===================================== 0:58 the cliffhanger: the pin flickers, the Booth panics, Nan knows that pin =====================================
const strobe = (t: number) => (Math.floor(t * 30 / 2) % 2 ? 1 : 0.15);
// the pin sits at body (-0.1, 1.271, 0.128) on Alfie (Person: chest, left of the zip), turned by his facing
const PIN_W: [number, number, number] = [
  ALF_WIN.x - 0.1 * Math.cos(ALF_WIN.ry) + 0.128 * Math.sin(ALF_WIN.ry), 1.271, ALF_WIN.z + 0.1 * Math.sin(ALF_WIN.ry) + 0.128 * Math.cos(ALF_WIN.ry),
];
const pinFlicker: Shot = {
  id: 'pin-flicker', t0: E(21) + 0.1, t1: S(22) - 0.02,
  cam: [[0, cam([PIN_W[0] + 0.3 * FWD_A[0], PIN_W[1] + 0.02, PIN_W[2] + 0.3 * FWD_A[1]], PIN_W, 32)], [S(22) - 0.02 - (E(21) + 0.1), cam([PIN_W[0] + 0.24 * FWD_A[0], PIN_W[1] + 0.015, PIN_W[2] + 0.24 * FWD_A[1]], PIN_W, 32), 'lin']],
  shake: [[0.05, 0.6], [0.3, 0.5]],
  sw: (ts) => (strobe(ts) > 0.5 ? 1 : 0.35),
  set: (c) => <NanKitchen sw={c.sw}><TableTop open={1} tenner={false} /></NanKitchen>,
  cast: [{ who: 'lead', seed: 0.3, noBreath: true, pin: (ts) => strobe(ts), keys: [[0, { ...ALF_WIN, face: 'shock', shL: [10, 8], elL: 20, shR: [10, 8], elR: 20 }]] }],
};
const boothShout: Shot = {
  id: 'booth-shout', t0: S(22) - 0.02, t1: S(22) + 0.83,
  cam: [[0, cam([0.26, 1.6, 1.32], [0.67, 1.5, -0.03], 36)], [0.85, cam([0.31, 1.59, 1.16], [0.67, 1.5, -0.03], 36), 'lin']],
  shake: [[0.05, 0.2]],
  set: () => <Booth tip={1} spill={1} />,
  cast: [
    { who: 'producer', seed: 1.7, heldL: () => <Clipboard />, keys: [[0, { x: 0.85, y: 0, z: -0.15, ry: -0.75, shL: [16, -8], elL: 75, twL: 30, handL: 'fist', spine: 18, face: 'scream', shR: [108, 20], elR: 6, handR: 'point', headTurn: -10 }], [0.4, { spine: 22, shR: [116, 20] }], [0.85, { spine: 20 }]] },
  ],
};
const pinLight = (t: number) => <pointLight position={[PIN_W[0] + 0.15 * FWD_A[0], PIN_W[1] + 0.05, PIN_W[2] + 0.15 * FWD_A[1]]} intensity={1.1 * strobe(t)} distance={1.6} color="#FFD873" />;
// over Alfie's right shoulder, from above: Nan is tiny
const STARE_CAM: [number, number, number] = [AH_W[0] - 0.55 * FWD_A[0] + 0.5 * RIGHT_A[0], 1.86, AH_W[2] - 0.55 * FWD_A[1] + 0.5 * RIGHT_A[1]];
const nanStare: Shot = {
  id: 'nan-stare', t0: S(22) + 0.83, t1: S(23) + 0.75,
  cam: [[0, cam(STARE_CAM, [NH_W[0], 1.22, NH_W[2]], 38)], [S(23) + 0.75 - (S(22) + 0.83), cam([STARE_CAM[0] + 0.12 * FWD_A[0], 1.82, STARE_CAM[2] + 0.12 * FWD_A[1]], [NH_W[0], 1.23, NH_W[2]], 38), 'lin']],
  sw: 1,
  set: (c) => <NanKitchen><TableTop open={1} tenner={false} />{pinLight(c.t)}</NanKitchen>,
  cast: [
    { who: 'lead', seed: 0.3, pin: (ts) => strobe(ts), keys: [[0, { ...ALF_WIN, face: 'shock', shL: [10, 8], elL: 20, shR: [10, 8], elR: 20, headNod: 14 }]] },
    nanAt([[0, { ...NAN_FACING, face: 'warm', shR: [30, 10], elR: 60, shL: [25, 5], elL: 50, headNod: 0 }], [0.25, { face: 'shock', headNod: 6, spine: -4 }, 'out'], [1.5, { headNod: 8 }]]),
  ],
};
const nanCU: Shot = {
  id: 'nan-cu', t0: S(23) + 0.75, t1: E(23),
  cam: [[0, cam(nanCam(1.0, 0.12, 1.34), [NH_W[0], 1.2, NH_W[2]], 34)], [E(23) - (S(23) + 0.75), cam(nanCam(0.82, 0.1, 1.33), [NH_W[0], 1.21, NH_W[2]], 34), 'lin']],
  sw: 1,
  set: (c) => <NanKitchen><TableTop open={1} tenner={false} />{pinLight(c.t)}</NanKitchen>,
  cast: [nanAt([[0, { ...NAN_FACING, face: 'shock', shR: [30, 10], elR: 60, shL: [25, 5], elL: 50, headNod: 6, spine: -4 }], [0.7, { face: 'worried', headNod: 4 }], [1.6, { face: 'shock', headNod: 2 }]])],
};

export const ACT2: Shot[] = [
  blow, jump, hero, shrink,
  shopIn, shopKeeper, shopAlfie, shopReceipt,
  bfRun, bfWedge, bfAssistant, bfTag, bfMate,
  kitchenTins, kitchenJar, kitchenNan, kitchenTwo,
  glass, nanReal, alfieMuch, nanQuarter, alfieSee, nanPrint,
  pinFlicker, boothShout, nanStare, nanCU,
];
export const TITLE = { at: S(8) + 0.36, until: S(8) + 2.1 };
export const BLACK_AT = E(23);
export const TOTAL = E(23) + 0.4;
