# Before editing: understand, research if useful, agree on the content

This is a mandatory editorial intake for the tool-capable agent managing a new
video job. It is not another service, dependency, model call or autonomous agent.
Do it once at the start, and reopen only if the subject or requirements change.

## 1. Understand the job before acting

Before cutting, installing optional tools, designing graphics or rendering:

- Read the request, available creator preferences, script/outline, notes and
  existing transcript. Inventory the supplied clips, images, screenshots,
  audio, reference documents and local capabilities. If no transcript exists,
  perform the minimum local non-destructive inspection/transcription necessary
  to understand the footage (reuse cached results). Do not claim to have seen
  or heard anything the available tools cannot actually inspect.
- Identify the subject, central message, intended audience, platform, purpose,
  language, length, aspect ratio/delivery format, desired style, source order,
  constraints and any crucial missing information. Distinguish user requirements
  from inferred defaults. Respect the existing footage, voice and author intent.
- Consider what could improve the explanation, pacing, evidence and visual
  presentation. Identify gaps, outdated or unverifiable claims, examples that
  could help, relevant illustrations and the tools/materials already available.
  Prefer existing lightweight tools; optional installations follow
  [tool-catalog.md](tool-catalog.md).
- Present a compact understanding and practical plan. Ask only consequential
  unresolved questions together, not a generic questionnaire. Never repeat
  questions already answered in the request or creator/project notes.

## 2. Consult the user about research and content additions

During that same first exchange, offer the user a choice unless already clearly
answered in the request:

- Keep the supplied content as-is and improve only the edit.
- Check relevant current sources, dates, facts and developments where this
  would materially improve the content; present findings and proposed updates
  before adding them.
- Use a new or updated detail, link, source, screenshot, clip or note the user
  wants to provide, either instead of research or alongside it.

Ask conversationally, for example in Turkish:
"Videonun konusunu ve mevcut malzemeyi inceledim. [Kısa özet ve somut öneri.]
Yalnızca mevcut içeriği mi kurgulayayım, yoksa güncel kaynakları araştırıp
iyileştirme önerileri de sunayım mı? Eklemek istediğin yeni bir bilgi, kaynak
veya görüntü var mı?"

If research is not useful, say so briefly and still offer any user-supplied
additions. If the user already requested research or additions, do not ask for
the same authorization again; clarify only meaningful outstanding decisions.
A clear edit-only instruction means no external content research/additions.
If a user wants no questions and gave a sufficient brief, proceed within it
without inventing additions; document the editorial assumptions.
Do not repeatedly interrupt the user about small implementation choices.

## 3. If research is authorized

Use trusted, relevant, current and preferably primary sources. For
time-sensitive claims check both publication date and the date of the event
or data. Compare important claims, distinguish confirmed facts from opinions
or unresolved conflicts, and note the research date. Do not claim web research
if browsing is unavailable. Ask for supplied links/documents when necessary.
Do not upload private footage or transcripts to external services without
authorization. Search public sources using non-sensitive topic descriptions.

Keep a lightweight source record in work/NOTES.md or work/sources.md with
the actual URL, title, date where available, verified claim, proposed use,
and attribution/license for third-party assets. Do not invent citations,
quotes, screenshots, numbers, or supporting evidence. Label illustrative
graphics as illustrations and do not imply they are factual footage.

Present only material findings: what is current, what differs from the
original, what could be added, and why. Ask for the user's approval before
changing meaning, adding factual claims, rewriting narration, introducing
external footage/assets, or correcting a substantive claim. A user can
approve all proposed additions or select specific ones. If they explicitly
delegated these editorial decisions, apply only within the delegated scope
and report what changed. If an update needs narration the original recording
does not contain, propose an approved title card, insert, or new recording;
never fabricate the speaker's words or voice.

## 4. Production

Record the agreed subject, requirements, assumptions, research choice and
approved additions in the local project work/NOTES.md. Keep original and
new material distinguishable. Then run the compact provider-neutral edit,
using one planner and existing scripts first. Keep research notes separate
from the rough-cut JSON; send only needed facts to the relevant planning step.
Preview and request feedback before final output. This workflow is editorial
guidance for the host agent, not a runtime permission gate in the Python CLI.
