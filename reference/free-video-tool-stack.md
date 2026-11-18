# Free video tool stack / Ücretsiz video araçları

> **Scope:** This is an **on-demand integration guide** for [Video Edit Workbench](../README.md), not a lockfile, a one-click factory, a claim that every project has been tested, or permission to spend money. The existing Python/NumPy/FFmpeg/Whisper editing engine remains the default. The machine-readable catalog is [video-tool-registry.json](video-tool-registry.json).

## Rules: subscription AI, zero extra invoices

- Use a coding agent the user already has access to (e.g. Codex or Claude Code), within its existing plan limits; a chat subscription is **not** an unlimited/free API key.
- **No** new credit purchases, billed AI APIs, cloud rendering, provider billing, or remote upload of private source footage by default. Never assume that an open-source GitHub skill makes the hosted service free.
- Never run package installers, npm postinstall scripts, executable dependencies, downloaded model weights, or shell commands copied from the internet without checking source, security, licenses, compatibility and host permission. No silent `npx` download.
- Install **only the optional tool actually needed**, into a local or isolated environment. Do not vendor third-party code into this MIT-licensed repo, include their weights, auto-pull gigabytes of models, or install every item.
- Preserve originals in `src/`. Use temporary/derived `work/` paths and reviewed `out/` outputs. Validate audio, aspect ratio, transcript, rights and cuts. Follow [editorial intake](editorial-intake.md) before production.
- The user's target is 1080 × 1920 MP4 by default for Shorts, subject to project requirements. "Viral" is not a guaranteed or measurable output of a library.

## 13 named free-code/local options from the conversation

| Tool / upstream | Role | Zero-extra-cost limits | Workbench integration status |
|---|---|---|---|
| [FFmpeg / FFprobe](https://ffmpeg.org/) | Cut, audio, export, captions, verification | Local tools; binaries/codecs have build-dependent licenses | **Core / already wired** |
| [Faster Whisper](https://github.com/SYSTRAN/faster-whisper) | Local speech transcription | Free code; speech model download and model license may differ | **Existing optional backend** |
| [FFmpeg Skill](https://github.com/kajisho5/ffmpeg-skill) | Agent-facing FFmpeg operations/MCP | Free, local; duplicates existing helpers | **Optional, not installed** |
| [Auto-Editor](https://github.com/WyattBlue/auto-editor) | Silence/motion-based rough cut | Free local CLI; decisions still require review | **Optional, not installed** |
| [Claude Shorts](https://github.com/AgriciDaniel/claude-shorts) | Long video → candidate Shorts; captions | Free repo; Claude Code access required; setup downloads dependencies | **Optional alternative pipeline** |
| [Ghost Editor](https://github.com/kurbaitaev/ghost-editor) | Talking-head reels, AI motion styles | Free repo; Apple Silicon Mac + paid Claude Code plan; some optional provider calls require keys | **Optional alternative pipeline** |
| [OpenMontage](https://github.com/OpenMontageInc/OpenMontage) | Agentic clip/faceless/composition workflows | AGPL-3.0; some examples/workflows depend on billed providers | **Optional orchestration** |
| [rea-video](https://github.com/JuneYaooo/rea-video) | Breakdown / shot-by-shot style and `VIDEO.md` | Offline analysis free; model-assisted analysis and remakes can be paid | **Optional analysis handoff** |
| [HyperFrames](https://github.com/heygen-com/hyperframes) | HTML-native local editor/render, titles, captions | Local engine and Studio free (Apache 2.0); specific Pro/HeyGen features not free | **Optional renderer** |
| [Remotion](https://github.com/remotion-dev/remotion) | React-based animation and captions | Source-available license; free use depends on eligibility. Check current terms | **Alternative renderer** |
| [Piper TTS](https://github.com/rhasspy/piper) | Local voiceover | Linked upstream is **archived**; voices have individual licenses | **Optional TTS; maintained distribution recommended** |
| [ComfyUI](https://github.com/Comfy-Org/ComfyUI) | Local AI image and, with suitable models, video generation | Free software; significant GPU/VRAM needs, model license varies | **Optional asset generator** |
| [Higgsfield Skills](https://github.com/higgsfield-ai/skills) | Connect AI agents to Higgsfield generation | MIT skill source is free; the Higgsfield service uses credits | **BLOCKED in no-extra-spend mode** |

**Not eligible as unrestricted free services:** OpusClip, Descript, ChatCut and hosted Higgsfield/HeyGen generation were discussed as alternatives, not installed free dependencies. They may offer trials or limited free plans, but the zero-extra-cost route must not rely on those. The original [claude-video-edit](https://github.com/YildizDikme/claude-video-edit) upstream is credited in the root README; this fork already contains its workflow.

## Mode A — Long YouTube or stream recordings → Shorts

1. **Legal ingest:** use the user's locally supplied, owned or authorized recording in `src/`; do not automatically download arbitrary third-party content. Verify source rights and platform monetization rules.
2. **Inspect/transcribe:** run existing `scripts/transcribe.py`, then `scripts/low_token.py prepare` as described in [low-token.md](low-token.md). Faster Whisper is already supported.
3. **Select moments:** prefer a compact transcript decision by the existing coding agent; **Claude Shorts** is an optional specialized alternative if Claude Code is installed. Propose several 15–60-second coherent candidates with hook, start/end and rationale; this is an editorial suggestion, not a guarantee of virality.
4. **Cut and reframe:** existing `cuts.py`, `build.py`, `verify.py` and [short preset](creative-tools.md) first. If needed, use **FFmpeg Skill** for a specialized operation or **Auto-Editor** to propose silence/motion cuts. Never overwrite an approved `work/edl.json`.
5. **Graphics:** local FFmpeg ASS overlay by default; **choose ONE** of HyperFrames or Remotion if animated caption work genuinely benefits.
6. Preview and confirm rights, word boundaries, portrait crop and caption accuracy before publishing.

**External handoff:** a specialized editor outputs a *new media file* to a distinct `work/external/<tool>/` directory. Probe and review it; only after approval, add it to the project's `src/` or integrate explicitly into an EDL. No adapter automatically converts Claude Shorts' timeline into Workbench's `work/program.json`.

## Mode B — Faceless AI Shorts from scratch

1. Human/agent writes script, factual claims, rights-cleared storyboard and asset list; user's existing agent can plan without purchasing API credits.
2. **OpenMontage** may be evaluated for free/open-stock and local composition recipes, with all provider API paths disabled; otherwise use local stills, licensed stock clips or original screen recordings.
3. **Piper** for offline narration when the *specific voice-model license* permits the use; the linked Piper repository is archived, so review an actively maintained build first.
4. **ComfyUI** can create local images/video only if hardware and downloaded model terms allow it; on CPU/low VRAM use licensed stock, images, kinetic text and 2.5D movement. Do not substitute a paid cloud generation model.
5. **rea-video** can analyze the timing, transitions and typography of a reference. Its output is a report and `VIDEO.md`, **not** a rendered video. Reproduce techniques with original/licensed assets; don't copy a third party's protected footage/voices.
6. Compose in the existing FFmpeg/GSAP engine or use **HyperFrames** locally for reusable animated templates. Remotion is a *substitute* renderer, not another mandatory layer. Export a reviewed 9:16 MP4.

**Paid-feature traps:** HyperFrames' `reverse-any-video` and `style-sampling` are listed as Pro features; do not invoke them in a free workflow. Higgsfield Editorial Motion Graphics runs through Higgsfield's provider service; its skill being on GitHub does not remove usage charges.

## Mode C — Edit personally recorded footage

1. Keep originals in `src/`, perform [editorial intake](editorial-intake.md), then local transcription and conservative rough-cut using existing scripts.
2. Optionally test **Auto-Editor** for pause trimming, or **Ghost Editor** only on a compatible Apple Silicon Mac with an existing Claude Code subscription. Some Ghost Editor additions (ElevenLabs narrator, Gemini frame check) involve remote services; disable them unless specifically approved.
3. Optional **rea-video** for analysis of an independently licensed reference. Workbench already produces word-anchored captions and template cards; prefer these before adding a renderer.
4. For complex typography or transitions choose **HyperFrames** *or* **Remotion**; keep the program timeline accurate. FFmpeg Skill can help with isolated local edits.
5. Preview, review cuts/loudness/face safe areas and export.

## Local CLI: inspect, select, don't install

Run in the repository directory, using Python 3.10+:

```sh
python scripts/video_tool_stack.py list
python scripts/video_tool_stack.py doctor --mode long-to-shorts
python scripts/video_tool_stack.py list --mode faceless --json
python scripts/video_tool_stack.py plan --mode long-to-shorts --out work/shorts-plan.json
python scripts/video_tool_stack.py plan --mode faceless
python scripts/video_tool_stack.py plan --mode own-footage
```

Create `work/` before requesting an output file. An existing plan is *never overwritten*. `doctor` only reports a lightweight binary/module presence status for known tools and `not-checked` for external project installs; it **does not run or download** anything. The `plan` JSON is advisory; there is no direct cross-repository execution bridge yet.

## Optional installation / isolated experiments (NOT automatic)

| Tool | Prerequisite & starting point | Caution |
|---|---|---|
| FFmpeg Skill | [Official README](https://github.com/kajisho5/ffmpeg-skill#quick-start); FFmpeg + Python | Optional MCP/CLI; existing engine often suffices |
| Claude Shorts | [README](https://github.com/AgriciDaniel/claude-shorts#installation); Claude Code, Bash, Node and Python; WSL2 on Windows | Test sample, inspect setup scripts first |
| Ghost Editor | [Installation guide](https://github.com/kurbaitaev/ghost-editor/blob/main/docs/INSTALL.md); Apple Silicon/Claude Code | Avoid optional cloud steps by default |
| HyperFrames | [Quickstart](https://hyperframes.heygen.com/quickstart); Node >=22 + FFmpeg | Local CLI/Studio only; exclude Pro and cloud services |
| rea-video | [Quickstart](https://github.com/JuneYaooo/rea-video#quick-start); Python >=3.10 + FFmpeg | Output `VIDEO.md` and report for analysis; no direct render |
| OpenMontage | [Repo and provider docs](https://github.com/OpenMontageInc/OpenMontage); check AGPL and optional providers | Disable provider credentials and paid models |
| Auto-Editor | [Upstream docs](https://auto-editor.com/); install in separate environment | Don't trust automatic removals without preview |
| Piper, ComfyUI, Remotion | Follow upstream installation and individual asset/model licenses | GPU, sound model, or license constraints vary |

Do not copy a command from this table and run it without the safety checks in [tool-catalog.md](tool-catalog.md). Never treat a package install as equivalent to a working end-to-end integration.

## Manual interoperability contract

- **Input:** absolute or project-relative local paths, a requested mode, creator style/target format, explicit rights/permissions and a reviewed work plan. A URL alone does not imply download consent or copyright clearance.
- **Output:** reference analysis → `work/reference/<job>/VIDEO.md` or report; optional generated assets → `work/external/<tool>/<job>/`; cut plans → approved local EDL; rendered previews → `out/`.
- **Validation:** run `ffprobe` and, where applicable, existing `verify.py` / `visual_review.py`; preserve provenance, source links, licenses, frame rate, duration and loudness in `work/NOTES.md`. Never overwrite original clips or silently publish.
- **Credentials:** keep any explicit provider credentials outside source control and don't configure providers at all for no-extra-spend projects. No external API calls should be inferred from the presence of Codex, Claude Code, Higgsfield, HeyGen or OpenMontage.
- **Fallback:** tool unavailable, incompatible, paid, unsafe or slow → stay on existing Python/FFmpeg/Whisper workflow and report the limitation.

## Tests and maturity

```sh
python -m unittest discover -s tests -v
python scripts/video_tool_stack.py doctor --json
```

The tests validate routing, registry guards and no-overwrite behavior **without external packages**. No end-to-end performance or output-quality claim is made for any optional integration. New upstream packages must be audited and tested on a short sample before promoted to a real production path.
