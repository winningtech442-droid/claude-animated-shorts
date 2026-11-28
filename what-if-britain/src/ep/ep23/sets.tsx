// EP23 Pay Later (global edition): this episode's guests, sets and hero props (v3: built for the story, retired after).
// Metres, floor y = 0, the camera mostly at +z looking -z. Invented names and signs only: the store is "HARGREAVES",
// no real shop, brand, logo or pay-later provider. Prices in dollars (the global edition, SCRIPT.md).
import React from 'react';
import * as THREE from 'three';
import { textTexture } from '../../kit/text';
import { Bg } from '../../worlds/kit';
import { M, Bx, canvasTex, mixC } from '../ep21/sets';
import { lerp, clamp } from '../kit3';
import type { Look } from '../../cast/Person';

type V3 = [number, number, number];
const PI = Math.PI;

// ---------- this episode's guests (two new silhouettes, SCRIPT.md) ----------
/** The pay-later Rep: short and square, barrel chest, no neck, slicked hair, a huge grin; teal gilet, white shirt. */
export const REP: Look = {
  name: 'Rep', skin: '#D9A47E', skinShade: '#C48D68', hair: '#17110D', hairStyle: 'crop', eyes: '#3A2A1E',
  jacket: '#1E8C84', jacketTrim: '#14655F', top: '#F7F6F0', legs: '#2B3140', shoes: '#8A5A32', sole: '#3A2416',
  height: 1.56, build: 1.2, collar: 'suit', shoulders: 1.32, chest: 1.4, legLen: 0.78, limbs: 1.08, head: 1.04, neck: 0.15, chin: 0.25,
};
/** The store Owner: pear-shaped (narrow sloping shoulders, wide hips), bald with a grey horseshoe, walrus moustache,
 *  brown shop coat, glasses. */
export const OWNER: Look = {
  name: 'Owner', skin: '#EBC2A4', skinShade: '#D5AA8A', hair: '#8E867C', hairStyle: 'bald', sideHair: '#A39C92', moustache: '#9A9288',
  eyes: '#4A5A6A', jacket: '#8A6A48', jacketTrim: '#6E5236', top: '#EEE8DA', legs: '#4A4038', shoes: '#2E241C', sole: '#1E1814',
  height: 1.72, build: 1.0, collar: 'suit', shoulders: 0.76, hips: 1.5, belly: 0.3, glasses: true, head: 1.05, chin: 0.45,
};
/** Background shoppers in the what-if store (extras, not guests). */
export const SHOPPERS: Look[] = [
  { name: 'Shopper1', skin: '#7A4E34', skinShade: '#663F29', hair: '#141010', hairStyle: 'crop', eyes: '#2A1E16', jacket: '#D9762B', jacketTrim: '#B05E20', top: '#F2EEE4', legs: '#2E3A52', shoes: '#F1EEE6', sole: '#D6D1C6', height: 1.8, build: 1.0, collar: 'hoodie' },
  { name: 'Shopper2', skin: '#F0CFB8', skinShade: '#DDB69C', hair: '#C9A15A', hairStyle: 'bun', eyes: '#3E5A6A', jacket: '#4E7A3A', jacketTrim: '#3C5E2C', top: '#EDE6D8', legs: '#3A3530', shoes: '#3A2C22', sole: '#2A201A', height: 1.66, build: 0.9, collar: 'harrington' },
  { name: 'Shopper3', skin: '#C59270', skinShade: '#AE7C5C', hair: '#3A2A20', hairStyle: 'quiff', eyes: '#3A2A1E', jacket: '#6A4E9A', jacketTrim: '#523C78', top: '#D9D4C8', legs: '#22242A', shoes: '#2B2B2E', sole: '#E7E3DA', height: 1.74, build: 1.05, collar: 'hoodie' },
];

// ---------- textures ----------
const sign = (key: string, w: number, h: number, bg: string, lines: { text: string; y: number; size: number; color: string }[], border?: string) =>
  textTexture(key, { w, h, bg, border, lines: lines.map((l) => ({ ...l, x: w / 2, weight: 900 })) });
export const Plane: React.FC<{ p: V3; w: number; h: number; tex: THREE.Texture | null; rot?: V3; glow?: boolean; o?: number }> = ({ p, w, h, tex, rot, glow, o = 1 }) => (
  <mesh position={p} rotation={rot}><planeGeometry args={[w, h]} />{glow ? <meshBasicMaterial map={tex ?? undefined} toneMapped={false} transparent={o < 1} opacity={o} /> : <M c="#ffffff" map={tex} r={0.7} o={o} />}</mesh>
);
const tiles = () => canvasTex('ep23tiles', 256, 256, (g) => {
  g.fillStyle = '#EDE6D8'; g.fillRect(0, 0, 256, 256);
  for (let y = 0; y < 2; y++) for (let x = 0; x < 2; x++) { g.fillStyle = (x + y) % 2 ? '#E2D9C6' : '#F2ECE0'; g.fillRect(x * 128 + 2, y * 128 + 2, 124, 124); }
  for (let i = 0; i < 500; i++) { g.fillStyle = ['rgba(150,120,90,.10)', 'rgba(90,90,110,.08)', 'rgba(255,255,255,.18)'][i % 3]; g.fillRect((i * 53) % 256, (i * 89) % 256, 3, 3); }
}, [6, 6]);
const wallTex = () => canvasTex('ep23wall', 256, 256, (g) => {
  g.fillStyle = '#F1E7D3'; g.fillRect(0, 0, 256, 256);
  g.fillStyle = '#E6D9BF'; for (let x = 0; x < 256; x += 64) g.fillRect(x, 0, 4, 256);
}, [5, 2]);
const saleBanner = () => sign('ep23sale', 1024, 300, '#D7262E', [{ text: 'SALE', y: 160, size: 230, color: '#FFFFFF' }]);
const laterBanner = () => sign('ep23laterbanner', 1024, 300, '#2A1E66', [{ text: 'PAY LATER', y: 160, size: 190, color: '#7FFFEA' }]);
const storeSign = () => sign('ep23store', 1024, 160, '#1F2F4F', [{ text: 'HARGREAVES', y: 84, size: 110, color: '#F3E3B4' }]);
const deptSign = (t: string) => sign(`ep23dept${t}`, 512, 128, '#F7F2E6', [{ text: t, y: 66, size: 70, color: '#1F2F4F' }], '#1F2F4F');
export const screenTex = (t: string, bg = '#0E3B36', fg = '#7FFFEA') => sign(`ep23scr${t}${bg}`, 512, 320, bg, [{ text: t, y: 165, size: t.length > 7 ? 92 : 128, color: fg }]);
const tagTex = (t: string) => sign(`ep23tag${t}`, 256, 384, '#FFFFFF', [{ text: t, y: 230, size: 104, color: '#111111' }], '#111111');

// ---------- light rig: a bright store, morning ----------
export const StoreLights: React.FC<{ sw: number; dim?: number }> = ({ sw, dim = 0 }) => (
  <>
    <ambientLight intensity={0.62 * (1 - 0.5 * dim)} color={mixC('#FFF4E4', '#C2B8FF', sw)} />
    <hemisphereLight args={[mixC('#FFF6EA', '#AFC5FF', sw), mixC('#9A8A72', '#55498A', sw), 0.85]} />
    <directionalLight position={[2.4, 5.0, 4.2]} intensity={1.45 * (1 - 0.6 * dim)} color={mixC('#FFEAD0', '#C6CCFF', sw)} />
    <directionalLight position={[-2.6, 3.4, -3.6]} intensity={0.95} color={mixC('#FFFFFF', '#8FF0E0', sw)} />
  </>
);

// ---------- the hero prop: a red puffer jacket that rips into four ----------
const RED = '#D6262C', RED_D = '#A81C22';
/** One quilted puffer panel: flattened rolls with dark stitch seams between them, wider at the shoulder. */
const Panel: React.FC<{ w: number; h: number; n: number; side: 1 | -1 }> = ({ w, h, n, side }) => (
  <group>
    {Array.from({ length: n }).map((_, i) => {
      const k = i / (n - 1), ww = w * (0.9 + 0.12 * k), y = -h / 2 + (i + 0.5) * (h / n);
      return (
        <group key={i} position={[side * (ww - w) * 0.5, y, 0]}>
          <mesh rotation={[0, 0, PI / 2]} scale={[1, 1, 0.55]}><capsuleGeometry args={[h / n / 2, Math.max(0.001, ww - h / n), 6, 16]} /><M c={i % 2 ? RED : mixC(RED, '#ffffff', 0.07)} r={0.42} /></mesh>
          {i > 0 ? <Bx p={[0, -h / n / 2, 0.012]} s={[ww * 0.98, 0.006, 0.05]} c={RED_D} /> : null}
        </group>
      );
    })}
  </group>
);
/** A sleeve: a quilted tube with a black cuff, hanging from the shoulder. */
const Sleeve: React.FC<{ side: 1 | -1 }> = ({ side }) => (
  <group rotation={[0, 0, side * 0.3]}>
    <mesh position={[0, -0.2, 0]}><capsuleGeometry args={[0.055, 0.3, 6, 14]} /><M c={RED} r={0.42} /></mesh>
    {[0, 1, 2].map((i) => <mesh key={i} position={[0, -0.1 - i * 0.1, 0]} rotation={[PI / 2, 0, 0]}><torusGeometry args={[0.057, 0.005, 6, 18]} /><M c={RED_D} /></mesh>)}
    <mesh position={[0, -0.39, 0]}><cylinderGeometry args={[0.048, 0.048, 0.05, 14]} /><M c="#1E1E22" r={0.7} /></mesh>
  </group>
);
/** The jacket, about 0.6 m tall, front to camera. rip 0..1 sends four parts apart (sleeves out, body halves apart) with a
 *  puff of stuffing; tag shows the $100 tag swinging (tagSwing radians). */
export const Jacket: React.FC<{ rip?: number; tag?: boolean; tagSwing?: number; s?: number }> = ({ rip = 0, tag = true, tagSwing = 0, s = 1 }) => {
  const u = clamp(rip), e = u * (2 - u);
  const half = (side: 1 | -1) => (
    <group position={[side * (0.115 + 0.22 * e), 0.06 * e, 0.04 * e]} rotation={[0.3 * e, side * 0.4 * e, side * 0.5 * e]}>
      <Panel w={0.23} h={0.52} n={5} side={side} />
      <Bx p={[-side * 0.11, 0, 0.035]} s={[0.012, 0.52, 0.012]} c="#C9CED6" />
      <mesh position={[-side * 0.05, 0.285, 0]} rotation={[0, 0, side * 0.2]}><boxGeometry args={[0.11, 0.06, 0.08]} /><M c="#1E1E22" r={0.6} /></mesh>
      <mesh position={[side * 0.02, 0.3, -0.06]} scale={[0.95, 0.75, 0.75]}><sphereGeometry args={[0.1, 16, 12, side > 0 ? 0 : PI, PI]} /><M c={RED_D} r={0.5} /></mesh>
    </group>
  );
  return (
    <group scale={s}>
      {half(-1)}{half(1)}
      {[-1, 1].map((side) => (
        <group key={side} position={[side * (0.25 + 0.38 * e), 0.24 + 0.18 * e, -0.01]} rotation={[0.5 * e, 0, side * (0.15 + 1.2 * e)]}>
          <Sleeve side={side as 1 | -1} />
        </group>
      ))}
      {u > 0 && u < 0.98 ? Array.from({ length: 9 }).map((_, i) => (
        <mesh key={i} position={[(i - 4) * 0.05 * (1 + e), 0.1 + ((i * 37) % 9) * 0.03 + 0.3 * e, 0.12 + 0.1 * e]} scale={0.6 + 1.2 * e * (1 - u)}>
          <sphereGeometry args={[0.03, 10, 8]} /><M c="#F4F1EA" r={0.9} />
        </mesh>
      )) : null}
      {tag && rip <= 0 ? (
        <group position={[0.17, 0.12, 0.05]} rotation={[0, 0, tagSwing]}>
          <mesh position={[0, -0.05, 0]}><cylinderGeometry args={[0.002, 0.002, 0.1, 6]} /><M c="#222" /></mesh>
          <group position={[0, -0.15, 0.003]}><Plane p={[0, 0, 0]} w={0.1} h={0.15} tex={tagTex('$100')} /></group>
        </group>
      ) : null}
    </group>
  );
};
/** One quarter of the ripped jacket (to hold or wear): a sleeve or a body half. */
export const JacketPiece: React.FC<{ kind: 'sleeve' | 'half'; side?: 1 | -1; s?: number }> = ({ kind, side = 1, s = 1 }) => (
  <group scale={s}>
    {kind === 'sleeve' ? <Sleeve side={side} /> : (
      <group><Panel w={0.23} h={0.52} n={5} side={side} /><Bx p={[-side * 0.11, 0, 0.035]} s={[0.012, 0.52, 0.012]} c="#C9CED6" /></group>
    )}
  </group>
);
/** The $100 tag torn in four, fluttering down from `from` to the floor over u 0..1. */
export const TornTag: React.FC<{ u: number; from: V3 }> = ({ u, from }) => (
  <group>
    {[0, 1, 2, 3].map((i) => {
      const k = clamp(u * (1 - i * 0.06)), dx = (i - 1.5) * 0.09, flt = Math.sin(k * PI * (2.5 + i * 0.4) + i) * 0.06;
      const y = lerp(from[1], 0.004, k * k * (3 - 2 * k));
      return (
        <group key={i} position={[from[0] + dx * (0.4 + k) + flt, y, from[2] + 0.05 * i * k]} rotation={[k < 1 ? 1.2 * Math.sin(k * 9 + i) : -PI / 2, k * 4 + i, k < 1 ? 0.6 * Math.cos(k * 7 + i) : i]}>
          <mesh><planeGeometry args={[0.055, 0.08]} /><M c="#ffffff" r={0.7} side={THREE.DoubleSide} /></mesh>
          <Plane p={[0, 0, 0.001]} w={0.055} h={0.08} tex={tagTex(['$1', '00', '$', '1'][i])} />
        </group>
      );
    })}
  </group>
);

// ---------- the till: a counter with a card reader (normal) or the giant PAY LATER button (what-if) ----------
export const TILL = { x: 0.85, z: -0.35, top: 0.98 };
export const CardReader: React.FC<{ text?: string; lit?: number }> = ({ text = 'PAY IN 4', lit = 1 }) => (
  <group>
    <Bx p={[0, 0.03, 0]} s={[0.1, 0.06, 0.16]} c="#26272B" r={0.4} />
    <group position={[0, 0.1, -0.02]} rotation={[-0.5, 0, 0]}>
      <Bx p={[0, 0, 0]} s={[0.11, 0.16, 0.025]} c="#1C1D21" r={0.4} />
      <Plane p={[0, 0.02, 0.0135]} w={0.09} h={0.085} tex={screenTex(text)} glow o={lit} />
    </group>
  </group>
);
/** A big red dome button on a pedestal with its label: press 0..1 pushes it in. */
export const PayLaterButton: React.FC<{ press?: number; s?: number }> = ({ press = 0, s = 1 }) => (
  <group scale={s}>
    <mesh position={[0, 0.05, 0]}><cylinderGeometry args={[0.16, 0.18, 0.1, 28]} /><M c="#2A1E66" r={0.4} /></mesh>
    <mesh position={[0, 0.11 - 0.04 * press, 0]} scale={[1, 0.55, 1]}><sphereGeometry args={[0.13, 28, 16, 0, PI * 2, 0, PI / 2]} /><M c="#E8263A" e="#FF3344" ei={0.25 + 0.6 * press} r={0.25} /></mesh>
    <group position={[0, 0.11, 0.2]} rotation={[-0.35, 0, 0]}><Plane p={[0, 0, 0]} w={0.36} h={0.11} tex={sign('ep23btnlbl', 512, 156, '#2A1E66', [{ text: 'PAY LATER', y: 80, size: 92, color: '#7FFFEA' }])} glow /></group>
  </group>
);
export const Till: React.FC<{ later?: boolean; reader?: string; press?: number; drawer?: number }> = ({ later = false, reader = 'PAY IN 4', press = 0, drawer = 0 }) => (
  <group position={[TILL.x, 0, TILL.z]}>
    {/* counter body: white front, navy kick and top */}
    <Bx p={[0, 0.46, 0]} s={[1.7, 0.92, 0.62]} c="#F4F1EA" r={0.6} />
    <Bx p={[0, 0.05, 0.02]} s={[1.72, 0.1, 0.6]} c="#1F2F4F" />
    <Bx p={[0, 0.95, 0]} s={[1.78, 0.06, 0.68]} c="#1F2F4F" r={0.35} />
    <Bx p={[0, 0.62, 0.315]} s={[1.6, 0.05, 0.01]} c="#B3262E" />
    {later ? (
      <>
        <group position={[0.15, TILL.top, 0.08]}><PayLaterButton press={press} /></group>
        {/* where the cash drawer was: an empty slot */}
        <Bx p={[-0.45, 0.8, 0.312]} s={[0.5, 0.12, 0.01]} c="#3A3D46" />
        <group position={[-0.5, TILL.top + 0.17, -0.12]}><Bx p={[0, 0, 0]} s={[0.36, 0.24, 0.03]} c="#1C1D21" /><Plane p={[0, 0, 0.016]} w={0.33} h={0.2} tex={screenTex('$0 TODAY')} glow /></group>
      </>
    ) : (
      <>
        <group position={[0.15, TILL.top, 0.12]}><CardReader text={reader} /></group>
        {/* the till and its cash drawer */}
        <Bx p={[-0.45, TILL.top + 0.09, -0.05]} s={[0.42, 0.18, 0.36]} c="#3A3D46" r={0.5} />
        <Bx p={[-0.45, TILL.top + 0.03, 0.15 + 0.2 * drawer]} s={[0.4, 0.07, 0.3]} c="#2A2C33" r={0.5} />
        <group position={[-0.45, TILL.top + 0.3, -0.1]} rotation={[-0.2, 0, 0]}><Bx p={[0, 0, 0]} s={[0.3, 0.2, 0.03]} c="#1C1D21" /><Plane p={[0, 0, 0.016]} w={0.27} h={0.16} tex={screenTex('$100', '#0E2A3B', '#FFE27A')} glow /></group>
      </>
    )}
  </group>
);

// ---------- clothes rail with coats ----------
const COATS = ['#2E5E8C', '#E3C04A', '#4E7A3A', '#8A3A5A', '#E8E2D2', '#2B2B2E', '#C86A2E'];
export const Rail: React.FC<{ p: V3; ry?: number; n?: number; seed?: number; gap?: number }> = ({ p, ry = 0, n = 7, seed = 0, gap = -1 }) => (
  <group position={p} rotation={[0, ry, 0]}>
    <mesh position={[0, 1.45, 0]} rotation={[0, 0, PI / 2]}><cylinderGeometry args={[0.015, 0.015, 1.5, 10]} /><M c="#C9CED6" m={0.8} r={0.25} /></mesh>
    {[-0.72, 0.72].map((x) => <mesh key={x} position={[x, 0.72, 0]}><cylinderGeometry args={[0.015, 0.015, 1.45, 10]} /><M c="#C9CED6" m={0.8} r={0.25} /></mesh>)}
    {[-0.72, 0.72].map((x) => <Bx key={`f${x}`} p={[x, 0.02, 0]} s={[0.06, 0.04, 0.5]} c="#9EA4AE" />)}
    {Array.from({ length: n }).map((_, i) => i === gap ? null : (
      <group key={i} position={[-0.6 + (i * 1.2) / (n - 1), 0.98, 0]} rotation={[0, PI / 2 + ((i * 7 + seed) % 5 - 2) * 0.06, 0]}>
        <mesh position={[0, 0.45, 0]} rotation={[0, 0, PI / 2]}><torusGeometry args={[0.03, 0.004, 6, 12, PI]} /><M c="#C9CED6" m={0.8} /></mesh>
        <Bx p={[0, 0.0, 0]} s={[0.07, 0.86, 0.42]} c={COATS[(i + seed) % COATS.length]} r={0.75} />
        <Bx p={[0.04, 0.32, 0]} s={[0.02, 0.14, 0.16]} c={mixC(COATS[(i + seed) % COATS.length], '#000000', 0.15)} />
      </group>
    ))}
  </group>
);

// ---------- bulky things the what-if shoppers carry off ----------
export const Telly: React.FC<{ s?: number }> = ({ s = 1 }) => (
  <group scale={s}>
    <Bx p={[0, 0, 0]} s={[0.95, 0.6, 0.14]} c="#C9A877" r={0.85} />
    <Plane p={[0, 0.02, 0.071]} w={0.7} h={0.4} tex={sign('ep23tvbox', 512, 300, '#C9A877', [{ text: 'TV', y: 150, size: 200, color: '#1F2F4F' }])} />
  </group>
);
export const Sofa: React.FC<{ s?: number; c?: string }> = ({ s = 1, c = '#3A6A8C' }) => (
  <group scale={s}>
    <Bx p={[0, 0.22, 0]} s={[1.7, 0.26, 0.75]} c={c} r={0.9} />
    <Bx p={[0, 0.55, -0.3]} s={[1.7, 0.5, 0.18]} c={c} r={0.9} />
    {[-1, 1].map((k) => <Bx key={k} p={[k * 0.8, 0.42, 0]} s={[0.16, 0.4, 0.75]} c={mixC(c, '#000000', 0.12)} r={0.9} />)}
    {[-0.42, 0.42].map((x) => <Bx key={x} p={[x, 0.39, 0.03]} s={[0.8, 0.1, 0.66]} c={mixC(c, '#ffffff', 0.12)} r={0.9} />)}
  </group>
);
export const Fridge: React.FC<{ s?: number }> = ({ s = 1 }) => (
  <group scale={s}><Bx p={[0, 0.85, 0]} s={[0.6, 1.7, 0.6]} c="#E9ECEF" r={0.3} /><Bx p={[0.24, 1.15, 0.305]} s={[0.03, 0.4, 0.02]} c="#9EA4AE" /><Bx p={[0, 1.08, 0.302]} s={[0.6, 0.012, 0.01]} c="#B8BEC6" /></group>
);
export const Gnome: React.FC<{ s?: number }> = ({ s = 1 }) => (
  <group scale={s}>
    <mesh position={[0, 0.12, 0]}><cylinderGeometry args={[0.07, 0.09, 0.22, 14]} /><M c="#3A6AC2" r={0.6} /></mesh>
    <mesh position={[0, 0.27, 0]}><sphereGeometry args={[0.06, 14, 12]} /><M c="#F0C7A8" r={0.6} /></mesh>
    <mesh position={[0, 0.23, 0.03]} scale={[1, 1.2, 0.8]}><sphereGeometry args={[0.055, 12, 10]} /><M c="#F4F1EA" r={0.9} /></mesh>
    <mesh position={[0, 0.39, 0]}><coneGeometry args={[0.065, 0.2, 14]} /><M c="#D6262C" r={0.6} /></mesh>
  </group>
);
export const JetSki: React.FC<{ s?: number }> = ({ s = 1 }) => (
  <group scale={s}>
    <mesh position={[0, 0.25, 0]} scale={[1, 0.5, 0.45]}><sphereGeometry args={[0.7, 24, 16]} /><M c="#F2F2EE" r={0.3} /></mesh>
    <mesh position={[0.05, 0.42, 0]} scale={[0.55, 0.3, 0.3]}><sphereGeometry args={[0.6, 20, 14]} /><M c="#E8263A" r={0.3} /></mesh>
    <Bx p={[-0.25, 0.55, 0]} s={[0.4, 0.08, 0.22]} c="#1E1E22" r={0.6} />
    <Bx p={[0.3, 0.62, 0]} s={[0.06, 0.12, 0.42]} c="#26272B" />
  </group>
);
export const BoxPile: React.FC<{ n?: number; seed?: number }> = ({ n = 5, seed = 0 }) => (
  <group>
    {Array.from({ length: n }).map((_, i) => {
      const w = 0.28 + ((i * 13 + seed) % 5) * 0.05, h = 0.2 + ((i * 7 + seed) % 4) * 0.06;
      return <Bx key={i} p={[((i * 29 + seed) % 5 - 2) * 0.08, 0.1 + i * 0.19, ((i * 17) % 3 - 1) * 0.05]} s={[w, h, 0.3]} c={['#C9A877', '#B89464', '#D9BC8C'][i % 3]} r={0.9} rot={[0, ((i * 11) % 7 - 3) * 0.08, 0]} />;
    })}
  </group>
);

// ---------- the store floor: rails, an escalator, the SALE banner, the till ----------
/** later: the what-if store (PAY LATER banner and button, no cash drawer). Children are placed in store space. */
export const SaleFloor: React.FC<{ sw?: number; later?: boolean; press?: number; reader?: string; drawer?: number; railGap?: number; children?: React.ReactNode }> = ({ sw = 0, later = false, press = 0, reader, drawer = 0, railGap = -1, children }) => {
  const fl = tiles(), wl = wallTex();
  return (
    <group>
      <StoreLights sw={sw} />
      <Bg color={mixC('#F4ECDD', '#5D55A8', sw)} />
      {/* floor, back wall, side wall */}
      <mesh rotation={[-PI / 2, 0, 0]} position={[0, 0, 0]}><planeGeometry args={[14, 12]} /><M c="#ffffff" map={fl} r={0.35} /></mesh>
      <mesh position={[0, 2.2, -4.2]}><planeGeometry args={[14, 4.4]} /><M c="#ffffff" map={wl} r={0.9} /></mesh>
      <mesh position={[-4.6, 2.2, 0]} rotation={[0, PI / 2, 0]}><planeGeometry args={[12, 4.4]} /><M c="#ffffff" map={wl} r={0.9} /></mesh>
      {/* ceiling light panels */}
      {[-2.4, 0, 2.4].map((x) => [-2.6, -0.4, 1.8].map((z) => (
        <mesh key={`${x}${z}`} position={[x, 3.6, z]} rotation={[PI / 2, 0, 0]}><planeGeometry args={[1.2, 0.5]} /><meshBasicMaterial color={mixC('#FFF8EC', '#CFC8FF', sw)} toneMapped={false} /></mesh>
      )))}
      {/* the banner and the store name */}
      <Bx p={[0.4, 3.3, -4.15]} s={[3.6, 1.05, 0.04]} c={later ? '#2A1E66' : '#D7262E'} />
      <Plane p={[0.4, 3.3, -4.12]} w={3.4} h={1.0} tex={later ? laterBanner() : saleBanner()} glow={later} />
      <Plane p={[2.6, 3.0, -4.17]} w={2.0} h={0.32} tex={storeSign()} />
      <Plane p={[2.6, 2.45, -4.17]} w={1.0} h={0.25} tex={deptSign('COATS')} />
      {/* the front of the store (seen in reverse shots): big windows on a bright street, the entrance doors */}
      <mesh position={[0, 2.2, 5.2]} rotation={[0, PI, 0]}><planeGeometry args={[14, 4.4]} /><M c="#ffffff" map={wl} r={0.9} /></mesh>
      {[-3.3, -1.1, 3.3].map((x, i) => (
        <group key={i} position={[x, 1.55, 5.17]}>
          <Bx p={[0, 0, 0]} s={[1.9, 2.3, 0.06]} c="#1F2F4F" />
          <mesh position={[0, 0, -0.04]} rotation={[0, PI, 0]}><planeGeometry args={[1.75, 2.15]} /><meshBasicMaterial color={mixC('#DCEFFF', '#9FFFF0', sw)} toneMapped={false} /></mesh>
        </group>
      ))}
      <group position={[1.1, 1.2, 5.17]}>
        <Bx p={[0, 0.05, 0]} s={[1.5, 2.5, 0.06]} c="#C9A43A" />
        <mesh position={[0, 0.05, -0.04]} rotation={[0, PI, 0]}><planeGeometry args={[1.38, 2.38]} /><meshBasicMaterial color={mixC('#E8F4FF', '#AFFFF2', sw)} toneMapped={false} /></mesh>
        <Bx p={[0, 0.05, -0.05]} s={[0.04, 2.38, 0.02]} c="#C9A43A" />
      </group>
      <mesh position={[4.6, 2.2, 0]} rotation={[0, -PI / 2, 0]}><planeGeometry args={[12, 4.4]} /><M c="#ffffff" map={wl} r={0.9} /></mesh>
      <Rail p={[-3.4, 0, 3.6]} ry={-0.2} seed={4} />
      <Rail p={[2.4, 0, 3.0]} ry={0.25} seed={6} />
      <Plane p={[-4.57, 2.6, 2.4]} w={1.0} h={0.25} rot={[0, PI / 2, 0]} tex={deptSign('MENS')} />
      {/* the escalator rising at the back left */}
      <group position={[-2.6, 0, -2.9]} rotation={[0, 0.25, 0]}>
        <mesh position={[0, 1.15, 0]} rotation={[0, 0, 0.6]}><boxGeometry args={[3.6, 0.35, 1.0]} /><M c="#B8BEC6" m={0.6} r={0.35} /></mesh>
        {[-1, 1].map((k) => (
          <mesh key={k} position={[0, 1.55, k * 0.52]} rotation={[0, 0, 0.6]}><boxGeometry args={[3.6, 0.6, 0.04]} /><meshStandardMaterial color={mixC('#CFE8F2', '#9FFFF0', sw)} transparent opacity={0.3} roughness={0.05} depthWrite={false} /></mesh>
        ))}
        {[-1, 1].map((k) => <mesh key={`h${k}`} position={[0, 1.88, k * 0.52]} rotation={[0, 0, 0.6]}><boxGeometry args={[3.7, 0.05, 0.06]} /><M c="#1E1E22" r={0.5} /></mesh>)}
      </group>
      {/* pillars */}
      {[[-3.4, -1.0], [3.3, -1.6]].map(([x, z], i) => <Bx key={i} p={[x, 2.0, z]} s={[0.5, 4.0, 0.5]} c="#E9E1D0" />)}
      {/* rails of coats */}
      <Rail p={[-1.25, 0, -0.9]} ry={0.15} seed={0} gap={railGap} />
      <Rail p={[-0.6, 0, -2.7]} ry={-0.1} seed={3} />
      <Rail p={[2.6, 0, -2.6]} ry={0.35} seed={5} />
      <Rail p={[-3.0, 0, 0.9]} ry={1.3} seed={2} />
      <Till later={later} reader={reader} press={press} drawer={drawer} />
      {/* contact shadow under the till */}
      <mesh rotation={[-PI / 2, 0, 0]} position={[TILL.x, 0.004, TILL.z]}><planeGeometry args={[2.0, 0.95]} /><meshBasicMaterial color="#000" transparent opacity={0.1} depthWrite={false} /></mesh>
      {children}
    </group>
  );
};
