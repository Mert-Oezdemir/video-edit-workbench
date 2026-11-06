# Style: graphics that support the voice

The graphics in this skill are web pages: HTML + CSS + GSAP, with three.js when a 3D object helps explain something. A page is frozen at any time with `?t=SECONDS` and rendered frame by frame. Everything below is measured at a 1920×1080 stage (rendered at 2× for 4K). For a Short, the stage is 1080×1920.

## 1. What goes on screen

The goal of every graphic is understanding. Before building a beat, decide what would make the idea click for a viewer who has never heard of it (see "Creative direction" in `SKILL.md`): a drawing of the abstract idea, a small box that says what an unfamiliar tool is, the video's own measured data, a real screenshot, a before and after.

- **Never transcribe the narration onto the screen.** A card that repeats the sentence being spoken is a subtitle, not a graphic. Show what the voice cannot carry:
  - structure (steps, a list of options, a before/after)
  - numbers and data (counters, small charts)
  - the one key idea of a section, in a few words
  - a source shown the way it looks (an article window with its title and a highlighted line), with the link in the description, not on screen
  - a picture of the thing being discussed
- **Rephrase, do not quote.** "I stopped writing prompts" → "Writing prompts? / Stopped."
- **Fewer, longer-lasting cards.** In a talking-head video, one card that stays and grows as the speaker continues beats five cards flashing past. After the opening, reduce the density.
- **Never cover the face, the hands making a point, or the UI the speaker is pointing at.** Keep a visible cursor visible.

## 2. Palette (neutral default)

Take the colours from the creator profile (`reference/profile.md`) when there is one: its accent becomes `--accent`, its support colours the secondary tokens, and its avoid list is a hard limit. Use the channel's brand colour as the single accent if they have one. Otherwise use this neutral set. Keep one accent per video: two strong accents compete.

Dark (default for talking heads and screen recordings):

| Token | Value | Use |
|---|---|---|
| `--bg` | `#0B0C0E` | full-screen pages, veils |
| `--glass` | `rgba(18, 20, 24, 0.62)` | card fill over video |
| `--glass-solid` | `#16181C` | card fill over flat backgrounds |
| `--line` | `rgba(255, 255, 255, 0.10)` | 1 px card border, dividers |
| `--ink` | `#F4F4F1` | main text |
| `--ink-2` | `#BFC3CA` | secondary text |
| `--label` | `#9198A3` | kicker labels (never for content) |
| `--accent` | `#3D8BFF` | the one accent: bars, underlines, the active item |
| `--accent-ink` | `#A8C8FF` | accent-coloured text (second language line, emphasis) |
| `--good` / `--bad` / `--warn` | `#35C27D` / `#F0524D` / `#F2B53C` | meaning only (correct / wrong / caution) |

Light (paper look, for bright recordings or diagrams):

| Token | Value |
|---|---|
| `--bg` | `#F3F2EE` |
| `--glass` | `rgba(255, 255, 255, 0.78)` |
| `--line` | `rgba(0, 0, 0, 0.09)` |
| `--ink` | `#141518` |
| `--ink-2` | `#4A4F57` |
| `--accent` | `#1F6FEB` |
| `--accent-ink` | `#1557C0` |

With a brand colour: set `--accent` to it, derive `--accent-ink` by lightening it (dark theme) or darkening it (light theme) until text contrast on the card is at least 4.5:1. Check it; do not guess.

## 3. Glass cards

The basic unit. Dark frosted glass over the video, readable at phone size:

```css
.card {
  background: var(--glass);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 22px 26px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.28);   /* small and tight, never a big soft glow */
}
.card .kick { font: 600 20px/1 var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--label); }
.card .kick::before { content: ""; display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--accent); margin-right: 10px; }
.card h3 { font: 700 44px/1.1 var(--sans); color: var(--ink); }
.card .l2 { font: 700 44px/1.1 var(--sans); color: var(--accent-ink); }   /* second language: same size */
```

- **Blur:** a real `backdrop-filter: blur()` looks best but is expensive. Use it on a few small cards at most. Never put a full-screen live `backdrop-filter` or CSS `filter` on the stage: it stutters during playback. For a blurred full-frame background, draw a downscaled frame into a small canvas with `ctx.filter = 'blur()'` and scale it up.
- **Over a flat or already-blurred background** use `--glass-solid` without blur.
- Radius 10–16 px for cards, 6–8 px for chips. Keep one radius scale per video.

## 4. Typography

- One sans family for everything, plus one monospace for small labels and code. Variable fonts with Latin-extended glyphs (for Turkish, German, etc.) must be loaded and decoded before the first frame (`document.fonts.ready`).
- **Minimum sizes at 1080p:** content text 32 px, card titles 44 px and up, kicker labels 20 px, nothing under 18 px. Small mono labels are the first thing to become unreadable on a phone.
- Bold-ish weights (600–800) for anything the viewer must read. No thin weights, no italics, no low-opacity content text.
- Key phrases get a drawn underline in the accent colour, not a highlight box over the text.

## 5. Two languages on screen (optional)

When the channel has an international audience:

- Both languages at the **same size**, in two colours that both read clearly: main language in `--ink` on top, second language in `--accent-ink` below. No "EN / TR" labels on statements.
- Long source texts (a prompt, a quote): two columns side by side, rows aligned paragraph by paragraph, with column headers.
- Keep second-language text short; it doubles the reading load.

## 6. Layout

- Safe margins: 64 px from every frame edge (Short: also keep clear of the platform's UI at the bottom ~300 px and right ~120 px).
- **Nothing overlaps.** No stamp laid across a card, no card over another card, no tag over a screenshot. Put things beside each other.
- **Nothing sits cut off at the frame edge.** Every camera hold shows its group whole with about 44 px of margin.
- Mark the face (or any keep-out area) with `data-keepout` and every card with `data-box`; `scripts/audit.mjs` checks overlaps and margins at sampled times. Run it before every handover.

## 7. Motion

- Eased, not linear: `power3.out` / `expo.out` for entrances, `power2.inOut` for camera moves. No bounce or elastic eases unless it is a playful Short.
- **Word-locked:** an element appears when its word is said (about 0.1 s before the word's onset) and leaves after its sentence ends. Revealing a whole title at the start of a sentence feels like the graphics are running ahead.
- **Do not compress the timeline to shorten a scene.** Cut beats instead. A sped-up animation feels broken.
- Camera moves (zoom into a screenshot, pan across a board): slow, at most about 1 % scale change per frame. Never a hard jump in scale. Cut-synced punch-ins at 30 fps without motion blur read as jolts; use them rarely (about one per minute at most), or not at all.
- Typing animations type at a human pace with eased line reveals; a machine-gun typewriter is not motion design.
- Play once on load, then hold. No looping idle animation behind text the viewer is reading.

| Video type | Entrance length | Holds | Extras |
|---|---|---|---|
| Educational | 0.6–0.9 s | long | diagrams, step boards, calm camera pans across a large board |
| Talk | 0.5–0.8 s | long | keyword card that swaps on its word, counters, a lower third once |
| Tutorial | 0.4–0.7 s | medium | zoom on the UI, highlight boxes, numbered steps |
| Short | 0.25–0.45 s | short | bigger type, hook card in the first 2 s, captions with the spoken word underlined |

## 8. three.js

Use 3D when it explains: a part being assembled, an object that is the topic, a spatial idea. Not as decoration.

- The scene's time must come from the timeline (`TL.time()`), not from `requestAnimationFrame` deltas, so every frame renders the same in preview and in the final render.
- Prewarm shaders and load every model and texture before the first frame (the template's `ASSETS` list); the renderer waits for them.
- Keep the camera calm; let the object move.

## 9. Transitions and recurring elements

Transitions hide jumps and mark changes of topic. Use one where something actually changes, never as decoration. All of these are in `template/script.js`.

| Transition | When | What it looks like |
|---|---|---|
| Chapter veil | a new main chapter | a full-frame dark pane wipes in from the left behind a thin accent edge, shows "CHAPTER 03 / 08", the title (and second language) and a row of chapter marks, then wipes off to the right. About 1.5 s in total. The cut happens under the closed pane, so the viewer never sees the jump. |
| Text veil | a section that is not a chapter: an inserted clip, a montage of an older video, the goodbye | the same pane with its own short line ("Let's watch some clips from that video") |
| Blur dip | a cut where the picture jumps (the speaker moves, the screen changes) | the frame blurs for about 0.18 s into the cut and clears in about 0.32 s |
| Dark blur dip | a cut that removes a whole stretch and moves to another subject | blur plus about 80 % darkening in about 0.3 s, back in about 0.55 s |
| Speaker dip | on a full-screen board, the speaker's cut-out jumps between two takes | only the cut-out blurs and dims for a moment; the board stays still |
| Board in / out | a full-screen board (a diagram, data) replaces the video | the dark board fades in under a veil or over about 0.7 s, never in one frame; the speaker's cut-out slides to its place on the board and back. On a board without the speaker, the cut-out does not move at all. |

Rules:

- **No blur on plain cuts.** If neither the picture nor the subject jumps, a straight cut is best. Blur pulses on every cut look like a glitch.
- **Let the last word finish.** A veil or a dip starts after the last word of the section has fully decayed, on 0.3–0.6 s of the clip's own room tone. Never wipe across a word.
- **No sound on transitions by default.** Use transition sounds only when the profile asks for them. Sound effects belong to moments where a sound is the subject.
- **Short and identical.** Veils last about 1.5 s and are gone right after the chapter starts. Every veil in a video uses the same pane, edge and type.

Recurring elements:

- **Chapter chip:** a small chip in a top corner shows the current chapter number and title for the rest of the chapter.
- **Lower third:** the profile's name and role, once, early. It slides out from the edge or from behind the face cut-out and retracts the same way. The logo only if the profile allows it.
- **Like / subscribe:** if used, one short animation in the first minute and one at the end, never in the middle of an explanation.
- **End screen:** a calm typographic goodbye in the creator's own words ("See you in the next video"), revealed as it is said, wiped in like a veil. The video ends about one second after the last word. Do not draw a portrait or likeness of the creator unless they ask for one.

## 10. Avoid

- Radial gradients, round glows, vignettes and big soft shadows behind elements: they band into visible rings after video compression.
- Full-frame colour washes over the speaker (a sepia "old days" tint, a red alarm flash).
- Cream or white cards over a dark video: they pull all the attention. Keep cards darker than the subject.
- Physics distortions (rubbery UI, warps) and speed ramps unless the user asks.
- Other people's URLs on screen.
- Emoji as icons in cards.
