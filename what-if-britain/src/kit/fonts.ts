// Load fonts before any canvas texture draws text (guide ch. 4).
import '@fontsource/inter/600.css';
import '@fontsource/inter/800.css';
import '@fontsource/jetbrains-mono/500.css';
import { continueRender, delayRender } from 'remotion';
let gate: number | null = null;
export const waitFonts = () => {
  if (gate !== null || typeof document === 'undefined') return;
  gate = delayRender('fonts');
  Promise.all([document.fonts.load('600 40px Inter'), document.fonts.load('800 40px Inter'), document.fonts.load('500 40px "JetBrains Mono"')]).then(() => continueRender(gate!));
};
