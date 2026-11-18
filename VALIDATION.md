## Executable production checks

The new `tests/test_production.py` exercises real FFmpeg media for all three
modes: selected video excerpts, multiple personal clips, and an image storyboard
with a separate local narration track. Each produces a preview and a
1080×1920 H.264/AAC final, with full decode verification. Tests also cover
stale/wrong preview approval, no-overwrite behavior, unchanged source hashes,
bad segment ranges, missing files, path restrictions and paid-provider policy.
CI installs FFmpeg so these tests run rather than skip. Local runs without
FFmpeg explicitly skip the real-media group.

This does not validate optional upstream adapters, AI editorial quality,
voice models, GPU generation, face tracking or natural Turkish transcription.
The fixtures are synthetic and short; longer/natural footage needs review.

## Real local three-mode smoke test

The new `workbench.py` CLI is separately tested for input/file safety,
plan selection and actual FFmpeg MP4 renders. A dedicated GitHub Actions
`media-smoke` job generates its **own synthetic** recording, then creates
an edited video, a captioned vertical Short and a faceless vertical Short;
it probes each output's 1080x1920 dimensions.

```sh
python -m unittest discover -s tests -p test_workbench_cli.py -v
RUN_MEDIA_SMOKE=1 python -m unittest discover -s tests -p test_workbench_smoke.py -v
```

No third-party video, voice model, API call or private source is included.
These tests do **not** establish reliable "viral" editing or the compatibility
of every optional repo in the catalog.

## Optional free video stack and handoff checks

The tracked optional-tool registry, three-mode routing CLI and external
asset handoff can be validated without downloading models or invoking APIs:

```sh
python scripts/video_tool_stack.py list --json
python scripts/video_tool_stack.py plan --mode long-to-shorts
python scripts/video_tool_stack.py plan --mode faceless
python scripts/video_tool_stack.py plan --mode own-footage
python -m unittest discover -s tests -p 'test_video_tool_stack.py' -v
python -m unittest discover -s tests -p 'test_external_handoff.py' -v
```

The unit tests mock FFprobe for generated video handoffs and use a real
filesystem only for safe temporary dummy files. End-to-end generated media,
cloud/paid feature availability and third-party installer security are **not**
validated by these tests. See [reference/free-video-tool-stack.md](reference/free-video-tool-stack.md).

# Verified workflow

On 7 November 2026, a Windows run completed with Python 3.10, Node 26, FFmpeg 9, Chrome, and faster-whisper 1.2.1.

A locally synthesized English recording was converted to a 640×360 source video. Faster-whisper with the tiny.en model on CPU produced three utterances. The normal command entry points then completed:

1. `scripts/transcribe.py` produced word timestamps and energy envelopes.
2. `scripts/preflight.py` accepted the edit list.
3. `scripts/cuts.py` created three pieces and a 236-frame program.
4. `scripts/build.py audio video` generated audio and an exactly 236-frame preview.
5. `scripts/verify.py --all` transcribed both joins and flagged zero joins.
6. `scripts/render.mjs` rendered the full program through Chrome with two workers.
7. `scripts/sfx.py lib` generated all eight synthesized effects.
8. `scripts/mix.py` combined the rendered parts, voice, and a tick cue into a final MP4.
9. FFprobe confirmed 236 H.264 video frames at 1920×1080 with AAC audio. FFmpeg decoded the complete final file without reporting errors.

The final program lasts approximately 7.87 seconds. The mix measured −14.0 LUFS with a −1.0 dBTP true peak.

The scene was adapted from the template to display the actual transcript words. A real edit requires its own scene content in `scene/script.js`.

The two regression tests cover outward rounding of a fractional final frame and fading a single-frame audio piece at 120 fps.

This run used a short synthetic recording and the small English model. Natural speech, other languages, longer recordings, GPU configurations and other operating systems require their own checks. A human still reviews transcription accuracy, audible joins and the final picture.
