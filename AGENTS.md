# Video Edit Workbench — agent instructions

Any coding or tool-capable AI can use this repository. The editing engine is
provider-neutral; no Claude dependency or mandatory paid API.

- Before editing any new video, follow reference/editorial-intake.md: inspect
  the topic, requirements, supplied material and available options; summarize
  the plan and ask once about current-source research and user-provided additions
  unless already answered. Do not change factual content without authorization.

- Match the brief to the [production routes](reference/production-routes.md)
  before selecting tools. Use the route's review artifact, upstream selection
  cues and handoff checks. A plain talking-head edit can go straight to the
  lightweight workflow.
- Default to Python + NumPy + FFmpeg/FFprobe + one local Whisper backend.
- Read reference/low-token.md for the compact planning contract. Run existing
  scripts instead of rewriting them. Keep verbose logs out of model context.
- For captions and simple graphics read reference/creative-tools.md.
- For any task the existing tools cannot handle, consult reference/tool-catalog.md.
  Choose and install only the optional tool needed for the current task using
  official sources and a local isolated environment. No need to ask the user
  which tool to choose. Follow the host's permissions and the catalog's limits.
- Do not install every recommended package, add them to core dependencies, or
  require GPU, Node, a server, multiple agents, or an AI API for plain video edits.
- Read reference/audio.md before audio changes and reference/style.md for graphics.
  Preserve source files and preview changes before final render.

The optional tool catalog is advice, not pre-installed features. Keep the
existing pipeline and use advanced tools only for the concrete job.
