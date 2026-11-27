// Shared timings for the acting test (seconds). audio/acting_sfx.py reads this file's numbers too.
export const BEATS = {
  nanFill0: 0.6, nanLand: 2.6, glide1: 4.4, alfFill0: 5.6, alfPass: 7.0, alfLand: 9.0,
  sigh: 10.9, slump: 11.9, mateIn: 13.6, switch: 16.2, hope: 16.9,
};
export const LEN = 20.5;
// Thoughts: shown as POV text by the speaker's head. *word* = yellow.
export const THOUGHTS = [
  { who: 'nan', text: 'we moaned about *that*.', t0: 2.9, t1: 4.6, side: 1 },
  { who: 'lead', text: "hang on… that's *mine*?", t0: 7.2, t1: 8.8, side: -1 },
  { who: 'lead', text: 'seven and a half years… of my *whole* pay', t0: 9.6, t1: 11.7, side: -1 },
  { who: 'lead', text: "i'm never moving *out*.", t0: 12.2, t1: 13.9, side: -1 },
  { who: 'mate', text: 'just rent, *mate*.', t0: 14.6, t1: 16.0, side: -1 },
  { who: 'lead', text: 'wait. what *if*…', t0: 17.5, t1: 19.6, side: -1 },
];
