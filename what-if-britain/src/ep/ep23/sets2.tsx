// EP23 act 2 sets: Mate's front hall (the letterbox), the car boot sale in the rain, the store's back office; and their
// props (envelopes, snow shovel, LATE FEE sticker, kick scooter, the long receipt). Metres, floor y = 0, camera at +z.
import React from 'react';
import * as THREE from 'three';
import { textTexture } from '../../kit/text';
import { Bg } from '../../worlds/kit';
import { M, Bx, canvasTex, mixC } from '../ep21/sets';
import { lerp, clamp } from '../kit3';
import { Plane, StoreLights } from './sets';

type V3 = [number, number, number];
const PI = Math.PI;
const sign = (key: string, w: number, h: number, bg: string, lines: { text: string; y: number; size: number; color: string; font?: 'JetBrains Mono' }[], border?: string) =>
  textTexture(key, { w, h, bg, border, lines: lines.map((l) => ({ ...l, x: w / 2, weight: 900 })) });

// ---------- props ----------
/** A plain window envelope with a red PAY stripe: an instalment letter. */
export const PayLetter: React.FC<{ s?: number }> = ({ s = 1 }) => (
  <group scale={s}>
    <Bx p={[0, 0, 0]} s={[0.22, 0.008, 0.11]} c="#F4F1EA" r={0.9} />
    <mesh position={[0.02, 0.0045, 0.0]} rotation={[-PI / 2, 0, 0]}><planeGeometry args={[0.2, 0.09]} />
      <meshStandardMaterial map={sign('ep23letter', 256, 128, '#F4F1EA', [{ text: 'PAYMENT 2 OF 4', y: 70, size: 25, color: '#B3262E' }]) ?? undefined} roughness={0.9} /></mesh>
  </group>
);
/** n envelopes scattered in a heap of height h around (0,0), deterministic. */
export const LetterHeap: React.FC<{ n: number; r: number; h: number }> = ({ n, r, h }) => (
  <group>
    {h > 0.05 ? <mesh position={[0, h * 0.42, 0]} scale={[r, h * 0.95, r * 0.8]}><sphereGeometry args={[1, 24, 16, 0, PI * 2, 0, PI / 2]} /><M c="#EDE7DA" r={0.95} /></mesh> : null}
    {Array.from({ length: n }).map((_, i) => {
      const a = i * 2.39996, d = r * Math.sqrt(((i * 37) % 100) / 100);
      const x = Math.cos(a) * d, z = Math.sin(a) * d * 0.8, top = h > 0.05 ? h * 0.42 + h * 0.95 * Math.sqrt(Math.max(0, 1 - (d / r) ** 2)) : 0.01;
      return <group key={i} position={[x, top + 0.005, z]} rotation={[((i * 13) % 7 - 3) * 0.08, a, ((i * 11) % 7 - 3) * 0.08]}><PayLetter /></group>;
    })}
  </group>
);
export const SnowShovel: React.FC = () => (
  <group>
    <mesh position={[0, -0.45, 0]}><cylinderGeometry args={[0.015, 0.015, 0.9, 8]} /><M c="#8A5A32" r={0.7} /></mesh>
    <mesh position={[0, 0.02, 0]} rotation={[PI / 2, 0, 0]}><torusGeometry args={[0.05, 0.01, 6, 14, PI]} /><M c="#1E1E22" /></mesh>
    <group position={[0, -0.95, 0.04]} rotation={[0.25, 0, 0]}><Bx p={[0, -0.12, 0]} s={[0.42, 0.3, 0.02]} c="#2E6BC2" r={0.5} /></group>
  </group>
);
export const LateFeeSticker: React.FC<{ s?: number }> = ({ s = 1 }) => (
  <group scale={s}><Plane p={[0, 0, 0]} w={0.16} h={0.08} tex={sign('ep23latefee', 384, 192, '#E8263A', [{ text: 'LATE FEE', y: 100, size: 84, color: '#FFFFFF' }], '#FFFFFF')} /></group>
);
/** A kick scooter, deck along x, handlebar at +x. */
export const KickScooter: React.FC = () => (
  <group>
    <Bx p={[0, 0.09, 0]} s={[0.62, 0.03, 0.13]} c="#1E8C84" r={0.4} />
    {[-0.3, 0.32].map((x) => <mesh key={x} position={[x, 0.07, 0]} rotation={[PI / 2, 0, 0]}><cylinderGeometry args={[0.07, 0.07, 0.04, 16]} /><M c="#1E1E22" r={0.6} /></mesh>)}
    <mesh position={[0.36, 0.5, 0]} rotation={[0, 0, 0.12]}><cylinderGeometry args={[0.018, 0.018, 0.86, 10]} /><M c="#C9CED6" m={0.7} r={0.3} /></mesh>
    <mesh position={[0.41, 0.92, 0]} rotation={[PI / 2, 0, 0]}><cylinderGeometry args={[0.016, 0.016, 0.42, 10]} /><M c="#1E1E22" /></mesh>
  </group>
);
/** The Rep's card reader on its lanyard, held out: a red flash when it scans (flash 0..1). */
export const RepReader: React.FC<{ flash?: number; text?: string }> = ({ flash = 0, text = 'SCAN' }) => (
  <group>
    <Bx p={[0, 0, 0]} s={[0.08, 0.14, 0.025]} c="#1C1D21" r={0.4} />
    <Plane p={[0, 0.025, 0.0135]} w={0.065} h={0.07} glow tex={sign(`ep23rr${text}${flash > 0.5}`, 256, 280, flash > 0.5 ? '#B3101C' : '#0E3B36', [{ text, y: 150, size: text.length > 4 ? 64 : 90, color: flash > 0.5 ? '#FFFFFF' : '#7FFFEA' }])} />
  </group>
);
/** The long receipt the Owner holds up: JACKET $100 / FEE -$8 / SHOP $92 (lines of 12 characters or fewer). */
export const FeeReceipt: React.FC<{ u?: number }> = ({ u = 1 }) => {
  const tex = textTexture('ep23feereceipt', {
    w: 384, h: 640, bg: '#FBFAF4',
    lines: [
      { text: 'HARGREAVES', x: 192, y: 60, size: 42, color: '#222', weight: 800, font: 'JetBrains Mono' },
      { text: 'PAY LATER', x: 192, y: 118, size: 30, color: '#555', weight: 500, font: 'JetBrains Mono' },
      { text: 'JACKET $100', x: 192, y: 240, size: 50, color: '#222', weight: 800, font: 'JetBrains Mono' },
      { text: 'FEE    -$8', x: 192, y: 350, size: 56, color: '#C0272D', weight: 800, font: 'JetBrains Mono' },
      { text: 'SHOP   $92', x: 192, y: 460, size: 56, color: '#222', weight: 800, font: 'JetBrains Mono' },
      { text: 'FEE: UP TO 8%', x: 192, y: 575, size: 30, color: '#555', weight: 500, font: 'JetBrains Mono' },
    ],
  });
  const k = Math.max(0.02, clamp(u)), L = 0.48 * k;
  if (tex) { tex.repeat.set(1, k); tex.offset.set(0, 1 - k); }
  return <mesh position={[0, -L / 2, 0]}><planeGeometry args={[0.29, L]} /><meshStandardMaterial map={tex ?? undefined} color="#ffffff" roughness={0.9} side={THREE.DoubleSide} /></mesh>;
};

// ---------- Mate's front hall: the front door (letterbox at y 0.9) at the back, stairs on the right ----------
export const HALL2 = { doorZ: -2.2, slotY: 0.92, width: 2.6 };
const hallPaper = () => canvasTex('ep23hallpaper', 256, 256, (g) => {
  g.fillStyle = '#E9D9B8'; g.fillRect(0, 0, 256, 256);
  g.fillStyle = '#D8C49C'; for (let x = 0; x < 256; x += 32) g.fillRect(x, 0, 10, 256);
}, [3, 2]);
const hallCarpet = () => canvasTex('ep23hallcarpet', 128, 128, (g) => {
  g.fillStyle = '#7A3A3A'; g.fillRect(0, 0, 128, 128);
  for (let i = 0; i < 700; i++) { g.fillStyle = i % 2 ? 'rgba(40,10,10,.12)' : 'rgba(255,220,200,.07)'; g.fillRect((i * 37) % 128, (i * 61) % 128, 2, 2); }
}, [3, 6]);
export const FrontHall: React.FC<{ sw?: number; open?: number; children?: React.ReactNode }> = ({ sw = 1, open = 0, children }) => {
  const pp = hallPaper(), cp = hallCarpet(), W = HALL2.width;
  return (
    <group>
      <ambientLight intensity={0.6} color={mixC('#FFF1DE', '#C8C0FF', sw)} />
      <hemisphereLight args={[mixC('#FFF4E2', '#AFC5FF', sw), mixC('#7A6A58', '#5A4F8A', sw), 0.8]} />
      <directionalLight position={[1.2, 3.0, 3.0]} intensity={1.2} color={mixC('#FFE6C4', '#C6CCFF', sw)} />
      <pointLight position={[0, 2.3, -0.4]} intensity={6} distance={6} color={mixC('#FFE2B0', '#CFC8FF', sw)} />
      <Bg color={mixC('#3A3026', '#2A2250', sw)} />
      <mesh rotation={[-PI / 2, 0, 0]} position={[0, 0, 0]}><planeGeometry args={[W, 7]} /><M c="#ffffff" map={cp} r={0.95} /></mesh>
      {[-1, 1].map((k) => <mesh key={k} position={[k * W / 2, 1.4, 0]} rotation={[0, -k * PI / 2, 0]}><planeGeometry args={[7, 2.8]} /><M c="#ffffff" map={pp} r={0.9} /></mesh>)}
      {[-1, 1].map((k) => <Bx key={`s${k}`} p={[k * (W / 2 - 0.01), 0.06, 0]} s={[0.02, 0.12, 7]} c="#F4F1EA" />)}
      <mesh position={[0, 2.8, 0]} rotation={[PI / 2, 0, 0]}><planeGeometry args={[W, 7]} /><M c="#F2EEE4" /></mesh>
      {/* the back wall and the front door with its frosted panes and the brass letterbox */}
      <mesh position={[0, 1.4, HALL2.doorZ - 0.02]}><planeGeometry args={[W, 2.8]} /><M c="#ffffff" map={pp} r={0.9} /></mesh>
      <group position={[0, 0, HALL2.doorZ]}>
        <Bx p={[0, 1.05, 0]} s={[0.98, 2.1, 0.06]} c="#F4F1EA" />
        <group position={[-0.43, 0, 0.04]} rotation={[0, -1.4 * open, 0]}>
          <group position={[0.43, 0, 0]}>
            <Bx p={[0, 1.02, 0]} s={[0.86, 2.0, 0.05]} c="#1F4F3A" r={0.5} />
            {[[-0.2, 1.62], [0.2, 1.62]].map(([x, y], i) => <mesh key={i} position={[x, y, 0.027]}><planeGeometry args={[0.3, 0.5]} /><meshBasicMaterial color={mixC('#E8F0F6', '#AFFFF2', sw)} toneMapped={false} /></mesh>)}
            <Bx p={[0, HALL2.slotY, 0.03]} s={[0.3, 0.07, 0.015]} c="#C9A43A" r={0.3} />
            <Bx p={[0, HALL2.slotY, 0.038]} s={[0.24, 0.022, 0.005]} c="#1E1A14" />
            <mesh position={[0.32, 1.0, 0.04]}><sphereGeometry args={[0.03, 12, 10]} /><M c="#C9A43A" m={0.6} r={0.3} /></mesh>
          </group>
        </group>
        {open > 0 ? <mesh position={[0, 1.02, -0.05]}><planeGeometry args={[0.86, 2.0]} /><meshBasicMaterial color={mixC('#DCEBFF', '#AFFFF2', sw)} toneMapped={false} /></mesh> : null}
      </group>
      {/* the stairs up the right wall, a radiator and a coat hook on the left */}
      {Array.from({ length: 10 }).map((_, i) => <Bx key={i} p={[W / 2 - 0.36, 0.1 + i * 0.2, -1.6 + i * 0.26]} s={[0.7, 0.2, 0.28]} c="#E6DDCB" />)}
      <mesh position={[W / 2 - 0.72, 1.4, -0.4]} rotation={[0.66, 0, 0]}><boxGeometry args={[0.04, 0.05, 3.3]} /><M c="#8A5A32" r={0.6} /></mesh>
      <group position={[-W / 2 + 0.06, 0.45, -0.8]}>{Array.from({ length: 8 }).map((_, i) => <Bx key={i} p={[0, 0, -0.35 + i * 0.1]} s={[0.05, 0.5, 0.06]} c="#F4F1EA" r={0.4} />)}</group>
      <group position={[-W / 2 + 0.1, 1.75, 0.2]}>
        <Bx p={[0, 0, 0]} s={[0.04, 0.06, 0.5]} c="#8A5A32" />
        <Bx p={[0.08, -0.35, -0.1]} s={[0.12, 0.6, 0.38]} c="#5E6B3A" r={0.9} />
      </group>
      {children}
    </group>
  );
};

// ---------- the car boot sale in the rain: a car park, two cars with their boots up, the store lit up behind ----------
const tarmac = () => canvasTex('ep23tarmac', 256, 256, (g) => {
  g.fillStyle = '#4C4E54'; g.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 1500; i++) { g.fillStyle = i % 3 ? 'rgba(20,20,25,.18)' : 'rgba(200,200,210,.08)'; g.fillRect((i * 37) % 256, (i * 91) % 256, 2, 2); }
}, [6, 6]);
const Car: React.FC<{ c: string; boot?: number }> = ({ c, boot = 1 }) => (
  <group>
    <Bx p={[0, 0.5, 0]} s={[1.7, 0.55, 3.6]} c={c} r={0.35} />
    <Bx p={[0, 0.98, -0.25]} s={[1.55, 0.48, 2.0]} c={c} r={0.35} />
    {[-1, 1].map((k) => <mesh key={k} position={[k * 0.78, 1.0, -0.25]} rotation={[0, k * PI / 2, 0]}><planeGeometry args={[1.6, 0.34]} /><M c="#2A3440" r={0.1} /></mesh>)}
    {[[-0.82, -1.15], [0.82, -1.15], [-0.82, 1.15], [0.82, 1.15]].map(([x, z], i) => <mesh key={i} position={[x, 0.3, z]} rotation={[0, 0, PI / 2]}><cylinderGeometry args={[0.3, 0.3, 0.2, 18]} /><M c="#1E1E22" r={0.7} /></mesh>)}
    {/* the open boot: the lid swung up, the boot floor with a blanket */}
    <group position={[0, 1.2, 0.75]} rotation={[-1.9 * boot, 0, 0]}><Bx p={[0, 0, 0.45]} s={[1.5, 0.05, 0.9]} c={c} r={0.35} /></group>
    <Bx p={[0, 0.79, 1.45]} s={[1.4, 0.04, 0.6]} c="#7A2E3A" r={0.95} />
    {[-1, 1].map((k) => <Bx key={`l${k}`} p={[k * 0.65, 0.68, 1.81]} s={[0.25, 0.12, 0.02]} c="#B3262E" e="#FF3344" ei={0.4} />)}
  </group>
);
export const FoldTable: React.FC = () => (
  <group>
    <Bx p={[0, 0.72, 0]} s={[1.2, 0.04, 0.6]} c="#E6E8EC" r={0.5} />
    {[[-0.55, -0.25], [0.55, -0.25], [-0.55, 0.25], [0.55, 0.25]].map(([x, z], i) => <mesh key={i} position={[x, 0.36, z]}><cylinderGeometry args={[0.012, 0.012, 0.72, 8]} /><M c="#9EA4AE" m={0.6} /></mesh>)}
  </group>
);
const storeFar = () => sign('ep23storefar', 1024, 160, '#1F2F4F', [{ text: 'HARGREAVES', y: 84, size: 110, color: '#7FFFEA' }]);
export const CarBoot: React.FC<{ sw?: number; children?: React.ReactNode }> = ({ sw = 1, children }) => {
  const tm = tarmac();
  return (
    <group>
      <ambientLight intensity={0.55} color={mixC('#D8DEE8', '#B8B0FF', sw)} />
      <hemisphereLight args={[mixC('#C9D3E2', '#9FB0FF', sw), mixC('#3A3A40', '#3A3270', sw), 0.8]} />
      <directionalLight position={[2.0, 5.0, 4.0]} intensity={0.9} color={mixC('#E8EEF8', '#C6CCFF', sw)} />
      <directionalLight position={[-3, 2.5, -4]} intensity={0.6} color={mixC('#FFFFFF', '#8FF0E0', sw)} />
      <Bg color={mixC('#8A93A3', '#4E4688', sw)} fog={[mixC('#8A93A3', '#4E4688', sw), 9, 30]} />
      <mesh rotation={[-PI / 2, 0, 0]} position={[0, 0, -6]}><planeGeometry args={[30, 30]} /><M c="#ffffff" map={tm} r={0.25} m={0.15} /></mesh>
      {[-4.5, -1.5, 1.5, 4.5].map((x) => <Bx key={x} p={[x, 0.003, -1.5]} s={[0.08, 0.004, 4.5]} c="#E8E6DE" />)}
      {/* puddles */}
      {[[-0.9, 1.2, 0.7], [1.6, 0.4, 0.5], [0.3, -3.5, 0.9]].map(([x, z, r], i) => <mesh key={i} rotation={[-PI / 2, 0, 0]} position={[x, 0.004, z]} scale={[1, 0.6, 1]}><circleGeometry args={[r, 24]} /><meshStandardMaterial color="#2A3040" roughness={0.05} metalness={0.6} /></mesh>)}
      <group position={[-0.35, 0, -1.75]} rotation={[0, 0.06, 0]}><Car c="#3A5E8C" /></group>
      <group position={[2.3, 0, -2.0]} rotation={[0, -0.08, 0]}><Car c="#B8BEC6" /></group>
      <group position={[-3.2, 0, -2.3]} rotation={[0, 0.1, 0]}><Car c="#7A2E3A" boot={0} /></group>
      {/* the store across the car park, lit up */}
      <group position={[0.5, 0, -16]}>
        <Bx p={[0, 3.2, 0]} s={[16, 6.4, 0.5]} c="#C9BFA8" />
        {[-5.5, -2.5, 0.5, 3.5, 6.5].map((x) => <mesh key={x} position={[x, 1.6, 0.26]}><planeGeometry args={[2.4, 2.4]} /><meshBasicMaterial color={mixC('#FFE7B0', '#7FFFEA', sw)} toneMapped={false} /></mesh>)}
        <Plane p={[0, 4.6, 0.27]} w={7} h={1.1} tex={storeFar()} glow />
      </group>
      {children}
    </group>
  );
};

// ---------- the store's back office: cramped, boxes to the ceiling, a desk with an adding machine, a strip light ----------
const cork = () => canvasTex('ep23cork', 128, 128, (g) => {
  g.fillStyle = '#B8875A'; g.fillRect(0, 0, 128, 128);
  for (let i = 0; i < 600; i++) { g.fillStyle = i % 2 ? 'rgba(80,50,20,.18)' : 'rgba(255,230,190,.1)'; g.fillRect((i * 37) % 128, (i * 61) % 128, 2, 2); }
});
export const BackOffice: React.FC<{ sw?: number; children?: React.ReactNode }> = ({ sw = 1, children }) => (
  <group>
    <ambientLight intensity={0.55} color={mixC('#FFF4E0', '#C8C0FF', sw)} />
    <hemisphereLight args={[mixC('#FFF6E8', '#AFC5FF', sw), mixC('#6A5A48', '#4A3F7A', sw), 0.7]} />
    <directionalLight position={[0.5, 4.0, 3.0]} intensity={1.15} color={mixC('#FFF2DC', '#C6CCFF', sw)} />
    <pointLight position={[0, 2.35, 0]} intensity={7} distance={6} color={mixC('#FFFFFF', '#CFC8FF', sw)} />
    <Bg color={mixC('#4A4034', '#2A2250', sw)} />
    <mesh rotation={[-PI / 2, 0, 0]}><planeGeometry args={[5, 5]} /><M c="#8C8478" r={0.9} /></mesh>
    <mesh position={[0, 1.3, -1.6]}><planeGeometry args={[5, 2.6]} /><M c="#D9D2C2" r={0.95} /></mesh>
    {[-1, 1].map((k) => <mesh key={k} position={[k * 2.0, 1.3, 0]} rotation={[0, -k * PI / 2, 0]}><planeGeometry args={[5, 2.6]} /><M c="#CFC7B5" r={0.95} /></mesh>)}
    {/* the strip light */}
    <Bx p={[0, 2.5, -0.2]} s={[1.2, 0.05, 0.12]} c="#E6E8EC" />
    <mesh position={[0, 2.47, -0.2]} rotation={[PI / 2, 0, 0]}><planeGeometry args={[1.1, 0.08]} /><meshBasicMaterial color={mixC('#FFFFF4', '#DCD6FF', sw)} toneMapped={false} /></mesh>
    {/* boxes stacked to the ceiling on both sides */}
    {[-1, 1].map((k) => Array.from({ length: 9 }).map((_, i) => (
      <Bx key={`${k}${i}`} p={[k * (1.55 + ((i * 7) % 3) * 0.04), 0.22 + Math.floor(i / 3) * 0.45, -1.2 + (i % 3) * 0.55]} s={[0.6, 0.42, 0.5]} c={['#C9A877', '#B89464', '#D9BC8C'][(i + (k > 0 ? 1 : 0)) % 3]} r={0.9} rot={[0, ((i * 11) % 5 - 2) * 0.05, 0]} />
    )))}
    {/* the desk, an old adding machine, a lamp, the corkboard */}
    <Bx p={[0, 0.74, -0.75]} s={[1.5, 0.05, 0.7]} c="#6E5236" r={0.6} />
    {[[-0.68, -0.45], [0.68, -0.45], [-0.68, -1.05], [0.68, -1.05]].map(([x, z], i) => <Bx key={i} p={[x, 0.37, z]} s={[0.05, 0.74, 0.05]} c="#5A4230" />)}
    <group position={[0.45, 0.77, -0.75]}><Bx p={[0, 0.05, 0]} s={[0.26, 0.1, 0.3]} c="#3A3D46" r={0.5} /><Bx p={[0, 0.12, -0.08]} s={[0.22, 0.06, 0.08]} c="#2A2C33" />{Array.from({ length: 9 }).map((_, i) => <Bx key={i} p={[-0.07 + (i % 3) * 0.07, 0.105, 0.0 + Math.floor(i / 3) * 0.06]} s={[0.04, 0.02, 0.035]} c="#E9E1D0" />)}</group>
    <mesh position={[0, 1.55, -1.58]}><planeGeometry args={[1.1, 0.7]} /><M c="#ffffff" map={cork()} r={0.95} /></mesh>
    {[[-0.3, 1.65, '#F7E36A'], [0.05, 1.45, '#F4F1EA'], [0.32, 1.7, '#9FD0FF']].map(([x, y, c], i) => <Bx key={i} p={[x as number, y as number, -1.57]} s={[0.18, 0.2, 0.005]} c={c as string} rot={[0, 0, (i - 1) * 0.1]} />)}
    {children}
  </group>
);
export { lerp };
