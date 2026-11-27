// Props shared by every world. Generic designs only: no real banknote, coin, logo or brand is reproduced.
import React from 'react';
import * as THREE from 'three';
import { textTexture } from '../kit/text';

const M: React.FC<{ c: string; r?: number; m?: number; e?: string; ei?: number }> = ({ c, r = 0.7, m = 0, e, ei = 0 }) => (
  <meshStandardMaterial color={c} roughness={r} metalness={m} emissive={e ?? '#000000'} emissiveIntensity={ei} />
);

/** A twelve-sided bimetal pound-style coin, generic face (just a £). Lies flat unless `stand`. */
export const Coin: React.FC<{ s?: number; stand?: boolean; spin?: number }> = ({ s = 1, stand = false, spin = 0 }) => {
  const face = textTexture('coinface', { w: 256, h: 256, bg: '#C8A951', lines: [{ text: '£1', x: 128, y: 134, size: 110, color: '#7A5E1E', weight: 800 }],
    draw: (g) => { g.fillStyle = '#B9BCC0'; g.beginPath(); g.arc(128, 128, 84, 0, Math.PI * 2); g.fill(); } });
  return (
    <group scale={s} rotation={stand ? [Math.PI / 2, spin, 0] : [0, spin, 0]}>
      <mesh>
        <cylinderGeometry args={[0.0117, 0.0117, 0.0028, 12]} />
        <M c="#D9B45A" r={0.35} m={0.45} />
      </mesh>
      {[1, -1].map((k) => (
        <mesh key={k} position={[0, k * 0.00145, 0]} rotation={[-k * Math.PI / 2, 0, 0]}>
          <circleGeometry args={[0.0113, 12]} />
          <meshStandardMaterial map={face ?? undefined} color="#ffffff" roughness={0.4} metalness={0.3} />
        </mesh>
      ))}
    </group>
  );
};

/** A stack of n coins. */
export const CoinStack: React.FC<{ n: number; s?: number; lean?: number }> = ({ n, s = 1, lean = 0 }) => (
  <group scale={s}>
    {Array.from({ length: n }).map((_, i) => (
      <group key={i} position={[Math.sin(i * 2.3) * 0.0008 + lean * i * 0.0006, 0.0014 + i * 0.0029, Math.cos(i * 1.7) * 0.0008]}>
        <Coin spin={i * 0.4} />
      </group>
    ))}
  </group>
);

/** A generic banknote: £ value, no portrait, marked ILLUSTRATIVE so it can never be mistaken for real money. */
export const Note: React.FC<{ value?: string; s?: number; tint?: string }> = ({ value = '20', s = 1, tint = '#7E5AA6' }) => {
  const tex = textTexture(`note${value}${tint}`, {
    w: 512, h: 256, bg: '#EDE6D6', border: tint,
    draw: (g) => {
      g.fillStyle = tint; g.globalAlpha = 0.25; g.fillRect(0, 0, 512, 256); g.globalAlpha = 1;
      g.strokeStyle = tint; g.lineWidth = 3; for (let i = 0; i < 9; i++) { g.beginPath(); g.arc(380, 128, 20 + i * 9, 0, Math.PI * 2); g.stroke(); }
    },
    lines: [
      { text: `£${value}`, x: 120, y: 110, size: 96, color: tint, weight: 800 },
      { text: 'ILLUSTRATIVE', x: 120, y: 190, size: 26, color: tint, weight: 700, font: 'JetBrains Mono' },
    ],
  });
  return (
    <mesh scale={s} rotation={[-Math.PI / 2, 0, 0]}>
      <planeGeometry args={[0.14, 0.07]} />
      <meshStandardMaterial map={tex ?? undefined} color="#ffffff" roughness={0.8} side={THREE.DoubleSide} />
    </mesh>
  );
};

/** A shop price tag. `old` draws a struck-through old price above the new one. */
export const PriceTag: React.FC<{ price: string; old?: string; s?: number; color?: string }> = ({ price, old, s = 1, color = '#F6D33C' }) => {
  const tex = textTexture(`tag${price}${old ?? ''}${color}`, {
    w: 512, h: 320, bg: color, border: '#1E1E1E',
    draw: (g) => {
      if (old) { g.font = '700 80px Inter'; g.fillStyle = '#5A4A1A'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(old, 256, 80);
        g.strokeStyle = '#C0272D'; g.lineWidth = 10; g.beginPath(); g.moveTo(130, 92); g.lineTo(382, 66); g.stroke(); }
    },
    lines: [{ text: price, x: 256, y: old ? 210 : 165, size: old ? 150 : 170, color: '#1E1E1E', weight: 800 }],
  });
  return (
    <group scale={s}>
      <mesh>
        <boxGeometry args={[0.32, 0.2, 0.01]} />
        <meshStandardMaterial color={color} roughness={0.6} />
      </mesh>
      <mesh position={[0, 0, 0.0055]}>
        <planeGeometry args={[0.32, 0.2]} />
        <meshStandardMaterial map={tex ?? undefined} color="#ffffff" roughness={0.6} />
      </mesh>
    </group>
  );
};

/** A folded newspaper with a headline (generic masthead). */
export const Newspaper: React.FC<{ headline: string; sub?: string; s?: number }> = ({ headline, sub = '', s = 1 }) => {
  const tex = textTexture(`news${headline}${sub}`, {
    w: 600, h: 800, bg: '#F2EEE4',
    draw: (g) => {
      g.fillStyle = '#1A1A1A'; g.fillRect(30, 30, 540, 90);
      g.fillStyle = '#BDB7AA'; for (let i = 0; i < 14; i++) g.fillRect(30 + (i % 2) * 280, 470 + Math.floor(i / 2) * 42, 260, 14);
    },
    lines: [
      { text: 'THE DAILY POST', x: 300, y: 76, size: 56, color: '#F2EEE4', weight: 800 },
      { text: headline, x: 300, y: 250, size: headline.length > 14 ? 58 : 82, color: '#141414', weight: 800 },
      { text: sub, x: 300, y: 360, size: 34, color: '#3A3A3A', weight: 600 },
    ],
  });
  return (
    <mesh scale={s}>
      <planeGeometry args={[0.36, 0.48]} />
      <meshStandardMaterial map={tex ?? undefined} color="#ffffff" roughness={0.9} side={THREE.DoubleSide} />
    </mesh>
  );
};

/** A screen showing a line chart that rises or falls; `p` (0..1) how much of the line has drawn. */
export const ChartScreen: React.FC<{ up?: boolean; p?: number; label?: string; s?: number }> = ({ up = false, p = 1, label = 'GBP', s = 1 }) => {
  const steps = 10;
  const k = Math.max(1, Math.round(p * steps));
  const tex = textTexture(`chart${up}${k}${label}`, {
    w: 640, h: 400, bg: '#0E1520',
    draw: (g) => {
      g.strokeStyle = '#1F2D3E'; g.lineWidth = 2; for (let i = 1; i < 6; i++) { g.beginPath(); g.moveTo(0, i * 66); g.lineTo(640, i * 66); g.stroke(); }
      g.strokeStyle = up ? '#36D27A' : '#FF4D57'; g.lineWidth = 10; g.lineJoin = 'round'; g.beginPath();
      for (let i = 0; i <= k; i++) { const x = 40 + (560 * i) / steps; const base = up ? 330 - i * 26 : 80 + i * 26; const y = base + ((i * 37) % 23) - 11; i ? g.lineTo(x, y) : g.moveTo(x, y); }
      g.stroke();
    },
    lines: [{ text: label, x: 40, y: 34, size: 30, color: '#9FB0C4', weight: 600, font: 'JetBrains Mono', align: 'left' }],
  });
  return (
    <group scale={s}>
      <mesh>
        <boxGeometry args={[0.66, 0.42, 0.03]} />
        <meshStandardMaterial color="#1A1D22" roughness={0.5} />
      </mesh>
      <mesh position={[0, 0, 0.016]}>
        <planeGeometry args={[0.62, 0.38]} />
        <meshBasicMaterial map={tex ?? undefined} toneMapped={false} />
      </mesh>
    </group>
  );
};

/** A smart energy meter display showing a £ figure. */
export const Meter: React.FC<{ value: string; s?: number; alarm?: boolean }> = ({ value, s = 1, alarm = false }) => {
  const tex = textTexture(`meter${value}${alarm}`, {
    w: 400, h: 300, bg: alarm ? '#3A0D10' : '#0F2A1D',
    lines: [{ text: 'TODAY', x: 200, y: 60, size: 36, color: '#9FC4B0', weight: 600, font: 'JetBrains Mono' }, { text: value, x: 200, y: 170, size: 110, color: alarm ? '#FF6A6A' : '#7CF2A8', weight: 800 }],
  });
  return (
    <group scale={s}>
      <mesh>
        <boxGeometry args={[0.16, 0.13, 0.03]} />
        <meshStandardMaterial color="#E9E6DF" roughness={0.5} />
      </mesh>
      <mesh position={[0, 0.005, 0.016]}>
        <planeGeometry args={[0.12, 0.09]} />
        <meshBasicMaterial map={tex ?? undefined} toneMapped={false} />
      </mesh>
    </group>
  );
};

/** A barrel of oil (for North Sea and fuel stories). */
export const Barrel: React.FC<{ s?: number; color?: string }> = ({ s = 1, color = '#1F3B5A' }) => (
  <group scale={s}>
    <mesh position={[0, 0.44, 0]}>
      <cylinderGeometry args={[0.29, 0.29, 0.88, 28]} />
      <M c={color} r={0.45} m={0.3} />
    </mesh>
    {[0.2, 0.68].map((y) => (
      <mesh key={y} position={[0, y, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[0.292, 0.012, 8, 32]} />
        <M c="#0F1E2E" r={0.5} />
      </mesh>
    ))}
  </group>
);

/** The rate dial (committee room wall, or a table close-up): needle from 0% to 16%, the value under it.
 *  Animate `value` with a non-rounded grow: { key: 'value', ..., round: false }. */
export const Dial: React.FC<{ value: number; s?: number; label?: string; max?: number }> = ({ value, s = 1, label = 'BANK RATE', max = 16 }) => {
  const face = textTexture(`dialface${label}${max}`, {
    w: 512, h: 512, bg: '#F2EBDC',
    draw: (g) => {
      const cx = 256, cy = 270, R = 200;
      g.lineCap = 'round';
      // red zone from 10% up
      g.strokeStyle = '#C8102E'; g.lineWidth = 26; g.beginPath();
      g.arc(cx, cy, R - 20, (-225 + (270 * 10) / max) * Math.PI / 180, (-225 + 270) * Math.PI / 180); g.stroke();
      for (let i = 0; i <= max; i++) {
        const a = (-225 + (270 * i) / max) * Math.PI / 180, big = i % 4 === 0;
        g.strokeStyle = '#2A2420'; g.lineWidth = big ? 8 : 4;
        g.beginPath(); g.moveTo(cx + Math.cos(a) * (R - (big ? 48 : 34)), cy + Math.sin(a) * (R - (big ? 48 : 34)));
        g.lineTo(cx + Math.cos(a) * (R - 6), cy + Math.sin(a) * (R - 6)); g.stroke();
        if (big) { g.font = '800 40px Inter'; g.fillStyle = '#2A2420'; g.textAlign = 'center'; g.textBaseline = 'middle';
          g.fillText(String(i), cx + Math.cos(a) * (R - 82), cy + Math.sin(a) * (R - 82)); }
      }
      g.strokeStyle = '#B89A52'; g.lineWidth = 14; g.beginPath(); g.arc(256, 256, 248, 0, Math.PI * 2); g.stroke();
    },
    lines: [{ text: label, x: 256, y: 214, size: 26, color: '#5A4A3A', weight: 800 }],
  });
  const v = Math.round(Math.max(0, Math.min(max, value)) * 4) / 4;
  const txt = `${Number.isInteger(v) ? v : v.toFixed(2).replace(/0$/, '')}%`;
  const read = textTexture(`dialval${txt}`, { w: 320, h: 120, bg: '#1A1714', lines: [{ text: txt, x: 160, y: 62, size: 92, color: v >= 10 ? '#FF5A5A' : '#FFD45A', weight: 800 }] });
  const ang = ((-225 + (270 * Math.max(0, Math.min(max, value))) / max) * Math.PI) / 180;
  return (
    <group scale={s}>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.5, 0.5, 0.06, 48]} />
        <M c="#B89A52" r={0.3} m={0.7} />
      </mesh>
      <mesh position={[0, 0, 0.031]}>
        <circleGeometry args={[0.47, 48]} />
        <meshStandardMaterial map={face ?? undefined} color="#ffffff" roughness={0.6} />
      </mesh>
      <mesh position={[0, -0.3, 0.034]}>
        <planeGeometry args={[0.32, 0.12]} />
        <meshBasicMaterial map={read ?? undefined} toneMapped={false} />
      </mesh>
      {/* needle: pivots at the dial centre (texture centre y 270/512 -> slightly below middle) */}
      <group position={[0, -0.025, 0.045]} rotation={[0, 0, -ang]}>
        <mesh position={[0.17, 0, 0]}>
          <boxGeometry args={[0.36, 0.022, 0.012]} />
          <M c="#C8102E" r={0.4} />
        </mesh>
      </group>
      <mesh position={[0, -0.025, 0.05]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.035, 0.035, 0.02, 20]} />
        <M c="#2A2420" r={0.3} m={0.6} />
      </mesh>
    </group>
  );
};

/** A model terraced house for the tabletop (about 26 cm wide). `squash` 0..1 crushes it into the table;
 *  `sale` adds a tiny FOR SALE board. Animate squash with a non-rounded grow. */
export const House: React.FC<{ s?: number; squash?: number; door?: string; brick?: string; sale?: boolean }> = ({ s = 1, squash = 0, door = '#1F3A5F', brick = '#A85A3C', sale = false }) => {
  const k = Math.max(0, Math.min(1, squash));
  const sign = sale ? textTexture('housesale', { w: 256, h: 128, bg: '#C0272D', lines: [{ text: 'FOR SALE', x: 128, y: 66, size: 50, color: '#FFFFFF', weight: 800 }] }) : null;
  return (
    <group scale={[s * (1 + 0.25 * k), s * (1 - 0.7 * k), s * (1 + 0.15 * k)]}>
      <mesh position={[0, 0.11, 0]}><boxGeometry args={[0.26, 0.22, 0.18]} /><M c={brick} r={0.85} /></mesh>
      <mesh position={[0, 0.27, 0]} rotation={[0, Math.PI / 4, 0]} scale={[1, 1, 1]}>
        <coneGeometry args={[0.19, 0.12, 4]} />
        <M c="#4A4E57" r={0.8} />
      </mesh>
      <mesh position={[-0.06, 0.06, 0.091]}><boxGeometry args={[0.05, 0.09, 0.004]} /><M c={door} r={0.4} /></mesh>
      {[[0.06, 0.07], [-0.06, 0.16], [0.06, 0.16]].map(([x, y], i) => (
        <mesh key={i} position={[x, y, 0.091]}><boxGeometry args={[0.05, 0.045, 0.004]} /><M c="#2D3A4A" e="#FFD9A0" ei={0.5} r={0.2} /></mesh>
      ))}
      {sign ? (
        <group position={[0.17, 0, 0.1]}>
          <mesh position={[0, 0.06, 0]}><boxGeometry args={[0.006, 0.12, 0.006]} /><M c="#EDE6D6" /></mesh>
          <mesh position={[0, 0.12, 0.004]}><planeGeometry args={[0.08, 0.04]} /><meshStandardMaterial map={sign} color="#ffffff" /></mesh>
        </group>
      ) : null}
    </group>
  );
};

/** A full-size estate agent's FOR SALE board on a post (generic: no agent's name). Slam it in with
 *  move: { to, t0, t1, ease: 'drop' }. `sold` swaps the board. */
export const SaleBoard: React.FC<{ s?: number; sold?: boolean; tilt?: number }> = ({ s = 1, sold = false, tilt = 0 }) => {
  const tex = textTexture(`saleboard${sold}`, {
    w: 512, h: 384, bg: sold ? '#1F3A5F' : '#C0272D', border: '#FFFFFF',
    lines: sold ? [{ text: 'SOLD', x: 256, y: 196, size: 150, color: '#FFFFFF', weight: 800 }]
      : [{ text: 'FOR', x: 256, y: 120, size: 110, color: '#FFFFFF', weight: 800 }, { text: 'SALE', x: 256, y: 262, size: 140, color: '#FFFFFF', weight: 800 }],
  });
  return (
    <group scale={s} rotation={[0, 0, tilt]}>
      <mesh position={[0, 0.9, -0.02]}><boxGeometry args={[0.08, 1.8, 0.08]} /><M c="#EDE6D6" r={0.8} /></mesh>
      <mesh position={[0, 1.5, 0.03]}><boxGeometry args={[0.82, 0.62, 0.03]} /><M c={sold ? '#1F3A5F' : '#C0272D'} r={0.6} /></mesh>
      <mesh position={[0, 1.5, 0.046]}><planeGeometry args={[0.8, 0.6]} /><meshStandardMaterial map={tex ?? undefined} color="#ffffff" roughness={0.6} /></mesh>
    </group>
  );
};

/** A supermarket trolley holding n items (0-14). Grow n to fill it. */
export const Trolley: React.FC<{ n?: number; s?: number }> = ({ n = 0, s = 1 }) => {
  const goods = ['#D9483B', '#F2B33D', '#3A7CC2', '#4FA35C', '#E8E2D2', '#8A4FB5', '#F07C2E', '#2E9C9A'];
  const wire = '#B8BEC6';
  const bar = (p: [number, number, number], sz: [number, number, number]) => <mesh position={p}><boxGeometry args={sz} /><M c={wire} r={0.3} m={0.8} /></mesh>;
  return (
    <group scale={s}>
      {/* basket frame */}
      {bar([0, 0.55, 0.28], [0.9, 0.025, 0.025])}{bar([0, 0.55, -0.28], [0.9, 0.025, 0.025])}
      {bar([0, 1.0, 0.3], [0.95, 0.025, 0.025])}{bar([0, 1.0, -0.3], [0.95, 0.025, 0.025])}
      {bar([0.45, 0.78, 0], [0.025, 0.45, 0.6])}{bar([-0.47, 0.78, 0], [0.025, 0.47, 0.62])}
      {Array.from({ length: 7 }).map((_, i) => bar([-0.42 + i * 0.14, 0.78, 0.29], [0.012, 0.45, 0.012]))}
      {Array.from({ length: 7 }).map((_, i) => bar([-0.42 + i * 0.14, 0.78, -0.29], [0.012, 0.45, 0.012]))}
      {bar([0, 0.55, 0], [0.9, 0.012, 0.56])}
      {/* handle and wheels */}
      {bar([-0.6, 1.05, 0], [0.04, 0.04, 0.62])}
      {bar([-0.53, 1.02, 0.29], [0.16, 0.025, 0.025])}{bar([-0.53, 1.02, -0.29], [0.16, 0.025, 0.025])}
      {bar([0, 0.3, 0.22], [0.8, 0.025, 0.025])}{bar([0, 0.3, -0.22], [0.8, 0.025, 0.025])}
      {[[-0.38, 0.22], [0.38, 0.22], [-0.38, -0.22], [0.38, -0.22]].map(([x, z], i) => (
        <group key={i}>
          {bar([x, 0.17, z], [0.02, 0.26, 0.02])}
          <mesh position={[x, 0.05, z]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.05, 0.05, 0.03, 16]} /><M c="#1E1E1E" r={0.7} /></mesh>
        </group>
      ))}
      {/* the shopping */}
      {Array.from({ length: Math.max(0, Math.min(14, Math.round(n))) }).map((_, i) => {
        const col = i % 5, row = Math.floor(i / 5);
        const h = 0.16 + ((i * 37) % 7) * 0.025;
        return (
          <mesh key={i} position={[-0.32 + col * 0.16, 0.58 + h / 2 + row * 0.1, ((i * 53) % 3 - 1) * 0.15]} rotation={[0, (i * 0.7) % 1, 0]}>
            {i % 3 === 0 ? <cylinderGeometry args={[0.055, 0.055, h, 16]} /> : <boxGeometry args={[0.13, h, 0.11]} />}
            <M c={goods[i % goods.length]} r={0.5} />
          </mesh>
        );
      })}
    </group>
  );
};

/** The planted slip (script-rules 12): milk going into an empty mug, the teabag still on the side. Kitchen-table scale. */
export const Tea: React.FC<{ s?: number; pour?: number }> = ({ s = 1, pour = 1 }) => (
  <group scale={s}>
    <mesh position={[0, 0.05, 0]}><cylinderGeometry args={[0.042, 0.038, 0.1, 24, 1, true]} /><meshStandardMaterial color="#F4F1EA" roughness={0.4} side={THREE.DoubleSide} /></mesh>
    <mesh position={[0, 0.002, 0]} rotation={[-Math.PI / 2, 0, 0]}><circleGeometry args={[0.038, 24]} /><M c="#F4F1EA" /></mesh>
    <mesh position={[0, 0.012 + 0.03 * pour, 0]} rotation={[-Math.PI / 2, 0, 0]}><circleGeometry args={[0.039, 24]} /><M c="#FBFAF5" r={0.3} /></mesh>
    <mesh position={[0.05, 0.055, 0]} rotation={[0, 0, Math.PI / 2]}><torusGeometry args={[0.025, 0.007, 8, 16, Math.PI]} /><M c="#F4F1EA" /></mesh>
    {/* the milk bottle, tipped over the empty mug */}
    <group position={[-0.06, 0.2, 0]} rotation={[0, 0, -1.9]}>
      <mesh><cylinderGeometry args={[0.035, 0.035, 0.16, 20]} /><meshStandardMaterial color="#FFFFFF" roughness={0.15} transparent opacity={0.9} /></mesh>
      <mesh position={[0, 0.1, 0]}><cylinderGeometry args={[0.018, 0.03, 0.04, 20]} /><meshStandardMaterial color="#FFFFFF" roughness={0.15} /></mesh>
      <mesh position={[0, 0.125, 0]}><cylinderGeometry args={[0.02, 0.02, 0.012, 20]} /><M c="#1F5FBF" r={0.4} /></mesh>
    </group>
    {pour > 0.05 ? <mesh position={[0.005, 0.1, 0]}><cylinderGeometry args={[0.006, 0.006, 0.12, 8]} /><M c="#FBFAF5" r={0.3} /></mesh> : null}
    {/* the unused teabag on a saucer */}
    <mesh position={[0.12, 0.004, 0.04]}><cylinderGeometry args={[0.04, 0.04, 0.008, 24]} /><M c="#E9E4DA" /></mesh>
    <mesh position={[0.12, 0.012, 0.04]}><boxGeometry args={[0.035, 0.008, 0.035]} /><M c="#C9A97A" r={0.9} /></mesh>
  </group>
);

/** A phone lying face up with a notification (for the share ask). */
export const Phone: React.FC<{ s?: number; text?: string }> = ({ s = 1, text = 'NEW VIDEO' }) => {
  const tex = textTexture(`phone${text}`, { w: 256, h: 512, bg: '#101418',
    draw: (g) => { g.fillStyle = '#2A3442'; g.beginPath(); g.roundRect(18, 150, 220, 110, 18); g.fill(); },
    lines: [{ text: '18:42', x: 128, y: 80, size: 50, color: '#FFFFFF', weight: 700 }, { text, x: 128, y: 205, size: 30, color: '#FFD43B', weight: 800 }] });
  return (
    <group scale={s}>
      <mesh position={[0, 0.004, 0]}><boxGeometry args={[0.075, 0.008, 0.15]} /><M c="#1A1A1A" r={0.3} m={0.4} /></mesh>
      <mesh position={[0, 0.0085, 0]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[0.068, 0.14]} /><meshBasicMaterial map={tex ?? undefined} toneMapped={false} /></mesh>
    </group>
  );
};

// ---------- Ep 05 (7 Nov 2026): gas storage ----------
/** A glass jar of glowing blue gas, 1 unit tall at s = 1 (base on y 0). fill 0..1; glow scales the light; dim fades it. */
export const GasJar: React.FC<{ s?: number; fill?: number; glow?: number; dim?: number }> = ({ s = 1, fill = 1, glow = 1, dim = 1 }) => {
  const f = Math.max(0, Math.min(1, fill));
  const H = 0.86;
  return (
    <group scale={s}>
      {f > 0.01 ? (
        <mesh position={[0, 0.04 + (H * f) / 2, 0]}>
          <cylinderGeometry args={[0.27, 0.27, H * f, 20]} />
          <meshStandardMaterial color="#9ED6FF" emissive="#3FA2FF" emissiveIntensity={1.6 * glow * dim} roughness={0.3} toneMapped={false} />
        </mesh>
      ) : null}
      <mesh position={[0, 0.47, 0]}>
        <cylinderGeometry args={[0.3, 0.3, 0.92, 20, 1, true]} />
        <meshStandardMaterial color={f > 0.01 ? '#CFEAFF' : '#5B6670'} transparent opacity={f > 0.01 ? 0.28 : 0.55} roughness={0.1} side={THREE.DoubleSide} />
      </mesh>
      <mesh position={[0, 0.01, 0]}><cylinderGeometry args={[0.3, 0.3, 0.02, 20]} /><M c="#7C8790" r={0.4} /></mesh>
      <mesh position={[0, 0.96, 0]}><cylinderGeometry args={[0.24, 0.26, 0.1, 20]} /><M c="#C9CED3" r={0.3} m={0.7} /></mesh>
    </group>
  );
};

/** A plank shelf of n gas jars with a sign at its start. dir 'x' runs left to right; 'z' runs away into the distance.
 *  lit: jars 0..lit glow (fractional half-fills one). drop: the last dropN jars fall through the floor (0..1). */
export const JarShelf: React.FC<{ n?: number; lit?: number; label?: string; sub?: string; s?: number; dir?: 'x' | 'z'; drop?: number; dropN?: number; gap?: number; signS?: number }> = ({
  n = 12, lit, label, sub, s = 1, dir, drop = 0, dropN = 6, gap = 0.42, signS = 1,
}) => {
  const L = lit ?? n;
  const d = dir ?? (n > 20 ? 'z' : 'x');
  const len = n * gap;
  const sign = label ? textTexture(`shelfsign${label}${sub ?? ''}`, { w: 512, h: 288, bg: '#1E2A36', border: '#FFD43B',
    lines: [{ text: label, x: 256, y: sub ? 100 : 144, size: label.length > 5 ? 84 : 120, color: '#FFFFFF', weight: 800 }, ...(sub ? [{ text: sub, x: 256, y: 218, size: 76, color: '#FFD43B', weight: 800 }] : [])] }) : null;
  const pos = (i: number): [number, number, number] => (d === 'x' ? [-len / 2 + gap / 2 + i * gap, 0, 0] : [0, 0, -i * gap]);
  return (
    <group scale={s}>
      <mesh position={d === 'x' ? [0, -0.04, 0] : [0, -0.04, -len / 2 + gap / 2]}>
        <boxGeometry args={d === 'x' ? [len + 0.1, 0.08, 0.5] : [0.5, 0.08, len + 0.1]} />
        <M c="#8A5E3C" r={0.7} />
      </mesh>
      {Array.from({ length: n }).map((_, i) => {
        const falling = i >= n - dropN ? Math.max(0, Math.min(1, drop * 1.6 - (n - 1 - i) * 0.1)) : 0;
        const p = pos(i);
        if (falling >= 0.999) return null;
        return (
          <group key={i} position={[p[0], p[1] - falling * falling * 2.2, p[2]]} scale={(1 - falling * 0.5) * 0.45}>
            <GasJar fill={Math.max(0, Math.min(1, L - i))} />
          </group>
        );
      })}
      {sign ? (
        <group position={d === 'x' ? [-len / 2 - 0.55, 0, 0.1] : [0.6, 0, 0.45]} rotation={[0, d === 'x' ? 0.15 : -0.35, 0]} scale={signS}>
          <mesh position={[0, 0.24, -0.02]}><boxGeometry args={[0.04, 0.48, 0.04]} /><M c="#2B2F36" /></mesh>
          <mesh position={[0, 0.72, 0]}><planeGeometry args={[0.8, 0.45]} /><meshBasicMaterial map={sign} toneMapped={false} /></mesh>
        </group>
      ) : null}
    </group>
  );
};

/** A tear-off day calendar standing on a table (about 18 cm tall): DAY on top, the number big. */
export const Calendar: React.FC<{ day?: string; s?: number }> = ({ day = '1', s = 1 }) => {
  const tex = textTexture(`cal${day}`, { w: 320, h: 400, bg: '#FBF8F0',
    draw: (g) => { g.fillStyle = '#C8102E'; g.fillRect(0, 0, 320, 110); g.fillStyle = '#1E1E1E'; for (let i = 0; i < 6; i++) { g.beginPath(); g.arc(40 + i * 48, 14, 7, 0, 7); g.fill(); } },
    lines: [{ text: 'DAY', x: 160, y: 66, size: 64, color: '#FFFFFF', weight: 800 }, { text: day, x: 160, y: 265, size: 220, color: '#1E1E1E', weight: 800 }] });
  return (
    <group scale={s} rotation={[-0.12, 0, 0]}>
      <mesh position={[0, 0.09, -0.012]}><boxGeometry args={[0.15, 0.19, 0.02]} /><M c="#E9E4DA" /></mesh>
      <mesh position={[0, 0.09, 0.0]}><planeGeometry args={[0.14, 0.175]} /><meshStandardMaterial map={tex ?? undefined} color="#ffffff" roughness={0.8} /></mesh>
    </group>
  );
};

/** The planted slip (Ep 05): scones done jam first, cream on top (the Cornish way), on a tea towel that says DEVON. Table scale. */
export const Scones: React.FC<{ s?: number }> = ({ s = 1 }) => {
  const towel = textTexture('toweldevon', { w: 512, h: 384, bg: '#F4F1EA',
    draw: (g) => { g.fillStyle = '#2E6B4F'; g.fillRect(0, 30, 512, 22); g.fillRect(0, 332, 512, 22); g.fillStyle = '#C8102E'; g.fillRect(0, 62, 512, 8); g.fillRect(0, 314, 512, 8); },
    lines: [{ text: 'DEVON', x: 256, y: 196, size: 120, color: '#2E6B4F', weight: 800 }] });
  return (
    <group scale={s}>
      <mesh position={[0.02, 0.002, 0.06]} rotation={[-Math.PI / 2, 0, 0.15]}><planeGeometry args={[0.36, 0.27]} /><meshStandardMaterial map={towel ?? undefined} color="#ffffff" roughness={0.95} /></mesh>
      <mesh position={[-0.02, 0.008, -0.04]}><cylinderGeometry args={[0.11, 0.1, 0.012, 28]} /><M c="#F7F5F0" r={0.3} /></mesh>
      {[[-0.07, -0.05], [0.04, -0.02]].map(([x, z], i) => (
        <group key={i} position={[x, 0.014, z]}>
          <mesh position={[0, 0.016, 0]}><cylinderGeometry args={[0.04, 0.042, 0.032, 20]} /><M c="#D9A866" r={0.9} /></mesh>
          <mesh position={[0, 0.034, 0]}><cylinderGeometry args={[0.038, 0.038, 0.006, 20]} /><M c="#B0142B" r={0.35} /></mesh>
          <mesh position={[0, 0.045, 0]} scale={[1, 0.7, 1]}><sphereGeometry args={[0.03, 16, 10]} /><M c="#FFF8E6" r={0.6} /></mesh>
        </group>
      ))}
      {/* the jam jar and the cream pot, so the order reads */}
      <mesh position={[0.13, 0.03, -0.08]}><cylinderGeometry args={[0.025, 0.025, 0.06, 16]} /><meshStandardMaterial color="#8E0F22" roughness={0.2} transparent opacity={0.9} /></mesh>
      <mesh position={[0.13, 0.065, -0.08]}><cylinderGeometry args={[0.027, 0.027, 0.012, 16]} /><M c="#E9E4DA" /></mesh>
    </group>
  );
};

/** A knitted jumper (Nan's line): green with a red band, sleeves out. About 50 cm wide. */
export const Jumper: React.FC<{ s?: number }> = ({ s = 1 }) => (
  <group scale={s}>
    <mesh><boxGeometry args={[0.44, 0.42, 0.1]} /><M c="#2E6B4F" r={0.95} /></mesh>
    <mesh position={[0, -0.12, 0.052]}><boxGeometry args={[0.44, 0.06, 0.004]} /><M c="#C8102E" r={0.95} /></mesh>
    <mesh position={[0, 0.2, 0.052]}><boxGeometry args={[0.16, 0.04, 0.004]} /><M c="#EFE8DA" r={0.95} /></mesh>
    {[-1, 1].map((sd) => <mesh key={sd} position={[sd * 0.3, 0.06, 0]} rotation={[0, 0, sd * 0.9]}><boxGeometry args={[0.36, 0.11, 0.09]} /><M c="#2E6B4F" r={0.95} /></mesh>)}
  </group>
);

export const PROPS = { Jumper, Coin, CoinStack, Note, PriceTag, Newspaper, ChartScreen, Meter, Barrel, Dial, House, SaleBoard, Trolley, Tea, Phone, GasJar, JarShelf, Calendar, Scones };
