# Piasu v22 — precise Japanese lyric timing

Word/mora-level timestamps for a 123.272s one-image anime MV, plus the verification
procedure and a standalone generator for SRT and enhanced LRC.

This is a **timing dataset and a reproducible method**, not a video renderer.
The audio, source illustration and MV render scripts are NOT included.

## What is here

| path | what |
|---|---|
| `data/lines_final.json` | source of truth: 22 rows, `s`/`e`, `phrases`, `toks`, `dur` |
| `data/timeline_ja.md` | human-readable 22-row timeline with phrase split points |
| `data/lyrics_v22.srt` | 22 line-level subtitle cues |
| `data/lyrics_v22_wordlevel.lrc` | enhanced LRC with A2 `<mm:ss.xx>` word tags |
| `docs/timing-verification.md` | full row table, word table, overrides, known defects |
| `docs/forced-alignment-research.md` | research notes: tool options, licences, failure modes |
| `tools/build_subtitles.py` | regenerates SRT / LRC / verification from `lines_final.json` |
| `NOTICE.md` | provenance, third-party tools, licence status, caveats |

## How the timing was produced

1. **Chunk alignment** with `Qwen3-ForcedAligner-0.6B` on the isolated vocal track
   (6 anchor points, ≤30ms). This gives the initial word/mora boundaries.
2. **Vocal-envelope silence measurement** re-anchored the 8 chorus lines and the
   final 2 lines, where forced alignment drifts on held notes and rests.
3. **4 manual phrase overrides** (`phrases[].ovr`) where uniform syllable splitting
   fails — e.g. row 1 has a 0.92s rest; evenly distributing syllables across a line
   with a rest produces wrong boundaries. The original reasons are preserved in the data.
4. **Independent verification**: row order, bounds, phrase/token containment,
   token overlap, cross-check against the markdown timeline. Numbers in
   `docs/timing-verification.md` are measured, not transcribed.

No third-party code is copied. `tools/build_subtitles.py` uses only the Python stdlib.

## Measured results

| item | value |
|---|---|
| rows / duration | 22 / 123.272s |
| word & mora tokens | 152 |
| token coverage | 75.68s |
| phrase overrides | 4 |
| inter-word silence gaps | 27 |
| zero-length tokens (`s == e`) | 11 |
| boundary violations (>10ms tolerance) | 0 |
| overlapping tokens | 0 |
| timeline cross-check mismatches | 0 |
| structural issues | 0 |

> Method note: the first version of the checker conflated zero-length tokens with
> boundary violations and reported 12 false "structural issues". Splitting the
> question into "out of bounds" / "zero length" / "overlap" with a 10ms tolerance
> produces the table above. A checker should ask *is this out of bounds*, not
> *is this perfect*.

## Regenerate

```bash
python tools/build_subtitles.py \
  --source data/lines_final.json \
  --timeline data/timeline_ja.md \
  --out data
```

## Known limitations

- `Qwen3-ForcedAligner` officially lists **Speech** as its supported audio type;
  singing is outside documented scope. See `NOTICE.md`.
- 11 zero-length tokens are defects in the aligner output. Do not allocate visible
  duration to them or you get 0-frame flicker.
- English rows 12 and 20 have 7 tokens each; their word timings were flagged as
  unreliable and should be visually checked before use.
- A row before the last line contains a 0.94s rest; the corresponding storyboard
  block is only 1.46s.
- **This is a timing source, not proof that a frame actually drew the text.**
  A timeline self-check only proves a phrase falls inside the correct shot.
  Always inspect rendered frames.
- Lyrics are original text for this project; the song audio was generated with
  Lyria 3 Pro. Copyright status of AI-assisted text varies by jurisdiction —
  review before commercial reuse.

## Licence

Original work in this directory is covered by the repository root `LICENSE`.
Third-party tools and their licence status are listed in `NOTICE.md`.
