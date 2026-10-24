#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Two checks that catch the two most common lyric-subtitle delivery bugs.

1. COVER   every character of the full line must also appear in the background
           typography. Rule R8. A missing particle is invisible to you after
           having read the line 50 times, and instantly obvious to a viewer.
2. ORDER   the concatenation of the reveal segments must equal the full line --
           catches dropped or duplicated phrases after a rebuild.

Exit code 1 if either check fails, so it can gate a render.

Usage:
  python check_lyric_coverage.py --lines lines.json
  python check_lyric_coverage.py --lines lines.json --strict
"""
import argparse
import json
import sys


def chars(s):
    """Characters that must be present, ignoring whitespace and punctuation."""
    skip = set(" \u3000\t\n、。，．!?！？…・,")
    return [c for c in s if c not in skip]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lines", required=True,
                    help='json: [{"id":9,"full":"君を見るたび","segs":[...],"bg":"君を見るたび"}]')
    ap.add_argument("--strict", action="store_true", help="treat UNSURE timings as failures")
    a = ap.parse_args()

    with open(a.lines, encoding="utf-8") as f:
        lines = json.load(f)

    fails = 0
    for ln in lines:
        lid = ln.get("id")
        full = ln.get("full", "")
        segs = ln.get("segs") or []
        bg_chars = set(chars(ln.get("bg", "")))

        missing = [c for c in chars(full) if c not in bg_chars]
        cover_ok = not missing

        joined = "".join(segs)
        order_ok = joined == full

        print("COVER line=%r missing=%r OK=%s" % (full, missing, cover_ok))
        print("ORDER segs=%r joined_equals_full=%s" % (segs, order_ok))
        if not cover_ok:
            print("  !! background typography is missing: %s" % "".join(missing))
            fails += 1
        if not order_ok:
            print("  !! segments do not reconstruct the line")
            fails += 1
        if a.strict and ln.get("unsure"):
            print("  !! timing flagged UNSURE")
            fails += 1
        print()

    if fails:
        print("FAILED: %d check(s)" % fails)
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
