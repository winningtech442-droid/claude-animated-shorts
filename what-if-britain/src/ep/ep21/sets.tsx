// EP21 Mattress Money: the sets for this episode (v3: built for the story, retired after it). Metres, floor y = 0,
// the camera mostly looks down -z. The bedroom's bed runs away from the camera so the seesaw gag reads in 9:16.
import React from 'react';
import * as THREE from 'three';
import { Note } from '../../props';
import { textTexture } from '../../kit/text';
import { lerp } from '../kit3';
import { Bg } from '../../worlds/kit';

type V3 = [number, number, number];
export const M: React.FC<{ c: string; r?: number; m?: number; e?: string; ei?: number; o?: number; map?: THREE.Texture | null; side?: THREE.Side }> = ({ c, r = 0.85, m = 0, e, ei = 0, o = 1, map, side }) => (
  <meshStandardMaterial color={c} roughness={r} metalness={m} emissive={e ?? '#000000'} emissiveIntensity={ei} transparent={o < 1} opacity={o} map={map ?? undefined} side={side} />
);
export const Bx: React.FC<{ p: V3; s: V3; c: string; r?: number; rot?: V3; e?: string; ei?: number; map?: THREE.Texture | null }> = ({ p, s, c, r, rot, e, ei, map }) => (
  <mesh position={p} rotation={rot}><boxGeometry args={s} /><M c={c} r={r} e={e} ei={ei} map={map} /></mesh>
);

// ---------- canvas textures (drawn once) ----------
const texCache = new Map<string, THREE.CanvasTexture>();
export const canvasTex = (key: string, w: number, h: number, draw: (g: CanvasRenderingContext2D) => void, repeat?: [number, number]) => {
  const hit = texCache.get(key);
  if (hit || typeof document === 'undefined') return hit ?? null;
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d')!);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
  texCache.set(key, t); return t;
};
const wallpaper = () => canvasTex('wallpaper', 256, 256, (g) => {
  g.fillStyle = '#A9BA9C'; g.fillRect(0, 0, 256, 256);
  g.fillStyle = '#E8E2CF'; for (let x = 0; x < 256; x += 64) g.fillRect(x + 22, 0, 16, 256);
  g.fillStyle = '#C9A0A0'; for (let y = 16; y < 256; y += 64) for (let x = 0; x < 256; x += 64) { g.beginPath(); g.arc(x + 54, y, 5, 0, Math.PI * 2); g.fill(); }
}, [6, 3]);
const carpet = () => canvasTex('carpet', 128, 128, (g) => {
  g.fillStyle = '#B49C80'; g.fillRect(0, 0, 128, 128);
  for (let i = 0; i < 900; i++) { g.fillStyle = i % 2 ? 'rgba(90,70,50,.10)' : 'rgba(255,240,220,.10)'; g.fillRect((i * 37) % 128, (i * 61) % 128, 2, 2); }
}, [8, 8]);
const duvetTex = () => canvasTex('duvet', 256, 256, (g) => {
  g.fillStyle = '#F2EEE4'; g.fillRect(0, 0, 256, 256);
  g.fillStyle = 'rgba(31,47,79,.55)'; for (let i = 0; i < 256; i += 64) { g.fillRect(i, 0, 22, 256); g.fillRect(0, i, 256, 22); }
}, [3, 4]);
const foamTex = () => canvasTex('foam', 128, 128, (g) => {
  for (let y = 0; y < 4; y++) for (let x = 0; x < 4; x++) {
    const grd = g.createLinearGradient(x * 32, 0, x * 32 + 32, 0);
    const dark = (x + y) % 2 ? ['#2E3038', '#474A55'] : ['#474A55', '#2E3038'];
    grd.addColorStop(0, dark[0]); grd.addColorStop(1, dark[1]); g.fillStyle = grd; g.fillRect(x * 32, y * 32, 32, 32);
  }
}, [6, 4]);
const netCurtain = () => canvasTex('net', 128, 128, (g) => {
  g.clearRect(0, 0, 128, 128); g.fillStyle = 'rgba(255,255,255,0.55)'; g.fillRect(0, 0, 128, 128);
  g.strokeStyle = 'rgba(255,255,255,0.9)'; g.lineWidth = 2;
  for (let i = 0; i < 128; i += 16) { g.beginPath(); g.arc(64, 64, i, 0, Math.PI * 2); g.stroke(); }
}, [2, 2]);

// ---------- light rigs ----------
export const mixC = (a: string, b: string, k: number) => '#' + new THREE.Color(a).lerp(new THREE.Color(b), k).getHexString();
export const RoomLights: React.FC<{ sw: number }> = ({ sw }) => (
  <>
    <ambientLight intensity={0.55} color={mixC('#FFF1DE', '#B8B0FF', sw)} />
    <hemisphereLight args={[mixC('#FFF4E2', '#9FB7FF', sw), mixC('#8C7A64', '#4A3F7A', sw), 0.6]} />
    <directionalLight position={[2.6, 3.0, 4.2]} intensity={1.35} color={mixC('#FFE6C4', '#C6CCFF', sw)} />
    <directionalLight position={[2.2, 3.4, -3.8]} intensity={0.9} color={mixC('#FFFFFF', '#8FF0E0', sw)} />
  </>
);

// ---------- props ----------
export const Envelope: React.FC<{ fat?: number }> = ({ fat = 1 }) => (
  <group>
    <Bx p={[0, 0, 0]} s={[0.24, 0.022 + 0.018 * fat, 0.13]} c="#E3D3A6" r={0.9} />
    <mesh position={[0, 0.02 + 0.01 * fat, -0.02]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[0.24, 0.07]} /><M c="#D8C691" /></mesh>
    {/* the corners of the notes poking out */}
    <group position={[0.1, 0.005, 0.04]} rotation={[0, 0.3, 0]}><Note s={0.9} /></group>
  </group>
);
export const Toast: React.FC = () => (
  <group rotation={[Math.PI / 2, 0, 0]}>
    <Bx p={[0, 0, 0]} s={[0.11, 0.016, 0.1]} c="#D9A35A" r={0.95} />
    <Bx p={[0, 0.0005, 0]} s={[0.095, 0.017, 0.085]} c="#E8C47F" r={0.95} />
  </group>
);
export const Clipboard: React.FC = () => (
  <group rotation={[0.2, 0, 0]} position={[0, -0.12, 0.06]}>
    <Bx p={[0, 0, 0]} s={[0.23, 0.31, 0.012]} c="#8A5A35" />
    <Bx p={[0, -0.01, 0.008]} s={[0.2, 0.26, 0.004]} c="#F6F4EE" r={0.95} />
    <Bx p={[0, 0.14, 0.012]} s={[0.08, 0.035, 0.012]} c="#B9BCC2" r={0.3} />
    {[0, 1, 2, 3, 4].map((i) => <Bx key={i} p={[-0.01, 0.08 - i * 0.045, 0.011]} s={[0.15 - (i % 2) * 0.04, 0.006, 0.002]} c="#5B6170" />)}
  </group>
);
export const Mug: React.FC<{ tip?: number }> = ({ tip = 0 }) => (
  <group rotation={[0, 0, -tip * 1.45]}>
    <mesh position={[0, 0.05, 0]}><cylinderGeometry args={[0.042, 0.04, 0.1, 24, 1, true]} /><M c="#1F3A68" r={0.4} side={THREE.DoubleSide} /></mesh>
    <mesh position={[0, 0.002, 0]} rotation={[-Math.PI / 2, 0, 0]}><circleGeometry args={[0.04, 24]} /><M c="#1F3A68" /></mesh>
    {tip < 0.6 ? <mesh position={[0, 0.085, 0]} rotation={[-Math.PI / 2, 0, 0]}><circleGeometry args={[0.039, 24]} /><M c="#8A5A3A" r={0.2} /></mesh> : null}
    <mesh position={[0.05, 0.055, 0]} rotation={[0, 0, Math.PI / 2]}><torusGeometry args={[0.025, 0.007, 8, 16, Math.PI]} /><M c="#1F3A68" /></mesh>
  </group>
);
/** A banknote in flight: drifts down see-sawing. u = 0..1 through its fall. */
export const FallingNote: React.FC<{ from: V3; to: V3; u: number; spin?: number; s?: number }> = ({ from, to, u, spin = 1, s = 1 }) => {
  const k = Math.min(1, Math.max(0, u));
  const sway = Math.sin(k * Math.PI * 5 * spin) * (1 - k);
  const p: V3 = [lerp(from[0], to[0], k) + 0.12 * sway, lerp(from[1], to[1], 1 - (1 - k) * (1 - k)), lerp(from[2], to[2], k)];
  return <group position={p} rotation={[0.6 * sway, k * 3 * spin, 0.5 * sway]}><Note s={s} /></group>;
};

// ---------- the bedroom (terraced house, morning) ----------
export const BED = { x: 0.05, top: 0.62, head: -1.35, foot: 0.3, pivotZ: -0.7 };
export const WARD = { x: -1.45, z: -2.45, front: -2.14 };
export const Bedroom: React.FC<{
  sw?: number; tilt?: number; lift?: number; doorL?: number; doorR?: number; shake?: number; gapGlow?: number; children?: React.ReactNode;
}> = ({ sw = 0, tilt = 0, lift = 0, doorL = 0, doorR = 0, shake = 0, gapGlow = 0, children }) => {
  const wp = wallpaper(), cp = carpet(), dv = duvetTex(), net = netCurtain();
  return (
    <group>
      <RoomLights sw={sw} />
      <Bg color={mixC('#DCE9F5', '#6D63B8', sw)} />
      {/* floor, walls, skirting */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0.6]}><planeGeometry args={[4.2, 7.2]} /><M c="#ffffff" map={cp} r={1} /></mesh>
      <mesh position={[0, 1.4, -2.8]}><planeGeometry args={[4.2, 2.8]} /><M c="#ffffff" map={wp} /></mesh>
      <mesh position={[-2.05, 1.4, 0.6]} rotation={[0, Math.PI / 2, 0]}><planeGeometry args={[7.2, 2.8]} /><M c="#ffffff" map={wp} /></mesh>
      <mesh position={[2.05, 1.4, 0.6]} rotation={[0, -Math.PI / 2, 0]}><planeGeometry args={[7.2, 2.8]} /><M c="#ffffff" map={wp} /></mesh>
      <Bx p={[0, 0.05, -2.78]} s={[4.2, 0.1, 0.03]} c="#F4F1EA" />
      <Bx p={[-2.03, 0.05, 0.6]} s={[0.03, 0.1, 7.2]} c="#F4F1EA" />
      {/* the sash window with net curtains and morning light */}
      <group position={[0.85, 1.55, -2.77]}>
        <Bx p={[0, 0, 0]} s={[1.12, 1.37, 0.06]} c="#F4F1EA" />
        <mesh position={[0, 0, 0.035]}><planeGeometry args={[1.0, 1.25]} /><M c={mixC('#CFE6FF', '#7FE8DA', sw)} e={mixC('#E8F3FF', '#9FFFF0', sw)} ei={0.95} r={0.2} /></mesh>
        <Bx p={[0, 0, 0.05]} s={[1.0, 0.05, 0.03]} c="#F4F1EA" />
        <Bx p={[0, 0, 0.05]} s={[0.04, 1.25, 0.03]} c="#F4F1EA" />
        <mesh position={[0, -0.25, 0.08]}><planeGeometry args={[1.0, 0.75]} /><meshStandardMaterial map={net ?? undefined} transparent opacity={0.85} color="#ffffff" roughness={1} /></mesh>
        <Bx p={[0, -0.71, 0.08]} s={[1.2, 0.05, 0.14]} c="#F4F1EA" />
        <Bx p={[-0.68, -0.05, 0.12]} s={[0.22, 1.5, 0.06]} c="#B4563F" r={1} />
        <Bx p={[0.68, -0.05, 0.12]} s={[0.22, 1.5, 0.06]} c="#B4563F" r={1} />
        <Bx p={[0, 0.76, 0.12]} s={[1.6, 0.04, 0.04]} c="#8A6A4A" />
      </group>
      {/* a framed print and a rug */}
      <group position={[-0.35, 1.75, -2.77]}>
        <Bx p={[0, 0, 0]} s={[0.5, 0.38, 0.03]} c="#3A2E26" />
        <mesh position={[0, 0, 0.02]}><planeGeometry args={[0.42, 0.3]} /><M c="#D8C9A8" /></mesh>
        <mesh position={[0, -0.03, 0.022]}><circleGeometry args={[0.08, 24]} /><M c="#B4563F" /></mesh>
      </group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[-1.05, 0.006, 0.6]}><planeGeometry args={[1.3, 1.9]} /><M c="#1F2F4F" r={1} /></mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[-1.05, 0.007, 0.6]}><planeGeometry args={[1.1, 1.7]} /><M c="#B3262E" r={1} /></mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[-1.05, 0.008, 0.6]}><planeGeometry args={[0.9, 1.5]} /><M c="#EFE8DA" r={1} /></mesh>
      {/* bedside table and lamp */}
      <group position={[1.1, 0, -1.6]}>
        <Bx p={[0, 0.25, 0]} s={[0.45, 0.5, 0.4]} c="#C99A62" />
        <mesh position={[0, 0.56, 0]}><cylinderGeometry args={[0.06, 0.08, 0.12, 16]} /><M c="#E9E2D3" /></mesh>
        <mesh position={[0, 0.72, 0]}><coneGeometry args={[0.16, 0.2, 20, 1, true]} /><M c="#F3D9A6" e="#FFD08A" ei={0.35} side={THREE.DoubleSide} /></mesh>
      </group>
      {/* the bed: pine frame, then the mattress group pivots (tilt = seesaw: foot down, head up; lift = near side up) */}
      <group position={[BED.x, 0, 0]}>
        <Bx p={[0, 0.17, -0.7]} s={[1.42, 0.3, 2.15]} c="#C99A62" />
        <Bx p={[0, 0.8, -1.82]} s={[1.5, 1.0, 0.08]} c="#B98A55" />
        <Bx p={[0, 1.32, -1.82]} s={[1.56, 0.06, 0.12]} c="#A97A47" />
        <group position={[0, 0.32, BED.pivotZ]} rotation={[tilt, 0, 0]}>
          <group position={[0.71, 0, 0]} rotation={[0, 0, -lift]}>
            <group position={[-0.71, 0, 0]}>
              <Bx p={[0, 0.12, 0]} s={[1.36, 0.24, 2.08]} c="#EDE8DC" r={0.95} />
              <mesh position={[0, 0.27, 0.25]}><boxGeometry args={[1.44, 0.07, 1.58]} /><M c="#ffffff" map={dv} r={0.95} /></mesh>
              <mesh position={[0, 0.31, -0.8]} scale={[0.5, 0.09, 0.2]}><sphereGeometry args={[1, 24, 16]} /><M c="#F8F6F0" r={0.95} /></mesh>
            </group>
          </group>
        </group>
      </group>
      {/* the wardrobe in the back-left corner: doors hinge at the outer edges */}
      <group position={[WARD.x, 0, WARD.z]} rotation={[0, 0, 0.035 * shake]}>
        <group position={[0, 0.03 * Math.abs(shake), 0]}>
          <Bx p={[0, 1.0, 0]} s={[1.0, 2.0, 0.6]} c="#E6DFD0" />
          <Bx p={[0, 2.03, 0.02]} s={[1.08, 0.07, 0.66]} c="#D6CDBB" />
          <Bx p={[0, 1.0, 0.27]} s={[0.94, 1.86, 0.02]} c="#2A231E" />
          <mesh position={[0, 1.0, 0.345]}><planeGeometry args={[0.03, 1.8]} /><M c="#FFE27A" e="#FFD54A" ei={2.5 * gapGlow} o={gapGlow > 0.01 ? 1 : 0} /></mesh>
          {gapGlow > 0.01 ? <pointLight position={[0, 1.0, 0.6]} intensity={1.2 * gapGlow} distance={2.2} color="#FFD873" /> : null}
          {[-1, 1].map((s) => (
            <group key={s} position={[s * 0.48, 1.0, 0.3]} rotation={[0, s * (s < 0 ? doorL : doorR), 0]}>
              <Bx p={[-s * 0.24, 0, 0.01]} s={[0.47, 1.85, 0.03]} c="#EFE9DC" />
              <Bx p={[-s * 0.24, 0.45, 0.03]} s={[0.36, 0.7, 0.01]} c="#E2DACB" />
              <Bx p={[-s * 0.24, -0.45, 0.03]} s={[0.36, 0.7, 0.01]} c="#E2DACB" />
              <mesh position={[-s * 0.43, 0, 0.04]}><sphereGeometry args={[0.018, 12, 10]} /><M c="#B89A5A" m={0.6} r={0.3} /></mesh>
            </group>
          ))}
        </group>
      </group>
      {/* contact shadows */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[BED.x, 0.01, -0.7]}><planeGeometry args={[1.6, 2.4]} /><meshBasicMaterial color="#000" transparent opacity={0.18} depthWrite={false} /></mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[WARD.x, 0.01, WARD.z + 0.05]}><planeGeometry args={[1.15, 0.8]} /><meshBasicMaterial color="#000" transparent opacity={0.2} depthWrite={false} /></mesh>
      {children}
    </group>
  );
};

// ---------- the Booth (the show's recording booth: the only set that repeats) ----------
const onAirTex = () => textTexture('onair', { w: 256, h: 96, bg: '#2A0A0C', lines: [{ text: 'ON AIR', x: 128, y: 50, size: 58, color: '#FF3B3B', weight: 800 }] });
export const Booth: React.FC<{ tip?: number; spill?: number; children?: React.ReactNode }> = ({ tip = 0, spill = 0, children }) => {
  const foam = foamTex(), onair = onAirTex();
  return (
    <group>
      <Bg color="#15161B" />
      <ambientLight intensity={0.4} color="#FFE2C0" />
      <hemisphereLight args={['#FFD9B0', '#20222A', 0.45]} />
      <spotLight position={[-1.2, 2.6, 1.6]} angle={0.7} penumbra={0.8} intensity={14} color="#FFD7A8" />
      <directionalLight position={[1.5, 2.2, 2.5]} intensity={0.9} color="#FFE9D0" />
      <pointLight position={[0.9, 1.9, -1.2]} intensity={0.8} distance={2.5} color="#FF4040" />
      <mesh rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[6, 6]} /><M c="#2C2E35" r={1} /></mesh>
      <mesh position={[0, 1.4, -1.45]}><planeGeometry args={[4, 2.8]} /><M c="#ffffff" map={foam} r={1} /></mesh>
      <mesh position={[-1.6, 1.4, 0]} rotation={[0, Math.PI / 2, 0]}><planeGeometry args={[4, 2.8]} /><M c="#ffffff" map={foam} r={1} /></mesh>
      <mesh position={[1.7, 1.4, 0]} rotation={[0, -Math.PI / 2, 0]}><planeGeometry args={[4, 2.8]} /><M c="#ffffff" map={foam} r={1} /></mesh>
      <group position={[0.9, 1.95, -1.43]}>
        <Bx p={[0, 0, 0]} s={[0.42, 0.17, 0.05]} c="#1A1A1E" />
        <mesh position={[0, 0, 0.03]}><planeGeometry args={[0.38, 0.14]} /><meshBasicMaterial map={onair ?? undefined} toneMapped={false} /></mesh>
      </group>
      {/* desk, console, mic on its arm, pop filter */}
      <Bx p={[0, 0.74, -0.6]} s={[1.8, 0.05, 0.75]} c="#6B4A35" />
      {[[-0.85, -0.95], [0.85, -0.95], [-0.85, -0.25], [0.85, -0.25]].map(([x, z], i) => <Bx key={i} p={[x, 0.37, z]} s={[0.05, 0.72, 0.05]} c="#3A2A20" />)}
      <group position={[0.55, 0.79, -0.7]} rotation={[-0.25, 0, 0]}>
        <Bx p={[0, 0.03, 0]} s={[0.62, 0.06, 0.4]} c="#1E1F24" />
        {Array.from({ length: 8 }).map((_, i) => (
          <group key={i}>
            <Bx p={[-0.26 + i * 0.075, 0.065, 0.02]} s={[0.012, 0.005, 0.22]} c="#0B0B0D" />
            <Bx p={[-0.26 + i * 0.075, 0.075, 0.02 + ((i * 37) % 9) / 60 - 0.07]} s={[0.035, 0.02, 0.025]} c={['#E8E8E8', '#E33', '#3B7', '#E8E8E8'][i % 4]} />
          </group>
        ))}
      </group>
      <Bx p={[-0.6, 1.0, -0.85]} s={[0.04, 0.5, 0.04]} c="#26272B" />
      <mesh position={[-0.3, 1.25, -0.82]} rotation={[0, 0, -1.2]}><cylinderGeometry args={[0.013, 0.013, 0.62, 10]} /><M c="#26272B" r={0.4} /></mesh>
      <group position={[0, 1.22, -0.72]} rotation={[0.25, 0, 0]}>
        <mesh><cylinderGeometry args={[0.045, 0.04, 0.2, 20]} /><M c="#2B2B2E" r={0.4} m={0.3} /></mesh>
        <mesh position={[0, 0.12, 0]}><sphereGeometry args={[0.05, 20, 16]} /><M c="#B8BCC4" r={0.35} m={0.7} /></mesh>
      </group>
      <group position={[0, 1.33, -0.55]}>
        <mesh><torusGeometry args={[0.075, 0.006, 8, 28]} /><M c="#111" /></mesh>
        <mesh><circleGeometry args={[0.072, 28]} /><M c="#0E0E10" o={0.55} side={THREE.DoubleSide} /></mesh>
      </group>
      {/* the narrator's tea, which goes over when the stunt does */}
      <group position={[0.28, 0.765, -0.38]}><Mug tip={tip} /></group>
      {spill > 0 ? <mesh position={[0.42, 0.768, -0.36]} rotation={[-Math.PI / 2, 0, 0]} scale={[1 + 1.6 * spill, 0.7 + 0.8 * spill, 1]}><circleGeometry args={[0.07, 24]} /><M c="#7A4A2C" r={0.1} /></mesh> : null}
      {children}
    </group>
  );
};
