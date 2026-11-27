// Studio demo: a short North Sea oil teaser that exercises every world type, all three transitions,
// expressions, props and the big-number card. Not a real episode (it is under 60 s).
import type { Episode } from '../../engine/types';
import words from './words.json';

export const demo: Episode = {
  id: 'Demo',
  title: 'Studio demo',
  words,
  shots: [
    {
      id: 'S1', cue: 0, world: 'kitchen', worldArgs: { meter: '£4.72', alarm: true }, line: 'Your energy bill',
      cam: { from: { p: [-0.3, 1.5, 3.6], t: [0.9, 1.3, -0.2], fov: 44 }, to: { p: [0.1, 1.5, 3.0], t: [1.0, 1.32, -0.2], fov: 42 } },
      exitInto: [1.6, 1.5, -0.85],
      actors: [{ who: 'lead', at: [0.55, 0, 0.35], rotY: -0.35, faces: [[0, 'neutral'], [0.5, 'shock']],
        poses: [[0, {}], [0.45, { shL: [40, 25], elL: 70, shR: [40, 25], elR: 70, lean: -5, headTurn: 35 }]] }],
    },
    {
      id: 'S2', cue: 'going up again', world: 'table', enter: 'fly', line: 'going up again',
      cam: { from: { p: [0.26, 0.2, 0.36], t: [0, 0.04, 0], fov: 34 }, to: { p: [0.16, 0.14, 0.26], t: [0, 0.05, 0], fov: 34 }, move: 'fast' },
      props: [
        { kind: 'CoinStack', at: [0, 0, 0], s: 2.2, args: { n: 3 }, grow: { key: 'n', from: 3, to: 22, t0: 0.1, t1: 1.0 } },
        { kind: 'Note', at: [-0.17, 0.001, 0.08], rot: [0, 0.4, 0], s: 1.3, args: { value: '20' } },
        { kind: 'Coin', at: [0.12, 0.002, 0.1], s: 2.2 },
      ],
    },
    {
      id: 'S3', cue: 'In 1975', world: 'street', worldArgs: { night: 0.3 }, enter: 'whip', line: 'In 1975, Britain struck oil. Norway did too.',
      cam: { from: { p: [-0.6, 1.6, 6.2], t: [-0.4, 1.45, 1], fov: 38 }, to: { p: [-0.4, 1.55, 5.0], t: [-0.4, 1.5, 1], fov: 38 } },
      exitInto: [-0.4, 2.2, 1.6],
      actors: [
        { who: 'lead', at: [-1.0, 0.1, 1.0], rotY: 0.25, faces: [[0, 'happy']], poses: [[0, {}], [0.3, { shR: [150, 20], elR: 10, handR: 'point' }]] },
        { who: 'mate', at: [0.4, 0.1, 1.1], rotY: -0.3, faces: [[0, 'neutral'], [1.2, 'disbelief']], poses: [[0, { shL: [10, 12], elL: 80, handL: 'fist' }]] },
      ],
      props: [{ kind: 'Newspaper', at: [-0.4, 2.2, 1.6], s: 1.8, from: 0.15, args: { headline: 'OIL FOUND', sub: 'North Sea, 1975' } }],
    },
    {
      id: 'S4', cue: 'But Norway', world: 'bank', worldArgs: { name: 'THE OIL FUND' }, enter: 'fly', line: 'But Norway saved it.',
      cam: { from: { p: [0, 1.7, 15], t: [0, 4.2, 1], fov: 46 }, to: { p: [0, 2.0, 9.5], t: [0, 4.6, 1], fov: 44 }, move: 'fast' },
    },
    {
      id: 'S5', cue: 'Today its fund', world: 'floor', worldArgs: { board: '$2.2TN', boardSub: 'NORWAY OIL FUND' }, enter: 'cut', line: 'Today its fund is worth over two trillion dollars.',
      cam: { from: { p: [0, 1.7, 4.2], t: [0, 2.3, -3.8], fov: 46 }, to: { p: [0, 1.9, 2.2], t: [0, 2.5, -3.8], fov: 42 } },
      number: { text: '$2.2 trillion', sub: "Norway's oil fund, June 2026", at: 1.1 },
    },
    {
      id: 'S6', cue: 'So where', world: 'street', worldArgs: { night: 0.6 }, enter: 'whip', line: 'So where did ours go?',
      cam: { from: { p: [0.15, 1.78, 2.5], t: [0, 1.72, 1], fov: 30 }, to: { p: [0.05, 1.76, 2.05], t: [0, 1.72, 1], fov: 30 } },
      actors: [{ who: 'lead', at: [0, 0.1, 1.0], faces: [[0, 'thinking'], [0.7, 'disbelief']], poses: [[0, { shL: [30, 30], elL: 60, shR: [30, 30], elR: 60, handL: 'open', handR: 'open' }]] }],
    },
  ],
};
