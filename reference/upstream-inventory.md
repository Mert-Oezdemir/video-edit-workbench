# Upstream resource inventory

Use [production routes](production-routes.md) to choose a workflow first. Then
use this index to find individual skills, cards, templates, demos, scripts,
transition references, styles and media assets by path.

1. Open the relevant project section and its curated entry points. Search that
   project's tracked path list for terms from the brief, such as `compare`,
   `camera`, `captions`, `stinger` or `transition`. Read only the relevant matches.
2. Open a matched file in the pinned GitHub tree. Its permalink is
   `https://github.com/<owner>/<repo>/blob/<commit>/<path>`. Encode characters
   such as spaces and use `tree` for directories. Use the README or nearby
   manifest to check the artifact's purpose, inputs, platform and license.
3. Record the selected path and pinned revision in the project notes, together
   with the selected workflow and how the resource will be tested or handed off.

The path lists describe files tracked by the 16 pinned Git snapshots, including
assets and supporting files. They contain paths only. Follow Git LFS pointers,
submodule references or upstream instructions when an asset lives elsewhere.
Detailed file content needs upstream access or an existing local copy. Curated
entries were checked for existence. External scripts and assets require their own
compatibility checks and production review.

### Example lookup · Before and after in a launch film

Use the Workbench for the actual rough cut. For a designed comparison beat,
inspect Herk Edit Kit's `t1-overview-compare.html` and its associated style
metadata. Use the layout only if it accommodates the actual footage and caption
safe area. Compare motion options in SaaS Motion Kit's transition atlas, then
check HyperFrames' registry for a compatible editable block. Review a short
render before committing to the whole film.

## brag

[Pinned tree](https://github.com/latent-spaces/brag/tree/06379432a9243c951dfcc051153be18d2d261044) · [All 373 tracked paths](upstream-inventory/brag.txt)

- [Upstream README](https://github.com/latent-spaces/brag/blob/06379432a9243c951dfcc051153be18d2d261044/README.md)
- Full repo-to-film workflow · [skills/brag/SKILL.md](https://github.com/latent-spaces/brag/blob/06379432a9243c951dfcc051153be18d2d261044/skills/brag/SKILL.md)
- Shorter path to a launch cut · [skills/brag-slim/SKILL.md](https://github.com/latent-spaces/brag/blob/06379432a9243c951dfcc051153be18d2d261044/skills/brag-slim/SKILL.md)
- Brag’s own product brief example · [PRODUCT.md](https://github.com/latent-spaces/brag/blob/06379432a9243c951dfcc051153be18d2d261044/PRODUCT.md)

## opus-video-skills

[Pinned tree](https://github.com/tuzhechen2005/opus-video-skills/tree/dafed5bd55eb8bca01baeff2b059cab2446cf042) · [All 73 tracked paths](upstream-inventory/opus-video-skills.txt)

- [Upstream README](https://github.com/tuzhechen2005/opus-video-skills/blob/dafed5bd55eb8bca01baeff2b059cab2446cf042/README.md)
- Hand-painted animation workflow · [skills/painted-animation/SKILL.md](https://github.com/tuzhechen2005/opus-video-skills/blob/dafed5bd55eb8bca01baeff2b059cab2446cf042/skills/painted-animation/SKILL.md)
- Kinetic typography reel workflow · [skills/kinetic-reel/SKILL.md](https://github.com/tuzhechen2005/opus-video-skills/blob/dafed5bd55eb8bca01baeff2b059cab2446cf042/skills/kinetic-reel/SKILL.md)
- Typography and motion rules · [skills/kinetic-reel/references/style-guide.md](https://github.com/tuzhechen2005/opus-video-skills/blob/dafed5bd55eb8bca01baeff2b059cab2446cf042/skills/kinetic-reel/references/style-guide.md)

## motion-graphics

[Pinned tree](https://github.com/Barty-Bart/motion-graphics/tree/3d83d987d658601d8a1269eb691622bdcd427335) · [All 160 tracked paths](upstream-inventory/motion-graphics.txt)

- [Upstream README](https://github.com/Barty-Bart/motion-graphics/blob/3d83d987d658601d8a1269eb691622bdcd427335/README.md)
- Word-timed motion B-roll · [skills/motion-broll/SKILL.md](https://github.com/Barty-Bart/motion-graphics/blob/3d83d987d658601d8a1269eb691622bdcd427335/skills/motion-broll/SKILL.md)
- Local foreground separation · [skills/object-separation/SKILL.md](https://github.com/Barty-Bart/motion-graphics/blob/3d83d987d658601d8a1269eb691622bdcd427335/skills/object-separation/SKILL.md)
- Single-element promo · [skills/explainer-engaging/SKILL.md](https://github.com/Barty-Bart/motion-graphics/blob/3d83d987d658601d8a1269eb691622bdcd427335/skills/explainer-engaging/SKILL.md)
- Sound-effect inventory · [skills/sound-effects/sfx/manifest.json](https://github.com/Barty-Bart/motion-graphics/blob/3d83d987d658601d8a1269eb691622bdcd427335/skills/sound-effects/sfx/manifest.json)
- Additional skill entry points: [skills/explainer-default/SKILL.md](https://github.com/Barty-Bart/motion-graphics/blob/3d83d987d658601d8a1269eb691622bdcd427335/skills/explainer-default/SKILL.md), [skills/explainer-high-energy/SKILL.md](https://github.com/Barty-Bart/motion-graphics/blob/3d83d987d658601d8a1269eb691622bdcd427335/skills/explainer-high-energy/SKILL.md), [skills/sound-effects/SKILL.md](https://github.com/Barty-Bart/motion-graphics/blob/3d83d987d658601d8a1269eb691622bdcd427335/skills/sound-effects/SKILL.md).

## motion-video-kit

[Pinned tree](https://github.com/echris6/motion-video-kit/tree/e4b1c0004080fe6a0deb883631bad5eba1e5f339) · [All 26 tracked paths](upstream-inventory/motion-video-kit.txt)

- [Upstream README](https://github.com/echris6/motion-video-kit/blob/e4b1c0004080fe6a0deb883631bad5eba1e5f339/README.md)
- Business-film workflow · [business-motion-film/SKILL.md](https://github.com/echris6/motion-video-kit/blob/e4b1c0004080fe6a0deb883631bad5eba1e5f339/business-motion-film/SKILL.md)
- Review prompts · [business-motion-film/references/critic-prompts.md](https://github.com/echris6/motion-video-kit/blob/e4b1c0004080fe6a0deb883631bad5eba1e5f339/business-motion-film/references/critic-prompts.md)
- Contact sheet for frame review · [business-motion-film/scripts/contact-sheet.sh](https://github.com/echris6/motion-video-kit/blob/e4b1c0004080fe6a0deb883631bad5eba1e5f339/business-motion-film/scripts/contact-sheet.sh)

## product-launch-motion

[Pinned tree](https://github.com/AbubakrChan/product-launch-motion/tree/edbfb105382f21507bad895d8b5f6e0faa67487c) · [All 42 tracked paths](upstream-inventory/product-launch-motion.txt)

- [Upstream README](https://github.com/AbubakrChan/product-launch-motion/blob/edbfb105382f21507bad895d8b5f6e0faa67487c/README.md)
- Current beat-grid launch workflow · [SKILL.md](https://github.com/AbubakrChan/product-launch-motion/blob/edbfb105382f21507bad895d8b5f6e0faa67487c/SKILL.md)
- Motion and timing details · [references/technique.md](https://github.com/AbubakrChan/product-launch-motion/blob/edbfb105382f21507bad895d8b5f6e0faa67487c/references/technique.md)
- Shot ideas for the legacy workflow · [legacy/references/09-shot-catalog.md](https://github.com/AbubakrChan/product-launch-motion/blob/edbfb105382f21507bad895d8b5f6e0faa67487c/legacy/references/09-shot-catalog.md)
- Additional skill entry points: [legacy/SKILL.md](https://github.com/AbubakrChan/product-launch-motion/blob/edbfb105382f21507bad895d8b5f6e0faa67487c/legacy/SKILL.md).

## claude-motion-design

[Pinned tree](https://github.com/howseen-ai/claude-motion-design/tree/3d90d349ef3fdde9b7e89de4df4a2159c9e8697f) · [All 24 tracked paths](upstream-inventory/claude-motion-design.txt)

- [Upstream README](https://github.com/howseen-ai/claude-motion-design/blob/3d90d349ef3fdde9b7e89de4df4a2159c9e8697f/README.md)
- HTML motion workflow · [skill/motion-design/SKILL.md](https://github.com/howseen-ai/claude-motion-design/blob/3d90d349ef3fdde9b7e89de4df4a2159c9e8697f/skill/motion-design/SKILL.md)
- Browser-to-video template · [skill/motion-design/scripts/render_template.py](https://github.com/howseen-ai/claude-motion-design/blob/3d90d349ef3fdde9b7e89de4df4a2159c9e8697f/skill/motion-design/scripts/render_template.py)
- Reference adaptation brief · [skill/motion-design/scripts/remake/BRIEF_TEMPLATE.md](https://github.com/howseen-ai/claude-motion-design/blob/3d90d349ef3fdde9b7e89de4df4a2159c9e8697f/skill/motion-design/scripts/remake/BRIEF_TEMPLATE.md)

## lemo-opuscar

[Pinned tree](https://github.com/lemomo-ai/lemo-opuscar/tree/3a7132b996be0241c1ea0ab180d519f06e6f10b6) · [All 3,840 tracked paths](upstream-inventory/lemo-opuscar.txt)

- [Upstream README](https://github.com/lemomo-ai/lemo-opuscar/blob/3a7132b996be0241c1ea0ab180d519f06e6f10b6/README.md)
- Individual style names, groups and suggested uses · [styleboard/catalog.json](https://github.com/lemomo-ai/lemo-opuscar/blob/3a7132b996be0241c1ea0ab180d519f06e6f10b6/styleboard/catalog.json)
- Style-specific instructions, demo code and assets · [styles/](https://github.com/lemomo-ai/lemo-opuscar/tree/3a7132b996be0241c1ea0ab180d519f06e6f10b6/styles)
- Additional skill entry points: [plugin/skills/lemo-opuscar/SKILL.md](https://github.com/lemomo-ai/lemo-opuscar/blob/3a7132b996be0241c1ea0ab180d519f06e6f10b6/plugin/skills/lemo-opuscar/SKILL.md), [tools/directory/SKILL.md](https://github.com/lemomo-ai/lemo-opuscar/blob/3a7132b996be0241c1ea0ab180d519f06e6f10b6/tools/directory/SKILL.md).

## onetake

[Pinned tree](https://github.com/feitangyuan/onetake/tree/abb6d17279cdc749e27e99aa534a062d8fd01ced) · [All 114 tracked paths](upstream-inventory/onetake.txt)

- [Upstream README](https://github.com/feitangyuan/onetake/blob/abb6d17279cdc749e27e99aa534a062d8fd01ced/README.md)
- Continuous motion workflow · [SKILL.md](https://github.com/feitangyuan/onetake/blob/abb6d17279cdc749e27e99aa534a062d8fd01ced/SKILL.md)
- Motion checks · [scripts/test_motion.js](https://github.com/feitangyuan/onetake/blob/abb6d17279cdc749e27e99aa534a062d8fd01ced/scripts/test_motion.js)
- Frame comparison · [scripts/frame_diff.py](https://github.com/feitangyuan/onetake/blob/abb6d17279cdc749e27e99aa534a062d8fd01ced/scripts/frame_diff.py)
- Worked examples · [cases/](https://github.com/feitangyuan/onetake/tree/abb6d17279cdc749e27e99aa534a062d8fd01ced/cases)

## herk-edit-kit

[Pinned tree](https://github.com/nateherkai/herk-edit-kit/tree/10511e5af86fc47756ea89803b397422e2d89284) · [All 1,050 tracked paths](upstream-inventory/herk-edit-kit.txt)

- [Upstream README](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/README.md)
- Raw-to-social editing sequence · [docs/EDITING-PLAYBOOK.md](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/docs/EDITING-PLAYBOOK.md)
- Style library registry · [style-library/registry.json](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/style-library/registry.json)
- Vox style metadata · [style-library/01-vox-explainer/style.json](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/style-library/01-vox-explainer/style.json)
- Concrete comparison card · [style-library/01-vox-explainer/cards/tier1/t1-overview-compare.html](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/style-library/01-vox-explainer/cards/tier1/t1-overview-compare.html)
- Editable scene templates · [style-templates/](https://github.com/nateherkai/herk-edit-kit/tree/10511e5af86fc47756ea89803b397422e2d89284/style-templates)
- Additional skill entry points: [.agents/skills/cut-mistakes/SKILL.md](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/.agents/skills/cut-mistakes/SKILL.md), [.agents/skills/cut-silences/SKILL.md](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/.agents/skills/cut-silences/SKILL.md), [.agents/skills/edit-video/SKILL.md](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/.agents/skills/edit-video/SKILL.md), [.agents/skills/gsap/SKILL.md](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/.agents/skills/gsap/SKILL.md), [.agents/skills/hyperframes-cli/SKILL.md](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/.agents/skills/hyperframes-cli/SKILL.md), [.agents/skills/hyperframes-registry/SKILL.md](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/.agents/skills/hyperframes-registry/SKILL.md), [.agents/skills/hyperframes-video-beats/SKILL.md](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/.agents/skills/hyperframes-video-beats/SKILL.md), [.agents/skills/hyperframes/SKILL.md](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/.agents/skills/hyperframes/SKILL.md), [.agents/skills/make-a-video/SKILL.md](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/.agents/skills/make-a-video/SKILL.md), [.agents/skills/motion-showreel/SKILL.md](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/.agents/skills/motion-showreel/SKILL.md), [.agents/skills/short-form-edit/SKILL.md](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/.agents/skills/short-form-edit/SKILL.md), [.agents/skills/short-form-video/SKILL.md](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/.agents/skills/short-form-video/SKILL.md), [.agents/skills/style-library/SKILL.md](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/.agents/skills/style-library/SKILL.md), [.agents/skills/video-storytelling/SKILL.md](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/.agents/skills/video-storytelling/SKILL.md), [.agents/skills/website-to-hyperframes/SKILL.md](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/.agents/skills/website-to-hyperframes/SKILL.md).

## rea-video

[Pinned tree](https://github.com/JuneYaooo/rea-video/tree/07dd587119e884f7c50fbfae92e47840de86bea5) · [All 938 tracked paths](upstream-inventory/rea-video.txt)

- [Upstream README](https://github.com/JuneYaooo/rea-video/blob/07dd587119e884f7c50fbfae92e47840de86bea5/README.md)
- Breakdown format · [docs/videomd.md](https://github.com/JuneYaooo/rea-video/blob/07dd587119e884f7c50fbfae92e47840de86bea5/docs/videomd.md)
- Shot analysis · [docs/decompose.md](https://github.com/JuneYaooo/rea-video/blob/07dd587119e884f7c50fbfae92e47840de86bea5/docs/decompose.md)
- Rebuild planning · [docs/replicate.md](https://github.com/JuneYaooo/rea-video/blob/07dd587119e884f7c50fbfae92e47840de86bea5/docs/replicate.md)
- CLI and its options · [docs/cli.md](https://github.com/JuneYaooo/rea-video/blob/07dd587119e884f7c50fbfae92e47840de86bea5/docs/cli.md)
- Additional skill entry points: [skills/rea-video/SKILL.md](https://github.com/JuneYaooo/rea-video/blob/07dd587119e884f7c50fbfae92e47840de86bea5/skills/rea-video/SKILL.md).

## open-edit

[Pinned tree](https://github.com/veedstudio/open-edit/tree/e4dc93892268eaf04b64386935ba6e53098a5c79) · [All 286 tracked paths](upstream-inventory/open-edit.txt)

- [Upstream README](https://github.com/veedstudio/open-edit/blob/e4dc93892268eaf04b64386935ba6e53098a5c79/README.md)
- Editing workflow · [.claude/skills/open-edit/SKILL.md](https://github.com/veedstudio/open-edit/blob/e4dc93892268eaf04b64386935ba6e53098a5c79/.claude/skills/open-edit/SKILL.md)
- Individual editing, caption, motion and rendering commands · [cli/src/commands/](https://github.com/veedstudio/open-edit/tree/e4dc93892268eaf04b64386935ba6e53098a5c79/cli/src/commands)

## saas-motion-kit

[Pinned tree](https://github.com/tugrawork-creator/saas-motion-kit/tree/bc7a414d6b66ceb09dfaa511e6237f382571bc84) · [All 509 tracked paths](upstream-inventory/saas-motion-kit.txt)

- [Upstream README](https://github.com/tugrawork-creator/saas-motion-kit/blob/bc7a414d6b66ceb09dfaa511e6237f382571bc84/README.md)
- Pick a tone · [creative/tone-matrix.md](https://github.com/tugrawork-creator/saas-motion-kit/blob/bc7a414d6b66ceb09dfaa511e6237f382571bc84/creative/tone-matrix.md)
- Compare transitions · [creative/transition-atlas.md](https://github.com/tugrawork-creator/saas-motion-kit/blob/bc7a414d6b66ceb09dfaa511e6237f382571bc84/creative/transition-atlas.md)
- Production steps in order · [playbook/](https://github.com/tugrawork-creator/saas-motion-kit/tree/bc7a414d6b66ceb09dfaa511e6237f382571bc84/playbook)
- Same story across several visual directions · [examples/six-films/README.md](https://github.com/tugrawork-creator/saas-motion-kit/blob/bc7a414d6b66ceb09dfaa511e6237f382571bc84/examples/six-films/README.md)
- Additional skill entry points: [.claude/skills/saas-motion-video/SKILL.md](https://github.com/tugrawork-creator/saas-motion-kit/blob/bc7a414d6b66ceb09dfaa511e6237f382571bc84/.claude/skills/saas-motion-video/SKILL.md).

## hyperframes-community-skills

[Pinned tree](https://github.com/heygen-com/hyperframes-community-skills/tree/ba7a0bb6d3567d124c51f6074625043bfe0b32eb) · [All 139 tracked paths](upstream-inventory/hyperframes-community-skills.txt)

- [Upstream README](https://github.com/heygen-com/hyperframes-community-skills/blob/ba7a0bb6d3567d124c51f6074625043bfe0b32eb/README.md)
- 3D caption treatment · [skills/camera-3d-captions/SKILL.md](https://github.com/heygen-com/hyperframes-community-skills/blob/ba7a0bb6d3567d124c51f6074625043bfe0b32eb/skills/camera-3d-captions/SKILL.md)
- Paint-on treatment · [skills/p5-paint-animation/SKILL.md](https://github.com/heygen-com/hyperframes-community-skills/blob/ba7a0bb6d3567d124c51f6074625043bfe0b32eb/skills/p5-paint-animation/SKILL.md)
- Side-by-side screen compositing · [skills/duo/SKILL.md](https://github.com/heygen-com/hyperframes-community-skills/blob/ba7a0bb6d3567d124c51f6074625043bfe0b32eb/skills/duo/SKILL.md)
- Additional skill entry points: [skills/day-in-my-life/SKILL.md](https://github.com/heygen-com/hyperframes-community-skills/blob/ba7a0bb6d3567d124c51f6074625043bfe0b32eb/skills/day-in-my-life/SKILL.md), [skills/prod-by-claude/SKILL.md](https://github.com/heygen-com/hyperframes-community-skills/blob/ba7a0bb6d3567d124c51f6074625043bfe0b32eb/skills/prod-by-claude/SKILL.md), [skills/session-story/SKILL.md](https://github.com/heygen-com/hyperframes-community-skills/blob/ba7a0bb6d3567d124c51f6074625043bfe0b32eb/skills/session-story/SKILL.md), [skills/vox-explainer/SKILL.md](https://github.com/heygen-com/hyperframes-community-skills/blob/ba7a0bb6d3567d124c51f6074625043bfe0b32eb/skills/vox-explainer/SKILL.md), [skills/x-posting-license/SKILL.md](https://github.com/heygen-com/hyperframes-community-skills/blob/ba7a0bb6d3567d124c51f6074625043bfe0b32eb/skills/x-posting-license/SKILL.md).

## snapcn

[Pinned tree](https://github.com/shadcn-labs/snapcn/tree/18b973d7592adf2099a4d5cc2d8970862a4e1172) · [All 1,190 tracked paths](upstream-inventory/snapcn.txt)

- [Upstream README](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/README.md)
- Searchable component guide · [skills/snapcn/references/components/index.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/skills/snapcn/references/components/index.md)
- Composition patterns · [skills/snapcn/references/archetypes/index.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/skills/snapcn/references/archetypes/index.md)
- Editable Remotion component source · [registry/](https://github.com/shadcn-labs/snapcn/tree/18b973d7592adf2099a4d5cc2d8970862a4e1172/registry)
- Additional skill entry points: [.claude/skills/animation-vocabulary/SKILL.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/.claude/skills/animation-vocabulary/SKILL.md), [.claude/skills/apple-design/SKILL.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/.claude/skills/apple-design/SKILL.md), [.claude/skills/design-system/SKILL.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/.claude/skills/design-system/SKILL.md), [.claude/skills/emil-design-eng/SKILL.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/.claude/skills/emil-design-eng/SKILL.md), [.claude/skills/find-animation-opportunities/SKILL.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/.claude/skills/find-animation-opportunities/SKILL.md), [.claude/skills/improve-animations/SKILL.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/.claude/skills/improve-animations/SKILL.md), [.claude/skills/interactivity-best-practices/SKILL.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/.claude/skills/interactivity-best-practices/SKILL.md), [.claude/skills/motion-quality/SKILL.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/.claude/skills/motion-quality/SKILL.md), [.claude/skills/review-animations/SKILL.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/.claude/skills/review-animations/SKILL.md), [.claude/skills/ux-ui-maxpro/SKILL.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/.claude/skills/ux-ui-maxpro/SKILL.md), [skills/remotion-explainer-video/SKILL.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/skills/remotion-explainer-video/SKILL.md), [skills/remotion-kinetic-typography/SKILL.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/skills/remotion-kinetic-typography/SKILL.md), [skills/remotion-launch-video/SKILL.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/skills/remotion-launch-video/SKILL.md), [skills/remotion-logo-animation/SKILL.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/skills/remotion-logo-animation/SKILL.md), [skills/remotion-motion-graphics/SKILL.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/skills/remotion-motion-graphics/SKILL.md), [skills/remotion-product-demo/SKILL.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/skills/remotion-product-demo/SKILL.md), [skills/snapcn/SKILL.md](https://github.com/shadcn-labs/snapcn/blob/18b973d7592adf2099a4d5cc2d8970862a4e1172/skills/snapcn/SKILL.md).

## ffmpeg-skill

[Pinned tree](https://github.com/kajisho5/ffmpeg-skill/tree/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65) · [All 425 tracked paths](upstream-inventory/ffmpeg-skill.txt)

- [Upstream README](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/README.md)
- Media operation workflow · [SKILL.md](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/SKILL.md)
- Inputs, outputs and machine-readable discovery · [docs/contract.md](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/docs/contract.md)
- Local media operations · [scripts/](https://github.com/kajisho5/ffmpeg-skill/tree/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/scripts)
- Additional skill entry points: [.claude/skills/build-artifacts/SKILL.md](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/.claude/skills/build-artifacts/SKILL.md), [.claude/skills/ci-pipeline-synthesizer/SKILL.md](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/.claude/skills/ci-pipeline-synthesizer/SKILL.md), [.claude/skills/code-review/SKILL.md](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/.claude/skills/code-review/SKILL.md), [.claude/skills/concurrent-branches/SKILL.md](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/.claude/skills/concurrent-branches/SKILL.md), [.claude/skills/cross-surface-changes/SKILL.md](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/.claude/skills/cross-surface-changes/SKILL.md), [.claude/skills/defect-reports/SKILL.md](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/.claude/skills/defect-reports/SKILL.md), [.claude/skills/destructive-operations/SKILL.md](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/.claude/skills/destructive-operations/SKILL.md), [.claude/skills/git-hygiene/SKILL.md](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/.claude/skills/git-hygiene/SKILL.md), [.claude/skills/github-actions/SKILL.md](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/.claude/skills/github-actions/SKILL.md), [.claude/skills/mcp-server-design/SKILL.md](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/.claude/skills/mcp-server-design/SKILL.md), [.claude/skills/release-management/SKILL.md](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/.claude/skills/release-management/SKILL.md), [.claude/skills/reproducing-ci-locally/SKILL.md](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/.claude/skills/reproducing-ci-locally/SKILL.md), [.claude/skills/sibling-sweep/SKILL.md](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/.claude/skills/sibling-sweep/SKILL.md), [.claude/skills/verifying-external-behavior/SKILL.md](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/.claude/skills/verifying-external-behavior/SKILL.md), [skills/ffmpeg-skill/SKILL.md](https://github.com/kajisho5/ffmpeg-skill/blob/f1c97cbffeac71b8fdfca2f790ceb00db3bcce65/skills/ffmpeg-skill/SKILL.md).

## hyperframes

[Pinned tree](https://github.com/heygen-com/hyperframes/tree/95e4e7f880f5005211412e926b307f4a53f47246) · [All 10,328 tracked paths](upstream-inventory/hyperframes.txt)

- [Upstream README](https://github.com/heygen-com/hyperframes/blob/95e4e7f880f5005211412e926b307f4a53f47246/README.md)
- CLI workflow and validation · [skills/hyperframes-cli/SKILL.md](https://github.com/heygen-com/hyperframes/blob/95e4e7f880f5005211412e926b307f4a53f47246/skills/hyperframes-cli/SKILL.md)
- Component selection and installation · [skills/hyperframes-registry/SKILL.md](https://github.com/heygen-com/hyperframes/blob/95e4e7f880f5005211412e926b307f4a53f47246/skills/hyperframes-registry/SKILL.md)
- Individual blocks and components · [registry/registry.json](https://github.com/heygen-com/hyperframes/blob/95e4e7f880f5005211412e926b307f4a53f47246/registry/registry.json)
- Editable assets and source · [registry/](https://github.com/heygen-com/hyperframes/tree/95e4e7f880f5005211412e926b307f4a53f47246/registry)
- Additional skill entry points: [.agents/skills/captions-overlay/SKILL.md](https://github.com/heygen-com/hyperframes/blob/95e4e7f880f5005211412e926b307f4a53f47246/.agents/skills/captions-overlay/SKILL.md), [.agents/skills/changelog-video/SKILL.md](https://github.com/heygen-com/hyperframes/blob/95e4e7f880f5005211412e926b307f4a53f47246/.agents/skills/changelog-video/SKILL.md), [.agents/skills/cut-the-curve/SKILL.md](https://github.com/heygen-com/hyperframes/blob/95e4e7f880f5005211412e926b307f4a53f47246/.agents/skills/cut-the-curve/SKILL.md), [.agents/skills/motion-doctrine/SKILL.md](https://github.com/heygen-com/hyperframes/blob/95e4e7f880f5005211412e926b307f4a53f47246/.agents/skills/motion-doctrine/SKILL.md), [.agents/skills/oversized-cursor/SKILL.md](https://github.com/heygen-com/hyperframes/blob/95e4e7f880f5005211412e926b307f4a53f47246/.agents/skills/oversized-cursor/SKILL.md), [.agents/skills/seam-craft/SKILL.md](https://github.com/heygen-com/hyperframes/blob/95e4e7f880f5005211412e926b307f4a53f47246/.agents/skills/seam-craft/SKILL.md), [skills/figma/SKILL.md](https://github.com/heygen-com/hyperframes/blob/95e4e7f880f5005211412e926b307f4a53f47246/skills/figma/SKILL.md), [skills/hyperframes/SKILL.md](https://github.com/heygen-com/hyperframes/blob/95e4e7f880f5005211412e926b307f4a53f47246/skills/hyperframes/SKILL.md), [skills/media-use/SKILL.md](https://github.com/heygen-com/hyperframes/blob/95e4e7f880f5005211412e926b307f4a53f47246/skills/media-use/SKILL.md), [skills/remotion-to-hyperframes/SKILL.md](https://github.com/heygen-com/hyperframes/blob/95e4e7f880f5005211412e926b307f4a53f47246/skills/remotion-to-hyperframes/SKILL.md), [skills/reverse-any-video/SKILL.md](https://github.com/heygen-com/hyperframes/blob/95e4e7f880f5005211412e926b307f4a53f47246/skills/reverse-any-video/SKILL.md), [skills/slideshow/SKILL.md](https://github.com/heygen-com/hyperframes/blob/95e4e7f880f5005211412e926b307f4a53f47246/skills/slideshow/SKILL.md), [skills/style-sampling/SKILL.md](https://github.com/heygen-com/hyperframes/blob/95e4e7f880f5005211412e926b307f4a53f47246/skills/style-sampling/SKILL.md).
