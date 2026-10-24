# mv-jp-lyrics-subtitle

An agent skill for putting **Japanese song lyrics on screen the way a Japanese reader reads them** — not the way a renderer happens to wrap text.

Four mistakes this fixes, all of which "look fine" to a non-Japanese viewer and read as wrong instantly to a Japanese one:

| Mistake | What it produces | Fix |
|---|---|---|
| Timing by syllable count | every mora gets the same time; real singing is 2–3× uneven | measure onsets on the separated vocal track |
| Breaking mid-word | `君 / を見るたび` — a particle alone at line start | break at 文節 (bunsetsu) boundaries only |
| All-kana lyrics | the AI-generated lyric sheet written in hiragana, pasted straight to screen | 漢字仮名交じり normalisation |
| Snap-to-pitch-change | the phrase-final falling note is read as the next phrase's start, ~0.4 s early | energy gate: singing must continue for 180 ms |

## Install

Drop the folder into your agent's skills directory, or add it as a submodule. No build step, no dependencies beyond `librosa` / `numpy` for the measurement script.

## Use

```bash
# 1. measure real onsets from a separated vocal track
python scripts/measure_lyric_onsets.py --vocal vocals.wav --lines lines.json --out timing.json

# 2. gate the render on the two content checks
python scripts/check_lyric_coverage.py --lines lines.json
```

`lines.json`:

```json
[{"id": 9, "start": 42.26, "end": 48.00,
  "kana": ["きみを", "みるたび", "しんぞうがとまるの"],
  "disp": ["君を", "見るたび", "心臓が止まるの"]}]
```

Output flags any line whose snap deviation exceeds `--unsure 0.45` seconds, so you know which lines still need a human listen instead of shipping silent errors.

## What is in SKILL.md

- the eight hard rules (R1–R8) with counter-examples
- the three-stage onset algorithm and **why stage 3 cannot be skipped**, with the measured false positive (44.81 accepted vs 45.24 true)
- a kana → kanji normalisation table, and where *not* to over-kanji-ise
- typography numbers reverse-engineered from four commercial anime MVs (97–108 px main lyric, 270–670 px background type, no backing plate + 2–3 px stroke)
- vertical multi-column layout as visible phrase segmentation
- the vertical-typography height limit: `font_size ≤ 940 / (chars × 1.46)`, so an 8-character phrase physically cannot reach 97 px

## Honest limits

- English lines have no pitch plateaus; the script falls back to a 52 % duration split and marks the line `unsure`.
- Melisma (one syllable across several notes) produces more plateaus than syllables; snapping will drift. Listen to it.
- Any line with snap deviation > 0.45 s is **not measured**, it is guessed. The script says so.

## Licence

MIT. See `LICENSE`.
