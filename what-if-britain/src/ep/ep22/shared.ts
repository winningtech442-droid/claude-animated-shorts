// EP22 shared timing: line n's start and end from lines.json (tools/cast_voice.py), used by every shot file.
import lines from '../../episodes/ep22/lines.json';
const L = lines as { start: number; end: number }[];
export const S = (n: number) => L[n - 1].start;
export const E = (n: number) => L[n - 1].end;
export const O_T1 = S(8) - 0.05; // the cold open ends on the NAN jar, just before "And what if Britain..."
