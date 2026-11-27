import type { Episode, Word } from './types';

const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9£$%.']/g, '').replace(/\.$/, '');

/** Start time of the occ-th match of a phrase in the words (guide ch. 5: the single timing source). */
export const T = (words: Word[], phrase: string, occ = 0) => {
  const want = phrase.split(/\s+/).map(norm).filter(Boolean);
  let seen = 0;
  for (let i = 0; i + want.length <= words.length; i++) {
    if (want.every((w, k) => norm(words[i + k].text) === w)) {
      if (seen === occ) return words[i].start;
      seen++;
    }
  }
  throw new Error(`cue "${phrase}" (occurrence ${occ}) not found in words.json`);
};

/** Shot start times: a word cue cuts 0.2 s after the phrase starts; the first shot starts at 0. */
export const shotStarts = (ep: Episode) =>
  ep.shots.map((s, i) => (i === 0 ? 0 : typeof s.cue === 'number' ? s.cue : T(ep.words, s.cue, s.occ ?? 0) + 0.2));

export const duration = (ep: Episode) => ep.words[ep.words.length - 1].end + (ep.tail ?? 0.6);
