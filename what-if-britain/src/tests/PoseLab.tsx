// Pose lab: one still, several poses side by side, to tune arm shapes quickly.
import React from 'react';
import { AbsoluteFill } from 'remotion';
import { ThreeCanvas } from '@remotion/three';
import { Person, FACES, BODY, Body } from '../cast/Person';
import { CAST } from '../cast/cast';
export const LAB: Partial<Body>[] = [
  { shL: [30, -6], elL: 100, twL: 70, shR: [36, -6], elR: 95, twR: 70, handL: 'fist', handR: 'fist' },
  { shL: [95, 28], elL: 120, twL: 55, shR: [95, 28], elR: 120, twR: 55 },
  { shL: [120, 22], elL: 115, twL: 40, shR: [120, 22], elR: 115, twR: 40 },
  { shL: [80, 40], elL: 135, twL: 70, shR: [80, 40], elR: 135, twR: 70 },
];
export const PoseLab: React.FC = () => (
  <AbsoluteFill style={{ background: '#111' }}>
    <ThreeCanvas width={1080} height={1920} camera={{ position: [0, 1.2, 6.2], fov: 38, near: 0.05, far: 50 }} onCreated={({ camera }) => camera.lookAt(0, 1.1, 0)}>
      <ambientLight intensity={0.6} /><directionalLight position={[1, 3, 4]} intensity={1.4} />
      {LAB.map((b, i) => (
        <Person key={i} look={i < 2 ? CAST.mate : CAST.lead} face={FACES.neutral} body={{ ...BODY, ...b }} position={[-1.15 + i * 0.78, 0, 0]} rotationY={0.25} />
      ))}
    </ThreeCanvas>
  </AbsoluteFill>
);
