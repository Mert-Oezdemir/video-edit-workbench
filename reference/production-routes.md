# Video production routes / Video üretim yolları

Start with [editorial intake](editorial-intake.md). Identify the available material, the intended audience and the deliverable. Pick a primary route below and add only the steps that solve an actual need. In `work/NOTES.md`, record the route, the planned outputs, evidence for any product claims and the next review artifact. A project can use a route's editorial method with the Workbench's existing tools.

## Pick by input and output

| Input and desired output | Production order | First review artifact |
| --- | --- | --- |
| Raw speaking footage → clean talk, tutorial or vertical Short | Inspect → transcribe → compact edit plan → preflight/cut/build/verify → proxy → optional reframe, captions and B-roll → final | Rough-cut proxy and proposed removals |
| Product repo or live UI → launch film | Inspect repo and run the relevant flow → capture real UI/proof → write hook, feature beats and CTA → storyboard → choose a motion style and renderer → preview → mix and export | Storyboard with evidence and one rendered beat |
| Reference video → analysis or an original adaptation | Inspect reference → log shots, timings, audio and observed visual techniques → identify required assets → choose a renderer per shot → prototype original equivalents → assemble and review | Timestamped shot breakdown and one sample |
| Script, data, screenshots or slides → motion piece | Set narrative beats and aspect ratio → design one representative frame → choose visual vocabulary → animate → render short sample → finish and review | Style frame and short sample |
| Finished video → captions, reframe, QC or platform variants | Probe streams → perform the requested operation on a copy → check short excerpt → export → probe and inspect delivered files | Representative excerpt and media specs |

## Raw footage and short-form edits

1. Use [low-token editing](low-token.md) with the original media under `src/`. Once source ranges are approved, preflight `work/edl.json` and build the proxy. Consult [the EDL](edl.md) for the source-time contract.
2. Use the [creative tools](creative-tools.md) after cuts stabilize. Anchor cards and B-roll to the assembled program, and inspect the crop for faces, slide details and interface controls. Rebuild captions and program-timed overlays after any cut changes.
3. Use Herk Edit Kit for short-form story and card ideas, Barty-Bart for word-timed motion B-roll or local subject separation, and open-edit when the project calls for its HTML-based edit, subtitles or slides. Use ffmpeg-skill if a standalone probe, crop, loudness check or export would benefit from structured results.
4. Review the joins, subtitle spelling, framing and audio. Follow [audio guidance](audio.md) and export using the selected Workbench or external path.

## Product launches and scripted motion

1. Start from actual product behavior. For a repo-to-launch workflow, Brag can take the repo context through to a HyperFrames composition and export. Use the Workbench route when the launch is mainly a cut of real narration or recorded UI.
2. Map each beat to a viewer takeaway and to a real screenshot, demo action, supplied asset or explicitly illustrative scene. Use the SaaS Motion Kit tone matrix and storyboard references if choosing a direction. Use lemo-opuscar or opus-video-skills when the brief calls for a specific visual style.
3. Pick **one** main composition path. Use the Workbench's GSAP template for graphics anchored to edited speech, HyperFrames for a standalone HTML timeline, snapcn when working in React/Remotion, or claude-motion-design for a standalone HTML/Playwright/FFmpeg workflow. Prototype the most difficult beat first.
4. For a continuous film, use onetake when the story needs a camera or object that stays continuous across beats. Use product-launch-motion when the concept depends on a persistent shape, cursor-driven UI and a measured beat grid. Their timing and rendering workflows are distinct. Start with the chosen project's own example and preview the transitions before committing to full production.
5. Apply the motion-video-kit review method where warranted. Review key frames and moving excerpts against the brief, revise specific defects, then check the rendered seams and sound. A second reviewer is optional. Keep the result grounded in the supplied product evidence.

## Reference analysis

Use rea-video to structure a `VIDEO.md` shot breakdown. Record source time ranges, framing, camera movement, typography, layers, transitions, cuts and audio cues. Label production-method guesses separately from observations. Choose which techniques serve the new brief, create original assets or use cleared assets, and convert selected cues into the new project's program time. A reference breakdown supplies a plan for a separate build.

## Sources and their roles

Each entry is an upstream option. Open its README and, for a skill, the selected `SKILL.md` to get the current prerequisites, command and input/output contract. Follow the [tool catalog's setup protocol](tool-catalog.md#decision-protocol) for optional tools.

| Upstream | Role and selection cue | What to bring back to the project |
| --- | --- | --- |
| [brag](https://github.com/latent-spaces/brag) | Repo-to-launch story and HyperFrames production. Use for a short release or project showcase. | Plan, composition brief, share copy and `brag-output/brag.mp4` |
| [opus-video-skills](https://github.com/tuzhechen2005/opus-video-skills) | Code-generated aesthetics. Pick `painted-animation` for illustration or `kinetic-reel` for typography. | Style choices, editable source and rendered shot |
| [motion-graphics](https://github.com/Barty-Bart/motion-graphics) | Targeted skills for word-timed B-roll, object separation, explainers and SFX. Choose the specific skill. | Timed B-roll, separated subject, short sequence or audio cues |
| [motion-video-kit](https://github.com/echris6/motion-video-kit) | Business-film art direction, sound pass, keyframe review and critic loop. | Contact sheet, timestamped review notes and mix decisions |
| [product-launch-motion](https://github.com/AbubakrChan/product-launch-motion) | Use the v2 beat-grid and deterministic browser-seek workflow for cursor-led launches. Check the upstream version before using a recipe. | Beat grid, storyboard, rendered film and seam review |
| [claude-motion-design](https://github.com/howseen-ai/claude-motion-design) | Standalone HTML composition captured with Playwright and encoded with FFmpeg. | Browser scene source and rendered clip |
| [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) | Style index and code-generated demo films. Choose one style that suits the brief. | Style prompt, chosen visual rules and an original sample |
| [onetake](https://github.com/feitangyuan/onetake) | Continuous camera or object motion. Use the upstream continuity checks for joins between beats. | Motion plan, continuity observations and render |
| [herk-edit-kit](https://github.com/nateherkai/herk-edit-kit) | Transcript-led social editing, storytelling and HyperFrames card references. | Keep/drop rationale, story beats, selected card or project export |
| [rea-video](https://github.com/JuneYaooo/rea-video) | Shot-level reference analysis, including mixed media and caption/audio timing. | `VIDEO.md`, shot map and required-asset list |
| [open-edit](https://github.com/veedstudio/open-edit) | Alternate agent-led pipeline for subtitles, footage edits, slides and browser-rendered graphics. Check which steps need a provider before use. | Caption files where available, composition and rendered file |
| [saas-motion-kit](https://github.com/tugrawork-creator/saas-motion-kit) | Software promo art direction, storyboard themes and transitions with a staged HyperFrames workflow. | Tone, storyboard, transition rationale and rendered beats |
| [hyperframes-community-skills](https://github.com/heygen-com/hyperframes-community-skills) | Individual add-ons for specialized treatments. For example, choose `camera-3d-captions` for depth around a speaker or `p5-paint-animation` for a paint-on sequence. | Selected treatment and independently reviewed asset or composition |
| [snapcn](https://github.com/shadcn-labs/snapcn) | Remotion component registry for UI demos, device frames, terminal sessions, animated text and logo stings. | Editable React component wired into the Remotion composition and its render |
| [ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) | Local media operations via script/CLI or MCP. Consult the upstream machine-readable contract and tool help for inputs. | Structured probe/QC report or processed media |
| [HyperFrames](https://github.com/heygen-com/hyperframes) | HTML composition renderer and component registry. Start with its CLI/registry skill and local preview for an HTML motion project. Some upstream workflows use separate services. | Editable composition, preview and local MP4 render |

## Handoff and verification

- Use a dedicated project folder for external compositions and generated intermediates. Retain editable source when the deliverable calls for it. Read the upstream license and the terms for each third-party asset before reuse. Inspect any external skill's commands, dependencies, network and account requirements before running it.
- Treat `work/edl.json` as **source time** and `work/program.json` as **assembled program time**. For an external overlay record program start, duration, target width/height/FPS, alpha requirements and whether its audio is intended. A renderer's native project stays with that renderer. To combine it with the Workbench output, render media and composite or splice it explicitly, then probe the result. Check alpha support on a sample before rendering a transparent overlay in full.
- Track which output owns the final audio mix. Use [the Workbench mix](audio.md) for a Workbench-built program, or verify the external renderer's own mix when delivering its finished film. Avoid applying both to an already mixed deliverable.
- Check duration, resolution, FPS, audio tracks, framing, readable captions, subtitle synchronization and cut/transition seams on the actual deliverable. Review representative stills and moving excerpts. Record what was measured, what was reviewed and any remaining limitation.
- If an optional renderer is unavailable, make a small preview with the local Workbench template or SRT/ASS tools if they can convey the requested effect. Report any difference the viewer will see.

## Türkçe başlangıç

- **Ham kayıt:** transkript → kurgu planı → kesim ve proxy → altyazı/grafik → final.
- **Ürün veya repo:** gerçek ekran ve kanıt → hikâye ve storyboard → tek bir render yolu → kısa örnek → final.
- **Referans video:** zaman kodlu sahne analizi → gerekli varlıklar → özgün örnek → seçilen üretim yolu.
- **Hazır video:** teknik inceleme → istenen düzeltme veya format → örnek kontrolü → teslim.
