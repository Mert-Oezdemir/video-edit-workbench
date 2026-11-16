# On-demand video tools — agent reference / İhtiyaç halinde araç kataloğu

This is a recommendation catalog, not an install list. The default engine remains
Python, NumPy, FFmpeg/FFprobe, and a single local Whisper backend. No extra tool,
model, service or dependency is mandatory. Any tool-capable AI agent can choose
and install a suitable optional tool during a specific job when the existing
engine is insufficient. A chat-only model cannot install anything; its host
agent or the user must execute the operation.

For task-specific workflows and the 16 upstream video projects, consult
[production routes](production-routes.md).

The [upstream resource inventory](upstream-inventory.md) maps these projects to specific resources and pins the source revisions.

## Decision protocol

1. Identify the intended visual/audio improvement and whether the existing
   FFmpeg filters, SRT/ASS cards, existing scripts or GSAP template can do it.
2. If not, determine the lightest optional tool that fills the gap. Check what
   is already installed, the official docs, current OS/Python/Node compatibility,
   license, download size, CPU/RAM/GPU requirements and trustworthiness.
3. If the task needs it, the agent may install the chosen dependency without
   asking the user to choose between tools, subject to host permissions. Use an
   isolated project-local environment (e.g. venv, local npm workspace, portable
   executable) and a compatible pinned version. Do not add optional packages to
   the core dependency manifest or install all recommendations. Do not escalate
   privileges, change system PATH/settings, use paid services, upload media, or
   download unusually large models/assets without explicit user authorization.
   Do not bypass approval or sandbox controls.
4. Test a small representative excerpt first. If useful, use it only for the
   relevant shots. Record tool/version, purpose, installation source, license,
   local commands, output and any limitations in work/NOTES.md. Reuse the tool
   next time if compatible; prefer local cache over repeated downloads.
5. Keep raw media unchanged. Anchor derived assets to program time and review
   duration, synchronization, framing and audio. If unavailable or unsuccessful,
   use the existing fallback and report the limitation.

## Catalog (choose one where appropriate; never install everything)

| Need | Existing/lightest choice first | Optional tool and official documentation |
|---|---|---|
| Silence and retakes | Existing cuts.py and Whisper | [Auto-Editor](https://auto-editor.com/) for alternate silence/motion-based rough editing |
| Scene and shot detection | FFmpeg scene/black/freeze filters, visual_review.py | [PySceneDetect](https://www.scenedetect.com/docs/latest/) for detailed shot indexing |
| Face-aware crop or card placement | Manual framing and FFmpeg crop | [MediaPipe](https://developers.google.com/edge/mediapipe/solutions/vision/face_detector) for face coordinates, [OpenCV](https://docs.opencv.org/) for tracking and image analysis |
| Zoom, pan, highlight | FFmpeg crop/scale/zoompan/drawbox, GSAP | OpenCV only for tracking a moving target |
| Captions and kinetic typography | Existing SRT/ASS and GSAP | [Lottie](https://airbnb.io/lottie/) for compatible existing vector animation assets |
| Motion graphics, animated UI | Existing HTML/CSS/GSAP | [Remotion](https://www.remotion.dev/docs/) for React-based compositions when they justify a separate renderer |
| 3D explanation | Existing browser scene, [Three.js](https://threejs.org/docs/) if needed | [Blender](https://docs.blender.org/) for 3D compositing/rendering (heavy; only for specific shots) |
| Mathematical diagrams | SVG/CSS or GSAP | [Manim](https://docs.manim.community/) for mathematical animations |
| Cutouts/backgrounds | FFmpeg masks or an existing transparent asset | [rembg](https://github.com/danielgatis/rembg) for still-image cutouts; not a temporally stable video segmentation solution. MediaPipe segmentation for video when appropriate |
| B-roll / visual evidence | User's own footage, local media; insert via FFmpeg | PySceneDetect for local clip indexing; externally sourced media only when authorized and licensed |
| Color correction | FFmpeg eq/curves/colorbalance/lut3d | OpenCV only for specialized analysis; review source/output side by side |
| Shake stabilization | Existing FFmpeg deshake; vidstab if available in build | OpenCV only for more specialized motion tracking |
| Voice cleanup | Preserve voice; existing gain adjustment | FFmpeg highpass/notch/afftdn or [RNNoise](https://github.com/xiph/rnnoise) only when user asks for processing, with A/B preview |
| Sound effects | Existing sfx.py synthesized library | Earshot-style workflow optionally: assess its actual upstream repo, license, provenance and need before downloading; don't install from an unverified name |
| Graphics, plots, thumbnails | SVG/HTML/CSS, FFmpeg | [Pillow](https://pillow.readthedocs.io/), [Matplotlib](https://matplotlib.org/stable/) for raster graphics or genuine data charts |
| Edit interchange | Existing JSON EDL and program | [OpenTimelineIO](https://opentimelineio.readthedocs.io/) if another editor needs an interchange format; check adapter support |
| Advanced publishing formats | Existing FFmpeg output | No added dependency unless a target format actually requires one |

For filters see [FFmpeg official reference](https://ffmpeg.org/ffmpeg-filters.html).
For every visual effect, prefer clarity and restraint over decoration.
Do not silently replace the established editing engine; optional tools produce
intermediate clips, overlays, audio or metadata that the existing engine can
consume. Check asset and tool licenses independently; never assume generated or
downloaded content is automatically cleared for commercial publication.

## Türkçe kısa kural

Önce mevcut araçlarla çöz. Yetmiyorsa bu katalogdan sadece işe yarayan aracı
seç, resmi kaynağından proje ortamına kur, kısa bir parçada dene ve kullan.
Kullanıcı her seferinde araç seçmek zorunda değildir. İzin, ücret, gizlilik veya
sistem geneline kurulum gerektiğinde onay al. Gerek yoksa hiçbir şey kurma.
Bu katalog bir öneri listesidir; araçlar bu repoya entegre edilmiş veya
test edilmiş sayılmaz.
