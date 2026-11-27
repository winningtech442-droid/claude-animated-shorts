// Indoor worlds: corner shop, kitchen, trading floor, tabletop. Generic products: no brands.
import React from 'react';
import { B, Bg, Cyl, Pane, rnd } from './kit';
import { ChartScreen, Meter } from '../props';
import { textTexture } from '../kit/text';

type V3 = [number, number, number];

const Room: React.FC<{ w: number; d: number; h: number; wall: string; floor: string; side?: string; ceil?: string }> = ({ w, d, h, wall, floor, side, ceil = '#EDE8DF' }) => (
  <group>
    <B p={[0, -0.05, d / 2 - 1]} s={[w, 0.1, d]} c={floor} />
    <B p={[0, h / 2, -1]} s={[w, h, 0.1]} c={wall} />
    <B p={[-w / 2, h / 2, d / 2 - 1]} s={[0.1, h, d]} c={side ?? wall} />
    <B p={[w / 2, h / 2, d / 2 - 1]} s={[0.1, h, d]} c={side ?? wall} />
    <B p={[0, h, d / 2 - 1]} s={[w, 0.1, d]} c={ceil} />
  </group>
);

const Lights: React.FC<{ bg: string; sun?: number; warm?: string; amb?: number }> = ({ bg, sun = 1.3, warm = '#FFE6C4', amb = 0.7 }) => (
  <>
    <Bg color={bg} />
    <hemisphereLight args={['#FFF6EA', '#6B5E52', amb]} />
    <ambientLight intensity={0.3} />
    <directionalLight position={[2, 5, 6]} intensity={sun} color={warm} />
    <pointLight position={[0, 2.6, 1.5]} intensity={6} distance={9} color={warm} />
  </>
);

/** A corner shop: shelves of generic goods on the back wall, a counter with a till at the front right.
 *  Anchors: shelf price tags at y 1.0-1.6 on z -0.55; customer stands about (0, 0, 1.2). */
export const SHOP = { shelfZ: -0.55, counter: [1.8, 0, 0.6] as V3, till: [1.8, 1.05, 0.55] as V3, customer: [0, 0, 1.2] as V3 };
export const CornerShop: React.FC<{ t: number }> = () => {
  const goods = ['#D9483B', '#F2B33D', '#3A7CC2', '#4FA35C', '#E8E2D2', '#8A4FB5', '#F07C2E', '#2E9C9A'];
  const open = textTexture('shopsign', { w: 512, h: 128, bg: '#1F3A5F', lines: [{ text: 'OPEN 7 TIL 11', x: 256, y: 68, size: 64, color: '#FFD45A', weight: 800 }] });
  return (
    <group>
      <Lights bg="#3A2E26" />
      <Room w={7} d={6} h={3} wall="#E9DFC9" floor="#9A8E7E" side="#DDD1B8" />
      {/* floor tiles */}
      {Array.from({ length: 12 }).map((_, i) => <B key={i} p={[-3.25 + i * 0.6, 0.002, 2]} s={[0.02, 0.005, 6]} c="#857A6B" />)}
      {/* back shelving: four shelves of boxes, tins and bottles */}
      {[0.35, 0.85, 1.35, 1.85].map((y, r) => (
        <group key={r}>
          <B p={[-0.6, y - 0.05, -0.75]} s={[5, 0.04, 0.45]} c="#8A6A4A" />
          {Array.from({ length: 18 }).map((_, i) => {
            const h = 0.22 + rnd(r, i) * 0.18;
            const c = goods[(i * 3 + r * 5) % goods.length];
            return rnd(r + 9, i) > 0.5 ? (
              <B key={i} p={[-3 + i * 0.27, y + h / 2 - 0.03, -0.75]} s={[0.22, h, 0.3]} c={c} r={0.5} />
            ) : (
              <Cyl key={i} p={[-3 + i * 0.27, y + h / 2 - 0.03, -0.75]} r={0.08} h={h} c={c} rough={0.4} m={0.3} />
            );
          })}
        </group>
      ))}
      {/* fridge on the left, glowing */}
      <group position={[-3.0, 0, 0.4]}>
        <B p={[0, 1.05, 0]} s={[0.9, 2.1, 0.8]} c="#2A2F36" />
        <mesh position={[0.46, 1.1, 0]} rotation={[0, Math.PI / 2, 0]}>
          <planeGeometry args={[0.7, 1.8]} />
          <meshStandardMaterial color="#BFE3F2" emissive="#9AD8F0" emissiveIntensity={0.8} transparent opacity={0.85} />
        </mesh>
      </group>
      {/* counter and till */}
      <group position={SHOP.counter}>
        <B p={[0, 0.5, 0]} s={[1.8, 1.0, 0.8]} c="#6E4E36" />
        <B p={[0, 1.02, 0]} s={[1.9, 0.05, 0.9]} c="#C9B79A" />
        <B p={[0, 1.15, -0.05]} s={[0.45, 0.22, 0.35]} c="#2A2F36" />
        <B p={[0, 1.33, -0.15]} s={[0.4, 0.2, 0.04]} c="#1A1D22" rot={[-0.3, 0, 0]} e="#3AE07A" ei={0.4} />
      </group>
      <mesh position={[-0.6, 2.55, -0.94]}>
        <planeGeometry args={[2.2, 0.55]} />
        <meshStandardMaterial map={open ?? undefined} color="#ffffff" emissive="#ffffff" emissiveMap={open ?? undefined} emissiveIntensity={0.3} />
      </mesh>
    </group>
  );
};

/** A kitchen: counter along the back wall with a kettle, a window, a table at the front, a smart meter on the wall.
 *  Anchors: meter on the wall at (1.6, 1.5, -0.9); table top y 0.76 around (0, 0, 1.2). */
export const KITCHEN = { meter: [1.6, 1.5, -0.9] as V3, table: [0, 0.76, 1.2] as V3, stand: [-0.9, 0, 0.5] as V3 };
export const Kitchen: React.FC<{ t: number; meter?: string; alarm?: boolean; night?: boolean; heat?: number; snow?: boolean; steam?: boolean }> = ({ t, meter = '£4.72', alarm = false, night = true, heat = 0, snow = false, steam = false }) => (
  <group>
    <Lights bg="#2E2A30" warm="#FFE0B8" />
    <Room w={6} d={6} h={2.8} wall="#D7E3D6" floor="#B79C7E" side="#C9D7C8" />
    {/* units, worktop, splashback tiles */}
    <B p={[-0.6, 0.45, -0.65]} s={[4.4, 0.9, 0.6]} c="#3F5D73" />
    <B p={[-0.6, 0.92, -0.65]} s={[4.5, 0.05, 0.65]} c="#E8E2D6" />
    {Array.from({ length: 4 }).map((_, i) => <B key={i} p={[-2.4 + i * 1.2, 0.45, -0.34]} s={[0.02, 0.8, 0.02]} c="#2F4757" />)}
    {Array.from({ length: 10 }).map((_, i) => <B key={`t${i}`} p={[-2.8 + i * 0.45, 1.2, -0.94]} s={[0.43, 0.43, 0.02]} c={i % 2 ? '#F2EFE8' : '#E7E3DA'} />)}
    <B p={[-2.4, 1.85, -0.75]} s={[1.6, 0.7, 0.4]} c="#3F5D73" />
    {/* window over the sink */}
    <Pane p={[-0.4, 1.75, -0.92]} w={1.3} h={0.9} lit={night ? 0.05 : 0.9} />
    {/* kettle */}
    <group position={[0.7, 0.95, -0.65]}>
      <Cyl p={[0, 0.13, 0]} r={0.1} h={0.26} c="#C8CCD0" rough={0.25} m={0.8} />
      <B p={[0.12, 0.14, 0]} s={[0.04, 0.16, 0.04]} c="#2A2F36" />
    </group>
    {/* smart meter on the wall */}
    <group position={KITCHEN.meter}>
      <Meter value={meter} alarm={alarm} s={3} />
    </group>
    {/* radiator */}
    <group position={[2.4, 0.55, -0.9]}>{Array.from({ length: 8 }).map((_, i) => <B key={i} p={[i * 0.08 - 0.3, 0, 0]} s={[0.05, 0.6, 0.1]} c="#F2F0EA" e="#FF7A2E" ei={heat * (0.55 + 0.1 * Math.sin(t * 5 + i))} />)}
      {heat > 0 ? <pointLight position={[0, 0.2, 0.4]} intensity={heat * 3} distance={2.5} color="#FF8A3D" /> : null}</group>
    {/* snow falling past the window (Ep 05: winter) */}
    {snow ? Array.from({ length: 40 }).map((_, i) => {
      const y = 0.45 - ((rnd(i, 1) * 0.9 + t * 0.35) % 0.9);
      return <mesh key={`sn${i}`} position={[-0.4 + (rnd(i, 2) - 0.5) * 1.2 + Math.sin(t * 2 + i) * 0.03, 1.75 + y, -0.89]}><sphereGeometry args={[0.012, 6, 4]} /><meshBasicMaterial color="#FFFFFF" /></mesh>;
    }) : null}
    {/* steam off the kettle */}
    {steam ? Array.from({ length: 7 }).map((_, i) => {
      const k = (rnd(i, 3) + t * 0.6) % 1;
      return <mesh key={`st${i}`} position={[0.7 + Math.sin(t * 3 + i) * 0.04, 1.25 + k * 0.5, -0.65]} scale={0.04 + k * 0.08}><sphereGeometry args={[1, 10, 8]} /><meshStandardMaterial color="#FFFFFF" transparent opacity={0.55 * (1 - k)} /></mesh>;
    }) : null}
    {/* table and chairs */}
    <B p={[0, 0.74, 1.2]} s={[1.4, 0.05, 0.9]} c="#A47A52" />
    {[[-0.6, 0.85], [0.6, 0.85], [-0.6, 1.55], [0.6, 1.55]].map(([x, z], i) => <B key={i} p={[x, 0.37, z]} s={[0.05, 0.74, 0.05]} c="#7E5A3C" />)}
  </group>
);

/** A trading floor: rows of desks with chart screens, a wall board with a big rate. `crash` turns screens and light red. */
export const FLOOR = { board: [0, 2.6, -3.8] as V3, desk: [0, 0, 0.6] as V3 };
export const TradingFloor: React.FC<{ t: number; crash?: boolean; board?: string; boardSub?: string; p?: number }> = ({ t, crash = false, board = 'GBP 2.77', boardSub = 'STERLING', p = 1 }) => {
  const tex = textTexture(`board${board}${boardSub}${crash}`, {
    w: 1024, h: 384, bg: '#0B0F14',
    lines: [
      { text: boardSub, x: 512, y: 70, size: 54, color: '#8FA3B8', weight: 600, font: 'JetBrains Mono' },
      { text: board, x: 512, y: 220, size: 190, color: crash ? '#FF4D57' : '#3AE07A', weight: 800, font: 'JetBrains Mono' },
    ],
  });
  return (
    <group>
      <Bg color={crash ? '#1A0B0E' : '#0D1218'} />
      <hemisphereLight args={[crash ? '#FFB0B0' : '#C8D8F0', '#20242A', 0.5]} />
      <ambientLight intensity={0.25} />
      <directionalLight position={[2, 6, 5]} intensity={1.1} color="#E8EEF8" />
      <pointLight position={[0, 3, -2]} intensity={crash ? 18 : 10} distance={12} color={crash ? '#FF3B47' : '#7FB7FF'} />
      <B p={[0, -0.05, 0]} s={[16, 0.1, 14]} c="#2A2E35" />
      <B p={[0, 2.5, -4]} s={[16, 5, 0.1]} c="#1C2027" />
      <mesh position={FLOOR.board}>
        <planeGeometry args={[5.4, 2.0]} />
        <meshBasicMaterial map={tex ?? undefined} toneMapped={false} />
      </mesh>
      {/* three rows of desks, each desk with two screens */}
      {[-2.2, -0.8, 0.6].map((z, r) =>
        [-3.6, -1.8, 0, 1.8, 3.6].map((x, i) => (
          <group key={`${r}${i}`} position={[x, 0, z]}>
            <B p={[0, 0.74, 0]} s={[1.6, 0.05, 0.8]} c="#5A5F68" />
            <B p={[0, 0.37, 0]} s={[1.5, 0.72, 0.05]} c="#3A3E45" />
            {[-0.38, 0.38].map((dx, k) => (
              <group key={k} position={[dx, 1.06, -0.18]} rotation={[-0.08, k ? -0.12 : 0.12, 0]}>
                <ChartScreen up={!crash && rnd(r * 5 + i, k) > 0.35} p={p} label={k ? 'FTSE' : 'GBP'} s={1.05} />
              </group>
            ))}
          </group>
        )),
      )}
    </group>
  );
};

/** A wooden tabletop for close-ups of coins, notes and tags. Props go on y = 0. */
export const Tabletop: React.FC<{ t: number; wood?: string; lamp?: string }> = ({ wood = '#8A5E3C', lamp = '#FFE2B8' }) => (
  <group>
    <Bg color={'#1E1914'} />
    <hemisphereLight args={['#FFF0DC', '#3A2E24', 0.6]} />
    <ambientLight intensity={0.25} />
    <directionalLight position={[0.6, 2, 0.8]} intensity={2.0} color={lamp} />
    <pointLight position={[-0.3, 0.6, 0.3]} intensity={0.8} distance={3} color="#FFD7A0" />
    <B p={[0, -0.02, 0]} s={[3, 0.04, 2]} c={wood} r={0.6} />
    {Array.from({ length: 14 }).map((_, i) => <B key={i} p={[0, 0.0005, -0.95 + i * 0.14]} s={[3, 0.001, 0.004]} c="#6E4A2E" />)}
  </group>
);
