// EP22 Typed Money: the sets for this episode (v3: built for the story, retired after it). Metres, floor y = 0.
// The bank front faces +z (the camera stands in the street looking -z); the revolving door turns about (0, 0, DOOR.z).
// Invented names and signs only: the bank is "THRIFTWELL BANK", no real bank, logo or banknote design.
import React from 'react';
import * as THREE from 'three';
import { Coin } from '../../props';
import { textTexture } from '../../kit/text';
import { Bg } from '../../worlds/kit';
import { M, Bx, canvasTex, mixC } from '../ep21/sets';
import { lerp } from '../kit3';
import type { Look } from '../../cast/Person';

type V3 = [number, number, number];
const PI = Math.PI;

// ---------- this episode's guests (two new silhouettes, see SCRIPT.md) ----------
export const MANAGER: Look = {
  name: 'Manager', skin: '#EDC3A6', skinShade: '#D8AA8C', hair: '#6E5A48', hairStyle: 'bald', eyes: '#4A4A5A',
  jacket: '#2E3346', jacketTrim: '#262A3A', top: '#F2EFE8', legs: '#2E3346', shoes: '#1E1A18', sole: '#151210',
  height: 1.74, build: 1.15, collar: 'suit', belly: 1, limbs: 0.72, legLen: 0.92, head: 1.08, chin: 1,
};
export const BUILDER: Look = {
  name: 'Builder', skin: '#C98A64', skinShade: '#B27652', hair: '#2A1E16', hairStyle: 'bald', eyes: '#3A2A1E',
  jacket: '#F2D31C', jacketTrim: '#C9CDD2', top: '#5A6270', legs: '#3E4A5E', shoes: '#6B4A2E', sole: '#2A1E14',
  height: 1.76, build: 0.82, collar: 'hoodie', limbs: 0.78, head: 0.96,
};
// background savers in the what-if bank hall (each holding a jar)
export const SAVERS: Look[] = [
  { name: 'Saver1', skin: '#F0CDB4', skinShade: '#DDB49A', hair: '#B8B2A8', hairStyle: 'grey', eyes: '#4A5A6A', jacket: '#7A8C5A', jacketTrim: '#5E6E44', top: '#EDE6D8', legs: '#4A4440', shoes: '#3A2C22', sole: '#2A201A', height: 1.62, build: 1.05, collar: 'cardigan', stoop: 0.3 },
  { name: 'Saver2', skin: '#6E4630', skinShade: '#5C3A28', hair: '#151010', hairStyle: 'bun', eyes: '#2A1E16', jacket: '#B5473A', jacketTrim: '#8E362C', top: '#F4EEE2', legs: '#26324A', shoes: '#F1EEE6', sole: '#D6D1C6', height: 1.68, build: 0.92, collar: 'harrington' },
  { name: 'Saver3', skin: '#E2B08E', skinShade: '#CC9A78', hair: '#C77B3A', hairStyle: 'crop', eyes: '#3E5A3A', jacket: '#3A5E8C', jacketTrim: '#2E4A70', top: '#D9D4C8', legs: '#5A5040', shoes: '#2B2B2E', sole: '#E7E3DA', height: 1.9, build: 0.9, collar: 'hoodie', legLen: 1.08, head: 0.95 },
];

// ---------- textures ----------
const sign = (key: string, w: number, h: number, bg: string, lines: { text: string; y: number; size: number; color: string }[], border?: string) =>
  textTexture(key, { w, h, bg, border, lines: lines.map((l) => ({ ...l, x: w / 2, weight: 800 })) });
const Sign: React.FC<{ p: V3; w: number; h: number; tex: THREE.Texture | null; rot?: V3; glow?: boolean }> = ({ p, w, h, tex, rot, glow }) => (
  <mesh position={p} rotation={rot}><planeGeometry args={[w, h]} />{glow ? <meshBasicMaterial map={tex ?? undefined} toneMapped={false} /> : <M c="#ffffff" map={tex} r={0.7} />}</mesh>
);
const stone = () => canvasTex('ep22stone', 256, 256, (g) => {
  g.fillStyle = '#E6DCC6'; g.fillRect(0, 0, 256, 256);
  g.strokeStyle = '#CFC3A8'; g.lineWidth = 3;
  for (let y = 0; y <= 256; y += 64) { g.beginPath(); g.moveTo(0, y); g.lineTo(256, y); g.stroke(); }
  for (let y = 0; y < 256; y += 64) for (let x = (y / 64) % 2 ? 64 : 0; x <= 256; x += 128) { g.beginPath(); g.moveTo(x, y); g.lineTo(x, y + 64); g.stroke(); }
  for (let i = 0; i < 700; i++) { g.fillStyle = i % 2 ? 'rgba(120,100,70,.06)' : 'rgba(255,255,240,.08)'; g.fillRect((i * 53) % 256, (i * 97) % 256, 3, 3); }
}, [4, 3]);
const paving = () => canvasTex('ep22paving', 128, 128, (g) => {
  g.fillStyle = '#B9B6AE'; g.fillRect(0, 0, 128, 128); g.strokeStyle = '#9C998F'; g.lineWidth = 3;
  for (let i = 0; i <= 128; i += 64) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i, 128); g.moveTo(0, i); g.lineTo(128, i); g.stroke(); }
  for (let i = 0; i < 300; i++) { g.fillStyle = 'rgba(80,80,80,.07)'; g.fillRect((i * 41) % 128, (i * 73) % 128, 2, 2); }
}, [7, 5]);
const shutterTex = () => canvasTex('ep22shutter', 128, 128, (g) => {
  g.fillStyle = '#9EA4AE'; g.fillRect(0, 0, 128, 128);
  for (let y = 0; y < 128; y += 16) { g.fillStyle = '#7E848E'; g.fillRect(0, y + 12, 128, 4); g.fillStyle = '#B7BCC4'; g.fillRect(0, y, 128, 3); }
}, [1, 8]);
const brick = () => canvasTex('ep22brick', 256, 256, (g) => {
  g.fillStyle = '#B9C2C6'; g.fillRect(0, 0, 256, 256);
  for (let y = 0; y < 256; y += 32) for (let x = (y / 32) % 2 ? -32 : 0; x < 256; x += 64) {
    g.fillStyle = ['#A8573E', '#B5634A', '#9C4E37', '#AE5B42'][((x + y) / 32) & 3]; g.fillRect(x + 2, y + 2, 60, 28);
  }
}, [3, 4]);
const marble = () => canvasTex('ep22marble', 256, 256, (g) => {
  for (let y = 0; y < 4; y++) for (let x = 0; x < 4; x++) { g.fillStyle = (x + y) % 2 ? '#EDE7DA' : '#2F3A4A'; g.fillRect(x * 64, y * 64, 64, 64); }
}, [6, 6]);
/** The coins seen through the frosted glass: a dense pile of gold, silver and copper discs. */
const coinMass = () => canvasTex('ep22coinmass', 256, 256, (g) => {
  g.fillStyle = '#7A6334'; g.fillRect(0, 0, 256, 256);
  const cols = ['#D9B45A', '#C9A548', '#B9BCC0', '#C77F4A', '#E3C46E', '#A9ADB2'];
  for (let i = 0; i < 260; i++) {
    const x = (i * 71) % 256, y = (i * 113 + (i >> 3) * 17) % 256, r = 9 + ((i * 7) % 6);
    g.fillStyle = cols[i % cols.length]; g.beginPath(); g.ellipse(x, y, r, r * 0.55, ((i * 13) % 10) / 10, 0, PI * 2); g.fill();
    g.fillStyle = 'rgba(255,255,230,.35)'; g.beginPath(); g.ellipse(x - r * 0.3, y - r * 0.15, r * 0.35, r * 0.16, 0, 0, PI * 2); g.fill();
  }
}, [2, 1]);

// ---------- light rig: bright morning on the high street ----------
export const StreetLights: React.FC<{ sw: number; dim?: number }> = ({ sw, dim = 0 }) => (
  <>
    <ambientLight intensity={0.5 + 0.15 * dim} color={mixC('#FFF3E0', '#B8B0FF', sw)} />
    <hemisphereLight args={[mixC('#DDEBFF', '#9FB7FF', sw), mixC('#8F8574', '#4A3F7A', sw), 0.75]} />
    <directionalLight position={[3.5, 5.0, 4.0]} intensity={1.6 * (1 - 0.55 * dim)} color={mixC('#FFE7C2', '#C6CCFF', sw)} />
    <directionalLight position={[-2.5, 3.2, -3.5]} intensity={1.0} color={mixC('#FFFFFF', '#8FF0E0', sw)} />
  </>
);
export const HallLights: React.FC<{ sw: number; dim?: number }> = ({ sw, dim = 0 }) => (
  <>
    <ambientLight intensity={0.75 * (1 - 0.6 * dim)} color={mixC('#FFF1DE', '#C8C0FF', sw)} />
    <hemisphereLight args={[mixC('#FFF4E2', '#AFC5FF', sw), mixC('#7A6A58', '#5A4F8A', sw), 0.8]} />
    <directionalLight position={[2.0, 4.0, 4.0]} intensity={1.3 * (1 - 0.7 * dim)} color={mixC('#FFE6C4', '#C6CCFF', sw)} />
    <directionalLight position={[-2.2, 3.4, -3.8]} intensity={0.95} color={mixC('#FFFFFF', '#8FF0E0', sw)} />
  </>
);

// ---------- the hero prop: a big sweet-shop jar of coins, frosted and tinted (SCRIPT.md: not clear glass) ----------
/** About 46 cm tall. fill 0..1 is how full; heap shows the shiny coins piled at the open neck; label is a paper label;
 *  tape adds the parcel tape of the mended jar. */
export const CoinJar: React.FC<{ fill?: number; heap?: boolean; label?: string; tape?: boolean; s?: number }> = ({ fill = 0.92, heap = true, label, tape = false, s = 1 }) => {
  const mass = coinMass();
  const lbl = label ? sign(`ep22jarlbl${label}`, 256, 128, '#F3E9CF', [{ text: label, y: 66, size: label.length > 5 ? 56 : 72, color: '#1F3A68' }], '#B3262E') : null;
  const R = 0.15, H = 0.36, fh = H * fill;
  return (
    <group scale={s}>
      {/* the coins inside, seen through the frost */}
      <mesh position={[0, 0.012 + fh / 2, 0]}><cylinderGeometry args={[R * 0.93, R * 0.93, fh, 28]} /><M c="#ffffff" map={mass} r={0.45} m={0.35} /></mesh>
      {/* the frosted, tinted glass: body, shoulder, neck */}
      <mesh position={[0, H / 2, 0]}><cylinderGeometry args={[R, R, H, 32, 1, true]} /><meshStandardMaterial color="#CFE3DA" transparent opacity={0.55} roughness={0.55} metalness={0.05} side={THREE.DoubleSide} depthWrite={false} /></mesh>
      <mesh position={[0, 0.004, 0]} rotation={[-PI / 2, 0, 0]}><circleGeometry args={[R, 32]} /><M c="#B8CFC6" r={0.5} /></mesh>
      <mesh position={[0, H + 0.03, 0]}><cylinderGeometry args={[R * 0.72, R, 0.06, 32, 1, true]} /><meshStandardMaterial color="#CFE3DA" transparent opacity={0.55} roughness={0.55} side={THREE.DoubleSide} depthWrite={false} /></mesh>
      <mesh position={[0, H + 0.075, 0]}><cylinderGeometry args={[R * 0.74, R * 0.72, 0.03, 32, 1, true]} /><meshStandardMaterial color="#DCEDE6" transparent opacity={0.7} roughness={0.4} side={THREE.DoubleSide} /></mesh>
      <mesh position={[0, H + 0.09, 0]} rotation={[PI / 2, 0, 0]}><torusGeometry args={[R * 0.74, 0.008, 8, 32]} /><M c="#E8F4EF" r={0.3} /></mesh>
      {/* a few coins pressed against the frosted side, so the money reads at a glance */}
      {fill > 0.3 ? [[0.3, 0.1], [1.1, 0.18], [2.0, 0.07], [2.9, 0.22], [3.8, 0.13], [4.9, 0.25], [5.6, 0.09]].map(([a, y], i) => (
        <group key={i} position={[Math.sin(a) * R * 1.005, Math.min(fh, H) * (y / 0.26) * 0.9 + 0.02, Math.cos(a) * R * 1.005]} rotation={[0, a, 0]}>
          <group rotation={[PI / 2, 0, 0.4 * i]}><Coin s={1.7} /></group>
        </group>
      )) : null}
      {/* the heap of shiny coins at the neck */}
      {heap && fill > 0.85 ? (
        <group position={[0, H + 0.06, 0]}>
          <mesh scale={[1, 0.38, 1]}><sphereGeometry args={[R * 0.7, 24, 12, 0, PI * 2, 0, PI / 2]} /><M c="#ffffff" map={mass} r={0.4} m={0.4} /></mesh>
          {Array.from({ length: 22 }).map((_, i) => {
            const a = i * 2.4, rr = R * 0.6 * Math.sqrt(((i * 37) % 22) / 22);
            return (
              <group key={i} position={[Math.cos(a) * rr, 0.05 - rr * 0.35 + (i % 3) * 0.004, Math.sin(a) * rr]} rotation={[0.35 * Math.sin(i), a, 0.35 * Math.cos(i * 1.3)]}>
                <Coin s={1.7} />
              </group>
            );
          })}
        </group>
      ) : null}
      {lbl ? <mesh position={[0, H * 0.55, R * 1.01]}><planeGeometry args={[0.16, 0.08]} /><M c="#ffffff" map={lbl} r={0.8} /></mesh> : null}
      {tape ? [0.12, 0.27].map((y, i) => (
        <mesh key={i} position={[0, y, 0]} rotation={[0, 0, 0.12 * (i ? -1 : 1)]}><cylinderGeometry args={[R * 1.012, R * 1.012, 0.045, 32, 1, true]} /><M c="#C9A45E" r={0.5} /></mesh>
      )) : null}
    </group>
  );
};

/** The smashed jar: frosted shards and a spray of coins on the pavement. u 0..1 spreads them from the impact point. */
export const Smash: React.FC<{ u: number; at?: V3 }> = ({ u, at = [0, 0, 0] }) => {
  const k = 1 - (1 - Math.min(1, u)) ** 3;
  return (
    <group position={at}>
      {Array.from({ length: 9 }).map((_, i) => {
        const a = i * 0.71 + 0.3, d = (0.12 + ((i * 5) % 7) * 0.05) * k;
        return (
          <mesh key={i} position={[Math.cos(a) * d, 0.012 + 0.01 * (i % 2), Math.sin(a) * d]} rotation={[-PI / 2 + 0.2 * (i % 3), 0, a * 2]}>
            <circleGeometry args={[0.04 + 0.015 * (i % 3), 3]} /><meshStandardMaterial color="#CFE3DA" transparent opacity={0.7} roughness={0.4} side={THREE.DoubleSide} />
          </mesh>
        );
      })}
      {Array.from({ length: 46 }).map((_, i) => {
        const a = i * 2.39996, d = (0.08 + 0.9 * Math.sqrt(((i * 29) % 46) / 46)) * k;
        const hop = Math.sin(PI * Math.min(1, u * (1.2 + (i % 4) * 0.3))) * 0.08 * (1 - k * 0.6);
        return (
          <group key={i} position={[Math.cos(a) * d, 0.003 + Math.max(0, hop), Math.sin(a) * d * 0.8]} rotation={[0.2 * Math.sin(i * 3.1) * (1 - k), a, 0]}>
            <Coin s={1.7} />
          </group>
        );
      })}
    </group>
  );
};

/** The one coin that rolls in a slow circle on its edge and topples over (the redirection's stillness).
 *  u 0..1 through the roll; it falls flat over the last fifth. */
export const RollingCoin: React.FC<{ u: number; at: V3; r?: number }> = ({ u, at, r = 0.07 }) => {
  const roll = Math.min(1, u / 0.8), fall = Math.max(0, (u - 0.8) / 0.2);
  const ang = 2.4 * PI * (1 - (1 - roll) ** 2);            // slows down
  const lean = 0.18 + 0.5 * roll ** 2 + (PI / 2 - 0.68) * fall ** 2 + (fall >= 1 ? 0 : 0);
  const wobble = fall > 0 ? 0.04 * Math.sin(fall * 30) * (1 - fall) : 0;
  return (
    <group position={[at[0] + Math.cos(ang) * r, at[1], at[2] + Math.sin(ang) * r]} rotation={[0, -ang, 0]}>
      <group rotation={[0, 0, Math.min(PI / 2, lean) + wobble]}>
        <group position={[0, 0.0117 * 2.4, 0]}><group rotation={[PI / 2, 0, ang * 3]}><Coin s={2.4} /></group></group>
      </group>
    </group>
  );
};

// ---------- the high-street bank front (bright morning) ----------
export const DOOR = { z: 0.55, r: 0.95, h: 2.25 };
const bankSign = () => sign('ep22banksign', 1024, 180, '#1F2F4F', [{ text: 'THRIFTWELL BANK', y: 94, size: 104, color: '#F3E3B4' }]);
const hoursSign = () => sign('ep22hours', 256, 320, '#F4F1EA', [{ text: 'OPEN', y: 70, size: 64, color: '#1F2F4F' }, { text: '9 - 5', y: 150, size: 54, color: '#B3262E' }, { text: 'MON-SAT', y: 225, size: 40, color: '#1F2F4F' }]);
const shopSign = (t: string, bg: string, fg: string) => sign(`ep22shop${t}`, 512, 128, bg, [{ text: t, y: 66, size: 66, color: fg }]);

/** The revolving door: a glass drum with four wings turning by `spin` radians. */
export const RevolvingDoor: React.FC<{ spin: number; sw?: number }> = ({ spin, sw = 0 }) => (
  <group position={[0, 0, DOOR.z]}>
    {/* the drum's canopy and floor disc */}
    <mesh position={[0, DOOR.h + 0.09, 0]}><cylinderGeometry args={[DOOR.r + 0.06, DOOR.r + 0.06, 0.18, 40]} /><M c="#1F2F4F" r={0.5} m={0.2} /></mesh>
    <mesh position={[0, 0.006, 0]} rotation={[-PI / 2, 0, 0]}><circleGeometry args={[DOOR.r, 40]} /><M c="#4A4440" r={0.8} /></mesh>
    {/* the curved glass sides (left and right quarters stay put) */}
    {[-1, 1].map((k) => (
      <mesh key={k} position={[0, DOOR.h / 2, 0]}>
        <cylinderGeometry args={[DOOR.r, DOOR.r, DOOR.h, 24, 1, true, k > 0 ? PI / 4 : PI * 1.25, PI / 2]} />
        <meshStandardMaterial color={mixC('#CFE8F2', '#9FFFF0', sw)} transparent opacity={0.22} roughness={0.05} side={THREE.DoubleSide} depthWrite={false} />
      </mesh>
    ))}
    {[-1, 1].map((k) => [-1, 1].map((j) => (
      <Bx key={`${k}${j}`} p={[k * DOOR.r * Math.SQRT1_2, DOOR.h / 2, j * DOOR.r * Math.SQRT1_2]} s={[0.05, DOOR.h, 0.05]} c="#C9A43A" r={0.3} />
    )))}
    {/* the four wings */}
    <group rotation={[0, spin, 0]}>
      <mesh position={[0, DOOR.h / 2, 0]}><cylinderGeometry args={[0.035, 0.035, DOOR.h, 12]} /><M c="#C9A43A" m={0.6} r={0.3} /></mesh>
      {[0, 1, 2, 3].map((i) => (
        <group key={i} rotation={[0, i * PI / 2, 0]}>
          <mesh position={[DOOR.r / 2, DOOR.h / 2, 0]}><planeGeometry args={[DOOR.r - 0.04, DOOR.h - 0.1]} /><meshStandardMaterial color={mixC('#CFE8F2', '#9FFFF0', sw)} transparent opacity={0.16} roughness={0.05} side={THREE.DoubleSide} depthWrite={false} /></mesh>
          <Bx p={[DOOR.r / 2, DOOR.h - 0.06, 0]} s={[DOOR.r - 0.04, 0.05, 0.04]} c="#C9A43A" r={0.3} />
          <Bx p={[DOOR.r / 2, 0.06, 0]} s={[DOOR.r - 0.04, 0.08, 0.04]} c="#C9A43A" r={0.3} />
          <Bx p={[DOOR.r - 0.04, DOOR.h / 2, 0]} s={[0.04, DOOR.h - 0.1, 0.04]} c="#C9A43A" r={0.3} />
          <Bx p={[DOOR.r * 0.55, 1.05, 0.03]} s={[0.4, 0.035, 0.035]} c="#E2C26A" r={0.3} />
        </group>
      ))}
    </group>
  </group>
);

export const BankFront: React.FC<{ spin?: number; sw?: number; shake?: number; rain?: number; shutter?: number; children?: React.ReactNode }> = ({ spin = 0, sw = 0, shake = 0, rain = 0, shutter = 0, children }) => {
  const st = stone(), pv = paving(), bk = brick(), bs = bankSign(), hs = hoursSign();
  return (
    <group>
      <StreetLights sw={sw} dim={rain} />
      <Bg color={mixC(mixC('#BFDDF5', '#6D63B8', sw), '#4E5670', rain * 0.8)} />
      {rain > 0 ? <mesh rotation={[-PI / 2, 0, 0]} position={[0, 0.003, 2.6]}><planeGeometry args={[14, 5.2]} /><meshStandardMaterial color="#20283A" transparent opacity={0.35 * rain} roughness={0.08} metalness={0.4} depthWrite={false} /></mesh> : null}
      {shutter > 0 ? (
        <group position={[0, 0, DOOR.z + DOOR.r + 0.08]}>
          <Bx p={[0, DOOR.h + 0.15, 0]} s={[2.3, 0.3, 0.2]} c="#5B6170" r={0.5} />
          <group position={[0, DOOR.h + 0.02 - (DOOR.h * shutter) / 2, 0]}>
            <mesh><planeGeometry args={[2.1, DOOR.h * shutter]} /><M c="#ffffff" map={shutterTex()} r={0.6} m={0.3} /></mesh>
            <Bx p={[0, -(DOOR.h * shutter) / 2, 0.02]} s={[2.15, 0.06, 0.06]} c="#3A3F4A" r={0.4} />
          </group>
          {[-1, 1].map((k) => <Bx key={k} p={[k * 1.08, DOOR.h / 2, 0]} s={[0.07, DOOR.h + 0.2, 0.12]} c="#3A3F4A" r={0.4} />)}
        </group>
      ) : null}
      {/* pavement, kerb and road */}
      <mesh rotation={[-PI / 2, 0, 0]} position={[0, 0, 2.6]}><planeGeometry args={[14, 5.2]} /><M c="#ffffff" map={pv} r={0.9} /></mesh>
      <Bx p={[0, 0.06, 5.25]} s={[14, 0.12, 0.2]} c="#8E8B84" />
      <mesh rotation={[-PI / 2, 0, 0]} position={[0, -0.005, 8]}><planeGeometry args={[14, 5.4]} /><M c="#4A4B50" r={0.95} /></mesh>
      <group position={[0.01 * shake, 0, 0]}>
        {/* the stone facade, columns either side of the door, the gold-on-navy fascia */}
        <mesh position={[0, 2.4, -0.02]}><planeGeometry args={[5.2, 4.8]} /><M c="#ffffff" map={st} r={0.9} /></mesh>
        {[-1, 1].map((k) => (
          <group key={k}>
            <mesh position={[k * 1.3, 1.45, 0.18]}><cylinderGeometry args={[0.17, 0.19, 2.9, 20]} /><M c="#EDE4D0" r={0.8} /></mesh>
            <Bx p={[k * 1.3, 2.96, 0.18]} s={[0.5, 0.14, 0.5]} c="#E2D8C0" />
            <Bx p={[k * 1.3, 0.08, 0.18]} s={[0.48, 0.16, 0.48]} c="#E2D8C0" />
            {/* tall windows with blinds */}
            <group position={[k * 2.05, 1.55, 0.0]}>
              <Bx p={[0, 0, 0]} s={[0.95, 1.9, 0.08]} c="#1F2F4F" />
              <mesh position={[0, 0, 0.045]}><planeGeometry args={[0.83, 1.78]} /><M c={mixC('#9FC3DA', '#7FE8DA', sw)} e={mixC('#CFE6FF', '#9FFFF0', sw)} ei={0.25} r={0.15} /></mesh>
              {[0, 1, 2, 3, 4, 5, 6].map((i) => <Bx key={i} p={[0, 0.85 - i * 0.07, 0.05]} s={[0.83, 0.03, 0.01]} c="#EDE7DA" />)}
              <Bx p={[0, -1.0, 0.1]} s={[1.05, 0.06, 0.2]} c="#E2D8C0" />
            </group>
          </group>
        ))}
        <Bx p={[0, 3.25, 0.12]} s={[3.6, 0.48, 0.12]} c="#1F2F4F" />
        <Sign p={[0, 3.25, 0.185]} w={3.3} h={0.42} tex={bs} glow />
        <Bx p={[0, 3.55, 0.16]} s={[5.2, 0.1, 0.3]} c="#E2D8C0" />
        <Sign p={[-0.98, 1.55, 0.29]} w={0.26} h={0.32} tex={hs} />
        {/* neighbours: a brick terrace either side */}
        {[-1, 1].map((k) => (
          <group key={k} position={[k * 4.6, 0, -0.1]}>
            <mesh position={[0, 2.4, 0]}><planeGeometry args={[4.0, 4.8]} /><M c="#ffffff" map={bk} r={0.95} /></mesh>
            <Bx p={[0, 2.6, 0.06]} s={[3.4, 0.4, 0.1]} c={k < 0 ? '#2E6B4F' : '#7A2E3A'} />
            <Sign p={[0, 2.6, 0.115]} w={2.6} h={0.32} tex={k < 0 ? shopSign('CHIPPY', '#2E6B4F', '#F7E9C0') : shopSign('NEWSAGENT', '#7A2E3A', '#F7E9C0')} />
            <mesh position={[0, 1.2, 0.05]}><planeGeometry args={[3.0, 1.8]} /><M c={mixC('#9FC3DA', '#7FE8DA', sw)} e="#CFE6FF" ei={0.2} r={0.15} /></mesh>
          </group>
        ))}
        <RevolvingDoor spin={spin} sw={sw} />
      </group>
      {/* street furniture: a bin and a bollard on the kerb */}
      <group position={[2.3, 0, 3.6]}>
        <mesh position={[0, 0.45, 0]}><cylinderGeometry args={[0.24, 0.22, 0.9, 20]} /><M c="#1F2F4F" r={0.5} /></mesh>
        <mesh position={[0, 0.92, 0]}><cylinderGeometry args={[0.26, 0.26, 0.06, 20]} /><M c="#C9A43A" r={0.4} m={0.4} /></mesh>
      </group>
      {[-2.6, -1.2].map((x, i) => <mesh key={i} position={[x, 0.4, 4.9]}><cylinderGeometry args={[0.07, 0.08, 0.8, 14]} /><M c="#1E1F24" r={0.4} /></mesh>)}
      {/* the door's contact shadow */}
      <mesh rotation={[-PI / 2, 0, 0]} position={[0, 0.008, DOOR.z]}><circleGeometry args={[DOOR.r + 0.1, 32]} /><meshBasicMaterial color="#000" transparent opacity={0.12} depthWrite={false} /></mesh>
      {children}
    </group>
  );
};

// ---------- the what-if bank hall: savers queue clutching their jars; the cashiers' shelves full of labelled jars ----------
export const HALL = { counterZ: -2.2, shelfZ: -3.1 };
const counterGlass = () => sign('ep22cashier', 512, 96, '#1F2F4F', [{ text: 'CASHIER', y: 50, size: 56, color: '#F3E3B4' }]);
const savingsBoard = () => sign('ep22savingsin', 768, 160, '#F3E9CF', [{ text: 'SAVINGS IN', y: 82, size: 92, color: '#1F2F4F' }], '#B3262E');
export const SHELF_LABELS = ['MRS PATEL', 'D. OKAFOR', 'NAN', 'J. REID', 'MR LEE', 'S. KHAN'];
export const BankHall: React.FC<{ sw?: number; dim?: number; screen?: string; children?: React.ReactNode }> = ({ sw = 1, dim = 0, screen, children }) => {
  const mb = marble(), st = stone(), cg = counterGlass(), sb = savingsBoard();
  return (
    <group>
      <HallLights sw={sw} dim={dim} />
      <Bg color={mixC(mixC('#E8E0D0', '#5E558F', sw), '#15131F', dim * 0.7)} />
      {screen !== undefined ? <group position={[COMPUTER.x, 1.045, COMPUTER.z]}><OldComputer screen={screen} /></group> : null}
      {dim > 0 ? <pointLight position={[COMPUTER.x - 0.5, 1.7, COMPUTER.z + 0.7]} intensity={2.2 * dim} distance={4} color="#FFD08A" /> : null}
      <mesh rotation={[-PI / 2, 0, 0]} position={[0, 0, 0]}><planeGeometry args={[8, 9]} /><M c="#ffffff" map={mb} r={0.35} /></mesh>
      <mesh position={[0, 2.0, -3.6]}><planeGeometry args={[8, 4]} /><M c="#ffffff" map={st} r={0.9} /></mesh>
      {[-1, 1].map((k) => <mesh key={k} position={[k * 3.2, 2.0, 0.5]} rotation={[0, -k * PI / 2, 0]}><planeGeometry args={[9, 4]} /><M c="#ffffff" map={st} r={0.9} /></mesh>)}
      {/* the long counter with glass screens */}
      <Bx p={[0, 0.5, HALL.counterZ]} s={[5.2, 1.0, 0.6]} c="#6B4A35" />
      <Bx p={[0, 1.02, HALL.counterZ]} s={[5.3, 0.05, 0.7]} c="#3A2A20" r={0.4} />
      {[-1.7, 0, 1.7].map((x, i) => (
        <group key={i} position={[x, 0, HALL.counterZ]}>
          <mesh position={[0, 1.5, 0]}><planeGeometry args={[1.5, 0.9]} /><meshStandardMaterial color={mixC('#CFE8F2', '#9FFFF0', sw)} transparent opacity={0.18} roughness={0.05} depthWrite={false} /></mesh>
          <Bx p={[0, 2.0, 0]} s={[1.6, 0.14, 0.08]} c="#1F2F4F" />
          <Sign p={[0, 2.0, 0.045]} w={0.9} h={0.12} tex={cg} glow />
        </group>
      ))}
      {/* the shelves behind: every saver's jar, labelled */}
      {[0.9, 1.6].map((y, row) => (
        <group key={row} position={[0, y, HALL.shelfZ]}>
          <Bx p={[0, -0.02, 0]} s={[4.6, 0.04, 0.34]} c="#8A5E3C" />
          {Array.from({ length: 8 }).map((_, i) => {
            const lab = SHELF_LABELS[(i + row * 3) % SHELF_LABELS.length];
            return <group key={i} position={[-1.95 + i * 0.56, 0, 0]}><CoinJar s={0.62} fill={0.55 + 0.4 * (((i + row) * 7) % 5) / 5} heap={false} label={lab} /></group>;
          })}
        </group>
      ))}
      <Bx p={[0, 2.55, HALL.shelfZ + 0.05]} s={[2.4, 0.42, 0.06]} c="#1F2F4F" />
      <Sign p={[0, 2.55, HALL.shelfZ + 0.085]} w={2.2} h={0.36} tex={sb} />
      {/* queue posts and rope */}
      {[-1.4, -0.4, 0.6].map((x, i) => <group key={i} position={[x, 0, -0.9]}><mesh position={[0, 0.48, 0]}><cylinderGeometry args={[0.03, 0.03, 0.95, 10]} /><M c="#C9A43A" m={0.6} r={0.3} /></mesh><mesh position={[0, 0.02, 0]}><cylinderGeometry args={[0.14, 0.16, 0.04, 16]} /><M c="#C9A43A" m={0.6} r={0.3} /></mesh></group>)}
      {[-0.9, 0.1].map((x, i) => <mesh key={i} position={[x, 0.82, -0.9]} rotation={[0, 0, PI / 2]}><cylinderGeometry args={[0.018, 0.018, 1.0, 8]} /><M c="#8E2430" r={0.7} /></mesh>)}
      {children}
    </group>
  );
};

/** Ease helper for a world prop following an actor: linear walk from a to b over [t0, t1]. */
export const along = (ts: number, t0: number, t1: number, a: number, b: number) => lerp(a, b, Math.min(1, Math.max(0, (ts - t0) / (t1 - t0))));

// ---------- act 2 props ----------
export const COMPUTER = { x: 1.7, z: -2.12 };
/** A beige old-school computer on the counter, screen facing the customers (+z). screen = the text on the balance screen. */
export const OldComputer: React.FC<{ screen: string }> = ({ screen }) => {
  const [who, amt] = screen.split('|');
  const tex = textTexture(`ep22screen${screen}`, { w: 512, h: 384, bg: '#0E2A1C', lines: [
    { text: 'ACCOUNT', x: 256, y: 60, size: 44, color: '#7DFFB0', weight: 700, font: 'JetBrains Mono' },
    { text: who ?? '', x: 256, y: 130, size: 56, color: '#7DFFB0', weight: 700, font: 'JetBrains Mono' },
    { text: 'BALANCE', x: 256, y: 225, size: 40, color: '#7DFFB0', weight: 700, font: 'JetBrains Mono' },
    { text: amt ?? '', x: 256, y: 305, size: 92, color: '#E9FFF2', weight: 700, font: 'JetBrains Mono' },
  ], draw: (g) => { g.fillStyle = 'rgba(125,255,176,0.06)'; for (let y = 0; y < 384; y += 6) g.fillRect(0, y, 512, 2); } });
  return (
    <group>
      <Bx p={[0, 0.03, 0.02]} s={[0.46, 0.06, 0.4]} c="#D8CFB8" />
      <Bx p={[0, 0.3, -0.05]} s={[0.5, 0.42, 0.42]} c="#E2D9C2" />
      <mesh position={[0, 0.31, 0.162]}><planeGeometry args={[0.4, 0.3]} /><meshBasicMaterial map={tex ?? undefined} toneMapped={false} /></mesh>
      <Bx p={[0, 0.07, 0.36]} s={[0.46, 0.035, 0.17]} c="#D8CFB8" />
      {Array.from({ length: 12 }).map((_, i) => <Bx key={i} p={[-0.19 + (i % 6) * 0.075, 0.092, 0.33 + Math.floor(i / 6) * 0.06]} s={[0.055, 0.012, 0.045]} c="#F2EEE4" />)}
      <pointLight position={[0, 0.31, 0.45]} intensity={0.5} distance={1.2} color="#7DFFB0" />
    </group>
  );
};
/** An umbrella held over a head: canopy radius 0.55. */
export const Umbrella: React.FC<{ c?: string; tilt?: number }> = ({ c = '#1F2F4F', tilt = 0 }) => (
  <group rotation={[tilt, 0, 0]}>
    <mesh position={[0, 0.45, 0]}><cylinderGeometry args={[0.012, 0.012, 0.9, 8]} /><M c="#2A2A2E" /></mesh>
    <mesh position={[0, 0.92, 0]}><coneGeometry args={[0.55, 0.22, 8, 1, true]} /><M c={c} r={0.4} side={THREE.DoubleSide} /></mesh>
  </group>
);
const cashBoard = () => sign('ep22cashboard', 768, 480, '#1F2F4F', [
  { text: 'CASH:', y: 120, size: 110, color: '#F3E3B4' }, { text: '£3 IN', y: 250, size: 130, color: '#FFFFFF' }, { text: 'EVERY £100', y: 385, size: 104, color: '#FFD43B' },
], '#C9A43A');
const steel = () => canvasTex('ep22steel', 128, 128, (g) => {
  g.fillStyle = '#8C939C'; g.fillRect(0, 0, 128, 128);
  for (let i = 0; i < 128; i += 2) { g.fillStyle = `rgba(255,255,255,${0.03 + 0.03 * ((i * 7) % 3)})`; g.fillRect(0, i, 128, 1); }
  g.fillStyle = '#6E757E'; for (let x = 8; x < 128; x += 40) for (let y = 8; y < 128; y += 40) { g.beginPath(); g.arc(x, y, 3, 0, Math.PI * 2); g.fill(); }
}, [4, 2]);
/** The vault: a steel wall at z = 0 with a round door (hinge on +x, swings out towards +z by `open` 0..1),
 *  and behind it an enormous, nearly empty room with a few jars on one shelf and the CASH board. */
export const VAULT = { r: 1.0, cy: 1.15, depth: 6.5 };
export const Vault: React.FC<{ open?: number; sw?: number; children?: React.ReactNode }> = ({ open = 0, sw = 1, children }) => {
  const stl = steel(), cb = cashBoard();
  const wall = new THREE.Shape(); wall.moveTo(-4, 0); wall.lineTo(4, 0); wall.lineTo(4, 3.6); wall.lineTo(-4, 3.6); wall.lineTo(-4, 0);
  const hole = new THREE.Path(); hole.absarc(0, VAULT.cy, VAULT.r, 0, Math.PI * 2, false); wall.holes.push(hole);
  return (
    <group>
      <HallLights sw={sw} />
      <Bg color={mixC('#2A2E36', '#2B2550', sw)} />
      <pointLight position={[0, 3.2, -3]} intensity={6} distance={11} color={mixC('#E8F0FF', '#B8B0FF', sw)} />
      {/* the hall side (floor in front of the wall) */}
      <mesh rotation={[-PI / 2, 0, 0]} position={[0, 0, 2]}><planeGeometry args={[8, 4]} /><M c="#ffffff" map={marble()} r={0.35} /></mesh>
      <mesh><shapeGeometry args={[wall]} /><M c="#ffffff" map={stl} r={0.45} m={0.5} side={THREE.DoubleSide} /></mesh>
      <mesh position={[0, VAULT.cy, 0.02]}><torusGeometry args={[VAULT.r + 0.04, 0.07, 12, 48]} /><M c="#C9A43A" r={0.3} m={0.7} /></mesh>
      {/* the door: hinge at x = +r */}
      <group position={[VAULT.r + 0.05, VAULT.cy, 0.12]} rotation={[0, open * PI * 0.62, 0]}>
        <group position={[-(VAULT.r + 0.05), 0, 0]}>
          <mesh rotation={[PI / 2, 0, 0]}><cylinderGeometry args={[VAULT.r, VAULT.r, 0.22, 48]} /><M c="#A8AEB6" r={0.35} m={0.75} /></mesh>
          <mesh position={[0, 0, 0.115]}><circleGeometry args={[VAULT.r * 0.82, 48]} /><M c="#8C939C" r={0.3} m={0.8} /></mesh>
          {/* the wheel */}
          <group position={[0, 0, 0.16]} rotation={[0, 0, open * 3]}>
            <mesh><torusGeometry args={[0.3, 0.03, 10, 32]} /><M c="#C9A43A" r={0.3} m={0.7} /></mesh>
            {[0, 1, 2].map((i) => <mesh key={i} rotation={[0, 0, (i * PI) / 3]}><boxGeometry args={[0.62, 0.035, 0.035]} /><M c="#C9A43A" r={0.3} m={0.7} /></mesh>)}
          </group>
          {Array.from({ length: 10 }).map((_, i) => <mesh key={i} position={[Math.cos((i * PI) / 5) * VAULT.r * 0.9, Math.sin((i * PI) / 5) * VAULT.r * 0.9, 0.12]}><sphereGeometry args={[0.035, 10, 8]} /><M c="#C9A43A" m={0.7} r={0.3} /></mesh>)}
        </group>
      </group>
      {/* inside: steel walls, an echoing floor, one shelf with a few jars, the board */}
      <mesh rotation={[-PI / 2, 0, 0]} position={[0, 0.001, -VAULT.depth / 2]}><planeGeometry args={[6, VAULT.depth]} /><M c="#4F555E" r={0.6} m={0.3} /></mesh>
      <mesh position={[0, 1.8, -VAULT.depth]}><planeGeometry args={[6, 3.6]} /><M c="#ffffff" map={stl} r={0.45} m={0.5} /></mesh>
      {[-1, 1].map((k) => <mesh key={k} position={[k * 3, 1.8, -VAULT.depth / 2]} rotation={[0, -k * PI / 2, 0]}><planeGeometry args={[VAULT.depth, 3.6]} /><M c="#ffffff" map={stl} r={0.45} m={0.5} /></mesh>)}
      <mesh position={[0, 3.6, -VAULT.depth / 2]} rotation={[PI / 2, 0, 0]}><planeGeometry args={[6, VAULT.depth]} /><M c="#3A3F47" /></mesh>
      <group position={[-0.6, 1.0, -VAULT.depth + 0.3]}>
        <Bx p={[0, -0.02, 0]} s={[3.6, 0.05, 0.4]} c="#6E757E" r={0.4} />
        {[-1.2, -0.75].map((x, i) => <group key={i} position={[x, 0, 0]}><CoinJar s={0.62} fill={0.5 + 0.3 * i} heap={false} /></group>)}
        <group position={[1.3, 0, 0]}><CoinJar s={0.62} fill={0.25} heap={false} /></group>
      </group>
      {Array.from({ length: 4 }).map((_, i) => <Bx key={i} p={[-2.0 + i * 1.3, 1.6, -VAULT.depth + 0.3]} s={[0.04, 1.2, 0.4]} c="#6E757E" />)}
      <group position={[2.97, 1.85, -2.6]} rotation={[0, -PI / 2, 0]}>
        <Bx p={[0, 0, -0.03]} s={[1.7, 1.08, 0.05]} c="#C9A43A" />
        <Sign p={[0, 0, 0.0]} w={1.6} h={1.0} tex={cb} />
      </group>
      {children}
    </group>
  );
};
/** Rain over the frame (HTML overlay): slanting streaks that fall with time. */
export const Rain: React.FC<{ t: number; o?: number }> = ({ t, o = 1 }) => (
  <svg width={1080} height={1920} style={{ position: 'absolute', inset: 0, opacity: o, pointerEvents: 'none' }}>
    {Array.from({ length: 140 }).map((_, i) => {
      const x0 = (i * 397) % 1180 - 50, sp = 2600 + ((i * 53) % 700), y = (((i * 811) % 1920) + t * sp) % 2100 - 100, L = 60 + ((i * 17) % 50);
      return <line key={i} x1={x0 + y * 0.12} y1={y} x2={x0 + (y + L) * 0.12} y2={y + L} stroke="rgba(220,230,255,0.55)" strokeWidth={i % 3 ? 2 : 3} />;
    })}
  </svg>
);
