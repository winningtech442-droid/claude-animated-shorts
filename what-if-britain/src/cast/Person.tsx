// A 3D character built from code: no models to download, so every episode draws the same person.
// Units: metres, feet on y = 0, facing +z. Everything is a pure function of its props (no clocks, no state).
import React, { useMemo } from 'react';
import * as THREE from 'three';

export type Look = {
  name: string;
  skin: string; skinShade: string; hair: string; hairStyle: 'crop' | 'quiff' | 'bun' | 'bald' | 'grey';
  eyes: string; jacket: string; jacketTrim: string; top: string; legs: string; shoes: string; sole: string;
  height: number; build: number; // 1 = average width
  pin?: boolean; glasses?: boolean; collar?: 'harrington' | 'cardigan' | 'suit' | 'hoodie';
  // v3 body system (27 Nov 2026). All optional: unset gives the v2 body, so older episodes look the same.
  belly?: number; // 0 flat .. 1 big round belly (the top shows between the open jacket)
  stoop?: number; // 0 upright .. 1 bent back, rounded shoulders, head pushed forward, knees soft
  head?: number; // head size, 1 = v2
  limbs?: number; // arm and leg thickness, 1 = v2
  legLen?: number; armLen?: number; // limb length multipliers (lanky > 1, stumpy < 1)
  chin?: number; // 0 .. 1 double chin and jowls
  glassesSize?: number; // 1 = v2 frames; Nan's are huge
  headset?: 'boom' | 'phones'; // the producer's talkback headset, the narrator's studio headphones
};

export type Face = {
  browL: number; browR: number; // raise, -1 (frown down) .. 1 (up)
  browTilt: number; // -1 angry (inner down) .. 1 worried (inner up)
  lid: number; // 0 open .. 1 shut
  wide: number; // 0 .. 1 eyes wide (shock)
  look: [number, number]; // eye direction x, y in -1..1
  open: number; // mouth open 0..1
  smile: number; // -1 frown .. 1 grin
  width: number; // mouth width 0.6..1.4
  teeth: number; // 0..1 show teeth (grit / grin)
  cheek: number; // 0..1 puffed cheeks (holding breath)
  blush: number;
};

export const FACES: Record<string, Face> = {
  neutral: { browL: 0, browR: 0, browTilt: 0, lid: 0.12, wide: 0, look: [0, 0], open: 0, smile: 0.1, width: 1, teeth: 0, cheek: 0, blush: 0 },
  happy: { browL: 0.35, browR: 0.35, browTilt: 0, lid: 0.2, wide: 0, look: [0, 0], open: 0.25, smile: 0.9, width: 1.15, teeth: 0.7, cheek: 0, blush: 0.25 },
  laugh: { browL: 0.6, browR: 0.6, browTilt: 0.2, lid: 0.75, wide: 0, look: [0, 0], open: 0.8, smile: 1, width: 1.25, teeth: 0.8, cheek: 0, blush: 0.4 },
  shock: { browL: 1, browR: 1, browTilt: 0.3, lid: 0, wide: 1, look: [0, 0], open: 0.95, smile: -0.1, width: 0.8, teeth: 0.5, cheek: 0, blush: 0 },
  scream: { browL: 0.8, browR: 0.8, browTilt: 0.9, lid: 0.05, wide: 0.8, look: [0, 0], open: 1, smile: -0.5, width: 1.3, teeth: 1, cheek: 0, blush: 0.2 },
  worried: { browL: 0.4, browR: 0.4, browTilt: 1, lid: 0.15, wide: 0.3, look: [0, -0.2], open: 0.15, smile: -0.6, width: 0.9, teeth: 0, cheek: 0, blush: 0 },
  angry: { browL: -0.6, browR: -0.6, browTilt: -1, lid: 0.35, wide: 0, look: [0, 0], open: 0.35, smile: -0.7, width: 1.1, teeth: 1, cheek: 0, blush: 0.3 },
  smug: { browL: 0.7, browR: -0.2, browTilt: -0.3, lid: 0.45, wide: 0, look: [0.4, 0], open: 0, smile: 0.6, width: 1.05, teeth: 0, cheek: 0, blush: 0 },
  sad: { browL: 0.1, browR: 0.1, browTilt: 0.9, lid: 0.4, wide: 0, look: [0, -0.5], open: 0, smile: -0.9, width: 0.9, teeth: 0, cheek: 0, blush: 0 },
  disbelief: { browL: 1, browR: -0.3, browTilt: 0.2, lid: 0.25, wide: 0.4, look: [0, 0], open: 0.3, smile: -0.2, width: 0.85, teeth: 0, cheek: 0, blush: 0 },
  thinking: { browL: 0.5, browR: -0.2, browTilt: 0.3, lid: 0.3, wide: 0, look: [0.6, 0.6], open: 0, smile: -0.15, width: 0.85, teeth: 0, cheek: 0, blush: 0 },
  holding: { browL: 0.5, browR: 0.5, browTilt: 0.6, lid: 0.1, wide: 0.6, look: [0, 0], open: 0, smile: 0, width: 0.6, teeth: 0, cheek: 1, blush: 0.7 },
  // v3 (EP21): deadpan and heavy-lidded, for the shopkeeper and the sales assistant
  bored: { browL: -0.15, browR: 0.1, browTilt: 0, lid: 0.55, wide: 0, look: [0.15, -0.1], open: 0, smile: -0.25, width: 0.95, teeth: 0, cheek: 0, blush: 0 },
  // v3 (EP21): soft and kind, for Nan
  warm: { browL: 0.3, browR: 0.3, browTilt: 0.45, lid: 0.3, wide: 0, look: [0, 0], open: 0.1, smile: 0.55, width: 1.05, teeth: 0.2, cheek: 0, blush: 0.3 },
};

export const mixFace = (a: Face, b: Face, k: number): Face => {
  const l = (x: number, y: number) => x + (y - x) * k;
  return {
    browL: l(a.browL, b.browL), browR: l(a.browR, b.browR), browTilt: l(a.browTilt, b.browTilt), lid: l(a.lid, b.lid), wide: l(a.wide, b.wide),
    look: [l(a.look[0], b.look[0]), l(a.look[1], b.look[1])], open: l(a.open, b.open), smile: l(a.smile, b.smile), width: l(a.width, b.width),
    teeth: l(a.teeth, b.teeth), cheek: l(a.cheek, b.cheek), blush: l(a.blush, b.blush),
  };
};

/** Arms and legs as angles in degrees. sh = [forward, out] at the shoulder, el = elbow bend; hip/knee the same for legs. */
export type Body = {
  lean: number; turn: number; headTurn: number; headTilt: number; headNod: number;
  shL: [number, number]; elL: number; shR: [number, number]; elR: number;
  hipL: [number, number]; knL: number; hipR: [number, number]; knR: number;
  handL?: 'open' | 'fist' | 'point'; handR?: 'open' | 'fist' | 'point';
  sit?: boolean; bounce?: number;
  // Whole-body acting (10 Nov). All default to 0, so older episodes look the same.
  spine?: number; // upper body bends forward (+) or back (-) at the waist, degrees; the legs stay planted
  side?: number; // upper body leans to its right (+) or left (-), degrees
  crouch?: number; // 0 straight .. 1 deep: knees bend and the hips drop, feet stay on the floor
  shrug?: number; // shoulders up (+1) or slumped down and forward (-1)
  sway?: number; // hips shift sideways, metres (weight onto one leg)
  twL?: number; twR?: number; // upper-arm twist, degrees: + turns the elbow's bend inward across the body (crossed arms, hands on head)
};
export const BODY: Body = { lean: 0, turn: 0, headTurn: 0, headTilt: 0, headNod: 0, shL: [0, 8], elL: 10, shR: [0, 8], elR: 10, hipL: [0, 3], knL: 0, hipR: [0, 3], knR: 0 };

const d2r = THREE.MathUtils.degToRad;

// ---------- Union Jack pin: a canvas texture, drawn once ----------
let flagTex: THREE.CanvasTexture | null = null;
const unionJack = () => {
  if (flagTex || typeof document === 'undefined') return flagTex;
  const c = document.createElement('canvas');
  c.width = 240; c.height = 240;
  const g = c.getContext('2d')!;
  g.fillStyle = '#012169'; g.fillRect(0, 0, 240, 240);
  g.save(); g.beginPath(); g.rect(30, 60, 180, 120); g.clip();
  g.lineCap = 'butt';
  g.strokeStyle = '#FFFFFF'; g.lineWidth = 22;
  g.beginPath(); g.moveTo(30, 60); g.lineTo(210, 180); g.moveTo(210, 60); g.lineTo(30, 180); g.stroke();
  g.strokeStyle = '#C8102E'; g.lineWidth = 8;
  g.beginPath(); g.moveTo(30, 60); g.lineTo(210, 180); g.moveTo(210, 60); g.lineTo(30, 180); g.stroke();
  g.restore();
  g.fillStyle = '#012169'; g.fillRect(0, 0, 240, 60); g.fillRect(0, 180, 240, 60); g.fillRect(0, 0, 30, 240); g.fillRect(210, 0, 30, 240);
  // the flag fills the round pin: redraw full-bleed so the circle crop shows the whole design
  const f = document.createElement('canvas'); f.width = 240; f.height = 240;
  const h = f.getContext('2d')!;
  h.drawImage(c, 30, 60, 180, 120, -30, 0, 300, 240);
  h.fillStyle = '#FFFFFF'; h.fillRect(0, 96, 240, 48); h.fillRect(96, 0, 48, 240);
  h.fillStyle = '#C8102E'; h.fillRect(0, 106, 240, 28); h.fillRect(106, 0, 28, 240);
  flagTex = new THREE.CanvasTexture(f);
  flagTex.colorSpace = THREE.SRGBColorSpace;
  return flagTex;
};

const Pin: React.FC<{ glow?: number }> = ({ glow = 0 }) => {
  const tex = unionJack();
  return (
    <group>
      {glow > 0.01 ? (
        <>
          <mesh position={[0, 0, -0.002]}>
            <circleGeometry args={[0.036 + 0.012 * glow, 32]} />
            <meshBasicMaterial color="#FFE27A" transparent opacity={0.7 * glow} toneMapped={false} />
          </mesh>
          <pointLight position={[0, 0, 0.05]} intensity={0.25 * glow} distance={0.18} color="#FFE27A" />
        </>
      ) : null}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.034, 0.034, 0.008, 32]} />
        <meshStandardMaterial color="#D9B45A" metalness={0.8} roughness={0.25} />
      </mesh>
      <mesh position={[0, 0, 0.0045]}>
        <circleGeometry args={[0.028, 32]} />
        <meshStandardMaterial map={tex ?? undefined} color={tex ? '#ffffff' : '#012169'} roughness={0.35} />
      </mesh>
    </group>
  );
};

// ---------- small helpers ----------
const Mat: React.FC<{ c: string; r?: number; m?: number }> = ({ c, r = 0.75, m = 0 }) => <meshStandardMaterial color={c} roughness={r} metalness={m} />;

/** A limb segment hanging down from its joint (length L, radius r). */
const Seg: React.FC<{ L: number; r: number; c: string; r2?: number }> = ({ L, r, c, r2 }) => (
  <mesh position={[0, -L / 2, 0]}>
    <capsuleGeometry args={[r2 ?? r, Math.max(0.001, L - 2 * r), 6, 14]} />
    <Mat c={c} />
  </mesh>
);

const Hand: React.FC<{ c: string; kind: 'open' | 'fist' | 'point'; side: 1 | -1 }> = ({ c, kind, side }) => (
  <group>
    <mesh scale={[1, 1.15, 0.7]} position={[0, -0.045, 0]}>
      <sphereGeometry args={[0.045, 16, 12]} />
      <Mat c={c} r={0.6} />
    </mesh>
    {/* thumb */}
    <mesh position={[side * -0.035, -0.035, 0.02]} rotation={[0, 0, side * 0.6]}>
      <capsuleGeometry args={[0.014, 0.03, 4, 8]} />
      <Mat c={c} r={0.6} />
    </mesh>
    {kind !== 'fist'
      ? [-0.022, -0.007, 0.008, 0.023].map((x, i) => (
          <mesh key={i} position={[x, kind === 'point' && i !== 1 ? -0.07 : -0.1 + Math.abs(x) * 0.3, kind === 'point' && i !== 1 ? 0.02 : 0]} rotation={[kind === 'point' && i !== 1 ? -1.4 : 0, 0, 0]}>
            <capsuleGeometry args={[0.0105, kind === 'point' && i !== 1 ? 0.02 : 0.045, 4, 8]} />
            <Mat c={c} r={0.6} />
          </mesh>
        ))
      : null}
  </group>
);

// ---------- the face ----------
const Eye: React.FC<{ x: number; f: Face; c: string; skin: string; side: 1 | -1 }> = ({ x, f, c, skin, side }) => {
  const R = 0.036 * (1 + 0.14 * f.wide);
  const tilt = f.browTilt;
  const smileLid = f.smile > 0.4 ? (f.smile - 0.4) * 1.6 : 0;
  const lid = THREE.MathUtils.clamp(f.lid - 0.1 * f.wide, 0, 1);
  const lx = f.look[0] * 0.45, ly = f.look[1] * 0.35;
  return (
    <group position={[x, 0, 0]}>
      <mesh>
        <sphereGeometry args={[R, 24, 18]} />
        <meshStandardMaterial color="#F7F4EE" roughness={0.25} />
      </mesh>
      <group rotation={[-ly, lx, 0]}>
        <mesh position={[0, 0, R * 1.003]}>
          <circleGeometry args={[R * 0.55, 24]} />
          <meshStandardMaterial color={c} roughness={0.3} />
        </mesh>
        <mesh position={[0, 0, R * 1.006]}>
          <circleGeometry args={[R * (0.27 - 0.08 * f.wide), 20]} />
          <meshStandardMaterial color="#0B0B0E" roughness={0.2} />
        </mesh>
        <mesh position={[R * 0.2, R * 0.22, R * 1.009]}>
          <circleGeometry args={[R * 0.1, 12]} />
          <meshBasicMaterial color="#FFFFFF" />
        </mesh>
      </group>
      {/* lids: caps of a slightly bigger sphere. The upper one grows down from the top pole as the eye shuts,
          the lower one up from the bottom; tilt turns them for angry (inner corner down) and worried (inner up). */}
      <group rotation={[0, 0, side * d2r(-12 * tilt)]}>
        <mesh>
          <sphereGeometry args={[R * 1.07, 28, 14, 0, Math.PI * 2, 0, Math.PI * (0.22 + 0.36 * lid)]} />
          <meshStandardMaterial color={skin} roughness={0.7} side={THREE.DoubleSide} />
        </mesh>
        <mesh rotation={[Math.PI, 0, 0]}>
          <sphereGeometry args={[R * 1.06, 28, 10, 0, Math.PI * 2, 0, Math.PI * (0.2 + 0.14 * Math.max(0, smileLid))]} />
          <meshStandardMaterial color={skin} roughness={0.7} side={THREE.DoubleSide} />
        </mesh>
      </group>
    </group>
  );
};

const Mouth: React.FC<{ f: Face; skin: string; shade: string }> = ({ f }) => {
  const geo = useMemo(() => {
    const w = 0.042 * f.width;
    const o = 0.006 + 0.05 * f.open;
    const s = f.smile * 0.02;
    const sh = new THREE.Shape();
    sh.moveTo(-w, s);
    sh.quadraticCurveTo(0, s * -0.4 + o * 0.25, w, s);
    sh.quadraticCurveTo(w * 0.55, -o - s * 0.2, 0, -o - Math.max(0, s) * 0.6);
    sh.quadraticCurveTo(-w * 0.55, -o - s * 0.2, -w, s);
    return new THREE.ShapeGeometry(sh, 16);
  }, [f.width, f.open, f.smile]);
  const teethGeo = useMemo(() => {
    const w = 0.038 * f.width;
    const s = f.smile * 0.02;
    const sh = new THREE.Shape();
    sh.moveTo(-w, s - 0.002);
    sh.quadraticCurveTo(0, s * -0.4 + (0.006 + 0.05 * f.open) * 0.25 - 0.002, w, s - 0.002);
    sh.lineTo(w * 0.9, s - 0.014);
    sh.quadraticCurveTo(0, s * -0.4 - 0.012, -w * 0.9, s - 0.014);
    return new THREE.ShapeGeometry(sh, 12);
  }, [f.width, f.open, f.smile]);
  return (
    <group>
      <mesh geometry={geo}>
        <meshStandardMaterial color="#3A1418" roughness={0.6} side={THREE.DoubleSide} />
      </mesh>
      {f.open > 0.4 ? (
        <mesh position={[0, -0.006 - 0.04 * f.open, 0.001]} scale={[f.width, 0.6, 1]}>
          <circleGeometry args={[0.022, 16]} />
          <meshStandardMaterial color="#C4545E" roughness={0.6} />
        </mesh>
      ) : null}
      {f.teeth > 0.05 && f.open > 0.05 ? (
        <mesh geometry={teethGeo} position={[0, 0, 0.002]}>
          <meshStandardMaterial color="#F4F0E6" roughness={0.35} transparent opacity={Math.min(1, f.teeth * 1.5)} side={THREE.DoubleSide} />
        </mesh>
      ) : null}
    </group>
  );
};

const Head: React.FC<{ look: Look; f: Face }> = ({ look, f }) => {
  const R = 0.118;
  const chin = look.chin ?? 0;
  const browY = (b: number) => Math.max(0.066, 0.064 + 0.016 * b + 0.01 * f.wide);
  const hairC = look.hairStyle === 'grey' ? '#B9B5AE' : look.hair;
  return (
    <group>
      {/* skull, jaw, ears, nose */}
      <mesh scale={[0.92, 1.08, 0.98]}>
        <sphereGeometry args={[R, 40, 32]} />
        <Mat c={look.skin} r={0.65} />
      </mesh>
      <mesh position={[0, -0.055, 0.02]} scale={[0.78, 0.6, 0.85]}>
        <sphereGeometry args={[R, 32, 24]} />
        <Mat c={look.skin} r={0.65} />
      </mesh>
      {[-1, 1].map((s) => (
        <mesh key={s} position={[s * 0.108, 0.0, -0.005]} scale={[0.45, 1, 0.7]}>
          <sphereGeometry args={[0.032, 16, 12]} />
          <Mat c={look.skinShade} r={0.7} />
        </mesh>
      ))}
      <mesh position={[0, 0.0, 0.118]} scale={[0.8, 1.1, 1]} rotation={[0.2, 0, 0]}>
        <sphereGeometry args={[0.022, 16, 12]} />
        <Mat c={look.skinShade} r={0.6} />
      </mesh>
      {/* cheeks: blush and the puffed hold */}
      {[-1, 1].map((s) => (
        <mesh key={`c${s}`} position={[s * (0.062 + 0.012 * f.cheek), -0.04, 0.078 + 0.022 * f.cheek]} scale={0.8 + 0.9 * f.cheek}>
          <sphereGeometry args={[0.028, 16, 12]} />
          <meshStandardMaterial color={new THREE.Color(look.skin).lerp(new THREE.Color('#E0707A'), 0.15 + 0.35 * f.blush)} roughness={0.7} />
        </mesh>
      ))}
      {/* eyes */}
      <group position={[0, 0.03, 0.098]}>
        <Eye x={-0.042} f={f} c={look.eyes} skin={look.skin} side={-1} />
        <Eye x={0.042} f={f} c={look.eyes} skin={look.skin} side={1} />
      </group>
      {/* brows */}
      {[-1, 1].map((s) => (
        <mesh key={`b${s}`} position={[s * 0.043, browY(s < 0 ? f.browL : f.browR), 0.118]} rotation={[0.15, 0, Math.PI / 2 + s * d2r(-16 * f.browTilt)]}>
          <capsuleGeometry args={[0.0075, 0.032, 4, 8]} />
          <Mat c={look.hairStyle === 'grey' ? '#8C877F' : look.hair} r={0.9} />
        </mesh>
      ))}
      {/* mouth, on the front of the jaw */}
      <group position={[0, -0.066 + 0.004 * f.cheek, 0.124 + 0.008 * f.cheek]} rotation={[0.32, 0, 0]} scale={1.15}>
        <Mouth f={f} skin={look.skin} shade={look.skinShade} />
      </group>
      {/* hair */}
      {look.hairStyle !== 'bald' ? (
        <group>
          <mesh position={[0, 0.03, -0.01]} scale={[0.97, look.hairStyle === 'quiff' ? 1.02 : 0.98, 1.0]}>
            <sphereGeometry args={[R * 1.04, 32, 24, 0, Math.PI * 2, 0, Math.PI * 0.29]} />
            <Mat c={hairC} r={0.95} />
          </mesh>
          <mesh position={[0, -0.005, -0.03]} scale={[0.96, 1, 0.92]}>
            <sphereGeometry args={[R * 1.05, 32, 24, Math.PI * 0.6, Math.PI * 0.8, 0.2, Math.PI * 0.5]} />
            <Mat c={hairC} r={0.95} />
          </mesh>
          {/* the back of the head (v3: characters are now seen from behind, e.g. the Narrator at the mic) */}
          <mesh position={[0, 0.0, -0.012]} scale={[0.97, 1.0, 0.98]}>
            <sphereGeometry args={[R * 1.045, 32, 24, Math.PI, Math.PI, 0.12, Math.PI * 0.52]} />
            <Mat c={hairC} r={0.95} />
          </mesh>
          {/* a soft hairline: tufts along the front edge instead of a hard brim */}
          {look.hairStyle !== 'grey' && look.hairStyle !== 'bun'
            ? [-0.085, -0.057, -0.028, 0, 0.028, 0.057, 0.085].map((x, i) => (
                <mesh key={`t${i}`} position={[x, (look.hairStyle === 'crop' ? 0.1 : 0.118) - Math.abs(x) * 0.25 + (i % 2) * 0.006, 0.075 - Math.abs(x) * 0.35]} scale={look.hairStyle === 'crop' ? [1, 0.55, 0.7] : [1.2, 0.8, 0.9]}>
                  <sphereGeometry args={[0.026, 12, 10]} />
                  <Mat c={hairC} r={0.95} />
                </mesh>
              ))
            : null}
          {look.hairStyle === 'quiff' ? (
            <mesh position={[0.01, 0.118, 0.055]} rotation={[0.6, 0, -0.15]} scale={[1.9, 0.85, 1.1]}>
              <sphereGeometry args={[0.042, 16, 12]} />
              <Mat c={hairC} r={0.95} />
            </mesh>
          ) : null}
          {look.hairStyle === 'bun' ? (
            <mesh position={[0, 0.12, -0.06]}>
              <sphereGeometry args={[0.05, 16, 12]} />
              <Mat c={hairC} r={0.95} />
            </mesh>
          ) : null}
        </group>
      ) : null}
      {chin > 0 ? (
        <group>
          <mesh position={[0, -0.112, 0.03]} scale={[0.72 + 0.12 * chin, 0.36 + 0.14 * chin, 0.78]}>
            <sphereGeometry args={[R, 28, 20]} />
            <Mat c={look.skin} r={0.65} />
          </mesh>
          {[-1, 1].map((s) => (
            <mesh key={`j${s}`} position={[s * 0.074, -0.072, 0.045]} scale={0.7 + 0.5 * chin}>
              <sphereGeometry args={[0.034, 16, 12]} />
              <Mat c={look.skin} r={0.65} />
            </mesh>
          ))}
        </group>
      ) : null}
      {look.headset ? (
        <group>
          <mesh position={[0, 0.02, -0.005]} rotation={[0, 0, 0]}>
            <torusGeometry args={[0.132, look.headset === 'phones' ? 0.012 : 0.007, 8, 32, Math.PI]} />
            <Mat c="#26272B" r={0.45} />
          </mesh>
          {[-1, 1].map((s) => (
            <mesh key={`h${s}`} position={[s * 0.128, 0.0, -0.005]} rotation={[0, 0, Math.PI / 2]}>
              <cylinderGeometry args={look.headset === 'phones' ? [0.05, 0.05, 0.04, 20] : [0.034, 0.034, 0.025, 16]} />
              <Mat c="#1C1D21" r={0.4} />
            </mesh>
          ))}
          {look.headset === 'boom' ? (
            <group position={[-0.13, -0.01, 0.0]} rotation={[0, -0.95, 0.35]}>
              <mesh position={[0, 0, 0.07]} rotation={[Math.PI / 2, 0, 0]}>
                <cylinderGeometry args={[0.004, 0.004, 0.14, 8]} />
                <Mat c="#26272B" />
              </mesh>
              <mesh position={[0, 0, 0.14]}>
                <sphereGeometry args={[0.012, 12, 10]} />
                <Mat c="#111215" />
              </mesh>
            </group>
          ) : null}
        </group>
      ) : null}
      {look.glasses ? (
        <group position={[0, 0.03, 0.135]} scale={look.glassesSize ?? 1}>
          {[-1, 1].map((s) => (
            <mesh key={s} position={[s * 0.042, 0, 0]}>
              <torusGeometry args={[0.03, 0.003, 8, 24]} />
              <Mat c="#2A2420" r={0.4} />
            </mesh>
          ))}
          <mesh>
            <boxGeometry args={[0.024, 0.004, 0.004]} />
            <Mat c="#2A2420" />
          </mesh>
        </group>
      ) : null}
    </group>
  );
};

// ---------- the whole person ----------
export const Person: React.FC<{
  look: Look; face: Face; body?: Partial<Body>; position?: [number, number, number]; rotationY?: number; scale?: number; pinGlow?: number;
  heldL?: React.ReactNode; heldR?: React.ReactNode; // props in the hands (clipboard, walking stick, envelope...)
}> = ({ look, face, body = {}, position = [0, 0, 0], rotationY = 0, scale = 1, pinGlow = 0, heldL, heldR }) => {
  const b: Body = { ...BODY, ...body };
  // stoop: bent back, rounded shoulders, the head lifted so the face still looks ahead, knees a little soft
  const st = look.stoop ?? 0;
  if (st) {
    b.spine = (b.spine ?? 0) + 30 * st; b.headNod = b.headNod - 24 * st; b.shrug = (b.shrug ?? 0) - 0.45 * st;
    b.crouch = Math.max(b.crouch ?? 0, 0.1 * st);
  }
  const H = look.height;
  const k = H / 1.75;
  const W = look.build;
  const LT = look.limbs ?? 1;
  const bel = look.belly ?? 0;
  const hs = look.head ?? 1;
  const legL = 0.82 * k * (look.legLen ?? 1), thigh = legL * 0.5, shin = legL * 0.5;
  const crA = b.sit ? 0 : 42 * (b.crouch ?? 0); // thigh forward / shin back, degrees
  const hipY = b.sit ? 0.46 : legL * Math.cos(d2r(crA)) + 0.04;
  const shr = b.shrug ?? 0;
  const torsoH = 0.5 * k;
  const shoulderY = torsoH * 0.92;
  const armUp = 0.29 * k * (look.armLen ?? 1), armLo = 0.27 * k * (look.armLen ?? 1);
  const bounce = b.bounce ?? 0;
  const LW = W * LT; // limb thickness
  const arm = (side: 1 | -1, sh: [number, number], el: number, hand: Body['handL'], tw = 0, held?: React.ReactNode) => (
    <group position={[side * (0.2 - 0.02 * Math.max(0, -shr)) * W, shoulderY + 0.035 * shr, 0.03 * Math.max(0, -shr)]} rotation={[d2r(-sh[0]), 0, d2r(side * sh[1])]}>
    <group rotation={[0, d2r(-side * tw), 0]}>
      <mesh>
        <sphereGeometry args={[0.058 * LW, 16, 12]} />
        <Mat c={look.jacket} />
      </mesh>
      <Seg L={armUp} r={0.05 * LW} c={look.jacket} />
      <mesh position={[0, -armUp, 0]}>
        <sphereGeometry args={[0.046 * LW, 14, 10]} />
        <Mat c={look.jacket} />
      </mesh>
      <group position={[0, -armUp, 0]} rotation={[d2r(-el), 0, 0]}>
        <Seg L={armLo} r={0.044 * LW} c={look.jacket} />
        <mesh position={[0, -armLo + 0.01, 0]}>
          <cylinderGeometry args={[0.047 * LW, 0.047 * LW, 0.03, 16]} />
          <Mat c={look.jacketTrim} />
        </mesh>
        <group position={[0, -armLo - 0.01, 0]}>
          <Hand c={look.skin} kind={hand ?? 'open'} side={side} />
          {held ?? null}
        </group>
      </group>
    </group>
    </group>
  );
  const leg = (side: 1 | -1, hip: [number, number], kn: number) => (
    <group position={[side * 0.095 * W, 0, 0]} rotation={[d2r(-(hip[0] + crA)), 0, d2r(side * hip[1])]}>
      <Seg L={thigh} r={0.07 * LW} c={look.legs} />
      <mesh position={[0, -thigh, 0]}>
        <sphereGeometry args={[0.062 * LW, 14, 10]} />
        <Mat c={look.legs} />
      </mesh>
      <group position={[0, -thigh, 0]} rotation={[d2r(kn + 2 * crA), 0, 0]}>
        <Seg L={shin} r={0.058 * LW} c={look.legs} />
        <group position={[0, -shin, 0.04]} rotation={[d2r(-crA), 0, 0]}>
          <mesh scale={[1, 0.6, 1.9]} position={[0, -0.01, 0]}>
            <sphereGeometry args={[0.055, 16, 12]} />
            <Mat c={look.shoes} r={0.5} />
          </mesh>
          <mesh position={[0, -0.035, 0]} scale={[1.05, 0.25, 2.0]}>
            <sphereGeometry args={[0.055, 16, 8]} />
            <Mat c={look.sole} r={0.6} />
          </mesh>
        </group>
      </group>
    </group>
  );
  return (
    <group position={position} rotation={[0, rotationY, 0]} scale={scale}>
      <group position={[b.sway ?? 0, hipY + bounce, 0]} rotation={[d2r(b.lean), d2r(b.turn), 0]}>
        {/* pelvis and legs */}
        <mesh scale={[1.25 * W, 0.7, 0.85 + 0.25 * bel]}>
          <sphereGeometry args={[0.13, 24, 16]} />
          <Mat c={look.legs} />
        </mesh>
        {leg(-1, b.hipL, b.knL)}
        {leg(1, b.hipR, b.knR)}
        <group rotation={[d2r(b.spine ?? 0), 0, d2r(-(b.side ?? 0))]}>
        {/* torso: the jacket over a top */}
        <mesh position={[0, torsoH * 0.5, 0]} scale={[1.08 * W, 1, 0.68 + 0.22 * bel]}>
          <capsuleGeometry args={[0.17, torsoH * 0.6, 8, 24]} />
          <Mat c={look.jacket} />
        </mesh>
        {/* belly: a round front in the top's colour, bulging between the open jacket */}
        {bel > 0 ? (
          <group>
            {/* the mass: jacket-coloured, so the silhouette swells low and round */}
            <mesh position={[0, torsoH * 0.34, 0.03 + 0.045 * bel]} scale={[1.08 * W, 0.95, 0.95]}>
              <sphereGeometry args={[0.17 * (0.85 + 0.35 * bel), 32, 24]} />
              <Mat c={look.jacket} />
            </mesh>
            {/* the shirt showing down the open front, stretched over it */}
            <mesh position={[0, torsoH * 0.37, 0.075 + 0.075 * bel]} scale={[0.58 * W, 1.05, 0.82]}>
              <sphereGeometry args={[0.135 * (0.85 + 0.4 * bel), 28, 20]} />
              <Mat c={look.top} />
            </mesh>
          </group>
        ) : null}
        {/* stoop: a rounded upper back */}
        {st > 0 ? (
          <mesh position={[0, shoulderY - 0.04, -0.06]} scale={[1.0 * W, 0.8, 0.75]}>
            <sphereGeometry args={[0.12 + 0.03 * st, 20, 14]} />
            <Mat c={look.jacket} />
          </mesh>
        ) : null}
        {/* open front showing the top */}
        <mesh position={[0, shoulderY - 0.035, 0.085]} rotation={[0.35, 0, 0]} scale={[1, 0.55, 0.35]}>
          <sphereGeometry args={[0.055, 20, 14]} />
          <Mat c={look.top} />
        </mesh>
        {/* collar */}
        <mesh position={[0, shoulderY + 0.02, 0]} rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.07, 0.025, 10, 24]} />
          <Mat c={look.collar === 'harrington' ? look.jacketTrim : look.jacket} />
        </mesh>
        {/* hem band */}
        <mesh position={[0, 0.06, 0]} scale={[1.08 * W, 1, 0.7 + 0.22 * bel]}>
          <cylinderGeometry args={[0.172, 0.172, 0.05, 24]} />
          <Mat c={look.jacketTrim} />
        </mesh>
        {look.pin ? (
          <group position={[-0.1 * W, torsoH * 0.78, 0.128]} rotation={[-0.08, -0.25, 0]}>
            <Pin glow={pinGlow} />
          </group>
        ) : null}
        {arm(-1, b.shL, b.elL, b.handL, b.twL ?? 0, heldL)}
        {arm(1, b.shR, b.elR, b.handR, b.twR ?? 0, heldR)}
        {/* neck and head */}
        <mesh position={[0, shoulderY + 0.06, 0]}>
          <cylinderGeometry args={[0.045 * Math.max(1, W * 0.9), 0.05 * Math.max(1, W * 0.9), 0.1, 16]} />
          <Mat c={look.skinShade} />
        </mesh>
        <group position={[0, shoulderY + 0.074 + 0.176 * hs, 0.01 + 0.03 * st]} rotation={[d2r(b.headNod), d2r(b.headTurn), d2r(b.headTilt)]} scale={1.38 * hs}>
          <Head look={look} f={face} />
        </group>
        </group>
      </group>
    </group>
  );
};
