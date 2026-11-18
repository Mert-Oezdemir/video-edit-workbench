# Agent capabilities / Ajanın imkanları

This is the first routing reference for a tool-capable agent. It describes what
can be done, which path does it, and what must be checked. It is not a claim
that every tool is installed or every combination has been tested.

## Understand the request and choose the path

The user can describe the desired video in ordinary language. Extract source
material, message, length, orientation, resolution, frame rate, subtitles,
sound and output type from that brief. Reuse answers already given. Choose
tools autonomously; ask only for consequential missing editorial decisions.
Do not ask the user to select a library or write a command.

Classify each needed capability:

1. **Ready command:** an existing script implements the operation.
2. **Local composition:** the agent can construct a specific FFmpeg command or
   adapt the scene with existing tools. This needs a short sample check and
   output validation; it is not a turnkey feature in produce.py.
3. **Optional dependency:** documented upstream tool, not a working adapter.
   Check installation, compatibility, license and actual invocation first.
4. **Unavailable or service-dependent:** explain the gap and use an acceptable
   local alternative. Never silently spend money or promise an untested feature.

For a concrete job, inspect the machine and media, state a short plan, produce
a preview, verify it, and deliver final output only after the required review.
An agent with file/terminal access can execute; a text-only chat cannot.

## Implemented paths and local possibilities

| User asks for | Execution route | Limits / checks |
|---|---|---|
| Long recording → selected Short | Agent chooses coherent passages from local transcript; produce.py renders reviewed ranges | No automatic viral scoring, face tracking or highlight model in the runner |
| Faceless story/explainer | Agent authors script/storyboard; produce.py composes local stills/clips, optional supplied narration and captions | It does not create images, speech or script by calling a model |
| Edit personal footage | Existing transcribe/cuts/build/verify pipeline; produce.py for explicitly selected ranges | Use existing word-boundary pipeline when speech-safe cuts matter |
| Vertical 9:16 MP4 | produce.py init → doctor → preview → final | Preview 360×640; final 1080×1920, 30 fps, H.264/AAC |
| Horizontal 16:9 or square 1:1 | Existing scene/source-resolution path where suitable, or agent-composed FFmpeg scale/pad/crop/export | New produce.py has no ratio option; do not pretend that changing a nonexistent flag works |
| Custom dimensions, 4K or different FPS | Inspect existing render/build options; otherwise explicit local FFmpeg operation | Check encoder, source detail, resource cost, frame timing and preview; upscaling does not create detail |
| MOV, WebM, another container/codec | Agent-composed FFmpeg conversion | Inspect available encoder/muxer and compatible audio/pixel format; extension alone is insufficient |
| Trim, concatenate, resize, pad, center crop, pan/zoom | Existing helpers or explicit FFmpeg filters | Confirm framing; center crop is not face-aware tracking |
| Local transcription | transcribe.py with an installed local Whisper backend | Model, language and hardware must be checked; downloads are not implied by availability |
| Subtitles / simple text cards | creative_overlay.py; supplied output-timeline captions in produce.py | Check libass, fonts, sync, reading speed and safe areas |
| Bespoke motion graphics / diagram | Existing HTML/CSS/GSAP scene; render.mjs where appropriate | Optional browser/Node prerequisites; custom scenes require actual implementation and visual review |
| Loudness, sound mix, synthesized SFX | Existing build.py, mix.py, loudness.py and sfx.py | Read audio.md; do not apply voice processing or effects without the brief supporting it |
| Silence/retake cleanup | Existing Whisper/cuts workflow; reviewed agent decisions | Never delete uncertain content merely to shorten the video |
| Multiple output versions | Keep each version in distinct job/output paths; choose route per version | Check each version; produce.py uses fixed filenames and refuses overwrite |
| Long-form video | Existing pipeline or deliberately composed local job | produce.py currently caps a job at 200 segments / 2 hours; a segment at 1 hour; do not assume unlimited duration |

## Optional tools: known possibilities, not installed features

Read [the registry](video-tool-registry.json), [free-first workflows](free-video-tool-stack.md)
and [installation protocol](tool-catalog.md) only as needed.

- **FFmpeg Skill:** optional agent interface for local FFmpeg operations.
- **Auto-Editor:** optional alternative rough-cut/silence processing.
- **Claude Shorts:** optional specialist pipeline; compatible Claude access needed.
- **Ghost Editor:** platform/subscription constrained alternative; review cloud steps.
- **OpenMontage:** optional orchestration; audit paid-provider paths and license.
- **rea-video:** reference/style analysis; it does not itself render a final video.
- **HyperFrames / Remotion:** optional renderers; check local prerequisites and
  free-use/license limits. Do not add both by default.
- **Piper:** possible local narration; select a maintained distribution and
  appropriately licensed voice. No TTS adapter is implemented in produce.py.
- **ComfyUI:** possible local asset generation if hardware and model terms allow.
  No generation adapter is implemented in produce.py.
- **Higgsfield Skills:** distinguish hosted generation from reusable local
  assembly/caption/timing helpers and editorial methods. Hosted calls remain
  blocked for zero-extra-spend jobs. Local helpers are candidates for adaptation,
  not already integrated tools; inspect exact files, dependencies and licenses,
  preserve attribution, and test before reuse. Do not run a full setup/auth
  workflow just to borrow a local technique.

External tools can hand off an existing file through external_handoff.py.
That creates an unapproved review manifest; it does not execute an upstream
tool, convert its timeline or import it into the edit automatically.

## Runtime discovery and validation

Run only relevant checks. `python scripts/doctor.py` checks the legacy base
environment; `python scripts/video_tool_stack.py doctor --mode MODE` checks
catalog presence only. Neither proves a working GPU, downloaded model, voice,
third-party adapter or correct video. For production manifests, use
`python scripts/produce.py --project PROJECT doctor` to inspect that job.

For a composed FFmpeg path, inspect source streams with FFprobe and check
the required encoders, muxers and filters in the local FFmpeg build. Work on
derived local files and pass arguments without a shell. Do not execute model
text as a command. Keep new outputs separate from source and reviewed outputs.

Validate output width/height, frame rate, duration, audio, codec/container,
subtitle synchronization and complete decode. Inspect representative frames;
the user reviews audible joins and editorial quality. A passing command or
unit test does not prove that the requested content is good.

Keep a compact record in the video project's work/NOTES.md: requested delivery,
selected route, installed tools actually used, commands, verified output
metadata, preview location, review state and any unmet requirement. Reuse
measurements instead of repeating model calls or dumping logs into context.

## Cost and truthful reporting

Use the existing AI session for planning and local tools for media processing.
No extra API purchase, cloud generation, uploads or paid features by default.
The shared spend_policy.py blocks remote plan_provider.py API access unless
both explicit paid-workflow switches are set. This does not sandbox arbitrary
third-party programs or prevent a user-configured local server from proxying
to a paid backend. Check those separately before use.

Tell the user what was executed, what was validated and what remains missing.
Do not claim you installed a catalog, generated AI imagery, heard audio,
achieved virality or published changes unless that actually happened.
