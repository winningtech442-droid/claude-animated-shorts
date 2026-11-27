// Building blocks for worlds: boxes, prisms, light rigs. Matte, low-poly, soft bevels (guide ch. 7).
import React from 'react';
import * as THREE from 'three';
import { useThree } from '@react-three/fiber';

type V3 = [number, number, number];
export const rnd = (seed: number, i: number) => {
  const x = Math.sin(seed * 127.1 + i * 311.7) * 43758.5453;
  return x - Math.floor(x);
};

export const B: React.FC<{ p: V3; s: V3; c: string; r?: number; m?: number; rot?: V3; e?: string; ei?: number }> = ({ p, s, c, r = 0.85, m = 0, rot, e, ei = 0 }) => (
  <mesh position={p} rotation={rot}>
    <boxGeometry args={s} />
    <meshStandardMaterial color={c} roughness={r} metalness={m} emissive={e ?? '#000000'} emissiveIntensity={ei} />
  </mesh>
);

export const Cyl: React.FC<{ p: V3; r: number; h: number; c: string; rot?: V3; seg?: number; rough?: number; m?: number; e?: string; ei?: number }> = ({ p, r, h, c, rot, seg = 20, rough = 0.8, m = 0, e, ei = 0 }) => (
  <mesh position={p} rotation={rot}>
    <cylinderGeometry args={[r, r, h, seg]} />
    <meshStandardMaterial color={c} roughness={rough} metalness={m} emissive={e ?? '#000000'} emissiveIntensity={ei} />
  </mesh>
);

/** A triangular prism (roofs, pediments): base width w, height h, depth d, apex up. */
export const Prism: React.FC<{ p: V3; w: number; h: number; d: number; c: string }> = ({ p, w, h, d, c }) => {
  const shape = React.useMemo(() => {
    const s = new THREE.Shape();
    s.moveTo(-w / 2, 0); s.lineTo(w / 2, 0); s.lineTo(0, h); s.closePath();
    return new THREE.ExtrudeGeometry(s, { depth: d, bevelEnabled: false });
  }, [w, h, d]);
  return (
    <mesh geometry={shape} position={[p[0], p[1], p[2] - d / 2]}>
      <meshStandardMaterial color={c} roughness={0.9} />
    </mesh>
  );
};

/** Sets the scene's background and fog. (A <color attach> inside a group attaches to the group, not the scene.) */
export const Bg: React.FC<{ color: string; fog?: [string, number, number] }> = ({ color, fog }) => {
  const { scene } = useThree();
  scene.background = new THREE.Color(color);
  scene.fog = fog ? new THREE.Fog(fog[0], fog[1], fog[2]) : null;
  return null;
};

/** Sky, fog and a soft key light. `warm` 0..1 shifts toward dusk. */
export const Sky: React.FC<{ top: string; fog: string; near?: number; far?: number; sun?: number; amb?: number; keyPos?: V3; keyColor?: string }> = ({
  fog, near = 14, far = 60, sun = 1.6, amb = 0.55, keyPos = [6, 10, 8], keyColor = '#FFF1DE', top,
}) => (
  <>
    <Bg color={top} fog={[fog, near, far]} />
    <hemisphereLight args={[top, '#5A5048', amb]} />
    <ambientLight intensity={0.25} />
    <directionalLight position={keyPos} intensity={sun} color={keyColor} />
    <directionalLight position={[-6, 4, -4]} intensity={0.35} color="#BFD2FF" />
  </>
);

/** A window pane that glows (lit room behind it). */
export const Pane: React.FC<{ p: V3; w: number; h: number; lit?: number; frame?: string }> = ({ p, w, h, lit = 0.3, frame = '#F2EEE6' }) => (
  <group position={p}>
    <B p={[0, 0, 0]} s={[w + 0.12, h + 0.12, 0.06]} c={frame} />
    <mesh position={[0, 0, 0.035]}>
      <planeGeometry args={[w, h]} />
      <meshStandardMaterial color="#2D3A4A" emissive="#FFD9A0" emissiveIntensity={lit} roughness={0.2} />
    </mesh>
    <B p={[0, 0, 0.045]} s={[0.04, h, 0.02]} c={frame} />
    <B p={[0, 0, 0.045]} s={[w, 0.04, 0.02]} c={frame} />
  </group>
);
