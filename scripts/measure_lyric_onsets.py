#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Measure real sung onsets for Japanese lyric phrases.

Reads a separated VOCAL track + a line table, returns per-文節 onset times.

Why not just divide the line duration by syllable count:
  real singing is 2-3x uneven between morae, and phrase-final notes hold.
Why not just use pitch changes:
  a phrase-final falling note looks exactly like a new note onset -- using it
  puts the next phrase ~0.4s early. See RULE_ENERGY_GATE below.

Requires: librosa, numpy, scipy
"""
import argparse
import json
import sys

import numpy as np

try:
    import librosa
except ImportError:
    sys.exit("need librosa: pip install librosa")

SMALL_KANA = set("ゃゅょぁぃぅぇぉゎャュョァィゥェォヮ")
IGNORE = set(" \u3000、。，．!?！？…・,")


def mora_count(s):
    """Approximate mora count: small kana merge into the previous mora."""
    n = 0
    for i, c in enumerate(s):
        if c in IGNORE:
            continue
        if c in SMALL_KANA and i > 0:
            continue
        n += 1
    return max(n, 1)


def candidates(seg, sr):
    """Legit note-change candidates inside one line."""
    hop = 128
    f0, _, _ = librosa.pyin(seg, fmin=150, fmax=900, sr=sr,
                            frame_length=2048, hop_length=hop)
    t = np.arange(len(f0)) * hop / sr

    with np.errstate(invalid="ignore"):
        midi = 69 + 12 * np.log2(np.maximum(f0, 1.0) / 440.0)
    midi = np.where(np.isnan(f0), np.nan, midi)

    # median filter: kill vibrato, keep note changes
    k = 9
    smooth = midi.copy()
    for i in range(len(midi)):
        w = midi[max(0, i - k):i + k + 1]
        w = w[~np.isnan(w)]
        smooth[i] = np.median(w) if len(w) else np.nan

    rms = librosa.feature.rms(y=seg, frame_length=1024, hop_length=hop)[0]
    if len(rms) < len(t):
        rms = np.pad(rms, (0, len(t) - len(rms)), mode="edge")
    rms = rms[:len(t)]
    voiced = ~np.isnan(f0)

    def is_real_change(c):
        """RULE_ENERGY_GATE: a note change must still have singing AFTER it.

        Without the second condition, the falling note at the end of a phrase
        is accepted as the start of the next one (measured on a real track:
        44.81 accepted, true onset 45.24 -- 0.43s early).
        """
        i = int(c * sr / hop)
        w1 = max(2, int(0.040 * sr / hop))
        w2 = max(3, int(0.180 * sr / hop))
        before = rms[max(0, i - w1):max(1, i - 1)]
        after = rms[i + 1:i + 1 + w1]
        if len(before) and len(after) and float(np.mean(after)) < 0.55 * float(np.mean(before)):
            return False                      # energy collapses: phrase end
        tail = voiced[i + 1:i + 1 + w2]
        return len(tail) > 0 and float(np.mean(tail)) >= 0.60

    pitch = []
    last = None
    for i in range(1, len(smooth)):
        if np.isnan(smooth[i]):
            continue
        if last is None:
            last = smooth[i]
            continue
        if abs(smooth[i] - last) >= 0.8:
            pitch.append(float(t[i]))
            last = smooth[i]
        else:
            last = 0.7 * last + 0.3 * smooth[i]

    energy = [float(o) for o in librosa.onset.onset_detect(
        y=seg, sr=sr, hop_length=hop, units="time", backtrack=False, delta=0.30, wait=3)]

    out = []
    for c in sorted([c for c in pitch if is_real_change(c)] + energy):
        if not out or c - out[-1] > 0.14:
            out.append(c)
    return out


def measure(vocal_path, lines, unsure_threshold=0.45):
    y, sr = librosa.load(vocal_path, sr=22050, mono=True)
    report = []
    for ln in lines:
        lid, t0, t1 = ln["id"], float(ln["start"]), float(ln["end"])
        disp = ln.get("disp") or ln.get("kana")
        if ln.get("latin") or not ln.get("kana"):
            half = t0 + (t1 - t0) * 0.52
            report.append({"id": lid, "start": t0, "end": t1, "latin": True,
                           "segs": [{"onset": t0, "text": disp[0], "snap": 0.0},
                                    {"onset": round(half, 3), "text": disp[1], "snap": 0.0}],
                           "unsure": True,
                           "note": "Latin: no pitch plateaus, split by duration ratio"})
            continue

        counts = [mora_count(k) for k in ln["kana"]]
        total = sum(counts)
        bnd = candidates(y[int(t0 * sr):int(t1 * sr)], sr)

        segs = [{"onset": round(t0, 3), "text": disp[0], "snap": 0.0}]
        acc = 0
        for k in range(1, len(ln["kana"])):
            acc += counts[k - 1]
            want = t0 + (acc / total) * (t1 - t0)
            if bnd:
                best = min(bnd, key=lambda b: abs((t0 + b) - want))
                on, snap = t0 + best, abs((t0 + best) - want)
            else:
                on, snap = want, 9.99
            segs.append({"onset": round(on, 3), "text": disp[k], "snap": round(snap, 3)})

        segs.sort(key=lambda s: s["onset"])
        unsure = any(s["snap"] > unsure_threshold for s in segs)
        report.append({"id": lid, "start": t0, "end": t1, "morae": counts,
                       "n_boundaries": len(bnd), "segs": segs, "unsure": unsure})
        print("%2d  %7.2f-%7.2f  bnd=%-2d morae=%-2d  %s%s" % (
            lid, t0, t1, len(bnd), total,
            "  ".join("%s@%.2f(%.2f)" % (s["text"], s["onset"], s["snap"]) for s in segs),
            "   <-- UNSURE, listen to it" if unsure else ""))
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vocal", required=True, help="separated vocals wav")
    ap.add_argument("--lines", required=True, help="line table json")
    ap.add_argument("--out", default="lyric_timing.json")
    ap.add_argument("--unsure", type=float, default=0.45,
                    help="snap deviation above this gets flagged (default 0.45s)")
    a = ap.parse_args()

    with open(a.lines, encoding="utf-8") as f:
        lines = json.load(f)
    rep = measure(a.vocal, lines, a.unsure)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)

    bad = [r["id"] for r in rep if r.get("unsure")]
    print("\nwrote %s" % a.out)
    print("UNSURE lines: %s" % (bad if bad else "none"))


if __name__ == "__main__":
    main()
