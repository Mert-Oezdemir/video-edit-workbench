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
