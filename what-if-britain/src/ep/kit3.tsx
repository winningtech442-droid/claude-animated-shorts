// v3 episode kit (27 Nov 2026): story scenes built per episode, any cast per shot, whole-body stunts (characters can
// fly, flop and tumble), the timeline switch, captions coloured by speaker. Everything is a pure function of the frame.
// STUDIO-RULES v3: one location per scene, a new angle every ~2 s, captions bold with a black outline in the lower third.
import React from 'react';
import * as THREE from 'three';
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import { ThreeCanvas } from '@remotion/three';
import { Person, Look } from '../cast/Person';
import { CAST } from '../cast/cast';
import { EASE, clamp, lerp, prog, poseAt, breathe, blink, CamSync, Crack, project, Key, Cam, Ease, V3 } from '../tests/ActingTest';

export type { Key, Cam, Ease, V3 };
export { clamp, lerp, prog, EASE };

// ---------- actors ----------
/** A pose key plus the root transform: position y/z (x is in Pose) and whole-body rotation (radians, applied
 *  innermost rz, then ry, then rx). vis 0 hides the actor (e.g. inside a wardrobe). Fields carry forward from the
 *  previous key, so each key only lists what changes. */
export type Pose3 = Key[1] & { y?: number; z?: number; rx?: number; ry?: number; rz?: number; vis?: number; scale?: number };
export type Key3 = [number, Pose3, Ease?];
export type Actor = {
  who: string; // cast key in CAST, or a guest
  look?: Look;
  keys: Key3[];
  pin?: (ts: number) => number; // pin glow
  heldL?: (ts: number) => React.ReactNode; heldR?: (ts: number) => React.ReactNode;
  seed?: number; noBreath?: boolean;
};

const ROOT = ['y', 'z', 'rx', 'ry', 'rz', 'scale'] as const;
const carry = (keys: Key3[]): Key3[] => {
  let acc: Pose3 = {};
  return keys.map(([t, p, e]) => { acc = { ...acc, ...p }; return [t, acc, e] as Key3; });
};
export const actorAt = (a: Actor, ts: number) => {
  const keys = carry(a.keys);
  const body = poseAt(keys as Key[], ts) as any;
  let i = 0; while (i < keys.length - 1 && keys[i + 1][0] <= ts) i++;
  const ka = keys[i], kb = keys[Math.min(i + 1, keys.length - 1)];
  const k = kb[0] === ka[0] ? 1 : EASE[kb[2] ?? 'io'](clamp((ts - ka[0]) / (kb[0] - ka[0])));
  const root: Record<string, number> = {};
  for (const n of ROOT) root[n] = lerp((ka[1][n] as number) ?? (n === 'scale' ? 1 : 0), (kb[1][n] as number) ?? (ka[1][n] as number) ?? (n === 'scale' ? 1 : 0), k);
  const vis = (k < 1 ? ka[1].vis : kb[1].vis) ?? 1;
  body.sit = (k < 0.5 ? ka[1].sit : kb[1].sit) ?? false; // poseAt only blends numbers: carry the sit flag across
  return { body: a.noBreath ? body : breathe(body, ts, 3.4, 0.8), root, vis };
};

export const ActorView: React.FC<{ a: Actor; ts: number; t: number }> = ({ a, ts, t }) => {
  const { body, root, vis } = actorAt(a, ts);
  if (!vis) return null;
  const look = a.look ?? CAST[a.who];
  return (
    <group position={[body.x ?? 0, root.y, root.z]} rotation={[root.rx, root.ry, root.rz]} scale={root.scale}>
      <Person look={look} face={blink(body.faceMix, ts + (a.seed ?? 0), a.seed ?? 0.5)} body={body} rotationY={body.turnY ?? 0}
        pinGlow={a.pin ? a.pin(ts) : 0} heldL={a.heldL?.(ts)} heldR={a.heldR?.(ts)} />
    </group>
  );
};

// ---------- shots ----------
export type Ctx = { t: number; ts: number; sw: number; cam: Cam; proj: (w: V3) => [number, number] };
export type Shot = {
  id: string; t0: number; t1: number;
  cam: [number, Cam, Ease?][];
  set: (c: Ctx) => React.ReactNode;
  cast: Actor[];
  sw?: number | ((ts: number) => number); // timeline switch: violet-teal grade
  crack?: number; // shot time of the white crack
  shake?: [number, number][]; // [shot time, strength]: impact kicks that flip every frame and die in ~7 frames
  overlay?: (c: Ctx) => React.ReactNode;
};

export const cam = (p: V3, t: V3, fov = 40): Cam => ({ p, t, fov });
const camAt = (keys: [number, Cam, Ease?][], t: number): Cam => {
  let i = 0; while (i < keys.length - 1 && keys[i + 1][0] <= t) i++;
  const a = keys[i], b = keys[Math.min(i + 1, keys.length - 1)];
  const k = b[0] === a[0] ? 1 : EASE[b[2] ?? 'io'](clamp((t - a[0]) / (b[0] - a[0])));
  const L = (u: V3, v: V3) => u.map((x, j) => lerp(x, v[j], k)) as V3;
  return { p: L(a[1].p, b[1].p), t: L(a[1].t, b[1].t), fov: lerp(a[1].fov, b[1].fov, k) };
};

// ---------- captions ----------
export const SPEAKER_COLOUR: Record<string, string> = {
  narrator: '#FFFFFF', alfie: '#9FD0FF', mate: '#BDE58F', nan: '#F7B2DC', producer: '#FFC94D',
};
const GUEST_COLOUR = '#8FE8E4';
type Wd = { text: string; start: number; end: number; speaker: string; line: number };
type Page = { words: number[]; start: number; end: number; speaker: string };
const pagesOf = (W: Wd[]): Page[] => {
  const pages: Page[] = []; let cur: number[] = [];
  const flush = () => { if (cur.length) pages.push({ words: cur, start: W[cur[0]].start, end: W[cur[cur.length - 1]].end, speaker: W[cur[0]].speaker }); cur = []; };
  W.forEach((w, i) => {
    if (cur.length) {
      const prev = W[cur[cur.length - 1]];
      const len = cur.map((k) => W[k].text).join(' ').length + 1 + w.text.length;
      if (w.line !== prev.line || cur.length >= 3 || len > 18 || /[.?!,]$/.test(prev.text.replace(/\*/g, ''))) flush();
    }
    cur.push(i);
  });
  flush(); return pages;
};

const OUTLINE = '-4px 0 0 #000, 4px 0 0 #000, 0 -4px 0 #000, 0 4px 0 #000, -3px -3px 0 #000, 3px -3px 0 #000, -3px 3px 0 #000, 3px 3px 0 #000, 0 8px 14px rgba(0,0,0,.55)';

// ---------- the episode ----------
export const makeEpisode3 = (cfg: {
  id: string; shots: Shot[]; words: Wd[]; total: number;
  hook?: { node: React.ReactNode; until: number };
  title?: { at: number; until: number };
}) => {
  const pages = pagesOf(cfg.words);
  const Comp: React.FC = () => {
    const f = useCurrentFrame(); const { fps, width: W, height: H } = useVideoConfig();
    const t = f / fps;
    const shot = cfg.shots.find((s) => t >= s.t0 && t < s.t1) ?? cfg.shots[cfg.shots.length - 1];
    const ts = t - shot.t0;
    let cm = camAt(shot.cam, ts);
    for (const [at, s] of shot.shake ?? []) {
      const fr = Math.round((ts - at) * fps);
      if (fr >= 0 && fr < 8) {
        const a = s * (1 - fr / 8) * (fr % 2 ? -1 : 1);
        cm = { ...cm, p: [cm.p[0] + 0.03 * a, cm.p[1] + 0.022 * a, cm.p[2]], t: [cm.t[0] + 0.03 * a, cm.t[1] + 0.02 * a, cm.t[2]] };
      }
    }
    const sw = typeof shot.sw === 'function' ? shot.sw(ts) : shot.sw ?? 0;
    const proj = (w: V3) => project(cm, w, W, H) as [number, number];
    const ctx: Ctx = { t, ts, sw, cam: cm, proj };
    const inShot = new Set(shot.cast.map((a) => a.who));
    const page = pages.find((pg, k) => t >= pg.start - 0.04 && t < (pages[k + 1]?.start ?? Infinity) - 0.04 && t < pg.end + 0.35);

    return (
      <AbsoluteFill style={{ background: '#0b0b10' }}>
        <ThreeCanvas width={W} height={H} camera={{ position: cm.p, fov: cm.fov, near: 0.03, far: 80 }} onCreated={({ camera }) => camera.lookAt(...cm.t)}>
          <CamSync cam={cm} />
          {shot.set(ctx)}
          {shot.cast.map((a, i) => <ActorView key={a.who + i} a={a} ts={ts} t={t} />)}
        </ThreeCanvas>

        {/* the timeline switch: cooler violet-teal grade with a vignette */}
        {sw > 0 ? <AbsoluteFill style={{ pointerEvents: 'none', background: `radial-gradient(ellipse at 50% 45%, rgba(40,20,110,0) 40%, rgba(30,12,80,${0.55 * sw}) 100%)`, boxShadow: `inset 0 0 0 2000px rgba(90,70,220,${0.13 * sw})`, mixBlendMode: 'normal' }} /> : null}
        {shot.overlay?.(ctx)}
        {shot.crack !== undefined && ts >= shot.crack - 0.02 && ts < shot.crack + 0.9
          ? <Crack k={prog(ts, shot.crack, shot.crack + 0.3, 'out')} fade={1 - prog(ts, shot.crack + 0.6, shot.crack + 0.9)} flash={Math.max(0, 1 - (ts - shot.crack) / 0.2)} />
          : null}

        {cfg.hook && t < cfg.hook.until ? (
          <div style={{ position: 'absolute', top: 200, left: 40, right: 40, textAlign: 'center', opacity: clamp(t / 0.15) * (1 - prog(t, cfg.hook.until - 0.3, cfg.hook.until)),
            fontFamily: 'Inter', fontWeight: 800, fontSize: 84, lineHeight: 1.08, color: '#fff', textShadow: OUTLINE }}>{cfg.hook.node}</div>
        ) : null}

        {cfg.title && t >= cfg.title.at && t < cfg.title.until ? (() => {
          const k = prog(t, cfg.title.at, cfg.title.at + 0.22, 'back'), out = 1 - prog(t, cfg.title.until - 0.25, cfg.title.until);
          return (
            <div style={{ position: 'absolute', top: 560, width: '100%', textAlign: 'center', transform: `scale(${0.4 + 0.6 * k})`, opacity: clamp(k * 1.5) * out, fontFamily: 'Inter', fontWeight: 900, letterSpacing: -2 }}>
              <div style={{ fontSize: 150, lineHeight: 0.95, color: '#fff', textShadow: OUTLINE }}>WHAT IF</div>
              <div style={{ fontSize: 150, lineHeight: 0.95, color: '#E8263A', textShadow: OUTLINE }}>BRITAIN</div>
            </div>
          );
        })() : null}

        {page ? (
          <div style={{ position: 'absolute', left: 50, right: 50, top: 1300, textAlign: 'center' }}>
            {page.words.map((wi, k) => {
              const w = cfg.words[wi]; const raw = w.text; const pop = /^\*.*\*[^*]*$/.test(raw) && !/^\w\*+/.test(raw); const said = w.start <= t;
              const colour = pop ? '#FF4040' : SPEAKER_COLOUR[w.speaker] ?? GUEST_COLOUR;
              return (
                <span key={wi} style={{ display: 'inline-block', marginRight: k < page.words.length - 1 ? 22 : 0, fontFamily: 'Inter', fontWeight: 800, fontSize: 82,
                  fontStyle: inShot.has(w.speaker) ? 'normal' : 'italic', color: colour, opacity: said ? 1 : 0.0, textShadow: OUTLINE,
                  transform: said && t < w.start + 0.1 ? 'scale(1.12)' : undefined }}>{pop ? raw.replace(/^\*/, '').replace(/\*([^*]*)$/, '$1') : raw}</span>
              );
            })}
          </div>
        ) : null}
      </AbsoluteFill>
    );
  };
  return { Comp, frames: Math.ceil(cfg.total * 30) };
};
