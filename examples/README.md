# Örnekler / Sample workflows

The examples include **text files only**. No third-party copyrighted videos, credentials, model weights or downloads are bundled. Use a separate project directory; do not commit user recordings.

## Faceless: usable with FFmpeg only

```sh
python workbench.py init examples-project
cp examples/faceless/script.txt examples-project/src/script.txt
python workbench.py faceless --project examples-project --script src/script.txt
```

Windows PowerShell: `Copy-Item examples/faceless/script.txt examples-project/src/script.txt`. Result: `examples-project/out/faceless.mp4` plus .srt/.ass and .json. The no-narration example is **silent** by design. Add own images and licensed narration to enrich it.

## Long → Shorts

Copy your *authorized* local video to `examples-project/src/recording.mp4`, together with its correct `recording.srt`; then:

```sh
python workbench.py shorts --project examples-project --input src/recording.mp4 --srt src/recording.srt --minimum 3 --maximum 50 --count 2 --plan-only
# Review examples-project/out/recording-shorts-plan.json
python workbench.py shorts --project examples-project --input src/recording.mp4 --srt src/recording.srt --selections out/recording-shorts-plan.json --burn-captions
```

The included `shorts/sample.srt` is **illustrative** and does not match your own recording; do not blindly add it to unrelated video. Plans are editable JSON with `clips: [{start, end, title}]`; timings are seconds.

## Own footage

```sh
python workbench.py edit --project examples-project --input src/recording.mp4 --format portrait
```

For automatic silence trimming: add `--remove-silence` (no SRT retiming in quick mode). To review the cut list without encoding: add `--plan-only`.

## Synthetic 5-second media (for local testing)

If FFmpeg is installed, you may generate **your own synthetic** MP4:

```sh
ffmpeg -f lavfi -i "testsrc2=size=320x568:rate=30" -f lavfi -i "sine=frequency=440:sample_rate=44100" -t 5 -c:v libx264 -c:a aac examples-project/src/recording.mp4
```

Copy `examples/shorts/sample.srt` to `examples-project/src/recording.srt` for that synthetic test (it is *timing demonstration*, not a truthful speech transcript). Run `shorts` with `--minimum 1 --maximum 4` on this file. Review video and audio before any real production.

For full manual advanced precision, read [low-token.md](../reference/low-token.md) and [creative-tools.md](../reference/creative-tools.md).
