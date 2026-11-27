// North Sea worlds (built 7 Nov 2026 for Ep 05). Generic: no company logo, no real platform design.
//   sea    : the giant gas cupboard standing in the North Sea (the hero), or a shelf of jars on the water
//   rig    : a gas platform in the rain, a steel door stencilled ROUGH, rows of lights that go out
//   cavern : the rock cavern under the seabed (the bottom half of the cupboard), a valve on the pipe
//   shore  : a Yorkshire seafront: promenade, railing, pastel terrace; a tiny rig or tanker on the horizon
// Everything is a pure function of time (t = episode seconds, lt = shot seconds).
import React from 'react';
import * as THREE from 'three';
import { B, Bg, Cyl, Pane, rnd } from './kit';
import { textTexture } from '../kit/text';
import { JarShelf, GasJar } from '../props';

type V3 = [number, number, number];
const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const inOut = (u: number) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2);
const ramp = (lt: number, at?: [number, number]) => (at ? inOut(clamp((lt - at[0]) / Math.max(0.01, at[1] - at[0]))) : 1);
const anim = (v: number, to: number | undefined, lt: number, at?: [number, number]) => (to === undefined ? v : v + (to - v) * ramp(lt, at));

/** Low-poly North Sea: a displaced plane, flat-shaded, rebuilt each frame from t. */
const Waves: React.FC<{ t: number; size?: number; seg?: number; c?: string; z?: number; amp?: number }> = ({ t, size = 120, seg = 70, c = '#3D5766', z = 0, amp = 0.35 }) => {
  const geo = React.useMemo(() => new THREE.PlaneGeometry(size, size, seg, seg), [size, seg]);
  const pos = geo.attributes.position as THREE.BufferAttribute;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), y = pos.getY(i);
    pos.setZ(i, amp * (Math.sin(x * 0.55 + t * 1.3) * 0.6 + Math.sin(y * 0.8 - t * 1.7 + x * 0.2) * 0.5 + Math.sin((x + y) * 1.6 + t * 2.4) * 0.18));
  }
  pos.needsUpdate = true;
  geo.computeVertexNormals();
  return (
    <mesh geometry={geo} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, z]}>
      <meshStandardMaterial color={c} roughness={0.55} metalness={0.1} flatShading />
    </mesh>
  );
};

/** Rain streaks around a point (falling, wind-slanted). */
const Rain: React.FC<{ t: number; at?: V3; w?: number; h?: number; d?: number; n?: number; k?: number }> = ({ t, at = [0, 0, 0], w = 16, h = 14, d = 16, n = 140, k = 1 }) => (
  <group position={at}>
    {Array.from({ length: Math.round(n * k) }).map((_, i) => {
      const y = h - (((rnd(i, 1) * h) + t * 11) % h);
      return (
        <mesh key={i} position={[(rnd(i, 2) - 0.5) * w + y * 0.12, y, (rnd(i, 3) - 0.5) * d]} rotation={[0, 0, 0.12]}>
          <boxGeometry args={[0.018, 0.55, 0.018]} />
          <meshBasicMaterial color="#C9D6DE" transparent opacity={0.45} />
        </mesh>
      );
    })}
  </group>
);

/** Gulls: a flat V that flaps, circling. */
const Gulls: React.FC<{ t: number; at?: V3; n?: number; r?: number; s?: number }> = ({ t, at = [0, 9, -2], n = 3, r = 5, s = 1 }) => (
  <group position={at}>
    {Array.from({ length: n }).map((_, i) => {
      const a = t * 0.5 + (i * Math.PI * 2) / n;
      const flap = Math.sin(t * 9 + i * 2) * 0.5;
      return (
        <group key={i} position={[Math.cos(a) * r, Math.sin(t * 0.7 + i) * 0.6 + i * 0.5, Math.sin(a) * r * 0.5]} rotation={[0, -a, 0]} scale={s}>
          {[-1, 1].map((sd) => (
            <mesh key={sd} position={[sd * 0.22, 0, 0]} rotation={[0, 0, sd * flap]}>
              <boxGeometry args={[0.44, 0.02, 0.12]} />
              <meshStandardMaterial color="#F4F4F0" roughness={0.8} />
            </mesh>
          ))}
          <mesh><boxGeometry args={[0.1, 0.08, 0.3]} /><meshStandardMaterial color="#EDEDE8" /></mesh>
        </group>
      );
    })}
  </group>
);

const Overcast: React.FC<{ top?: string; fog?: string; near?: number; far?: number; sun?: number }> = ({ top = '#8C99A3', fog = '#8C99A3', near = 18, far = 90, sun = 1.1 }) => (
  <>
    <Bg color={top} fog={[fog, near, far]} />
    <hemisphereLight args={['#DDE6EE', '#2E3B44', 0.75]} />
    <ambientLight intensity={0.3} />
    <directionalLight position={[-6, 12, 10]} intensity={sun} color="#F2F0EA" />
    <directionalLight position={[8, 4, -6]} intensity={0.4} color="#AFC4D8" />
  </>
);

// ---------------- the giant cupboard ----------------
export const CUPBOARD = { at: [0, 0, -4] as V3, w: 6.2, h: 9.2, d: 2.4, legs: 1.6 };
/** A kitchen wall cupboard the size of a tower block. 12 jars on 4 shelves (3 each), counted from the top:
 *  jar i glows when i < lit (a fractional lit half-fills the last one). bottom: pulse the bottom half (Rough's half). */
const GiantCupboard: React.FC<{ t: number; lt: number; open: number; lit: number; empty?: boolean; bottom?: number; moth?: number }> = ({ t, lt, open, lit, empty = false, bottom = 0, moth }) => {
  const { w, h, d, legs } = CUPBOARD;
  const body = '#EFE7D6', door = '#7E9A86', trim = '#D9CFBB';
  const innerW = w - 0.4, comp = (h - 0.4) / 4;
  const ang = open * 1.95;
  const mk = moth === undefined ? -1 : clamp((lt - moth) / 1.0);
  return (
    <group position={CUPBOARD.at}>
      {/* legs into the sea, waves slapping */}
      {[[-w / 2 + 0.4, -d / 2 + 0.4], [w / 2 - 0.4, -d / 2 + 0.4], [-w / 2 + 0.4, d / 2 - 0.4], [w / 2 - 0.4, d / 2 - 0.4]].map(([x, z], i) => (
        <group key={i}>
          <Cyl p={[x, legs / 2 - 1, z]} r={0.32} h={legs + 2} c="#BFB6A4" />
          <mesh position={[x, 0.05 + Math.sin(t * 2.6 + i) * 0.12, z]} rotation={[-Math.PI / 2, 0, 0]}>
            <ringGeometry args={[0.34, 0.75 + 0.15 * Math.sin(t * 3 + i * 2), 16]} />
            <meshBasicMaterial color="#E8EEF2" transparent opacity={0.7} />
          </mesh>
        </group>
      ))}
      <group position={[0, legs, 0]}>
        {/* carcass: back, sides, top, bottom; a cornice and plinth */}
        <B p={[0, h / 2, -d / 2 + 0.1]} s={[w, h, 0.2]} c="#E2D8C4" />
        {[-1, 1].map((sd) => <B key={sd} p={[sd * (w / 2 - 0.1), h / 2, 0]} s={[0.2, h, d]} c={body} />)}
        <B p={[0, h - 0.1, 0]} s={[w, 0.2, d]} c={body} />
        <B p={[0, 0.1, 0]} s={[w, 0.2, d]} c={body} />
        <B p={[0, h + 0.12, 0.05]} s={[w + 0.4, 0.24, d + 0.3]} c={trim} />
        <B p={[0, -0.1, 0.05]} s={[w + 0.2, 0.2, d + 0.2]} c={trim} />
        {/* shelves and jars */}
        {[1, 2, 3].map((k) => <B key={k} p={[0, 0.2 + k * comp, 0]} s={[innerW, 0.12, d - 0.3]} c="#E9E0CC" />)}
        <pointLight position={[0, h * 0.55, d / 2 - 0.2]} intensity={empty ? 2 : 6 + 10 * clamp(lit / 12)} distance={14} color="#6FB8FF" />
        {!empty ? Array.from({ length: 12 }).map((_, i) => {
          const row = Math.floor(i / 3), col = i % 3; // row 0 = top
          const f = clamp(lit - i);
          const pulse = row >= 2 ? bottom * (0.5 + 0.5 * Math.sin(t * 7)) : 0;
          return (
            <group key={i} position={[(col - 1) * (innerW / 3), 0.26 + (3 - row) * comp, 0.1]}>
              <GasJar s={1.45} fill={f} glow={1 + pulse * 1.5} dim={bottom > 0 && row < 2 ? 0.45 : 1} />
            </group>
          );
        }) : null}
        {/* a moth flies out of the empty cupboard */}
        {mk >= 0 && mk < 1 ? (
          <group position={[Math.sin(mk * 9) * 0.8, h * 0.5 + mk * 1.5, d / 2 + 0.5 + mk * 5]} rotation={[0, 0, Math.sin(t * 40) * 0.5]} scale={2.6}>
            {[-1, 1].map((sd) => <mesh key={sd} position={[sd * 0.18, 0, 0]} rotation={[0, 0, sd * Math.sin(t * 40) * 0.8]}><boxGeometry args={[0.32, 0.02, 0.24]} /><meshStandardMaterial color="#8C8270" /></mesh>)}
          </group>
        ) : null}
        {/* doors, hinged on the outer edges */}
        {[-1, 1].map((sd) => (
          <group key={sd} position={[sd * (w / 2), 0.1, d / 2]} rotation={[0, sd * ang, 0]}>
            <group position={[-sd * (w / 4), (h - 0.2) / 2, 0.06]}>
              <B p={[0, 0, 0]} s={[w / 2 - 0.04, h - 0.2, 0.12]} c={door} r={0.6} />
              <B p={[0, 0, 0.07]} s={[w / 2 - 0.6, h - 0.9, 0.04]} c="#8DAA95" r={0.6} />
              <B p={[-sd * (w / 4 - 0.35), 0, 0.12]} s={[0.12, 0.9, 0.1]} c="#C9B27A" m={0.7} r={0.3} />
            </group>
          </group>
        ))}
      </group>
    </group>
  );
};

/** The sea with the giant cupboard (default) or a shelf of jars standing on the water (shelf: 'uk' | 'germany'). */
export const Sea: React.FC<{ t: number; lt?: number; open?: number; openTo?: number; openAt?: [number, number]; lit?: number; litTo?: number; litAt?: [number, number];
  empty?: boolean; bottom?: number; moth?: number; shelf?: 'uk' | 'germany'; tag?: boolean; tagAt?: [number, number]; rain?: number }> = ({
  t, lt = 0, open = 1, openTo, openAt, lit = 12, litTo, litAt, empty, bottom = 0, moth, shelf, tag = false, tagAt = [0.1, 0.8], rain = 0.6,
}) => {
  const o = anim(open, openTo, lt, openAt);
  const l = anim(lit, litTo, lt, litAt);
  const tk = ramp(lt, tagAt);
  const tagTex = tag ? textTexture('bigtag2bn', { w: 512, h: 320, bg: '#F6D33C', border: '#1E1E1E', lines: [{ text: '£2BN', x: 256, y: 165, size: 170, color: '#1E1E1E', weight: 800 }] }) : null;
  return (
    <group>
      <Overcast />
      <Waves t={t} />
      <Gulls t={t} at={[0, 12.5, -3]} n={3} r={6} s={1.6} />
      {rain > 0 ? <Rain t={t} at={[0, 0, 2]} k={rain} w={20} d={14} /> : null}
      {shelf ? (
        <group position={[0, 0.15, 0]}>
          {shelf === 'uk'
            ? <JarShelf n={12} lit={12} label="UK" sub="12 DAYS" s={1} dir="z" signS={1.0} />
            : <group position={[3.2, 0, 0]}><JarShelf n={100} lit={100} label="GERMANY" sub="100+ DAYS" s={1} dir="z" signS={2.2} /></group>}
        </group>
      ) : (
        <GiantCupboard t={t} lt={lt} open={o} lit={l} empty={empty} bottom={bottom} moth={moth} />
      )}
      {tagTex ? (
        // the price tag unrolls down the left door, top to bottom
        <group position={[-1.6, CUPBOARD.legs + CUPBOARD.h * (0.95 - 0.45 * tk), CUPBOARD.at[2] + CUPBOARD.d / 2 + 0.6]} rotation={[0, 0.25, 0]}>
          <mesh scale={[1, Math.max(0.05, tk), 1]}><planeGeometry args={[4.2, 2.6]} /><meshStandardMaterial map={tagTex} color="#ffffff" roughness={0.6} side={THREE.DoubleSide} /></mesh>
        </group>
      ) : null}
    </group>
  );
};

// ---------------- the rig ----------------
export const RIG = { deck: 5.2, door: [0.6, 5.2, 1.52] as V3 };
const stencil = () => textTexture('roughdoor', { w: 512, h: 768, bg: '#5E6A72',
  draw: (g) => { g.fillStyle = '#4C575F'; for (let i = 0; i < 6; i++) g.fillRect(30, 40 + i * 120, 452, 6); g.fillStyle = '#C9A13A'; g.fillRect(0, 700, 512, 68);
    g.fillStyle = '#1E1E1E'; for (let i = 0; i < 8; i++) { g.beginPath(); g.moveTo(i * 70, 768); g.lineTo(i * 70 + 35, 700); g.lineTo(i * 70 + 70, 700); g.lineTo(i * 70 + 35, 768); g.fill(); } },
  lines: [{ text: 'ROUGH', x: 256, y: 300, size: 150, color: '#F2F0EA', weight: 800, font: 'JetBrains Mono' }] });
const permitTex = () => textTexture('permitapril', { w: 400, h: 520, bg: '#F2EEE4', border: '#1E1E1E',
  draw: (g) => { g.fillStyle = '#BDB7AA'; for (let i = 0; i < 6; i++) g.fillRect(50, 330 + i * 26, 300, 10); g.fillStyle = '#C0272D'; g.fillRect(0, 0, 400, 70); },
  lines: [{ text: 'PERMIT', x: 200, y: 38, size: 44, color: '#FFFFFF', weight: 800 }, { text: 'APRIL', x: 200, y: 190, size: 112, color: '#1E1E1E', weight: 800 }] });

export const Rig: React.FC<{ t: number; lt?: number; off?: [number, number]; dark?: boolean; permit?: boolean; slam?: number; rain?: number }> = ({ t, lt = 0, off, dark = false, permit = true, slam, rain = 1 }) => {
  const D = RIG.deck;
  const rows = 4;
  const offK = dark ? 1 : off ? clamp((lt - off[0]) / Math.max(0.01, off[1] - off[0])) : 0;
  const door = stencil();
  const ptx = permit ? permitTex() : null;
  const slamK = slam === undefined ? 1 : clamp((lt - slam) / 0.18);
  return (
    <group>
      <Overcast top={dark ? '#4A5560' : '#7F8D98'} fog={dark ? '#4A5560' : '#7F8D98'} sun={dark ? 0.6 : 1.0} />
      <Waves t={t} c="#344D5B" amp={0.45} />
      <Rain t={t} at={[0, 0, 4]} k={rain} w={22} h={16} d={18} n={170} />
      <Gulls t={t} at={[-2, 14, -1]} n={4} r={7} s={1.4} />
      {/* four legs with cross-bracing */}
      {[[-3, -2], [3, -2], [-3, 2], [3, 2]].map(([x, z], i) => <Cyl key={i} p={[x, D / 2 - 1.5, z]} r={0.45} h={D + 3} c="#D8B23A" rough={0.6} />)}
      {[-2, 2].map((z) => <B key={z} p={[0, 1.6, z]} s={[6, 0.18, 0.18]} c="#B8952E" rot={[0, 0, 0.45]} />)}
      {[-3, 3].map((x) => <B key={x} p={[x, 1.6, 0]} s={[0.18, 0.18, 4]} c="#B8952E" rot={[0.5, 0, 0]} />)}
      {/* deck, railing */}
      <B p={[0, D - 0.2, 0]} s={[8, 0.4, 6]} c="#5D646B" />
      {Array.from({ length: 17 }).map((_, i) => <B key={i} p={[-4 + i * 0.5, D + 0.5, 2.95]} s={[0.05, 1, 0.05]} c="#E0B83C" />)}
      <B p={[0, D + 1.0, 2.95]} s={[8, 0.07, 0.07]} c="#E0B83C" />
      {/* the cabin with the steel door */}
      <B p={[-0.4, D + 1.5, 0]} s={[4.6, 3, 3]} c="#E9E4D8" />
      <B p={[-0.4, D + 3.05, 0]} s={[4.8, 0.12, 3.2]} c="#B8B0A0" />
      <Pane p={[-1.9, D + 1.9, 1.52]} w={1.1} h={0.7} lit={dark ? 0.02 : 0.6 * (1 - offK)} frame="#C9C4BA" />
      <group position={RIG.door}>
        <mesh position={[0, 1.15, 0.01]}>
          <planeGeometry args={[1.25, 2.3]} />
          <meshStandardMaterial map={door ?? undefined} color="#ffffff" roughness={0.45} metalness={0.4} />
        </mesh>
        {ptx ? (
          <group position={[0.32, 0.95, 0.05]} rotation={[0.25 * Math.sin(t * 7) * slamK, 0, 0.12 * Math.sin(t * 5.3)]}>
            <mesh position={[0, -0.32, 0]}><planeGeometry args={[0.5, 0.65]} /><meshStandardMaterial map={ptx} color="#ffffff" roughness={0.8} side={THREE.DoubleSide} /></mesh>
            <B p={[0, 0, 0.005]} s={[0.22, 0.05, 0.01]} c="#D9D2B8" />
          </group>
        ) : null}
      </group>
      {/* the derrick: a lattice tower with rows of lights */}
      <group position={[2.4, D, -1]}>
        {[[-0.7, -0.7], [0.7, -0.7], [-0.7, 0.7], [0.7, 0.7]].map(([x, z], i) => <B key={i} p={[x * (1 - 0.0), 4.5, z]} s={[0.12, 9, 0.12]} c="#C8402E" rot={[0, 0, -x * 0.02]} />)}
        {Array.from({ length: 9 }).map((_, i) => <B key={i} p={[0, 0.6 + i, 0.7]} s={[1.4, 0.06, 0.06]} c="#C8402E" rot={[0, 0, i % 2 ? 0.6 : -0.6]} />)}
        {Array.from({ length: rows }).map((_, r) => {
          const on = 1 - clamp(offK * rows - (rows - 1 - r)); // top row goes out first
          return Array.from({ length: 4 }).map((_, k) => (
            <mesh key={`${r}${k}`} position={[-0.75 + k * 0.5, 1.6 + r * 2.1, 0.85]}>
              <sphereGeometry args={[0.13, 10, 8]} />
              <meshStandardMaterial color={on > 0.5 ? '#FFF4D0' : '#3A3A3A'} emissive="#FFD27A" emissiveIntensity={on * 3} />
            </mesh>
          ));
        })}
        {offK < 0.99 ? <pointLight position={[0, 5, 2]} intensity={8 * (1 - offK)} distance={14} color="#FFD27A" /> : null}
      </group>
      {/* deck floodlights */}
      {[-3.6, 3.6].map((x, i) => {
        const on = 1 - clamp(offK * 4 - 3.2 - i * 0.3);
        return (
          <group key={x} position={[x, D + 1.6, 2.6]}>
            <Cyl p={[0, -0.8, 0]} r={0.05} h={1.6} c="#2B2F36" />
            <mesh><boxGeometry args={[0.4, 0.3, 0.2]} /><meshStandardMaterial color="#DDD" emissive="#FFE9B0" emissiveIntensity={on * 2.5} /></mesh>
          </group>
        );
      })}
    </group>
  );
};

// ---------------- the cavern under the sea ----------------
export const Cavern: React.FC<{ t: number; lt?: number; lit?: number; litTo?: number; litAt?: [number, number]; valve?: [number, number] }> = ({ t, lt = 0, lit = 6, litTo, litAt, valve }) => {
  const l = anim(lit, litTo, lt, litAt);
  const vk = valve ? ramp(lt, valve) : 0;
  return (
    <group>
      <Bg color="#0A1820" fog={['#0A1820', 6, 22]} />
      <hemisphereLight args={['#8FB8D0', '#3A3028', 1.0]} />
      <ambientLight intensity={0.5} />
      <directionalLight position={[2, 6, 5]} intensity={1.2} color="#A8C8DC" />
      <pointLight position={[-2, 2.5, 2.5]} intensity={4} distance={9} color="#9FC8E0" />
      <pointLight position={[0, 1.6, 1.8]} intensity={2 + 3 * clamp(l / 6)} distance={8} color="#6FB8FF" />
      {/* rock: floor, roof and lumpy walls */}
      <B p={[0, -0.1, 0]} s={[16, 0.2, 14]} c="#3A3530" r={0.95} />
      {Array.from({ length: 34 }).map((_, i) => {
        const a = (i / 34) * Math.PI * 1.25 - Math.PI * 0.125;
        const R = 3.4 + rnd(i, 4) * 1.4;
        return (
          <mesh key={i} position={[Math.cos(a) * R * 1.3, Math.sin(a) * R * 0.9 + 0.4, -1.8 - rnd(i, 5) * 1.6]} rotation={[rnd(i, 6) * 3, rnd(i, 7) * 3, 0]}>
            <dodecahedronGeometry args={[0.9 + rnd(i, 8) * 0.8, 0]} />
            <meshStandardMaterial color={i % 3 ? '#4A4239' : '#5A5046'} roughness={1} flatShading />
          </mesh>
        );
      })}
      {Array.from({ length: 10 }).map((_, i) => (
        <mesh key={`f${i}`} position={[-4 + i * 0.9, 0.2, 1.6 + rnd(i, 9) * 1.5]}>
          <dodecahedronGeometry args={[0.25 + rnd(i, 10) * 0.35, 0]} />
          <meshStandardMaterial color="#4E463D" roughness={1} flatShading />
        </mesh>
      ))}
      {/* the rock shelf with six jars: Rough's half of the cupboard */}
      <B p={[0, 0.55, -0.4]} s={[4.6, 0.18, 1.2]} c="#6A6055" r={0.95} />
      {Array.from({ length: 6 }).map((_, i) => (
        <group key={i} position={[-1.9 + i * 0.76, 0.64, -0.4]}>
          <GasJar s={0.5} fill={clamp(l - i)} />
        </group>
      ))}
      {/* the pipe up to the sea, and its valve wheel */}
      <Cyl p={[2.6, 2.4, 0.2]} r={0.16} h={4.8} c="#8E8A80" m={0.5} rough={0.5} />
      <Cyl p={[1.1, 1.15, -1.1]} r={0.16} h={3.0} c="#8E8A80" m={0.5} rough={0.5} rot={[0, 0, Math.PI / 2]} />
      <Cyl p={[2.6, 1.15, -0.45]} r={0.16} h={1.3} c="#8E8A80" m={0.5} rough={0.5} rot={[Math.PI / 2, 0, 0]} />
      <group position={[2.6, 1.3, 0.42]} rotation={[0, 0, -vk * Math.PI * 3]}>
        <mesh><torusGeometry args={[0.42, 0.05, 8, 24]} /><meshStandardMaterial color="#C8102E" roughness={0.5} /></mesh>
        {[0, 1, 2].map((k) => <B key={k} p={[0, 0, 0]} s={[0.84, 0.05, 0.05]} c="#C8102E" rot={[0, 0, (k * Math.PI) / 3]} />)}
        <Cyl p={[0, 0, -0.05]} r={0.09} h={0.12} c="#2B2F36" rot={[Math.PI / 2, 0, 0]} />
      </group>
      {/* bubbles drift up while the gas still flows */}
      {Array.from({ length: 16 }).map((_, i) => {
        const y = ((rnd(i, 11) * 5 + t * 1.2) % 5);
        return (vk < 0.9 ? (
          <mesh key={`b${i}`} position={[2.6 + (rnd(i, 12) - 0.5) * 0.6, y, 0.5 + (rnd(i, 13) - 0.5) * 0.4]}>
            <sphereGeometry args={[0.04 + rnd(i, 14) * 0.04, 8, 6]} />
            <meshStandardMaterial color="#CFEFFF" transparent opacity={0.5 * (1 - vk)} />
          </mesh>) : null);
      })}
    </group>
  );
};

// ---------------- the Yorkshire seafront ----------------
const PASTEL = ['#E8C9B0', '#BFD6D9', '#E9E1B8', '#D8C2D9', '#C7DABC', '#EDE6DA'];
/** Promenade along x at z 0..2; the sea is +z (toward a camera looking back at the town); the terrace stands at z -3.
 *  rig: a tiny platform on the horizon; tanker: a tiny ship on the horizon (0..1 how far it has come). */
export const Shore: React.FC<{ t: number; lt?: number; rig?: boolean; tanker?: number; dusk?: number }> = ({ t, rig = false, tanker, dusk = 0.2 }) => (
  <group>
    <Bg color={dusk > 0.5 ? '#5C6578' : '#9AA6B0'} fog={[dusk > 0.5 ? '#5C6578' : '#9AA6B0', 30, 170]} />
    <hemisphereLight args={['#E2E8EE', '#3A3E44', 0.75]} />
    <ambientLight intensity={0.3} />
    <directionalLight position={[-5, 10, 12]} intensity={1.1} color="#FFF0DC" />
    <directionalLight position={[6, 5, -10]} intensity={0.45} color="#B8CCE0" />
    {/* the sea, out to the horizon on +z */}
    <group position={[0, -1.2, 62]}><Waves t={t} size={130} seg={60} amp={0.3} /></group>
    {/* sea wall, promenade, railing */}
    <B p={[0, -0.6, 2.4]} s={[60, 1.4, 0.6]} c="#9C968A" />
    <B p={[0, -0.05, 0.4]} s={[60, 0.1, 4.6]} c="#C9C2B4" />
    {Array.from({ length: 41 }).map((_, i) => <B key={i} p={[-20 + i, 0.5, 2.3]} s={[0.06, 1, 0.06]} c="#2F5D7C" />)}
    <B p={[0, 1.0, 2.3]} s={[60, 0.08, 0.1]} c="#2F5D7C" />
    <B p={[0, 0.55, 2.3]} s={[60, 0.05, 0.06]} c="#2F5D7C" />
    {/* the terrace across the road, every window lit */}
    <B p={[0, -0.05, -2.2]} s={[60, 0.1, 3.4]} c="#4A4F55" />
    {Array.from({ length: 9 }).map((_, i) => {
      const x = -14 + i * 3.5;
      return (
        <group key={i} position={[x, 0, -5]}>
          <B p={[0, 3.6, 0]} s={[3.46, 7.2, 3]} c={PASTEL[i % PASTEL.length]} />
          <B p={[0, 7.3, 0]} s={[3.6, 0.25, 3.2]} c="#4A4E57" />
          <B p={[-0.9, 1.1, 1.52]} s={[0.9, 2.1, 0.08]} c={['#1F3A5F', '#7A2E2E', '#2E5A3E'][i % 3]} />
          {[[0.7, 1.5], [-0.9, 4.0], [0.7, 4.0], [-0.9, 6.0], [0.7, 6.0]].map(([wx, wy], k) => (
            <Pane key={k} p={[wx, wy, 1.53]} w={1.0} h={1.1} lit={0.35 + dusk * 0.6 * (rnd(i, k) > 0.2 ? 1 : 0.2)} frame="#F4F1EA" />
          ))}
        </group>
      );
    })}
    {/* lamp posts on the prom */}
    {[-6.5, 6.5].map((x) => (
      <group key={x} position={[x, 0, 1.9]}>
        <Cyl p={[0, 1.8, 0]} r={0.06} h={3.6} c="#2F5D7C" />
        <mesh position={[0, 3.7, 0]}><sphereGeometry args={[0.16, 12, 8]} /><meshStandardMaterial color="#FFF2D0" emissive="#FFD27A" emissiveIntensity={0.4 + dusk} /></mesh>
      </group>
    ))}
    <Gulls t={t} at={[2, 5, 6]} n={3} r={4} s={0.8} />
    {/* on the horizon */}
    {rig ? (
      <group position={[-6, -1.2, 110]} scale={0.9}>
        {[[-2, 0], [2, 0]].map(([x], i) => <Cyl key={i} p={[x, 2, 0]} r={0.3} h={4} c="#3E4650" />)}
        <B p={[0, 4.2, 0]} s={[6, 0.6, 3]} c="#3E4650" />
        <B p={[-0.5, 5.4, 0]} s={[3, 1.8, 2]} c="#4A525C" />
        <B p={[2, 7.5, 0]} s={[0.4, 6, 0.4]} c="#3E4650" />
        <mesh position={[2, 10.6, 0]}><sphereGeometry args={[0.35, 8, 6]} /><meshStandardMaterial color="#FFE9B0" emissive="#FFD27A" emissiveIntensity={2} /></mesh>
      </group>
    ) : null}
    {tanker !== undefined ? (
      <group position={[4 - tanker * 3, -1.0, 120 - tanker * 25]} scale={1.2}>
        <B p={[0, 0.8, 0]} s={[12, 1.6, 2.6]} c="#2A3440" />
        <B p={[0, 1.65, 0]} s={[11.4, 0.1, 2.4]} c="#7A2E2E" />
        <B p={[-4.6, 2.8, 0]} s={[2.2, 2.2, 2.2]} c="#E9E4D8" />
        {[-2, 0, 2].map((x) => <mesh key={x} position={[x, 2.0, 0]}><sphereGeometry args={[0.6, 12, 8]} /><meshStandardMaterial color="#D9D4C8" /></mesh>)}
        <mesh position={[-4.6, 4.2, 0]}><sphereGeometry args={[0.18, 8, 6]} /><meshStandardMaterial color="#FFF" emissive="#FFEFC0" emissiveIntensity={2.5 + Math.sin(t * 4)} /></mesh>
      </group>
    ) : null}
  </group>
);
