// Minimal headless Chrome driver over the DevTools protocol. No npm dependencies.
// Needs a global WebSocket (Node 22+, or Node 20/21 with --experimental-websocket: the scripts re-launch themselves).
import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

export function ensureWebSocket() {
  if (typeof globalThis.WebSocket !== 'undefined') return true;
  const r = spawn(process.execPath, ['--experimental-websocket', ...process.argv.slice(1)], { stdio: 'inherit' });
  r.on('close', (c) => process.exit(c ?? 1));
  return false;
}

export function findChrome() {
  const c = [
    process.env.CHROME,
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser',
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  ].filter(Boolean);
  const hit = c.find((p) => existsSync(p));
  if (!hit) throw new Error('Chrome not found. Set CHROME=/path/to/chrome');
  return hit;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export async function openPage({ width, height, dpr = 1 }) {
  const port = 9300 + Math.floor(Math.random() * 600);
  const prof = mkdtempSync(join(tmpdir(), 've-chrome-'));
  const chrome = spawn(findChrome(), [
    '--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`,
    `--window-size=${width},${height}`, '--hide-scrollbars', '--mute-audio', '--no-first-run', '--no-default-browser-check',
    '--autoplay-policy=no-user-gesture-required', '--disable-background-timer-throttling', '--disable-renderer-backgrounding',
    'about:blank',
  ], { stdio: 'ignore' });
  const close = () => { try { chrome.kill('SIGKILL'); } catch (e) {} try { rmSync(prof, { recursive: true, force: true }); } catch (e) {} };
  process.on('exit', close);

  let list = null;
  for (let i = 0; i < 120 && !list; i++) {
    await sleep(150);
    try { list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); } catch (e) {}
  }
  if (!list) throw new Error('Chrome did not start');
  const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener('open', r, { once: true }));
  let seq = 0;
  const waiting = new Map(), listeners = [];
  ws.addEventListener('message', (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && waiting.has(m.id)) { const { res, rej } = waiting.get(m.id); waiting.delete(m.id); m.error ? rej(new Error(m.error.message)) : res(m.result); }
    else if (m.method) listeners.forEach((f) => f(m));
  });
  const send = (method, params = {}) => new Promise((res, rej) => { const id = ++seq; waiting.set(id, { res, rej }); ws.send(JSON.stringify({ id, method, params })); });
  const evaluate = async (expression) => {
    const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text);
    return r.result.value;
  };
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: dpr, mobile: false });

  const goto = async (url) => {
    const loaded = new Promise((r) => listeners.push((m) => { if (m.method === 'Page.loadEventFired') r(); }));
    await send('Page.navigate', { url });
    await loaded;
    for (let i = 0; i < 300; i++) { if (await evaluate('!!(window.__scene && window.__sceneReady)')) break; await sleep(100); }
    if (!(await evaluate('!!window.__scene'))) throw new Error('the page has no window.__scene (is it a scene from the template?)');
    await evaluate('window.__sceneReady()');
  };
  const shot = async (quality = 95) => Buffer.from((await send('Page.captureScreenshot', { format: 'jpeg', quality, fromSurface: true })).data, 'base64');
  return { send, evaluate, goto, shot, close: () => { try { ws.close(); } catch (e) {} close(); } };
}

export function withParam(url, p) {
  return url + (url.includes('?') ? '&' : '?') + p;
}
