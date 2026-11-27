// EP21 Mattress Money: the ladder and twist sets (all in the what-if Britain, so they carry the switch grade).
// Corner shop, the Black Friday electronics shop, Nan's kitchen. Invented names and signs only (no real brands).
import React from 'react';
import * as THREE from 'three';
import { Note } from '../../props';
import { textTexture } from '../../kit/text';
import { Bg } from '../../worlds/kit';
import { M, Bx, canvasTex, mixC, RoomLights } from './sets';
import type { Look } from '../../cast/Person';

type V3 = [number, number, number];

// ---------- this episode's guests ----------
export const SHOPKEEPER: Look = {
  name: 'Shopkeeper', skin: '#E7BE9C', skinShade: '#D3A784', hair: '#8C877F', hairStyle: 'bald', eyes: '#4A5A3A',
  jacket: '#7A3B2E', jacketTrim: '#5E2C22', top: '#EFE8D6', legs: '#4A4A52', shoes: '#2A221C', sole: '#1E1814',
  height: 1.98, build: 0.84, collar: 'cardigan', limbs: 0.78, legLen: 1.1, armLen: 1.12, head: 0.95, glasses: true, glassesSize: 0.85,
};
export const ASSISTANT: Look = {
  name: 'Assistant', skin: '#F1C9A5', skinShade: '#DDB38F', hair: '#7A2E22', hairStyle: 'bun', eyes: '#3E5A3A',
  jacket: '#2E5FA8', jacketTrim: '#244C88', top: '#2E5FA8', legs: '#1E1F24', shoes: '#F2F0EA', sole: '#D6D1C6',
  height: 1.42, build: 0.9, collar: 'hoodie', head: 1.08,
};

// ---------- textures ----------
const lino = () => canvasTex('lino', 128, 128, (g) => {
  for (let y = 0; y < 4; y++) for (let x = 0; x < 4; x++) { g.fillStyle = (x + y) % 2 ? '#D9D2C2' : '#8F9A86'; g.fillRect(x * 32, y * 32, 32, 32); }
}, [6, 6]);
const tiles = () => canvasTex('tiles', 128, 128, (g) => {
  g.fillStyle = '#F1EDE3'; g.fillRect(0, 0, 128, 128); g.strokeStyle = '#CFC8BA'; g.lineWidth = 3;
  for (let i = 0; i <= 128; i += 32) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i, 128); g.moveTo(0, i); g.lineTo(128, i); g.stroke(); }
  g.fillStyle = '#5B7FB0'; for (let y = 16; y < 128; y += 64) for (let x = 16; x < 128; x += 64) { g.beginPath(); g.arc(x, y, 6, 0, Math.PI * 2); g.fill(); }
}, [8, 4]);
const floral = () => canvasTex('floral', 256, 256, (g) => {
  g.fillStyle = '#E9D8C4'; g.fillRect(0, 0, 256, 256);
  for (let y = 0; y < 256; y += 64) for (let x = (y / 64) % 2 ? 32 : 0; x < 256; x += 64) {
    g.fillStyle = '#C46B6B'; for (let k = 0; k < 5; k++) { g.beginPath(); g.arc(x + 32 + 9 * Math.cos(k * 1.26), y + 32 + 9 * Math.sin(k * 1.26), 6, 0, Math.PI * 2); g.fill(); }
    g.fillStyle = '#E8C25A'; g.beginPath(); g.arc(x + 32, y + 32, 4, 0, Math.PI * 2); g.fill();
    g.fillStyle = '#6E8F5E'; g.fillRect(x + 31, y + 42, 2, 14);
  }
}, [5, 3]);
const greyTiles = () => canvasTex('greytiles', 128, 128, (g) => {
  g.fillStyle = '#BFC3C8'; g.fillRect(0, 0, 128, 128); g.strokeStyle = '#A6AAB0'; g.lineWidth = 2;
  for (let i = 0; i <= 128; i += 64) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i, 128); g.moveTo(0, i); g.lineTo(128, i); g.stroke(); }
}, [6, 6]);
const sign = (key: string, w: number, h: number, bg: string, lines: { text: string; y: number; size: number; color: string; font?: 'Inter' | 'JetBrains Mono' }[]) =>
  textTexture(key, { w, h, bg, lines: lines.map((l) => ({ ...l, x: w / 2, weight: 800 })) });
const Sign: React.FC<{ p: V3; w: number; h: number; tex: THREE.Texture | null; rot?: V3; glow?: boolean }> = ({ p, w, h, tex, rot, glow }) => (
  <mesh position={p} rotation={rot}><planeGeometry args={[w, h]} />{glow ? <meshBasicMaterial map={tex ?? undefined} toneMapped={false} /> : <M c="#ffffff" map={tex} r={0.7} />}</mesh>
);

// ---------- props ----------
export const Milk: React.FC = () => (
  <group>
    <mesh position={[0, 0.09, 0]}><cylinderGeometry args={[0.04, 0.045, 0.18, 20]} /><M c="#F7F7F2" r={0.3} /></mesh>
    <mesh position={[0, 0.19, 0]}><cylinderGeometry args={[0.028, 0.035, 0.03, 20]} /><M c="#F7F7F2" r={0.3} /></mesh>
    <mesh position={[0, 0.21, 0]}><cylinderGeometry args={[0.03, 0.03, 0.012, 20]} /><M c="#2E7D4F" r={0.5} /></mesh>
  </group>
);
export const Loaf: React.FC = () => (
  <group>
    <mesh position={[0, 0.07, 0]} scale={[1, 0.75, 0.6]}><capsuleGeometry args={[0.08, 0.14, 8, 16]} /><M c="#C98A45" r={0.9} /></mesh>
    <Bx p={[0, 0.07, 0]} s={[0.1, 0.13, 0.2]} c="#E9E2CC" r={0.95} />
  </group>
);
/** a receipt strip printing out: u 0..1 */
export const Receipt: React.FC<{ u: number }> = ({ u }) => {
  const tex = textTexture('receipt2', {
    w: 256, h: 512, bg: '#FBFAF4',
    lines: [
      { text: 'CORNER SHOP', x: 128, y: 40, size: 26, color: '#222', weight: 800, font: 'JetBrains Mono' },
      { text: 'MILK + BREAD', x: 128, y: 105, size: 24, color: '#222', weight: 500, font: 'JetBrains Mono' },
      { text: '2016:  £10', x: 128, y: 205, size: 34, color: '#222', weight: 800, font: 'JetBrains Mono' },
      { text: 'NOW: ~£14', x: 128, y: 285, size: 36, color: '#C0272D', weight: 800, font: 'JetBrains Mono' },
      { text: 'PRICES UP 37%', x: 128, y: 385, size: 22, color: '#555', weight: 500, font: 'JetBrains Mono' },
      { text: 'ILLUSTRATIVE', x: 128, y: 465, size: 18, color: '#777', weight: 500, font: 'JetBrains Mono' },
    ],
  });
  const L = 0.28 * Math.max(0.02, u);
  if (tex) { tex.repeat.set(1, Math.max(0.02, u)); tex.offset.set(0, 1 - Math.max(0.02, u)); }
  return <mesh position={[0, L / 2, 0]}><planeGeometry args={[0.14, L]} /><meshStandardMaterial map={tex ?? undefined} color="#ffffff" roughness={0.9} side={THREE.DoubleSide} /></mesh>;
};
export const Till: React.FC<{ drawer?: number; receipt?: number }> = ({ drawer = 0, receipt = 0 }) => (
  <group>
    <Bx p={[0, 0.06, 0]} s={[0.4, 0.12, 0.38]} c="#2B2D33" r={0.5} />
    <Bx p={[0, 0.03, 0.12 + 0.2 * drawer]} s={[0.36, 0.06, 0.2]} c="#3A3D45" r={0.5} />
    <Bx p={[0, 0.2, -0.08]} s={[0.3, 0.18, 0.04]} rot={[-0.35, 0, 0]} c="#1A1B1F" r={0.3} e="#7FE3C0" ei={0.25} />
    <Bx p={[0.32, 0.07, 0]} s={[0.16, 0.14, 0.18]} c="#E6E3DA" r={0.6} />
    <group position={[0.32, 0.15, 0.05]} rotation={[-0.22, 0, 0]}><Receipt u={receipt} /></group>
  </group>
);
export const TVBox: React.FC<{ flip?: number; tagX?: number }> = ({ flip = 0, tagX = 0.5 }) => {
  const front = sign('tvbox', 512, 384, '#1E2230', [
    { text: 'MEGA 75" TV', y: 90, size: 64, color: '#FFFFFF' },
    { text: '-70%', y: 230, size: 150, color: '#FFD400' },
    { text: 'BLACK FRIDAY', y: 340, size: 44, color: '#FF4040' },
  ]);
  const tagA = sign('tagA', 256, 160, '#FFD400', [{ text: '-70%', y: 85, size: 96, color: '#1E1E1E' }]);
  const tagB = sign('tagB', 256, 160, '#FFFFFF', [{ text: 'SAME AS', y: 55, size: 42, color: '#1E1E1E' }, { text: 'JULY', y: 115, size: 60, color: '#C0272D' }]);
  return (
    <group>
      <Bx p={[0, 0.55, 0]} s={[1.3, 1.1, 0.22]} c="#B98F5E" r={0.95} />
      <Sign p={[0, 0.58, 0.112]} w={1.24} h={0.93} tex={front} />
      {/* the swing tag on a string: flips over to show the truth */}
      <group position={[tagX, 1.02, 0.14]} rotation={[0, flip * Math.PI, 0]}>
        <mesh position={[0, 0.0, 0]}><cylinderGeometry args={[0.002, 0.002, 0.06, 4]} /><M c="#EDEDED" /></mesh>
        <Sign p={[0, -0.115, 0.002]} w={0.28} h={0.175} tex={tagA} />
        <Sign p={[0, -0.115, -0.002]} w={0.28} h={0.175} tex={tagB} rot={[0, Math.PI, 0]} />
      </group>
    </group>
  );
};
export const BiscuitTin: React.FC<{ open?: number }> = ({ open = 1 }) => (
  <group>
    <mesh position={[0, 0.06, 0]}><cylinderGeometry args={[0.13, 0.13, 0.12, 32, 1, true]} /><M c="#2D4F8E" r={0.4} m={0.4} side={THREE.DoubleSide} /></mesh>
    <mesh position={[0, 0.004, 0]} rotation={[-Math.PI / 2, 0, 0]}><circleGeometry args={[0.13, 32]} /><M c="#2D4F8E" /></mesh>
    <mesh position={[0, 0.1, 0]}><torusGeometry args={[0.131, 0.006, 8, 32]} /><M c="#C9A43A" m={0.6} r={0.3} /></mesh>
    {/* crumbs of money: notes shrunk almost to nothing */}
    {Array.from({ length: 14 }).map((_, i) => (
      <group key={i} position={[0.07 * Math.cos(i * 2.3), 0.03 + 0.004 * (i % 4), 0.07 * Math.sin(i * 2.3)]} rotation={[0, i, 0]}><Note s={0.12} /></group>
    ))}
    {/* the lid: on top when shut, flies off in an arc and lands leaning against the tin */}
    <group position={[0.24 * open, 0.125 + 0.32 * Math.sin(Math.PI * Math.min(1, open)) + 0.005 * open, 0.06 * open]} rotation={[0.3 * open, 2.5 * open, -1.25 * open]}>
      <mesh><cylinderGeometry args={[0.137, 0.137, 0.03, 32]} /><M c="#B3262E" r={0.4} m={0.3} /></mesh>
      <mesh position={[0, 0.016, 0]} rotation={[-Math.PI / 2, 0, 0]}><circleGeometry args={[0.1, 28]} /><M c="#E7C65A" r={0.4} m={0.4} /></mesh>
    </group>
  </group>
);
export const SavingsJar: React.FC = () => {
  const lbl = sign('savings', 256, 128, '#F3E9CF', [{ text: 'SAVINGS', y: 50, size: 52, color: '#1F3A68' }, { text: 'earning', y: 100, size: 30, color: '#6B5A45' }]);
  return (
    <group>
      <mesh position={[0, 0.15, 0]}><cylinderGeometry args={[0.1, 0.1, 0.3, 28]} /><meshStandardMaterial color="#DDEFF5" transparent opacity={0.35} roughness={0.05} /></mesh>
      <mesh position={[0, 0.32, 0]}><cylinderGeometry args={[0.085, 0.085, 0.04, 28]} /><M c="#C9A43A" m={0.6} r={0.3} /></mesh>
      {/* full-size notes rolled inside */}
      {[0, 1, 2].map((i) => (
        <mesh key={i} position={[-0.035 + 0.035 * i, 0.15, 0.0]} rotation={[0, 0, 0.1 * (i - 1)]}><cylinderGeometry args={[0.028, 0.028, 0.25, 16]} /><M c={['#9C7CC4', '#C97D46', '#9C7CC4'][i]} r={0.8} /></mesh>
      ))}
      <Sign p={[0, 0.15, 0.101]} w={0.15} h={0.075} tex={lbl} />
    </group>
  );
};
export const Magnifier: React.FC = () => (
  <group>
    <mesh><torusGeometry args={[0.055, 0.007, 10, 32]} /><M c="#2A2420" r={0.4} /></mesh>
    <mesh><circleGeometry args={[0.053, 32]} /><meshStandardMaterial color="#E8F6FF" transparent opacity={0.25} roughness={0.05} side={THREE.DoubleSide} /></mesh>
    <mesh position={[0, -0.1, 0]}><cylinderGeometry args={[0.009, 0.011, 0.1, 12]} /><M c="#6B3A22" /></mesh>
  </group>
);
export const Cane: React.FC = () => (
  <group position={[0, -0.05, 0.02]}>
    <mesh position={[0, -0.42, 0]}><cylinderGeometry args={[0.012, 0.012, 0.84, 10]} /><M c="#5A3A22" r={0.5} /></mesh>
    <mesh position={[0.04, 0.0, 0]} rotation={[0, 0, Math.PI / 2]}><torusGeometry args={[0.04, 0.012, 8, 16, Math.PI]} /><M c="#5A3A22" r={0.5} /></mesh>
  </group>
);

// ---------- the corner shop ----------
const shopSign = () => sign('newsgrocer', 512, 96, '#1F3A68', [{ text: 'NEWS & GROCER', y: 50, size: 56, color: '#F3E9CF' }]);
export const CornerShop: React.FC<{ sw?: number; drawer?: number; receipt?: number; slide?: number; children?: React.ReactNode }> = ({ sw = 1, drawer = 0, receipt = 0, slide = 0, children }) => {
  const ln = lino();
  return (
    <group>
      <RoomLights sw={sw} />
      <Bg color={mixC('#EFE6D2', '#6D63B8', sw)} />
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}><planeGeometry args={[6, 6]} /><M c="#ffffff" map={ln} r={0.6} /></mesh>
      <Bx p={[0, 1.4, -2.3]} s={[6, 2.8, 0.05]} c="#EDE4CF" />
      <Bx p={[0, 0.45, -2.27]} s={[6, 0.9, 0.04]} c="#4E7A5C" />
      {/* shelves of goods behind the counter */}
      {[0, 1, 2, 3].map((r) => (
        <group key={r} position={[0.5, 0.95 + 0.38 * r, -2.1]}>
          <Bx p={[0, 0, 0]} s={[2.6, 0.03, 0.32]} c="#B7A27F" />
          {Array.from({ length: 13 }).map((_, i) => (
            <Bx key={i} p={[-1.2 + 0.2 * i, 0.12, 0]} s={[0.15, 0.22 + 0.05 * ((i * 7 + r) % 3), 0.18]} c={['#D9473B', '#F2C14E', '#3A7CC1', '#4FA36B', '#E58B3A', '#8E5BB5'][(i + r * 2) % 6]} r={0.6} />
          ))}
        </group>
      ))}
      <Sign p={[0.5, 2.55, -2.2]} w={1.7} h={0.32} tex={shopSign()} />
      {/* the drinks fridge on the left */}
      <group position={[-1.45, 0, -1.6]}>
        <Bx p={[0, 1.0, 0]} s={[0.8, 2.0, 0.6]} c="#D7DCE0" />
        <mesh position={[0, 1.0, 0.305]}><planeGeometry args={[0.7, 1.85]} /><M c="#EAF6FF" e="#F4FBFF" ei={0.6} o={0.9} /></mesh>
        {[0, 1, 2, 3].map((r) => Array.from({ length: 4 }).map((_, i) => (
          <mesh key={`${r}${i}`} position={[-0.24 + 0.16 * i, 0.35 + 0.42 * r, 0.2]}><cylinderGeometry args={[0.035, 0.035, 0.2, 12]} /><M c={['#F7F7F2', '#D9473B', '#3A7CC1', '#F2C14E'][(i + r) % 4]} r={0.4} /></mesh>
        )))}
      </group>
      {/* the counter */}
      <group position={[0.55, 0, -0.65]}>
        <Bx p={[0, 0.5, 0]} s={[2.1, 1.0, 0.55]} c="#7A5A3F" />
        <Bx p={[0, 1.015, 0]} s={[2.2, 0.03, 0.62]} c="#E7DCC6" r={0.4} />
        <group position={[0.55, 1.03, -0.05]}><Till drawer={drawer} receipt={receipt} /></group>
        {/* the shopping: half of it slides back */}
        <group position={[-0.5 + 0.12 * slide, 1.03, 0.14 - 0.3 * slide]}><Milk /></group>
        <group position={[-0.22 + 0.1 * slide, 1.03, 0.12 - 0.32 * slide]} rotation={[0, 0.4 + 0.3 * slide, 0]}><Loaf /></group>
        {[0, 1, 2].map((i) => <Bx key={i} p={[-0.85 + 0.12 * i, 1.12, 0.12]} s={[0.1, 0.18, 0.06]} c={['#F2C14E', '#D9473B', '#3A7CC1'][i]} r={0.6} />)}
      </group>
      {children}
    </group>
  );
};

// ---------- the electronics shop on Black Friday ----------
const banner1 = () => sign('bfbanner', 1024, 256, '#0E0E12', [{ text: 'BLACK FRIDAY', y: 110, size: 150, color: '#FFD400' }, { text: 'DEALS END TONIGHT*', y: 215, size: 40, color: '#FFFFFF' }]);
const banner2 = () => sign('bfbanner2', 512, 256, '#E8263A', [{ text: 'UP TO', y: 70, size: 60, color: '#FFFFFF' }, { text: '70% OFF', y: 165, size: 110, color: '#FFFFFF' }]);
export const SaleShop: React.FC<{ sw?: number; shake?: number; children?: React.ReactNode }> = ({ sw = 1, shake = 0, children }) => {
  const gt = greyTiles();
  return (
    <group>
      <RoomLights sw={sw} />
      <directionalLight position={[0, 4, 2]} intensity={0.6} color="#FFFFFF" />
      <Bg color={mixC('#E6E8EC', '#5C57A8', sw)} />
      <mesh rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[7, 7]} /><M c="#ffffff" map={gt} r={0.35} /></mesh>
      <Bx p={[0, 1.6, -2.4]} s={[7, 3.2, 0.05]} c="#F4F4F6" />
      <Sign p={[0, 2.55, -2.35]} w={3.2} h={0.8} tex={banner1()} glow />
      <Sign p={[-1.9, 1.55, -2.34]} w={1.1} h={0.55} tex={banner2()} glow />
      {/* a wall of TVs */}
      {[0, 1].map((r) => [0, 1, 2].map((i) => (
        <group key={`${r}${i}`} position={[0.2 + 0.95 * i, 1.15 + 0.62 * r, -2.33]}>
          <Bx p={[0, 0, 0]} s={[0.86, 0.52, 0.05]} c="#111216" r={0.3} />
          <mesh position={[0, 0, 0.03]}><planeGeometry args={[0.8, 0.46]} /><M c="#1A2A44" e={['#3FA0FF', '#FF7A3F', '#7FE3A0'][(i + r) % 3]} ei={0.55} r={0.2} /></mesh>
        </group>
      )))}
      {/* display plinth */}
      <Bx p={[-0.2, 0.06, -0.9]} s={[1.6, 0.12, 0.8]} c="#2B2D33" r={0.4} />
      {/* the shop front at z = 1: a narrow doorway between two plate-glass windows, pavement outside */}
      <ShopFront shake={shake} />
      {children}
    </group>
  );
};
export const DOOR = { z: 1.0, half: 0.5, top: 2.1 };
const fascia = () => sign('tvaudio', 1024, 160, '#16181F', [{ text: 'TV & AUDIO', y: 84, size: 96, color: '#FFFFFF' }]);
const sticker = () => sign('sticker70', 256, 256, '#FFD400', [{ text: '-70%', y: 128, size: 96, color: '#1E1E1E' }]);
const slabs = () => canvasTex('slabs', 128, 128, (g) => {
  g.fillStyle = '#9EA2A6'; g.fillRect(0, 0, 128, 128); g.strokeStyle = '#7F8387'; g.lineWidth = 3;
  for (let i = 0; i <= 128; i += 64) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i, 128); g.moveTo(0, i); g.lineTo(128, i); g.stroke(); }
}, [5, 3]);
export const ShopFront: React.FC<{ shake?: number }> = ({ shake = 0 }) => {
  const sl = slabs(), fa = fascia(), st = sticker();
  const z = DOOR.z, h = DOOR.half;
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.004, z + 1.3]}><planeGeometry args={[7, 2.6]} /><M c="#ffffff" map={sl} r={0.9} /></mesh>
      <group position={[0.012 * shake, 0, 0]}>
        {/* door posts and lintel */}
        {[-1, 1].map((k) => <Bx key={k} p={[k * (h + 0.06), DOOR.top / 2, z]} s={[0.12, DOOR.top, 0.14]} c="#2B2D33" r={0.4} />)}
        <Bx p={[0, DOOR.top + 0.06, z]} s={[2 * h + 0.24, 0.12, 0.14]} c="#2B2D33" r={0.4} />
      </group>
      {/* the fascia sign across the whole front */}
      <Bx p={[0, 2.6, z]} s={[6, 0.7, 0.12]} c="#16181F" />
      <Sign p={[0, 2.6, z + 0.065]} w={2.6} h={0.42} tex={fa} glow />
      {/* stall risers and the glass either side of the door */}
      {[-1, 1].map((k) => (
        <group key={k}>
          <Bx p={[k * 1.6, 0.22, z]} s={[2.0, 0.44, 0.14]} c="#2B2D33" r={0.4} />
          <mesh position={[k * 1.6, 1.32, z]}><planeGeometry args={[2.0, 1.76]} /><meshStandardMaterial color="#CFE8F2" transparent opacity={0.14} roughness={0.05} depthWrite={false} /></mesh>
          <Bx p={[k * 1.6, 2.22, z]} s={[2.0, 0.06, 0.12]} c="#2B2D33" />
          <Sign p={[k * 1.25, 1.55, z + 0.01]} w={0.42} h={0.42} tex={st} />
        </group>
      ))}
    </group>
  );
};

// ---------- Nan's kitchen ----------
export const NanKitchen: React.FC<{ sw?: number; children?: React.ReactNode }> = ({ sw = 1, children }) => {
  const tl = tiles(), fl = floral();
  return (
    <group>
      <RoomLights sw={sw} />
      <Bg color={mixC('#F4E8D6', '#6D63B8', sw)} />
      <mesh rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[6, 6]} /><M c="#ffffff" map={lino()} r={0.6} /></mesh>
      <mesh position={[0, 1.95, -2.2]}><planeGeometry args={[6, 1.5]} /><M c="#ffffff" map={fl} /></mesh>
      <mesh position={[0, 0.6, -2.2]}><planeGeometry args={[6, 1.2]} /><M c="#ffffff" map={tl} r={0.4} /></mesh>
      {/* worktop, kettle, teapot */}
      <Bx p={[0, 0.45, -1.95]} s={[4, 0.9, 0.55]} c="#6E8F5E" />
      <Bx p={[0, 0.915, -1.95]} s={[4.05, 0.04, 0.6]} c="#E9E2D3" r={0.4} />
      <group position={[-0.9, 0.94, -1.95]}>
        <mesh position={[0, 0.12, 0]}><cylinderGeometry args={[0.09, 0.11, 0.24, 20]} /><M c="#D8DDE2" m={0.7} r={0.25} /></mesh>
        <mesh position={[0.1, 0.18, 0]} rotation={[0, 0, -0.8]}><cylinderGeometry args={[0.015, 0.02, 0.12, 10]} /><M c="#D8DDE2" m={0.7} r={0.25} /></mesh>
      </group>
      <group position={[-0.45, 0.94, -1.95]}>
        <mesh position={[0, 0.09, 0]} scale={[1, 0.8, 1]}><sphereGeometry args={[0.11, 20, 16]} /><M c="#7A2E3A" r={0.4} /></mesh>
      </group>
      {/* the window over the sink with net curtains: daylight for the twist */}
      <group position={[0.75, 1.65, -2.18]}>
        <Bx p={[0, 0, 0]} s={[1.0, 0.95, 0.05]} c="#F4F1EA" />
        <mesh position={[0, 0, 0.03]}><planeGeometry args={[0.88, 0.83]} /><M c={mixC('#DDEEFF', '#8FF0E0', sw)} e={mixC('#EEF7FF', '#9FFFF0', sw)} ei={1.0} r={0.2} /></mesh>
        <Bx p={[0, 0, 0.045]} s={[0.04, 0.83, 0.02]} c="#F4F1EA" />
      </group>
      {/* a wall clock */}
      <group position={[-1.6, 2.0, -2.17]}>
        <mesh rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.17, 0.17, 0.04, 28]} /><M c="#F7F3EA" /></mesh>
        <mesh position={[0, 0, 0.025]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[0.17, 0.012, 8, 28]} /><M c="#7A2E3A" /></mesh>
      </group>
      {/* the table with a lace cloth */}
      <group position={[0.05, 0, -0.75]}>
        <mesh position={[0, 0.74, 0]}><cylinderGeometry args={[0.55, 0.55, 0.04, 36]} /><M c="#8A6240" /></mesh>
        <mesh position={[0, 0.765, 0]}><cylinderGeometry args={[0.6, 0.6, 0.01, 36]} /><M c="#FBF8F0" r={0.95} /></mesh>
        <mesh position={[0, 0.37, 0]}><cylinderGeometry args={[0.05, 0.08, 0.72, 16]} /><M c="#6B4A32" /></mesh>
      </group>
      {children}
    </group>
  );
};

// ---------- small props for the ladder and the twist ----------
/** The sales assistant's placard on a stick. */
export const Placard: React.FC = () => {
  const t = sign('placard', 256, 192, '#E8263A', [{ text: 'BLACK', y: 62, size: 64, color: '#FFFFFF' }, { text: 'FRIDAY', y: 132, size: 64, color: '#FFD400' }]);
  return (
    <group position={[0, -0.05, 0.03]}>
      <mesh position={[0, 0.25, 0]}><cylinderGeometry args={[0.012, 0.012, 0.75, 8]} /><M c="#B98F5E" /></mesh>
      <Bx p={[0, 0.72, 0]} s={[0.42, 0.32, 0.012]} c="#E8263A" />
      <Sign p={[0, 0.72, 0.007]} w={0.4} h={0.3} tex={t} />
    </group>
  );
};
/** Nan's butter knife, held in a fist (the blade points along -y). */
export const ButterKnife: React.FC = () => (
  <group position={[0, -0.04, 0.02]}>
    <mesh position={[0, 0.02, 0]}><cylinderGeometry args={[0.011, 0.011, 0.09, 10]} /><M c="#F1EDE3" r={0.5} /></mesh>
    <Bx p={[0, -0.08, 0]} s={[0.022, 0.12, 0.003]} c="#D8DDE2" r={0.25} />
  </group>
);
/** A round digestive biscuit: `snap` 0..1 moves the broken-off piece (more than a quarter of it) away along `to`. */
export const Biscuit: React.FC<{ snap?: number; to?: V3; gone?: boolean }> = ({ snap = 0, to = [0.06, 0.04, 0], gone = false }) => (
  <group rotation={[Math.PI / 2, 0, 0]}>
    <mesh rotation={[0, 0.3 * Math.PI, 0]}><cylinderGeometry args={[0.036, 0.036, 0.008, 28, 1, false, 0, Math.PI * 2 * (snap > 0 ? 0.7 : 1)]} /><M c="#C99A5B" r={0.95} /></mesh>
    {snap > 0 && !gone ? (
      <group position={[to[0] * snap, to[2] * snap, -to[1] * snap]} rotation={[0, 0.3 * Math.PI, 0.4 * snap]}>
        <mesh><cylinderGeometry args={[0.036, 0.036, 0.008, 12, 1, false, Math.PI * 2 * 0.7, Math.PI * 2 * 0.3]} /><M c="#C99A5B" r={0.95} /></mesh>
      </group>
    ) : null}
  </group>
);
/** The magnifying glass with a huge eye in the lens (the eye looks at the camera). */
export const BigEyeGlass: React.FC<{ blink?: number }> = ({ blink = 0 }) => (
  <group>
    <Magnifier />
    <group position={[0, 0, 0.004]}>
      <mesh scale={[1, 1 - 0.92 * blink, 1]}><circleGeometry args={[0.046, 32]} /><meshBasicMaterial color="#F7F4EE" /></mesh>
      {blink < 0.5 ? <mesh position={[0.004, -0.002, 0.001]}><circleGeometry args={[0.022, 28]} /><meshBasicMaterial color="#3E6B8A" /></mesh> : null}
      {blink < 0.5 ? <mesh position={[0.004, -0.002, 0.002]}><circleGeometry args={[0.011, 24]} /><meshBasicMaterial color="#101014" /></mesh> : null}
      {blink < 0.5 ? <mesh position={[0.012, 0.008, 0.003]}><circleGeometry args={[0.004, 12]} /><meshBasicMaterial color="#FFFFFF" /></mesh> : null}
    </group>
  </group>
);
/** Nan's cup of tea on a saucer. */
export const Teacup: React.FC = () => (
  <group>
    <mesh position={[0, 0.004, 0]}><cylinderGeometry args={[0.07, 0.06, 0.008, 24]} /><M c="#F4F1EA" r={0.3} /></mesh>
    <mesh position={[0, 0.04, 0]}><cylinderGeometry args={[0.045, 0.032, 0.065, 24, 1, true]} /><M c="#F4F1EA" r={0.3} side={THREE.DoubleSide} /></mesh>
    <mesh position={[0, 0.066, 0]} rotation={[-Math.PI / 2, 0, 0]}><circleGeometry args={[0.042, 24]} /><M c="#9A6A42" r={0.2} /></mesh>
    <mesh position={[0.05, 0.04, 0]} rotation={[0, 0, Math.PI / 2]}><torusGeometry args={[0.016, 0.005, 8, 16, Math.PI]} /><M c="#F4F1EA" r={0.3} /></mesh>
  </group>
);
