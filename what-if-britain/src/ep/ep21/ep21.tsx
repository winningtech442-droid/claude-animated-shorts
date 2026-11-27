// EP21 Mattress Money (v3 pilot). This file holds the cold open (0:00-0:20) for the user's test render; the rest
// of the episode is added after that approval. Timings follow src/episodes/ep21/lines.json (tools/cast_voice.py).
import React from 'react';
import words from '../../episodes/ep21/words.json';
import { makeEpisode3, cam, Shot, Actor, prog, lerp } from '../kit3';
import { Bedroom, Booth, Envelope, Toast, Clipboard, FallingNote, BED, WARD } from './sets';
import { Note } from '../../props';

const PI = Math.PI;
const tiny = (s = 0.22) => <group position={[0.01, -0.09, 0.05]} rotation={[PI / 2, 0, 0.2]}><Note s={s} /></group>;

// ---------- 0:00 bait: Alfie stuffs the envelope under the mattress (MS, already moving on frame 1) ----------
const alfStuff: Actor = {
  who: 'lead', seed: 0.3,
  keys: [
    [0, { x: -0.98, z: -0.95, ry: PI / 2, spine: 34, crouch: 0.18, face: 'smug', shL: [62, 6], elL: 30, shR: [48, 4], elR: 55, handL: 'open', handR: 'fist', headNod: 8 }],
    [0.9, { shR: [70, 2], elR: 22, headNod: 12 }],
    [1.8, { shR: [78, 0], elR: 10, face: 'happy' }],
    [2.5, { shR: [55, 6], elR: 40, shL: [30, 8], elL: 45 }],
    [3.0, { spine: 12, crouch: 0.05, shL: [20, 10], elL: 40, shR: [62, 8], elR: 35, face: 'smug', headNod: 2, headTurn: -25 }],
    [3.6, { shR: [58, 8], elR: 30 }],
  ],
  heldR: (ts) => (ts < 2.4 ? <group position={[0, -0.09, 0.06]} rotation={[0.5, 0, 0]} scale={1.5}><Envelope /></group> : null),
};
const stuff: Shot = {
  id: 'stuff', t0: 0, t1: 3.6,
  cam: [[0, cam([0.62, 1.42, 0.45], [-0.6, 1.08, -0.95], 40)], [3.6, cam([0.45, 1.38, 0.18], [-0.62, 1.08, -0.95], 40), 'lin']],
  set: (c) => (
    <Bedroom lift={0.13 * prog(c.ts, 0.2, 0.9) * (1 - prog(c.ts, 2.4, 2.9))}>
      {c.ts > 2.4 ? <group position={[-0.42, 0.575, -0.95]} rotation={[0, 0.2, 0]}><Envelope /></group> : null}
    </Bedroom>
  ),
  cast: [alfStuff],
};

// ---------- 0:03.6 the flop: Mate belly-flops on the foot end, the mattress fires Alfie into the wardrobe ----------
const T_FLOP = 7.0 - 3.6, T_LAND = 7.2 - 3.6, T_WARD = 7.55 - 3.6;
const alfSit: Actor = {
  who: 'lead', seed: 0.3,
  keys: [
    [0, { x: 0.0, y: 0.25, z: -1.3, ry: 0, sit: true, hipL: [90, 6], knL: 4, hipR: [90, 6], knR: 4, spine: -4, face: 'smug', shL: [20, 28], elL: 20, shR: [30, 22], elR: 35, headNod: 0, headTurn: 0, crouch: 0 }],
    [0.6, { shR: [40, 28], elR: 20 }], [0.9, { shR: [28, 22], elR: 38 }], [1.2, { shR: [40, 28], elR: 20 }], [1.5, { shR: [28, 22], elR: 38 }],
    [2.6, { face: 'happy', headTurn: 18 }],
    [T_FLOP, { face: 'worried', headTurn: 10, spine: 2 }],
    [T_LAND, { face: 'shock', shL: [40, 40], shR: [40, 40], elL: 30, elR: 30 }],
    [T_LAND + 0.18, { x: -0.7, y: 1.55, z: -1.9, rx: -1.3, face: 'scream', shL: [160, 50], shR: [160, 50], elL: 10, elR: 10, hipL: [60, 20], hipR: [110, 20], knL: 60, knR: 10 }, 'out'],
    [T_WARD, { x: WARD.x, y: 0.55, z: WARD.z + 0.1, rx: -2.7, rz: 0.4 }, 'in'],
    [T_WARD + 0.02, { vis: 0 }],
  ],
};
const mateFlop: Actor = {
  who: 'mate', seed: 2.2,
  keys: [
    [0, { x: 1.45, y: 0, z: 0.95, ry: -PI / 2, face: 'neutral', shR: [55, 8], elR: 95, handR: 'fist', shL: [0, 8], elL: 10 }],
    [1.4, { x: 1.45 }],
    [2.6, { x: 0.15, face: 'thinking' }],
    [3.0, { ry: -PI / 2, headTurn: 25, face: 'smug' }],
    [3.15, { ry: -PI * 0.75, shrug: 0.6 }],
    [T_FLOP - 0.3, { ry: -PI, shrug: 0, spine: -14, shL: [150, 30], shR: [150, 30], elL: 20, elR: 20, face: 'happy', headTurn: 0 }],
    [T_FLOP, { spine: -18 }],
    [T_LAND, { y: 0.9, rx: -PI / 2, spine: 0, shL: [170, 20], shR: [170, 20], face: 'holding', hipL: [0, 4], hipR: [0, 4] }, 'in'],
    [T_LAND + 0.1, { y: 0.78, knL: 0, knR: 0 }, 'out'],
    [T_LAND + 0.25, { y: 0.92 }, 'out'],
    [T_LAND + 0.45, { y: 0.86, shL: [175, 35], shR: [175, 35], face: 'holding' }],
  ],
  heldR: (ts) => (ts < T_FLOP + 0.04 ? <group position={[0, -0.09, 0.05]}><Toast /></group> : null),
};
const flop: Shot = {
  id: 'flop', t0: 3.6, t1: 9.5,
  cam: [
    [0, cam([0.6, 1.68, 3.6], [-0.3, 0.86, -1.25], 50)],
    [T_LAND, cam([0.5, 1.58, 3.15], [-0.32, 0.9, -1.25], 50), 'lin'],
    [T_WARD + 0.85, cam([0.5, 1.58, 3.12], [-0.32, 0.9, -1.25], 50)],
    [9.5 - 3.6, cam([0.42, 1.45, 2.55], [0.05, 0.85, -0.2], 46), 'io'],
  ],
  shake: [[T_LAND, 1.0], [T_WARD, 1.5]],
  set: (c) => {
    const ts = c.ts;
    const tilt = ts < T_LAND ? 0 : 0.17 * Math.exp(-(ts - T_LAND) * 5) * Math.cos((ts - T_LAND) * 22);
    const doors = ts < T_WARD - 0.08 ? 0 : ts < T_WARD + 0.05 ? 1.6 * prog(ts, T_WARD - 0.08, T_WARD - 0.02, 'out') : 1.6 * (1 - prog(ts, T_WARD + 0.05, T_WARD + 0.1, 'in'));
    const shake = ts < T_WARD + 0.1 ? 0 : Math.exp(-(ts - T_WARD - 0.1) * 6) * Math.sin((ts - T_WARD) * 40);
    const toastU = prog(ts, T_FLOP + 0.04, T_LAND + 0.5, 'lin');
    return (
      <Bedroom tilt={tilt} doorL={doors} doorR={doors} shake={shake}>
        {ts < T_LAND + 0.02 ? <group position={[-0.42, 0.575, -0.95]} rotation={[0, 0.2, 0]}><Envelope /></group> : null}
        {ts > T_LAND ? [0, 1, 2, 3, 4, 5, 6].map((i) => (
          <FallingNote key={i} from={[-0.3 + 0.08 * i, 0.9, -1.2]} to={[-0.9 + 0.3 * i, 0.03, -1.3 + 0.35 * ((i * 3) % 5)]} u={prog(ts, T_LAND + 0.05 * i, T_LAND + 1.6 + 0.12 * i, 'lin')} spin={0.6 + 0.15 * i} />
        )) : null}
        {ts > T_WARD ? <FallingNote from={[0.32, 1.82, 2.35]} to={[0.36, 1.12, 2.42]} u={prog(ts, T_WARD + 0.05, T_WARD + 1.0, 'lin')} spin={0.7} s={1.1} /> : null}
        {ts > T_FLOP && ts < T_LAND + 0.5 ? <group position={[lerp(0.2, 0.05, toastU), 1.0 + 1.1 * Math.sin(PI * toastU) + (toastU > 0.95 ? -0.05 : 0), lerp(0.7, 0.25, toastU)]} rotation={[toastU * 9, toastU * 4, 0]}><Toast /></group> : null}
        {ts >= T_LAND + 0.5 ? <group position={[0.05, 1.08, 0.22]} rotation={[0.1, 0.4, 0]}><Toast /></group> : null}
      </Bedroom>
    );
  },
  cast: [alfSit, mateFlop],
};

// ---------- 0:09.5 the Booth: "Is he okay?" / "That wasn't in the script." / "Oh s***. His pin." ----------
const producer = (keys: Actor['keys']): Actor => ({ who: 'producer', seed: 1.7, keys, heldL: () => <Clipboard /> });
const prodBase = { x: 0.85, y: 0, z: -0.15, ry: -0.75, shL: [16, -8] as [number, number], elL: 75, twL: 30, handL: 'fist' as const, shR: [10, 10] as [number, number], elR: 20 };
const narrator: Actor = {
  who: 'narrator', seed: 0.9,
  keys: [
    [0, { x: 0, y: 0.04, z: 0.02, ry: PI, sit: true, hipL: [90, 8], knL: 88, hipR: [90, 8], knR: 88, spine: 8, shL: [50, 10], elL: 60, shR: [50, 10], elR: 60, face: 'neutral' }],
    [0.12, { spine: -12, shR: [65, 35], elR: 35, headTilt: 6 }],
    [0.45, { spine: 10, shR: [50, 12], elR: 60, headTilt: 0 }],
  ],
};
const booth1: Shot = {
  id: 'booth-prod1', t0: 9.5, t1: 10.62,
  cam: [[0, cam([0.08, 1.48, 1.65], [0.84, 1.36, -0.15], 40)], [1.12, cam([0.18, 1.48, 1.32], [0.84, 1.38, -0.15], 40), 'lin']],
  set: () => <Booth />,
  cast: [producer([[0, { ...prodBase, face: 'worried', spine: 6 }], [0.3, { spine: 12, face: 'worried', headTilt: -6 }], [1.12, { spine: 14 }]]), narrator],
};
const booth2: Shot = {
  id: 'booth-narr', t0: 10.62, t1: 12.25,
  cam: [[0, cam([0.46, 1.74, 1.62], [0.12, 0.98, -0.52], 44)], [1.63, cam([0.34, 1.64, 1.25], [0.12, 1.0, -0.52], 44), 'lin']],
  shake: [[0.1, 0.5]],
  set: (c) => <Booth tip={prog(c.ts, 0.1, 0.38, 'in')} spill={prog(c.ts, 0.36, 1.2, 'out')} />,
  cast: [narrator, producer([[0, { ...prodBase, face: 'worried', spine: 12 }]])],
};
const booth3: Shot = {
  id: 'booth-prod2', t0: 12.25, t1: 14.62,
  cam: [[0, cam([0.4, 1.55, 1.22], [0.84, 1.45, -0.15], 36)], [2.37, cam([0.52, 1.55, 0.86], [0.84, 1.46, -0.15], 36), 'lin']],
  shake: [[0.2, 0.4]],
  set: () => <Booth tip={1} spill={1} />,
  cast: [producer([
    [0, { ...prodBase, face: 'shock', spine: 4 }],
    [0.2, { face: 'scream', shrug: 0.5 }],
    [1.25, { face: 'shock', shrug: 0.2 }],
    [1.45, { shR: [108, 20], elR: 6, handR: 'point', face: 'scream', headTurn: -10 }, 'out'],
  ]), narrator],
};

// ---------- 0:14.6 the pin: glow through the wardrobe gap, the white crack, the switch ----------
const wardGlow: Shot = {
  id: 'ward-glow', t0: 14.62, t1: 15.3,
  cam: [[0, cam([-1.2, 1.25, -0.85], [-1.45, 1.12, -2.15], 40)], [0.68, cam([-1.25, 1.22, -1.15], [-1.45, 1.12, -2.15], 40), 'lin']],
  crack: 0.28,
  sw: (ts) => (ts < 0.28 ? 0 : 1),
  set: (c) => <Bedroom sw={c.sw} gapGlow={0.5 + 0.5 * prog(c.ts, 0, 0.28)} shake={c.ts > 0.28 ? 0.6 * Math.exp(-(c.ts - 0.28) * 8) * Math.sin(c.ts * 50) : 0} />,
  cast: [],
};

// ---------- 0:15.3 the switched bedroom: Alfie crawls out; his money has shrunk ----------
const crawl: Actor = {
  who: 'lead', seed: 0.3, pin: (ts) => 0.65 + 0.35 * Math.sin(ts * 7),
  keys: [
    [0, { x: WARD.x, y: -0.33, z: -2.3, ry: 0, crouch: 1, spine: 70, shL: [95, 10], elL: 8, shR: [95, 10], elR: 8, face: 'worried', headNod: -32, vis: 0 }],
    [0.06, { vis: 1 }],
    [0.35, { z: -2.12, shL: [80, 10], shR: [108, 10] }],
    [0.6, { z: -1.98, shL: [108, 10], shR: [80, 10], face: 'disbelief' }],
    [0.9, { z: -1.85, shL: [94, 10], shR: [94, 10], headNod: -40 }],
  ],
};
const crawlShot: Shot = {
  id: 'crawl', t0: 15.3, t1: 16.2,
  cam: [[0, cam([-0.9, 1.02, 0.2], [-1.45, 0.45, -1.95], 40)], [0.9, cam([-0.95, 0.96, -0.05], [-1.45, 0.42, -1.9], 40), 'lin']],
  sw: 1,
  set: (c) => (
    <Bedroom sw={1} doorL={1.25 * prog(c.ts, 0.0, 0.3, 'out')} doorR={0.25 * prog(c.ts, 0.05, 0.3, 'out')}>
      {TINY_ON_FLOOR}
    </Bedroom>
  ),
  cast: [crawl],
};
const TINY_ON_FLOOR = [[-1.2, -1.5, 0.4], [-1.65, -1.62, 1.3], [-1.05, -1.95, 2.1], [-1.5, -1.25, 0.9], [-0.85, -1.6, 2.6]].map(([x, z, r], i) => (
  <group key={i} position={[x, 0.012, z]} rotation={[0, r, 0]}><Note s={0.22} /></group>
));

// ---------- 0:16.2 on "tiny?": a macro of the shrunken twenty pinched in Alfie's fingers ----------
const SKIN = '#E6B896';
const Finger: React.FC<{ p: [number, number, number]; r: [number, number, number]; L?: number }> = ({ p, r, L = 0.07 }) => (
  <mesh position={p} rotation={r}><capsuleGeometry args={[0.0105, L, 8, 16]} /><meshStandardMaterial color={SKIN} roughness={0.6} /></mesh>
);
const macro: Shot = {
  id: 'macro', t0: 16.2, t1: 17.0,
  cam: [[0, cam([-1.22, 0.43, -1.27], [-1.3, 0.355, -1.5], 30)], [0.8, cam([-1.235, 0.415, -1.33], [-1.3, 0.355, -1.5], 30), 'lin']],
  sw: 1,
  set: (c) => {
    const j = 0.0015 * Math.sin(c.ts * 55); // trembling fingers
    return (
      <Bedroom sw={1}>
        <group position={[-1.3 + j, 0.355, -1.5]} rotation={[1.2, 0.15, 0.1]}>
          <Note s={0.3} />
          <Finger p={[0.028, 0.012, -0.018]} r={[0.2, 0, -1.1]} />
          <Finger p={[0.03, -0.012, -0.012]} r={[-0.25, 0, -1.25]} L={0.055} />
        </group>
      </Bedroom>
    );
  },
  cast: [],
};

// ---------- 0:17.6 Mate squints at a twenty the size of a stamp ----------
const mateSquint: Actor = {
  who: 'mate', seed: 2.2,
  keys: [
    [0, { x: 0.18, y: 0.2, z: 0.42, ry: -0.25, sit: true, hipL: [90, 10], knL: 88, hipR: [90, 10], knR: 88, spine: 6, face: 'thinking', shR: [80, 30], elR: 125, twR: 25, handR: 'fist', shL: [15, 12], elL: 35, headTilt: -6 }],
    [0.6, { spine: 4, headNod: 2 }],
    [1.3, { face: 'disbelief', headTilt: 6 }],
    [3.0, { spine: 5 }],
  ],
};
const squint: Shot = {
  id: 'mate-squint', t0: 17.0, t1: 20.0,
  cam: [[0, cam([0.12, 1.42, 1.95], [0.26, 1.4, 0.42], 36)], [3.0, cam([0.16, 1.42, 1.5], [0.26, 1.4, 0.42], 36), 'lin']],
  sw: 1,
  set: () => (
    <Bedroom sw={1}>
      {/* the shrunken twenty, pinched at the top of his fist (placed in the room so it always faces the lens) */}
      <group position={[0.335, 1.385, 0.61]} rotation={[PI / 2 + 0.12, 0.1, 0.18]}><Note s={0.34} /></group>
    </Bedroom>
  ),
  cast: [mateSquint],
};

export const ep21 = makeEpisode3({
  id: 'ep21',
  shots: [stuff, flop, booth1, booth2, booth3, wardGlow, crawlShot, macro, squint],
  words: words as any,
  total: 20.0,
  hook: { node: <><span style={{ color: '#FFD43B' }}>£1,000</span> under the mattress?</>, until: 3.0 },
});
export const BED_INFO = BED; // keep the import used for tools that read the layout
