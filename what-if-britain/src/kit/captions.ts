type Wd = { text: string; start: number; end: number };
export const buildPages = (WS: Wd[]) => {
  const pages: { words: number[]; start: number; end: number }[] = []; let cur: number[] = [];
  const flush = () => { if (cur.length) pages.push({ words: cur, start: WS[cur[0]].start, end: WS[cur[cur.length - 1]].end }); cur = []; };
  WS.forEach((w, i) => {
    if (cur.length) {
      const prev = WS[cur[cur.length - 1]];
      const len = cur.map((k) => WS[k].text).join(" ").length + 1 + w.text.length;
      if (cur.length >= 4 || len > 22 || /[.?!"]$/.test(prev.text) || (/,$/.test(prev.text) && cur.length >= 2) || w.start - prev.end > 0.3) flush();
    }
    cur.push(i);
  });
  flush(); return pages;
};
// show page while t in [start-0.05, nextStart-0.05); hide 0.45 s after its end if the next page is >0.7 s away;
// spoken words white, upcoming ~45% grey, 4 px white underline under the current word; 0.1 s fade in.
