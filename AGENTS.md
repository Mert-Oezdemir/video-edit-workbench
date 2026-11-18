# Video Edit Workbench — agent instructions

Any coding or tool-capable AI can use this repository. The editing engine is
provider-neutral; no Claude dependency or mandatory paid API.

- First read reference/agent-capabilities.md. Treat the user's natural-language
  request as the job brief; choose the execution path yourself. A fixed preset
  in produce.py is not the limit of FFmpeg or of the agent's available tools.
  Distinguish implemented commands, local operations requiring a composed
  command, optional installations, and unavailable/paid services. Verify the
  current machine before promising an output. Never claim catalog entries are
  installed integrations or silently replace the requested format.

- Before editing any new video, follow reference/editorial-intake.md: inspect
  the topic, requirements, supplied material and available options; summarize
  the plan and ask once about current-source research and user-provided additions
  unless already answered. Do not change factual content without authorization.

- Default to Python + NumPy + FFmpeg/FFprobe + one local Whisper backend.
- Read reference/low-token.md for the compact planning contract. Run existing
  scripts instead of rewriting them. Keep verbose logs out of model context.
- For executable three-mode local production, read reference/production.md.
  Use produce.py init/doctor/preview/final with reviewed local manifests.
  Never pass preview approval on the user's behalf before they review it.
- For long-form-to-Shorts, faceless production, or personal-footage modes, read
  reference/free-video-tool-stack.md and reference/video-tool-registry.json.
  Use `python scripts/video_tool_stack.py plan --mode MODE` as an advisory
  routing plan. The CLI never installs tools or spends credits; review the plan
  and only use optional tools when the existing editor cannot meet the need.
- No external provider keys, paid Higgsfield/HeyGen generation, HyperFrames Pro,
  cloud rendering, or subscription API calls in a zero-extra-spend workflow.
  A coding-agent subscription does not imply free API access. Ghost Editor and
  Claude Shorts need a compatible existing agent plan and platform; rea-video
  analyzes but does not itself render. Never present these optional recipes as
  installed, compatible, or end-to-end tested. Preserve rights and source media.
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
