# The edit list (`work/edl.json`)

The EDL says which spoken pieces to keep and in what order. You (Claude) write it after reading the transcripts; `cuts.py` turns it into frame-exact pieces with cut points snapped to real word edges.

```json
{
  "fps": 30,
  "pace": "natural",
  "clips": {
    "a": "src/take-01.mov",
    "b": "src/take-02.mov"
  },
  "items": [
    { "chapter": "Intro" },
    { "clip": "a", "utt": 0 },
    { "clip": "a", "utt": [2, 4] },
    { "clip": "a", "utt": 5, "start": 61.20 },
    { "clip": "a", "utt": 6, "end": 70.10, "exact": true },
    { "chapter": "How it works" },
    { "clip": "b", "range": [12.00, 18.50] },
    { "note": "utt 7-9 of clip a are retakes of utt 6, dropped" }
  ]
}
```

| Field | Meaning |
|---|---|
| `fps` | Frame rate of the sources and the program. All clips must share it. |
| `pace` | `natural` (default) or `tight`. See `audio.md` section 2. |
| `clips` | Short id → source file (relative to the project). The id is also the transcript name. |
| `chapter` | Starts a chapter at this point of the program. Used for veils and the YouTube chapter list. |
| `clip` + `utt` | Keep utterance N (or N to M) from that clip's transcript. Pauses inside are shortened to the pace. |
| `start` / `end` | Source seconds that trim the utterance(s). Snapped to the quietest 10 ms within ±0.15 s unless `exact` is true. |
| `exact` | Use `start` / `end` exactly as given. For points you measured on the envelope yourself. |
| `range` | A raw source range kept as is: no pause removal. For reactions, a demo with sound, a laugh. |
| `keep_pauses` | On a `utt` item: keep its internal pauses (dramatic pause, a beat before a punch line). |
| `note` | Ignored. Write down why something was dropped; it helps the next review. |

Tips:

- Utterance numbers come from `work/transcripts/<clip>.txt`, which shows `#index [start-end] text`.
- To drop the first half-sentence of a utterance ("So the... So the main point is"), set `start` just before the second "So"; check the envelope around it with `python3 $SKILL/scripts/cuts.py --project . --peek a 60.5 62.0`.
- Keep the items in the order of the script, not the order of recording.
- After every change: `cuts.py`, `build.py audio video`, `verify.py`.
