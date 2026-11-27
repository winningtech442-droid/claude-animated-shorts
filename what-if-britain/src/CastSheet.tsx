import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { ThreeCanvas } from '@remotion/three';
import { Person, FACES, BODY } from './cast/Person';
import { CAST } from './cast/cast';

// Frame i (0..11): the lead's face in each expression. 12: full body of the lead, 13: the three together.
const NAMES = Object.keys(FACES);
export const CastSheet: React.FC = () => {
  const f = useCurrentFrame();
  const close = f < NAMES.length;
  const face = FACES[close ? NAMES[f] : 'happy'];
  const cam = close ? { position: [0.03, 1.66, 1.05] as [number, number, number], fov: 26 } : f === 12 ? { position: [0, 1.0, 3.6] as [number, number, number], fov: 40 } : { position: [0, 1.0, f === 14 ? 7.6 : f === 15 ? 4.2 : 5.2] as [number, number, number], fov: 40 };
  return (
    <AbsoluteFill style={{ background: 'linear-gradient(#D9E6F2, #B8C8D8)' }}>
      <ThreeCanvas width={1080} height={1920} camera={{ ...cam, near: 0.01, far: 100 }} onCreated={({ camera }) => camera.lookAt(0, close ? 1.63 : 0.95, 0)}>
        <ambientLight intensity={0.55} />
        <hemisphereLight args={['#FFF4E6', '#7A8AA0', 0.6]} />
        <directionalLight position={[1.5, 3, 2.5]} intensity={1.6} />
        <directionalLight position={[-2, 1.5, -1]} intensity={0.5} color="#BFD4FF" />
        <mesh rotation={[-Math.PI / 2, 0, 0]}>
          <circleGeometry args={[6, 48]} />
          <meshStandardMaterial color="#C9C3B8" roughness={1} />
        </mesh>
        {f === 15 ? (
          <>
            <Person look={CAST.mate} face={FACES.neutral} position={[-0.55, 0, 0]} rotationY={Math.PI / 2} />
            <Person look={CAST.nan} face={FACES.neutral} position={[0.55, 0, 0]} rotationY={Math.PI / 2} />
          </>
        ) : f === 14 ? (
          <>
            <Person look={CAST.producer} face={FACES.worried} position={[-1.5, 0, -0.4]} rotationY={0.35} />
            <Person look={CAST.mate} face={FACES.disbelief} position={[-0.75, 0, -0.1]} rotationY={0.3} body={{ shL: [10, 12], elL: 80, handL: 'fist' }} />
            <Person look={CAST.lead} face={FACES.shock} body={{ shL: [40, 30], elL: 30, shR: [40, 30], elR: 30 }} />
            <Person look={CAST.nan} face={FACES.smug} position={[0.72, 0, -0.1]} rotationY={-0.3} />
            <Person look={CAST.narrator} face={FACES.neutral} position={[1.5, 0, -0.4]} rotationY={-0.35} />
          </>
        ) : f < 13 ? (
          <Person look={CAST.lead} face={face} body={f === 12 ? { shR: [20, 35], elR: 70, shL: [0, 10], elL: 15, headTilt: 6 } : {}} />
        ) : (
          <>
            <Person look={CAST.mate} face={FACES.disbelief} position={[-0.75, 0, -0.1]} rotationY={0.3} body={{ shL: [10, 12], elL: 80, handL: 'fist' }} />
            <Person look={CAST.lead} face={FACES.shock} body={{ shL: [40, 30], elL: 30, shR: [40, 30], elR: 30 }} />
            <Person look={CAST.nan} face={FACES.smug} position={[0.72, 0, -0.1]} rotationY={-0.3} />
          </>
        )}
      </ThreeCanvas>
      <div style={{ position: 'absolute', top: 90, width: '100%', textAlign: 'center', font: '800 64px Inter', color: '#1B2433' }}>
        {close ? NAMES[f].toUpperCase() : f === 12 ? 'LEAD' : f === 14 ? 'PRODUCER · MATE · ALFIE · NAN · NARRATOR' : f === 15 ? 'SIDE: MATE · NAN' : 'MATE · LEAD · NAN'}
      </div>
    </AbsoluteFill>
  );
};
