// Layout audit: at sampled times, finds visible cards ([data-box]) that overlap each other, cover a keep-out
// area ([data-keepout], e.g. the speaker's face) or sit closer than --margin px to the frame edge.
//
// usage: node scripts/audit.mjs URL [--every 0.5] [--at 3,7.5] [--margin 40]
import { ensureWebSocket, openPage, withParam } from './_cdp.mjs';

if (!ensureWebSocket()) await new Promise(() => {});

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(`--${k}`); return i >= 0 ? args[i + 1] : d; };
const URL0 = args[0];
if (!URL0 || URL0.startsWith('--')) { console.error('usage: node scripts/audit.mjs URL [--every 0.5] [--margin 40]'); process.exit(1); }
const MARGIN = +opt('margin', 40);

const page = await openPage({ width: 1920, height: 1080 });
await page.goto(withParam(URL0, 'still'));
const info = await page.evaluate('({ d: window.__scene.duration, missing: window.__scene.missing })');
const times = opt('at', null) ? opt('at').split(',').map(Number)
  : [...Array(Math.floor(info.d / +opt('every', 0.5)) + 1).keys()].map((i) => +(i * +opt('every', 0.5)).toFixed(3));

const problems = new Map();
for (const t of times) {
  await page.evaluate(`window.__scene.render(${t})`);
  const r = await page.evaluate(`(() => {
    const stage = document.querySelector('#stage'), st = stage.getBoundingClientRect(), W = +document.body.dataset.w || 1920, H = +document.body.dataset.h || 1080, s = st.width / W;
    const R = (e) => { const b = e.getBoundingClientRect(); return { x: (b.left - st.left) / s, y: (b.top - st.top) / s, w: b.width / s, h: b.height / s }; };
    const vis = (e) => { for (let n = e; n && n !== stage; n = n.parentElement) { const c = getComputedStyle(n); if (c.display === 'none' || c.visibility === 'hidden' || +c.opacity < 0.05) return false; } return true; };
    const name = (e) => e.id || e.className || e.tagName;
    const boxes = [...document.querySelectorAll('[data-box]')].filter(vis).map((e) => [name(e), R(e)]).filter(([, b]) => b.w > 2 && b.h > 2);
    const keep = [...document.querySelectorAll('[data-keepout]')].map(R);
    const hit = (a, b) => a.x < b.x + b.w - 4 && a.x + a.w > b.x + 4 && a.y < b.y + b.h - 4 && a.y + a.h > b.y + 4;
    const out = [];
    for (const [n, b] of boxes) {
      if (b.x < ${MARGIN} || b.y < ${MARGIN} || b.x + b.w > W - ${MARGIN} || b.y + b.h > H - ${MARGIN}) out.push('edge: ' + n);
      if (keep.some((k) => hit(b, k))) out.push('covers keep-out: ' + n);
    }
    for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) if (hit(boxes[i][1], boxes[j][1])) out.push('overlap: ' + boxes[i][0] + ' / ' + boxes[j][0]);
    return out;
  })()`);
  for (const p of r) { if (!problems.has(p)) problems.set(p, []); problems.get(p).push(t); }
}
page.close();
if (info.missing.length) console.log(`phrases not found: ${JSON.stringify(info.missing)}`);
for (const [p, ts] of problems) console.log(`${p}  at ${ts.length > 6 ? ts.slice(0, 3).join(', ') + ' … ' + ts.slice(-2).join(', ') : ts.join(', ')} s`);
console.log(`audit: ${times.length} moments, ${problems.size} problem(s)${info.missing.length ? ', missing phrases' : ''}`);
process.exit(problems.size || info.missing.length ? 1 : 0);
