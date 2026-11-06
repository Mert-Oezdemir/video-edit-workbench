/* The scene: every beat is a tween on TL at a time taken from the spoken words.
 * Replace the demo beats below with the beats of your video. Keep the helpers.
 *   at('phrase')             time just before the phrase is said
 *   at('phrase', {end:true}) time just after the phrase ends
 *   at('phrase', {from: t})  search only after t (for words said more than once)
 *   cue(t, 'whoosh', -3)     sound effect at t, 3 dB under its default level
 */
window.buildScene = ({ TL, at, cue, chapters, duration, stage, still }) => {
  const $ = (s) => stage.querySelector(s);
  const IN = 'power3.out', OUT = 'power2.in', MOVE = 'power2.inOut';
  const hasVideo = !!$('#v').getAttribute('src');
  const css = (name) => getComputedStyle(document.body).getPropertyValue(name).trim();

  /* card in / out: rise 24 px and fade; visibility is handled by autoAlpha */
  const cardIn = (el, t, d = 0.7) => t != null && TL.fromTo(el, { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: d, ease: IN, immediateRender: false }, t);
  const cardOut = (el, t, d = 0.5) => t != null && TL.to(el, { autoAlpha: 0, y: -12, duration: d, ease: OUT }, t);
  TL.set(stage.querySelectorAll('.card'), { autoAlpha: 0 }, 0);

  /* subtle line texture when there is no video (lines, never radial glows) */
  if (!hasVideo) {
    const svg = $('#bgLines');
    let d = '';
    for (let y = 60; y < 1080; y += 60) d += `M0 ${y}H1920`;
    for (let x = 60; x < 1920; x += 60) d += `M${x} 0V1080`;
    svg.innerHTML = `<path d="${d}" stroke="rgba(255,255,255,0.035)" stroke-width="1"/>` +
      '<rect x="720" y="120" width="560" height="960" rx="18" fill="none" stroke="rgba(255,255,255,0.12)" stroke-dasharray="8 10"/>' +
      '<text x="1000" y="610" fill="rgba(255,255,255,0.25)" font-family="Inter, sans-serif" font-size="26" text-anchor="middle">speaker</text>';
  }

  /* ---------- transitions (reference/style.md, section 9) ----------
   * veil(a, z, …)  full-frame pane: closes from a, opens from z. Chapters close it 0.55 s before the cut,
   *                so the jump happens under the closed pane. Use veilText() for a section that is not a chapter.
   * blurDip(t)     a cut where the picture jumps.   darkDip(t)  a cut that removes a stretch and changes subject.
   * No sound on transitions unless the creator profile asks for it (TRANSITION_SOUND). */
  const TRANSITION_SOUND = false;
  const veil = (id, a, z, kick, title, subtitle = '', prog = '') => {
    const v = $('#veil').cloneNode(true);
    v.id = id;
    $('#veil').after(v);
    v.querySelector('.kick').textContent = kick;
    v.querySelector('.t1').textContent = title;
    v.querySelector('.t2').textContent = subtitle;
    if (prog) v.querySelector('.prog').innerHTML = prog; else v.querySelector('.prog').remove();
    TL.set(v, { autoAlpha: 0 }, 0);
    TL.set(v, { autoAlpha: 1 }, a);
    TL.fromTo(v.querySelector('.pane'), { clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0% 0 0)', duration: 0.45, ease: MOVE, immediateRender: false }, a);
    TL.fromTo(v.querySelector('.edge'), { x: 0, opacity: 1 }, { x: 1917, duration: 0.45, ease: MOVE, immediateRender: false }, a);
    TL.set(v.querySelector('.edge'), { opacity: 0 }, a + 0.45);
    TL.fromTo(v.querySelector('.inner'), { autoAlpha: 0, x: -30 }, { autoAlpha: 1, x: 0, duration: 0.5, ease: IN, immediateRender: false }, a + 0.2);
    TL.to(v.querySelector('.inner'), { autoAlpha: 0, x: 30, duration: 0.3, ease: OUT }, z - 0.32);
    TL.fromTo(v.querySelector('.pane'), { clipPath: 'inset(0 0% 0 0)' }, { clipPath: 'inset(0 0% 0 100%)', duration: 0.5, ease: MOVE, immediateRender: false }, z);
    TL.set(v, { autoAlpha: 0 }, z + 0.52);
    if (TRANSITION_SOUND) cue(a, 'soft-whoosh', -6);
  };
  const veilText = (id, a, z, kick, line, line2 = '') => veil(id, a, z, kick, line, line2);
  const video = $('#v');
  const dip = (t, blur, dark, tin, tout) => {
    if (t == null) return;
    TL.fromTo(video, { filter: 'blur(0px) brightness(1)' }, { filter: `blur(${blur}px) brightness(${1 - dark})`, duration: tin, ease: 'power2.in', immediateRender: false }, t - tin);
    TL.to(video, { filter: 'blur(0px) brightness(1)', duration: tout, ease: 'power2.out' }, t);
    TL.set(video, { filter: 'none' }, t + tout);   // no filter left on the video between dips (it costs every frame)
  };
  const blurDip = (t) => dip(t, 16, 0, 0.18, 0.32);
  const darkDip = (t) => dip(t, 18, 0.8, 0.32, 0.55);

  /* ---------- chapters: a veil for every chapter after the first, a chip for each ---------- */
  const VEIL = 1.5;   // seconds: about 0.55 s before the chapter cut to 0.95 s after it
  chapters.forEach((ch, i) => {
    const no = String(i + 1).padStart(2, '0');
    const chip = $('#chip').cloneNode(true);
    chip.id = `chip${i}`;
    TL.set(chip, { autoAlpha: 0 }, 0);
    chip.querySelector('.no').textContent = no;
    chip.querySelector('.tt').textContent = ch.title;
    $('#chip').after(chip);
    const end = i + 1 < chapters.length ? chapters[i + 1].time : duration;
    const shown = i === 0 ? ch.time + 0.6 : ch.time + VEIL - 0.4;
    cardIn(chip, shown, 0.6);
    cardOut(chip, Math.max(shown + 1, end - 0.6), 0.3);
    if (i === 0) return;

    const prog = chapters.map((c, k) => `<span class="${k === i ? 'on' : ''}">${String(k + 1).padStart(2, '0')}</span>`).join('<b></b>');
    veil(`veil${i}`, ch.time - 0.55, ch.time + 0.95, `Chapter ${no} / ${String(chapters.length).padStart(2, '0')}`, ch.title, ch.subtitle || '', prog);
  });
  // Examples, not used by the demo: a text veil before an inserted montage, and dips at two kinds of cut.
  //   veilText('veilClips', t0, t0 + 1.9, 'From the last video', "Let's watch some clips");
  //   blurDip(timeOfAJumpCut);  darkDip(timeOfATopicCut);

  /* ---------- lower third: once, early ---------- */
  const lower = $('#lower');
  TL.fromTo(lower, { autoAlpha: 0, x: -40 }, { autoAlpha: 1, x: 0, duration: 0.8, ease: IN, immediateRender: false }, at('This scene'));
  TL.to(lower, { autoAlpha: 0, x: -40, duration: 0.6, ease: OUT }, at('spoken', { end: true }) + 0.4);

  /* ---------- keyword card: one idea at a time, swapped on its word ---------- */
  const kw = $('#kw'), roll = kw.querySelector('.roll');
  const kwSay = (t, a, b) => {
    if (t == null) return;
    const el = document.createElement('div');
    el.innerHTML = `<div class="t1">${a}</div>` + (b ? `<div class="t2">${b}</div>` : '');
    roll.appendChild(el);
    TL.set(el, { autoAlpha: 0 }, 0);
    const prev = roll.children[roll.children.length - 2];
    if (prev) TL.to(prev, { yPercent: -60, autoAlpha: 0, duration: 0.45, ease: OUT }, t);
    TL.fromTo(el, { yPercent: 60, autoAlpha: 0 }, { yPercent: 0, autoAlpha: 1, duration: 0.6, ease: IN, immediateRender: false }, t + (prev ? 0.12 : 0));
    return el;
  };
  cardIn(kw, at('graphics'));
  kwSay(at('graphics'), 'Graphics', 'follow the voice');
  kwSay(at('Every card'), 'On the word', 'not before it');
  cardOut(kw, chapters[1] ? chapters[1].time - 0.4 : null);

  /* ---------- steps: the list grows as each step is said ---------- */
  const steps = $('#steps');
  cardIn(steps, at('First'));
  [['transcribe', 'Transcribe'], ['cut', 'Cut on word edges'], ['animate', 'Animate'], ['render', 'Render']].forEach(([w, label], i) => {
    const row = document.createElement('div');
    row.className = 'row';
    row.innerHTML = `<span class="n">${String(i + 1).padStart(2, '0')}</span><span>${label}</span>`;
    steps.appendChild(row);
    const t = at(w, { from: chapters[1] ? chapters[1].time : 0 });
    TL.fromTo(row, { autoAlpha: 0, x: -16, height: 0, paddingTop: 0, paddingBottom: 0 },
      { autoAlpha: 1, x: 0, height: 'auto', paddingTop: 16, paddingBottom: 16, duration: 0.5, ease: IN, immediateRender: false }, t);
    TL.fromTo(row.querySelector('.n'), { color: css('--label') }, { color: css('--accent'), duration: 0.3, immediateRender: false }, t);
    if (i) TL.to(steps.querySelectorAll('.row .n')[i - 1], { color: css('--label'), duration: 0.3 }, t);
    cue(t, 'tick');
  });
  TL.set(steps.querySelectorAll('.row'), { autoAlpha: 0, height: 0, paddingTop: 0, paddingBottom: 0 }, 0);
  cardOut(steps, chapters[2] ? chapters[2].time - 0.4 : null);

  /* ---------- sound chapter: keyword with a drawn underline, then a counter ---------- */
  const s3 = chapters[2] ? chapters[2].time : 0;
  const tm = at('measured', { from: s3 });
  if (tm != null) {
    cardIn(kw, tm);
    const el = kwSay(tm, '<span class="u">Measured,<i></i></span>', 'not heard');
    TL.to(el.querySelector('.u > i'), { scaleX: 1, duration: 0.5, ease: IN }, at('heard', { from: s3 }));
  }
  const counter = $('#counter'), num = counter.querySelector('.num'), tc = at('minus', { from: s3 });
  if (tc != null) {
    cardIn(counter, tc);
    cue(tc, 'pop');
    const o = { v: 0 };
    TL.fromTo(o, { v: 0 }, { v: -14, duration: 1.2, ease: 'power2.out', immediateRender: false,
      onUpdate: () => { num.textContent = Math.round(o.v) === 0 ? '0' : `−${Math.abs(Math.round(o.v))}`; } }, tc + 0.3);
    TL.fromTo(counter.querySelector('.bar > i'), { scaleX: 0 }, { scaleX: 0.72, duration: 1.2, ease: 'power2.out', immediateRender: false }, tc + 0.3);
  }
};
