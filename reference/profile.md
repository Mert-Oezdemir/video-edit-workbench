# The creator profile

The profile is how this skill remembers a creator between videos. It is written on the first run (see "First run" in `SKILL.md`) and read at the start of every project.

- Location: `~/.claude/video-edit/profile.md`
- Logo and other brand files: `~/.claude/video-edit/brand/`
- It is personal. It never goes into a shared project folder or a repository.

## Format

Plain Markdown, one field per line, so both the user and Claude can read and edit it. Leave a field out when the user skipped it; the defaults in `reference/style.md` and `reference/audio.md` apply then.

```markdown
# Creator profile

name: Name Surname
role: Developer · Tech creator
channel: Channel name
platforms: YouTube, Instagram
spoken_language: en
screen_languages: en            # or "tr + en", both at the same size
accent: "#2E7D6B"
support_colors: "#F4F4F1", "#16181C"
avoid_colors: red, neon green
logo: ~/.claude/video-edit/brand/logo.svg
logo_use: lower third, end screen
font: default
usual_videos: educational, tutorial
motion: calm                    # calm / medium / energetic
sound_effects: only when a sound is the subject   # never / only when a sound is the subject / also quiet on transitions
music: no
loudness: YouTube -14 LUFS
captions: yes, en
deliverables: 4K, chapters list
never: glows, italics, emoji

## Lasting rules

- 2026-01-15: no sound on transitions
- 2026-01-15: chapter veils short, about 1.5 s
```

## How the fields are used

| Field | Used for |
|---|---|
| `name`, `role` | the lower third (once, early) and the end screen |
| `accent`, `support_colors` | the scene's `--accent` and secondary tokens; derive the text tint from the accent and check contrast (`reference/style.md`, section 2) |
| `avoid_colors`, `never` | hard limits for every scene |
| `logo`, `logo_use` | only where the user allowed it, small, never over the face |
| `screen_languages` | one or two lines on every card, same size |
| `motion`, `usual_videos` | the default video type and entrance speeds |
| `sound_effects`, `music` | whether `cue()` is used at all, and where |
| `loudness`, `captions`, `deliverables` | the final render and the hand-over list |
| Lasting rules | everything the user said should hold for every video; add new ones with the date as soon as they are said |
