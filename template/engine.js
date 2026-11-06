/* Scene engine: one GSAP timeline driven by the program clock.
 *
 * Preview:  the program video plays with its sound; the timeline follows video.currentTime.
 * Render:   ?still — nothing plays; render.mjs calls window.__scene.render(t) for every frame.
 * Keys:     Space play/pause · ←/→ 5 s · R restart · M mute effects
 * URL:      ?t=12.5 freeze at 12.5 s · ?src=FILE program video (default ../work/proxy.mp4, "none" for no video)
 *           ?demo built-in demo program (no project needed) · ?still render mode · ?nohud hide the timecode
 *
 * script.js defines window.buildScene(api) and adds tweens to api.TL at times from api.at('spoken phrase').
 */
(() => {
  const Q = new URLSearchParams(location.search);
  const STILL = Q.has('still'), DEMO = Q.has('demo');
  const body = document.body;
  const W = +body.dataset.w || 1920, H = +body.dataset.h || 1080;
  const stage = document.querySelector('#stage');
  const video = document.querySelector('#v');

  /* ---- stage: fixed design size, scaled to the window ---- */
  stage.style.width = W + 'px';
  stage.style.height = H + 'px';
  const fit = () => {
    const s = Math.min(innerWidth / W, innerHeight / H);
    stage.style.transform = `translate(${(innerWidth - W * s) / 2}px, ${(innerHeight - H * s) / 2}px) scale(${s})`;
  };
  addEventListener('resize', fit);
  fit();

  const TL = gsap.timeline({ paused: true });
  const SFX = [], missing = [], ASSETS = [], frameHooks = [];
  let PROGRAM = null, duration = 0, words = [], normWords = [];

  const norm = (s) => s.toLocaleLowerCase().normalize('NFC').replace(/[^\p{L}\p{N}]+/gu, '');

  /* at('phrase'): time just before the first word of the phrase is spoken (lead 0.1 s).
   * Options: { from: seconds to search after, end: true for the end of the phrase's last word, lead }.
   * A phrase that is not found is recorded in window.__scene.missing (render.mjs refuses to render then). */
  function at(phrase, opt = {}) {
    const want = phrase.split(/\s+/).map(norm).filter(Boolean);
    const from = opt.from ?? 0, lead = opt.lead ?? 0.1;
    for (let i = 0; i + want.length <= normWords.length; i++) {
      if (words[i][0] < from) continue;
      let ok = true;
      for (let k = 0; k < want.length && ok; k++) ok = normWords[i + k] === want[k] || (k === want.length - 1 && normWords[i + k].startsWith(want[k]));
      if (ok) return opt.end ? words[i + want.length - 1][1] + 0.05 : Math.max(0, words[i][0] - lead);
    }
    missing.push(phrase);
    return null;
  }

  /* cue(t, 'whoosh', gainDb): a sound effect at program time t. Same clock as the picture. */
  function cue(t, name, gain = 0) {
    if (t == null) return;
    SFX.push({ t: +t.toFixed(3), name, gain });
  }

  /* ---- preview sound: effects play live through WebAudio from ./sfx/<name>.wav ---- */
  let actx = null, muted = Q.has('mute');
  const buffers = {};
  async function loadSfx() {
    if (STILL || !SFX.length) return;
    actx = new AudioContext();
    for (const name of new Set(SFX.map((c) => c.name))) {
      try {
        const r = await fetch(`sfx/${name}.wav`);
        if (r.ok) buffers[name] = await actx.decodeAudioData(await r.arrayBuffer());
      } catch (e) { /* missing effect file: the preview stays silent, the mix still has it */ }
    }
  }
  function playCue(c) {
    if (muted || !actx || !buffers[c.name]) return;
    if (actx.state === 'suspended') actx.resume();
    const src = actx.createBufferSource(), g = actx.createGain();
    src.buffer = buffers[c.name];
    g.gain.value = Math.pow(10, (c.gain || 0) / 20);
    src.connect(g).connect(actx.destination);
    src.start();
  }

  /* ---- clock ---- */
  let clock = 0, last = performance.now(), playing = false, prevClock = 0;
  const hasVideo = () => video && video.src && !video.dataset.none;

  function apply(t) {
    // At least 0.1 ms: a paused timeline that is still at 0 does not render a seek to 0, so the TL.set(…, 0)
    // calls that hide later cards never ran and every card showed on the first frame (the one YouTube shows).
    TL.seek(Math.max(1e-4, Math.min(t, TL.duration() || t)), false);
    frameHooks.forEach((f) => f(t));
  }

  function tick(now) {
    const dt = (now - last) / 1000;
    last = now;
    if (playing) {
      if (hasVideo()) {
        const vt = video.currentTime;
        if (video.paused || video.seeking) clock = vt;
        else if (Math.abs(vt - clock) > 0.25) clock = vt;
        else clock += dt + (vt - clock) * 0.03;   // follow the video smoothly: currentTime alone is jittery
      } else {
        clock += dt;
      }
      if (clock >= duration) { clock = duration; playing = false; if (hasVideo()) video.pause(); }
      for (const c of SFX) if (c.t > prevClock && c.t <= clock) playCue(c);
    }
    prevClock = clock;
    apply(clock);
    hud();
    requestAnimationFrame(tick);
  }

  function play() {
    playing = !playing;
    if (hasVideo()) playing ? video.play() : video.pause();
  }
  function seek(t) {
    clock = prevClock = Math.max(0, Math.min(duration, t));
    if (hasVideo()) video.currentTime = clock;
    apply(clock);
  }

  /* ---- render mode: one exact frame per call ---- */
  async function render(t) {
    playing = false;
    if (hasVideo()) {
      video.pause();
      if (Math.abs(video.currentTime - t) > 0.0005) {
        await new Promise((res) => { video.addEventListener('seeked', res, { once: true }); video.currentTime = t; });
      }
      if (video.readyState < 2) await new Promise((res) => video.addEventListener('canplay', res, { once: true }));
    }
    await Promise.all(ASSETS);
    clock = t;
    apply(t);
    return true;
  }

  /* ---- HUD (preview only) ---- */
  const hudEl = document.querySelector('#hud');
  function hud() {
    if (!hudEl || STILL || Q.has('nohud')) return;
    const m = Math.floor(clock / 60), s = (clock % 60).toFixed(2).padStart(5, '0');
    hudEl.textContent = `${m}:${s} / ${(duration / 60) | 0}:${String(Math.round(duration % 60)).padStart(2, '0')}` +
      (missing.length ? `   ·   ${missing.length} phrase(s) not found: ${missing.slice(0, 3).join(' | ')}` : '') +
      (playing ? '' : '   ·   Space to play');
  }

  addEventListener('keydown', (e) => {
    if (e.code === 'Space') { e.preventDefault(); play(); }
    else if (e.code === 'ArrowRight') seek(clock + 5);
    else if (e.code === 'ArrowLeft') seek(clock - 5);
    else if (e.code === 'KeyR') seek(0);
    else if (e.code === 'KeyM') muted = !muted;
  });

  /* ---- boot ---- */
  async function loadProgram() {
    if (DEMO) return window.DEMO_PROGRAM;
    try {
      const r = await fetch(Q.get('program') || '../work/program.json', { cache: 'no-store' });
      if (r.ok) return await r.json();
    } catch (e) { /* no project yet */ }
    return window.DEMO_PROGRAM;
  }

  (async () => {
    PROGRAM = await loadProgram();
    words = (PROGRAM.words || []).map((w) => [w[0], w[1], w[2]]);
    normWords = words.map((w) => norm(w[2]));
    duration = PROGRAM.duration || (PROGRAM.frames / PROGRAM.fps) || 30;
    const src = Q.get('src') || (PROGRAM === window.DEMO_PROGRAM ? 'none' : '../work/proxy.mp4');
    if (src === 'none') { video.dataset.none = '1'; video.removeAttribute('src'); video.style.display = 'none'; }
    else {
      video.src = src;
      video.muted = STILL;
      ASSETS.push(new Promise((res) => (video.readyState >= 1 ? res() : video.addEventListener('loadedmetadata', res, { once: true }))));
    }
    if (document.fonts) ASSETS.push(document.fonts.ready);

    window.buildScene({ TL, at, cue, words, chapters: PROGRAM.chapters || [], duration, W, H, stage, ASSETS,
      onFrame: (f) => frameHooks.push(f), still: STILL });
    if (TL.duration() < duration) TL.set({}, {}, duration);   // the timeline spans the whole program

    window.__scene = { render, SFX, missing, duration, TL, fps: PROGRAM.fps || 30 };
    window.__sceneReady = () => Promise.all(ASSETS);
    await loadSfx();
    const t0 = Q.has('t') ? +Q.get('t') : 0;
    if (STILL) { await render(t0); return; }
    seek(t0);
    requestAnimationFrame((n) => { last = n; tick(n); });
  })();
})();
