// Text drawn onto a canvas texture (price tags, headlines, screens). Cached by key, so each texture is drawn once.
// Fonts must already be loaded (kit/fonts.ts holds the render until they are).
import * as THREE from 'three';

const cache = new Map<string, THREE.CanvasTexture>();

export type TextSpec = {
  w: number; h: number; bg: string;
  lines: { text: string; x: number; y: number; size: number; color: string; weight?: number; font?: 'Inter' | 'JetBrains Mono'; align?: CanvasTextAlign }[];
  border?: string; draw?: (g: CanvasRenderingContext2D) => void;
};

export const textTexture = (key: string, s: TextSpec) => {
  const hit = cache.get(key);
  if (hit || typeof document === 'undefined') return hit ?? null;
  const c = document.createElement('canvas');
  c.width = s.w; c.height = s.h;
  const g = c.getContext('2d')!;
  g.fillStyle = s.bg; g.fillRect(0, 0, s.w, s.h);
  s.draw?.(g);
  for (const l of s.lines) {
    g.font = `${l.weight ?? 700} ${l.size}px ${l.font === 'JetBrains Mono' ? '"JetBrains Mono"' : 'Inter'}`;
    g.fillStyle = l.color; g.textAlign = l.align ?? 'center'; g.textBaseline = 'middle';
    g.fillText(l.text, l.x, l.y);
  }
  if (s.border) { g.strokeStyle = s.border; g.lineWidth = Math.max(4, s.w / 80); g.strokeRect(0, 0, s.w, s.h); }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  // only cache once the fonts are in, so no texture is stuck with a fallback face
  if (document.fonts.check('700 40px Inter') && document.fonts.check('500 40px "JetBrains Mono"')) cache.set(key, t);
  return t;
};
