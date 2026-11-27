// Acting test (10 Nov 2026): the locked cast on a dark "glow" stage, whole-body acting, thoughts as on-screen POV text.
// Everything is a pure function of the frame. Timings live in BEATS so the sound script reads the same numbers.
import React from 'react';
import * as THREE from 'three';
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import { ThreeCanvas } from '@remotion/three';
import { Person, FACES, BODY, mixFace, Body, Face } from '../cast/Person';
import { CAST } from '../cast/cast';
import { BEATS as B, THOUGHTS, LEN } from './actingBeats';

export type V3 = [number, number, number];
export type Ease = 'io' | 'out' | 'in' | 'back' | 'lin';
export const EASE: Record<Ease, (t: number) => number> = {
  io: (t) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2),
  out: (t) => 1 - Math.pow(1 - t, 3),
  in: (t) => t * t * t,
  back: (t) => { const c1 = 1.8, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  lin: (t) => t,
};
export const clamp = (v: number, a = 0, b = 1) => Math.max(a, Math.min(b, v));
export const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
export const prog = (t: number, a: number, b: number, e: Ease = 'io') => EASE[e](clamp((t - a) / (b - a)));

// ---------- poses ----------
export type Pose = Partial<Body> & { x?: number; face?: string; turnY?: number };
export type Key = [number, Pose, Ease?];
const NUMS = ['lean', 'turn', 'headTurn', 'headTilt', 'headNod', 'elL', 'elR', 'knL', 'knR', 'bounce', 'spine', 'side', 'crouch', 'shrug', 'sway', 'x', 'turnY', 'twL', 'twR'] as const;
const PAIRS = ['shL', 'shR', 'hipL', 'hipR'] as const;
const BASE: Pose = { ...BODY, spine: 0, side: 0, crouch: 0, shrug: 0, sway: 0, bounce: 0, twL: 0, twR: 0 };

export function poseAt(keys: Key[], t: number) {
  let i = 0; while (i < keys.length - 1 && keys[i + 1][0] <= t) i++;
  const a = keys[i], b = keys[Math.min(i + 1, keys.length - 1)];
  const pa = { ...BASE, ...a[1] } as Record<string, any>, pb = { ...BASE, ...a[1], ...b[1] } as Record<string, any>;
  const k = b[0] === a[0] ? 1 : EASE[b[2] ?? 'io'](clamp((t - a[0]) / (b[0] - a[0])));
  const out: Record<string, any> = {};
  for (const n of NUMS) out[n] = lerp(pa[n] ?? 0, pb[n] ?? 0, k);
  for (const n of PAIRS) out[n] = [lerp(pa[n][0], pb[n][0], k), lerp(pa[n][1], pb[n][1], k)];
  out.handL = k < 0.5 ? pa.handL : pb.handL; out.handR = k < 0.5 ? pa.handR : pb.handR;
  const fa = FACES[pa.face ?? 'neutral'], fb = FACES[pb.face ?? pa.face ?? 'neutral'];
  out.faceMix = mixFace(fa, fb, clamp(k * 1.6)); // the face leads the body slightly
  // walking: legs swing while x moves
  const dx = (pb.x ?? 0) - (pa.x ?? 0);
  if (Math.abs(dx) > 0.05) {
    const steps = Math.max(1, Math.round(Math.abs(dx) / 0.32));
    const ph = Math.sin(k * steps * Math.PI);
    out.hipL = [out.hipL[0] + 22 * ph, out.hipL[1]]; out.hipR = [out.hipR[0] - 22 * ph, out.hipR[1]];
    out.knL += 18 * Math.max(0, ph); out.knR += 18 * Math.max(0, -ph);
    out.bounce += -0.012 * Math.abs(ph);
  }
  return out as Body & { x: number; turnY: number; faceMix: Face };
}
// breathing on top of any pose: chest rises, shoulders lift a touch
export const breathe = (p: any, t: number, rate = 3.4, amp = 1) => {
  const s = Math.sin((t * 2 * Math.PI) / rate);
  return { ...p, spine: p.spine - 1.2 * s * amp, shrug: p.shrug + 0.12 * s * amp, headNod: p.headNod - 0.8 * s * amp };
};
export const blink = (f: Face, t: number, seed: number) => {
  const c = (t + seed) % 3.7; const k = c < 0.12 ? Math.sin((c / 0.12) * Math.PI) : 0;
  return { ...f, lid: Math.max(f.lid, k) };
};

// Arm shapes used below (shoulder [forward, out], elbow bend)
export const HANG = { shL: [0, 6] as [number, number], elL: 8, shR: [0, 6] as [number, number], elR: 8, twL: 0, twR: 0 };
export const HANDS_FRONT = { shL: [28, -18] as [number, number], elL: 78, shR: [28, -18] as [number, number], elR: 78, handL: 'fist' as const, handR: 'open' as const };
export const ON_HEAD = { shL: [120, 22] as [number, number], elL: 115, twL: 40, shR: [120, 22] as [number, number], elR: 115, twR: 40 };
export const OVER_MOUTH = { shL: [95, 28] as [number, number], elL: 120, twL: 55, shR: [95, 28] as [number, number], elR: 120, twR: 55, handL: 'open' as const, handR: 'open' as const };
export const PALMS_UP = { shL: [22, 30] as [number, number], elL: 75, shR: [22, 30] as [number, number], elR: 75, twL: 0, twR: 0 };
export const CROSSED = { shL: [30, -6] as [number, number], elL: 100, twL: 70, shR: [36, -6] as [number, number], elR: 95, twR: 70, handL: 'fist' as const, handR: 'fist' as const };
export const CHIN = { shR: [40, -10] as [number, number], elR: 128, twR: 35, handR: 'fist' as const };
export const OPEN_ARMS = { shL: [18, 40] as [number, number], elL: 22, shR: [18, 40] as [number, number], elR: 22, twL: 0, twR: 0 };

const NAN_X = -1.45, ALF_X = 0.25, MATE_X = 1.75;
const NAN: Key[] = [
  [0, { x: NAN_X, ...HANDS_FRONT, face: 'neutral', headTurn: 18, turnY: 0.25 }],
  [B.nanFill0, { x: NAN_X, ...HANDS_FRONT, face: 'neutral', headTurn: 30, headNod: 4, turnY: 0.25 }],
  [B.nanLand, { x: NAN_X, ...HANDS_FRONT, face: 'smug', headTurn: 6, headNod: -12, headTilt: 6, spine: -5, shrug: 0.35, turnY: 0.15 }, 'back'],
  [B.nanLand + 0.6, { x: NAN_X, ...HANDS_FRONT, face: 'smug', headTurn: 4, headNod: -10, headTilt: -5, spine: -4, shrug: 0.2, bounce: 0.012, turnY: 0.15 }],
  [B.nanLand + 1.2, { x: NAN_X, ...HANDS_FRONT, face: 'smug', headTurn: 4, headNod: -10, headTilt: 5, spine: -4, shrug: 0.2, bounce: 0, turnY: 0.15 }],
  [B.mateIn, { x: NAN_X, ...HANDS_FRONT, face: 'smug', headTurn: 4, headNod: -8, spine: -3, turnY: 0.15 }],
];
const ALF: Key[] = [
  [0, { x: ALF_X, ...HANG, face: 'neutral', turnY: 0.2 }],
  [B.glide1, { x: ALF_X, ...HANG, face: 'neutral', turnY: 0.2, headTurn: 25 }],
  [B.alfFill0, { x: ALF_X, ...HANG, face: 'thinking', turnY: 0.3, headTurn: 35, spine: 4 }],
  [B.alfPass, { x: ALF_X + 0.05, ...HANG, ...CHIN, face: 'worried', turnY: 0.35, headTurn: 38, spine: 12, headNod: 4, sway: 0.03 }],
  [B.alfLand - 0.1, { x: ALF_X + 0.08, ...HANG, ...CHIN, face: 'worried', turnY: 0.4, headTurn: 40, spine: 16, headNod: 6, sway: 0.03 }],
  // the number lands: freeze, then recoil
  [B.alfLand + 0.25, { x: ALF_X + 0.08, ...HANG, ...CHIN, face: 'shock', turnY: 0.4, headTurn: 40, spine: 16, headNod: 6, sway: 0.03 }],
  [B.alfLand + 0.65, { x: ALF_X - 0.3, ...ON_HEAD, face: 'shock', turnY: 0.15, headTurn: 18, spine: -12, headNod: -8, crouch: 0.1, shrug: 0.6 }, 'back'],
  [B.alfLand + 1.6, { x: ALF_X - 0.3, ...ON_HEAD, face: 'disbelief', turnY: 0.15, headTurn: 14, spine: -9, headNod: -4, crouch: 0.06, shrug: 0.5 }],
  // the sigh: chest fills ... and everything drops
  [B.sigh, { x: ALF_X - 0.3, ...PALMS_UP, face: 'worried', turnY: 0.05, headTurn: 0, spine: -6, headNod: -10, shrug: 0.7 }],
  [B.sigh + 0.6, { x: ALF_X - 0.3, ...PALMS_UP, face: 'worried', turnY: 0.05, spine: -7, headNod: -12, shrug: 0.8 }],
  [B.slump, { x: ALF_X - 0.3, ...HANG, shL: [8, -4], shR: [8, -4], elL: 14, elR: 14, face: 'sad', turnY: 0, spine: 24, headNod: 22, crouch: 0.16, shrug: -1, sway: -0.02 }, 'in'],
  [B.slump + 1.2, { x: ALF_X - 0.3, ...HANG, shL: [8, -4], shR: [8, -4], elL: 14, elR: 14, face: 'sad', turnY: 0, spine: 26, headNod: 24, crouch: 0.18, shrug: -1, sway: -0.02 }],
  [B.mateIn + 1.2, { x: ALF_X - 0.3, ...HANG, shL: [8, -4], shR: [8, -4], elL: 14, elR: 14, face: 'sad', turnY: 0.1, headTurn: 30, spine: 24, headNod: 18, crouch: 0.16, shrug: -1 }],
  [B.switch - 0.05, { x: ALF_X - 0.3, ...HANG, shL: [8, -4], shR: [8, -4], elL: 14, elR: 14, face: 'sad', turnY: 0, headTurn: 0, spine: 25, headNod: 22, crouch: 0.17, shrug: -1 }],
  // hope: head lifts first, then the chest opens, a dip, a step forward
  [B.hope, { x: ALF_X - 0.3, ...HANG, shL: [8, -4], shR: [8, -4], elL: 14, elR: 14, face: 'thinking', spine: 16, headNod: -6, crouch: 0.14, shrug: -0.6 }, 'out'],
  [B.hope + 0.5, { x: ALF_X - 0.3, ...HANG, face: 'disbelief', spine: -4, headNod: -8, crouch: 0.04, shrug: 0.3 }, 'out'],
  [B.hope + 0.85, { x: ALF_X - 0.28, ...HANG, elL: 30, elR: 30, face: 'happy', spine: 6, headNod: 0, crouch: 0.3, shrug: 0 }],
  [B.hope + 1.45, { x: ALF_X + 0.05, ...OPEN_ARMS, face: 'happy', spine: -6, headNod: -6, crouch: 0, shrug: 0.4, bounce: 0.03 }, 'back'],
  [B.hope + 2.1, { x: ALF_X + 0.05, ...OPEN_ARMS, shL: [14, 32], shR: [14, 32], face: 'laugh', spine: -3, headNod: -4, shrug: 0.25, bounce: 0 }],
  [LEN, { x: ALF_X + 0.05, ...OPEN_ARMS, shL: [12, 30], shR: [12, 30], face: 'happy', spine: -2, headNod: -3, shrug: 0.2 }],
];
const MATE: Key[] = [
  [0, { x: MATE_X + 1.4, ...CROSSED, face: 'neutral', turnY: -0.35 }],
  [B.mateIn, { x: MATE_X + 1.4, ...CROSSED, face: 'neutral', turnY: -0.35 }],
  [B.mateIn + 0.9, { x: MATE_X, ...HANG, face: 'neutral', turnY: -0.45 }],
  [B.mateIn + 1.4, { x: MATE_X, ...CROSSED, face: 'smug', turnY: -0.4, headTilt: 12, sway: 0.06, side: -5, headTurn: -15 }, 'back'],
  [B.switch, { x: MATE_X, ...CROSSED, face: 'smug', turnY: -0.4, headTilt: 9, sway: 0.06, side: -4, headTurn: -15 }],
  [B.hope + 0.9, { x: MATE_X, ...CROSSED, face: 'disbelief', turnY: -0.45, headTilt: -2, sway: 0.03, side: 0, headTurn: -25 }],
  [B.hope + 1.4, { x: MATE_X + 0.08, ...OVER_MOUTH, face: 'shock', turnY: -0.45, headTilt: 0, sway: 0, side: 0, spine: -8, headTurn: -22, shrug: 0.5 }, 'back'],
  [LEN, { x: MATE_X + 0.08, ...OVER_MOUTH, face: 'shock', turnY: -0.45, spine: -6, headTurn: -22, shrug: 0.4 }],
];

// ---------- camera ----------
export type Cam = { p: V3; t: V3; fov: number };
const CAMS: [number, Cam, Ease?][] = [
  [0, { p: [NAN_X + 0.4, 1.35, 5.0], t: [NAN_X + 0.4, 1.22, 0], fov: 38 }],
  [B.glide1, { p: [NAN_X + 0.5, 1.35, 4.9], t: [NAN_X + 0.5, 1.22, 0], fov: 38 }],
  [B.glide1 + 1.2, { p: [ALF_X + 0.5, 1.35, 5.4], t: [ALF_X + 0.5, 1.22, 0], fov: 38 }],
  [B.alfLand, { p: [ALF_X + 0.45, 1.33, 5.0], t: [ALF_X + 0.45, 1.2, 0], fov: 38 }],
  [B.slump + 1.0, { p: [ALF_X + 0.25, 1.3, 4.6], t: [ALF_X + 0.2, 1.18, 0], fov: 38 }],
  [B.mateIn + 0.5, { p: [ALF_X + 0.62, 1.4, 7.4], t: [ALF_X + 0.62, 1.25, 0], fov: 38 }],
  [B.switch, { p: [ALF_X + 0.62, 1.4, 7.3], t: [ALF_X + 0.62, 1.25, 0], fov: 38 }],
  [LEN, { p: [ALF_X + 0.62, 1.36, 6.4], t: [ALF_X + 0.62, 1.22, 0], fov: 38 }],
];
function camAt(t: number): Cam {
  let i = 0; while (i < CAMS.length - 1 && CAMS[i + 1][0] <= t) i++;
  const a = CAMS[i], b = CAMS[Math.min(i + 1, CAMS.length - 1)];
  const k = b[0] === a[0] ? 1 : EASE[b[2] ?? 'io'](clamp((t - a[0]) / (b[0] - a[0])));
  const L = (u: V3, v: V3) => u.map((x, j) => lerp(x, v[j], k)) as V3;
  return { p: L(a[1].p, b[1].p), t: L(a[1].t, b[1].t), fov: lerp(a[1].fov, b[1].fov, k) };
}
export const project = (cam: Cam, w: V3, W: number, H: number) => {
  const c = new THREE.PerspectiveCamera(cam.fov, W / H, 0.01, 100);
  c.position.set(...cam.p); c.lookAt(...cam.t); c.updateMatrixWorld(); c.updateProjectionMatrix();
  const v = new THREE.Vector3(...w).project(c);
  return [(v.x * 0.5 + 0.5) * W, (-v.y * 0.5 + 0.5) * H];
};

// ---------- set pieces ----------
export const Dots: React.FC<{ x0: number; value: number; total: number; glow: string; dimBelow?: number }> = ({ x0, value, total, glow, dimBelow = 0 }) => {
  const n = Math.round(value * 10);
  return (
    <group>
      {Array.from({ length: Math.ceil(total) * 10 }).map((_, i) => {
        const col = Math.floor(i / 10), row = i % 10;
        if (col * 10 + row >= Math.round(total * 10)) return null;
        const on = i < n;
        const old = i < dimBelow * 10;
        return (
          <mesh key={i} position={[x0 + col * 0.1, 0.06 + row * 0.072, -0.35]}>
            <sphereGeometry args={[on ? 0.022 : 0.009, 12, 8]} />
            <meshBasicMaterial color={on ? (old ? '#9a9a9a' : glow) : '#3a3a40'} toneMapped={false} />
          </mesh>
        );
      })}
    </group>
  );
};
export const DashLine: React.FC<{ from: V3; to: V3; color?: string; seg?: number }> = ({ from, to, color = '#8d8d95', seg = 0.06 }) => {
  const d = new THREE.Vector3(...to).sub(new THREE.Vector3(...from)); const L = d.length(); const n = Math.floor(L / (seg * 2));
  const dir = d.clone().normalize();
  const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
  return (
    <group>
      {Array.from({ length: n }).map((_, i) => {
        const c = new THREE.Vector3(...from).addScaledVector(dir, (i * 2 + 0.5) * seg);
        return (
          <mesh key={i} position={c} quaternion={q}>
            <cylinderGeometry args={[0.004, 0.004, seg, 6]} />
            <meshBasicMaterial color={color} toneMapped={false} />
          </mesh>
        );
      })}
    </group>
  );
};
export const Spot: React.FC<{ x: number; on: number; tint: string }> = ({ x, on, tint }) => (
  <group>
    <mesh position={[x, 1.6, -0.1]}>
      <coneGeometry args={[0.75, 3.4, 40, 1, true]} />
      <meshBasicMaterial color={tint} transparent opacity={0.05 * on} depthWrite={false} side={THREE.DoubleSide} toneMapped={false} />
    </mesh>
    <mesh position={[x, 0.002, 0.1]} rotation={[-Math.PI / 2, 0, 0]} scale={[1, 0.55, 1]}>
      <circleGeometry args={[0.8, 48]} />
      <meshBasicMaterial color={tint} transparent opacity={0.12 * on} depthWrite={false} toneMapped={false} />
    </mesh>
    <spotLight position={[x, 3.6, 1.2]} target-position={[x, 0.9, 0]} angle={0.42} penumbra={0.7} intensity={on * 22} distance={8} decay={1.6} color={tint} />
  </group>
);

// ---------- 2D overlays ----------
export const Thought: React.FC<{ text: string; t: number; t0: number; t1: number; at: [number, number]; side: 1 | -1 }> = ({ text, t, t0, t1, at, side }) => {
  if (t < t0 - 0.05 || t > t1 + 0.4) return null;
  const words = text.split(' ');
  const shown = Math.min(words.length, Math.floor((t - t0) / 0.13) + 1);
  const fade = 1 - clamp((t - t1) / 0.35);
  const rise = (1 - prog(t, t0, t0 + 0.3, 'out')) * 14;
  const [hx, hy] = at;
  const tx = hx + side * 60, ty = hy - 175 - rise;
  return (
    <div style={{ position: 'absolute', left: 0, top: 0, width: '100%', height: '100%', opacity: fade }}>
      {/* the thinking trail: three dots rising from the head */}
      {[0, 1, 2].map((i) => (
        <div key={i} style={{ position: 'absolute', left: hx + side * (18 + i * 18) - 5, top: hy - 70 - i * 26 - rise, width: 6 + i * 3, height: 6 + i * 3, borderRadius: 99,
          background: 'rgba(255,255,255,.85)', boxShadow: '0 0 12px rgba(255,255,255,.6)', opacity: clamp((t - t0 + 0.1 - i * 0.07) / 0.12) }} />
      ))}
      <div style={{ position: 'absolute', left: side > 0 ? tx : undefined, right: side < 0 ? 1080 - tx : undefined, top: ty, maxWidth: 430,
        textAlign: side > 0 ? 'left' : 'right', fontFamily: 'Inter', fontWeight: 600, fontStyle: 'italic', fontSize: 46, lineHeight: 1.18,
        color: '#fff', textShadow: '0 0 18px rgba(255,255,255,.35), 0 3px 10px rgba(0,0,0,.9)', letterSpacing: -0.3 }}>
        {words.map((w, i) => (
          <span key={i} style={{ opacity: i < shown ? 1 : 0, color: w.startsWith('*') ? '#FFD400' : '#fff' }}>{w.replace(/\*/g, '')}{' '}</span>
        ))}
      </div>
    </div>
  );
};
export const Label: React.FC<{ text: string; x: number; y: number; o: number; size?: number }> = ({ text, x, y, o, size = 26 }) => (
  <div style={{ position: 'absolute', left: x - 300, top: y, width: 600, textAlign: 'center', opacity: o, fontFamily: 'Inter', fontWeight: 600,
    fontSize: size, letterSpacing: 7, color: 'rgba(255,255,255,.72)' }}>{text}</div>
);

export const ActingTest: React.FC = () => {
  const f = useCurrentFrame(); const { fps, width: W, height: H } = useVideoConfig();
  const t = f / fps;
  const cam = camAt(t);
  const sw = prog(t, B.switch, B.switch + 0.45, 'out'); // timeline switch
  const glow = sw > 0 ? `rgb(${lerp(255, 140, sw) | 0},${lerp(255, 236, sw) | 0},${lerp(255, 226, sw) | 0})` : '#ffffff';

  const nanVal = 3.6 * prog(t, B.nanFill0, B.nanLand);
  const alfVal = 7.6 * prog(t, B.alfFill0, B.alfLand, 'lin');
  const nan = breathe(poseAt(NAN, t), t, 3.8, 0.8), alf = breathe(poseAt(ALF, t), t, t > B.slump && t < B.switch ? 4.6 : 3.2), mate = breathe(poseAt(MATE, t), t, 3.6);
  const head = (p: any, h: number): V3 => [p.x + (p.sway ?? 0), h, 0];
  const [nhx, nhy] = project(cam, head(nan, 1.72), W, H);
  const [ahx, ahy] = project(cam, head(alf, 1.92 - (alf.crouch ?? 0) * 0.16 - Math.max(0, alf.spine) * 0.004), W, H);
  const [mhx, mhy] = project(cam, head(mate, 1.98), W, H);
  const [ncx, ncy] = project(cam, [NAN_X + 0.53, -0.05, -0.35], W, H);
  const [acx, acy] = project(cam, [ALF_X + 0.75, -0.05, -0.35], W, H);
  const [mkx, mky] = project(cam, [ALF_X + 0.4 + 3.6 * 0.1 - 0.05, 0.86, -0.35], W, H);

  const bigVal = t < B.glide1 + 0.6 ? nanVal : alfVal;
  const bigLanded = (t >= B.nanLand && t < B.glide1 + 0.6) || t >= B.alfLand;
  const bigSub = t < B.glide1 + 0.6 ? "NAN'S HOUSE · 1997" : 'YOUR HOUSE · TODAY';
  const pop = bigLanded ? 1 + 0.12 * Math.max(0, 1 - ((t >= B.alfLand ? t - B.alfLand : t - B.nanLand) / 0.35)) : 1;
  const counterO = clamp((t - 0.4) / 0.4) * (t < B.glide1 + 0.3 ? 1 : t < B.glide1 + 0.6 ? 0 : clamp((t - B.alfFill0 + 0.3) / 0.3)) * (1 - prog(t, B.switch - 0.3, B.switch)) * (t > B.alfLand + 1.0 ? 1 - prog(t, B.alfLand + 1.0, B.alfLand + 1.5) : 1);

  return (
    <AbsoluteFill style={{ background: '#060609' }}>
      <ThreeCanvas width={W} height={H} camera={{ position: cam.p, fov: cam.fov, near: 0.05, far: 60 }}
        onCreated={({ camera }) => camera.lookAt(...cam.t)}>
        <CamSync cam={cam} />
        <color attach="background" args={[sw > 0 ? `rgb(${lerp(6, 16, sw) | 0},${lerp(6, 10, sw) | 0},${lerp(9, 28, sw) | 0})` : '#060609']} />
        <fog attach="fog" args={['#060609', 5, 11]} />
        <ambientLight intensity={0.28} />
        <hemisphereLight args={['#dfe6ff', '#101014', 0.35]} />
        <directionalLight position={[0.5, 2.5, 4]} intensity={0.9} />
        {/* floor and the dashed ground line */}
        <mesh rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[30, 20]} /><meshStandardMaterial color="#0d0d11" roughness={1} /></mesh>
        <DashLine from={[-4, 0.003, -0.35]} to={[5, 0.003, -0.35]} />
        <Spot x={NAN_X} on={1 - 0.6 * prog(t, B.glide1, B.glide1 + 1)} tint="#ffffff" />
        <Spot x={ALF_X - 0.1} on={prog(t, B.glide1 - 0.2, B.glide1 + 0.8)} tint={sw > 0 ? glow : '#ffffff'} />
        <Spot x={MATE_X} on={prog(t, B.mateIn + 0.3, B.mateIn + 1)} tint="#ffffff" />
        <Dots x0={NAN_X + 0.4} value={nanVal} total={3.6} glow="#ffffff" />
        <Dots x0={ALF_X + 0.4} value={alfVal} total={7.6} glow={glow} dimBelow={3.6} />
        {alfVal > 3.45 ? <DashLine from={[ALF_X + 0.4 + 3.55 * 0.1, 0.0, -0.33]} to={[ALF_X + 0.4 + 3.55 * 0.1, 0.82, -0.33]} color="#cfcfd6" seg={0.035} /> : null}
        <Person look={CAST.nan} face={blink(nan.faceMix, t, 1.1)} body={nan} position={[nan.x, 0, 0]} rotationY={nan.turnY} />
        <Person look={CAST.lead} face={blink(alf.faceMix, t, 0.3)} body={alf} position={[alf.x, 0, 0]} rotationY={alf.turnY} pinGlow={sw > 0 ? 0.6 + 0.4 * Math.sin((t - B.switch) * 6) : 0} />
        <Person look={CAST.mate} face={blink(mate.faceMix, t, 2.2)} body={mate} position={[mate.x, 0, 0]} rotationY={mate.turnY} />
      </ThreeCanvas>

      {/* numbers and labels */}
      <div style={{ position: 'absolute', top: 150, width: '100%', textAlign: 'center', opacity: counterO }}>
        <div style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: 28, letterSpacing: 9, color: 'rgba(255,255,255,.75)' }}>{bigSub}</div>
        <div style={{ fontFamily: 'Inter', fontWeight: 800, fontSize: 150, lineHeight: 1.08, transform: `scale(${pop})`,
          color: bigLanded ? '#FFD400' : '#fff', textShadow: bigLanded ? '0 0 40px rgba(255,212,0,.7)' : '0 0 30px rgba(255,255,255,.5)' }}>{bigVal.toFixed(1)}</div>
        <div style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: 26, letterSpacing: 8, color: 'rgba(255,255,255,.6)' }}>YEARS OF PAY</div>
      </div>
      <Label text="YEARS OF PAY FOR ONE HOUSE" x={ncx} y={ncy + 10} o={clamp((t - 0.6) / 0.4) * (1 - prog(t, B.glide1, B.glide1 + 0.6))} size={22} />
      <Label text="YEARS OF PAY FOR ONE HOUSE" x={acx} y={acy + 10} o={prog(t, B.alfFill0 - 0.4, B.alfFill0) * (1 - prog(t, B.mateIn, B.mateIn + 0.4))} size={22} />
      <Label text="NAN · 3.6" x={mkx} y={mky - 44} o={clamp((alfVal - 3.4) / 0.3) * (1 - prog(t, B.mateIn, B.mateIn + 0.4))} size={22} />

      {/* thoughts: what each of them is thinking, as POV text */}
      {THOUGHTS.map((th, i) => {
        const at: [number, number] = th.who === 'nan' ? [nhx, nhy] : th.who === 'mate' ? [mhx, mhy] : [ahx, ahy];
        return <Thought key={i} text={th.text} t={t} t0={th.t0} t1={th.t1} at={at} side={at[0] < 540 ? 1 : -1} />;
      })}

      {/* the timeline switch: crack + flash, then the question card */}
      {t >= B.switch - 0.02 && t < B.switch + 0.9 ? <Crack k={prog(t, B.switch, B.switch + 0.22, 'out')} fade={1 - prog(t, B.switch + 0.35, B.switch + 0.85)} flash={Math.max(0, 1 - (t - B.switch) / 0.2)} /> : null}
      <div style={{ position: 'absolute', bottom: 300, width: '100%', textAlign: 'center', opacity: prog(t, B.switch + 0.35, B.switch + 0.7) * (1 - prog(t, B.hope + 1.2, B.hope + 1.6)),
        fontFamily: 'Inter', fontWeight: 800, fontSize: 70, letterSpacing: 2, color: '#fff', textShadow: '0 0 24px rgba(255,255,255,.35)' }}>
        SO WHAT IF IT <span style={{ color: '#FFD400' }}>HADN'T</span>?
      </div>
      <div style={{ position: 'absolute', bottom: 90, width: '100%', textAlign: 'center', fontFamily: 'Inter', fontWeight: 600, fontSize: 22, letterSpacing: 8, color: 'rgba(255,255,255,.35)' }}>
        ACTING TEST 2 · EP 08
      </div>
    </AbsoluteFill>
  );
};

// keep the R3F camera on our path every frame
import { useThree } from '@react-three/fiber';
export const CamSync: React.FC<{ cam: Cam }> = ({ cam }) => {
  const { camera } = useThree();
  camera.position.set(...cam.p);
  (camera as THREE.PerspectiveCamera).fov = cam.fov;
  (camera as THREE.PerspectiveCamera).updateProjectionMatrix();
  camera.lookAt(...cam.t);
  return null;
};
export const Crack: React.FC<{ k: number; fade: number; flash: number }> = ({ k, fade, flash }) => {
  const pts = [[-20, 880], [180, 930], [260, 860], [430, 990], [560, 920], [700, 1040], [820, 960], [960, 1060], [1100, 1010]];
  const n = Math.max(2, Math.ceil(k * pts.length));
  return (
    <AbsoluteFill>
      <svg width={1080} height={1920} style={{ position: 'absolute', opacity: fade }}>
        <polyline points={pts.slice(0, n).map((p) => p.join(',')).join(' ')} fill="none" stroke="#e9fffb" strokeWidth={6}
          style={{ filter: 'drop-shadow(0 0 14px #7ff5e6)' }} />
      </svg>
      <AbsoluteFill style={{ background: `rgba(200,255,250,${flash * 0.5})` }} />
    </AbsoluteFill>
  );
};
