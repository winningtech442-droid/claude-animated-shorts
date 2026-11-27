import { Look } from './Person';

// The page's recurring cast. The lead always wears the Union Jack pin.
export const CAST: Record<string, Look> = {
  lead: {
    name: 'Alfie', skin: '#E6B896', skinShade: '#D29F7E', hair: '#3B2618', hairStyle: 'quiff', eyes: '#3E6B8A',
    jacket: '#1F2F4F', jacketTrim: '#B3262E', top: '#EFE8DA', legs: '#B9A887', shoes: '#F4F2EC', sole: '#D9D4C8',
    height: 1.78, build: 1, pin: true, collar: 'harrington',
  },
  mate: {
    name: 'Mate', skin: '#8D5A3B', skinShade: '#7A4C31', hair: '#16110E', hairStyle: 'crop', eyes: '#3A2618',
    jacket: '#5E6B3A', jacketTrim: '#2E3320', top: '#8E9196', legs: '#22242A', shoes: '#2B2B2E', sole: '#E7E3DA',
    height: 1.82, build: 1.08, collar: 'hoodie',
  },
  nan: {
    name: 'Nan', skin: '#F0C7B0', skinShade: '#DDB09A', hair: '#BDB8B0', hairStyle: 'bun', eyes: '#5B6E5A',
    jacket: '#6E3352', jacketTrim: '#5A2843', top: '#F1E6D2', legs: '#6D6A66', shoes: '#4A3428', sole: '#3A2A20',
    height: 1.6, build: 0.98, glasses: true, collar: 'cardigan',
  },
};
