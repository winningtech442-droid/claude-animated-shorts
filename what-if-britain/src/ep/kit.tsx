// Shot episodes on the dark glow stage (11 Nov 2026): one scene per board shot, locked cast, whole-body acting,
// thoughts as POV text, captions on, FOLLOW & SHARE end card. Everything is a pure function of the frame.
import React from 'react';
import * as THREE from 'three';
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import { ThreeCanvas } from '@remotion/three';
import { Person } from '../cast/Person';
import { CAST } from '../cast/cast';
import { buildPages } from '../kit/captions';
import { EASE, clamp, lerp, prog, poseAt, breathe, blink, Spot, Thought, Crack, CamSync, project, Key, Cam, Ease, V3 } from '../tests/ActingTest';

export type { Key, Cam, Ease, V3 };
export { clamp, lerp, prog, EASE };
export type WhoKey = 'nan' | 'alf' | 'mate';
type Wd = { text: string; start: number; end: number };
export type Ctx = { t: number; ts: number; cam: Cam; proj: (w: V3) => [number, number]; sw: number; glow: string };
export type Shot = {
  id: string; t0: number; t1: number;
  cam: [number, Cam, Ease?][];
  who?: Partial<Record<WhoKey, Key[]>>;
  mod?: Partial<Record<WhoKey, (p: any, ts: number) => any>>;
  spots?: { x: number; on?: number }[];
  world?: (c: Ctx) => React.ReactNode;
  hud?: (c: Ctx) => React.ReactNode;
  thoughts?: { who: WhoKey; text: string; t0: number; t1: number }[];
  sw?: number | ((ts: number) => number);
  crack?: { at: number; flashOnly?: boolean };
  scroll?: number; // lane dashes slide (m/s): a runner going nowhere
  noLane?: boolean;
  dim?: number; // end-card dim
};

const LOOK = { nan: CAST.nan, alf: CAST.lead, mate: CAST.mate };
const HEAD_H = { nan: 1.72, alf: 1.92, mate: 1.98 };
const SEED = { nan: 1.1, alf: 0.3, mate: 2.2 };

export const cam = (x: number, d: number, ty: number, fov = 38, lift = 0.32): Cam => ({ p: [x, ty + lift, d], t: [x, ty, 0], fov });
function camAt(keys: [number, Cam, Ease?][], t: number): Cam {
  let i = 0; while (i < keys.length - 1 && keys[i + 1][0] <= t) i++;
  const a = keys[i], b = keys[Math.min(i + 1, keys.length - 1)];
  const k = b[0] === a[0] ? 1 : EASE[b[2] ?? 'io'](clamp((t - a[0]) / (b[0] - a[0])));
  const L = (u: V3, v: V3) => u.map((x, j) => lerp(x, v[j], k)) as V3;
  return { p: L(a[1].p, b[1].p), t: L(a[1].t, b[1].t), fov: lerp(a[1].fov, b[1].fov, k) };
}
// a slow push-in or drift inside one shot
export const push = (x0: number, d0: number, ty: number, dur: number, x1 = x0, d1 = d0 - 0.5, fov = 38): [number, Cam, Ease?][] =>
  [[0, cam(x0, d0, ty, fov)], [dur, cam(x1, d1, ty, fov), 'io']];

// running in place: arms pump, knees lift
export const runMod = (hz = 1.7, amp = 1, lean = 14) => (p: any, ts: number) => {
  const s = Math.sin(2 * Math.PI * hz * ts), c = Math.cos(2 * Math.PI * hz * ts);
  return { ...p, hipL: [34 * amp * s, 3], hipR: [-34 * amp * s, 3], knL: 50 * amp * Math.max(0, s), knR: 50 * amp * Math.max(0, -s),
    shL: [-42 * amp * s, 8], shR: [42 * amp * s, 8], elL: 85, elR: 85, spine: (p.spine ?? 0) + lean, bounce: (p.bounce ?? 0) + 0.035 * amp * Math.abs(c) };
};

// ---------- glow props ----------
export const Glow: React.FC<{ c?: string; o?: number }> = ({ c = '#ffffff', o = 1 }) => <meshBasicMaterial color={c} transparent={o < 1} opacity={o} toneMapped={false} depthWrite={o >= 1} />;
export const Bar: React.FC<{ a: V3; b: V3; r?: number; c?: string; o?: number }> = ({ a, b, r = 0.011, c = '#ffffff', o = 1 }) => {
  const d = new THREE.Vector3(...b).sub(new THREE.Vector3(...a)); const L = d.length();
  const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.clone().normalize());
  const m = new THREE.Vector3(...a).addScaledVector(d, 0.5);
  return <mesh position={m} quaternion={q}><cylinderGeometry args={[r, r, L, 8]} /><Glow c={c} o={o} /></mesh>;
};
export const Box: React.FC<{ p: V3; s: V3; c?: string; glow?: boolean; o?: number; r?: V3 }> = ({ p, s, c = '#2a2a31', glow, o = 1, r = [0, 0, 0] }) => (
  <mesh position={p} rotation={r}><boxGeometry args={s} />{glow ? <Glow c={c} o={o} /> : <meshStandardMaterial color={c} roughness={0.8} transparent={o < 1} opacity={o} />}</mesh>
);
export const Lane: React.FC<{ off: number }> = ({ off }) => (
  <group>
    {Array.from({ length: 44 }).map((_, i) => {
      const x = -8 + i * 0.5 - (off % 0.5);
      return <mesh key={i} position={[x, 0.004, -0.35]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[0.24, 0.014]} /><Glow c="#8d8d95" /></mesh>;
    })}
  </group>
);

export const HudText: React.FC<{ x: number; y: number; text: string; size?: number; o?: number; color?: string; sp?: number; weight?: number }> = ({ x, y, text, size = 26, o = 1, color = 'rgba(255,255,255,.78)', sp = 7, weight = 600 }) => (
  <div style={{ position: 'absolute', left: x - 420, top: y, width: 840, textAlign: 'center', opacity: o, fontFamily: 'Inter', fontWeight: weight, fontSize: size, letterSpacing: sp, color, textShadow: '0 2px 10px rgba(0,0,0,.8)', whiteSpace: 'nowrap' }}>{text}</div>
);
export const Big: React.FC<{ top: number; main: string; sub?: string; o?: number; pop?: number; color?: string; size?: number }> = ({ top, main, sub, o = 1, pop = 1, color = '#FFD400', size = 170 }) => (
  <div style={{ position: 'absolute', top, width: '100%', textAlign: 'center', opacity: o }}>
    <div style={{ fontFamily: 'Inter', fontWeight: 800, fontSize: size, lineHeight: 1.05, transform: `scale(${pop})`, color, textShadow: `0 0 40px ${color}99` }}>{main}</div>
    {sub ? <div style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: 28, letterSpacing: 9, color: 'rgba(255,255,255,.75)', marginTop: 4 }}>{sub}</div> : null}
  </div>
);

// ---------- the episode ----------
export const makeShotEpisode = (cfg: { id: string; shots: Shot[]; words: Wd[]; total: number; endAt: number; hook?: { text: React.ReactNode; until: number }; endSub?: string; day?: boolean }) => {
  const pages = buildPages(cfg.words);
  const Comp: React.FC = () => {
    const f = useCurrentFrame(); const { fps, width: W, height: H } = useVideoConfig();
    const t = f / fps;
    const shot = cfg.shots.find((s) => t >= s.t0 && t < s.t1) ?? cfg.shots[cfg.shots.length - 1];
    const ts = t - shot.t0;
    const cm = camAt(shot.cam, ts);
    const sw = typeof shot.sw === 'function' ? shot.sw(ts) : shot.sw ?? 0;
    const glow = `rgb(${lerp(255, 140, sw) | 0},${lerp(255, 236, sw) | 0},${lerp(255, 226, sw) | 0})`;
    const proj = (w: V3) => project(cm, w, W, H) as [number, number];
    const ctx: Ctx = { t, ts, cam: cm, proj, sw, glow };

    const who = (['nan', 'alf', 'mate'] as WhoKey[]).filter((k) => shot.who?.[k]);
    const P: Record<string, any> = {};
    for (const k of who) {
      let p = breathe(poseAt(shot.who![k]!, ts), ts, k === 'nan' ? 3.8 : 3.4, 0.8);
      const m = shot.mod?.[k]; if (m) p = m(p, ts);
      P[k] = p;
    }
    const headPx = (k: WhoKey): [number, number] => {
      const p = P[k]; const h = HEAD_H[k] - (p.crouch ?? 0) * 0.16 - Math.max(0, p.spine ?? 0) * 0.004;
      return proj([p.x + (p.sway ?? 0), h, 0]);
    };
    const bg = cfg.day ? `rgb(${lerp(150, 112, sw) | 0},${lerp(205, 150, sw) | 0},${lerp(250, 232, sw) | 0})` : `rgb(${lerp(6, 16, sw) | 0},${lerp(6, 10, sw) | 0},${lerp(9, 28, sw) | 0})`;
    const page = pages.find((pg, k) => t >= pg.start - 0.05 && t < (pages[k + 1]?.start ?? Infinity) - 0.05 && t < pg.end + 0.45);
    const endK = prog(t, cfg.endAt, cfg.endAt + 0.28, 'back');

    return (
      <AbsoluteFill style={{ background: '#060609' }}>
        <ThreeCanvas width={W} height={H} camera={{ position: cm.p, fov: cm.fov, near: 0.05, far: 60 }} onCreated={({ camera }) => camera.lookAt(...cm.t)}>
          <CamSync cam={cm} />
          <color attach="background" args={[bg]} />
          {cfg.day ? (
            <>
              <fog attach="fog" args={[bg, 16, 46]} />
              <ambientLight intensity={0.85} color={`rgb(${lerp(255, 205, sw) | 0},${lerp(250, 215, sw) | 0},${lerp(240, 255, sw) | 0})`} />
              <hemisphereLight args={[`rgb(${lerp(255, 190, sw) | 0},${lerp(255, 225, sw) | 0},${lerp(255, 255, sw) | 0})`, '#b9a98f', 0.75]} />
              <directionalLight position={[4, 7, 6]} intensity={1.7} color={`rgb(${lerp(255, 200, sw) | 0},${lerp(244, 220, sw) | 0},${lerp(214, 255, sw) | 0})`} />
              {who.map((k) => <mesh key={'b' + k} position={[P[k].x, 0.012, 0.02]} rotation={[-Math.PI / 2, 0, 0]}><circleGeometry args={[0.38, 24]} /><meshBasicMaterial color="#000" transparent opacity={0.28} depthWrite={false} /></mesh>)}
            </>
          ) : (
            <>
              <fog attach="fog" args={[bg, 6, 13]} />
              <ambientLight intensity={0.3} />
              <hemisphereLight args={['#dfe6ff', '#101014', 0.35]} />
              <directionalLight position={[0.5, 2.5, 4]} intensity={0.9} />
              <mesh rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[40, 24]} /><meshStandardMaterial color={sw > 0 ? '#0c0c15' : '#0d0d11'} roughness={1} /></mesh>
              {shot.noLane ? null : <Lane off={ts * (shot.scroll ?? 0)} />}
              {(shot.spots ?? who.map((k) => ({ x: P[k].x, on: 1 }))).map((s, i) => <Spot key={i} x={s.x} on={s.on ?? 1} tint={sw > 0 ? glow : '#ffffff'} />)}
            </>
          )}
          {shot.world?.(ctx)}
          {who.map((k) => (
            <Person key={k} look={LOOK[k]} face={blink(P[k].faceMix, ts, SEED[k])} body={P[k]} position={[P[k].x, 0, 0]} rotationY={P[k].turnY}
              pinGlow={k === 'alf' && sw > 0 ? 0.6 + 0.4 * Math.sin(t * 6) : 0} />
          ))}
        </ThreeCanvas>

        {cfg.day && sw > 0 ? <AbsoluteFill style={{ pointerEvents: 'none', background: `radial-gradient(ellipse at 50% 45%, rgba(30,20,90,0) 45%, rgba(25,15,70,${0.5 * sw}) 100%)`, boxShadow: `inset 0 0 0 2000px rgba(110,90,220,${0.09 * sw})` }} /> : null}
        {shot.hud?.(ctx)}
        {(shot.thoughts ?? []).map((th, i) => {
          const at = headPx(th.who); return <Thought key={i} text={th.text} t={ts} t0={th.t0} t1={th.t1} at={at} side={at[0] < 540 ? 1 : -1} />;
        })}
        {shot.crack ? (
          ts >= shot.crack.at - 0.02 && ts < shot.crack.at + 0.9
            ? <Crack k={shot.crack.flashOnly ? 1 : prog(ts, shot.crack.at, shot.crack.at + 0.3, 'out')} fade={shot.crack.flashOnly ? 1 - prog(ts, shot.crack.at + 0.3, shot.crack.at + 0.85) : 1 - prog(ts, shot.crack.at + 0.6, shot.crack.at + 0.9)} flash={Math.max(0, 1 - (ts - shot.crack.at) / 0.2) * (shot.crack.flashOnly ? 1 : 0)} />
            : null
        ) : null}

        {cfg.hook && t < cfg.hook.until ? (
          <div style={{ position: 'absolute', top: 150, left: 24, right: 24, textAlign: 'center', opacity: clamp(t / 0.25) * (1 - prog(t, cfg.hook.until - 0.35, cfg.hook.until)),
            fontFamily: 'Inter', fontWeight: 800, fontSize: 58, lineHeight: 1.12, letterSpacing: 1, color: '#fff', textShadow: '0 0 24px rgba(255,255,255,.35), 0 3px 10px rgba(0,0,0,.8)', ...(cfg.day ? { background: 'rgba(10,12,22,.78)', borderRadius: 22, padding: '14px 22px', left: 60, right: 60 } : {}) }}>{cfg.hook.text}</div>
        ) : null}

        {page && t < cfg.endAt ? (
          <div style={{ position: 'absolute', left: 60, right: 60, top: 1290, display: 'flex', justifyContent: 'center' }}>
            <div style={{ background: 'rgba(10,12,16,0.88)', borderRadius: 18, padding: '14px 28px', font: '800 66px Inter', textAlign: 'center', lineHeight: 1.15 }}>
              {page.words.map((wi, k) => {
                const raw = cfg.words[wi].text; const key = raw.includes('*'); const said = cfg.words[wi].start <= t;
                return <span key={wi} style={{ color: key ? '#FFD43B' : '#FFFFFF', opacity: said ? 1 : 0.45, marginRight: k < page.words.length - 1 ? 16 : 0, display: 'inline-block',
                  transform: said && t < cfg.words[wi].start + 0.12 ? 'scale(1.08)' : undefined }}>{raw.replace(/\*/g, '')}</span>;
              })}
            </div>
          </div>
        ) : null}

        {/* the end card: bold, upper-middle, clear of TikTok's buttons and caption bar */}
        {t >= cfg.endAt ? (
          <AbsoluteFill>
            <AbsoluteFill style={{ background: `rgba(6,6,9,${0.5 * endK})` }} />
            <div style={{ position: 'absolute', top: 430, left: 0, right: 0, textAlign: 'center', transform: `scale(${0.6 + 0.4 * endK})`, opacity: clamp(endK * 1.4), fontFamily: 'Inter', fontWeight: 900 }}>
              <div style={{ fontSize: 210, lineHeight: 0.98, color: '#fff', letterSpacing: -2, textShadow: '0 0 50px rgba(255,255,255,.45), 0 6px 18px rgba(0,0,0,.7)' }}>FOLLOW</div>
              <div style={{ fontSize: 210, lineHeight: 0.98, color: '#FFD400', letterSpacing: -2, textShadow: '0 0 50px rgba(255,212,0,.6), 0 6px 18px rgba(0,0,0,.7)' }}>&amp; SHARE</div>
              {cfg.endSub ? <div style={{ marginTop: 40, fontSize: 40, fontWeight: 700, letterSpacing: 6, color: 'rgba(255,255,255,.85)', textShadow: '0 3px 10px rgba(0,0,0,.8)', opacity: clamp((endK - 0.6) / 0.4) }}>{cfg.endSub}</div> : null}
            </div>
          </AbsoluteFill>
        ) : null}
      </AbsoluteFill>
    );
  };
  return { Comp, frames: Math.ceil(cfg.total * 30) };
};
