# Video Edit Workbench — agent instructions

Any coding or tool-capable AI can use this repository. The editing engine is
provider-neutral; no Claude dependency or mandatory paid API.

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
