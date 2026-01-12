#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from pypdf import PdfReader

BASE = Path(__file__).resolve().parent

MANUALS = [
    {
        "model": "FT1001",
        "original_pdf": "18V Cordless Drill manual new(FT1001)(1).pdf",
        "rewritten_txt": "FT1001_Drill_Manual_REWRITTEN.txt",
    },
    {
        "model": "FT1002",
        "original_pdf": "18V cordless oscillating tool manual  new(FT1002)(1).pdf",
        "rewritten_txt": "FT1002_OscillatingTool_Manual_REWRITTEN.txt",
    },
    {
        "model": "FT1003",
        "original_pdf": "18V Cordless Mini Saw manual new(FT1003)(1).pdf",
        "rewritten_txt": "FT1003_MiniSaw_Manual_REWRITTEN.txt",
    },
    {
        "model": "FT1004",
        "original_pdf": "18V Cordless Rotary tool manual new(FT1004).pdf",
        "rewritten_txt": "FT1004_RotaryTool_Manual_REWRITTEN.txt",
    },
]

# Keywords to check. We only flag a keyword if it's present in the ORIGINAL but missing in the REWRITE.
KEYWORDS = [
    # compliance / regs
    "Proposition 65",
    "OEHHA",
    "California",
    "double insulated",
    "Class II",
    "earthing",
    "RCD",
    "GFCI",
    "EC declaration",
    "CE",
    "RoHS",

    # safety concepts
    "kickback",
    "abrasive",
    "cut-off",
    "wire brush",
    "polishing",
    "sanding",
    "grinding",
    "dust mask",
    "respirator",
    "crystalline silica",
    "lead-based",
    "pressure-treated",
    "arsenic",
    "chromium",
    "wood dust",
    "electromagnetic field",
    "vibration",
    "noise",

    # charger/battery
    "battery",
    "charger",
    "charging",
    "100-240",
    "polarity",

    # disposal / symbols
    "recycle",
    "recycling",
    "WEEE",
    "symbols",
    "read manual",
]


def normalize(s: str) -> str:
    s = s.lower()
    s = s.replace("\u2013", "-").replace("\u2014", "-")
    s = re.sub(r"\s+", " ", s)
    return s


def extract_pdf_text(path: Path, max_pages: int | None = None) -> str:
    r = PdfReader(str(path))
    pages = r.pages[:max_pages] if max_pages else r.pages
    out = []
    for p in pages:
        try:
            t = p.extract_text() or ""
        except Exception:
            t = ""
        out.append(t)
    return "\n".join(out)


def check_manual(m: dict) -> None:
    orig_path = BASE / m["original_pdf"]
    rew_path = BASE / m["rewritten_txt"]

    orig_text = normalize(extract_pdf_text(orig_path))
    rew_text = normalize(rew_path.read_text(encoding="utf-8"))

    missing = []
    for kw in KEYWORDS:
        nkw = normalize(kw)
        if nkw in orig_text and nkw not in rew_text:
            missing.append(kw)

    print("=" * 72)
    print(f"{m['model']} audit")
    print(f"  original:  {m['original_pdf']}")
    print(f"  rewritten: {m['rewritten_txt']}")
    print(f"  flagged missing keywords (present in original, absent in rewrite): {len(missing)}")
    for kw in missing:
        print(f"   - {kw}")


def main():
    for m in MANUALS:
        check_manual(m)


if __name__ == "__main__":
    main()
