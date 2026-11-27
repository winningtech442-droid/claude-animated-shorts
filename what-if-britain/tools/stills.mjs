// tools/stills.mjs
// usage: node tools/stills.mjs <outDir> <CompositionId> <t1> <t2> ...   (times in seconds)
// One bundle, many renderStill calls. Don't use a <Freeze>-based contact-sheet composition: it shows stale WebGL frames.
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";
const [outDir, id, ...times] = process.argv.slice(2);
import { findBrowser } from "./browser.mjs";
const hs = findBrowser();
const opts = { browserExecutable: hs, chromiumOptions: { gl: "swangle" } };
fs.mkdirSync(outDir, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id, ...opts });
for (const t of times) {
  const frame = Math.min(composition.durationInFrames - 1, Math.round(Number(t) * composition.fps));
  const output = `${outDir}/t${Number(t).toFixed(2).padStart(7, "0")}.jpg`;
  await renderStill({ composition, serveUrl, frame, output, imageFormat: "jpeg", jpegQuality: 85, ...opts });
}
console.log(`${times.length} stills -> ${outDir}`);
