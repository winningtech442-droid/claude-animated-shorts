// The Bank's committee room: wood panels, a long table, nine high-backed chairs and the rate dial on the wall.
// Generic: no crest, no real portraits, no faces. Never an opening frame (script-rules 3): something always moves.
//   spin  [t0, t1]  local seconds: the nine chairs swivel from the table round to face the camera
//   shake t0        local seconds: every chair shakes "no" (for "Not one of them is a politician")
//   rate / rateTo / rateAt [t0, t1]: the wall dial's needle moves from rate to rateTo
import React from 'react';
import { B, Bg, Cyl, Pane } from './kit';
import { Dial } from '../props';

type V3 = [number, number, number];
const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const inOut = (u: number) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2);

/** Chair seats sit around the table: 4 down each long side, 1 at the head (the chair nearest the dial). */
export const CHAIRS: { at: V3; face: number }[] = [
  ...[-1.8, -0.6, 0.6, 1.8].map((x) => ({ at: [x, 0, -0.15] as V3, face: 0 })),
  ...[-1.8, -0.6, 0.6, 1.8].map((x) => ({ at: [x, 0, 1.75] as V3, face: Math.PI })),
  { at: [-3.1, 0, 0.8] as V3, face: Math.PI / 2 },
];
export const COMMITTEE = { dial: [0, 2.15, -1.38] as V3, head: CHAIRS[8].at, table: [0, 0.78, 0.8] as V3 };

const Chair: React.FC<{ at: V3; yaw: number }> = ({ at, yaw }) => (
  <group position={at} rotation={[0, yaw, 0]}>
    <B p={[0, 0.48, 0]} s={[0.56, 0.08, 0.52]} c="#5B1F24" r={0.6} />
    <B p={[0, 1.0, -0.24]} s={[0.56, 1.0, 0.08]} c="#5B1F24" r={0.6} />
    <B p={[0, 1.52, -0.24]} s={[0.6, 0.06, 0.1]} c="#3A2418" />
    <Cyl p={[0, 0.24, 0]} r={0.04} h={0.44} c="#2B2F36" m={0.6} rough={0.3} />
    <B p={[0, 0.03, 0]} s={[0.5, 0.04, 0.08]} c="#2B2F36" />
    <B p={[0, 0.03, 0]} s={[0.08, 0.04, 0.5]} c="#2B2F36" />
  </group>
);

export const Committee: React.FC<{ t: number; lt?: number; spin?: [number, number]; shake?: number; rate?: number; rateTo?: number; rateAt?: [number, number]; dim?: number }> = ({
  lt = 0, spin, shake, rate = 3.75, rateTo, rateAt = [0.2, 0.9], dim = 0,
}) => {
  const sk = spin ? inOut(clamp((lt - spin[0]) / Math.max(0.01, spin[1] - spin[0]))) : 0;
  const shakeK = shake === undefined ? 0 : clamp(1 - Math.abs(lt - shake - 0.35) / 0.35);
  const r = rateTo === undefined ? rate : rate + (rateTo - rate) * inOut(clamp((lt - rateAt[0]) / Math.max(0.01, rateAt[1] - rateAt[0])));
  const panel = '#6E4A2E';
  return (
    <group>
      <Bg color="#1C1410" />
      <hemisphereLight args={['#FFE9CC', '#3A2A1E', 0.55 * (1 - dim * 0.5)]} />
      <ambientLight intensity={0.25} />
      <directionalLight position={[2.5, 5, 5]} intensity={1.2 * (1 - dim * 0.4)} color="#FFE2BC" />
      <pointLight position={[0, 2.6, 0.8]} intensity={7} distance={8} color="#FFD8A8" />
      {/* floor, back wall with panels, side walls, ceiling */}
      <B p={[0, -0.05, 1.5]} s={[9, 0.1, 7]} c="#4A2E22" />
      <B p={[0, 1.6, -1.5]} s={[9, 3.2, 0.1]} c={panel} />
      {Array.from({ length: 7 }).map((_, i) => (
        <group key={i} position={[-3.6 + i * 1.2, 0, -1.43]}>
          <B p={[0, 0.65, 0]} s={[1.0, 0.9, 0.03]} c="#7E5838" />
          {i !== 3 ? <B p={[0, 2.1, 0]} s={[1.0, 1.5, 0.03]} c="#7E5838" /> : null}
        </group>
      ))}
      <B p={[0, 1.15, -1.42]} s={[9, 0.06, 0.05]} c="#C9A45C" m={0.6} r={0.3} />
      {[-4.5, 4.5].map((x) => <B key={x} p={[x, 1.6, 1.5]} s={[0.1, 3.2, 7]} c="#644228" />)}
      <B p={[0, 3.2, 1.5]} s={[9, 0.1, 7]} c="#E9DFC9" />
      {/* tall windows on the right wall */}
      {[0.2, 2.2].map((z) => <group key={z} position={[4.44, 1.7, z]} rotation={[0, -Math.PI / 2, 0]}><Pane p={[0, 0, 0]} w={0.9} h={1.9} lit={0.55} frame="#E9DFC9" /></group>)}
      {/* the long table */}
      <B p={[0, 0.76, 0.8]} s={[4.6, 0.08, 1.4]} c="#3E2618" r={0.35} />
      <B p={[0, 0.81, 0.8]} s={[4.4, 0.01, 1.2]} c="#2E5A3E" r={0.9} />
      {[[-2.0, 0.3], [2.0, 0.3], [-2.0, 1.3], [2.0, 1.3]].map(([x, z], i) => <B key={i} p={[x, 0.38, z]} s={[0.12, 0.74, 0.12]} c="#2E1C12" />)}
      {/* nine papers and water glasses on the table */}
      {CHAIRS.slice(0, 8).map((c, i) => (
        <group key={i}>
          <B p={[c.at[0], 0.82, c.at[2] + (c.face ? -0.4 : 0.4)]} s={[0.24, 0.005, 0.32]} c="#F2EEE4" />
          <Cyl p={[c.at[0] + 0.22, 0.88, c.at[2] + (c.face ? -0.45 : 0.45)]} r={0.035} h={0.12} c="#CFE3EA" rough={0.1} />
        </group>
      ))}
      {/* the chairs: face the table, swivel round to the camera on `spin`, shake on `shake` */}
      {CHAIRS.map((c, i) => {
        const toCam = 0; // the chair model faces +z (the camera) at yaw 0
        const base = c.face;
        const yaw = base + (toCam - base) * sk + Math.sin((lt - (shake ?? 0)) * 38 + i) * 0.22 * shakeK;
        return <Chair key={i} at={c.at} yaw={yaw} />;
      })}
      {/* the rate dial on the back wall */}
      <group position={COMMITTEE.dial}>
        <Dial value={r} s={1.25} label="BANK RATE" />
      </group>
    </group>
  );
};
