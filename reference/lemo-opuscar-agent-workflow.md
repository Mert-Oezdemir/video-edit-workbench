# Lemo-Opuscar: AI agent karar ve çalışma kılavuzu

**Status: a supported read-only optional adapter, NOT an automatic film renderer.**
This is the concrete routing contract for an AI coding agent using Video Edit Workbench. Read [AGENTS.md](../AGENTS.md), [AI_START.md](../AI_START.md), [agent capabilities](agent-capabilities.md), [editorial intake](editorial-intake.md) and [Lemo integration instructions](lemo-opuscar.md). The commands below run from the Workbench repo root, unless explicitly stated otherwise.

## 1. What is actually possible?

| Task | Agent action | Readiness |
|---|---|---|
| Fast Shorts from an existing recording | Existing workbench.py shorts, SRT or local Whisper + FFmpeg | Executable Workbench feature |
| Trim, crop/reframe, clean user's footage | Existing workbench.py edit or high-precision EDL workflow | Executable Workbench feature |
| New faceless typographic 9:16 MP4 | Existing workbench.py faceless or produce.py | Executable Workbench feature; original image/voice generation is NOT included |
| Discover Lemo film styles | lemo_opuscar.py list / search on a separate local Lemo checkout | Executable read-only adapter |
| Inspect feasibility of a chosen Lemo style | Read local STYLE.md / prerequisites / license; compare with user brief | Agent analysis; NOT a renderer |
| Save chosen style and next steps | lemo_opuscar.py plan (new JSON, approved: false) | Executable read-only/non-destructive adapter |
| Render a Lemo film, make bespoke WebGL/Canvas/code visuals, camera moves, animation, narrated film | Use *upstream Lemo-Opuscar* in a separate environment following its official workflow if independently set up/authorized | **NOT integrated/executed by Workbench adapter** |
| Register an already rendered, owned/authorized local MP4 | external_handoff.py --tool lemo-opuscar --mode faceless | Executable **metadata/review handoff only** |
| Import MP4 automatically into approved EDL or produce final | No direct bridge; explicit manual timeline/production decision needed | **NOT implemented** |
| Upload to social media, buy credits, run hosted models, automatically download dependencies | Never through this adapter | **NOT implemented; forbidden by default policy** |

A style is a production approach, not an FFmpeg filter that can be applied with one command to arbitrary existing footage. Lemo primarily creates original **films in code**, while Workbench defaults to editing/composing **local** media. Do not promise that selecting a Lemo style automatically transforms an imported clip into that style.

## 2. Choose the correct route from natural language

Determine whether the user is asking for an **existing-video edit**, an **original film**, or a **hybrid**. Preserve the aspect ratio/duration and rights specified in the brief.

1. **"Bu uzun YouTube videosundan üç dikey short çıkar."** Use Workbench shorts; do *not* introduce Lemo. Optional original motion titles can be considered separately, not required.
2. **"Videomdaki sessizlikleri kaldır, altyazı ekle."** Use Workbench edit / accurate cut pipeline. Lemo is not a silence-removal tool.
3. **"Kahve markam için Neon Tubes tarzında animasyonlu bir açılış filmi yap."** Lemo is a relevant *optional production path*. Run local style discovery/plan; clearly distinguish plan from completed film. Upstream execution is separate.
4. **"Lemo'da hangi görsel tarzlar var, eğitim videosuna hangisi uygun?"** Read local metadata via list/search and use specific STYLE.md references to offer up to three candidates, explain their subject fit and actual prerequisites. No automatic rendering.
5. **"Mevcut konuşma videoma 5 saniyelik özel kod animasyonunu ekle."** A hybrid: edit original in Workbench; externally produce licensed code-generated motion snippet if required and available; register its MP4 via external_handoff.py; only after review manually integrate it. No automatic EDL rewrite.
6. **"Tamamen ücretsiz ve internete hiçbir şey göndermeden yap."** Choose existing local FFmpeg/typographic faceless/own-footage path first. An optional local Lemo checkout does not prove its upstream dependencies, fonts, TTS or models are offline. Don't silently run upstream.
7. **"Sinematik film istiyorum ama stil bilmiyorum."** From the brief (story vs. documentary, brand tone, desired visuals), use list/search to shortlist. Do not give a fabricated final-quality score or pretend the adapter can auto-render.

**Rule:** If the user didn't request a distinctive code-generated visual language, preserve the simple Workbench workflow. Avoid turning any ordinary edit into an expensive multi-tool production.

## 3. Determine which kinds of work the styles suit

The upstream catalog currently describes 99 styles. **Do not hardcode 99 entries or assume a future version has the same count.** Only report what's returned by the locally installed version. Categories and use cases are upstream metadata; they are *suggestions* rather than guaranteed capabilities.

Examples to guide selection (always verify they still exist through the CLI):

| Need | Look for (example slugs) | Use/limitation |
|---|---|---|
| Explanatory sketches, educational animations | whiteboard, chalkboard, sketchnote | Can suit concept explanations; bespoke diagrams still need separate Lemo production |
| Brand or product launch opener, neon city aesthetic | neon-tubes, glass-product, swiss-motion | More original motion design; don't imply product photos are generated |
| Data- or mechanism-based explainer | dataviz, blueprint, iso-infographic, teardown | Accurate numbers, sources and diagrams must be supplied and verified |
| News, archival or documentary presentation | caption-news, news-package, dark-documentary | Don't invent source footage, misrepresent illustrated scenes as evidence, or assume licensed archives |
| Illustrated story or game aesthetic | watercolor, pixel-rpg, cel-anime-80s | Production complexity/assets vary by style; some upstream styles require additional image-generation tools |
| Simple Short from an existing recording | **No Lemo needed** | Use Workbench shorts/edit instead |

**Ajanın seçim yöntemi:**
- Read a short user brief and extract subject, tone, intended audience, platform, length, visual references and constraints.
- The CLI metadata is primarily English; for a Turkish request, translate *search terms only* to English (e.g. "öğretici çizim" -> "explainer sketch"). Do not translate protected guides into distributable assets.
- List all local names if asked, or use keyword search to reduce token use; inspect a handful of matching style records' "uses" and read the **one to three** selected upstream STYLE.md files locally.
- Explain the options in the user's language with a reason (not fabricated scores). Prefer one justified choice only after the brief is clear. If uncertain, show 2–3 alternatives with the trade-off.
- For substantive brand/story changes, get creator approval according to editorial-intake.md.

## 4. Exact commands: detection → discovery → safe plan

First identify a Workbench project and runtime; use a new project directory if appropriate:

~~~sh
python workbench.py --help
python workbench.py doctor --json
python workbench.py init my-videos
~~~

The user or maintainer must have **separately installed** the upstream repository, e.g. in ~/lemo-opuscar. **Never auto-clone, install node modules, update a library or download data for style browsing**. On a different local directory, set --library PATH on each Lemo command (or LEMO_OPUSCAR_LIBRARY). The commands below do not require Node, browser, TTS or external APIs:

~~~sh
python scripts/lemo_opuscar.py doctor --json
python scripts/lemo_opuscar.py list --json
python scripts/lemo_opuscar.py search --query "explainer" --limit 8 --json
python scripts/lemo_opuscar.py search --query "brand launch" --limit 8
python scripts/lemo_opuscar.py plan --project my-videos --style neon-tubes
~~~

Search is **simple metadata keyword matching** (name, slug, category, "uses"), not an LLM similarity search. No match does not mean the film cannot be made. If results are poor, list styles and review the upstream style index; do not blindly choose the first match. For unknown or missing local Lemo checkout, report "not installed/unknown" and suggest a Workbench-local alternative.

The plan is written to a new local path:

    my-videos/work/style-plans/lemo-neon-tubes.json

Its contents explicitly say **advisory-style-plan-only**, **rendered: false**, **approved: false** and include a pointer to the original local STYLE.md. If the file exists, never overwrite it; choose --name another-take.json. Do not paste third-party STYLE.md prose into repository-owned prompts/templates or check it into git.

## 5. When the user authorizes separate Lemo film production

The adapter does not run Lemo. You may **explain** the separate upstream setup/invocation or hand the user to its own officially installed agent skill, but never claim Workbench executes it. The upstream documentation describes a Claude Code plugin with its own production workflow, code-rendering engine, film-specific directories and dependencies. Prerequisites may include Node 20+, Python 3.11+, FFmpeg 7+, and an image generator for certain styles.

The agent should:
1. Confirm rights, commercial context, existing agent/OS compatibility and local tool versions. Upstream **code** is largely MIT, **Markdown guides** CC BY-NC 4.0, and third-party assets have independent licenses. The upstream license allows particular film-production use but not unrestricted copying/distribution of guides. Avoid third-party trademarks, unlicensed voices or sample assets.
2. Follow upstream's current AGENTS.md, DIRECTOR.md, TECHNIQUE.md and selected STYLE.md **in that separate project**, not as a replacement for Workbench's AGENTS.md or a guarantee of applicability to the current host.
3. Treat storyboard, image-generation, TTS, music, cloud services, token usage and hardware as *potential* work or cost. No automatic package installation, remote use or billing from Workbench.
4. Request approval for style/storyboard and substantive changes. Verify any actual film produced by the separate upstream process, with its own tools and logs.
5. If upstream isn't available, make the user-requested best feasible local FFmpeg/HTML/GSAP version when appropriate and describe lost visual fidelity—do not describe it as an authentic Lemo render.

**Don't** assert "I rendered a Neon Tubes film" based on a style JSON, a code snippet, a passing doctor check or a plan. Real video must exist and be inspected.

## 6. Register separately generated media for human review

Have the user place an **existing** rights-cleared local MP4 inside their Workbench project's work/external/lemo-opuscar/ directory (manual copy; no remote download). Register it:

~~~sh
python scripts/external_handoff.py \
  --project my-videos \
  --tool lemo-opuscar --mode faceless \
  --kind rendered-video \
  --asset work/external/lemo-opuscar/film.mp4 \
  --out work/handoffs/lemo-film.json \
  --provenance "Locally produced with Lemo; verified source rights"
~~~

**What this does:** local ffprobe checks the presence of a video track and records metadata. A new manifest says pending-human-review, approved: false. **What it does not do:** render, assess aesthetic quality/licensing, edit an EDL, publish, convert formats or approve a final film.

For the next step, show the preview, inspect true aspect ratio, duration, frame rate, audio/sync, subtitles, visual artifacts and source provenance. Obtain explicit editorial approval before any hand-selected import or montage. If a reviewed timeline is subsequently built with produce.py, follow [production.md](production.md) for its separate preview hash approval and final. **Do not pass --approve-preview unless the user has approved that exact preview.**

## 7. Agent user-facing response contract

At each stage, report only verified operations, using these factual statuses (not fake completion):

- **AVAILABLE / READY_LOCAL:** Workbench's core required binaries and media are confirmed. This is *not* proof of a functioning Lemo renderer.
- **STYLE_DISCOVERED:** Local metadata found; cite style slug and its file path, not copied guide text.
- **PLAN_ONLY:** New JSON written, with path; nothing rendered or approved.
- **EXTERNAL_PRODUCTION_REQUIRED:** Upstream film generation needs separately configured compatible environment and permissions. Say what is missing.
- **HANDOFF_PENDING_REVIEW:** Existing MP4 inspected with ffprobe and review manifest saved; no timeline change.
- **FINAL_APPROVED:** Only after the actual output was rendered, checked, and approved according to the requested workflow. Never infer approval from a manifest.

Keep any use of these terms descriptive; there is no protocol exchanging these states with the upstream project. Mention actual command failures and available fallback, not promises that an untested adapter works.

## 8. Failure/fallback rules

| Problem | Correct response |
|---|---|
| Local Lemo clone missing | Explain path; ask only for access/permission that is truly needed; continue using built-in Workbench modes if they fit |
| No keyword match | List styles / inspect upstream index; do not invent a style slug |
| Selected style requires extra assets, image generation or model | Identify the exact missing input; don't silently download or call an API |
| No Claude Code, Node 20+, Python 3.11+, FFmpeg 7+, or compatible OS for upstream | Keep the read-only style plan if possible; do not claim an upstream film will render |
| Reuse/distribution of upstream Markdown guides or unclear commercial rights | Keep only metadata/path references, check upstream license and asset CREDITS, do not copy restricted material |
| Existing plan/handoff file | Create a new filename; never overwrite |
| Existing personal footage just needs cuts | Stay on Workbench shorts/edit, not Lemo |
| Rendered MP4 missing/invalid | No handoff/no imported timeline; report the actual error |
| Need video quality assessment | Preview actual output and use user review plus applicable local validation, not just unit tests |

## 9. Example agent briefs

- **"45-second 9:16 educational film about solar cells, blueprint style, no paid APIs."** Discover a local blueprint style, check possible upstream portrait support and dependencies, propose storyboard, create nonapproved plan. If upstream cannot be run locally with accepted permissions, offer a native typography/diagram version as a fallback; don't pretend Lemo rendered it.
- **"Turn my existing 20-minute lecture into five vertical clips with subtitles."** Do not use Lemo. Use local SRT/Whisper, select and verify cut candidates, render Workbench previews and seek approval.
- **"Add a five-second neon opening to my cooking Short."** Workbench handles the original cut. Lemo can be a separate optional generator for *only* the new opening. Register a completed asset, verify rights, inspect, and manually add to a reviewed edit if authorized.

### Quick rule for autonomous agents

> First inspect the user's intent, local resources, rights, cost constraints and media. Prefer the existing Workbench workflow for ordinary editing. For a specifically requested code-generated film, read this guide, search a *local* Lemo library, inspect the selected original STYLE.md, create a **nonapproved** plan, explain prerequisites and separate production, then safely review any actual exported MP4 through external_handoff.py. Never confuse style selection, plan generation, software installation, film rendering and final approval.
