#!/usr/bin/env python3
"""validate_layout.py — layout/density validator for the NI25 v2 entry.

Re-measures every text element of the page with the same fonts the draw
script uses and FAILS (exit 1) on any clipped deck, overflowing headline,
over-wide brief line, pin outside the map frame, or count mismatch.
Run:  python3 validate_layout.py
"""
import os
import sys
from PIL import Image, ImageFont, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import draw_news25_v2 as D

FD = "/usr/share/fonts/truetype/dejavu"
def F(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)

FAILURES = []
img = Image.new("RGB", (10, 10), "white")
d = ImageDraw.Draw(img)

def wrap(text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def check(label, text, font, max_w, max_lines):
    lines = wrap(text, font, max_w)
    if len(lines) > max_lines:
        FAILURES.append(f"{label}: {len(lines)} lines > {max_lines}: {text!r}")
    for ln in lines:
        if d.textlength(ln, font=font) > max_w + 0.5:
            FAILURES.append(f"{label}: line too wide: {ln!r}")
    return lines

# --- counts
total = len(D.LEADS) + len(D.MIDS) + len(D.BRIEFS)
if total != 49:
    FAILURES.append(f"story count {total} != 49")
if sum(n for _, n, _ in D.REGIONS) != 49:
    FAILURES.append("region strip does not sum to 49")
nums = sorted(s["n"] for s in D.LEADS + D.MIDS + D.BRIEFS)
if nums != list(range(1, 50)):
    FAILURES.append(f"story numbers are not 1..49: {nums}")

# region tallies vs strip
tally = {}
for s in D.LEADS + D.MIDS + D.BRIEFS:
    tally[s["region"]] = tally.get(s["region"], 0) + 1
for name, n, _ in D.REGIONS:
    if tally.get(name, 0) != n:
        FAILURES.append(f"region {name}: strip says {n}, stories say {tally.get(name, 0)}")
    if tally.get(name, 0) and tally[name] > 10 and name != "AMERICAS":
        FAILURES.append(f"region {name} over 10 stories: {tally[name]}")

# --- leads: headline <= 2 lines (serif bold 19, 316px), deck <= 3 (sans 12)
for L in D.LEADS:
    check(f"lead {L['n']} headline", L["headline"], F("DejaVuSerif-Bold.ttf", 19), 316, 2)
    check(f"lead {L['n']} deck", L["deck"], F("DejaVuSans.ttf", 12), 316, 3)

# --- mids: headline <= 2 lines (sans bold 12, 153px), deck <= 2 (sans 10)
for M in D.MIDS:
    check(f"mid {M['n']} headline", M["headline"], F("DejaVuSans-Bold.ttf", 12), 153, 2)
    check(f"mid {M['n']} deck", M["deck"], F("DejaVuSans.ttf", 10), 153, 2)
    kick = f"{M['n']:02d} {M['cat']} \u00b7 {M['city']}"
    if d.textlength(kick, font=F("DejaVuSans-Bold.ttf", 8)) > 139:
        FAILURES.append(f"mid {M['n']} kicker cannot fit even at 8px: {kick!r}")

# --- briefs: single line must fit its column (498px) with claim disc + source
for B in D.BRIEFS:
    left_w = (d.textlength(f"{B['n']:02d}  ", font=F("DejaVuSans.ttf", 9))
              + d.textlength(B["city"] + " \u2014 ", font=F("DejaVuSans-Bold.ttf", 9))
              + d.textlength(B["headline"], font=F("DejaVuSans.ttf", 9)))
    right_w = 12 + 4 + d.textlength(B["source"], font=F("DejaVuSans.ttf", 9))
    if left_w > 498 - right_w - 8:
        FAILURES.append(f"brief {B['n']}: line too wide ({left_w:.0f} > "
                        f"{498 - right_w - 8:.0f})")

# --- pins inside the map frame
pins = [(L["n"], L["lat"], L["lon"]) for L in D.LEAD_PINS]
pins += [(M["n"], M["lat"], M["lon"]) for M in D.MIDS]
for n, lat, lon in pins:
    px, py = D.project(lon, lat)
    if not (D.MAP["x0"] <= px <= D.MAP["x0"] + D.MAP["w"]
            and D.MAP["y0"] <= py <= D.MAP["y0"] + D.MAP["h"]):
        FAILURES.append(f"pin {n} outside map frame: ({px:.1f}, {py:.1f})")
for B in D.BRIEFS:
    px, py = D.project(B["lon"], B["lat"])
    px += B.get("jx", 0)
    py += B.get("jy", 0)
    if not (D.MAP["x0"] - 5 <= px <= D.MAP["x0"] + D.MAP["w"] + 5
            and D.MAP["y0"] - 5 <= py <= D.MAP["y0"] + D.MAP["h"] + 5):
        FAILURES.append(f"brief {B['n']} dot outside map frame")

# --- entry.png gate
path = os.path.join(HERE, "entry.png")
if not os.path.exists(path):
    FAILURES.append("entry.png missing — run draw_news25_v2.py first")
else:
    size = os.path.getsize(path)
    if size > 1048576:
        FAILURES.append(f"entry.png {size} bytes > 1 MiB")
    with Image.open(path) as im:
        if im.size != (1024, 1024):
            FAILURES.append(f"entry.png is {im.size}, not 1024x1024")
        if im.format != "PNG":
            FAILURES.append(f"entry.png format is {im.format}, not PNG")

if FAILURES:
    print(f"VALIDATION FAILED ({len(FAILURES)} problems):")
    for f in FAILURES:
        print("  -", f)
    sys.exit(1)
print(f"VALIDATION OK: 49 stories, 7 regions, {len(pins)} pins + "
      f"{len(D.BRIEFS)} dots in frame, entry.png within limits")
