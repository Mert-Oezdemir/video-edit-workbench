/* A tiny built-in program so the template can be opened with ?demo before any footage exists.
 * Same shape as work/program.json: words are [start, end, word] in program seconds. */
(() => {
  const lines = [
    [0.6, 'This scene shows how the graphics follow the voice.'],
    [4.2, 'Every card appears on the word that is spoken.'],
    [10.6, 'First we transcribe the raw takes.'],
    [13.0, 'Then we cut on real word edges.'],
    [15.4, 'Then we animate and render.'],
    [20.6, 'The voice is measured, not heard.'],
    [23.0, 'We aim for minus fourteen LUFS.'],
  ];
  const words = [];
  for (const [t0, text] of lines) {
    let t = t0;
    for (const w of text.split(' ')) {
      const d = 0.12 + 0.045 * w.replace(/\W/g, '').length;
      words.push([+t.toFixed(3), +(t + d).toFixed(3), w]);
      t += d + 0.06;
    }
  }
  window.DEMO_PROGRAM = {
    fps: 30,
    duration: 27,
    frames: 27 * 30,
    words,
    chapters: [
      { title: 'Intro', time: 0 },
      { title: 'Workflow', time: 8.0 },
      { title: 'Sound', time: 18.2 },
    ],
  };
})();
