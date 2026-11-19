# AI / Agent start here — Video Edit Workbench

Read the [agent capabilities map](reference/agent-capabilities.md) to choose between the starter CLI, reviewed manifest rendering and direct FFmpeg operations.

Read this file first, then [AGENTS.md](AGENTS.md), then the relevant mode guide in [QUICKSTART_TR.md](QUICKSTART_TR.md). This repo includes **real runnable local starter modes** plus optional third-party catalog entries. Do not confuse advisory tool plans with installed renderers.

## Command router

| User's intent | Executable baseline | Hard limitation |
|---|---|---|
| Long source video into Shorts | `python workbench.py shorts --project PROJECT --input src/recording.mp4 --srt src/subs.srt` | Need SRT, local Whisper (explicit model download), or reviewed selections. Suggested clips are NOT guaranteed viral |
| Faceless generated content | `python workbench.py faceless --project PROJECT --script src/script.txt` | Default output is **silent typography-based MP4**; add licensed images/audio/Piper for narration |
| Original code-generated film in a Lemo style | `python scripts/lemo_opuscar.py search --query "explainer" --json` (local metadata), then `plan --project PROJECT --style SLUG` | **Planning only**; upstream Lemo rendering is separate, requires compatible agent/dependencies and rights review |
| Personal footage edit | `python workbench.py edit --project PROJECT --input src/take.mp4 --format portrait` | Fast cut/reframe; for word-accurate cutting/retakes use existing low-token editor |

For machine-readable inventory use `python workbench.py tools --json`; for a **non-executing** optional tool recommendation use `python scripts/video_tool_stack.py plan --mode faceless` (other modes: `long-to-shorts`, `own-footage`). Consult [registry](reference/video-tool-registry.json) for licenses, permissions, integration status and cost classification. Avoid upgrading to paid/cloud features.

For code-generated original film, named Lemo style, or short custom animated
intro, read the **[complete agent decision and workflow guide](reference/lemo-opuscar-agent-workflow.md)**:
distinguish existing-clip editing from original film production; select a style
by local metadata; preview and approve external MP4 before importing it.
For local discovery use `python scripts/lemo_opuscar.py search --query
"explainer" --json`. These commands do not produce a Lemo movie.

Optional creative style choice for original faceless films: [Lemo-Opuscar guide](reference/lemo-opuscar.md). `scripts/lemo_opuscar.py` lists locally installed styles and writes a review-only plan; it does not install, generate a movie or grant rights to redistribute CC BY-NC guides.

## Agent operating contract

1. Discover `python workbench.py --help` and run `python workbench.py doctor --json`. If local FFmpeg missing, explain exactly what is missing; **do not invent a completed MP4**.
2. Inspect existing project and media. If project not initialized, choose a new path and run `python workbench.py init PROJECT`. Do not overwrite an existing project or video.
3. For narration/visuals check source rights and creator preferences. Choose a simple local method first; do not install all 14 catalog entries. If a source is a YouTube/stream URL, do not automatically download it; request authorized local source or a rights-cleared alternative.
4. For Shorts, use local SRT if available. If using Faster Whisper, run under existing subscription/code permissions and **explicitly authorize model download** only when the user has allowed it. Never treat a coding-agent subscription as free inference API access.
5. For an AI-reviewed moment selection, ask the user/agent to examine `--plan-only` JSON and **edit the clip timings**. Supply selections via `--selections out/video-shorts-plan.json`. Keep selected source unchanged.
6. For faceless video, the current agent can write original `src/script.txt`, then run the local renderer. A computer-generated caption video is not the same as text-to-video diffusion. To use ComfyUI or HyperFrames review their standalone requirements; no automatic bridge is claimed.
7. For advanced professional edits, use existing [low-token editor](reference/low-token.md) and [creative tools](reference/creative-tools.md). The fast `edit` CLI is conservative and does not silently replace an approved EDL.
8. Run first preview, inspect video with FFprobe and relevant QA scripts, confirm captions/audio and request final approval before publish. Save notes/provenance. Never automatically publish, charge credits, upload user media, expose secrets or change meaning without permission.

### Example agent user prompt

> Read `AI_START.md`, `AGENTS.md` and `QUICKSTART_TR.md`. Inspect my authorized footage in `my-videos/src/`. Produce a local, no-extra-cost 1080x1920 Shorts preview using the best available existing tools. Do not call paid providers or automatically download large models. If there is a transcript, suggest clip boundaries and show me the review JSON. Preserve originals and show the output path.

## Tool statuses (do not overclaim)

- **Wired baseline:** FFmpeg/FFprobe; optional installed Faster Whisper; runnable `shorts`, `faceless` and `edit` commands.
- **Read-only registry + recommendations:** FFmpeg Skill, Claude Shorts, Ghost Editor, OpenMontage, rea-video, HyperFrames, Remotion, ComfyUI, Auto-Editor, Piper, Higgsfield Skills, Lemo-Opuscar. They do **not** become embedded by appearing in the catalog.
- **Local interoperability:** `scripts/external_handoff.py` can register an already existing output for review, but does not launch a third-party repo or rewrite the editor timeline.
- **Costs:** Hosted Higgsfield calls blocked, HeyGen/HyperFrames Pro disabled, no cloud renderer or paid API.
- **Original project retained:** AGENTS, SKILL, Python/NumPy/Whisper cutting, verification, GSAP/Three.js, EDL, original documentation.

For any missing output, report the precise missing dependency/asset and give one free local alternative. Never claim completion based on a plan.
