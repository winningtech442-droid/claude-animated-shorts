// Outdoor worlds: a terraced street and a bank front. Generic: no real buildings, logos or brands.
import React from 'react';
import { B, Cyl, Prism, Pane, Sky, rnd } from './kit';
import { textTexture } from '../kit/text';
import { SaleBoard } from '../props';

type V3 = [number, number, number];
const BRICKS = ['#9C4A33', '#A85A3C', '#8E4430', '#B0644A', '#94503A', '#A04E36'];
const DOORS = ['#B3262E', '#1F3A5F', '#2E5D3A', '#1A1A1A', '#6B2F5A', '#C8A040'];

/** A terraced street at dusk: six houses facing +z along x, pavement at z 0..2, road beyond.
 *  Anchors: people stand on the pavement at y 0, z about 1. */
export const STREET = { pavement: 1.0, doorZ: -0.02, houseW: 4.4, postbox: [3.2, 0, 1.6] as V3, busStop: [-6.5, 0, 1.7] as V3 };
/** Era dressing (one street, three looks; the gate counts a new era as a new set):
 *   '2026' (default) as built; '1988' sodium-orange lamps, a boxy hatchback, estate agents' boards (`boards` 0-6,
 *   slammed into the gardens one after another from local time `slam`); '1975' power cut: lamps off, dark
 *   windows with a few candles. Period check (script-rules 6): no modern cars, phones or dishes in 1975/1988. */
const clamp01 = (x: number) => Math.min(1, Math.max(0, x));
const bounce = (u: number) => { const n = 7.5625, d = 2.75;
  if (u < 1 / d) return n * u * u; if (u < 2 / d) return n * (u -= 1.5 / d) * u + 0.75; if (u < 2.5 / d) return n * (u -= 2.25 / d) * u + 0.9375; return n * (u -= 2.625 / d) * u + 0.984375; };
const Hatchback: React.FC<{ p: V3; c: string }> = ({ p, c }) => (
  <group position={p}>
    <B p={[0, 0.45, 0]} s={[3.6, 0.55, 1.6]} c={c} r={0.4} />
    <B p={[-0.2, 0.95, 0]} s={[2.2, 0.5, 1.5]} c={c} r={0.4} />
    <B p={[-0.2, 0.95, 0.76]} s={[2.0, 0.38, 0.02]} c="#2D3A4A" r={0.1} />
    <B p={[1.82, 0.45, 0]} s={[0.04, 0.2, 1.3]} c="#E8E2D2" e="#FFE9B0" ei={0.4} />
    {[[-1.2, 0.8], [1.2, 0.8], [-1.2, -0.8], [1.2, -0.8]].map(([x, z], i) => <Cyl key={i} p={[x, 0.3, z]} r={0.3} h={0.2} c="#1E1E1E" rot={[Math.PI / 2, 0, 0]} />)}
  </group>
);
export const Street: React.FC<{ t: number; lt?: number; night?: number; sale?: string; era?: '1975' | '1988' | '2026'; boards?: number; slam?: number }> = ({ t, lt = 0, night: night0 = 0.35, sale, era = '2026', boards = 0, slam = 0 }) => {
  const cut = era === '1975';
  const night = cut ? Math.max(night0, 0.9) : night0;
  const lampC = era === '1988' ? '#FF9A3C' : '#FFC864';
  const sign = sale ? textTexture(`sale${sale}`, { w: 512, h: 160, bg: '#C0272D', lines: [{ text: sale, x: 256, y: 84, size: 92, color: '#FFFFFF', weight: 800 }] }) : null;
  return (
    <group>
      <Sky top={cut ? '#141A2E' : night > 0.5 ? '#2A3354' : '#E9A27A'} fog={cut ? '#141A2E' : night > 0.5 ? '#2A3354' : '#D99A7E'} sun={cut ? 0.35 : 1.2 + (1 - night) * 0.6} amb={cut ? 0.22 : 0.55} keyColor={cut ? '#9FB0D8' : '#FFD8B0'} keyPos={[-8, 7, 10]} near={12} far={45} />
      {/* road, kerb, pavement */}
      <B p={[0, -0.05, 6]} s={[60, 0.1, 8]} c="#454B52" />
      {Array.from({ length: 10 }).map((_, i) => <B key={i} p={[-27 + i * 6, 0.005, 6]} s={[2.4, 0.01, 0.14]} c="#E8E2D2" />)}
      <B p={[0, 0.06, 2.05]} s={[60, 0.12, 0.25]} c="#9A9890" />
      <B p={[0, 0.05, 1.0]} s={[60, 0.1, 2]} c="#B9B4AA" />
      {Array.from({ length: 24 }).map((_, i) => <B key={`pv${i}`} p={[-29.5 + i * 2.5, 0.101, 1]} s={[0.02, 0.005, 2]} c="#A29D93" />)}
      {/* the terrace */}
      {Array.from({ length: 6 }).map((_, i) => {
        const x = -11 + i * STREET.houseW;
        const brick = BRICKS[i % BRICKS.length];
        return (
          <group key={i} position={[x, 0, -1.6]}>
            <B p={[0, 3.1, 0]} s={[STREET.houseW - 0.04, 6.2, 3]} c={brick} />
            <B p={[STREET.houseW / 2 - 0.02, 3.1, 0]} s={[0.08, 6.2, 3.02]} c="#7A3A28" />
            <Prism p={[0, 6.2, 0]} w={STREET.houseW + 0.2} h={1.7} d={3.2} c="#4A4E57" />
            <B p={[STREET.houseW / 2 - 0.6, 7.6, -0.6]} s={[0.7, 1.4, 0.7]} c={brick} />
            {[0.25, 0.5].map((dx, k) => <Cyl key={k} p={[STREET.houseW / 2 - 0.6 + (dx - 0.37), 8.45, -0.6]} r={0.09} h={0.4} c="#B5603E" />)}
            {/* door, step, fanlight */}
            <B p={[-1.1, 1.15, 1.52]} s={[1.05, 2.2, 0.08]} c={DOORS[i % DOORS.length]} r={0.4} />
            <Cyl p={[-0.82, 1.15, 1.58]} r={0.04} h={0.04} c="#D8B45A" rot={[Math.PI / 2, 0, 0]} m={0.8} />
            <B p={[-1.1, 0.1, 1.75]} s={[1.4, 0.2, 0.5]} c="#C9C4BA" />
            <Pane p={[-1.1, 2.48, 1.53]} w={0.9} h={0.3} lit={0.4 + night * 0.5} />
            {/* bay window downstairs, two up */}
            <Pane p={[0.85, 1.5, 1.53]} w={1.6} h={1.5} lit={cut ? (rnd(i, 1) > 0.35 ? 0.75 + 0.15 * Math.sin(t * 9 + i) : 0.02) : 0.15 + night * (rnd(i, 1) > 0.4 ? 0.9 : 0.1)} />
            <B p={[0.85, 0.55, 1.6]} s={[1.9, 0.25, 0.22]} c="#E5E0D6" />
            <Pane p={[-1.1, 4.4, 1.53]} w={1.0} h={1.3} lit={cut ? 0.02 : 0.1 + night * (rnd(i, 2) > 0.5 ? 0.8 : 0.05)} />
            <Pane p={[0.85, 4.4, 1.53]} w={1.0} h={1.3} lit={cut ? 0.02 : 0.1 + night * (rnd(i, 3) > 0.6 ? 0.8 : 0.05)} />
            {/* low front wall */}
            <B p={[0.4, 0.35, 2.0]} s={[STREET.houseW - 1.6, 0.5, 0.2]} c={brick} />
          </group>
        );
      })}
      {/* lamp posts */}
      {[-8.5, 8.5].map((x) => (
        <group key={x} position={[x, 0, 1.85]}>
          <Cyl p={[0, 2.2, 0]} r={0.06} h={4.4} c="#2B2F36" />
          <B p={[0, 4.45, 0.25]} s={[0.25, 0.12, 0.6]} c="#2B2F36" />
          <mesh position={[0, 4.36, 0.45]}>
            <sphereGeometry args={[0.13, 12, 8]} />
            <meshStandardMaterial color={cut ? '#5A5A5A' : '#FFE3A8'} emissive={lampC} emissiveIntensity={cut ? 0 : 0.6 + night * 1.6} />
          </mesh>
          {night > 0.3 && !cut ? <pointLight position={[0, 4.1, 0.6]} intensity={night * 6} distance={7} color={lampC} /> : null}
        </group>
      ))}
      {/* a red post box (plain: no royal cypher) */}
      <group position={STREET.postbox}>
        <Cyl p={[0, 0.65, 0]} r={0.27} h={1.3} c="#C3191F" rough={0.4} />
        <mesh position={[0, 1.3, 0]}>
          <sphereGeometry args={[0.28, 20, 10, 0, Math.PI * 2, 0, Math.PI / 2]} />
          <meshStandardMaterial color="#C3191F" roughness={0.4} />
        </mesh>
        <B p={[0, 1.05, 0.26]} s={[0.3, 0.05, 0.04]} c="#1A1A1A" />
      </group>
      {/* bus stop */}
      <group position={STREET.busStop}>
        <B p={[0, 1.2, -0.4]} s={[2.4, 2.4, 0.04]} c="#9FB8C8" r={0.1} />
        <B p={[0, 2.45, 0]} s={[2.6, 0.08, 1.0]} c="#2B2F36" />
        {[-1.2, 1.2].map((x) => <Cyl key={x} p={[x, 1.2, 0.4]} r={0.04} h={2.4} c="#2B2F36" />)}
        <B p={[0, 0.5, -0.25]} s={[1.6, 0.06, 0.3]} c="#3A4048" />
      </group>
      {era === '1988' ? <Hatchback p={[-3.5, 0, 3.4]} c="#8E2B2B" /> : null}
      {/* estate agents' boards in the gardens, slammed in one after another */}
      {Array.from({ length: Math.min(6, boards) }).map((_, i) => {
        const order = [2, 1, 3, 0, 4, 5][i];
        const k = clamp01((lt - slam - i * 0.13) / 0.42);
        if (k <= 0) return null;
        const y = (1 - bounce(k)) * 3.2;
        return <group key={i} position={[-11 + order * STREET.houseW + 1.25, y, 0.22]}><SaleBoard s={0.95} tilt={(rnd(order, 7) - 0.5) * 0.08} /></group>;
      })}
      {sign ? (
        <mesh position={[-2.7, 3.1, 0.05]}>
          <planeGeometry args={[2.4, 0.75]} />
          <meshStandardMaterial map={sign} color="#ffffff" emissive="#ffffff" emissiveMap={sign} emissiveIntensity={0.25} />
        </mesh>
      ) : null}
    </group>
  );
};

/** A classical stone bank front: steps, six columns, pediment, big doors. Generic name only. */
export const BANK = { door: [0, 0, 1.2] as V3, steps: [0, 0, 3.2] as V3 };
export const Bank: React.FC<{ t: number; name?: string; night?: number }> = ({ t, name = 'THE BANK', night = 0 }) => {
  const sign = textTexture(`bank${name}`, { w: 1024, h: 128, bg: '#D9D0BE', lines: [{ text: name, x: 512, y: 68, size: 84, color: '#3A332A', weight: 800 }] });
  const stone = '#D9D0BE';
  return (
    <group>
      <Sky top={night ? '#26304E' : '#9EC3E6'} fog={night ? '#26304E' : '#B8D2EA'} sun={1.7} near={18} far={60} />
      <B p={[0, -0.05, 6]} s={[60, 0.1, 14]} c="#8F8A80" />
      {[0, 1, 2, 3].map((k) => <B key={k} p={[0, 0.12 + k * 0.24, 2.9 - k * 0.45]} s={[14 - k * 0.4, 0.24, 0.9 + k * 0.45]} c="#CFC6B3" />)}
      <B p={[0, 4.6, -0.6]} s={[16, 9.2, 3]} c={stone} />
      <B p={[0, 1.02, 1.0]} s={[13, 0.12, 2.6]} c="#CFC6B3" />
      {Array.from({ length: 6 }).map((_, i) => (
        <group key={i} position={[-5.5 + i * 2.2, 0, 1.6]}>
          <Cyl p={[0, 3.6, 0]} r={0.42} h={5.2} c="#E6DECD" seg={18} />
          <B p={[0, 1.15, 0]} s={[1.05, 0.25, 1.05]} c="#D2C9B6" />
          <B p={[0, 6.3, 0]} s={[1.05, 0.3, 1.05]} c="#D2C9B6" />
        </group>
      ))}
      <B p={[0, 6.8, 1.4]} s={[13.6, 0.7, 1.9]} c={stone} />
      <Prism p={[0, 7.15, 1.4]} w={13.8} h={2.1} d={1.9} c="#D2C9B6" />
      <mesh position={[0, 6.8, 2.36]}>
        <planeGeometry args={[9, 0.6]} />
        <meshStandardMaterial map={sign ?? undefined} color="#ffffff" roughness={0.9} />
      </mesh>
      {/* doors */}
      <B p={[0, 2.6, 0.92]} s={[2.6, 3.4, 0.1]} c="#2C2A26" r={0.5} />
      <B p={[0, 2.6, 0.98]} s={[0.06, 3.4, 0.02]} c="#B89A52" m={0.7} r={0.3} />
      {[-4.4, 4.4].map((x) => <Pane key={x} p={[x, 3.2, 0.92]} w={1.2} h={2.0} lit={night ? 0.7 : 0.1} frame="#CFC6B3" />)}
    </group>
  );
};
