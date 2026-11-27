// The episode player: one picture per shot, the camera always moving, fly-through and whip transitions,
// characters with expressions, props that pop in, and the one big-number card. Everything is a pure function of time.
import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import { ThreeCanvas } from '@remotion/three';
import { useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { Person, FACES, BODY, mixFace, Body } from '../cast/Person';
import { CAST } from '../cast/cast';
import { PROPS } from '../props';
import { Street, Bank } from '../worlds/outdoor';
import { CornerShop, Kitchen, TradingFloor, Tabletop } from '../worlds/indoor';
import { Committee } from '../worlds/committee';
import { Sea, Rig, Cavern, Shore } from '../worlds/sea';
import { buildPages } from '../kit/captions';
import { shotStarts, duration } from './timeline';
import type { Episode, Shot, V3, Actor, PropCue } from './types';

const WORLDS: Record<Shot['world'], React.FC<any>> = { street: Street, bank: Bank, shop: CornerShop, kitchen: Kitchen, floor: TradingFloor, table: Tabletop, committee: Committee, sea: Sea, rig: Rig, cavern: Cavern, shore: Shore };
const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
const lerp3 = (a: V3, b: V3, k: number): V3 => [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)];
const inOut = (u: number) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2);
const outBack = (u: number) => 1 + 2.2 * Math.pow(u - 1, 3) + 1.2 * Math.pow(u - 1, 2);
const bounce = (u: number) => { const n = 7.5625, d = 2.75;
  if (u < 1 / d) return n * u * u; if (u < 2 / d) return n * (u -= 1.5 / d) * u + 0.75; if (u < 2.5 / d) return n * (u -= 2.25 / d) * u + 0.9375; return n * (u -= 2.625 / d) * u + 0.984375; };

// The timeline switch (script-rules 6): one look for every what-if, so real history and the what-if never look alike.
// Cooler, violet-shifted grade with a soft vignette; the first what-if shot of a run opens on a white crack across the frame.
export const WHATIF_FILTER = 'saturate(1.3) contrast(1.1) brightness(0.94)';
const CRACK = 'M -20 610 L 180 655 L 245 590 L 410 720 L 470 660 L 640 770 L 700 700 L 860 840 L 930 790 L 1100 880';
const CRACK2 = 'M 410 720 L 395 820 L 450 900 M 700 700 L 745 610 L 720 520';
export const FLY = 0.38, WHIP = 0.16, ARRIVE = 0.3;
/** Engine switches (7 Nov 2026).
 *  cssBlur: scales the old CSS whip/fly blur. The motion-blur compositions (<id>-mb) pass 0.33, because the real
 *           blur from averaged sub-frames does the work (version C of the 7 Nov test).
 *  whip:    'pan'   = the camera itself swings sideways in 3D (fix: the old slide showed a black strip at the edge);
 *           'slide' = the old 2D slide of the whole picture, kept so it can be switched back. */
export const ENGINE = { cssBlur: 1, whip: 'pan' as 'pan' | 'slide' };
export const WHIP_YAW = 0.42; // radians the camera swings on a whip (about 24 degrees)
const yawTarget = (p: V3, t: V3, yaw: number): V3 => { // turn the look-at point about the camera's vertical axis
  const dx = t[0] - p[0], dz = t[2] - p[2], c = Math.cos(yaw), s = Math.sin(yaw);
  return [p[0] + dx * c - dz * s, t[1], p[2] + dx * s + dz * c];
};

const CamRig: React.FC<{ p: V3; t: V3; fov: number }> = ({ p, t, fov }) => {
  const { camera } = useThree();
  const cam = camera as THREE.PerspectiveCamera;
  cam.position.set(...p);
  cam.fov = fov; cam.near = 0.01; cam.far = 200;
  cam.updateProjectionMatrix();
  cam.lookAt(...t);
  return null;
};

/** Ease numbers between pose keys; faces blend over 0.12 s. */
const actorState = (a: Actor, lt: number) => {
  const faces = a.faces ?? [[0, 'neutral']];
  let fi = 0;
  for (let i = 0; i < faces.length; i++) if (faces[i][0] <= lt) fi = i;
  const cur = FACES[faces[fi][1]] ?? FACES.neutral;
  const prev = fi > 0 ? FACES[faces[fi - 1][1]] ?? FACES.neutral : cur;
  const face = fi > 0 ? mixFace(prev, cur, clamp((lt - faces[fi][0]) / 0.12)) : cur;
  const poses = a.poses ?? [[0, {}]];
  let pi = 0;
  for (let i = 0; i < poses.length; i++) if (poses[i][0] <= lt) pi = i;
  const A: Body = { ...BODY, ...poses[pi][1] } as Body;
  const next = poses[pi + 1];
  if (!next) return { face, body: A };
  const B: Body = { ...BODY, ...next[1] } as Body;
  const k = inOut(clamp((lt - poses[pi][0]) / Math.max(0.01, next[0] - poses[pi][0])));
  const mix = (x: any, y: any): any => (typeof x === 'number' ? lerp(x, y, k) : Array.isArray(x) ? x.map((v, i) => lerp(v, y[i], k)) : k < 0.5 ? x : y);
  const body = Object.fromEntries(Object.keys(A).map((key) => [key, mix((A as any)[key], (B as any)[key])])) as Body;
  return { face, body };
};

const Prop: React.FC<{ c: PropCue; lt: number }> = ({ c, lt }) => {
  const C = PROPS[c.kind] as React.FC<any>;
  const pop = c.from === undefined ? 1 : clamp((lt - c.from) / 0.28);
  if (pop <= 0) return null;
  const mu = c.move ? clamp((lt - c.move.t0) / (c.move.t1 - c.move.t0)) : 0;
  const pos = c.move ? lerp3(c.at, c.move.to, c.move.ease === 'drop' ? bounce(mu) : inOut(mu)) : c.at;
  const args = { ...(c.args ?? {}) };
  if (c.grow) { const g = lerp(c.grow.from, c.grow.to, inOut(clamp((lt - c.grow.t0) / (c.grow.t1 - c.grow.t0)))); args[c.grow.key] = c.grow.round === false ? g : Math.round(g); }
  const s = (c.s ?? 1) * (c.from === undefined ? 1 : outBack(pop));
  return (
    <group position={pos} rotation={c.rot ?? [0, 0, 0]} scale={s}>
      <C {...args} />
    </group>
  );
};

export const makeEpisode = (ep: Episode) => {
  const starts = shotStarts(ep);
  const total = duration(ep);
  const pages = ep.captions === false ? [] : buildPages(ep.words); // captions on by default
  const Comp: React.FC<{ cssBlur?: number }> = ({ cssBlur }) => {
    const cb = cssBlur ?? ENGINE.cssBlur;
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const t = frame / fps;
    let i = 0;
    for (let k = 0; k < starts.length; k++) if (starts[k] <= t) i = k;
    const shot = ep.shots[i];
    const next = ep.shots[i + 1];
    const len = (i + 1 < starts.length ? starts[i + 1] : total) - starts[i];
    const lt = t - starts[i];
    const u = clamp(lt / len);
    const move = shot.cam.move ?? 'drift';
    const ku = move === 'hold' ? 0 : move === 'fast' ? inOut(u) : 0.65 * u + 0.35 * (1 - Math.cos(Math.PI * u)) / 2;
    let p = lerp3(shot.cam.from.p, shot.cam.to.p, ku);
    let tgt = lerp3(shot.cam.from.t, shot.cam.to.t, ku);
    let fov = lerp(shot.cam.from.fov, shot.cam.to.fov, ku);
    let blur = 0, scale = 1, shiftX = 0, flash = 0;
    // leaving: dive into the exit point when the next shot flies in; whip sideways when it whips in
    const left = len - lt;
    if (next?.enter === 'fly' && left < FLY) {
      const k = Math.pow(1 - left / FLY, 2);
      p = lerp3(p, shot.exitInto ?? tgt, k * 0.9); fov *= 1 - 0.35 * k; blur = 7 * k; scale = 1 + 0.12 * k;
    }
    if (next?.enter === 'whip' && left < WHIP) { const k = 1 - left / WHIP; if (ENGINE.whip === 'pan') tgt = yawTarget(p, tgt, WHIP_YAW * k * k); else shiftX = -32 * k * k; blur = 14 * k; }
    // arriving
    if (shot.enter === 'fly' && lt < ARRIVE) { const k = Math.pow(1 - lt / ARRIVE, 2); p = lerp3(p, tgt, k * 0.55); blur = Math.max(blur, 7 * k); flash = 0.45 * k; }
    if (shot.enter === 'whip' && lt < WHIP) { const k = 1 - lt / WHIP; if (ENGINE.whip === 'pan') tgt = yawTarget(p, tgt, -WHIP_YAW * k * k); else shiftX = 32 * k * k; blur = Math.max(blur, 14 * k); }
    const W = WORLDS[shot.world];
    const wi = !!shot.whatif;
    const crackK = wi && !(i > 0 && ep.shots[i - 1].whatif) ? clamp(1 - lt / 0.5) : 0; // first what-if shot of a run
    const hook = ep.hook && t < (ep.hook.until ?? 3) ? clamp(Math.min(t / 0.15, ((ep.hook.until ?? 3) - t) / 0.25)) : 0;
    const num = shot.number;
    const numK = num ? clamp((lt - (num.at ?? 0.2)) / 0.22) : 0;
    const page = pages.find((pg, k) => t >= pg.start - 0.05 && t < (pages[k + 1]?.start ?? Infinity) - 0.05 && t < pg.end + 0.45);
    return (
      <AbsoluteFill style={{ background: '#000' }}>
        <AbsoluteFill style={{ transform: `translateX(${shiftX + (crackK > 0 ? Math.sin(lt * 90) * 0.6 * crackK : 0)}%) scale(${scale})`,
          filter: [wi ? WHATIF_FILTER : '', blur * cb > 0.2 ? `blur(${(blur * cb).toFixed(1)}px)` : ''].join(' ').trim() || undefined }}>
          <ThreeCanvas width={1080} height={1920} gl={{ antialias: false }} camera={{ fov: 40, position: [0, 1.6, 5] }}>
            <CamRig p={p} t={tgt} fov={fov} />
            <W t={t} lt={lt} {...(shot.worldArgs ?? {})} />
            {(shot.actors ?? []).map((a, k) => {
              const st = actorState(a, lt);
              return <Person key={k} look={CAST[a.who]} face={st.face} body={st.body} position={a.at} rotationY={a.rotY ?? 0} scale={a.scale ?? 1} pinGlow={wi && a.who === 'lead' ? 0.75 + 0.25 * Math.sin(t * 6) : 0} />;
            })}
            {(shot.props ?? []).map((c, k) => <Prop key={k} c={c} lt={lt} />)}
          </ThreeCanvas>
        </AbsoluteFill>
        {wi ? <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 50% 42%, rgba(0,0,0,0) 48%, rgba(30,10,60,0.75) 100%)', mixBlendMode: 'multiply' }} /> : null}
        {wi ? <AbsoluteFill style={{ background: 'linear-gradient(180deg, rgba(70,40,170,0.30), rgba(0,140,160,0.28))', mixBlendMode: 'color' }} /> : null}
        {crackK > 0.01 ? (
          <AbsoluteFill>
            <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{ position: 'absolute', inset: 0 }}>
              <path d={CRACK} stroke="#FFFFFF" strokeWidth={10 * crackK + 2} fill="none" opacity={Math.min(1, crackK * 1.6)} strokeLinejoin="miter" />
              <path d={CRACK2} stroke="#FFFFFF" strokeWidth={6 * crackK + 1} fill="none" opacity={Math.min(1, crackK * 1.6)} />
            </svg>
            <AbsoluteFill style={{ background: '#FFFFFF', opacity: 0.55 * Math.pow(crackK, 3) }} />
          </AbsoluteFill>
        ) : null}
        {flash > 0.01 ? <AbsoluteFill style={{ background: '#FFF6E6', opacity: flash }} /> : null}
        {hook > 0.01 ? (
          <div style={{ position: 'absolute', left: 70, right: 70, top: 230, display: 'flex', justifyContent: 'center', opacity: hook, transform: `translateY(${(1 - hook) * -20}px)` }}>
            <div style={{ background: '#FFD43B', color: '#111', font: '900 70px Inter', lineHeight: 1.08, padding: '18px 30px', borderRadius: 16, textAlign: 'center', boxShadow: '0 8px 0 #111' }}>{ep.hook!.text}</div>
          </div>
        ) : null}
        {num && numK > 0 ? (
          <div style={{ position: 'absolute', left: 0, right: 0, top: 1000, display: 'flex', justifyContent: 'center' }}>
            <div style={{ transform: `scale(${0.7 + 0.3 * outBack(numK)})`, opacity: numK, background: 'rgba(12,16,24,0.92)', borderRadius: 22, padding: '26px 48px', textAlign: 'center', borderLeft: '10px solid #C8102E' }}>
              <div style={{ font: '800 120px Inter', color: '#FFFFFF', lineHeight: 1.05 }}>{num.text}</div>
              {num.sub ? <div style={{ font: '600 40px Inter', color: '#AEB8C6', marginTop: 8 }}>{num.sub}</div> : null}
            </div>
          </div>
        ) : null}
        {page ? (
          <div style={{ position: 'absolute', left: 60, right: 60, top: 1290, display: 'flex', justifyContent: 'center' }}>
            <div style={{ background: 'rgba(10,12,16,0.88)', borderRadius: 18, padding: '14px 28px', font: '800 66px Inter', textAlign: 'center', lineHeight: 1.15 }}>
              {page.words.map((wi, k) => {
                const raw = ep.words[wi].text; const key = raw.includes('*'); const said = ep.words[wi].start <= t;
                const txt = raw.replace(/\*/g, '');
                return (
                  <span key={wi} style={{ color: key ? '#FFD43B' : '#FFFFFF', opacity: said ? 1 : 0.45, marginRight: k < page.words.length - 1 ? 16 : 0,
                    display: 'inline-block', transform: said && t < ep.words[wi].start + 0.12 ? 'scale(1.08)' : undefined }}>{txt}</span>
                );
              })}
            </div>
          </div>
        ) : null}
      </AbsoluteFill>
    );
  };
  return { Comp, frames: Math.ceil(total * 30), starts, total };
};
