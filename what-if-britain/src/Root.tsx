import React from 'react';
import { Composition } from 'remotion';
import { CastSheet } from './CastSheet';
import { makeEpisode } from './engine/Episode';
import { demo } from './episodes/demo/episode';
import { setPreview } from './episodes/set-preview/episode';
import { ep20 } from './ep/ep20';
import { ep21 } from './ep/ep21/ep21';
import { ep22 } from './ep/ep22/ep22';
import { waitFonts } from './kit/fonts';
import { ActingTest } from './tests/ActingTest';
import { PoseLab } from './tests/PoseLab';
import { LEN as ACT_LEN } from './tests/actingBeats';

// v3 (27 Nov 2026): the posted v2 episodes were archived (scripts and facts in archive/episodes/).
// ep20 stays as the latest hand-built reference (src/ep/), demo and set-preview as examples of the shot engine
// (src/engine/) and its parts library (src/worlds/, src/props/). Add each new episode here. 30 fps, no motion blur.
const ENGINE_EXAMPLES = [demo, setPreview].map((ep) => ({ ep, ...makeEpisode(ep) }));

export const Root: React.FC = () => {
  waitFonts();
  return (
    <>
      <Composition id="CastSheet" component={CastSheet} durationInFrames={16} fps={30} width={1080} height={1920} />
      <Composition id="PoseLab" component={PoseLab} durationInFrames={1} fps={30} width={1080} height={1920} />
      <Composition id="ActingTest" component={ActingTest} durationInFrames={Math.round(ACT_LEN * 30)} fps={30} width={1080} height={1920} />
      <Composition id="ep22" component={ep22.Comp} durationInFrames={ep22.frames} fps={30} width={1080} height={1920} />
      <Composition id="ep21" component={ep21.Comp} durationInFrames={ep21.frames} fps={30} width={1080} height={1920} />
      <Composition id="ep20" component={ep20.Comp} durationInFrames={ep20.frames} fps={30} width={1080} height={1920} />
      {ENGINE_EXAMPLES.map(({ ep, Comp, frames }) => (
        <Composition key={ep.id} id={ep.id} component={Comp} durationInFrames={frames} fps={30} width={1080} height={1920} />
      ))}
    </>
  );
};
