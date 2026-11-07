# NOTICE — provenance, third-party tools, licence status

## What is original work

Produced for this project, covered by the repository root `LICENSE`:

- `data/lines_final.json` — the 22-row timing dataset, including `phrases[].ovr`
  manual overrides and their written justifications.
- The vocal-envelope silence measurement used to re-anchor the 8 chorus lines and
  the final 2 lines.
- The independent verification procedure (bounds, ordering, overlap, timeline
  cross-check) and its measured results.
- `tools/build_subtitles.py` — the SRT / enhanced-LRC generator.
- All documentation in `docs/` and `README.md`.

The **format** (JSON with row/phrase/token timestamps), the **approach**
(forced alignment → envelope re-anchoring → manual rest override → independent
verification) and the **resulting numbers** are ours. The underlying forced
alignment algorithm is not.

## Third-party tools used — not shipped in this directory

| tool | role | licence | verification status |
|---|---|---|---|
| `Qwen3-ForcedAligner-0.6B` (Alibaba Qwen) | initial chunk alignment of the vocal track | Apache-2.0 per vendor blog | ⚠️ single source, not independently re-verified |
| `faster-whisper` base (CPU, int8) | sanity check of which characters belong to which line | MIT | local run only; **Whisper timestamps were NOT used** (measured ≈1.0s early on this track) |
| `numpy` | numeric work | BSD-3-Clause | import only, no copied code |
| `Pillow` | image work elsewhere in the project | HPND | import only, no copied code |
| `Demucs / htdemucs` | vocal stem separation upstream | MIT | upstream preprocessing only |
| `Lyria 3 Pro` | generated the song audio | vendor terms | audio not included here |

No source code from any of the above is copied into this directory.

## Explicitly evaluated and EXCLUDED from the delivery chain

| tool | why excluded |
|---|---|
| `torchaudio MMS_FA` | weights are **CC-BY-NC-4.0** (non-commercial) |
| `Echora MMS-300M` | personal non-commercial only; forbids paid services and redistribution |
| `MFA japanese_mfa` | CC-BY 4.0, but trained on read speech — singing is out of distribution |

These appear only in the research notes as evaluated alternatives.

## Caveats before any commercial reuse

1. The Apache-2.0 claim for `Qwen3-ForcedAligner` comes from a **single vendor
   page**. Re-verify against the model's own LICENSE file before commercial use.
2. The model card lists `Speech` under Audio Types. **Singing is not a documented
   supported input** — the alignment was used as a starting point and then
   corrected by envelope measurement, not trusted as ground truth.
3. The lyrics are original text written for this project; the audio was generated
   with Lyria 3 Pro. AI-assisted content has jurisdiction-dependent copyright
   status. Review before commercial reuse.
4. `docs/forced-alignment-research.md` cites third-party pages by URL. Those are
   references and measurements quoted in a research log, not copied content.
   One cited benchmark is a vendor comparison blog — its numbers are useful but
   its framing is not neutral.

## Privacy

No local machine paths, account names, client identifiers or personal contact
details are included in this directory. The MV render scripts (which contain
hard-coded local paths) are deliberately excluded.
