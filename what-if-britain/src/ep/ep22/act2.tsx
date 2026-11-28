// EP22 Typed Money, act 2: the title, the ladder (counter, vault, rainy run on the bank), the twist at the keyboard and
// the cliffhanger. Timings follow src/episodes/ep22/lines.json via S(n) / E(n) (same anchors as audio/ep22_sound.py).
import React from 'react';
import words from '../../episodes/ep22/words.json';
import { cam, Shot, Actor, ActorView, Key3, Pose3, FactCard, prog, lerp, clamp } from '../kit3';
import { Cane } from '../ep21/sets2';
import { BankFront, BankHall, CoinJar, Vault, Umbrella, Rain, MANAGER, BUILDER, SAVERS, COMPUTER, DOOR, VAULT } from './sets';
import { S, E, O_T1 } from './shared';

const PI = Math.PI;
const W = words as { text: string; start: number }[];
const wordAt = (txt: string, after = 0) => W.find((w) => w.text.replace(/\*/g, '').startsWith(txt) && w.start >= after)!.start;
const glow = (ts: number) => 0.65 + 0.35 * Math.sin(ts * 7);
const mgr = (keys: Key3[], seed = 6.1): Actor => ({ who: 'manager', look: MANAGER, seed, keys });
const HAND_JAR: Pose3 = { shL: [52, -16], elL: 70, shR: [52, -16], elR: 70, twL: 10, twR: 10, handL: 'open', handR: 'open' };

// ================= 0:22.2 WHAT IF BRITAIN: the hall, wide, then a push towards the counter =================
export const TITLE = { at: wordAt("Britain's", 22), until: wordAt("Britain's", 22) + 1.9 };
const P1_T1 = 23.95, P2_T1 = S(9) - 1.7;
const alfHall: Actor = { who: 'lead', seed: 0.3, pin: glow, keys: [[0, { x: -0.3, z: 0.6, ry: PI * 0.9, ...HAND_JAR, face: 'disbelief', headTurn: 20 }], [1.4, { headTurn: -15, face: 'worried' }]] };
const alfJar = (x: number, z: number, ry: number) => <group position={[x + 0.35 * Math.sin(ry), 0.98, z + 0.35 * Math.cos(ry)]} rotation={[0, ry, 0]}><CoinJar s={0.62} tape fill={0.45} heap={false} /></group>;
const mateHall: Actor = { who: 'mate', seed: 2.2, keys: [[0, { x: 0.65, z: 0.9, ry: PI * 1.1, face: 'thinking', shL: [10, 8], elL: 20, shR: [10, 8], elR: 20, headTurn: -20 }], [1.5, { headTurn: 15 }]] };
const SAVER_Q: [number, number, number, number][] = [[-1.6, -0.4, 0.4, 0], [1.4, -0.2, -0.3, 2], [-0.9, -1.2, 0.1, 1], [1.9, -1.0, -0.5, 0]];
const saverActs = SAVER_Q.map(([x, z, ry, li], i): Actor => ({ who: `saver${i}`, look: SAVERS[li], seed: 5 + i, mute: true,
  keys: [[0, { x, z, ry, ...HAND_JAR, face: i % 2 ? 'worried' : 'neutral', headTurn: i % 2 ? 12 : -10 }], [2 + i * 0.4, { headTurn: i % 2 ? -12 : 10 }]] }));
const saverJars = SAVER_Q.map(([x, z, ry, li], i) => (
  <group key={i} position={[x + 0.32 * Math.sin(ry), 0.98 + (SAVERS[li].height - 1.7) * 0.5, z + 0.32 * Math.cos(ry)]} rotation={[0, ry, 0]}><CoinJar s={0.62} heap={false} /></group>
));
const mgrWait = mgr([[0, { x: 0, z: -2.65, ry: 0, face: 'smug', shL: [30, -10], elL: 80, shR: [30, -10], elR: 80, twL: 50, twR: 50, handL: 'fist', handR: 'fist' }]]);
const titleWide: Shot = {
  id: 'title-wide', t0: O_T1, t1: P1_T1, sw: 1,
  cam: [[0, cam([0.4, 1.3, 4.6], [0, 1.1, -0.5], 50)], [P1_T1 - O_T1, cam([0.3, 2.3, 4.3], [0, 1.0, -1.0], 50), 'io']],
  set: () => <BankHall>{alfJar(-0.3, 0.6, PI * 0.9)}{saverJars}</BankHall>,
  cast: [alfHall, mateHall, ...saverActs, mgrWait],
};
const titlePush: Shot = {
  id: 'title-push', t0: P1_T1, t1: P2_T1, sw: 1,
  cam: [[0, cam([-0.2, 1.55, 0.9], [0, 1.45, -2.65], 40)], [P2_T1 - P1_T1, cam([-0.1, 1.55, -0.6], [0, 1.5, -2.65], 40), 'io']],
  set: () => <BankHall />,
  cast: [mgr([[0, { x: 0, z: -2.65, ry: 0, face: 'smug', shL: [30, -10], elL: 80, shR: [30, -10], elR: 80, twL: 50, twR: 50, handL: 'fist', handR: 'fist' }], [1.0, { headNod: -6, headTilt: 6 }]])],
};

// ================= 0:25.7 BEAT 1, the counter: the jar goes straight to the Builder's van loan =================
const Q1_T0 = P2_T1, Q1_T1 = S(9), SLAP = 0.95;
const JAR_Y = 1.045, JAR_Z = -2.1;
const alfCounter = (keys: Key3[]): Actor => ({ who: 'lead', seed: 0.3, pin: glow, keys });
const plonk: Shot = {
  id: 'plonk', t0: Q1_T0, t1: Q1_T1, sw: 1,
  cam: [[0, cam([0.85, 1.6, -0.35], [-0.05, 1.25, -2.3], 42)], [Q1_T1 - Q1_T0, cam([0.7, 1.58, -0.6], [-0.05, 1.22, -2.3], 42), 'lin']],
  shake: [[0.35, 0.4], [SLAP, 0.3]],
  set: (c) => {
    const k = prog(c.ts, 0, 0.35, 'in');
    return (
      <BankHall>
        <group position={[0, lerp(1.2, JAR_Y, k), lerp(-1.75, JAR_Z, k)]}><CoinJar s={0.62} tape fill={0.45} heap={false} label={c.ts > SLAP ? 'ALFIE' : undefined} /></group>
      </BankHall>
    );
  },
  cast: [
    alfCounter([[0, { x: 0, z: -1.4, ry: PI, ...HAND_JAR, shL: [70, -12], elL: 40, shR: [70, -12], elR: 40, spine: 14, face: 'happy' }], [0.35, { spine: 18 }], [0.7, { ...HAND_JAR, shL: [20, 6], elL: 20, shR: [20, 6], elR: 20, spine: 4, face: 'smug' }]]),
    mgr([[0, { x: 0, z: -2.65, ry: 0, face: 'smug', shL: [30, -10], elL: 80, shR: [30, -10], elR: 80, twL: 50, twR: 50 }],
      [SLAP - 0.25, { shR: [120, 10], elR: 40, handR: 'open', spine: 6 }, 'out'], [SLAP, { shR: [70, 6], elR: 30, spine: 16 }, 'in'], [SLAP + 0.5, { shR: [60, 10], elR: 40 }]]),
  ],
};
const Q2_T1 = S(10) - 0.05;
const slideX = (ts: number) => lerp(0, COMPUTER.x - 0.3, prog(ts, 0.1, 0.9, 'out'));
const slide: Shot = {
  id: 'slide', t0: Q1_T1, t1: Q2_T1, sw: 1,
  cam: [[0, cam([0.6, 1.75, 1.0], [0.75, 1.15, -2.1], 46)], [Q2_T1 - Q1_T1, cam([0.75, 1.7, 0.7], [0.85, 1.15, -2.1], 46), 'lin']],
  set: (c) => <BankHall><group position={[slideX(c.ts), JAR_Y, JAR_Z]}><CoinJar s={0.62} tape fill={0.45} heap={false} label="ALFIE" /></group></BankHall>,
  cast: [
    alfCounter([[0, { x: 0, z: -1.4, ry: PI - 0.3, face: 'shock', shR: [80, 30], elR: 10, handR: 'open', shL: [10, 8], elL: 20 }], [0.4, { x: 0.35, face: 'angry', shR: [95, 20], elR: 0, spine: 12, headTurn: -10 }, 'out'], [1.6, { x: 0.45, face: 'angry', spine: 14 }]]),
    mgr([[0, { x: 0, z: -2.65, ry: 0, shR: [70, 6], elR: 30, face: 'smug', spine: 10 }], [0.6, { x: 0.6, shR: [70, 40], elR: 10, spine: 12, handR: 'open' }, 'out'], [1.6, { x: 0.7, shR: [30, 10], elR: 40, face: 'smug', spine: 2 }]]),
    { who: 'builder', look: BUILDER, seed: 7.7, keys: [[0, { x: 1.55, z: -1.45, ry: PI + 0.25, face: 'happy', ...HAND_JAR, shL: [60, -10], elL: 60, shR: [60, -10], elR: 60 }]] },
    { who: 'mate', seed: 2.2, keys: [[0, { x: -0.75, z: -0.9, ry: PI - 0.5, face: 'disbelief', shL: [10, 8], elL: 20, shR: [10, 8], elR: 20, headTurn: -25 }]] },
  ],
};
const Q3_T1 = S(11) - 0.1;
const smug: Shot = {
  id: 'mgr-smug', t0: Q2_T1, t1: Q3_T1, sw: 1,
  cam: [[0, cam([0.75, 1.62, -1.25], [0.68, 1.52, -2.65], 34)], [Q3_T1 - Q2_T1, cam([0.73, 1.6, -1.55], [0.68, 1.53, -2.65], 34), 'lin']],
  set: () => <BankHall />,
  cast: [mgr([[0, { x: 0.7, z: -2.65, ry: 0, face: 'smug', shL: [30, -10], elL: 80, shR: [30, -10], elR: 80, twL: 50, twR: 50, headTilt: 6 }], [0.7, { headTilt: -4, headNod: -8, spine: -4 }], [1.4, { face: 'happy', headNod: -4 }]])],
};
const Q4_T1 = S(12) - 0.2;
const builderGo: Shot = {
  id: 'builder', t0: Q3_T1, t1: Q4_T1, sw: 1,
  cam: [[0, cam([1.1, 1.55, -0.15], [1.65, 1.35, -1.5], 40)], [Q4_T1 - Q3_T1, cam([0.8, 1.55, 0.6], [2.3, 1.2, -1.1], 46), 'io']],
  set: (c) => {
    const ts = c.ts, x = lerp(1.55, 2.75, prog(ts, 1.15, 2.4, 'in')), z = lerp(-1.45, -0.95, prog(ts, 1.15, 2.4, 'in'));
    const hug = ts > 0.15;
    return (
      <BankHall>
        {hug ? <group position={[x + 0.28 * Math.sin(ts < 1.0 ? 0.2 : 1.2), 1.0, z + 0.28 * Math.cos(ts < 1.0 ? 0.2 : 1.2)]} rotation={[0, 0.4, 0]}><CoinJar s={0.62} tape fill={0.45} heap={false} label="ALFIE" /></group>
          : <group position={[COMPUTER.x - 0.3, JAR_Y, JAR_Z]}><CoinJar s={0.62} tape fill={0.45} heap={false} label="ALFIE" /></group>}
      </BankHall>
    );
  },
  cast: [{ who: 'builder', look: BUILDER, seed: 7.7, keys: [
    [0, { x: 1.55, z: -1.45, ry: PI, face: 'happy', shL: [80, -10], elL: 30, shR: [80, -10], elR: 30 }],
    [0.15, { ry: 0.2, ...HAND_JAR, shL: [50, -24], elL: 95, shR: [50, -24], elR: 95, face: 'laugh', spine: -6 }, 'back'],
    [1.0, { ry: 1.2, face: 'happy', headTurn: -40 }],
    ...([1.15, 1.45, 1.75, 2.05, 2.35].map((t, i): Key3 => [t, { x: lerp(1.55, 2.75, (t - 1.15) / 1.25), z: lerp(-1.45, -0.95, (t - 1.15) / 1.25), hipL: [i % 2 ? 30 : -25, 3], knL: i % 2 ? 10 : 40, hipR: [i % 2 ? -25 : 30, 3], knR: i % 2 ? 40 : 10, bounce: 0.02 * (i % 2) }, 'lin'])),
  ] }],
};

// ================= 0:33.4 BEAT 2, the vault: the door flattens Mate, the vault is nearly empty =================
const R1_T0 = Q4_T1, R1_T1 = 34.3, OPEN0 = 0.15, OPEN1 = 0.7;
const doorOpen = (ts: number) => prog(ts, OPEN0, OPEN1, 'in');
const mateOnDoor = (open: number): Pose3 => { // Mate holds the wheel and is carried round to the wall
  const a = open * PI * 0.62, hx = VAULT.r + 0.05;
  const lx = -(VAULT.r + 0.05), lz = 0.55;
  return { x: hx + lx * Math.cos(a) + lz * Math.sin(a), z: 0.12 - lx * Math.sin(a) + lz * Math.cos(a), ry: a + PI };
};
const vaultHeave: Shot = {
  id: 'vault-heave', t0: R1_T0, t1: R1_T1, sw: 1,
  cam: [[0, cam([-1.7, 1.5, 3.4], [0.2, 1.15, 0.2], 46)], [R1_T1 - R1_T0, cam([-1.55, 1.45, 3.1], [0.4, 1.15, 0.2], 46), 'lin']],
  shake: [[OPEN1, 1.0]],
  set: (c) => {
    const o = doorOpen(c.ts); const p = mateOnDoor(o);
    const mate: Actor = { who: 'mate', seed: 2.2, keys: [[0, { ...p, y: 0, face: c.ts < OPEN0 ? 'holding' : c.ts < OPEN1 ? 'shock' : 'holding', spine: c.ts < OPEN0 ? -18 : 0, shL: [95, -10], elL: 20, shR: [95, -10], elR: 20, handL: 'fist', handR: 'fist', crouch: c.ts < OPEN0 ? 0.25 : 0 }]] };
    return <Vault open={o}>{c.ts < OPEN1 + 0.05 ? <ActorView a={mate} ts={c.ts} t={c.t} /> : null}</Vault>;
  },
  cast: [{ who: 'lead', seed: 0.3, pin: glow, keys: [[0, { x: -1.2, z: 1.1, ry: 0.5, face: 'worried', shL: [10, 8], elL: 20, shR: [10, 8], elR: 20 }], [OPEN1, { face: 'shock', shrug: 0.4 }]] }],
  onScreen: ['mate'],
};
const R2_T1 = S(13) - 0.05;
const vaultReveal: Shot = {
  id: 'vault-reveal', t0: R1_T1, t1: R2_T1, sw: 1,
  cam: [[0, cam([0.35, 1.55, 2.2], [0, 1.2, -5], 50)], [R2_T1 - R1_T1, cam([0.25, 1.5, 1.4], [0, 1.15, -5], 50), 'lin']],
  set: () => <Vault open={1} />,
  cast: [{ who: 'lead', seed: 0.3, pin: glow, keys: [[0, { x: -0.15, z: 0.35, ry: PI, face: 'shock', shL: [30, 30], elL: 30, shR: [30, 30], elR: 30 }]] }],
};
const R3_T1 = wordAt('hundred', 35);
const board: Shot = {
  id: 'vault-board', t0: R2_T1, t1: R3_T1, sw: 1,
  cam: [[0, cam([-1.45, 1.95, -2.35], [2.97, 1.95, -2.6], 40)], [R3_T1 - R2_T1, cam([-1.05, 1.95, -2.4], [2.97, 1.95, -2.6], 40), 'lin']],
  set: () => <Vault open={1} />,
  cast: [],
  onScreen: ['manager'],
};
const R4_T1 = S(14) - 0.1;
const whisper: Shot = {
  id: 'vault-whisper', t0: R3_T1, t1: R4_T1, sw: 1,
  cam: [[0, cam([1.55, 1.6, -0.2], [1.55, 1.45, -2.4], 44)], [R4_T1 - R3_T1, cam([1.55, 1.58, -0.5], [1.55, 1.45, -2.4], 44), 'lin']],
  set: () => <Vault open={1} />,
  cast: [
    mgr([[0, { x: 1.85, z: -2.45, ry: -PI / 2 + 0.45, face: 'worried', spine: 10, shR: [80, 30], elR: 110, twR: 30, handR: 'open', headTilt: 10 }], [1.0, { face: 'sad', headNod: 6 }]]),
    { who: 'lead', seed: 0.3, pin: glow, keys: [[0, { x: 1.25, z: -2.35, ry: PI / 2 - 0.45, face: 'disbelief', shL: [10, 8], elL: 20, shR: [10, 8], elR: 20 }], [0.9, { face: 'shock' }]] },
  ],
};
const R5_T1 = S(15) - 1.0;
const matePeel: Shot = {
  id: 'mate-peel', t0: R4_T1, t1: R5_T1, sw: 1,
  cam: [[0, cam([2.75, 1.65, 2.75], [2.2, 1.45, 0.35], 40)], [R5_T1 - R4_T1, cam([2.65, 1.62, 2.35], [2.2, 1.45, 0.35], 40), 'lin']],
  set: () => <Vault open={1} />,
  cast: [{ who: 'mate', seed: 2.2, keys: [
    [0, { x: 2.2, z: 0.32, ry: PI, face: 'holding', spine: -6, shL: [150, 50], elL: 10, shR: [150, 50], elR: 10 }],
    [0.45, { z: 0.42, spine: 8, rx: 0.12 }, 'out'],
    [0.75, { ry: -0.25, face: 'disbelief', shL: [20, 20], elL: 20, shR: [20, 20], elR: 20, rx: 0, spine: 4, headTilt: 10 }, 'back'],
    [1.8, { ry: -0.15, headTilt: -8, face: 'thinking' }],
  ] }],
};

// ================= 0:40.4 BEAT 3, the rainy high street: a run on the bank =================
const RAIN = (c: { t: number }) => <Rain t={c.t} />;
const QUEUE: [number, number, string, number][] = [[1.2, 2.15, '#B3262E', 0], [1.95, 2.2, '#1F2F4F', 1], [2.7, 2.1, '#2E6B4F', 2], [3.45, 2.2, '#7A3B2E', 0], [4.2, 2.15, '#C9A43A', 1], [4.95, 2.2, '#3A5E8C', 2]];
const queueActs = QUEUE.map(([x, z, , li], i): Actor => ({ who: `q${i}`, look: SAVERS[li], seed: 9 + i, mute: true,
  keys: [[0, { x, z, ry: -PI / 2 + 0.15, shR: [45, -10], elR: 80, twR: 20, handR: 'fist', shL: [10, 6], elL: 20, face: i % 2 ? 'angry' : 'worried', headTurn: i % 2 ? -15 : 10 }],
    [0.8 + 0.2 * i, { shL: [70, 10], elL: 30, handL: 'fist', face: 'angry' }], [1.6 + 0.2 * i, { shL: [10, 6], elL: 20 }]] }));
const umbrellas = QUEUE.map(([x, z, col, li], i) => (
  <group key={i} position={[x + 0.12, SAVERS[li].height * 0.62, z + 0.05]} rotation={[0, 0, 0.12]}><Umbrella c={col} /></group>
));
const NAN_AT = { x: 0.25, z: 2.45 };
const nanBang = (keys: Key3[]): Actor => ({ who: 'nan', seed: 3.3, keys, heldR: () => <Cane /> });
const DRUM_SPIN = PI / 4;
const S1_T1 = S(15) - 0.05;
const rainWide: Shot = {
  id: 'rain-wide', t0: R5_T1, t1: S1_T1, sw: 1,
  cam: [[0, cam([4.6, 2.6, 7.2], [1.6, 1.0, 1.6], 46)], [S1_T1 - R5_T1, cam([4.2, 2.4, 6.6], [1.5, 1.0, 1.6], 46), 'lin']],
  set: () => <BankFront sw={1} rain={1} spin={DRUM_SPIN}>{umbrellas}</BankFront>,
  overlay: RAIN,
  cast: [...queueActs, nanBang([[0, { ...NAN_AT, ry: PI, face: 'angry', shR: [150, 10], elR: 20 }], [0.3, { shR: [95, 10], elR: 10 }, 'in'], [0.6, { shR: [150, 10], elR: 20 }]])],
};
const S2_T1 = S(16) - 0.1;
const BANGS = [0.25, 0.75, 1.3];
const nanShot: Shot = {
  id: 'nan-bang', t0: S1_T1, t1: S2_T1, sw: 1,
  cam: [[0, cam([-1.75, 1.3, 1.95], [-0.1, 1.05, 2.25], 44)], [S2_T1 - S1_T1, cam([-1.55, 1.28, 2.0], [-0.1, 1.05, 2.25], 44), 'lin']],
  shake: BANGS.map((b) => [b, 0.35] as [number, number]),
  set: () => <BankFront sw={1} rain={1} spin={DRUM_SPIN}>{umbrellas}</BankFront>,
  overlay: RAIN,
  cast: [nanBang([
    [0, { ...NAN_AT, ry: PI + 0.6, face: 'angry', shR: [150, 10], elR: 30, shL: [30, 20], elL: 60 }],
    ...BANGS.flatMap((b): Key3[] => [[b - 0.18, { shR: [165, 10], elR: 35, spine: -6 }, 'out'], [b, { shR: [100, 10], elR: 5, spine: 10 }, 'in']]),
    [1.7, { shR: [120, 10], elR: 30, spine: 2, headTurn: -20 }],
  ]), ...queueActs.slice(0, 3)],
};
const S3_T1 = S(17) - 0.1, SLAM0 = 0.15, SLAM1 = 0.55;
const shutterShot: Shot = {
  id: 'shutter', t0: S2_T1, t1: S3_T1, sw: 1,
  cam: [[0, cam([1.7, 1.55, 4.3], [0, 1.25, 1.4], 44)], [S3_T1 - S2_T1, cam([1.55, 1.5, 3.95], [0, 1.22, 1.4], 44), 'lin']],
  shake: [[SLAM1, 1.2]],
  set: (c) => <BankFront sw={1} rain={1} spin={DRUM_SPIN} shutter={prog(c.ts, SLAM0, SLAM1, 'in')}>{umbrellas}</BankFront>,
  overlay: RAIN,
  cast: [
    mgr([[0, { x: 0, z: DOOR.z + 0.55, ry: 0, face: 'scream', shL: [170, 15], elL: 10, shR: [170, 15], elR: 10, handL: 'fist', handR: 'fist' }], [SLAM1, { shL: [120, 15], shR: [120, 15], crouch: 0.4, spine: 10 }, 'in'], [SLAM1 + 0.05, { vis: 0 }]]),
    nanBang([[0, { ...NAN_AT, ry: PI, face: 'angry', shR: [140, 10], elR: 20 }], [SLAM1, { z: NAN_AT.z + 0.15, face: 'shock', spine: -12, shR: [60, 20] }, 'out'], [S3_T1 - S2_T1, { face: 'angry' }]]),
    ...queueActs.slice(0, 2),
  ],
};
const S4_T1 = 47.0;
const alfRain: Shot = {
  id: 'alf-rain', t0: S3_T1, t1: S4_T1, sw: 1,
  cam: [[0, cam([1.45, 1.62, 4.3], [1.1, 1.5, 2.75], 36)], [S4_T1 - S3_T1, cam([1.4, 1.6, 3.85], [1.1, 1.52, 2.75], 36), 'lin']],
  set: () => <BankFront sw={1} rain={1} spin={DRUM_SPIN} shutter={1}>{umbrellas}</BankFront>,
  overlay: RAIN,
  cast: [{ who: 'lead', seed: 0.3, pin: glow, keys: [[0, { x: 1.1, z: 2.75, ry: 0.15, face: 'worried', ...{ shL: [22, 30], elL: 75, shR: [22, 30], elR: 75 }, shrug: 0.6, headTilt: -6 }], [0.6, { face: 'sad', headTilt: 6, shrug: 0.8 }], [1.4, { face: 'worried', headTurn: 20 }]] }],
};

// ================= 0:47.0 THE TWIST: behind the shutter, at the keyboard =================
const KEYS: Pose3 = { shL: [55, -20], elL: 75, shR: [55, -20], elR: 75, handL: 'open', handR: 'open' };
const MGR_AT = { x: 1.45, z: -1.45 };
const typing = (t0: number, t1: number, base: Pose3): Key3[] => Array.from({ length: Math.max(2, Math.round((t1 - t0) / 0.12)) }, (_, i): Key3 => [t0 + i * 0.12, { ...base, elL: i % 2 ? 70 : 82, elR: i % 2 ? 84 : 70 }]);
const TYPE0 = 48.95, TYPE1 = 49.4;                 // the £20,000 is typed in
const DEL0 = wordAt('vanishes', 54) - 0.25, DEL1 = wordAt('vanishes', 54) + 0.1; // and deleted again
const balance = (t: number) => {
  const up = '£20,000';
  if (t < TYPE0) return 'BUILDER|£0';
  if (t < TYPE1) return `BUILDER|${up.slice(0, Math.max(1, Math.ceil(((t - TYPE0) / (TYPE1 - TYPE0)) * up.length)))}`;
  if (t < DEL0) return `BUILDER|${up}`;
  if (t < DEL1) return `BUILDER|${up.slice(0, Math.max(1, up.length - Math.ceil(((t - DEL0) / (DEL1 - DEL0)) * (up.length - 1))))}`;
  return 'BUILDER|£0';
};
const REAL = [TYPE1 - 0.05, TYPE1 + 0.3] as const;  // the split second the grade flickers to the real Britain
const swTwist = (t: number) => (t >= REAL[0] && t < REAL[1] ? 0 : 1);
const twistSet = (dim = 1) => (c: { t: number }) => <BankHall sw={swTwist(c.t)} dim={dim} screen={balance(c.t)} />;
const mgrType = (keys: Key3[]) => mgr([[0, { ...MGR_AT, ry: PI, ...KEYS, spine: 12, face: 'neutral' }], ...keys]);
const alfTwist = (keys: Key3[]): Actor => ({ who: 'lead', seed: 0.3, pin: glow, keys: [[0, { x: 2.15, z: -1.3, ry: PI + 0.45, face: 'worried', shL: [10, 8], elL: 20, shR: [10, 8], elR: 20 }], ...keys] });
const mateTwist = (keys: Key3[]): Actor => ({ who: 'mate', seed: 2.2, keys: [[0, { x: 0.65, z: -1.15, ry: PI - 0.45, face: 'thinking', shL: [10, 8], elL: 20, shR: [10, 8], elR: 20 }], ...keys] });
const T1_T1 = 48.6;
const twistWide: Shot = {
  id: 'twist-wide', t0: S4_T1, t1: T1_T1, sw: 1,
  cam: [[0, cam([1.0, 1.75, -2.75], [1.5, 1.35, -1.2], 46)], [T1_T1 - S4_T1, cam([1.15, 1.7, -2.7], [1.5, 1.38, -1.25], 42), 'lin']],
  set: (c) => twistSet()(c),
  cast: [
    mgr([[0, { x: 1.9, z: -0.7, ry: PI * 0.8, face: 'worried', shR: [70, -20], elR: 30, handR: 'fist' }], [0.7, { ...MGR_AT, ry: PI, spine: 8, face: 'worried', shR: [40, 0], elR: 40 }, 'io'], [1.0, { ...KEYS, spine: 12 }], ...typing(1.1, 1.6, { ...KEYS, spine: 12 })]),
    alfTwist([[0, { x: 2.5, z: -0.5 }], [0.75, { x: 2.15, z: -1.3 }, 'io'], [1.2, { face: 'disbelief' }]]),
    mateTwist([]),
  ],
};
const T2_T1 = 50.3;
const screenUp: Shot = {
  id: 'screen-up', t0: T1_T1, t1: T2_T1,
  sw: (ts) => swTwist(T1_T1 + ts),
  cam: [[0, cam([1.95, 1.5, -0.65], [COMPUTER.x, 1.3, -1.96], 34)], [T2_T1 - T1_T1, cam([1.9, 1.48, -0.85], [COMPUTER.x, 1.3, -1.96], 34), 'lin']],
  set: (c) => twistSet()(c),
  cast: [mgrType(typing(0.1, TYPE1 - T1_T1 + 0.05, { ...KEYS, spine: 12 }))],
  overlay: (c) => <FactCard t={c.t} at={TYPE1 + 0.35} until={E(19) + 0.6} source="Bank of England">A bank loan creates brand-new money</FactCard>,
  onScreen: ['manager'],
};
const T3_T1 = S(20) - 0.05;
const alfAsk: Shot = {
  id: 'alf-ask', t0: T2_T1, t1: T3_T1, sw: 1,
  cam: [[0, cam([2.15, 1.62, -2.65], [2.2, 1.55, -1.3], 34)], [T3_T1 - T2_T1, cam([2.17, 1.6, -2.4], [2.2, 1.55, -1.3], 34), 'lin']],
  set: (c) => twistSet()(c),
  cast: [alfTwist([[0, { ry: PI - 0.1, face: 'disbelief', ...{ shL: [22, 30], elL: 75, shR: [22, 30], elR: 75 } }], [0.5, { face: 'shock' }]])],
  overlay: (c) => <FactCard t={c.t} at={TYPE1 + 0.35} until={E(19) + 0.6} source="Bank of England">A bank loan creates brand-new money</FactCard>,
};
const T4_T1 = S(21) - 0.1;
const typedIt: Shot = {
  id: 'typed-it', t0: T3_T1, t1: T4_T1, sw: 1,
  cam: [[0, cam([1.3, 1.62, -2.6], [1.45, 1.55, -1.45], 32)], [T4_T1 - T3_T1, cam([1.33, 1.62, -2.35], [1.45, 1.56, -1.45], 32), 'lin']],
  set: (c) => twistSet()(c),
  cast: [mgr([[0, { ...MGR_AT, ry: PI + 0.35, ...KEYS, spine: 4, face: 'smug', headTilt: 8 }], [0.3, { shR: [60, 30], elR: 100, twR: 30, handR: 'point', face: 'smug' }, 'out']])],
};
const T5_T1 = S(22) - 0.1;
const mateDo: Shot = {
  id: 'mate-do', t0: T4_T1, t1: T5_T1, sw: 1,
  cam: [[0, cam([0.8, 1.65, -2.55], [0.7, 1.6, -1.15], 34)], [T5_T1 - T4_T1, cam([0.78, 1.64, -2.25], [0.7, 1.6, -1.15], 34), 'lin']],
  set: (c) => twistSet()(c),
  cast: [mateTwist([[0, { ry: PI + 0.1, face: 'disbelief', shL: [22, 30], elL: 75, shR: [22, 30], elR: 75 }], [0.4, { face: 'shock', shrug: 0.5, spine: -6 }, 'back']])],
};
const T6_T1 = DEL0 - 0.35;
const tapAgain: Shot = {
  id: 'tap-again', t0: T5_T1, t1: T6_T1, sw: 1,
  cam: [[0, cam([1.95, 1.62, -0.85], [1.55, 1.2, -1.95], 40)], [T6_T1 - T5_T1, cam([1.9, 1.55, -1.05], [1.55, 1.2, -1.95], 40), 'lin']],
  set: (c) => twistSet()(c),
  cast: [mgrType([[0.2, { face: 'smug' }], ...typing(0.5, T6_T1 - T5_T1, { ...KEYS, spine: 12 })])],
  onScreen: ['manager'],
};
const T7_T1 = S(23) - 0.05;
const screenDown: Shot = {
  id: 'screen-down', t0: T6_T1, t1: T7_T1, sw: 1,
  cam: [[0, cam([1.95, 1.5, -0.7], [COMPUTER.x, 1.3, -1.96], 34)], [T7_T1 - T6_T1, cam([1.9, 1.48, -0.9], [COMPUTER.x, 1.3, -1.96], 34), 'lin']],
  set: (c) => twistSet()(c),
  cast: [mgrType(typing(0.1, DEL1 - T6_T1, { ...KEYS, spine: 12 }))],
  overlay: (c) => <FactCard t={c.t} at={DEL1 + 0.1} until={T7_T1 + 0.05} source="Bank of England">Pay the loan back, and that money is gone</FactCard>,
  onScreen: ['manager'],
};

// ================= 0:57.5 THE CLIFFHANGER: Alfie's pin goes haywire; the Manager knows it =================
const flicker = (ts: number) => 1.1 + Math.sin(ts * 31) * 0.9 + (Math.floor(ts * 12) % 3 === 0 ? 0.8 : 0);
const U1_T1 = S(24) - 0.04;
const PIN = { x: 2.15, z: -1.3 };
const pinFlick: Shot = {
  id: 'pin-flicker', t0: T7_T1, t1: U1_T1, sw: (ts) => (Math.floor(ts * 10) % 4 === 0 ? 0.6 : 1),
  cam: [[0, cam([PIN.x + 0.12, 1.36, PIN.z - 0.85], [PIN.x + 0.08, 1.3, PIN.z - 0.1], 32)], [U1_T1 - T7_T1, cam([PIN.x + 0.1, 1.33, PIN.z - 0.55], [PIN.x + 0.08, 1.3, PIN.z - 0.1], 32), 'lin']],
  shake: [[0.2, 0.5], [0.7, 0.5], [1.2, 0.5]],
  set: () => <BankHall sw={1} dim={1} screen="BUILDER|£0" />,
  cast: [{ who: 'lead', seed: 0.3, pin: flicker, keys: [[0, { x: PIN.x, z: PIN.z, ry: PI, face: 'shock', shL: [40, 30], elL: 30, shR: [40, 30], elR: 30, spine: -6 }]] }],
};
const CUT = E(24);
const mgrStare: Shot = {
  id: 'mgr-stare', t0: U1_T1, t1: CUT, sw: 1,
  cam: [[0, cam([1.05, 1.68, -2.7], [1.45, 1.58, -1.45], 36)], [CUT - U1_T1, cam([1.3, 1.64, -2.0], [1.45, 1.6, -1.45], 32), 'in']],
  shake: [[CUT - U1_T1 - 0.6, 0.5], [CUT - U1_T1 - 0.25, 0.7]],
  set: () => <BankHall sw={1} dim={1} screen="BUILDER|£0" />,
  cast: [mgr([[0, { ...MGR_AT, ry: PI + 0.5, face: 'shock', spine: -8, shL: [10, 8], elL: 20, shR: [10, 8], elR: 20, headNod: -8 }],
    [1.2, { face: 'disbelief', headTilt: 10, spine: -4, shR: [70, 20], elR: 30, handR: 'point' }], [2.4, { face: 'scream', headTilt: 0, spine: -10 }, 'back']])],
};

export const ACT2: Shot[] = [titleWide, titlePush, plonk, slide, smug, builderGo, vaultHeave, vaultReveal, board, whisper, matePeel,
  rainWide, nanShot, shutterShot, alfRain, twistWide, screenUp, alfAsk, typedIt, mateDo, tapAgain, screenDown, pinFlick, mgrStare];
export const BLACK_AT = CUT;
export const TOTAL = CUT + 0.4;
export { REAL };
