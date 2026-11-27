import type { Body } from '../cast/Person';

export type V3 = [number, number, number];
export type CamKey = { p: V3; t: V3; fov: number };
export type Word = { text: string; start: number; end: number };

/** A character in a shot. Keys are in shot-local seconds. */
export type Actor = {
  who: 'lead' | 'mate' | 'nan';
  at: V3; rotY?: number; scale?: number;
  faces?: [number, string][]; // [time, face name from FACES]
  poses?: [number, Partial<Body>][]; // [time, body pose]; numbers ease between keys
};

/** A prop in a shot: pops in at `from` (seconds), optionally moves between t0 and t1. */
export type PropCue = {
  kind: 'Coin' | 'CoinStack' | 'Note' | 'PriceTag' | 'Newspaper' | 'ChartScreen' | 'Meter' | 'Barrel' | 'Dial' | 'House' | 'SaleBoard' | 'Trolley' | 'Tea' | 'Phone' | 'GasJar' | 'JarShelf' | 'Calendar' | 'Scones' | 'Jumper';
  at: V3; rot?: V3; s?: number; args?: Record<string, unknown>;
  from?: number; move?: { to: V3; t0: number; t1: number; ease?: 'inOut' | 'drop' }; // drop = slam down with a bounce
  grow?: { key: string; from: number; to: number; t0: number; t1: number; round?: boolean }; // animate one numeric arg (stack height: rounded; dial value or squash: round: false)
};

/** One picture. `cue` = the phrase it cuts on (or a time in seconds). */
export type Shot = {
  id: string; cue: string | number; occ?: number; line?: string;
  world: 'street' | 'bank' | 'shop' | 'kitchen' | 'floor' | 'table' | 'committee' | 'sea' | 'rig' | 'cavern' | 'shore';
  worldArgs?: Record<string, unknown>;
  cam: { from: CamKey; to: CamKey; move?: 'drift' | 'fast' | 'hold' };
  enter?: 'cut' | 'whip' | 'fly'; // how we arrive in this shot
  exitInto?: V3; // where the camera dives when the NEXT shot enters by 'fly' (default: this shot's target)
  actors?: Actor[]; props?: PropCue[];
  number?: { text: string; sub?: string; at?: number }; // the one big-number card
  whatif?: boolean; // the alternate timeline: signature grade, a crack on the first what-if shot, Alfie's pin glows (script-rules 6)
};

export type Episode = { id: string; title: string; words: Word[]; shots: Shot[]; captions?: boolean; tail?: number;
  hook?: { text: string; until?: number } }; // the 3-7 word question on screen for the first 3 s (script-rules 3)
