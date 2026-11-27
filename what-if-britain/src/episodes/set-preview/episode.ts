// Set preview (not a real episode): every new set, prop and the timeline switch from the 6 Nov set session, one shot each.
import type { Episode, Shot, V3, CamKey } from '../../engine/types';
import words from './words.json';

const cam = (p: V3, t: V3, fov: number, to?: V3): { from: CamKey; to: CamKey } => ({ from: { p, t, fov }, to: { p: to ?? p, t, fov } });
const A = (who: 'lead' | 'mate' | 'nan', at: V3, face: string, rotY = 0, pose: Record<string, unknown> = {}) =>
  ({ who, at, rotY, faces: [[0, face]] as [number, string][], poses: [[0, pose]] as any });

const S: Shot[] = [
  { id: 'P01', cue: 0, world: 'committee', worldArgs: { rate: 3.75, rateTo: 4, rateAt: [0.3, 1.2] }, cam: cam([0.8, 3.3, 7.4], [0, 1.2, 0.2], 40) },
  { id: 'P02', cue: 1.7, world: 'committee', worldArgs: { spin: [0.1, 0.9], rate: 4 }, enter: 'whip', cam: cam([-0.6, 2.6, 6.6], [0, 0.9, 0.6], 40) },
  { id: 'P03', cue: 3.4, world: 'committee', worldArgs: { spin: [0, 0.01], shake: 0.2, rate: 4 }, enter: 'cut', cam: cam([2.6, 2.4, 6.4], [-0.4, 1.0, 0.8], 40),
    actors: [A('lead', [2.4, 0, 2.6], 'smug', -0.5, { shR: [70, 20], elR: 60, handR: 'open' })] },
  { id: 'P04', cue: 5.1, world: 'street', worldArgs: { era: '1988', night: 0.55, boards: 6, slam: 0.05 }, enter: 'whip', cam: cam([6.5, 1.8, 5.2], [-5.0, 1.5, 0.4], 46),
    actors: [A('nan', [3.4, 0, 1.3], 'sad', 0.9)] },
  { id: 'P05', cue: 6.9, world: 'street', worldArgs: { era: '1975', night: 0.95 }, enter: 'cut', cam: cam([6.5, 1.8, 5.2], [-5.0, 1.8, 0.4], 46) },
  { id: 'P06', cue: 8.6, world: 'table', enter: 'fly', cam: cam([0.12, 0.26, 0.9], [0.03, 0.1, 0], 34),
    props: [{ kind: 'House', at: [-0.06, 0, 0.02], s: 0.9, args: { squash: 0, sale: true }, grow: { key: 'squash', from: 0, to: 0.6, t0: 0.2, t1: 1.2, round: false } },
      { kind: 'Dial', at: [0.13, 0.11, -0.1], s: 0.2, args: { value: 3.75 }, grow: { key: 'value', from: 3.75, to: 4, t0: 0.1, t1: 0.8, round: false } }] },
  { id: 'P07', cue: 10.3, world: 'kitchen', worldArgs: { meter: '£4.72' }, whatif: true, enter: 'cut', cam: cam([0.0, 1.55, 3.4], [0.0, 1.35, 0.4], 40),
    actors: [A('lead', [-0.5, 0, 0.4], 'shock', 0.2), A('mate', [0.55, 0, 0.4], 'happy', -0.3)] },
  { id: 'P08', cue: 12.0, world: 'shop', whatif: true, enter: 'whip', cam: cam([-0.9, 1.75, 4.6], [-0.3, 0.9, 0.9], 42),
    props: [{ kind: 'Trolley', at: [0.1, 0, 0.9], rot: [0, 0.5, 0], args: { n: 2 }, grow: { key: 'n', from: 2, to: 14, t0: 0.1, t1: 1.2 } }],
    actors: [A('lead', [-1.0, 0, 1.0], 'worried', 0.5)] },
];

export const setPreview: Episode = { id: 'SetPreview', title: 'Set preview', words, shots: S, hook: { text: 'WHAT IF POLITICIANS SET YOUR RATE?', until: 3 } };
