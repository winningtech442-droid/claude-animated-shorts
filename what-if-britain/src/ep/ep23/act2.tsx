// EP23 Pay Later, act 2: the title, the ladder (the till, Mate's front hall, the car boot sale), the twist in the back
// office and the cliffhanger. Timings follow src/episodes/ep23/lines.json via S(n) / E(n).
import React from 'react';
import { cam, Shot, Actor, Key3, Pose3, prog, lerp, clamp } from '../kit3';
import { CAST } from '../../cast/cast';
import { Trolley } from '../../props';
import { Cane } from '../ep21/sets2';
import { Rain } from '../ep22/sets';
import { SaleFloor, JacketPiece, Telly, Sofa, Fridge, Gnome, JetSki, BoxPile, TILL, SHOPPERS, REP, OWNER } from './sets';
import { FrontHall, HALL2, PayLetter, LetterHeap, SnowShovel, LateFeeSticker, KickScooter, RepReader, FeeReceipt, CarBoot, FoldTable, BackOffice } from './sets2';
import { S, E, wordAt, walk, xAt, pinLive, GRIP } from './shared';

const PI = Math.PI;
export const TITLE = { at: wordAt("Britain's", 8), until: wordAt("Britain's", 8) + 1.9 };
const RAIN = (c: { t: number }) => <Rain t={c.t} />;
const label = (txt: string) => (c: { ts: number }) => {
  const k = prog(c.ts, 0.05, 0.25, 'back');
  return <div style={{ position: 'absolute', top: 330, width: '100%', textAlign: 'center', transform: `scale(${0.6 + 0.4 * k})`, opacity: clamp(k * 2),
    fontFamily: 'Inter', fontWeight: 900, fontSize: 110, color: '#FFD43B', textShadow: '-4px 0 0 #000, 4px 0 0 #000, 0 -4px 0 #000, 0 4px 0 #000, 0 8px 14px rgba(0,0,0,.55)' }}>{txt}</div>;
};
const sleeveHat = (x: number, z: number, ry: number, y = 1.88) => <group position={[x, y, z]} rotation={[0.5, ry, 1.45]}><JacketPiece kind="sleeve" s={0.8} /></group>;
const rep = (keys: Key3[], held?: (ts: number) => React.ReactNode): Actor => ({ who: 'rep', look: REP, seed: 7.3, keys, heldR: held });
const owner = (keys: Key3[], held?: (ts: number) => React.ReactNode): Actor => ({ who: 'owner', look: OWNER, seed: 8.1, keys, heldR: held, heldL: held ? () => null : undefined });
const nan = (keys: Key3[]): Actor => ({ who: 'nan', seed: 3.3, keys, heldR: () => <Cane /> });

// ================= 0:23 WHAT IF BRITAIN: the what-if store, wide and high, everyone walking out with everything ======
const T1_T0 = S(8) - 0.05, T1_T1 = TITLE.at + 0.9, T2_T1 = S(9) - 0.25;
const carryUp: Pose3 = { shL: [165, 12], elL: 15, shR: [165, 12], elR: 15, handL: 'open', handR: 'open', face: 'happy' };
const tv1 = walk(0, 3.2, 3.0, -2.6, 0.34, { z: 1.8, ry: -PI / 2, ...carryUp }, 'none');
const sofaL = walk(0, 3.2, -3.4, 0.6, 0.36, { z: -1.75, ry: PI / 2, shL: [55, -12], elL: 15, shR: [55, -12], elR: 15, handL: 'fist', handR: 'fist', face: 'happy' }, 'none');
const sofaR = sofaL.map(([t, p, e]) => [t, { ...p, x: (p.x ?? 0) + 1.75, ry: -PI / 2 }, e] as Key3);
const fridgeGuy = walk(0, 3.2, -0.6, 3.6, 0.32, { z: 2.6, ry: PI / 2, ...GRIP, spine: 10, face: 'happy' }, 'none');
const alfStore: Actor = { who: 'lead', seed: 0.3, pin: pinLive, keys: [[0, { x: -0.25, z: 0.6, ry: 0.4, face: 'disbelief', shL: [10, 12], elL: 20, shR: [10, 12], elR: 20, headTurn: 30 }], [1.6, { headTurn: -30 }], [3.0, { headTurn: 10, face: 'worried' }]] };
const mateStore: Actor = { who: 'mate', seed: 2.2, keys: [[0, { x: 0.45, z: 0.75, ry: -0.3, face: 'happy', shL: [10, 8], elL: 20, shR: [10, 8], elR: 20, headTurn: -25 }], [1.4, { headTurn: 25, face: 'laugh' }]] };
const crowd = (ts: number): Actor[] => [
  { who: 's0', look: SHOPPERS[0], seed: 4.1, mute: true, keys: tv1 },
  { who: 's1', look: SHOPPERS[1], seed: 4.7, mute: true, keys: sofaL },
  { who: 's2', look: SHOPPERS[2], seed: 5.3, mute: true, keys: sofaR },
  { who: 's3', look: { ...SHOPPERS[0], jacket: '#2E6B4F', hair: '#B8B2A8', hairStyle: 'grey' as const, height: 1.68 }, seed: 6.1, mute: true, keys: fridgeGuy },
].map((a) => ({ ...a, keys: a.keys.map(([t, p, e]) => [t + 0 * ts, p, e] as Key3) }));
const crowdProps = (ts: number) => (
  <>
    <group position={[xAt(tv1, ts), SHOPPERS[0].height + 0.32, 1.8]}><Telly /></group>
    <group position={[xAt(sofaL, ts) + 0.88, 0.32, -1.75]}><Sofa /></group>
    <group position={[xAt(fridgeGuy, ts) + 0.45, 0.25, 2.6]} rotation={[0, 0, -PI / 2 + 0.15]}><Fridge s={0.55} /></group>
  </>
);
const titleWide: Shot = {
  id: 'title-wide', t0: T1_T0, t1: T1_T1, sw: 1,
  cam: [[0, cam([0.2, 2.9, 5.6], [0.2, 0.9, 0.2], 50)], [T1_T1 - T1_T0, cam([0.25, 3.3, 5.0], [0.2, 0.8, 0.0], 50), 'io']],
  set: (c) => <SaleFloor sw={1} later>{sleeveHat(-0.25, 0.6, 0.4)}{crowdProps(c.ts)}</SaleFloor>,
  cast: [alfStore, mateStore, ...crowd(0)],
};
const titlePush: Shot = {
  id: 'title-push', t0: T1_T1, t1: T2_T1, sw: 1,
  cam: [[0, cam([-0.6, 1.6, 3.4], [0.6, 1.1, -0.3], 44)], [T2_T1 - T1_T1, cam([-0.3, 1.5, 2.4], [0.7, 1.1, -0.35], 44), 'io']],
  set: (c) => <SaleFloor sw={1} later press={0.5 + 0.5 * Math.sin(c.ts * 5)}>{crowdProps(c.ts + (T1_T1 - T1_T0))}</SaleFloor>,
  cast: crowd(0).map((a) => ({ ...a, keys: a.keys.map(([t, p, e]) => [t - (T1_T1 - T1_T0), p, e] as Key3) })),
};

// ================= beat 1, the till: Mate's car-sized trolley, PAY LATER for everything, then it rolls over Alfie's foot ==
const B1_T0 = T2_T1, B1_T1 = E(9) + 0.15, B2_T1 = E(10) + 0.5;
const BIG = 1.45; // the giant trolley's scale
const bigTrolley = (x: number, z: number) => (
  <group position={[x, 0, z]}>
    <Trolley s={BIG} />
    <group position={[0.1, 0.8 * BIG, 0]}><BoxPile n={4} seed={2} /></group>
    <group position={[0.15, 1.12 * BIG, 0]} rotation={[0, 0.3, 0]}><JetSki s={0.55} /></group>
    <group position={[-0.35, 0.82 * BIG, 0.1]}><Telly s={0.55} /></group>
    <group position={[0.42, 0.82 * BIG, -0.15]}><Gnome s={1.2} /></group>
  </group>
);
const TRX0 = -2.6, TRX1 = -0.55; // trolley centre: rolls in, stops at the till end
const trolleyX = (ts: number) => lerp(TRX0, TRX1, prog(ts, 0, 0.9, 'out'));
const mateShove: Actor = {
  who: 'mate', seed: 2.2,
  keys: [
    ...walk(0, 0.9, TRX0 - 0.6 * BIG - 0.45, TRX1 - 0.6 * BIG - 0.45, 0.3, { z: 0.6, ry: PI / 2, spine: 22, face: 'happy', shL: [75, -6], elL: 20, shR: [75, -6], elR: 20, handL: 'fist', handR: 'fist' }, 'none'),
    [1.15, { x: TRX1 - 0.6 * BIG - 0.2, spine: 4, face: 'laugh', shL: [150, 30], elL: 30, shR: [10, 10], elR: 20, hipL: [0, 3], knL: 0, hipR: [0, 3], knR: 0 }],
    [1.35, { shL: [100, 20], elL: 10 }],
    [B1_T1 - B1_T0, { face: 'laugh', shL: [140, 30], elL: 20 }],
  ],
};
const alfTill: Actor = { who: 'lead', seed: 0.3, pin: pinLive, keys: [[0, { x: TILL.x - 0.6, z: 0.3, ry: -0.6, face: 'worried', shL: [10, 10], elL: 20, shR: [10, 10], elR: 20 }], [1.3, { face: 'disbelief', headTurn: -10 }]] };
const trolleyIn: Shot = {
  id: 'trolley-in', t0: B1_T0, t1: B1_T1, sw: 1,
  cam: [[0, cam([-1.5, 1.55, 4.9], [-1.3, 1.2, 0.6], 52)], [B1_T1 - B1_T0, cam([-1.3, 1.55, 4.6], [-1.1, 1.2, 0.6], 52), 'lin']],
  shake: [[0.9, 0.5]],
  set: (c) => <SaleFloor sw={1} later press={prog(c.ts, 1.1, 1.25) * (1 - prog(c.ts, 1.4, 1.6))}>{bigTrolley(trolleyX(c.ts), 0.6)}{sleeveHat(TILL.x - 0.6, 0.3, -0.6)}</SaleFloor>,
  cast: [mateShove, alfTill],
};
const FOOT = 0.55; // the wheel lands on his foot
const alfFoot: Actor = {
  who: 'lead', seed: 0.3, pin: pinLive,
  keys: [
    [0, { x: 0.15, z: 0.95, ry: 0.5, face: 'worried', shL: [10, 10], elL: 20, shR: [10, 10], elR: 20 }],
    [FOOT, { face: 'scream', spine: 14, hipR: [55, 10], knR: 85, shL: [70, 40], elL: 20, shR: [70, 40], elR: 20, handL: 'open', handR: 'open', y: 0.1 }, 'out'],
    [FOOT + 0.3, { y: 0.0, face: 'angry', spine: 8 }],
    [FOOT + 0.6, { y: 0.08 }], [FOOT + 0.9, { y: 0, face: 'angry', shR: [60, 10], elR: 70, handR: 'point', hipR: [30, 8], knR: 60 }],
    [B2_T1 - B1_T1, { face: 'angry' }],
  ],
};
const foot: Shot = {
  id: 'foot', t0: B1_T1, t1: B2_T1, sw: 1,
  cam: [[0, cam([1.6, 1.25, 2.9], [0.15, 0.95, 0.95], 44)], [B2_T1 - B1_T1, cam([1.45, 1.4, 2.6], [0.1, 1.2, 0.95], 44), 'lin']],
  shake: [[FOOT, 0.9]],
  set: (c) => <SaleFloor sw={1} later>{bigTrolley(lerp(-0.85, -0.5, prog(c.ts, 0, FOOT, 'out')), 0.95)}{sleeveHat(0.15, 0.95, 0.5, 1.88 + (c.ts > FOOT && c.ts < FOOT + 0.3 ? 0.1 : 0))}</SaleFloor>,
  cast: [alfFoot],
};

// ================= beat 2, Mate's front hall, "later": the letterbox fires instalment letters; they shovel; the Rep ======
const H1_T0 = B2_T1, H1_T1 = S(11) + 0.25, H2_T1 = E(11) + 0.15, H3_T1 = E(12) + 0.2, H4_T1 = E(13) + 0.1, H5_T1 = S(15) - 0.2;
const heapH = (t: number) => lerp(0.25, 0.85, prog(t, H1_T0, H3_T1, 'out'));
/** Envelopes shot out of the letterbox along arcs that land on the heap; one every 0.06 s. */
const LetterStream: React.FC<{ t: number; t0: number }> = ({ t, t0 }) => (
  <group>
    {Array.from({ length: 14 }).map((_, i) => {
      const u = ((t - t0) / 0.85 + i / 14) % 1;
      const x = ((i * 37) % 9 - 4) * 0.07 * u, z = lerp(HALL2.doorZ + 0.05, HALL2.doorZ + 1.7, u), y = HALL2.slotY + 0.6 * Math.sin(PI * u) - (HALL2.slotY - heapH(t)) * u;
      return <group key={i} position={[x, Math.max(heapH(t) * 0.8, y), z]} rotation={[u * 6 + i, i, u * 4]}><PayLetter /></group>;
    })}
  </group>
);
const heap = (t: number) => <group position={[0, 0, -0.9]}><LetterHeap n={60} r={0.95} h={heapH(t)} /></group>;
const letterbox: Shot = {
  id: 'letterbox', t0: H1_T0, t1: H1_T1, sw: 1,
  cam: [[0, cam([0.1, 1.05, 0.6], [0, HALL2.slotY, HALL2.doorZ], 40)], [H1_T1 - H1_T0, cam([0.05, 1.0, 0.1], [0, HALL2.slotY, HALL2.doorZ], 40), 'lin']],
  set: (c) => <FrontHall>{heap(c.t)}<LetterStream t={c.t} t0={H1_T0} /></FrontHall>,
  cast: [],
  overlay: label('LATER...'),
};
const SHOVEL_ARMS = (k: number): Pose3 => ({ shL: [60 + 30 * k, -10], elL: 40, shR: [40 + 30 * k, -14], elR: 60, handL: 'fist', handR: 'fist', spine: 25 - 20 * k });
const alfShovel: Actor = {
  who: 'lead', seed: 0.3, pin: pinLive, heldR: () => <group rotation={[0.4, 0, 0]}><SnowShovel /></group>,
  keys: [[0, { x: -0.35, z: -0.55, ry: 0.35, face: 'worried', ...SHOVEL_ARMS(0) }], [0.4, { ...SHOVEL_ARMS(1), face: 'angry' }], [0.8, { ...SHOVEL_ARMS(0), face: 'worried' }], [1.2, { ...SHOVEL_ARMS(1) }], [1.6, { ...SHOVEL_ARMS(0), face: 'disbelief', headTurn: 25 }]],
};
const shovel: Shot = {
  id: 'shovel', t0: H1_T1, t1: H2_T1, sw: 1,
  cam: [[0, cam([0.35, 1.55, 1.6], [-0.3, 1.2, -0.55], 40)], [H2_T1 - H1_T1, cam([0.3, 1.55, 1.3], [-0.3, 1.25, -0.55], 40), 'lin']],
  set: (c) => <FrontHall>{heap(c.t)}<LetterStream t={c.t} t0={H1_T0} /></FrontHall>,
  cast: [alfShovel],
};
const fingers = (n: number): Pose3 => ({ shL: [70, -20], elL: 80, twL: 40, handL: n % 2 ? 'point' : 'open', shR: [55, -10], elR: 85, handR: 'point', headNod: 10 + 4 * (n % 2) });
const mateCount: Actor = {
  who: 'mate', seed: 2.2,
  keys: [[0, { x: 0.25, z: -0.5, ry: -0.45, face: 'thinking', ...fingers(0) }], [0.5, fingers(1)], [0.9, fingers(2)], [1.3, { ...fingers(3), face: 'disbelief' }], [1.8, { face: 'shock', headNod: -4, shL: [30, 20], elL: 30, shR: [30, 20], elR: 30, handL: 'open', handR: 'open' }]],
};
const count: Shot = {
  id: 'count', t0: H2_T1, t1: H3_T1, sw: 1,
  cam: [[0, cam([-0.45, 1.62, 1.35], [0.25, 1.5, -0.5], 38)], [H3_T1 - H2_T1, cam([-0.4, 1.63, 1.05], [0.25, 1.52, -0.5], 38), 'lin']],
  set: (c) => <FrontHall>{heap(c.t)}</FrontHall>,
  cast: [mateCount],
};
const REPRIDE: Pose3 = { shR: [70, -10], elR: 20, handR: 'fist', shL: [70, 10], elL: 20, handL: 'fist', spine: 10, hipL: [10, 4], knL: 10, hipR: [-25, 6], knR: 8, face: 'happy' };
const scooterAt = (x: number, z: number, ry: number) => <group position={[x, 0, z]} rotation={[0, ry - PI / 2, 0]}><KickScooter /></group>;
const repInZ = (ts: number) => lerp(HALL2.doorZ + 0.1, -0.15, prog(ts, 0.25, 0.9, 'out'));
const repIn: Shot = {
  id: 'rep-in', t0: H3_T1, t1: H4_T1, sw: 1,
  cam: [[0, cam([-0.1, 1.0, 1.9], [0.05, 1.0, -1.4], 46)], [H4_T1 - H3_T1, cam([-0.08, 0.98, 1.6], [0.05, 0.95, -0.8], 46), 'lin']],
  set: (c) => <FrontHall open={prog(c.ts, 0, 0.3, 'out')}>{heap(c.t)}{scooterAt(0.05, repInZ(c.ts) + 0.05, 0)}</FrontHall>,
  cast: [
    rep([[0, { x: 0.05, z: HALL2.doorZ + 0.1, y: 0.12, ry: 0, ...REPRIDE }], [0.25, { z: HALL2.doorZ + 0.1 }], [0.9, { z: -0.15 }, 'out'], [1.1, { face: 'smug', shL: [120, 20], elL: 40, handL: 'point', headTilt: -8 }]]),
    { who: 'lead', seed: 0.3, pin: pinLive, keys: [[0, { x: -0.6, z: 0.1, ry: 0.5, face: 'shock', ...SHOVEL_ARMS(0) }]], heldR: () => <group rotation={[0.4, 0, 0]}><SnowShovel /></group> },
    { who: 'mate', seed: 2.2, keys: [[0, { x: 0.85, z: 0.2, ry: -0.5, face: 'shock', shL: [30, 20], elL: 30, shR: [30, 20], elR: 30 }]] },
  ],
};
const STICK = 0.55;
const MATE_FACE: [number, number, number] = [0.28, 1.73, -0.2]; // Mate faces -x: his forehead, just in front of it
const sticker: Shot = {
  id: 'sticker', t0: H4_T1, t1: H5_T1, sw: 1,
  cam: [[0, cam([-0.55, 1.68, 0.75], [0.35, 1.58, -0.25], 40)], [H5_T1 - H4_T1, cam([-0.35, 1.7, 0.45], [0.33, 1.65, -0.22], 36), 'io']],
  shake: [[STICK, 0.35]],
  set: (c) => <FrontHall>{heap(c.t)}{c.ts >= STICK ? <group position={MATE_FACE} rotation={[0, -PI / 2, (c.ts - STICK) * 0 + 0.12]}><LateFeeSticker /></group> : null}</FrontHall>,
  cast: [
    rep([[0, { x: -0.25, z: -0.3, y: 0, ry: PI / 2, face: 'happy', shR: [30, 10], elR: 40, shL: [20, 10], elL: 20 }], [STICK - 0.25, { y: 0.18, shR: [160, -10], elR: 30, handR: 'open', spine: -6 }, 'out'], [STICK, { y: 0.22, shR: [150, -15], elR: 10 }], [STICK + 0.3, { y: 0, face: 'smug', shR: [20, 10], elR: 40 }, 'in']]),
    { who: 'mate', seed: 2.2, keys: [[0, { x: 0.4, z: -0.2, ry: -PI / 2, face: 'worried', shL: [20, 15], elL: 30, shR: [20, 15], elR: 30 }], [STICK, { face: 'shock', headNod: -6 }], [STICK + 0.4, { face: 'disbelief', headNod: 6, headTurn: 15, shR: [100, 10], elR: 120, handR: 'point' }]] },
  ],
};

// ================= beat 3, the car boot sale in the rain: flogging the jet ski; Nan and the never-never ======
const C1_T0 = H5_T1, C1_T1 = S(15) + 0.9, C2_T1 = E(15) + 0.1, C3_T1 = E(16) + 0.1, C4_T1 = E(17) + 0.1, C5_T1 = E(18) + 0.25, C6_T1 = S(19) - 0.3;
const shiver = (ts: number) => 0.012 * Math.sin(ts * 40);
const alfBoot = (ts0: number): Actor => ({ who: 'lead', seed: 0.3, pin: pinLive, keys: [[0, { x: -0.6, z: 0.55, ry: 0.15, face: 'sad', shL: [40, -20], elL: 100, twL: 50, shR: [40, -20], elR: 100, twR: 50, shrug: 0.6, sway: shiver(ts0) }], [1.2, { face: 'worried', headTurn: 25 }]] });
const mateBoot: Actor = { who: 'mate', seed: 2.2, keys: [[0, { x: 0.45, z: 0.5, ry: -0.2, face: 'sad', shL: [40, -20], elL: 100, twL: 50, shR: [40, -20], elR: 100, twR: 50, shrug: 0.6 }]] };
const nanWalk = walk(0, C1_T1 - C1_T0 - 0.2, 2.6, 1.75, 0.42, { z: 1.4, ry: -PI / 2, face: 'smug', shR: [20, 10], elR: 20 }, 'L');
const bootProps = (
  <>
    <group position={[0.1, 0, 1.35]}><FoldTable /></group>
    <group position={[-0.2, 0.74, 1.35]}><Gnome s={1.1} /></group>
    <group position={[0.4, 0.74, 1.3]}><Telly s={0.45} /></group>
    <group position={[1.15, 0, 1.15]} rotation={[0, -0.6, 0]}><JetSki s={0.8} /></group>
  </>
);
const carbootWide: Shot = {
  id: 'carboot-wide', t0: C1_T0, t1: C1_T1, sw: 1, overlay: RAIN,
  cam: [[0, cam([0.2, 1.7, 5.4], [0.1, 1.0, 0.6], 46)], [C1_T1 - C1_T0, cam([0.3, 1.6, 4.7], [0.2, 1.0, 0.7], 46), 'lin']],
  set: () => <CarBoot>{bootProps}</CarBoot>,
  cast: [alfBoot(0), mateBoot, nan([...nanWalk, [C1_T1 - C1_T0, { x: 1.75, face: 'smug', shR: [70, 20], elR: 20, spine: 10 }]])],
};
const nanSay: Shot = {
  id: 'nan-never', t0: C1_T1, t1: C2_T1, sw: 1, overlay: RAIN,
  cam: [[0, cam([0.85, 1.2, 3.55], [1.5, 1.0, 1.65], 36)], [C2_T1 - C1_T1, cam([0.95, 1.18, 3.3], [1.5, 1.0, 1.65], 36), 'lin']],
  set: () => <CarBoot>{bootProps}</CarBoot>,
  cast: [nan([[0, { x: 1.75, z: 1.5, ry: -0.75, face: 'smug', shR: [70, 20], elR: 20, spine: 10 }], [0.6, { face: 'warm', headTilt: 8 }], [1.4, { face: 'smug', shR: [80, 25], elR: 10 }]])],
};
const alfWhat: Shot = {
  id: 'alf-what', t0: C2_T1, t1: C3_T1, sw: 1, overlay: RAIN,
  cam: [[0, cam([0.1, 1.68, 2.2], [-0.6, 1.6, 0.55], 36)], [C3_T1 - C2_T1, cam([0.0, 1.66, 1.95], [-0.6, 1.62, 0.55], 36), 'lin']],
  set: () => <CarBoot>{bootProps}</CarBoot>,
  cast: [{ who: 'lead', seed: 0.3, pin: pinLive, keys: [[0, { x: -0.6, z: 0.55, ry: 0.55, face: 'disbelief', shrug: 0.4, headTilt: -10, shL: [40, -20], elL: 100, twL: 50, shR: [40, -20], elR: 100, twR: 50 }]] }],
};
const nanNever: Shot = {
  id: 'nan-pay', t0: C3_T1, t1: C4_T1, sw: 1, overlay: RAIN,
  cam: [[0, cam([0.88, 1.18, 3.35], [1.5, 1.0, 1.65], 32)], [C4_T1 - C3_T1, cam([0.92, 1.16, 3.15], [1.5, 1.0, 1.65], 32), 'lin']],
  set: () => <CarBoot>{bootProps}</CarBoot>,
  cast: [nan([[0, { x: 1.75, z: 1.5, ry: -0.75, face: 'smug', shR: [80, 25], elR: 10, spine: 10 }], [0.5, { face: 'bored', headNod: 6 }]])],
};
const alfRich: Shot = {
  id: 'alf-rich', t0: C4_T1, t1: C5_T1, sw: 1, overlay: RAIN,
  cam: [[0, cam([0.15, 1.6, 2.0], [-0.55, 1.55, 0.55], 38)], [C5_T1 - C4_T1, cam([0.05, 1.6, 1.7], [-0.55, 1.58, 0.55], 38), 'lin']],
  set: () => <CarBoot>{bootProps}</CarBoot>,
  cast: [{ who: 'lead', seed: 0.3, pin: pinLive, keys: [[0, { x: -0.6, z: 0.55, ry: 0.5, face: 'worried', shL: [30, 30], elL: 40, shR: [30, 30], elR: 40, handL: 'open', handR: 'open' }], [0.3, { face: 'angry', shL: [60, 40], elL: 30, shR: [60, 40], elR: 30, spine: 8 }]] }],
};
const matePoint: Shot = {
  id: 'mate-point', t0: C5_T1, t1: C6_T1, sw: 1, overlay: RAIN,
  cam: [[0, cam([0.75, 2.05, 2.15], [0.4, 1.45, -2.0], 46)], [C6_T1 - C5_T1, cam([0.7, 2.1, 1.85], [0.45, 2.3, -16], 38), 'io']],
  set: () => <CarBoot>{bootProps}</CarBoot>,
  cast: [{ who: 'mate', seed: 2.2, keys: [[0, { x: 0.45, z: 0.5, ry: PI - 0.1, face: 'thinking', shR: [100, 6], elR: 6, handR: 'point', shL: [10, 10], elL: 20 }]] }],
};

// ================= the twist: the back office. The grade flickers to the real world; the Owner and the receipt ======
const O1_T0 = C6_T1, O1_T1 = E(19) - 0.2, REC_T1 = S(20) + 0.9, O3_T1 = E(20) + 0.15, O4_T1 = E(21) + 0.1, O5_T1 = E(22) + 0.1, O6_T1 = E(23) + 0.15, O7_T1 = S(24) - 0.1;
export const REAL = [S(19) - 0.05, S(19) + 0.3] as const; // the split second the grade flickers to the real world
const swOffice = (t: number) => (t >= REAL[0] && t < REAL[1] ? 0 : 1);
const OWN: Pose3 = { x: 0, z: -1.2, ry: 0, face: 'sad', spine: 22, headNod: 10, shL: [40, -10], elL: 60, shR: [40, -10], elR: 60, handL: 'open', handR: 'open' };
const receiptAt = (u: number) => <group position={[0.27, 1.6, -0.88]} rotation={[-0.08, 0, 0.04]}><FeeReceipt u={u} /></group>;
const officeOwner: Shot = {
  id: 'office-owner', t0: O1_T0, t1: O1_T1, sw: (ts) => swOffice(O1_T0 + ts),
  cam: [[0, cam([0.25, 1.5, 1.4], [0.0, 1.3, -1.2], 40)], [O1_T1 - O1_T0, cam([0.15, 1.45, 0.75], [0.0, 1.35, -1.2], 40), 'lin']],
  set: (c) => <BackOffice sw={c.sw}>{c.ts > 0.4 ? receiptAt(prog(c.ts, 0.4, 0.9, 'out')) : null}</BackOffice>,
  cast: [owner([[0, OWN], [0.5, { spine: 6, headNod: 0, face: 'bored', shR: [120, -4], elR: 20, handR: 'fist' }, 'out'], [O1_T1 - O1_T0, { shR: [122, -4] }]])],
};
const receiptInsert: Shot = {
  id: 'receipt', t0: O1_T1, t1: REC_T1, sw: 1,
  cam: [[0, cam([0.28, 1.34, 0.05], [0.28, 1.34, -0.9], 34)], [REC_T1 - O1_T1, cam([0.28, 1.34, -0.1], [0.28, 1.34, -0.9], 34), 'lin']],
  set: () => <BackOffice>{receiptAt(1)}</BackOffice>,
  cast: [owner([[0, { ...OWN, spine: 6, headNod: 0, face: 'bored', shR: [122, -4], elR: 20, handR: 'fist' }]])],
};
const alfOffice = (keys: Key3[]): Actor => ({ who: 'lead', seed: 0.3, pin: pinLive, keys });
const ALF_O: Pose3 = { x: -0.45, z: 0.25, ry: PI - 0.15, face: 'shock', shL: [20, 15], elL: 30, shR: [20, 15], elR: 30 };
const MATE_O: Pose3 = { x: 0.45, z: 0.35, ry: PI + 0.2, face: 'disbelief', shL: [20, 10], elL: 30, shR: [20, 10], elR: 30 };
const alfEight: Shot = {
  id: 'alf-eight', t0: REC_T1, t1: O3_T1, sw: 1,
  cam: [[0, cam([-0.2, 1.62, -1.45], [-0.45, 1.6, 0.25], 38)], [O3_T1 - REC_T1, cam([-0.25, 1.62, -1.2], [-0.45, 1.62, 0.25], 38), 'lin']],
  set: () => <BackOffice />,
  cast: [alfOffice([[0, ALF_O], [0.3, { spine: -8, shL: [60, 40], elL: 20, shR: [60, 40], elR: 20, handL: 'open', handR: 'open' }]]), { who: 'mate', seed: 2.2, keys: [[0, MATE_O]] }],
};
const ownerUpTo: Shot = {
  id: 'owner-upto', t0: O3_T1, t1: O4_T1, sw: 1,
  cam: [[0, cam([-0.2, 1.55, 0.9], [0.0, 1.45, -1.2], 36)], [O4_T1 - O3_T1, cam([-0.15, 1.52, 0.6], [0.0, 1.47, -1.2], 36), 'lin']],
  set: () => <BackOffice />,
  cast: [owner([[0, { ...OWN, spine: 4, headNod: 0, face: 'bored', shR: [70, 20], elR: 70, handR: 'point', shL: [30, -10], elL: 60 }], [0.6, { headTilt: 8, shR: [75, 25], elR: 60 }]])],
};
const mateWhy: Shot = {
  id: 'mate-why', t0: O4_T1, t1: O5_T1, sw: 1,
  cam: [[0, cam([0.6, 1.66, -1.45], [0.45, 1.6, 0.35], 38)], [O5_T1 - O4_T1, cam([0.62, 1.66, -1.2], [0.45, 1.62, 0.35], 38), 'lin']],
  set: () => <BackOffice />,
  cast: [{ who: 'mate', seed: 2.2, keys: [[0, MATE_O], [0.3, { face: 'thinking', shR: [60, 40], elR: 50, handR: 'open', shrug: 0.5 }]], heldL: () => <group position={[0, -0.05, 0.05]}><Gnome s={0.8} /></group> }, alfOffice([[0, { ...ALF_O, face: 'worried' }]])],
};
const ownerMore: Shot = {
  id: 'owner-more', t0: O5_T1, t1: O6_T1, sw: 1,
  cam: [[0, cam([0.1, 1.5, 0.55], [0.0, 1.48, -1.2], 32)], [O6_T1 - O5_T1, cam([0.08, 1.5, 0.35], [0.0, 1.5, -1.2], 32), 'lin']],
  set: () => <BackOffice />,
  cast: [owner([[0, { ...OWN, spine: 2, headNod: 0, face: 'bored', shL: [20, 10], elL: 30, shR: [20, 10], elR: 30 }], [0.5, { face: 'smug', headNod: -4 }]])],
};
const gnomeHide: Shot = {
  id: 'gnome', t0: O6_T1, t1: O7_T1, sw: 1,
  cam: [[0, cam([2.6, 1.6, 0.55], [0.45, 1.35, 0.35], 40)], [O7_T1 - O6_T1, cam([2.4, 1.6, 0.55], [0.45, 1.38, 0.35], 40), 'lin']],
  set: () => <BackOffice />,
  cast: [{ who: 'mate', seed: 2.2, keys: [[0, { ...MATE_O, face: 'worried', shL: [40, -10], elL: 70, handL: 'open' }], [0.5, { shL: [-30, 15], elL: 40, face: 'holding', headTurn: -20 }, 'io']], heldL: () => <group position={[0, -0.05, 0.05]}><Gnome s={0.8} /></group> }],
};

// ================= the cliffhanger: the Rep scoots in and scans Alfie's pin; cut to black mid-word ======
const X1_T0 = O7_T1, SCAN = 0.75, X1_T1 = S(25) + 0.3, CUT = E(25);
const repScanKeys = (ts0: number): Key3[] => ([
  [0, { x: 1.7, z: 0.3, y: 0.12, ry: -PI / 2, ...REPRIDE }],
  [0.5, { x: -0.05, y: 0.12 }, 'out'],
  [SCAN - 0.1, { y: 0, face: 'happy', shR: [100, 0], elR: 10, handR: 'fist', spine: 4, hipL: [0, 3], knL: 0, hipR: [0, 3], knR: 0, shL: [10, 10], elL: 20 }],
  [SCAN + 0.2, { face: 'shock' }],
] as Key3[]).map(([t, p, e]) => [t - ts0, p, e] as Key3);
const readerFlash = (ts: number) => (ts > SCAN ? 1 : 0);
const repScan: Shot = {
  id: 'rep-scan', t0: X1_T0, t1: X1_T1, sw: 1,
  cam: [[0, cam([-1.45, 1.55, 1.55], [0.1, 1.2, 0.25], 44)], [X1_T1 - X1_T0, cam([-1.2, 1.5, 1.25], [-0.05, 1.25, 0.25], 40), 'io']],
  shake: [[SCAN, 0.4]],
  set: (c) => <BackOffice>{scooterAt(xAt(repScanKeys(0), Math.min(c.ts, 0.5)), 0.3, -PI / 2)}</BackOffice>,
  cast: [
    rep(repScanKeys(0), (ts) => <group position={[0, -0.02, 0.06]} rotation={[0, 0, 0]}><RepReader flash={readerFlash(ts)} text={ts > SCAN ? '3 OWED' : 'SCAN'} /></group>),
    { who: 'lead', seed: 0.3, pin: (ts) => (ts > SCAN ? 0.8 + 0.6 * Math.abs(Math.sin(ts * 23)) : pinLive(ts)), keys: [[0, { x: -0.45, z: 0.25, ry: 0.35, face: 'worried', shL: [20, 15], elL: 30, shR: [20, 15], elR: 30 }], [SCAN, { face: 'shock', spine: -10, shL: [70, 40], elL: 30, shR: [70, 40], elR: 30, handL: 'open', handR: 'open' }]] },
  ],
};
const repShock: Shot = {
  id: 'rep-shock', t0: X1_T1, t1: CUT + 0.05, sw: 1,
  cam: [[0, cam([0.25, 1.4, 1.75], [-0.05, 1.25, 0.3], 38)], [CUT - X1_T1, cam([0.15, 1.38, 1.25], [-0.05, 1.3, 0.3], 34), 'in']],
  shake: [[CUT - X1_T1 - 0.6, 0.3]],
  set: () => <BackOffice />,
  cast: [rep([[0, { x: -0.05, z: 0.3, ry: 0.15, face: 'shock', shR: [80, 0], elR: 60, handR: 'fist', shL: [10, 10], elL: 20 }], [1.0, { face: 'scream', spine: -8 }]], () => <group position={[0, -0.02, 0.06]}><RepReader flash={1} text="3 OWED" /></group>)],
};

export const ACT2: Shot[] = [titleWide, titlePush, trolleyIn, foot, letterbox, shovel, count, repIn, sticker,
  carbootWide, nanSay, alfWhat, nanNever, alfRich, matePoint, officeOwner, receiptInsert, alfEight, ownerUpTo, mateWhy, ownerMore, gnomeHide, repScan, repShock];
export const BLACK_AT = CUT;
export const TOTAL = CUT + 0.4;
void CAST;
