// Ep 20: America LOST money on Britain's war loan (20 Nov 2026). Follow-up to the WW2 loan video ("Your tax was still paying...").
// ONE location, NEW SET: THE COUNTER. A bright daylight hall split down the middle: LONDON (cream, navy/red bunting) on the left,
// WASHINGTON (pale blue, white star bunting) on the right; one long counter in front with BRITAIN | AMERICA panels and a brass
// divider; a year calendar on the back wall. Alfie stands for Britain, Mate plays America's man at the counter, Nan pours tea.
// Plain 30 fps. Times are the aligned voice (out/ep20/vo.mp3, voice F, 65.7 s) + a 3 s end card. world/hud use ABSOLUTE time t.
// The first second (STUDIO-RULES 2, 20 Nov): frame 1 is the cheque already slamming onto the counter, LOST! pops at 0.25 s,
// no hook card (caption + one big word only in the first 3 s).
// Planted slip: Nan's teapot has its spout and handle on the SAME side (shot s8). Never on a money number.
// Notes are generic and marked ILLUSTRATIVE. Nobody real is shown.
import React from 'react';
import { CROSSED, OPEN_ARMS, ON_HEAD, CHIN, HANDS_FRONT, PALMS_UP, OVER_MOUTH } from '../tests/ActingTest';
import { makeShotEpisode, Shot, Box, Big, cam, clamp, lerp, prog, V3 } from './kit';
import { textTexture } from '../kit/text';
import words from '../episodes/ep20/words.json';

const A2 = (a: number, b: number) => [a, b] as [number, number];
const SLACK = { shL: A2(6, 10), elL: 10, shR: A2(6, 10), elR: 10, twL: 0, twR: 0 };
const POINT = { shL: A2(6, 10), elL: 10, shR: A2(92, 8), elR: 8, handR: 'point' as const, twL: 0, twR: 0 };
const HOLD = { shL: A2(40, -4), elL: 70, shR: A2(40, -4), elR: 70, twL: 0, twR: 0 };
const HOLD1 = { shL: A2(6, 10), elL: 10, shR: A2(55, 6), elR: 60, twL: 0, twR: 0 };
const FIST1 = { shL: A2(6, 10), elL: 10, shR: A2(150, 20), elR: 40, handR: 'fist' as const, twL: 0, twR: 0 };
const SLAM = { shL: A2(6, 10), elL: 10, shR: A2(70, -10), elR: 20, handR: 'open' as const, twL: 0, twR: 0 };
const BEG = { shL: A2(45, -20), elL: 100, shR: A2(45, -20), elR: 100, twL: 60, twR: 60, handL: 'open' as const, handR: 'open' as const };
const GOLD = '#FFD400', RED = '#ff3b3b', GREEN = '#3f9d63';

// ---------- pop helpers (same look as Ep 19) ----------
const popK = (t: number, a: number, b: number) => (t < a || t > b + 0.13 ? 0 : t < b ? prog(t, a, a + 0.15, 'back') : 1 - prog(t, b, b + 0.12, 'in'));
const HP: React.FC<{ t: number; a: number; b: number; x: number; y: number; children: React.ReactNode }> = ({ t, a, b, x, y, children }) => {
  const k = popK(t, a, b); if (k <= 0.002) return null;
  return <div style={{ position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, transform: `scale(${k})`, transformOrigin: `${x}px ${y}px`, opacity: clamp(k * 3), pointerEvents: 'none' }}>{children}</div>;
};
const Pop: React.FC<{ text: string; y?: number; c?: string; size?: number; rot?: number }> = ({ text, y = 330, c = RED, size = 200, rot = -5 }) => (
  <div style={{ position: 'absolute', left: 0, right: 0, top: y, textAlign: 'center', transform: `rotate(${rot}deg)`, font: `900 ${size}px Inter`, color: c, WebkitTextStroke: '10px #fff', paintOrder: 'stroke fill', textShadow: '0 8px 24px rgba(0,0,0,.45)' }}>{text}</div>
);
const Tag: React.FC<{ x: number; y: number; text: string; c?: string; size?: number }> = ({ x, y, text, c = '#fff', size = 64 }) => (
  <div style={{ position: 'absolute', left: x - 480, top: y, width: 960, textAlign: 'center', font: `900 ${size}px Inter`, color: c, WebkitTextStroke: '8px #10131c', paintOrder: 'stroke fill' }}>{text}</div>
);

// ---------- the set: THE COUNTER ----------
const Sign: React.FC<{ p: V3; w: number; h: number; k: string; bg: string; lines: { text: string; x: number; y: number; size: number; color: string; weight?: number }[]; rot?: V3 }> = ({ p, w, h, k, bg, lines, rot }) => {
  const tex = textTexture(k, { w: 512, h: Math.round(512 * h / w), bg, lines });
  return <mesh position={p} rotation={rot}><planeGeometry args={[w, h]} /><meshBasicMaterial map={tex ?? undefined} color={tex ? '#ffffff' : bg} toneMapped={false} /></mesh>;
};
const TOP = 1.02, CZ = 0.62; // counter top height, counter-top depth line where props sit
const Bunting: React.FC<{ x0: number; x1: number; y: number; cols: string[] }> = ({ x0, x1, y, cols }) => (
  <group>
    <Box p={[(x0 + x1) / 2, y + 0.02, -2.05]} s={[x1 - x0, 0.015, 0.015]} c="#6b5a44" />
    {Array.from({ length: Math.round((x1 - x0) / 0.32) }).map((_, i) => (
      <mesh key={i} position={[x0 + 0.16 + i * 0.32, y - 0.1, -2.04]} rotation={[0, 0, Math.PI]}>
        <coneGeometry args={[0.1, 0.22, 3]} /><meshStandardMaterial color={cols[i % cols.length]} roughness={0.9} />
      </mesh>
    ))}
  </group>
);
const Calendar: React.FC<{ year: number; p?: V3 }> = ({ year, p = [0.3, 2.08, -2.08] }) => (
  <group position={p} scale={0.72}>
    <Box p={[0, 0, -0.02]} s={[0.86, 0.86, 0.03]} c="#7a5c3c" />
    <Sign p={[0, 0, 0.0]} w={0.78} h={0.78} k={`cal${year}`} bg="#fbf7ec" lines={[{ text: 'YEAR', x: 256, y: 80, size: 60, color: '#c0272d', weight: 900 }, { text: String(year), x: 256, y: 300, size: 170, color: '#1d2433', weight: 900 }]} />
  </group>
);
// generic dollar note, marked ILLUSTRATIVE; s scales it (the shrinking dollar)
const Note: React.FC<{ p: V3; s?: number; rot?: V3 }> = ({ p, s = 1, rot = [-Math.PI / 2, 0, 0] }) => (
  <group position={p} rotation={rot} scale={s}>
    <Sign p={[0, 0, 0]} w={0.5} h={0.22} k="note1" bg="#9cc9a0" lines={[{ text: '$1', x: 70, y: 112, size: 120, color: '#1f5e33', weight: 900 }, { text: '$1', x: 442, y: 112, size: 120, color: '#1f5e33', weight: 900 }, { text: 'ILLUSTRATIVE', x: 256, y: 112, size: 40, color: '#2f6e43', weight: 800 }]} />
  </group>
);
const Cheque: React.FC<{ p: V3; s?: number; text?: string; k?: string }> = ({ p, s = 1, text = 'PAY AMERICA', k = 'chq' }) => (
  <group position={p} scale={s} rotation={[-Math.PI / 2, 0, -0.06]}>
    <Sign p={[0, 0, 0.0]} w={0.6} h={0.26} k={k} bg="#f7f1de" lines={[{ text, x: 256, y: 70, size: 54, color: '#1d2433', weight: 900 }, { text: '$ ______', x: 256, y: 160, size: 60, color: '#1f5e33', weight: 900 }]} />
  </group>
);
// a stack of money on the counter: h metres tall, label under it
const Stack: React.FC<{ x: number; h: number; label: string; c?: string }> = ({ x, h, label, c = GREEN }) => (
  <group>
    {h > 0.01 ? <><Box p={[x, TOP + h / 2, CZ - 0.05]} s={[0.3, h, 0.3]} c={c} /><Box p={[x, TOP + h / 2, CZ - 0.05]} s={[0.31, h * 0.94, 0.12]} c="#e8e2d2" /></> : null}
    <Sign p={[x, TOP - 0.17, 0.97]} w={0.36} h={0.14} k={`lbl${label}`} bg="#1d2433" lines={[{ text: label, x: 256, y: 87, size: 100, color: '#fff', weight: 900 }]} />
  </group>
);
const Gift: React.FC<{ p: V3; s?: number }> = ({ p, s = 1 }) => (
  <group position={p} scale={s}>
    <Box p={[0, 0.17, 0]} s={[0.36, 0.34, 0.36]} c="#d7262e" />
    <Box p={[0, 0.17, 0]} s={[0.07, 0.35, 0.37]} c="#ffd21f" /><Box p={[0, 0.17, 0]} s={[0.37, 0.35, 0.07]} c="#ffd21f" />
    <mesh position={[-0.07, 0.38, 0]} rotation={[0, 0, 0.5]}><torusGeometry args={[0.07, 0.022, 8, 20]} /><meshStandardMaterial color="#ffd21f" /></mesh>
    <mesh position={[0.07, 0.38, 0]} rotation={[0, 0, -0.5]}><torusGeometry args={[0.07, 0.022, 8, 20]} /><meshStandardMaterial color="#ffd21f" /></mesh>
  </group>
);
// THE SLIP: spout and handle both on the +x side
const Teapot: React.FC<{ p: V3; tilt?: number }> = ({ p, tilt = 0 }) => (
  <group position={p} rotation={[0, 0, -tilt]}>
    <mesh scale={[1, 0.82, 1]}><sphereGeometry args={[0.13, 20, 16]} /><meshStandardMaterial color="#f2efe6" roughness={0.4} /></mesh>
    <mesh position={[0, 0.115, 0]}><cylinderGeometry args={[0.05, 0.06, 0.03, 16]} /><meshStandardMaterial color="#f2efe6" /></mesh>
    <mesh position={[0, 0.14, 0]}><sphereGeometry args={[0.022, 10, 8]} /><meshStandardMaterial color="#2f4f8f" /></mesh>
    <mesh position={[0.16, 0.03, 0.05]} rotation={[0, 0, -0.9]}><cylinderGeometry args={[0.018, 0.03, 0.15, 10]} /><meshStandardMaterial color="#f2efe6" /></mesh>
    <mesh position={[0.13, 0.0, -0.06]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[0.05, 0.014, 8, 16]} /><meshStandardMaterial color="#f2efe6" /></mesh>
    <mesh position={[0, -0.02, 0]}><torusGeometry args={[0.131, 0.008, 6, 30]} /><meshStandardMaterial color="#2f4f8f" /></mesh>
  </group>
);
const Cup: React.FC<{ p: V3 }> = ({ p }) => (
  <group position={p}>
    <mesh position={[0, 0.04, 0]}><cylinderGeometry args={[0.045, 0.035, 0.08, 16]} /><meshStandardMaterial color="#f2efe6" /></mesh>
    <mesh position={[0, 0.003, 0]}><cylinderGeometry args={[0.07, 0.07, 0.006, 20]} /><meshStandardMaterial color="#f2efe6" /></mesh>
  </group>
);
// the price arrow on the Washington wall: k 0..1+ grows it upwards
const PriceArrow: React.FC<{ k: number }> = ({ k }) => {
  const h = lerp(0.2, 2.6, clamp(k / 1.35, 0, 1.4));
  return (
    <group position={[1.75, 1.15, -2.0]} rotation={[0, 0, -0.18]}>
      <Box p={[0, h / 2, 0]} s={[0.16, h, 0.04]} c="#d7262e" />
      <mesh position={[0, h + 0.15, 0]}><coneGeometry args={[0.24, 0.32, 3]} /><meshStandardMaterial color="#d7262e" /></mesh>
    </group>
  );
};

const Hall: React.FC<{ year?: number; arrow?: number; extras?: React.ReactNode }> = ({ year, arrow = 0, extras }) => (
  <group>
    <Box p={[0, -0.05, 0]} s={[30, 0.1, 12]} c="#c9a77a" />
    {/* back wall, split down the middle */}
    <Box p={[-7.2, 2.5, -2.2]} s={[15, 5, 0.2]} c="#efe6d2" />
    <Box p={[7.8, 2.5, -2.2]} s={[15, 5, 0.2]} c="#dde8f2" />
    {/* windows: daylight both sides */}
    {[[-2.1, '#cfe8ff'], [3.0, '#cfe8ff']].map(([x, c]) => (
      <group key={String(x)} position={[x as number, 2.0, -2.08]}>
        <Box p={[0, 0, -0.01]} s={[1.5, 1.7, 0.03]} c="#8a6a48" />
        <mesh position={[0, 0, 0.01]}><planeGeometry args={[1.32, 1.52]} /><meshBasicMaterial color={c as string} toneMapped={false} /></mesh>
        <Box p={[0, 0, 0.03]} s={[0.05, 1.52, 0.02]} c="#8a6a48" /><Box p={[0, 0, 0.03]} s={[1.32, 0.05, 0.02]} c="#8a6a48" />
      </group>
    ))}
    <Sign p={[-2.1, 3.1, -2.07]} w={1.9} h={0.42} k="london" bg="#1d2a4d" lines={[{ text: 'LONDON', x: 256, y: 57, size: 76, color: '#f2dca0', weight: 900 }]} />
    <Sign p={[3.0, 3.1, -2.07]} w={1.9} h={0.42} k="washington" bg="#24508c" lines={[{ text: 'WASHINGTON', x: 256, y: 57, size: 60, color: '#ffffff', weight: 900 }]} />
    <Bunting x0={-4.2} x1={0.2} y={3.6} cols={['#1d2a4d', '#c0272d', '#f4f0e0']} />
    <Bunting x0={0.4} x1={5.0} y={3.6} cols={['#24508c', '#ffffff', '#c0272d']} />
    {year !== undefined ? <Calendar year={year} /> : null}
    {arrow > 0.01 ? <PriceArrow k={arrow} /> : null}
    {/* the counter: wood, BRITAIN | AMERICA panels, brass divider in the middle */}
    <Box p={[0.3, 0.5, 0.75]} s={[7.0, 1.0, 0.5]} c="#8f6a43" />
    <Box p={[0.3, TOP - 0.01, 0.72]} s={[7.1, 0.04, 0.62]} c="#6e4f30" />
    <Sign p={[-1.25, 0.55, 1.01]} w={1.6} h={0.36} k="pbritain" bg="#1d2a4d" lines={[{ text: 'BRITAIN', x: 256, y: 60, size: 84, color: '#f2dca0', weight: 900 }]} />
    <Sign p={[1.85, 0.55, 1.01]} w={1.6} h={0.36} k="pamerica" bg="#24508c" lines={[{ text: 'AMERICA', x: 256, y: 60, size: 84, color: '#ffffff', weight: 900 }]} />
    <Box p={[0.3, TOP + 0.08, 0.72]} s={[0.04, 0.16, 0.55]} c="#c9a23a" />
    {extras}
  </group>
);
const W = (o: { year?: number | ((t: number) => number); arrow?: number } = {}, fn?: (c: any) => React.ReactNode) => (c: any) =>
  <Hall year={typeof o.year === 'function' ? o.year(c.t) : o.year} arrow={o.arrow} extras={fn ? fn(c) : undefined} />;

// ---------- cameras ----------
const m = (x: number, d = 4.2, ty = 1.35, fov = 38) => cam(x, d, ty, fov, 0.35);   // medium over the counter
const c1 = (x: number, d = 2.3, ty = 1.55, fov = 38) => cam(x, d, ty, fov, 0.15);  // close: chest up
const AL = -0.35, MT = 0.95, NN = -1.45;                                                // Alfie (Britain), Mate (America), Nan
const k = (x: number, pose: object, face: string, extra: object = {}) => ({ x, ...pose, face, ...extra });
const yearAt = (t: number, t0: number, t1: number, y0: number, y1: number) => Math.round(lerp(y0, y1, prog(t, t0, t1)));

// value of the stacks: metres per $bn
const BN = 0.13;

const shots: Shot[] = [
  // 1. America LOST money on Britain's war loan! (frame 1: the cheque is already slamming down; LOST! at 0.25 s)
  { id: 's1', t0: 0, t1: 2.04, cam: [[0, c1(-0.1, 2.9, 1.45)], [2.04, c1(-0.05, 2.5, 1.45), 'io']],
    who: { alf: [[0, k(AL + 0.15, SLAM, 'angry', { turnY: 0.55, spine: 10 })], [0.25, k(AL + 0.15, SLAM, 'smug', { turnY: 0.5, spine: 6 }), 'back'], [2.04, k(AL + 0.15, HOLD1, 'smug', { turnY: 0.4 })]],
      mate: [[0, k(MT - 0.1, HANDS_FRONT, 'neutral', { turnY: -0.5 })], [0.3, k(MT - 0.1, OVER_MOUTH, 'shock', { turnY: -0.4, spine: -8 }), 'back'], [2.04, k(MT - 0.1, ON_HEAD, 'disbelief', { turnY: -0.3 })]] },
    world: W({}, ({ t }) => <group rotation={[0.75, 0, 0]} position={[0, 0.25, 0.55]}><Cheque p={[lerp(-0.45, -0.1, prog(t, 0.0, 0.3, 'out')), lerp(TOP + 0.3, TOP - 0.2, prog(t, 0.0, 0.25, 'in')), CZ - 0.9]} s={1.15} k="chqfinal" text="FINAL PAYMENT" /></group>),
    hud: ({ t }) => <HP t={t} a={0.22} b={1.95} x={540} y={470}><Pop text="LOST!" y={300} /></HP> },
  // 2. and we paid back nearly DOUBLE! (two stacks: LENT and BACK; BACK shoots up)
  { id: 's2', t0: 2.04, t1: 4.05, cam: [[0, m(0.3, 5.4, 1.5)], [2.01, m(0.3, 4.9, 1.5), 'io']],
    who: { alf: [[0, k(AL - 0.4, POINT, 'happy', { turnY: 0.6 })], [1.4, k(AL - 0.4, POINT, 'laugh', { turnY: 0.6, bounce: 0.03 }), 'back']],
      mate: [[0, k(MT + 0.5, CROSSED, 'smug', { turnY: -0.4 })]] },
    world: W({ year: 2006 }, ({ t }) => <><Stack x={0.1} h={4.33 * BN} label="LENT" /><Stack x={0.5} h={lerp(0.05, 7.5 * BN, prog(t, 2.5, 3.6, 'back'))} label="BACK" /></>),
    hud: ({ t }) => <HP t={t} a={3.4} b={4.0} x={540} y={420}><Big top={280} main="NEARLY ×2" color={GOLD} size={130} /></HP> },
  // 3. so what if we'd paid the lot back on DAY ONE? (Alfie to us, thinking, then palms up)
  { id: 's3', t0: 4.05, t1: 6.9, cam: [[0, c1(AL, 2.6, 1.55)], [2.85, c1(AL, 2.0, 1.6), 'io']],
    who: { alf: [[0, k(AL, CHIN, 'thinking', { turnY: 0.1, headTilt: 6 })], [1.7, k(AL, PALMS_UP, 'disbelief', { turnY: 0.0, shrug: 0.7, headTilt: 6 }), 'back']] },
    world: W({ year: 1946 }),
    hud: ({ t }) => <HP t={t} a={5.85} b={6.85} x={540} y={330}><Tag x={540} y={250} text="DAY ONE?" c={GOLD} size={96} /></HP> },
  // 4. after the war, Britain was SKINT (empty pockets, calendar 1945)
  { id: 's4', t0: 6.9, t1: 8.95, cam: [[0, m(AL, 3.6, 1.45)], [2.05, m(AL + 0.1, 3.2, 1.45), 'io']],
    who: { alf: [[0, k(AL, SLACK, 'worried', { turnY: 0.1 })], [1.3, k(AL, PALMS_UP, 'sad', { turnY: 0.1, shrug: 0.9, headTilt: -5 }), 'back']] },
    world: W({ year: 1945 }),
    hud: ({ t }) => <HP t={t} a={8.25} b={8.9} x={540} y={420}><Pop text="SKINT" y={320} size={170} /></HP> },
  // 5. we begged America for a GIFT (Alfie pleads across the counter; a gift box sits on Britain's side)
  { id: 's5', t0: 8.95, t1: 11.15, cam: [[0, m(0.3, 5.4, 1.45)], [2.2, m(0.3, 4.9, 1.45), 'io']],
    who: { alf: [[0, k(AL, SLACK, 'worried', { turnY: 0.6 })], [0.5, k(AL, BEG, 'sad', { turnY: 0.7, spine: 8 }), 'back']],
      mate: [[0, k(MT, CROSSED, 'neutral', { turnY: -0.5 })], [1.6, k(MT, CROSSED, 'thinking', { turnY: -0.5, headTilt: 6 }), 'back']] },
    world: W({ year: 1945 }, ({ t }) => <Gift p={[lerp(-0.3, 0.0, prog(t, 9.6, 10.3, 'out')), TOP, CZ]} s={lerp(0.01, 1, prog(t, 9.4, 9.8, 'back'))} />),
    hud: ({ t }) => <HP t={t} a={10.45} b={11.1} x={540} y={330}><Tag x={540} y={250} text="A GIFT?" c={GOLD} size={96} /></HP> },
  // 6. America said no. Have a LOAN instead. (Mate shakes his head, pushes the gift back, slaps a LOAN slip down)
  { id: 's6', t0: 11.15, t1: 13.85, cam: [[0, c1(MT - 0.1, 2.5, 1.5)], [2.7, c1(MT - 0.1, 2.0, 1.5), 'io']],
    who: { mate: [[0, k(MT, CROSSED, 'neutral', { turnY: -0.3 })], [0.8, k(MT, CROSSED, 'smug', { turnY: -0.3, headTilt: -8 }), 'back'], [1.5, k(MT, SLAM, 'smug', { turnY: -0.6, spine: 8 }), 'back'], [2.7, k(MT, HOLD1, 'smug', { turnY: -0.4 })]] },
    mod: { mate: (p: any, ts: number) => ({ ...p, turnY: p.turnY + (ts > 0.3 && ts < 1.0 ? 0.25 * Math.sin((ts - 0.3) * 18) : 0) }) },
    world: W({ year: 1945 }, ({ t }) => <>
      {t < 12.4 ? <Gift p={[lerp(0.0, -1.2, prog(t, 11.6, 12.3, 'in')), TOP, CZ]} /> : null}
      <Sign p={[0.75, lerp(TOP + 0.4, TOP + 0.006, prog(t, 12.5, 12.75, 'in')), CZ]} rot={[-Math.PI / 2, 0, 0.05]} w={0.6} h={0.36} k="loanslip" bg="#fbf7ec" lines={[{ text: 'LOAN', x: 256, y: 110, size: 130, color: '#c0272d', weight: 900 }, { text: '2% A YEAR', x: 256, y: 240, size: 70, color: '#1d2433', weight: 900 }]} />
    </>),
    hud: ({ t }) => <HP t={t} a={12.6} b={13.8} x={540} y={420}><Pop text="LOAN" y={300} size={190} c="#ffffff" rot={4} /></HP> },
  // 7. four point three billion dollars, at just two per cent ($4.3BN, then 2%)
  { id: 's7', t0: 13.85, t1: 17.15, cam: [[0, m(0.3, 5.4, 1.5)], [3.3, m(0.3, 4.9, 1.55), 'io']],
    who: { alf: [[0, k(AL, SLACK, 'neutral', { turnY: 0.5 })], [1.2, k(AL, OVER_MOUTH, 'shock', { turnY: 0.4 }), 'back'], [3.3, k(AL, HANDS_FRONT, 'worried', { turnY: 0.4 })]],
      mate: [[0, k(MT + 0.3, HOLD, 'smug', { turnY: -0.5 })]] },
    world: W({ year: 1946 }, ({ t }) => <Stack x={0.3} h={lerp(0.05, 4.33 * BN, prog(t, 14.1, 15.2, 'back'))} label="LENT" />),
    hud: ({ t }) => <>
      <HP t={t} a={14.2} b={15.85} x={540} y={400}><Big top={250} main="$4.3BN" color={GOLD} size={150} sub="LENT TO BRITAIN" /></HP>
      <HP t={t} a={16.1} b={17.1} x={540} y={400}><Big top={250} main="2%" color="#ffffff" size={170} sub="A YEAR" /></HP>
    </> },
  // 8. pay it back slowly, one instalment a year (Nan pours tea (the slip); Alfie slides a small cheque; calendar ticks)
  { id: 's8', t0: 17.15, t1: 19.85, cam: [[0, m(-0.9, 4.5, 1.4)], [2.7, m(-0.85, 4.0, 1.4), 'io']],
    who: { nan: [[0, k(NN, HOLD, 'happy', { turnY: 0.3 })], [1.6, k(NN, HOLD, 'smug', { turnY: 0.3, headTilt: 6 })]],
      alf: [[0, k(AL, SLACK, 'neutral', { turnY: 0.5 })], [1.1, k(AL, SLAM, 'neutral', { turnY: 0.6, spine: 6 }), 'back'], [2.7, k(AL, HOLD1, 'thinking', { turnY: 0.4 })]] },
    world: W({ year: (t) => yearAt(t, 18.2, 19.6, 1951, 1953) }, ({ t }) => <>
      <Teapot p={[NN + 0.3, TOP + 0.22, CZ - 0.05]} tilt={0.5 * prog(t, 17.4, 18.0) * (1 - prog(t, 19.2, 19.7))} />
      <Cup p={[NN + 0.55, TOP, CZ + 0.05]} />
      <Cheque p={[lerp(-0.3, 0.75, prog(t, 18.4, 19.3, 'io')), TOP + 0.006, CZ]} s={0.7} k="chqyear" text="THIS YEAR'S" />
    </>) },
  // ---------- the what-if: timeline switch ----------
  // 9. now picture the other way (violet, crack; Alfie dreamy)
  { id: 's9', t0: 19.85, t1: 22.0, cam: [[0, c1(AL, 2.5, 1.55)], [2.15, c1(AL, 2.0, 1.6), 'io']], sw: 1, crack: { at: 0 },
    who: { alf: [[0, k(AL, SLACK, 'neutral', { turnY: 0.0 })], [0.9, k(AL, PALMS_UP, 'happy', { turnY: 0.0, shrug: 0.4, headTilt: 8 }), 'back']] },
    world: W({ year: 1946 }) },
  // 10. we borrow it, then hand it straight back (the whole LENT stack slides across to America at once)
  { id: 's10', t0: 22.0, t1: 24.3, cam: [[0, m(0.3, 5.4, 1.5)], [2.3, m(0.3, 4.9, 1.5), 'io']], sw: 1,
    who: { alf: [[0, k(AL, HANDS_FRONT, 'happy', { turnY: 0.6 })], [1.2, k(AL, SLAM, 'laugh', { turnY: 0.6, spine: 10 }), 'back']],
      mate: [[0, k(MT, SLACK, 'neutral', { turnY: -0.5 })], [1.9, k(MT, HOLD, 'happy', { turnY: -0.5 }), 'back']] },
    world: W({ year: 1946 }, ({ t }) => <Stack x={lerp(0.05, 0.6, prog(t, 23.0, 23.9, 'io'))} h={4.33 * BN} label="LENT" />) },
  // 11. America gets every dollar while it still buys a LOT (a big glowing dollar note; FULL VALUE)
  { id: 's11', t0: 24.3, t1: 27.4, cam: [[0, c1(MT - 0.1, 2.6, 1.5)], [3.1, c1(MT - 0.1, 2.1, 1.5), 'io']], sw: 1,
    who: { mate: [[0, k(MT, HOLD, 'happy', { turnY: -0.2 })], [1.6, k(MT, OPEN_ARMS, 'laugh', { turnY: -0.1, bounce: 0.04 }), 'back']] },
    world: W({ year: 1946 }, ({ t }) => <Note p={[MT - 0.5, TOP + 0.3 + 0.03 * Math.sin(t * 3), CZ]} s={lerp(0.2, 1.1, prog(t, 24.5, 25.4, 'back'))} rot={[0, 0, 0.08]} />),
    hud: ({ t }) => <HP t={t} a={26.7} b={27.35} x={540} y={330}><Tag x={540} y={250} text="FULL VALUE" c={GOLD} size={96} /></HP> },
  // ---------- back to what happened ----------
  // 12. but that's not what happened (flash back to daylight; Alfie deadpan to camera, push in)
  { id: 's12', t0: 27.4, t1: 29.4, cam: [[0, c1(AL, 2.4, 1.6)], [2.0, c1(AL, 1.8, 1.65), 'io']], crack: { at: 0, flashOnly: true },
    who: { alf: [[0, k(AL, SLACK, 'neutral', { turnY: 0.0 })], [1.1, k(AL, CROSSED, 'neutral', { turnY: 0.0, headTilt: -4 }), 'back']] },
    world: W({ year: 1951 }) },
  // 13. we paid a bit every year, for DECADES (calendar races; small cheques keep sliding across)
  { id: 's13', t0: 29.4, t1: 31.85, cam: [[0, m(0.3, 5.4, 1.75)], [2.45, m(0.3, 4.9, 1.75), 'io']],
    who: { alf: [[0, k(AL, SLAM, 'worried', { turnY: 0.6, spine: 6 })]], mate: [[0, k(MT, HOLD, 'smug', { turnY: -0.5 })]] },
    mod: { alf: (p: any, ts: number) => ({ ...p, spine: 4 + 6 * Math.max(0, Math.sin(ts * 7)) }) },
    world: W({ year: (t) => yearAt(t, 29.6, 31.7, 1953, 1989) }, ({ t }) => <>
      {[0, 1, 2, 3, 4].map((i) => { const a = 29.6 + i * 0.45; const u = prog(t, a, a + 0.4, 'io'); return u > 0 && u < 1 ? <Cheque key={i} p={[lerp(-0.3, 0.9, u), TOP + 0.006, CZ]} s={0.6} k="chqyear" text="THIS YEAR'S" /> : null; })}
    </>),
    hud: ({ t }) => <HP t={t} a={31.0} b={31.8} x={540} y={380}><Tag x={540} y={300} text="FOR DECADES" c="#fff" size={80} /></HP> },
  // 14. and while we paid, American prices ROSE (a red arrow climbs the Washington wall)
  { id: 's14', t0: 31.85, t1: 34.4, cam: [[0, m(1.3, 4.8, 1.85)], [2.55, m(1.3, 4.3, 1.9), 'io']],
    who: { mate: [[0, k(MT, SLACK, 'neutral', { turnY: -0.6 })], [1.5, k(MT, POINT, 'worried', { turnY: 0.9 }), 'back']] },
    world: (c: any) => <Hall year={yearAt(c.t, 31.9, 34.3, 1989, 1996)} arrow={prog(c.t, 32.7, 34.2, 'out') * 0.6} />,
    hud: ({ t }) => <HP t={t} a={33.7} b={34.35} x={540} y={300}><Tag x={540} y={220} text="PRICES ↑" c={RED} size={100} /></HP> },
  // 15. and rose. and ROSE! (the arrow punches up past the bunting; Mate hands on head)
  { id: 's15', t0: 34.4, t1: 36.15, cam: [[0, m(1.3, 5.2, 2.0)], [1.75, m(1.3, 4.6, 2.05), 'io']],
    who: { mate: [[0, k(MT, POINT, 'shock', { turnY: 0.9 })], [0.8, k(MT, ON_HEAD, 'scream', { turnY: 0.2, spine: -8 }), 'back']] },
    world: (c: any) => <Hall year={yearAt(c.t, 34.4, 36.1, 1996, 2006)} arrow={0.6 + 0.35 * prog(c.t, 34.6, 34.9, 'back') + 0.5 * prog(c.t, 35.3, 35.6, 'back')} />,
    hud: ({ t }) => <HP t={t} a={35.3} b={36.1} x={540} y={400}><Pop text="ROSE!" y={280} /></HP> },
  // 16. by the end, a dollar bought a TENTH of what it used to (a dollar note shrinks to a tenth)
  { id: 's16', t0: 36.15, t1: 39.1, cam: [[0, m(0.3, 5.0, 1.45)], [2.95, m(0.3, 4.5, 1.45), 'io']],
    who: { alf: [[0, k(AL, SLACK, 'neutral', { turnY: 0.6 })], [1.6, k(AL, OVER_MOUTH, 'shock', { turnY: 0.5 }), 'back']],
      mate: [[0, k(MT, CHIN, 'thinking', { turnY: -0.5 })], [1.8, k(MT, ON_HEAD, 'disbelief', { turnY: -0.5 }), 'back']] },
    world: W({}, ({ t }) => <Note p={[0.3, TOP + 0.32, CZ]} rot={[0, 0, 0]} s={lerp(1.5, 0.15, prog(t, 37.0, 38.1, 'io'))} />),
    hud: ({ t }) => <HP t={t} a={37.75} b={39.05} x={540} y={400}><Big top={260} main="1/10" color={GOLD} size={170} sub="WHAT A DOLLAR BOUGHT" /></HP> },
  // 17. so every dollar we sent back was worth LESS (Alfie slides a tiny note; Mate squints at it)
  { id: 's17', t0: 39.1, t1: 42.2, cam: [[0, c1(MT - 0.2, 2.4, 1.45)], [3.1, c1(MT - 0.2, 1.9, 1.4), 'io']],
    who: { mate: [[0, k(MT, SLACK, 'neutral', { turnY: -0.4 })], [1.0, k(MT, CHIN, 'disbelief', { turnY: -0.5, spine: 12, headTilt: 10 }), 'back']] },
    world: W({ year: 2006 }, ({ t }) => <Note p={[lerp(0.2, MT - 0.35, prog(t, 39.3, 40.2, 'out')), TOP + 0.08, CZ]} rot={[0, 0, 0]} s={0.3} />),
    hud: ({ t }) => <HP t={t} a={41.4} b={42.15} x={540} y={330}><Tag x={540} y={250} text="WORTH LESS" c={RED} size={96} /></HP> },
  // 18. in total, we sent back seven and a half billion dollars (LENT vs BACK: BACK towers)
  { id: 's18', t0: 42.2, t1: 46.0, cam: [[0, m(0.3, 5.4, 1.7)], [3.8, m(0.3, 4.9, 1.75), 'io']],
    who: { alf: [[0, k(AL - 0.4, SLACK, 'neutral', { turnY: 0.5 })], [2.4, k(AL - 0.4, OPEN_ARMS, 'shock', { turnY: 0.4 }), 'back']],
      mate: [[0, k(MT + 0.5, SLACK, 'neutral', { turnY: -0.5 })], [2.8, k(MT + 0.5, OPEN_ARMS, 'laugh', { turnY: -0.4, bounce: 0.04 }), 'back']] },
    world: W({ year: 2006 }, ({ t }) => <><Stack x={0.1} h={4.33 * BN} label="LENT" /><Stack x={0.5} h={lerp(0.05, 7.5 * BN, prog(t, 42.6, 45.3, 'out'))} label="BACK" /></>),
    hud: ({ t }) => <HP t={t} a={44.6} b={45.95} x={540} y={330}><Big top={200} main="$7.5BN" color={GOLD} size={150} sub="SENT BACK IN TOTAL" /></HP> },
  // 19. sounds like a win for THEM (Mate smug, arms crossed, little bounce)
  { id: 's19', t0: 46.0, t1: 47.65, cam: [[0, c1(MT, 2.3, 1.55)], [1.65, c1(MT, 1.9, 1.6), 'io']],
    who: { mate: [[0, k(MT, CROSSED, 'smug', { turnY: -0.2, headTilt: -8 })], [0.8, k(MT, CROSSED, 'laugh', { turnY: -0.2, bounce: 0.03 }), 'back']] },
    world: W({ year: 2006 }) },
  // 20. but count it in the dollars they lent (Alfie raises a finger; the BACK stack starts to deflate)
  { id: 's20', t0: 47.65, t1: 50.2, cam: [[0, m(0.3, 5.4, 1.6)], [2.55, m(0.3, 4.9, 1.6), 'io']],
    who: { alf: [[0, k(AL - 0.4, SLACK, 'neutral', { turnY: 0.4 })], [0.7, k(AL - 0.4, FIST1, 'smug', { turnY: 0.3 }), 'back']],
      mate: [[0, k(MT + 0.5, CROSSED, 'smug', { turnY: -0.5 })], [2.0, k(MT + 0.5, CROSSED, 'worried', { turnY: -0.5 }), 'back']] },
    world: W({ year: 1946 }, ({ t }) => <><Stack x={0.1} h={4.33 * BN} label="LENT" /><Stack x={0.5} h={lerp(7.5 * BN, 6.0 * BN, prog(t, 49.0, 50.2, 'io'))} label="BACK" /></>),
    hud: ({ t }) => <HP t={t} a={48.7} b={50.15} x={540} y={300}><Tag x={540} y={220} text="IN 1946 DOLLARS" c="#fff" size={78} /></HP> },
  // 21. it's worth about two and a half BILLION (hero: BACK shrinks below LENT; ≈$2.5BN; Mate screams)
  { id: 's21', t0: 50.2, t1: 53.3, cam: [[0, m(0.3, 5.4, 1.55)], [3.1, m(0.3, 4.9, 1.5), 'io']],
    who: { alf: [[0, k(AL - 0.4, FIST1, 'smug', { turnY: 0.3 })], [2.2, k(AL - 0.4, OPEN_ARMS, 'laugh', { turnY: 0.3 }), 'back']],
      mate: [[0, k(MT + 0.5, CROSSED, 'worried', { turnY: -0.5 })], [2.1, k(MT + 0.5, ON_HEAD, 'scream', { turnY: -0.4, spine: -8 }), 'back']] },
    world: W({ year: 1946 }, ({ t }) => <><Stack x={0.1} h={4.33 * BN} label="LENT" /><Stack x={0.5} h={lerp(6.0 * BN, 2.5 * BN, prog(t, 50.4, 52.2, 'io'))} label="BACK" /></>),
    hud: ({ t }) => <HP t={t} a={52.15} b={53.25} x={540} y={330}><Big top={190} main="$2.5BN" color={GOLD} size={150} sub="ROUGHLY, IN 1946 DOLLARS" /></HP> },
  // 22. our rough sum. little more than HALF. (Alfie shrugs, honest; OUR ROUGH SUM label)
  { id: 's22', t0: 53.3, t1: 55.8, cam: [[0, c1(AL, 2.4, 1.55)], [2.5, c1(AL, 1.9, 1.6), 'io']],
    who: { alf: [[0, k(AL, HOLD1, 'thinking', { turnY: 0.1 })], [1.1, k(AL, PALMS_UP, 'smug', { turnY: 0.1, shrug: 0.6, headTilt: 6 }), 'back']] },
    world: W({ year: 2006 }),
    hud: ({ t }) => <><HP t={t} a={53.5} b={54.4} x={540} y={330}><Tag x={540} y={260} text="OUR ROUGH SUM" c="#fff" size={78} /></HP>
      <HP t={t} a={54.95} b={55.75} x={540} y={330}><Tag x={540} y={260} text="JUST OVER HALF" c={GOLD} size={84} /></HP></> },
  // 23. Britain got a cheap loan (Alfie grins, thumbs up energy)
  { id: 's23', t0: 55.8, t1: 57.3, cam: [[0, m(AL, 3.4, 1.5)], [1.5, m(AL, 3.0, 1.55), 'io']],
    who: { alf: [[0, k(AL, HOLD1, 'happy', { turnY: 0.2 })], [0.6, k(AL, FIST1, 'laugh', { turnY: 0.2, bounce: 0.04 }), 'back']] },
    world: W({ year: 2006 }) },
  // 24. America got paid in shrinking dollars (Mate holds up a tiny note, glum)
  { id: 's24', t0: 57.3, t1: 59.7, cam: [[0, c1(MT, 2.3, 1.5)], [2.4, c1(MT, 1.9, 1.5), 'io']],
    who: { mate: [[0, k(MT, HOLD1, 'sad', { turnY: -0.2 })], [1.5, k(MT, HOLD1, 'worried', { turnY: -0.2, headTilt: 8 }), 'back']] },
    world: W({ year: 2006 }, ({ t }) => <Note p={[MT + 0.3, 1.5, 0.35]} rot={[0, -0.2, 0]} s={lerp(0.9, 0.3, prog(t, 58.3, 59.3, 'io'))} />) },
  // 25. honestly? Britain won that one. (Alfie laughs, fist up; Nan claps behind)
  { id: 's25', t0: 59.7, t1: 62.1, cam: [[0, m(-0.9, 4.6, 1.5)], [2.4, m(-0.9, 4.1, 1.5), 'io']],
    who: { alf: [[0, k(AL, HOLD1, 'thinking', { turnY: 0.0, headTilt: 6 })], [0.8, k(AL, FIST1, 'laugh', { turnY: 0.0, bounce: 0.04 }), 'back']],
      nan: [[0, k(NN, HOLD, 'happy', { turnY: 0.3 })]] },
    mod: { nan: (p: any, ts: number) => ({ ...p, elL: p.elL + 18 * Math.max(0, Math.sin(ts * 14)), elR: p.elR + 18 * Math.max(0, Math.sin(ts * 14)) }) },
    world: W({ year: 2006 }, () => <><Teapot p={[NN + 0.3, TOP + 0.13, CZ - 0.05]} /><Cup p={[NN + 0.55, TOP, CZ + 0.05]} /></>),
    hud: ({ t }) => <HP t={t} a={61.3} b={62.05} x={540} y={330}><Tag x={540} y={250} text="BRITAIN WON?" c={GOLD} size={90} /></HP> },
  // 26. Britain or America? (face-off across the counter)
  { id: 's26', t0: 62.1, t1: 63.55, cam: [[0, m(0.3, 5.4, 1.55)], [1.45, m(0.3, 4.9, 1.55), 'io']],
    who: { alf: [[0, k(AL, CROSSED, 'smug', { turnY: 0.7 })]], mate: [[0, k(MT, CROSSED, 'angry', { turnY: -0.7 })]] },
    hud: ({ t }) => <HP t={t} a={62.3} b={63.5} x={540} y={330}><Tag x={540} y={250} text="WHO WON?" c="#fff" size={100} /></HP>,
    world: W({ year: 2006 }) },
  // 27. send this to an American, and ask them (Alfie turns to us and points; Mate glares)
  { id: 's27', t0: 63.55, t1: 65.9, cam: [[0, c1(AL + 0.1, 2.9, 1.55)], [2.35, c1(AL + 0.1, 2.5, 1.6), 'io']],
    who: { alf: [[0, k(AL, CROSSED, 'smug', { turnY: 0.4 })], [0.5, k(AL, POINT, 'laugh', { turnY: -0.6, shR: A2(80, 30) }), 'back']],
      mate: [[0, k(MT, CROSSED, 'angry', { turnY: -0.5 })]] },
    world: W({ year: 2006 }) },
  // end card
  { id: 'e', t0: 65.9, t1: 68.9, cam: [[0, m(0.3, 5.4, 1.5)], [3.0, m(0.3, 4.9, 1.5), 'io']],
    who: { alf: [[0, k(AL, FIST1, 'laugh', { turnY: 0.4 })]], mate: [[0, k(MT, CROSSED, 'angry', { turnY: -0.5 })]], nan: [[0, k(NN, HOLD, 'happy', { turnY: 0.3 })]] },
    world: W({ year: 2006 }) },
];

const { Comp, frames } = makeShotEpisode({
  id: 'ep20', shots, words: words as any, total: 68.9, endAt: 65.9, day: true,
  endSub: 'BRITAIN OR AMERICA?',
});
export const ep20 = { id: 'ep20', Comp, frames };
