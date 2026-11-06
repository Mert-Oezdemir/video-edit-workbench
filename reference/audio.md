# Audio: cuts, levels and sound effects

Read this before any cut, gain change or sound effect. Audio mistakes are the ones viewers notice first and forgive last, and they are exactly the ones you cannot hear. Every rule here exists because a measurement looked fine and a human ear said otherwise.

## 1. The voice is sacred

- **Never make the voice muffled.** Do not add noise reduction, EQ, compression, gates, de-essers or "enhancers" by default. Adaptive noise reduction and low-pass filters are the usual cause of a voice that sounds boxed, underwater or lisping in some places and fine in others. You cannot hear that happening.
- **Default processing is one linear gain.** The recording stays as it was, only louder or quieter. `build.py` does exactly this.
- Processing is allowed only when the user asks for it, and then only the minimum, with an A/B file for them to compare:
  - **A steady tonal whine** (a thin constant line in the spectrogram, often 7–20 kHz, visible in truly silent windows): narrow notch filters at those frequencies only.
  - **Hiss:** a static, profile-based reduction above about 2.5 kHz, a few dB at most, voice change ≤ 1–2 dB. Never an adaptive denoiser on the whole band.
  - **Rumble / hum below the voice:** a high-pass at 60–80 Hz.
  - **Too quiet even at full gain:** a gentle true-peak limiter (a few dB of gain reduction), see section 3.
- If the user says "it sounds muffled", "it hisses" or "you made it too loud", undo the processing first, then ask. Do not stack another filter on top.

## 2. Cutting: never clip a word

Whisper's word start and end times are approximate (often 0.1–0.4 s off around pauses) and SRT times are worse. **Cut points come from the energy envelope, not from Whisper.** `cuts.py` does this:

1. A 10 ms RMS envelope of each clip (dB). Speech regions = above a threshold set from the clip's own noise floor.
2. Inside a kept utterance, pauses longer than the pace's max gap are removed.
3. **Word ends:** the end is extended while the level stays above the soft floor (about −61 dB), up to 0.10 s, so a decaying last syllable is not chopped.
4. **Release bursts:** words ending in t, k, p, ç have a short silent closure followed by a burst (about 10–120 ms). If a short burst follows a short closure and silence follows it, it is kept. Without this rule, "basic" becomes "basi".
5. **Word starts:** the start is pulled back up to 0.06 s while the level is above the soft floor, so a soft onset is kept.
6. Margins: a small head before the first word and a tail after the last word, never reaching into the neighbouring speech.
7. Frame rounding goes outward: the cut never rounds into a word.
8. Every join gets a short fade: 4 ms in, 15 ms out. No clicks, no audible fade.

Pace presets (`edl.json` → `"pace"`):

| Pace | Head | Tail | Max kept pause | Feel |
|---|---|---|---|---|
| `natural` (default) | 0.10 s | 0.16 s | 0.35 s | Breathing room; educational and calm talks |
| `tight` | 0.04 s | 0.06 s | 0.15 s | Jump-cut YouTube pace; Shorts |

Rules learned the hard way:

- **Do not cut between two words that run together** (gap under ~0.2 s). Keep the sentence to its natural end instead; a cut there sounds like a chopped word.
- **A hand-set cut point must be checked against the envelope**, not against Whisper's word end. Whisper may end a word at its first syllable.
- **Snapping to the quietest 10 ms** near a hand-set point can land inside the previous or next word. Use `"exact": true` for points you measured yourself.
- **Re-transcribe after every build.** `verify.py` transcribes a window around every join. Read the joins: a half word, a doubled word ("and, and"), or a sentence that ends too early all show up there.
- **Hidden retakes** live inside a single Whisper utterance. A disfluency-heavy speaker can say "because I, because I actively" in one breath. When `verify.py` shows doubled phrases, split that utterance with `start`/`end` times.
- **Blank stares** are silent but visible: the speaker finishes, freezes, then restarts. Audio silence alone does not find them; check with a frame-difference measure or by asking the user. Cut them the same way as pauses.
- **Retakes that start the same way:** keep the take that is fluent to the end, not the first one.

## 3. Loudness

Targets for online video:

| Target | Value |
|---|---|
| Integrated loudness | about −14 LUFS (YouTube, most platforms). Acceptable range −16 to −13. |
| True peak | at most −1 dBTP |
| Loudness range (LRA) | a talking voice is usually 3–8 LU; much higher means a level problem |

- YouTube turns loud videos down to about −14 LUFS but generally does **not** turn quiet videos up. A video at −24 LUFS stays quiet and viewers keep changing the volume.
- `build.py` computes one gain: the smaller of (target − measured loudness) and (−1 dBTP − measured true peak). If the true peak stops the gain short of the target, it reports how many dB are missing. Then offer the user `--limiter`: a gentle true-peak limiter that allows the missing gain. Do not apply it silently.
- Measure correctly: `ebur128` on the actual stereo file. Downmixing with `-ac 1` sums the channels and reports a false peak about 3 dB too high. If you need mono, use `pan=mono|c0=c0`.
- Do not loudness-normalize twice. The final mix only checks the level; the gain was already set on the voice.

## 4. Mixing other sources

- **Inserted clips** (an old video, a screen recording with sound, a demo output): level each insert separately so its short-term loudness matches the surrounding voice. Recordings differ by 5–10 dB.
- **Synthetic or cloned voices** read louder than they measure: dry, even, bright. Sit them about 3 dB under the real voice and never brighten them with EQ.
- **Background music:** at least 18–22 dB under the voice while someone speaks. Dip it under speech; let it rise only in pauses and transitions.
- **Room tone, not digital silence.** When you need a short gap between two pieces, use a fraction of a second of the clip's own room tone. Pure digital zeros sound like a stop.

## 5. Sound effects

Effects are synthesized in Python from math (`scripts/sfx.py`): filtered noise with a moving filter for whooshes, short decaying sine bursts with a bit of noise for ticks and key presses, modal (inharmonic) partials for chimes. No downloads, no licences, fully reproducible.

Levels (peak, effect on its own):

| Use | Start at |
|---|---|
| Chapter transition whoosh (only when the profile asks for transition sounds) | −32 dBFS |
| UI tick / click / pop | −30 dBFS |
| Typing | −32 dBFS |
| Short (more energetic) | up to −26 dBFS |

- Effects must sit **under** the voice and never mask a word. Avoid placing a hit on top of a stressed syllable.
- Start quiet and let the user pull it up. Real corrections from practice: −32 dBFS was "can't hear it at all", −26 was "a bit less", −28 stuck. The same −28 whoosh was "a bit much" in a calmer video, and −34 stuck. The right level depends on the video; the user's ear decides.
- Normalize every effect type to a similar loudness so quiet types (a soft tick) are heard as well as loud ones (a whoosh).
- Many videos are better with no effects at all (serious educational parts, emotional parts). Ask, or follow the creator profile.
- **Default: no sound on transitions.** Veils, dips and board changes are silent unless the profile asks otherwise. Effects belong where a sound is the subject: demonstrating a whoosh and its level, the click of the button being explained.
- **Sync:** effects are cued from the scene timeline (`cue(t, name)`). The render exports the cue list, and `sfx.py track` renders the full-length effects track from it. Picture and sound come from the same clock, so they cannot drift.
- **Typing sounds** must follow the typing animation: one key sound per revealed character group, at the reveal time, with small random variation in pitch, level and timing so it does not sound like a machine gun. Never lay a generic typing loop under a typing animation; that is the classic "the keys don't match the text" mistake.

## 6. Captions and subtitles

- Captions follow the final audio exactly as spoken. Fix only misheard words (names, product names, technical terms); never rewrite sentences.
- Build captions from the **final** program audio, transcribed in chunks split at silences and padded with silence, not with neighbouring audio (neighbouring audio makes Whisper invent half words).
- Do not break inside fixed phrases (a number and its unit, a name).

## 7. What to report

After every build, report: program length, number of cuts, integrated LUFS, true peak, LRA, and the gain applied. If anything was limited, say by how much. Say what you could not verify by measurement and ask the user to listen to those spots (list timestamps).
