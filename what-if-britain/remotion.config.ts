import { Config } from "@remotion/cli/config";
import fs from "node:fs";
const pw = "/opt/pw-browsers";  // preinstalled headless Chromium in the cloud container
const cands = fs.existsSync(pw) ? fs.readdirSync(pw).filter((d) => d.startsWith("chromium_headless_shell")).flatMap((d) => [`${pw}/${d}/chrome-linux/headless_shell`, `${pw}/${d}/chrome-headless-shell-linux64/chrome-headless-shell`]) : [];
const hs = [...cands, '/usr/bin/google-chrome'].find((p) => fs.existsSync(p));
if (hs) Config.setBrowserExecutable(hs);
Config.setChromiumOpenGlRenderer("swangle");
Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(92);
