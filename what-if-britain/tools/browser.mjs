// Finds a headless Chromium: the cloud container's preinstalled one (either folder layout), else system Chrome.
import fs from 'node:fs';
export const findBrowser = () => {
  const pw = '/opt/pw-browsers';
  if (fs.existsSync(pw)) {
    for (const d of fs.readdirSync(pw).filter((d) => d.startsWith('chromium_headless_shell'))) {
      for (const p of [`${pw}/${d}/chrome-linux/headless_shell`, `${pw}/${d}/chrome-headless-shell-linux64/chrome-headless-shell`]) if (fs.existsSync(p)) return p;
    }
  }
  for (const p of ['/usr/bin/google-chrome', '/usr/bin/chromium']) if (fs.existsSync(p)) return p;
  return undefined;
};
