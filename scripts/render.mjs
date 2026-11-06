// Frame-exact render of a scene page in headless Chrome, piped into ffmpeg. Parallel workers, resumable.
//
// usage:
//   node scripts/render.mjs URL --out out/frames [--workers 4] [--dpr 2] [--from 0] [--to END] [--crf 18]
//   node scripts/render.mjs URL --stills out/stills --at 3.5,12,40.2        (check frames as JPG)
//
// The page must be a scene from the template: ?still is added, and every frame is prepared with
// window.__scene.render(t). The stage size comes from the page (1920x1080 -> 3840x2160 at --dpr 2).
// Each slice is written to part_<i>.mp4; a slice that already exists is skipped, so a stopped render resumes.
// sfx.json (the effect cues of the scene) is written next to the parts for mix.py.
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ensureWebSocket, openPage, withParam } from './_cdp.mjs';

if (!ensureWebSocket()) await new Promise(() => {});

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(`--${k}`); return i >= 0 ? args[i + 1] : d; };
const URL0 = args[0];
if (!URL0 || URL0.startsWith('--')) { console.error('usage: node scripts/render.mjs URL --out DIR [--workers 4] [--dpr 2]'); process.exit(1); }
const OUT = opt('out', null), STILLS = opt('stills', null), DPR = +opt('dpr', 2), CRF = opt('crf', '18');
const WORKERS = +opt('workers', 4), WORKER = opt('worker', null);
const url = withParam(URL0, 'still');

async function pageInfo() {
  const p = await openPage({ width: 640, height: 360 });
  await p.goto(url);
  const info = await p.evaluate(`({ w: +document.body.dataset.w || 1920, h: +document.body.dataset.h || 1080,
    fps: window.__scene.fps || 30, duration: window.__scene.duration, missing: window.__scene.missing, sfx: window.__scene.SFX })`);
  p.close();
  return info;
}

/* ---------- stills ---------- */
if (STILLS) {
  const info = await pageInfo();
  mkdirSync(STILLS, { recursive: true });
  const p = await openPage({ width: info.w, height: info.h, dpr: +opt('dpr', 1) });
  await p.goto(url);
  for (const t of opt('at', '0').split(',').map(Number)) {
    await p.evaluate(`window.__scene.render(${t})`);
    await p.evaluate('new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)))');
    const f = join(STILLS, `t${t.toFixed(2)}.jpg`);
    writeFileSync(f, await p.shot(92));
    console.log(f);
  }
  p.close();
  process.exit(0);
}

if (!OUT) { console.error('--out DIR is required'); process.exit(1); }
mkdirSync(OUT, { recursive: true });
const planPath = join(OUT, 'plan.json');

/* ---------- coordinator ---------- */
if (WORKER === null) {
  const info = await pageInfo();
  if (info.missing && info.missing.length) {
    console.error(`the scene has phrases that were not found in the words: ${JSON.stringify(info.missing)}`);
    console.error('fix them (or remove the beats) before rendering');
    process.exit(3);
  }
  const fps = info.fps, total = Math.round(info.duration * fps);
  const f0 = Math.round(+opt('from', 0) * fps), f1 = Math.min(total, Math.round(+opt('to', info.duration) * fps));
  const nSlices = Math.max(1, Math.min(WORKERS * 4, Math.ceil((f1 - f0) / 60)));
  const per = Math.ceil((f1 - f0) / nSlices);
  const slices = [...Array(nSlices).keys()].map((i) => [f0 + i * per, Math.min(f1, f0 + (i + 1) * per)]).filter(([a, b]) => b > a);
  writeFileSync(planPath, JSON.stringify({ url, fps, dpr: DPR, w: info.w, h: info.h, crf: CRF, slices }, null, 1));
  writeFileSync(join(OUT, 'sfx.json'), JSON.stringify(info.sfx || []));
  console.log(`render: ${f1 - f0} frames (${((f1 - f0) / fps).toFixed(2)} s) at ${info.w * DPR}x${info.h * DPR}, ${slices.length} slices, ${WORKERS} workers`);
  const t0 = Date.now();
  const runOne = (i) => new Promise((res) => {
    const k = spawn(process.execPath, [...process.execArgv, fileURLToPath(import.meta.url), URL0, '--out', OUT, '--worker', String(i)], { stdio: 'inherit' });
    k.on('close', (c) => res(c ?? 1));
  });
  const codes = slices.map(() => null);
  let next = 0;
  const lane = async () => {
    while (next < slices.length) {
      const i = next++;
      if (existsSync(join(OUT, `part_${i}.mp4`))) { codes[i] = 0; continue; }
      let c = 1;
      for (let k = 0; k < 3 && c !== 0; k++) { if (k) console.log(`slice ${i}: retry ${k}`); c = await runOne(i); }
      codes[i] = c;
    }
  };
  await Promise.all([...Array(Math.min(WORKERS, slices.length))].map(lane));
  const bad = codes.filter((c) => c).length;
  console.log(`${bad ? bad + ' slice(s) failed' : 'all slices done'} in ${((Date.now() - t0) / 60000).toFixed(1)} min -> ${OUT}`);
  process.exit(bad ? 1 : 0);
}

/* ---------- worker: one slice ---------- */
const P = JSON.parse(readFileSync(planPath, 'utf8'));
const wi = +WORKER, [a, b] = P.slices[wi];
let beat = Date.now();
setInterval(() => { if (Date.now() - beat > 90000) { console.error(`slice ${wi}: no progress for 90 s`); process.exit(4); } }, 5000).unref();

const page = await openPage({ width: P.w, height: P.h, dpr: P.dpr });
await page.goto(P.url);
const tmp = join(OUT, `part_${wi}.tmp.mp4`);
const ff = spawn('ffmpeg', [
  '-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(P.fps), '-c:v', 'mjpeg', '-i', '-',
  // Chrome's JPEG is full-range BT.601; video platforms expect limited-range BT.709
  '-vf', 'scale=in_range=full:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709,format=yuv420p',
  '-c:v', 'libx264', '-preset', 'medium', '-crf', String(P.crf), '-profile:v', 'high', '-g', String(P.fps * 2),
  '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv',
  '-r', String(P.fps), '-an', tmp,
], { stdio: ['pipe', 'inherit', 'inherit'] });

const n = b - a, t0 = Date.now();
for (let i = 0; i < n; i++) {
  const t = (a + i) / P.fps + 0.0005;   // half a millisecond into the frame: a seek never lands on the previous frame
  await page.evaluate(`window.__scene.render(${t.toFixed(5)})`);
  await page.evaluate('new Promise((r) => { let k = 0; const f = () => (++k >= 2 ? r() : requestAnimationFrame(f)); requestAnimationFrame(f); setTimeout(r, 400); })');
  const buf = await page.shot(96);
  beat = Date.now();
  if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  if (i % 150 === 0 || i === n - 1) {
    const rate = (i + 1) / ((Date.now() - t0) / 1000);
    console.log(`slice ${wi}: ${i + 1}/${n} · ${rate.toFixed(1)} fps · ~${((n - i - 1) / rate / 60).toFixed(1)} min left`);
  }
}
ff.stdin.end();
const code = await new Promise((r) => ff.on('close', r));
page.close();
if (code !== 0) { console.error(`slice ${wi}: ffmpeg exited ${code}`); process.exit(5); }
renameSync(tmp, join(OUT, `part_${wi}.mp4`));
process.exit(0);
