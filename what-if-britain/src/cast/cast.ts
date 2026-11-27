import { Look } from './Person';

// The page's recurring cast. The lead always wears the Union Jack pin (the timeline switch).
// v3 (27 Nov 2026, approved): Mate heavy-set, Nan tiny and stooped with huge glasses; the Booth's Producer and Narrator.
export const CAST: Record<string, Look> = {
  lead: {
    name: 'Alfie', skin: '#E6B896', skinShade: '#D29F7E', hair: '#3B2618', hairStyle: 'quiff', eyes: '#3E6B8A',
    jacket: '#1F2F4F', jacketTrim: '#B3262E', top: '#EFE8DA', legs: '#B9A887', shoes: '#F4F2EC', sole: '#D9D4C8',
    height: 1.78, build: 1, pin: true, collar: 'harrington',
  },
  mate: {
    name: 'Mate', skin: '#8D5A3B', skinShade: '#7A4C31', hair: '#16110E', hairStyle: 'crop', eyes: '#3A2618',
    jacket: '#5E6B3A', jacketTrim: '#2E3320', top: '#8E9196', legs: '#22242A', shoes: '#2B2B2E', sole: '#E7E3DA',
    height: 1.82, build: 1.32, collar: 'hoodie',
    belly: 1, limbs: 1.18, head: 0.9, chin: 0.7,
  },
  nan: {
    name: 'Nan', skin: '#F0C7B0', skinShade: '#DDB09A', hair: '#BDB8B0', hairStyle: 'bun', eyes: '#5B6E5A',
    jacket: '#6E3352', jacketTrim: '#5A2843', top: '#F1E6D2', legs: '#6D6A66', shoes: '#4A3428', sole: '#3A2A20',
    height: 1.46, build: 0.95, glasses: true, collar: 'cardigan',
    stoop: 0.85, head: 1.1, glassesSize: 1.45,
  },
  producer: {
    name: 'Producer', skin: '#C98E6E', skinShade: '#B57B5C', hair: '#2E211B', hairStyle: 'bun', eyes: '#3D2B20',
    jacket: '#D9A441', jacketTrim: '#B8862D', top: '#2B2F3A', legs: '#3C4A66', shoes: '#F1EEE6', sole: '#D6D1C6',
    height: 1.66, build: 0.95, collar: 'cardigan', headset: 'boom',
  },
  narrator: {
    name: 'Narrator', skin: '#E8C4A4', skinShade: '#D3AD8D', hair: '#6B5B4E', hairStyle: 'crop', eyes: '#4A5A6A',
    jacket: '#6B5A45', jacketTrim: '#574937', top: '#EDE7DA', legs: '#3B3A40', shoes: '#3A2C22', sole: '#2A201A',
    height: 1.8, build: 1.02, collar: 'suit', headset: 'phones',
  },
};
