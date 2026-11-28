// EP23 Pay Later (global edition). This file holds the cold open (0:00 to the hold on the PAY LATER till, the 10-20 s
// test render). Timings follow src/episodes/ep23/lines.json: S(n) / E(n) are line n's start and end.
import React from 'react';
import words from '../../episodes/ep23/words.json';
import { makeEpisode3, cam, Shot, Actor, ActorView, Key3, Pose3, prog, lerp, clamp } from '../kit3';
import { Booth, Clipboard } from '../ep21/sets';
import { Trolley } from '../../props';
import { SaleFloor, Jacket, JacketPiece, TornTag, Telly, Sofa, TILL, SHOPPERS } from './sets';
import { S, E, walk, xAt, pinIdle, pinLive, HUG, GRIP, FLOOR_SIT, ahead } from './shared';
import { ACT2, TITLE, BLACK_AT, TOTAL } from './act2';

const PI = Math.PI;
/** The jacket hugged to an actor's chest (world-placed: x, z, facing ry). */
const hugged = (x: number, z: number, ry: number, bob = 0, swing = 0) => {
  const [jx, jy, jz] = ahead(x, z, ry, 1.06 + bob, 0.17);
  return <group position={[jx, jy, jz]} rotation={[0.12, ry, 0]}><Jacket s={0.66} tagSwing={swing} /></group>;
};

// ---------- 0:00 bait: Alfie skids into the till hugging the last red puffer (thud on frame ~5) ----------
const A_T1 = 2.0, THUD = 0.32;
const alfSkid: Actor = {
  who: 'lead', seed: 0.3, pin: pinIdle,
  keys: [
    [0, { x: -0.75, z: 0.22, ry: PI / 2 - 0.25, face: 'happy', spine: -12, side: -6, crouch: 0.25, hipL: [-18, 6], knL: 10, hipR: [26, 4], knR: 22, ...HUG }],
    [THUD, { x: 0.12, spine: 10, side: 4, crouch: 0.1, hipL: [0, 4], knL: 4, hipR: [6, 4], knR: 6, face: 'shock' }, 'out'],
    [THUD + 0.25, { spine: 2, side: 0, crouch: 0, face: 'happy' }],
    [1.2, { ry: PI / 2 - 0.65, headTurn: -22, face: 'happy' }],
    [A_T1, { headTurn: -26 }],
  ],
};
const skid: Shot = {
  id: 'skid', t0: 0, t1: A_T1,
  cam: [[0, cam([0.95, 1.38, 2.45], [-0.15, 1.3, 0.2], 44)], [A_T1, cam([0.8, 1.38, 2.15], [0.0, 1.32, 0.2], 44), 'out']],
  shake: [[THUD, 0.9]],
  set: (c) => {
    const ts = c.ts; const k = prog(ts, 0, THUD, 'out');
    return <SaleFloor>{hugged(lerp(-0.75, 0.12, k), 0.22, PI / 2 - 0.25 - (ts > 1.2 ? 0.4 * prog(ts, THUD + 0.3, 1.2) : 0), 0, Math.sin(ts * 9) * 0.5 * Math.exp(-ts * 1.2) + (ts > THUD ? 0.4 * Math.sin((ts - THUD) * 11) * Math.exp(-(ts - THUD) * 3) : 0))}</SaleFloor>;
  },
  cast: [alfSkid],
};

// ---------- 0:02 from behind the till: Mate barrels in behind Alfie with an overloaded trolley ----------
const B_T0 = A_T1, B_T1 = 3.85;
const mateKeys = walk(0, 1.4, -2.4, -0.75, 0.3, { z: 1.05, ry: PI / 2, face: 'happy', spine: 14, shL: [70, -6], elL: 25, shR: [70, -6], elR: 25, handL: 'fist', handR: 'fist' }, 'none');
const mateTrolley: Actor = { who: 'mate', seed: 2.2, keys: [...mateKeys, [1.6, { x: -0.7, spine: 6, face: 'happy', hipL: [0, 3], knL: 0, hipR: [0, 3], knR: 0 }]] };
const alfWait: Actor = { who: 'lead', seed: 0.3, pin: pinIdle, keys: [[0, { x: 0.12, z: 0.22, ry: PI - 0.3, face: 'happy', ...HUG }], [0.9, { headTurn: 40, face: 'laugh' }], [1.5, { headTurn: 10, face: 'happy' }]] };
const overTill: Shot = {
  id: 'over-till', t0: B_T0, t1: B_T1,
  cam: [[0, cam([1.7, 1.85, -1.5], [-0.55, 1.0, 0.8], 50)], [B_T1 - B_T0, cam([1.55, 1.8, -1.3], [-0.6, 1.0, 0.85], 50), 'lin']],
  set: (c) => (
    <SaleFloor>
      {hugged(0.12, 0.22, PI - 0.3)}
      <group position={[xAt(mateKeys, Math.min(c.ts, 1.4)) + 0.85, 0, 1.05]}><Trolley n={14} /></group>
    </SaleFloor>
  ),
  cast: [mateTrolley, alfWait],
};

// ---------- 0:03.9 insert: Alfie's finger taps PAY IN 4; the screen flips to $25 TODAY ----------
const C_T0 = B_T1, C_T1 = 5.45, TAP = 0.75;
const alfTap: Actor = {
  who: 'lead', seed: 0.3, pin: pinIdle,
  keys: [
    [0, { x: TILL.x + 0.5, z: 0.22, ry: PI + 0.3, face: 'happy', shL: [62, -14], elL: 95, twL: 35, handL: 'open', shR: [20, 8], elR: 30, spine: 6 }],
    [TAP - 0.25, { shR: [85, -8], elR: 70, handR: 'point', spine: 22, headNod: 16 }],
    [TAP, { shR: [80, -8], elR: 62, spine: 26 }, 'in'],
    [TAP + 0.3, { shR: [70, 4], elR: 80, spine: 16, face: 'laugh' }],
  ],
};
const tap: Shot = {
  id: 'tap', t0: C_T0, t1: C_T1,
  cam: [[0, cam([TILL.x - 0.12, TILL.top + 0.16, TILL.z + 0.78], [TILL.x + 0.15, TILL.top + 0.13, TILL.z + 0.08], 30)], [C_T1 - C_T0, cam([TILL.x - 0.08, TILL.top + 0.15, TILL.z + 0.66], [TILL.x + 0.15, TILL.top + 0.13, TILL.z + 0.08], 30), 'lin']],
  set: (c) => <SaleFloor reader={c.ts < TAP + 0.05 ? 'PAY IN 4' : '$25 TODAY'}>{hugged(TILL.x + 0.5, 0.22, PI + 0.3)}</SaleFloor>,
  cast: [alfTap],
};

// ---------- 0:05.4 the tug of war: Mate grabs the jacket to bag it; it rips into four on "that-" ----------
const D_T0 = C_T1, RIP = E(1) - D_T0, D_T1 = E(1) + 0.3;
const tugX = (ts: number) => 0.38 + 0.05 * Math.sin(ts * 7) * prog(ts, 0.4, RIP);
const alfTug: Actor = {
  who: 'lead', seed: 0.3, pin: pinIdle,
  keys: [
    [0, { x: -0.08, z: 0.5, ry: PI / 2, face: 'happy', ...GRIP }],
    [0.45, { face: 'worried', spine: -10 }],
    [RIP - 0.3, { face: 'angry', spine: -20, crouch: 0.25, hipL: [20, 8], knL: 20, hipR: [-12, 6], knR: 6 }],
    [RIP, { face: 'angry', spine: -24 }],
    [RIP + 0.3, { x: -0.4, face: 'shock', spine: -30, shL: [110, 20], elL: 10, shR: [110, 20], elR: 10, handL: 'open', handR: 'open' }, 'out'],
  ],
};
const mateTug: Actor = {
  who: 'mate', seed: 2.2,
  keys: [
    [0, { x: 0.86, z: 0.5, ry: -PI / 2, face: 'happy', shR: [40, 6], elR: 40, shL: [20, 6], elL: 20 }],
    [0.35, { ...GRIP, spine: 6 }],
    [RIP - 0.3, { face: 'holding', spine: -18, crouch: 0.25, hipL: [20, 8], knL: 20, hipR: [-12, 6], knR: 6 }],
    [RIP, { spine: -22 }],
    [RIP + 0.3, { x: 1.18, face: 'shock', spine: -30, shL: [110, 20], elL: 10, shR: [110, 20], elR: 10, handL: 'open', handR: 'open' }, 'out'],
  ],
};
const tug: Shot = {
  id: 'tug', t0: D_T0, t1: D_T1,
  cam: [[0, cam([0.38, 1.4, 4.1], [0.38, 1.2, 0.5], 44)], [RIP, cam([0.38, 1.34, 3.6], [0.38, 1.2, 0.5], 44), 'in'], [D_T1 - D_T0, cam([0.38, 1.4, 3.9], [0.38, 1.1, 0.5], 48), 'out']],
  shake: [[RIP, 1.6]],
  set: (c) => {
    const ts = c.ts, stretch = 1 + 0.25 * prog(ts, 0.4, RIP);
    return (
      <SaleFloor>
        <group position={[tugX(ts), 1.18, 0.5]} rotation={[0, 0.1, 0]} scale={[ts < RIP ? stretch : 1, 1, 1]}>
          <Jacket s={0.78} rip={prog(ts, RIP, RIP + 0.3, 'out')} tag={ts < RIP} />
        </group>
        {ts >= RIP ? <TornTag u={prog(ts, RIP, RIP + 2.2, 'lin')} from={[0.52, 1.0, 0.6]} /> : null}
      </SaleFloor>
    );
  },
  cast: [alfTug, mateTug],
};

// ---------- 0:07.4 the stillness: both on their backsides, a sleeve on Alfie's head, the torn tag lands ----------
const F_T0 = D_T1, F_T1 = S(2) - 0.05;
const ALF_SIT: Pose3 = { ...FLOOR_SIT, x: -0.42, z: 0.6, ry: 0.55, face: 'shock' };
const MATE_SIT: Pose3 = { ...FLOOR_SIT, x: 1.18, z: 0.65, ry: -0.6, face: 'disbelief', shR: [50, 10], elR: 60, handR: 'fist' };
export const sleeveOnHead = (x: number, z: number, ry: number) => (
  <group position={[x - 0.02, 0.96, z - 0.02]} rotation={[0.25, ry, 1.45]}><JacketPiece kind="sleeve" s={0.8} /></group>
);
const mateHalf = (x: number, y: number, z: number, ry: number) => <group position={[x, y, z]} rotation={[1.25, ry, -0.2]}><JacketPiece kind="half" s={0.8} /></group>;
const stillShot: Shot = {
  id: 'still', t0: F_T0, t1: F_T1,
  cam: [[0, cam([0.38, 0.7, 4.3], [0.38, 0.5, 0.55], 50)], [F_T1 - F_T0, cam([0.38, 0.68, 4.1], [0.38, 0.5, 0.55], 50), 'lin']],
  set: (c) => (
    <SaleFloor>
      {sleeveOnHead(-0.42, 0.6, 0.55)}
      {mateHalf(1.12, 0.3, 0.98, -0.6)}
      <TornTag u={clamp(0.15 + 0.85 * prog(c.ts, 0, F_T1 - F_T0, 'lin'))} from={[0.52, 1.0, 0.6]} />
      <group position={[0.25, 0.08, 0.95]} rotation={[PI / 2, 0, 0.8]}><JacketPiece kind="sleeve" side={-1} s={0.85} /></group>
      <group position={[0.6, 0.07, 0.25]} rotation={[-PI / 2, 0, -0.4]}><JacketPiece kind="half" side={-1} s={0.8} /></group>
    </SaleFloor>
  ),
  cast: [{ who: 'lead', seed: 0.3, pin: pinIdle, noBreath: true, keys: [[0, ALF_SIT], [0.6, { face: 'disbelief' }]] }, { who: 'mate', seed: 2.2, noBreath: true, keys: [[0, MATE_SIT]] }],
};

// ---------- 0:08.3 Mate, half a jacket in his fist: "...You said split it." ----------
const G_T0 = F_T1, G_T1 = S(3) - 0.1;
const sorry: Shot = {
  id: 'mate-sorry', t0: G_T0, t1: G_T1,
  cam: [[0, cam([0.7, 0.95, 2.25], [1.18, 0.72, 0.65], 38)], [G_T1 - G_T0, cam([0.78, 0.93, 2.0], [1.18, 0.73, 0.65], 38), 'lin']],
  set: (c) => <SaleFloor>{mateHalf(1.12, 0.3 + 0.08 * prog(c.ts, 0.1, 0.5, 'out'), 0.98, -0.6)}</SaleFloor>,
  cast: [{ who: 'mate', seed: 2.2, keys: [[0, { ...MATE_SIT, face: 'worried' }], [0.35, { shR: [55, 10], elR: 60, headTilt: -10, face: 'holding', shrug: 0.5 }, 'out'], [G_T1 - G_T0, { headTilt: -14, shrug: 0.6 }]] }],
};

// ---------- 0:09.9 the Booth (as EP21-22) ----------
const producer = (keys: Key3[]): Actor => ({ who: 'producer', seed: 1.7, keys, heldL: () => <Clipboard /> });
const prodBase: Pose3 = { x: 0.85, y: 0, z: -0.15, ry: -0.75, shL: [16, -8], elL: 75, twL: 30, handL: 'fist', shR: [10, 10], elR: 20 };
const narr = (keys: Key3[]): Actor => ({ who: 'narrator', seed: 0.9, keys });
const narrSit: Pose3 = { x: 0, y: 0.04, z: 0.02, ry: PI, sit: true, hipL: [90, 8], knL: 88, hipR: [90, 8], knR: 88, spine: 8, shL: [50, 10], elL: 60, shR: [50, 10], elR: 60, face: 'neutral' };
const narrFrozen: Pose3 = { ...narrSit, spine: -4, shR: [125, 30], elR: 40, handR: 'open', shL: [60, 18], elL: 70, headTilt: 8 };
const H_T0 = G_T1, H_T1 = S(4) - 0.15;
const booth1: Shot = {
  id: 'booth-prod1', t0: H_T0, t1: H_T1,
  cam: [[0, cam([0.08, 1.48, 1.65], [0.84, 1.36, -0.15], 40)], [H_T1 - H_T0, cam([0.2, 1.48, 1.28], [0.84, 1.38, -0.15], 40), 'lin']],
  set: () => <Booth />,
  cast: [producer([[0, { ...prodBase, face: 'shock', spine: 6 }], [0.35, { spine: 14, face: 'disbelief', headTilt: -8, shR: [70, 20], elR: 60, handR: 'point' }], [H_T1 - H_T0, { spine: 15 }]]), narr([[0, narrFrozen]])],
};
const I_T0 = H_T1, I_T1 = S(5) - 0.15;
const booth2: Shot = {
  id: 'booth-narr', t0: I_T0, t1: I_T1,
  cam: [[0, cam([-0.5, 1.7, 1.55], [0.05, 1.15, -0.5], 42)], [I_T1 - I_T0, cam([-0.38, 1.62, 1.18], [0.05, 1.18, -0.5], 42), 'lin']],
  set: () => <Booth />,
  cast: [narr([[0, { ...narrFrozen, spine: 6, shR: [90, 40], elR: 70, handR: 'point' }], [0.4, { headTilt: -6, shR: [100, 45], elR: 55 }], [0.9, { shR: [92, 40], elR: 70 }], [I_T1 - I_T0, { shR: [96, 42] }]]), producer([[0, { ...prodBase, face: 'worried', spine: 12 }]])],
};
const J_T0 = I_T1, J_T1 = E(5) + 0.05; // the Booth stays under 6 s (STUDIO-RULES 5)
const booth3: Shot = {
  id: 'booth-prod2', t0: J_T0, t1: J_T1,
  cam: [[0, cam([0.4, 1.55, 1.22], [0.84, 1.45, -0.15], 36)], [J_T1 - J_T0, cam([0.52, 1.55, 0.86], [0.84, 1.46, -0.15], 36), 'lin']],
  shake: [[0.25, 0.22]],
  set: () => <Booth />,
  cast: [producer([
    [0, { ...prodBase, face: 'shock', spine: 4 }],
    [0.25, { face: 'scream', shrug: 0.5 }],
    [0.9, { face: 'shock', shrug: 0.2 }],
    [1.1, { shR: [108, 20], elR: 6, handR: 'point', face: 'scream', headTurn: -10 }, 'out'],
  ]), narr([[0, narrFrozen]])],
};

// ---------- 0:16 the pin fires on the shop floor: glow, the white crack, the switch ----------
const K_T0 = J_T1, K_T1 = S(6) - 0.05, CRACK = 0.42;
const pinShot: Shot = {
  id: 'pin', t0: K_T0, t1: K_T1,
  cam: [[0, cam([-0.2, 2.6, 1.3], [-0.42, 0.55, 0.62], 46)], [K_T1 - K_T0, cam([-0.25, 1.15, 1.5], [-0.42, 0.72, 0.6], 40), 'out']],
  crack: CRACK, sw: (ts) => (ts < CRACK ? 0 : 1), shake: [[CRACK, 0.8]],
  set: (c) => <SaleFloor sw={c.sw} later={c.ts >= CRACK}>{sleeveOnHead(-0.42, 0.6, 0.55)}</SaleFloor>,
  cast: [{ who: 'lead', seed: 0.3, noBreath: true, pin: (ts) => (ts < CRACK ? 0.3 + 2 * ts : 0.75 + 0.25 * Math.sin(ts * 9)), keys: [[0, { ...ALF_SIT, face: 'worried', headNod: -10 }], [CRACK, { face: 'shock', headNod: -16 }]] }],
};

// ---------- 0:17 the what-if store: no cash drawer, one giant PAY LATER button; shoppers walk out with a TV ----------
const M_T0 = K_T1, M_T1 = S(7) - 0.1;
const carryUp: Pose3 = { shL: [165, 12], elL: 15, shR: [165, 12], elR: 15, handL: 'open', handR: 'open', face: 'happy' };
const tellyGuy = walk(0, 2.2, 2.4, -1.6, 0.34, { z: 1.6, ry: -PI / 2, ...carryUp }, 'none');
const alfLook: Actor = {
  who: 'lead', seed: 0.3, pin: pinLive,
  keys: [
    [0, { x: TILL.x - 0.45, z: 0.2, ry: PI - 0.1, face: 'disbelief', spine: 30, headNod: 20, shL: [60, 10], elL: 30, shR: [60, 14], elR: 30, handR: 'open', handL: 'open' }],
    [0.8, { headTurn: 25 }], [1.4, { spine: 18, headNod: 4, headTurn: -20, face: 'worried' }], [M_T1 - M_T0, { headTurn: -30 }],
  ],
};
const laterWide: Shot = {
  id: 'later-wide', t0: M_T0, t1: M_T1, sw: 1,
  cam: [[0, cam([0.75, 1.62, -1.55], [0.35, 1.2, 0.5], 46)], [M_T1 - M_T0, cam([0.7, 1.58, -1.35], [0.35, 1.22, 0.5], 46), 'lin']],
  set: (c) => (
    <SaleFloor sw={1} later press={0.5 + 0.5 * Math.sin(c.ts * 4)}>
      <group position={[TILL.x - 0.45, 1.66, 0.12]} rotation={[0.6, PI - 0.1, 1.45]}><JacketPiece kind="sleeve" s={0.8} /></group>
      <group position={[xAt(tellyGuy, c.ts), SHOPPERS[0].height + 0.32, 1.6]}><Telly /></group>
    </SaleFloor>
  ),
  cast: [alfLook, { who: 'shopper0', look: SHOPPERS[0], seed: 4.1, mute: true, keys: tellyGuy }],
};

// ---------- 0:18.8 Mate gawps as two shoppers carry a sofa straight past the till ----------
const N_T0 = M_T1, N_T1 = E(7) + 0.3;
const sofaPair = (dx: number) => walk(0, N_T1 - N_T0, -3.4 + dx, 0.4 + dx, 0.36, { z: -1.75, ry: PI / 2, shL: [55, -12], elL: 15, shR: [55, -12], elR: 15, handL: 'fist', handR: 'fist', face: 'happy', spine: 4 }, 'none');
const sofaA = sofaPair(0), sofaB = sofaPair(1.75);
const mateGawp: Shot = {
  id: 'mate-gawp', t0: N_T0, t1: N_T1, sw: 1,
  cam: [[0, cam([-0.7, 1.5, 3.1], [-0.95, 1.3, 0.2], 40)], [N_T1 - N_T0, cam([-0.72, 1.5, 2.8], [-0.95, 1.32, 0.2], 40), 'lin']],
  set: (c) => <SaleFloor sw={1} later><group position={[xAt(sofaA, c.ts) + 0.88, 0.32, -1.75]}><Sofa /></group></SaleFloor>,
  cast: [
    { who: 'mate', seed: 2.2, keys: [[0, { x: -0.95, z: 0.55, ry: 0.15, face: 'disbelief', shL: [20, 10], elL: 30, shR: [20, 10], elR: 30, headTurn: -30 }], [0.6, { headTurn: 0, face: 'shock' }], [1.3, { headTurn: 35, face: 'disbelief', shrug: 0.4 }]] },
    { who: 'shopper1', look: SHOPPERS[1], seed: 4.7, mute: true, keys: sofaA },
    { who: 'shopper2', look: SHOPPERS[2], seed: 5.3, mute: true, keys: sofaB.map(([t, p, e]) => [t, { ...p, ry: -PI / 2 }, e] as Key3) },
  ],
};

// ---------- 0:20.8 push in on the PAY LATER button, pulsing (the hold before "And what if Britain...") ----------
const O_T0 = N_T1, O_T1 = S(8) - 0.05;
const btnHold: Shot = {
  id: 'button', t0: O_T0, t1: O_T1, sw: 1,
  cam: [[0, cam([TILL.x + 0.15, TILL.top + 0.65, TILL.z + 1.55], [TILL.x + 0.15, TILL.top + 0.1, TILL.z + 0.08], 34)], [O_T1 - O_T0, cam([TILL.x + 0.15, TILL.top + 0.32, TILL.z + 0.72], [TILL.x + 0.15, TILL.top + 0.1, TILL.z + 0.08], 34), 'io']],
  set: (c) => <SaleFloor sw={1} later press={0.5 + 0.5 * Math.sin(c.ts * 5)} />,
  cast: [],
};

export const COLD_OPEN: Shot[] = [skid, overTill, tap, tug, stillShot, sorry, booth1, booth2, booth3, pinShot, laterWide, mateGawp, btnHold];
export const TEST_END = O_T1;

export const ep23 = makeEpisode3({
  id: 'ep23',
  shots: [...COLD_OPEN, ...ACT2],
  words: words as any,
  total: TOTAL,
  title: TITLE,
  blackAt: BLACK_AT,
  hook: { node: <>Is <span style={{ color: '#FFD43B' }}>pay later</span> free?</>, until: 3.0 },
});
// keep ActorView imported for shots that draw riders from the set (act 2)
void ActorView;
