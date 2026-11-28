// EP22 Typed Money. This file holds the cold open (0:00 to the hold on Nan's jar, the 10-20 s test render).
// Timings follow src/episodes/ep22/lines.json (tools/cast_voice.py): S(n) / E(n) are line n's start and end.
import React from 'react';
import words from '../../episodes/ep22/words.json';
import { makeEpisode3, cam, Shot, Actor, ActorView, Key3, Pose3, prog, lerp, clamp } from '../kit3';
import { Coin } from '../../props';
import { Booth, Clipboard } from '../ep21/sets';
import { BankFront, BankHall, CoinJar, Smash, RollingCoin, DOOR, HALL, SAVERS } from './sets';

const PI = Math.PI;
import { S, E } from './shared';
import { ACT2, TITLE, BLACK_AT, TOTAL } from './act2';

// ---------- helpers ----------
/** Walking keys from x0 to x1 over [t0, t1] (shot time): legs and the free arm alternate every half stride. */
const walk = (t0: number, t1: number, x0: number, x1: number, stride = 0.36, base: Pose3 = {}, freeArm: 'L' | 'R' | 'both' = 'L'): Key3[] => {
  const out: Key3[] = []; const n = Math.max(1, Math.round((t1 - t0) / stride));
  for (let i = 0; i <= n; i++) {
    const t = t0 + (i * (t1 - t0)) / n, k = i / n, s = i % 2 ? 1 : -1;
    const arms: Pose3 = freeArm === 'R' ? { shR: [-14 * s, 6], elR: 18 } : freeArm === 'L' ? { shL: [14 * s, 6], elL: 18 } : { shL: [14 * s, 6], elL: 18, shR: [-14 * s, 6], elR: 18 };
    out.push([t, { ...base, x: lerp(x0, x1, k), hipL: [24 * s, 3], knL: s > 0 ? 8 : 30, hipR: [-24 * s, 3], knR: s > 0 ? 30 : 8, bounce: 0.012 * (i % 2), ...arms }, 'lin']);
  }
  return out;
};
const xAt = (keys: Key3[], ts: number) => { // the actor's x at shot time ts (linear between keys, as the walk uses)
  let x = keys[0][1].x ?? 0; let px = x, pt = keys[0][0];
  for (const [t, p] of keys) { const nx = p.x ?? px; if (ts <= t) return t === pt ? nx : lerp(px, nx, (ts - pt) / (t - pt)); px = nx; pt = t; x = nx; }
  return x;
};
const pinGlow = (ts: number) => 0.15 + 0.1 * Math.sin(ts * 5);

// Alfie carries the jar on his right shoulder: right arm up, the jar sitting on the shoulder (world-placed).
const SHOULDER_ARM: Pose3 = { shR: [165, 28], elR: 80, twR: 25, handR: 'open' };
const jarOnShoulder = (x: number, z: number, ry: number, bob: number) => {
  const lx = 0.34, ly = 1.47, lz = 0.02; // his right shoulder, local (+x)
  return <group position={[x + lx * Math.cos(ry) + lz * Math.sin(ry), ly + bob, z - lx * Math.sin(ry) + lz * Math.cos(ry)]} rotation={[0, ry, 0.1]}><CoinJar s={0.9} /></group>;
};

// ---------- 0:00 bait: Alfie staggers along the high street with the jar (MS, already moving on frame 1) ----------
const A_T1 = 1.9;
const alfWalkA = walk(0, A_T1, -0.9, 0.05, 0.34, { face: 'happy', ry: 0.55, z: 2.6, spine: 6, side: 6, headTurn: -10, ...SHOULDER_ARM }, 'L');
const alfA: Actor = { who: 'lead', seed: 0.3, pin: pinGlow, keys: alfWalkA };
const walkA: Shot = {
  id: 'walk', t0: 0, t1: A_T1,
  cam: [[0, cam([-0.75, 1.3, 4.5], [-0.85, 1.68, 2.6], 46)], [A_T1, cam([0.1, 1.3, 4.35], [0.0, 1.68, 2.6], 46), 'lin']],
  set: (c) => (
    <BankFront spin={0.25 * c.t}>
      {jarOnShoulder(xAt(alfWalkA, c.ts), 2.6, 0.55, 0.012 * Math.abs(Math.sin((c.ts / 0.34) * PI)))}
    </BankFront>
  ),
  cast: [alfA],
};

// ---------- 0:01.9 over his shoulder: the bank ahead, Mate jogging to the revolving door ----------
const B_T0 = A_T1, B_T1 = 3.9;
const alfWalkB = walk(0, B_T1 - B_T0, -2.3, -1.45, 0.36, { face: 'happy', ry: 0.95, z: 2.3, spine: 6, side: 6, ...SHOULDER_ARM }, 'L');
const alfB: Actor = { who: 'lead', seed: 0.3, pin: pinGlow, keys: alfWalkB };
const mateB: Actor = {
  who: 'mate', seed: 2.2,
  keys: [
    ...walk(0, 1.3, -0.2, 0.85, 0.3, { face: 'happy', ry: 1.2, z: 1.75, spine: 10 }, 'both'),
    [1.55, { x: 0.95, ry: -0.5, hipL: [0, 3], knL: 0, hipR: [0, 3], knR: 0, face: 'happy', shR: [140, 30], elR: 30, handR: 'open', headTurn: 0 }],
    [1.75, { shR: [150, 45], elR: 25 }], [1.95, { shR: [140, 25], elR: 35 }], [2.0, { shR: [148, 40], elR: 28 }],
  ],
};
const approach: Shot = {
  id: 'approach', t0: B_T0, t1: B_T1,
  cam: [[0, cam([-2.0, 1.95, 6.0], [-1.55, 1.3, 1.8], 50)], [B_T1 - B_T0, cam([-1.2, 1.9, 5.6], [-0.95, 1.28, 1.6], 50), 'lin']],
  set: (c) => (
    <BankFront spin={0.25 * c.t}>
      {jarOnShoulder(xAt(alfWalkB, c.ts), 2.3, 0.95, 0.012 * Math.abs(Math.sin((c.ts / 0.36) * PI)))}
    </BankFront>
  ),
  cast: [alfB, mateB],
};

// ---------- 0:03.9 Mate grabs a wing and winds up; Alfie steps into the door ----------
const C_T0 = B_T1, C_T1 = 5.4, SHOVE = 5.05 - C_T0;
const spinAt = (t: number) => { // the door's angle at episode time t: a lazy drift, then the shove sends it flying
  const t0 = C_T0 + SHOVE;
  if (t < t0) return 0.25 * t;
  const u = t - t0;
  return 0.25 * t0 + 2.2 * u + 9.5 * u * u; // ~3 turns by the spit-out
};
const mateC: Actor = {
  who: 'mate', seed: 2.2,
  keys: [
    [0, { x: 0.95, z: 1.75, ry: -0.75, face: 'happy', shR: [70, 10], elR: 20, shL: [70, -10], elL: 20, handR: 'open', handL: 'open', spine: 4 }],
    [SHOVE - 0.45, { spine: -16, face: 'smug', shR: [60, 10], elR: 70, shL: [60, -10], elL: 70, crouch: 0.15, side: 6 }, 'out'],
    [SHOVE, { spine: 28, face: 'holding', shR: [88, 6], elR: 4, shL: [88, -6], elL: 4, crouch: 0.25, side: -8, x: 0.75 }, 'in'],
    [SHOVE + 0.35, { spine: 20, face: 'shock', x: 0.7 }],
  ],
};
const alfC: Actor = {
  who: 'lead', seed: 0.3, pin: pinGlow,
  keys: [...walk(0, 1.1, -1.45, -0.6, 0.36, { face: 'happy', ry: 1.0, z: 1.65, spine: 6, side: 6, ...SHOULDER_ARM }, 'L'), [1.4, { x: -0.45, z: 1.2, ry: 2.3, face: 'worried' }]],
};
const shove: Shot = {
  id: 'shove', t0: C_T0, t1: C_T1,
  cam: [[0, cam([1.9, 1.55, 3.6], [0.4, 1.25, 1.2], 40)], [C_T1 - C_T0, cam([1.75, 1.5, 3.2], [0.4, 1.22, 1.1], 40), 'lin']],
  shake: [[SHOVE, 0.6]],
  set: (c) => {
    const ts = c.ts; const k = clamp((ts - 1.1) / 0.3);
    const x = ts < 1.1 ? xAt(alfC.keys, ts) : lerp(-0.6, -0.45, k);
    return <BankFront spin={spinAt(c.t)}>{jarOnShoulder(x, lerp(1.65, 1.2, k), lerp(1.0, 2.3, k), 0)}</BankFront>;
  },
  cast: [mateC, alfC],
};

// ---------- 0:05.4 the spin: round three times inside the glass, spat out, the jar smashes on "that-" ----------
const D_T0 = C_T1, SPIT = 6.22 - D_T0, LAND = E(1) - D_T0;
const alfSpinPos = (t: number) => { const a = spinAt(t) + 0.9; return [Math.sin(a) * 0.5, DOOR.z + Math.cos(a) * 0.5, a] as const; };
const alfD: Actor = {
  who: 'lead', seed: 0.3, pin: pinGlow,
  keys: [
    [0, { x: 0, y: 0.1, z: DOOR.z, face: 'scream', shL: [150, 40], elL: 20, shR: [150, 40], elR: 20, hipL: [30, 15], knL: 40, hipR: [-20, 15], knR: 10, spine: -10 }],
  ],
};
const spinShot: Shot = {
  id: 'spin', t0: D_T0, t1: E(1),
  cam: [[0, cam([0.1, 1.6, 5.3], [-0.2, 1.05, 1.2], 50)], [LAND, cam([-0.1, 1.5, 5.0], [-0.5, 0.9, 1.8], 50), 'lin']],
  set: (c) => {
    const ts = c.ts, t = c.t;
    // Alfie is carried round in a wing, then flung out to the pavement (front left)
    let ax: number, az: number, ay: number, ry: number, rx = 0, rz = 0;
    if (ts < SPIT) { const [x, z, a] = alfSpinPos(t); ax = x; az = z; ay = 0.05 + 0.08 * Math.sin(ts * 18); ry = a + PI / 2; rz = 0.25 * Math.sin(ts * 9); }
    else {
      const u = clamp((ts - SPIT) / (LAND - SPIT)); const [x0, z0] = alfSpinPos(C_T1 + SPIT);
      ax = lerp(x0, -1.5, u); az = lerp(z0, 3.6, u); ay = lerp(0.1, 0.13, u) + 0.9 * Math.sin(PI * u) * (1 - u * 0.4); ry = lerp(1.8, 2 * PI, u); rx = -PI / 2 * u; rz = 0.2 * u;
    }
    const ju = clamp((ts - SPIT) / (LAND - SPIT));
    const jx = ts < SPIT ? ax + 0.2 : lerp(ax + 0.2, -0.75, ju), jz = ts < SPIT ? az : lerp(az, 2.85, ju), jy = ts < SPIT ? 1.0 : 1.0 + 0.8 * Math.sin(PI * ju) - 1.0 * ju;
    const rider: Actor = { ...alfD, keys: [[0, { ...alfD.keys[0][1], x: ax, y: ay, z: az, rx, ry, rz }]] };
    return (
      <BankFront spin={spinAt(t)}>
        {/* Alfie rides the door round its axis, a path pose keys can't express, so he is drawn from the set */}
        <ActorView a={rider} ts={ts} t={t} />
        {ts < LAND - 0.01 ? <group position={[jx, Math.max(0, jy), jz]} rotation={[ju * 5, ts * 9, ju * 3]}><CoinJar /></group> : null}
      </BankFront>
    );
  },
  cast: [],
  onScreen: ['alfie'],
};

// ---------- 0:06.6 the stillness: shards and coins on the pavement, one coin rolls round and topples ----------
const SMASH_AT: [number, number, number] = [-0.75, 0, 2.85];
const F_T0 = E(1), F_T1 = S(2) - 0.05;
const alfSprawl: Actor = {
  who: 'lead', seed: 0.3, pin: pinGlow, noBreath: true,
  keys: [[0, { x: -1.5, y: 0.13, z: 3.6, rx: -PI / 2, ry: 0, rz: 0.2, face: 'shock', shL: [20, 80], elL: 25, shR: [20, 80], elR: 25, hipL: [10, 20], knL: 30, hipR: [-5, 15], knR: 10 }],
    [0.9, { face: 'worried' }]],
};
const still: Shot = {
  id: 'still', t0: F_T0, t1: F_T1,
  cam: [[0, cam([0.35, 0.3, 4.05], [-0.7, 0.06, 2.85], 44)], [F_T1 - F_T0, cam([0.28, 0.27, 3.9], [-0.72, 0.05, 2.85], 44), 'lin']],
  shake: [[0, 1.4]],
  set: (c) => (
    <BankFront spin={spinAt(c.t) * 0 + spinAt(E(1)) + 1.2 * (c.t - E(1)) * Math.exp(-(c.t - E(1)))}>
      <Smash u={prog(c.ts, 0, 0.35, 'out')} at={SMASH_AT} />
      <RollingCoin u={prog(c.ts, 0.05, F_T1 - F_T0 - 0.05, 'lin')} at={[-0.55, 0, 3.15]} />
    </BankFront>
  ),
  cast: [alfSprawl],
};

// ---------- 0:07.8 Mate, still holding the slowing door: "...Bit fast?" ----------
const G_T0 = F_T1, G_T1 = S(3) - 0.1;
const mateSorry: Actor = {
  who: 'mate', seed: 2.2,
  keys: [
    [0, { x: 0.7, z: 1.65, ry: -0.35, face: 'worried', spine: 6, shR: [88, 6], elR: 10, shL: [40, -6], elL: 30, handR: 'open' }],
    [0.25, { shL: [150, 25], elL: 120, twL: 40, handL: 'open', headTilt: -10, face: 'worried', shrug: 0.5 }, 'out'],
    [0.8, { headTilt: -14, face: 'holding', shrug: 0.6 }],
  ],
};
const sorry: Shot = {
  id: 'mate-sorry', t0: G_T0, t1: G_T1,
  cam: [[0, cam([0.15, 1.6, 3.4], [0.65, 1.55, 1.65], 36)], [G_T1 - G_T0, cam([0.25, 1.6, 3.05], [0.65, 1.56, 1.65], 36), 'lin']],
  set: (c) => (
    <BankFront spin={spinAt(E(1)) + 1.2 * (c.t - E(1)) * Math.exp(-(c.t - E(1)))}>
      <Smash u={1} at={SMASH_AT} />
    </BankFront>
  ),
  cast: [mateSorry],
};

// ---------- 0:08.7 the Booth ----------
const producer = (keys: Key3[]): Actor => ({ who: 'producer', seed: 1.7, keys, heldL: () => <Clipboard /> });
const prodBase: Pose3 = { x: 0.85, y: 0, z: -0.15, ry: -0.75, shL: [16, -8], elL: 75, twL: 30, handL: 'fist', shR: [10, 10], elR: 20 };
const narr = (keys: Key3[]): Actor => ({ who: 'narrator', seed: 0.9, keys });
const narrSit: Pose3 = { x: 0, y: 0.04, z: 0.02, ry: PI, sit: true, hipL: [90, 8], knL: 88, hipR: [90, 8], knR: 88, spine: 8, shL: [50, 10], elL: 60, shR: [50, 10], elR: 60, face: 'neutral' };
const narrFrozen: Pose3 = { ...narrSit, spine: -4, shR: [125, 30], elR: 40, handR: 'open', shL: [60, 18], elL: 70, headTilt: 8 }; // stopped mid-gesture
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
  cast: [narr([[0, narrFrozen], [0.5, { ...narrFrozen, headTilt: 12, shR: [122, 30] }], [I_T1 - I_T0, { ...narrFrozen, headTilt: 12, shR: [120, 30] }]]), producer([[0, { ...prodBase, face: 'worried', spine: 12 }]])],
};
const J_T0 = I_T1, J_T1 = E(5) + 0.25;
const booth3: Shot = {
  id: 'booth-prod2', t0: J_T0, t1: J_T1,
  cam: [[0, cam([0.4, 1.55, 1.22], [0.84, 1.45, -0.15], 36)], [J_T1 - J_T0, cam([0.52, 1.55, 0.86], [0.84, 1.46, -0.15], 36), 'lin']],
  shake: [[0.25, 0.22]],
  set: () => <Booth />,
  cast: [producer([
    [0, { ...prodBase, face: 'shock', spine: 4 }],
    [0.25, { face: 'scream', shrug: 0.5 }],
    [1.2, { face: 'shock', shrug: 0.2 }],
    [1.4, { shR: [108, 20], elR: 6, handR: 'point', face: 'scream', headTurn: -10 }, 'out'],
  ]), narr([[0, narrFrozen]])],
};

// ---------- 0:14.4 the pin fires on the pavement: glow, the white crack, the switch ----------
const K_T0 = J_T1, K_T1 = S(6) - 0.05, CRACK = 0.42;
const alfPin: Actor = { ...alfSprawl, keys: [[0, { ...alfSprawl.keys[0][1], face: 'worried' }], [CRACK, { face: 'shock' }]], pin: (ts) => (ts < CRACK ? 0.3 + 2 * ts : 0.75 + 0.25 * Math.sin(ts * 9)) };
const pinShot: Shot = {
  id: 'pin', t0: K_T0, t1: K_T1,
  cam: [[0, cam([-1.72, 3.0, 2.78], [-1.75, 0.0, 2.55], 50)], [K_T1 - K_T0, cam([-1.86, 1.15, 2.44], [-1.87, 0.2, 2.3], 40), 'out']],
  crack: CRACK,
  sw: (ts) => (ts < CRACK ? 0 : 1),
  shake: [[CRACK, 0.8]],
  set: (c) => (
    <BankFront sw={c.sw} spin={spinAt(E(1)) + 1.2}>
      <Smash u={1} at={SMASH_AT} />
    </BankFront>
  ),
  cast: [alfPin],
};

// ---------- 0:15.3 the what-if bank hall: Alfie on his knees scooping coins into the taped jar; savers clutch jars ----------
const M_T0 = K_T1, M_T1 = S(7) - 0.1;
const sglow = (ts: number) => 0.65 + 0.35 * Math.sin(ts * 7);
const alfScoop: Actor = {
  who: 'lead', seed: 0.3, pin: sglow,
  keys: [
    [0, { x: -0.25, y: -0.3, z: 1.1, ry: 0.35, crouch: 1, spine: 48, shL: [70, 20], elL: 40, shR: [70, -10], elR: 40, handL: 'open', handR: 'open', face: 'worried', headNod: -18 }],
    [0.4, { shL: [55, 25], elL: 70, shR: [85, -15], elR: 20 }], [0.8, { shL: [80, 20], elL: 25, shR: [55, -5], elR: 70 }],
    [1.2, { shL: [55, 25], elL: 70, shR: [85, -15], elR: 20, headNod: -6, face: 'disbelief', headTurn: 20 }],
    [1.6, { spine: 30, headNod: -16, headTurn: 35 }],
    [M_T1 - M_T0, { spine: 26, headNod: -18, headTurn: 40, face: 'disbelief' }],
  ],
};
const SAVER_POS: [number, number, number, number][] = [[-1.15, -0.55, 0.15, 0], [0.25, -1.25, -0.2, 1], [1.35, -0.6, -0.45, 2], [-0.35, -1.6, 0.1, 0]];
const savers: Actor[] = SAVER_POS.map(([x, z, ry, li], i) => ({
  who: `saver${i}`, look: SAVERS[li], seed: 5 + i, mute: true,
  keys: [[0, { x, z, ry, shL: [40, -22], elL: 85, shR: [40, -22], elR: 85, twL: 10, twR: 10, handL: 'open', handR: 'open', face: i % 2 ? 'worried' : 'neutral', headTurn: i % 2 ? 15 : -10 }],
    [2 + i * 0.3, { headTurn: i % 2 ? -10 : 12, face: i % 2 ? 'neutral' : 'worried' }]],
}));
const saverJars = SAVER_POS.map(([x, z, ry], i) => (
  <group key={i} position={[x + 0.32 * Math.sin(ry), 0.98 + (SAVERS[SAVER_POS[i][3]].height - 1.7) * 0.5, z + 0.32 * Math.cos(ry)]} rotation={[0, ry, 0]}><CoinJar s={0.62} heap={false} /></group>
));
const hall: Shot = {
  id: 'hall-scoop', t0: M_T0, t1: M_T1,
  cam: [[0, cam([1.6, 1.05, 3.4], [-0.2, 0.55, 0.75], 46)], [M_T1 - M_T0, cam([1.35, 1.0, 3.1], [-0.2, 0.52, 0.75], 46), 'lin']],
  sw: 1,
  set: (c) => (
    <BankHall sw={1}>
      <group position={[0.18, 0, 1.45]}><CoinJar tape fill={0.35 + 0.08 * prog(c.ts, 0, 2)} heap={false} /></group>
      {[[-0.3, 1.6], [0.05, 1.75], [-0.6, 1.4], [0.35, 1.9], [-0.1, 1.95], [0.5, 1.3]].map(([x, z], i) => (
        <group key={i} position={[x, 0.004, z]} rotation={[0, i, 0]}><Coin s={1.7} /></group>
      ))}
      {saverJars}
    </BankHall>
  ),
  cast: [alfScoop, ...savers],
};

// ---------- 0:17.7 Mate squints past the counter at the shelf: "Is that... your nan's name?" ----------
const N_T0 = M_T1, N_T1 = E(7) + 0.3;
const mateSquint: Actor = {
  who: 'mate', seed: 2.2,
  keys: [
    [0, { x: 0.45, z: -0.75, ry: PI - 0.15, face: 'thinking', spine: 8, headNod: -4, shR: [96, -4], elR: 8, handR: 'point', shL: [10, 8], elL: 20 }],
    [0.5, { spine: 12, headNod: -8 }],
    [1.1, { face: 'disbelief', headTilt: 8, spine: 14 }],
    [N_T1 - N_T0, { spine: 15 }],
  ],
};
const squint: Shot = {
  id: 'mate-squint', t0: N_T0, t1: N_T1,
  cam: [[0, cam([0.15, 1.75, -2.75], [0.4, 1.55, -0.75], 36)], [N_T1 - N_T0, cam([0.2, 1.72, -2.45], [0.4, 1.56, -0.75], 36), 'lin']],
  sw: 1,
  set: () => <BankHall sw={1} />,
  cast: [mateSquint],
};

// ---------- 0:19.7 push in on the jar labelled NAN (the hold before "And what if Britain...") ----------
const O_T0 = N_T1, O_T1 = S(8) - 0.05;
const NAN_JAR_X = -1.95 + 2 * 0.56; // shelf row 0, slot 2 (SHELF_LABELS[2] = 'NAN')
const nanJar: Shot = {
  id: 'nan-jar', t0: O_T0, t1: O_T1,
  cam: [[0, cam([NAN_JAR_X + 0.25, 1.2, HALL.shelfZ + 1.35], [NAN_JAR_X, 1.02, HALL.shelfZ], 34)], [O_T1 - O_T0, cam([NAN_JAR_X + 0.08, 1.12, HALL.shelfZ + 0.75], [NAN_JAR_X, 1.03, HALL.shelfZ], 34), 'io']],
  sw: 1,
  set: () => <BankHall sw={1} />,
  cast: [],
};

export const COLD_OPEN: Shot[] = [walkA, approach, shove, spinShot, still, sorry, booth1, booth2, booth3, pinShot, hall, squint, nanJar];
export const TEST_END = O_T1;

export const ep22 = makeEpisode3({
  id: 'ep22',
  shots: [...COLD_OPEN, ...ACT2],
  words: words as any,
  total: TOTAL,
  title: TITLE,
  blackAt: BLACK_AT,
  hook: { node: <>Wait, are your <span style={{ color: '#FFD43B' }}>savings</span> lent out?</>, until: 3.0 },
});
