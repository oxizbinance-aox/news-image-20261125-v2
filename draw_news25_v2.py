#!/usr/bin/env python3
"""draw_news25_v2.py — draws the NI25 v2 entry image (1024x1024, deterministic).

Fresh build for make.fun competition news-image-20261125 (Wednesday 25 Nov 2026).
49 stories, 7 regions, 3 leads + 12 mids + 34 briefs, solid world map with
numbered region-coloured pins, claim marks (C/R/CL) on every item.

Run:  python3 draw_news25_v2.py   -> writes entry.png next to this file.
The script FAILS (non-zero exit) if any headline/deck/brief does not fit its
box — no clipped text is allowed to render silently.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
FD = "/usr/share/fonts/truetype/dejavu"

def F(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)

def serif_b(s): return F("DejaVuSerif-Bold.ttf", s)
def serif(s):   return F("DejaVuSerif.ttf", s)
def sans(s):    return F("DejaVuSans.ttf", s)
def sans_b(s):  return F("DejaVuSans-Bold.ttf", s)

# ---------------------------------------------------------------- data
REGIONS = [
    ("AMERICAS",    11, "#b03a2e"),
    ("ASIA",        10, "#ca6f1e"),
    ("EUROPE",       7, "#2e6da4"),
    ("MIDDLE EAST",  7, "#7d3c98"),
    ("AFRICA",       8, "#1e8449"),
    ("OCEANIA",      3, "#00838f"),
    ("GLOBAL",       3, "#616161"),
]
REGION_COLOUR = {name: col for name, _, col in REGIONS}
assert sum(n for _, n, _ in REGIONS) == 49

CLAIM_FILL = {"C": "#1b7a3d", "R": "#155fa0", "CL": "#a86a00"}
CLAIM_WORD = {"C": "CONFIRMED", "R": "REPORTED", "CL": "CLAIM"}

# leads: n, city, region, category, headline, deck, stat, stat_label, claim, source
LEADS = [
    dict(n=4, city="JIUQUAN, CHINA", region="ASIA", cat="SPACE",
         headline="Pakistani first foreigner aboard China's space station",
         deck=("Shenzhou-24 lifted off 00:18 UTC; Muhammad Zeeshan Ali, 40, docks "
               "at Tiangong 11:56 UTC; crew stays 5-10 days. (Xinhua \u00b7 Reuters)"),
         stat="1st", stat_label="FOREIGNER ABOARD TIANGONG",
         claim="C", source="Xinhua \u00b7 Reuters", scene="rocket"),
    dict(n=14, city="WASHINGTON, US", region="AMERICAS", cat="TRADE",
         headline="US proposes new tariffs on 14 economies",
         deck=("USTR cites \u2018excess capacity\u2019: up to 20% on China, 25% India, 15% EU, "
               "35% Vietnam. Hearings Jan 2027; not in force yet. (USTR \u00b7 Reuters)"),
         stat="14", stat_label="ECONOMIES IN US TARIFF PLAN",
         claim="C", source="USTR \u00b7 Reuters", scene="tariffs"),
    dict(n=2, city="STRAIT OF HORMUZ", region="MIDDLE EAST", cat="CONFLICT",
         headline="Two tankers hit mines in the Strait of Hormuz",
         deck=("Iran\u2019s Guards say two tankers hit naval mines on an \u2018unauthorised route\u2019; "
               "Tehran also says it downed a US MQ-9 drone. (Reuters)"),
         stat="2", stat_label="TANKERS HIT MINES",
         claim="CL", source="Reuters", scene="hormuz"),
]

# mids: n, city, region, category, headline, deck (incl. source), stat, claim, lat, lon, scene
MIDS = [
    dict(n=1, city="SANTA CLARA", region="AMERICAS", cat="BUSINESS",
         headline="Nvidia slides as Trump role questioned",
         deck="Shares fell 5.9% on Trump role questions. (Reuters)",
         stat="-5.9%", claim="R", lat=37.35, lon=-121.95, scene="chip"),
    dict(n=3, city="CARTAGENA", region="AMERICAS", cat="SIEGE",
         headline="Hostages freed after supermarket siege",
         deck="Armed men held ~20; all freed unharmed. (Reuters/AP)",
         stat="ALL FREED", claim="C", lat=10.39, lon=-75.51, scene="market"),
    dict(n=5, city="DAKAR", region="AFRICA", cat="SPORT",
         headline="Senegal get AFCON title back",
         deck="CAS restored Senegal as 2025 champions. (Reuters)",
         stat="TITLE BACK", claim="C", lat=14.69, lon=-17.45, scene="trophy"),
    dict(n=6, city="MADRID", region="EUROPE", cat="POLITICS",
         headline="Spain heads to snap election",
         deck="Sanchez and Feijoo clashed on housing. (Reuters)",
         stat="29 NOV VOTE", claim="R", lat=40.42, lon=-3.70, scene="ballot"),
    dict(n=7, city="SHANGHAI", region="ASIA", cat="POLITICS",
         headline="China probes Shanghai party chief",
         deck="Graft probe into Chen Jining, Politburo member. (Reuters)",
         stat="PROBE", claim="R", lat=31.23, lon=121.47, scene="magnifier"),
    dict(n=8, city="BOGOR", region="ASIA", cat="DISASTER",
         headline="Dozens trapped in flooded gold mine",
         deck="Dozens trapped 100m down in flooded mine. (Reuters)",
         stat="100 M DOWN", claim="R", lat=-6.59, lon=106.79, scene="mine"),
    dict(n=9, city="WASHINGTON", region="AMERICAS", cat="POLITICS",
         headline="Democrats clinch 259 House seats",
         deck="Best result since 1990; party takes 259 seats. (AP)",
         stat="259 SEATS", claim="C", lat=38.90, lon=-77.04, scene="dome"),
    dict(n=10, city="AUSTIN", region="AMERICAS", cat="BUSINESS",
         headline="CrowdStrike to buy Zscaler for $44bn",
         deck="All-cash deal would build a $44bn giant. (AP/Reuters)",
         stat="$44BN", claim="R", lat=30.27, lon=-97.74, scene="shield"),
    dict(n=11, city="GAZA CITY", region="MIDDLE EAST", cat="CONFLICT",
         headline="Strikes kill Hamas security chief",
         deck="Israeli strikes killed seven in Gaza. (AP/Reuters)",
         stat="7 KILLED", claim="R", lat=31.50, lon=34.47, scene="alert"),
    dict(n=12, city="E. CONGO", region="AFRICA", cat="DISASTER",
         headline="Congo plane missing; rebels claim hit",
         deck="Aircraft missing; rebels claim the hit. (Reuters)",
         stat="PLANE MISSING", claim="CL", lat=-3.00, lon=29.00, scene="plane"),
    dict(n=13, city="CANBERRA", region="OCEANIA", cat="DIPLOMACY",
         headline="Solomons pick Australia as partner",
         deck="Treaty names Australia top partner. (Reuters)",
         stat="TREATY SIGNED", claim="C", lat=-35.28, lon=149.13, scene="treaty"),
    dict(n=15, city="TOKYO", region="ASIA", cat="MARKETS",
         headline="Nikkei falls 2.76% as tech sells off",
         deck="Chip rout: Tokyo -2.76%, Kospi -6.2%. (Reuters)",
         stat="-2.76%", claim="C", lat=35.68, lon=139.69, scene="stocks"),
]
LEAD_PINS = [
    dict(n=4, lat=40.96, lon=100.28, region="ASIA"),
    dict(n=14, lat=38.90, lon=-77.04, region="AMERICAS", jx=15, jy=-11),
    dict(n=2, lat=26.50, lon=56.00, region="MIDDLE EAST"),
]

# briefs: n, city, region, headline, claim, source, lat, lon, (optional jx/jy px jitter)
BRIEFS = [
    dict(n=16, city="LONDON", region="GLOBAL", headline="Oil down over 20% in November; Brent $87.49",
         claim="C", source="Reuters", lat=51.50, lon=-0.13, jx=-4, jy=2),
    dict(n=17, city="LUSAKA", region="AFRICA", headline="Zambia indicts opposition leader on treason charges",
         claim="R", source="Reuters", lat=-15.39, lon=28.32),
    dict(n=18, city="KHARTOUM", region="AFRICA", headline="UN condemns drone attacks; 28 abducted in Blue Nile",
         claim="C", source="UN/Reuters", lat=15.50, lon=32.56),
    dict(n=19, city="HONG KONG", region="ASIA", headline="City marks a year since the Tai Po fire",
         claim="C", source="AP", lat=22.32, lon=114.17),
    dict(n=20, city="MADRID", region="AMERICAS", headline="Abrego Garcia leaves US for Spain",
         claim="C", source="AP", lat=40.42, lon=-3.70, jx=4, jy=-3),
    dict(n=21, city="WASHINGTON", region="AMERICAS", headline="Unclassified CIA system breached in cyberattack",
         claim="R", source="AP", lat=38.90, lon=-77.04, jx=-6, jy=5),
    dict(n=22, city="LONDON", region="EUROPE", headline="UK defence plan at risk, watchdog warns",
         claim="R", source="Reuters", lat=51.50, lon=-0.13, jx=4, jy=-3),
    dict(n=23, city="WARSAW", region="EUROPE", headline="Russian drone enters Polish airspace",
         claim="R", source="Reuters", lat=52.23, lon=21.01),
    dict(n=24, city="MADRID", region="EUROPE", headline="Spain's top court amnesties Puigdemont",
         claim="C", source="Reuters", lat=40.42, lon=-3.70, jx=-4, jy=3),
    dict(n=25, city="TEHRAN", region="MIDDLE EAST", headline="Iran flogs singer 74 times, rights groups say",
         claim="R", source="Reuters", lat=35.69, lon=51.39),
    dict(n=26, city="ERBIL", region="MIDDLE EAST", headline="Iraq to seize Kurdish oilfields, PM orders",
         claim="R", source="Reuters", lat=36.19, lon=44.01),
    dict(n=27, city="HAVANA", region="GLOBAL", headline="WHO: end US fuel blockade on Cuba",
         claim="C", source="Reuters", lat=23.11, lon=-82.37),
    dict(n=28, city="CARACAS", region="AMERICAS", headline="Venezuela reveals $237.5bn debt pile",
         claim="R", source="Reuters", lat=10.49, lon=-66.88),
    dict(n=29, city="BUENOS AIRES", region="AMERICAS", headline="Argentina enters technical recession",
         claim="C", source="Reuters", lat=-34.60, lon=-58.38),
    dict(n=30, city="BOGOTA", region="AMERICAS", headline="Car bomb in Colombia injures 23",
         claim="R", source="AP", lat=4.71, lon=-74.07),
    dict(n=31, city="DHAKA", region="ASIA", headline="Bangladesh garment wage rises 36%",
         claim="C", source="Reuters", lat=23.81, lon=90.41),
    dict(n=32, city="ISLAMABAD", region="ASIA", headline="Pakistan warns of energy crisis",
         claim="R", source="Reuters", lat=33.68, lon=73.05),
    dict(n=33, city="MUMBAI", region="ASIA", headline="India's Sensex rises 1.8%",
         claim="C", source="Reuters", lat=19.08, lon=72.88),
    dict(n=34, city="CANBERRA", region="OCEANIA", headline="US envoy slams Australia digital law",
         claim="R", source="Reuters", lat=-35.28, lon=149.13, jx=5, jy=3),
    dict(n=35, city="SYDNEY", region="OCEANIA", headline="Australian inflation runs hot",
         claim="C", source="Reuters", lat=-33.87, lon=151.21),
    dict(n=36, city="MADRID", region="EUROPE", headline="Real Madrid thrash PSV 5-1",
         claim="C", source="Reuters", lat=40.42, lon=-3.70, jx=0, jy=5),
    dict(n=37, city="GULF OF MEXICO", region="AMERICAS", headline="Plane crash kills six",
         claim="C", source="Reuters", lat=25.00, lon=-90.00),
    dict(n=38, city="GOMA", region="AFRICA", headline="Violence surges at Ebola epicentre",
         claim="R", source="Reuters", lat=-1.66, lon=29.22),
    dict(n=39, city="JAKARTA", region="ASIA", headline="Indonesia's vice-president resigns",
         claim="R", source="Reuters", lat=-6.21, lon=106.85),
    dict(n=40, city="HASAKA", region="MIDDLE EAST", headline="IS attack kills two Syrian security staff",
         claim="R", source="Reuters", lat=36.48, lon=40.74),
    dict(n=41, city="NIAMEY", region="AFRICA", headline="Saudi national kidnapped by suspected IS militants",
         claim="R", source="Reuters", lat=13.51, lon=2.11),
    dict(n=42, city="AMMAN", region="MIDDLE EAST", headline="Jordan sentences man to death over officer attack",
         claim="C", source="Reuters", lat=31.95, lon=35.93),
    dict(n=43, city="RAS TANURA", region="MIDDLE EAST", headline="Houthis claim strike on Saudi oil refinery",
         claim="CL", source="Reuters", lat=26.65, lon=50.15),
    dict(n=44, city="PYONGYANG", region="ASIA", headline="N. Korea expels Swiss diplomat, shuts office",
         claim="C", source="AP", lat=39.04, lon=125.76),
    dict(n=45, city="LONDON", region="EUROPE", headline="UK nuclear test veterans win inquiry after 40 years",
         claim="C", source="AP", lat=51.50, lon=-0.13, jx=0, jy=-5),
    dict(n=46, city="PARIS", region="EUROPE", headline="Eurostar cancels Paris-London trains in staff strike",
         claim="C", source="AP", lat=48.86, lon=2.35),
    dict(n=47, city="BENGHAZI", region="AFRICA", headline="Libya vows retaliation after drone attack kills two",
         claim="R", source="AP", lat=32.12, lon=20.07),
    dict(n=48, city="JOHANNESBURG", region="AFRICA", headline="S. Africa convicts man over Russia fight trip",
         claim="C", source="AP", lat=-26.20, lon=28.05),
    dict(n=49, city="VATICAN CITY", region="GLOBAL", headline="Pope Francis diary tells of spiritual crisis",
         claim="R", source="AP", lat=41.90, lon=12.45),
]
assert len(LEADS) + len(MIDS) + len(BRIEFS) == 49
assert [b["n"] for b in BRIEFS] == list(range(16, 50))
assert sorted([s["n"] for s in LEADS + MIDS]) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

UTC_LINE = [
    ("00:18", "Shenzhou-24 lifts off"),
    ("03:55", "CIA breach reported"),
    ("06:00", "Nikkei closes -2.76%"),
    ("06:20", "Iraq seizes Kurdish fields"),
    ("08:07", "UK defence plan at risk"),
    ("11:56", "Tiangong docking"),
    ("21:00", "Nvidia closes -5.9%"),
]

# ---------------------------------------------------------------- helpers
FAILURES = []

def wrap(text, font, max_w, draw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def fit_check(label, text, font, max_w, max_lines, draw):
    lines = wrap(text, font, max_w, draw)
    if len(lines) > max_lines:
        FAILURES.append(f"{label}: {len(lines)} lines > {max_lines}: {text!r}")
    if any(draw.textlength(ln, font=font) > max_w + 0.5 for ln in lines):
        FAILURES.append(f"{label}: line too wide: {text!r}")
    return lines

def claim_disc(d, cx, cy, claim, r=7):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CLAIM_FILL[claim],
              outline="white", width=1)
    f = sans_b(9 if r >= 7 else 6)
    if claim == "CL":
        f = sans_b(7 if r >= 7 else 5)
    tw = d.textlength(claim, font=f)
    d.text((cx - tw / 2, cy - (5 if r >= 7 else 4)), claim, font=f, fill="white")

def pill(d, x, y, w, h, text, font, fg, bg):
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=bg)
    tw = d.textlength(text, font=font)
    d.text((x + (w - tw) / 2, y + (h - font.size) / 2 - 1), text, font=font, fill=fg)

# ---------------------------------------------------------------- map data
# Coarse continent outlines in (lon, lat); equirectangular, lat 90..-60.
N_AMERICA = [(-168,66),(-165,60),(-158,58),(-152,60),(-140,60),(-135,58),(-130,54),
    (-125,49),(-124,42),(-120,34),(-117,32),(-110,28),(-105,22),(-97,16),(-94,17),
    (-90,14),(-86,12),(-83,9),(-80,8),(-79,9),(-82,13),(-85,15),(-88,18),(-90,21),
    (-97,26),(-93,30),(-89,30),(-84,30),(-81,26),(-80,32),(-76,35),(-74,40),
    (-70,42),(-68,45),(-65,44),(-60,47),(-55,52),(-60,55),(-65,58),(-68,58),
    (-72,62),(-78,62),(-85,66),(-90,69),(-95,69),(-110,68),(-125,70),(-140,70),
    (-155,71),(-165,68)]
S_AMERICA = [(-80,8),(-77,4),(-80,-3),(-81,-6),(-77,-12),(-72,-18),(-70,-23),
    (-70,-30),(-72,-37),(-73,-44),(-74,-50),(-70,-54),(-66,-55),(-68,-50),
    (-65,-45),(-62,-40),(-58,-34),(-52,-32),(-48,-28),(-41,-23),(-39,-17),
    (-35,-9),(-35,-6),(-40,-3),(-44,-2),(-50,0),(-53,4),(-58,6),(-62,9),
    (-68,11),(-72,12),(-75,10),(-77,8)]
AFRICA = [(-6,35),(-10,31),(-15,27),(-17,21),(-17,15),(-15,11),(-13,8),(-8,5),
    (-4,5),(0,6),(6,4),(9,4),(9,0),(12,-5),(13,-12),(12,-18),(15,-27),(18,-34),
    (20,-35),(26,-34),(32,-26),(35,-24),(40,-16),(40,-10),(42,-4),(46,-1),(51,2),
    (51,11),(48,11),(44,11),(40,15),(38,18),(37,22),(35,28),(33,31),(30,32),
    (25,32),(20,32),(15,32),(10,34),(6,35)]
MADAGASCAR = [(44,-16),(47,-15),(50,-16),(50,-20),(47,-25),(44,-25),(43,-21)]
EURASIA = [(-10,36),(-9,38),(-9,43),(-2,44),(-1,46),(-4,48),(-1,49),(2,51),(5,53),
    (8,55),(8,57),(10,59),(5,60),(5,62),(10,64),(13,66),(18,69),(25,71),(30,70),
    (35,68),(40,68),(45,68),(50,69),(55,68),(60,69),(65,69),(70,72),(75,73),
    (80,73),(85,74),(90,75),(95,76),(100,77),(105,77),(110,74),(115,73),(120,73),
    (125,72),(130,72),(135,72),(140,72),(145,72),(150,70),(155,69),(160,69),
    (165,66),(170,66),(178,65),(178,62),(170,60),(162,60),(158,55),(156,51),
    (150,59),(162,56),(158,52),(150,45),(142,42),(140,38),(135,35),(130,33),
    (127,35),(122,38),(120,35),(122,30),(120,25),(118,25),(112,22),(108,18),
    (105,10),(103,8),(100,7),(98,10),(95,16),(92,21),(89,22),(86,20),(82,17),
    (80,13),(77,8),(75,10),(73,16),(70,20),(66,25),(62,25),(58,25),(56,26),
    (54,26),(52,28),(50,29),(48,30),(50,26),(52,26),(54,24),(56,26),(59,22),
    (55,17),(52,15),(48,14),(44,13),(42,15),(40,20),(38,24),(36,28),(35,31),
    (36,36),(34,36),(30,36),(27,37),(26,38),(23,36),(22,37),(20,39),(23,40),
    (26,41),(23,40),(20,40),(19,42),(15,44),(12,44),(8,44),(6,43),(3,42),(0,39),
    (-2,37),(-5,36),(-8,37)]
UK = [(-5,50),(-3,53),(-5,56),(-3,58),(-1,57),(0,53),(1,51)]
JAPAN = [(130,31),(132,33),(135,34),(137,35),(139,37),(140,39),(141,41),(142,44),
    (144,44),(142,40),(140,36),(137,34),(132,33)]
SUMATRA = [(95,5),(100,0),(104,-4),(106,-6),(103,-6),(100,-2),(97,3)]
JAVA = [(105,-6),(110,-7),(114,-7),(114,-9),(108,-8),(105,-7)]
BORNEO = [(109,1),(113,4),(117,6),(119,1),(117,-3),(113,-3),(110,-2)]
NEW_GUINEA = [(131,-1),(136,-2),(141,-3),(146,-6),(150,-9),(147,-9),(142,-8),
    (138,-8),(134,-4),(131,-2)]
NZ = [(167,-45),(170,-42),(173,-40),(175,-38),(177,-38),(174,-41),(171,-44),(168,-46)]
ICELAND = [(-22,64),(-18,63),(-14,64),(-18,66),(-22,65)]
GREENLAND = [(-55,60),(-50,60),(-45,60),(-40,64),(-32,68),(-25,70),(-20,74),
    (-22,76),(-30,80),(-40,80),(-50,78),(-58,76),(-60,74),(-58,70),(-55,64)]
SRI_LANKA = [(80,9),(81,8),(80,6),(79,8)]
TAIWAN = [(120,22),(121,23),(121,25),(120,24)]
CONTINENTS = [N_AMERICA, S_AMERICA, AFRICA, MADAGASCAR, EURASIA, UK, JAPAN,
              SUMATRA, JAVA, BORNEO, NEW_GUINEA, NZ, ICELAND, GREENLAND,
              SRI_LANKA, TAIWAN]

MAP = dict(x0=8, y0=626, w=1008, h=128)

def project(lon, lat):
    x = MAP["x0"] + (lon + 180.0) / 360.0 * MAP["w"]
    y = MAP["y0"] + (85.0 - lat) / 140.0 * MAP["h"]
    return x, y

# ---------------------------------------------------------------- scenes
def draw_rocket_scene(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#8ec8e8")
    for sx, sy, r in [(30, 18, 2), (90, 10, 1), (150, 24, 2), (240, 14, 1),
                      (290, 30, 2), (60, 46, 1), (200, 8, 1), (265, 48, 1)]:
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill="white")
    # Earth as a shallow arc band, ENTIRELY inside the scene (never below y+h)
    import math as _m
    pts = [(x + t * w, y + h - 26 * _m.sin(_m.pi * t)) for t in
           [i / 40.0 for i in range(41)]]
    pts += [(x + w, y + h), (x, y + h)]
    d.polygon(pts, fill="#3f7fb5")
    d.ellipse([x + 30, y + h - 12, x + 90, y + h], fill="#5da24a")
    d.ellipse([x + 220, y + h - 14, x + 280, y + h], fill="#5da24a")
    # rocket, centre-right
    rx = x + 178
    d.polygon([(rx, y + 34), (rx + 8, y + 22), (rx + 16, y + 34)], fill="#c0392b")
    d.rectangle([rx, y + 34, rx + 16, y + 78], fill="white")
    d.rectangle([rx + 5, y + 48, rx + 11, y + 62], fill="#2e6da4")
    d.polygon([(rx - 6, y + 78), (rx, y + 66), (rx, y + 78)], fill="#c0392b")
    d.polygon([(rx + 16, y + 78), (rx + 16, y + 66), (rx + 22, y + 78)], fill="#c0392b")
    d.polygon([(rx + 4, y + 78), (rx + 8, y + 92), (rx + 12, y + 78)], fill="#f39c12")
    d.ellipse([rx + 2, y + 88, rx + 14, y + 98], fill="#f5b041")
    # space station, right
    sx = x + 232
    d.rectangle([sx, y + 30, sx + 14, y + 62], fill="#d5d8dc")
    d.rectangle([sx - 26, y + 40, sx, y + 52], fill="#2e6da4")
    d.rectangle([sx + 14, y + 40, sx + 40, y + 52], fill="#2e6da4")
    d.rectangle([sx + 2, y + 20, sx + 10, y + 30], fill="#aeb6bf")
    d.rectangle([sx - 26, y + 40, sx + 40, y + 52], outline="white")
    # punch: giant 1st + label pill (top-left, clear of rocket/station)
    d.text((x + 10, y + 4), "1st", font=serif_b(46), fill="white",
           stroke_width=2, stroke_fill="#1a5276")
    pill(d, x + 10, y + 56, 148, 18, "FOREIGNER ABOARD TIANGONG",
         sans_b(9), "#1a5276", "white")
    pill(d, x + w - 108, y + h - 22, 100, 16, "SHENZHOU-24", sans_b(9),
         "white", "#1a5276")

def draw_tariffs_scene(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#fdf3d8")
    d.text((x + 10, y + 2), "14", font=serif_b(52), fill="#1a3a5c")
    d.text((x + 88, y + 10), "ECONOMIES", font=sans_b(15), fill="#1a3a5c")
    d.text((x + 88, y + 27), "IN US TARIFF PLAN", font=sans_b(10), fill="#5d6d7e")
    # bar chart: 4 economies, labels ABOVE each bar, countries BELOW baseline
    data = [("CHINA", 20, "#c0392b"), ("INDIA", 25, "#ca6f1e"),
            ("EU", 15, "#2e6da4"), ("VIETNAM", 35, "#7d3c98")]
    base = y + h - 18
    bw, gap = 34, 16
    cx0 = x + 22
    for i, (name, val, col) in enumerate(data):
        bx = cx0 + i * (bw + gap)
        bh = int(val * 1.1)
        d.rectangle([bx, base - bh, bx + bw, base], fill=col)
        vl = f"{val}%"
        vw = d.textlength(vl, font=sans_b(11))
        d.text((bx + (bw - vw) / 2, base - bh - 14), vl, font=sans_b(11), fill="#1a3a5c")
        nw = d.textlength(name, font=sans_b(8))
        d.text((bx + (bw - nw) / 2, base + 3), name, font=sans_b(8), fill="#5d6d7e")
    d.line([x + 14, base, x + w - 14, base], fill="#1a3a5c", width=2)
    d.text((x + w - 118, y + 4), "USTR \u00b7 SECTION 301", font=sans_b(9), fill="#5d6d7e")

def draw_hormuz_scene(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#cfe8f2")
    # Iran (top) and Arabia (bottom) land masses
    d.polygon([(x, y), (x + w, y), (x + w, y + 34), (x + 210, y + 44),
               (x + 150, y + 30), (x + 60, y + 40), (x, y + 30)],
              fill="#e8d9b0")
    d.polygon([(x, y + h), (x + w, y + h), (x + w, y + 82), (x + 240, y + 92),
               (x + 120, y + 80), (x + 40, y + 94), (x, y + 84)],
              fill="#e8d9b0")
    d.text((x + 215, y + 10), "IRAN", font=sans_b(10), fill="#7d6608")
    d.text((x + w - 52, y + h - 16), "OMAN", font=sans_b(10), fill="#7d6608")
    # dashed route through the strait
    for i in range(0, 300, 14):
        px = x + 12 + i
        py = y + 58 + int(6 * (1 - abs(i - 150) / 150.0))
        d.line([px, py, px + 8, py], fill="#5d6d7e", width=2)
    # two tankers
    for tx, ty in [(x + 96, y + 52), (x + 196, y + 66)]:
        d.rectangle([tx, ty, tx + 64, ty + 12], fill="#37474f")
        d.rectangle([tx + 44, ty - 8, tx + 58, ty], fill="white")
        d.rectangle([tx, ty + 12, tx + 64, ty + 15], fill="#c0392b")
    # mines (spiked dots)
    for mx, my in [(x + 84, y + 70), (x + 176, y + 56), (x + 262, y + 74)]:
        d.ellipse([mx - 4, my - 4, mx + 4, my + 4], fill="#1a1a1a")
        d.line([mx - 7, my, mx + 7, my], fill="#1a1a1a", width=1)
        d.line([mx, my - 7, mx, my + 7], fill="#1a1a1a", width=1)
    d.text((x + 10, y + 4), "2", font=serif_b(46), fill="#1a3a5c",
           stroke_width=2, stroke_fill="white")
    pill(d, x + 52, y + 14, 128, 18, "TANKERS HIT MINES", sans_b(9),
         "#7b241c", "white")
    d.text((x + 118, y + h - 18), "STRAIT OF HORMUZ", font=sans_b(9), fill="#1a5276")

MID_SCENES = {}

def mid_scene(d, x, y, w, h, key):
    """36px-tall pictogram strip for a mid card."""
    if key == "chip":
        d.rectangle([x, y, x + w, y + h], fill="#d6eaf8")
        for i, bx in enumerate([8, 30, 52, 74, 96, 118, 140]):
            d.rectangle([x + bx, y + 12, x + bx + 16, y + 30], fill="#aed6f1",
                        outline="#2e6da4")
        d.rectangle([x + 62, y + 4, x + 100, y + 20], fill="#1a3a5c")
        d.text((x + 68, y + 6), "NVDA", font=sans_b(9), fill="white")
        d.line([x + 108, y + 8, x + 150, y + 28], fill="#c0392b", width=3)
        d.polygon([(x + 150, y + 28), (x + 142, y + 26), (x + 150, y + 31)], fill="#c0392b")
    elif key == "market":
        d.rectangle([x, y, x + w, y + h], fill="#fdebd0")
        d.rectangle([x + 10, y + 8, x + 152, y + 24], fill="#27ae60")
        d.text((x + 14, y + 11), "SUPERMERCADO", font=sans_b(8), fill="white")
        d.rectangle([x + 10, y + 24, x + 150, y + 30], fill="#f1c40f")
        for bx in range(14, 150, 14):
            d.line([x + bx, y + 24, x + bx + 7, y + 30], fill="#1a1a1a", width=3)
        for px, col in [(30, "#2e6da4"), (80, "#e67e22"), (125, "#7d3c98")]:
            d.ellipse([x + px - 3, y + 25, x + px + 3, y + 31], fill=col)
    elif key == "trophy":
        d.rectangle([x, y, x + w, y + h], fill="#d5f5e3")
        d.rectangle([x, y, x + w, y + 10], fill="#1e8449")
        d.rectangle([x, y + 10, x + w, y + 16], fill="#f1c40f")
        d.rectangle([x, y + 16, x + w, y + 22], fill="#c0392b")
        d.ellipse([x + 66, y + 8, x + 96, y + 30], fill="#f1c40f", outline="#b7950b")
        d.rectangle([x + 76, y + 28, x + 86, y + 31], fill="#f1c40f")
    elif key == "ballot":
        d.rectangle([x, y, x + w, y + h], fill="#fadbd8")
        d.rectangle([x, y, x + w, y + 12], fill="#c0392b")
        d.rectangle([x, y + 12, x + w, y + 18], fill="#f1c40f")
        d.rectangle([x + 58, y + 12, x + 104, y + 31], fill="#f5f5f5",
                    outline="#1a1a1a")
        d.line([x + 58, y + 20, x + 104, y + 20], fill="#1a1a1a", width=1)
        d.rectangle([x + 118, y + 6, x + 136, y + 18], fill="white",
                    outline="#1a1a1a")
        d.text((x + 122, y + 7), "\u2713", font=sans_b(10), fill="#1b7a3d")
    elif key == "magnifier":
        d.rectangle([x, y, x + w, y + h], fill="#eaf2f8")
        for bx in [10, 40, 70, 100, 130]:
            d.rectangle([x + bx, y + 14, x + bx + 22, y + 34], fill="#aeb6bf")
            d.rectangle([x + bx + 4, y + 18, x + bx + 8, y + 22], fill="#f1c40f")
            d.rectangle([x + bx + 12, y + 24, x + bx + 16, y + 28], fill="#f1c40f")
        d.ellipse([x + 108, y + 2, x + 138, y + 31], outline="#1a1a1a", width=4)
        d.line([x + 132, y + 26, x + 148, y + 31], fill="#1a1a1a", width=4)
    elif key == "mine":
        d.rectangle([x, y, x + w, y + h], fill="#eaf2f8")
        d.polygon([(x, y + 32), (x + 40, y + 6), (x + 80, y + 32)], fill="#935116")
        d.polygon([(x + 80, y + 32), (x + 120, y + 12), (x + 163, y + 32)], fill="#7e5100")
        d.rectangle([x + 52, y + 24, x + 68, y + 32], fill="#1a1a1a")
        for rx in [20, 60, 100, 140]:
            d.line([x + rx, y + 2, x + rx - 3, y + 10], fill="#2e86c1", width=2)
            d.line([x + rx + 5, y + 4, x + rx + 2, y + 12], fill="#2e86c1", width=2)
    elif key == "dome":
        d.rectangle([x, y, x + w, y + h], fill="#d6eaf8")
        d.rectangle([x, y + 24, x + w, y + 32], fill="#7fb3d5")
        d.ellipse([x + 66, y + 2, x + 96, y + 26], fill="white", outline="#5d6d7e")
        d.rectangle([x + 58, y + 22, x + 104, y + 26], fill="white")
        for bx in [20, 46, 116, 142]:
            d.rectangle([x + bx, y + 24, x + bx + 8, y + 32], fill="white")
    elif key == "shield":
        d.rectangle([x, y, x + w, y + h], fill="#eaf2f8")
        d.rectangle([x + 12, y + 8, x + 62, y + 28], fill="#1a3a5c")
        d.text((x + 16, y + 11), "CRWD", font=sans_b(10), fill="white")
        d.rectangle([x + 100, y + 8, x + 150, y + 28], fill="#7d3c98")
        d.text((x + 104, y + 11), "ZS", font=sans_b(10), fill="white")
        d.polygon([(x + 76, y + 4), (x + 86, y + 10), (x + 76, y + 16),
                   (x + 66, y + 10)], fill="#f1c40f")
        d.line([x + 62, y + 18, x + 76, y + 18], fill="#1a1a1a", width=2)
        d.line([x + 86, y + 18, x + 100, y + 18], fill="#1a1a1a", width=2)
    elif key == "alert":
        d.rectangle([x, y, x + w, y + h], fill="#fdedec")
        for bx in [8, 42, 76, 110, 138]:
            d.rectangle([x + bx, y + 14, x + bx + 22, y + 32], fill="#aeb6bf")
        d.polygon([(x + 70, y + 2), (x + 92, y + 24), (x + 48, y + 24)], fill="#f39c12")
        d.text((x + 66, y + 8), "!", font=sans_b(14), fill="white")
    elif key == "plane":
        d.rectangle([x, y, x + w, y + h], fill="#d6eaf8")
        d.ellipse([x + 52, y + 8, x + 110, y + 26], fill="white", outline="#5d6d7e")
        d.polygon([(x + 110, y + 12), (x + 132, y + 16), (x + 110, y + 20)], fill="white")
        d.polygon([(x + 66, y + 26), (x + 76, y + 31), (x + 86, y + 26)], fill="white")
        for i in range(3):
            d.arc([x + 8 + i * 5, y + 4, x + 30 + i * 5, y + 28],
                  300, 60, fill="#2e86c1", width=2)
    elif key == "treaty":
        d.rectangle([x, y, x + w, y + h], fill="#eafaf1")
        d.rectangle([x + 52, y + 4, x + 110, y + 32], fill="white",
                    outline="#1a1a1a")
        d.line([x + 58, y + 10, x + 104, y + 10], fill="#1a1a1a", width=1)
        d.line([x + 58, y + 15, x + 104, y + 15], fill="#1a1a1a", width=1)
        d.line([x + 58, y + 20, x + 90, y + 20], fill="#1a1a1a", width=1)
        d.rectangle([x + 14, y + 10, x + 40, y + 22], fill="#1e8449")
        d.text((x + 18, y + 11), "AU", font=sans_b(9), fill="white")
        d.rectangle([x + 122, y + 10, x + 148, y + 22], fill="#2e6da4")
        d.text((x + 126, y + 11), "SB", font=sans_b(9), fill="white")
    elif key == "stocks":
        d.rectangle([x, y, x + w, y + h], fill="#fdebd0")
        d.ellipse([x + 62, y + 2, x + 100, y + 31], fill="#c0392b")
        d.line([x + 10, y + 12, x + 50, y + 10], fill="#c0392b", width=3)
        d.line([x + 50, y + 10, x + 62, y + 22], fill="#c0392b", width=3)
        d.line([x + 100, y + 22, x + 130, y + 14], fill="#c0392b", width=3)
        d.line([x + 130, y + 14, x + 152, y + 28], fill="#c0392b", width=3)
        d.polygon([(x + 152, y + 28), (x + 144, y + 26), (x + 152, y + 31)], fill="#c0392b")

# ---------------------------------------------------------------- draw
def draw_page():
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    # --- top bar
    d.rectangle([0, 0, W, 16], fill="#1a3a5c")
    top = "THE WORLD IN ONE DAY  \u00b7  49 STORIES  \u00b7  7 REGIONS  \u00b7  EVERY ONE DATED WEDNESDAY 25 NOVEMBER 2026"
    tf = sans_b(11)
    d.text(((W - d.textlength(top, font=tf)) / 2, 2), top, font=tf, fill="white")
    # --- masthead (auto-fit serif)
    size = 58
    while size > 30:
        mf = serif_b(size)
        if d.textlength("Wednesday 25 November 2026", font=mf) <= 1008:
            break
        size -= 1
    d.text(((W - d.textlength("Wednesday 25 November 2026", font=mf)) / 2, 18),
           "Wednesday 25 November 2026", font=mf, fill="#111111")
    # --- sub-headline
    sub = ("Pakistani astronaut boards China\u2019s space station  \u00b7  "
           "AI doubts sink Asia\u2019s chip stocks  \u00b7  "
           "US proposes tariffs on 14 economies")
    sf = serif(14)
    if d.textlength(sub, font=sf) > 1008:
        sf = serif(13)
    d.text(((W - d.textlength(sub, font=sf)) / 2, 82), sub, font=sf, fill="#1a3a5c")
    d.line([8, 97, 1016, 97], fill="#1a3a5c", width=1)
    # --- region strip (centred chips)
    chip_font = sans_b(11)
    widths = []
    for name, n, col in REGIONS:
        widths.append(d.textlength(f"{name} {n}", font=chip_font) + 18)
    total = sum(widths) + 6 * (len(REGIONS) - 1)
    cx = (W - total) / 2
    for (name, n, col), cw in zip(REGIONS, widths):
        d.rounded_rectangle([cx, 101, cx + cw, 119], radius=4, fill=col)
        t = f"{name} {n}"
        d.text((cx + (cw - d.textlength(t, font=chip_font)) / 2, 105), t,
               font=chip_font, fill="white")
        cx += cw + 6
    # --- UTC timeline (auto-fit)
    label = "THE DAY IN UTC   "
    parts = [f"{t} {e}" for t, e in UTC_LINE]
    body = "  \u00b7  ".join(parts)
    tsize = 10
    while tsize > 7:
        bf = sans(9)
        lf = sans_b(tsize)
        if (d.textlength(label, font=lf) + d.textlength(body, font=bf)) <= 1008:
            break
        tsize -= 1
    lf = sans_b(tsize)
    bf = sans(9)
    d.text((8, 124), label, font=lf, fill="#1a3a5c")
    d.text((8 + d.textlength(label, font=lf), 124), body, font=bf, fill="#333333")
    d.line([8, 136, 1016, 136], fill="#999999", width=1)

    # --- leads (3 columns)
    lead_x = [8, 344, 680]
    lead_w = 328
    ly, scene_h = 140, 114
    for i, L in enumerate(LEADS):
        x = lead_x[i]
        d.rectangle([x, ly, x + lead_w, ly + 240], outline="#bbbbbb", width=1)
        sx, sy = x, ly
        if L["scene"] == "rocket":
            draw_rocket_scene(d, sx, sy, lead_w, scene_h)
        elif L["scene"] == "tariffs":
            draw_tariffs_scene(d, sx, sy, lead_w, scene_h)
        else:
            draw_hormuz_scene(d, sx, sy, lead_w, scene_h)
        # kicker row
        ky = ly + scene_h + 5
        d.text((x + 6, ky), f"{L['n']:02d} \u00b7 {L['city']} \u2014 {L['cat']}",
               font=sans_b(10), fill="#1a3a5c")
        claim_disc(d, x + lead_w - 12, ky + 7, L["claim"], r=7)
        cw = d.textlength(CLAIM_WORD[L["claim"]], font=sans_b(8))
        d.text((x + lead_w - 22 - cw, ky + 3), CLAIM_WORD[L["claim"]],
               font=sans_b(8), fill=CLAIM_FILL[L["claim"]])
        # headline (2 lines max, serif bold 19)
        hl = fit_check(f"lead {L['n']} headline", L["headline"], serif_b(19),
                       lead_w - 12, 2, d)
        hy = ky + 18
        for j, ln in enumerate(hl):
            d.text((x + 6, hy + j * 23), ln, font=serif_b(19), fill="#111111")
        # deck (3 lines max, 12px) — must end inside the lead card
        dl = fit_check(f"lead {L['n']} deck", L["deck"], sans(12), lead_w - 12, 3, d)
        dy = hy + 48
        if dy + len(dl) * 15 > ly + 240:
            FAILURES.append(f"lead {L['n']} deck overflows card bottom")
        for j, ln in enumerate(dl):
            d.text((x + 6, dy + j * 15), ln, font=sans(12), fill="#333333")

    # --- mids (2 rows x 6)
    mid_w = 163
    mid_gap = 6
    mid_x0 = 8
    mid_y0 = 384
    mid_h = 112
    for idx, M in enumerate(MIDS):
        row, col = divmod(idx, 6)
        x = mid_x0 + col * (mid_w + mid_gap)
        y = mid_y0 + row * (mid_h + 4)
        d.rectangle([x, y, x + mid_w, y + mid_h], outline="#bbbbbb", width=1)
        mid_scene(d, x + 1, y + 1, mid_w - 2, 32, M["scene"])
        # stat punch banner
        py = y + 33
        d.rectangle([x + 1, py, x + mid_w - 1, py + 15],
                    fill=REGION_COLOUR[M["region"]])
        st = M["stat"]
        d.text((x + (mid_w - d.textlength(st, font=sans_b(11))) / 2, py + 2),
               st, font=sans_b(11), fill="white")
        # kicker row
        ky = py + 17
        kick = f"{M['n']:02d} {M['cat']} \u00b7 {M['city']}"
        kf = sans_b(9)
        if d.textlength(kick, font=kf) > mid_w - 24:
            kf = sans_b(8)
        if d.textlength(kick, font=kf) > mid_w - 24:
            kick = f"{M['n']:02d} {M['cat']}"
        d.text((x + 5, ky), kick, font=kf, fill="#1a3a5c")
        claim_disc(d, x + mid_w - 10, ky + 6, M["claim"], r=6)
        # headline (2 lines, 12px bold)
        hl = fit_check(f"mid {M['n']} headline", M["headline"], sans_b(12),
                       mid_w - 10, 2, d)
        hy = ky + 13
        for j, ln in enumerate(hl):
            d.text((x + 5, hy + j * 14), ln, font=sans_b(12), fill="#111111")
        # deck (2 lines, 10px) — must end inside the mid card
        dl = fit_check(f"mid {M['n']} deck", M["deck"], sans(10), mid_w - 10, 2, d)
        dy = hy + 27
        if dy + len(dl) * 11 > y + mid_h:
            FAILURES.append(f"mid {M['n']} deck overflows card bottom")
        for j, ln in enumerate(dl):
            d.text((x + 5, dy + j * 11), ln, font=sans(10), fill="#333333")

    # --- map section
    d.text((8, 616), "WHERE IT HAPPENED", font=sans_b(12), fill="#1a3a5c")
    d.text((200, 617), "pins carry the story numbers \u2014 dots are the briefs below",
           font=sans(10), fill="#5d6d7e")
    d.rectangle([MAP["x0"], MAP["y0"], MAP["x0"] + MAP["w"], MAP["y0"] + MAP["h"]],
                fill="#e8f0f4", outline="#bbbbbb", width=1)
    for poly in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill="#c9c9c9", outline="#a8a8a8")
    # ocean labels (geographically correct)
    of = sans_b(9)
    for label, lon, lat in [("PACIFIC", -158, 8), ("ATLANTIC", -32, 12),
                            ("PACIFIC", 168, 4), ("INDIAN", 78, -34)]:
        ox, oy = project(lon, lat)
        d.text((ox - d.textlength(label, font=of) / 2, oy - 5), label,
               font=of, fill="#7fa8bc")
    # brief dots first (under pins)
    for B in BRIEFS:
        bx, by = project(B["lon"], B["lat"])
        bx += B.get("jx", 0)
        by += B.get("jy", 0)
        d.ellipse([bx - 3, by - 3, bx + 3, by + 3],
                  fill=REGION_COLOUR[B["region"]], outline="white", width=1)
    # numbered pins: leads + mids
    pins = []
    for L in LEAD_PINS:
        pins.append((L["n"], L["lat"], L["lon"], L["region"], L.get("jx", 0), L.get("jy", 0)))
    for M in MIDS:
        pins.append((M["n"], M["lat"], M["lon"], M["region"], 0, 0))
    print("PIN DEBUG TABLE (n, lat, lon -> x, y):")
    for n, lat, lon, reg, jx, jy in sorted(pins):
        px, py = project(lon, lat)
        print(f"  pin {n:2d} {reg:12s} lat {lat:7.2f} lon {lon:8.2f} -> x {px:7.1f} y {py:6.1f}")
        assert MAP["x0"] <= px <= MAP["x0"] + MAP["w"], f"pin {n} x out of map"
        assert MAP["y0"] <= py <= MAP["y0"] + MAP["h"], f"pin {n} y out of map"
        # leader line for jittered pins
        if jx or jy:
            d.line([px, py, px + jx, py + jy], fill="#333333", width=1)
            px, py = px + jx, py + jy
        r = 8
        d.ellipse([px - r, py - r, px + r, py + r],
                  fill=REGION_COLOUR[reg], outline="white", width=2)
        nf = sans_b(9)
        ns = str(n)
        d.text((px - d.textlength(ns, font=nf) / 2, py - 6), ns, font=nf,
               fill="white")
    # map legend, two lines (second line shortened so it fits the page width)
    ly1 = 756
    lx = 8
    for name, n, col in REGIONS:
        d.rectangle([lx, ly1 + 1, lx + 8, ly1 + 9], fill=col)
        t = f"{name} {n}"
        d.text((lx + 11, ly1), t, font=sans_b(9), fill="#333333")
        lx += 11 + d.textlength(t, font=sans_b(9)) + 12
    legend2 = ("Numbers match the stories \u2014 dots = briefs   \u00b7   "
               "C = CONFIRMED   \u00b7   R = REPORTED   \u00b7   CL = CLAIM   \u00b7   "
               "HOW SURE: C = official record or 2+ sources; R = named source; "
               "CL = single-source or claimant statement")
    if d.textlength(legend2, font=sans(9)) > 1008:
        FAILURES.append("map legend line 2 too wide")
    d.text((8, 767), legend2, font=sans(9), fill="#333333")

    # --- ALSO section
    ay = 772
    d.text((8, ay), "ALSO ON WEDNESDAY 25 NOVEMBER \u2014 34 MORE STORIES",
           font=sans_b(13), fill="#b03a2e")
    d.text((560, ay + 2), "every brief carries its claim mark + named source",
           font=sans(10), fill="#5d6d7e")
    d.line([8, ay + 17, 1016, ay + 17], fill="#b03a2e", width=2)
    col_w = 498
    col_x = [8, 518]
    row_h = 10.0
    y0 = ay + 20
    for ci in range(2):
        items = BRIEFS[ci * 17:(ci + 1) * 17]
        for ri, B in enumerate(items):
            yy = y0 + ri * row_h
            left = f"{B['n']:02d}  {B['city']} \u2014 {B['headline']}"
            src = B["source"]
            sf = sans(9)
            # right zone: claim disc + source, right-aligned
            right_w = 12 + 4 + d.textlength(src, font=sf)
            lf = sans(9)
            lb = sans_b(9)
            left_w = (d.textlength(f"{B['n']:02d}  ", font=lf)
                      + d.textlength(B["city"] + " \u2014 ", font=lb)
                      + d.textlength(B["headline"], font=lf))
            if left_w > col_w - right_w - 8:
                FAILURES.append(
                    f"brief {B['n']}: line too wide ({left_w:.0f} > "
                    f"{col_w - right_w - 8:.0f}): {left!r}")
            d.text((col_x[ci], yy), f"{B['n']:02d}  ", font=lf, fill="#b03a2e")
            nx = col_x[ci] + d.textlength(f"{B['n']:02d}  ", font=lf)
            d.text((nx, yy), B["city"] + " \u2014 ", font=lb, fill="#111111")
            nx += d.textlength(B["city"] + " \u2014 ", font=lb)
            d.text((nx, yy), B["headline"], font=lf, fill="#333333")
            rx = col_x[ci] + col_w
            d.text((rx - d.textlength(src, font=sf), yy), src, font=sf,
                   fill="#5d6d7e")
            claim_disc(d, rx - d.textlength(src, font=sf) - 10, yy + 5,
                       B["claim"], r=5)

    # --- footer
    fy = 964
    d.rectangle([8, fy, 1016, 1022], fill="#fdf2f2", outline="#b03a2e", width=1)
    ff = sans(9)
    ffb = sans_b(9)
    lines = [
        ("DATE CHECK \u2014 ", "Every story here happened, or was first reported, on Wednesday "
         "25 November 2026 in at least one timezone. Counted for 25 Nov: CAS ruling (announced "
         "24 Nov) for the Dakar celebrations; Niger kidnap (weekend) first reported 25 Nov; Spain votes 29 Nov."),
        ("HOW THIS PAGE WAS CHECKED \u2014 ", "Each story verified against a named source dated "
         "25 Nov 2026 (Reuters, AP, BBC, Al Jazeera, Xinhua, UN, USTR). Market figures are closing "
         "prices; CL marks a single-source or claimant statement, not a confirmed fact."),
        ("", "Sources: Reuters \u00b7 AP \u00b7 BBC \u00b7 Al Jazeera \u00b7 Xinhua \u00b7 UN \u00b7 USTR \u00b7 "
         "Yonhap  \u2014  Press time 26 Nov 2026 04:30 UTC  \u2014  Drawn programmatically; no photographs."),
    ]
    yy = fy + 4
    for bold, rest in lines:
        for ln in wrap(bold + rest, ff, 992, d)[:2]:
            # bold prefix on first line only
            if ln.startswith(bold) and bold:
                d.text((14, yy), bold, font=ffb, fill="#b03a2e")
                d.text((14 + d.textlength(bold, font=ffb), yy),
                       ln[len(bold):], font=ff, fill="#333333")
            else:
                d.text((14, yy), ln, font=ff, fill="#333333")
            yy += 10.5
            if yy > 1023:
                FAILURES.append("footer overflow")
    return img

def main():
    img = draw_page()
    if FAILURES:
        print("LAYOUT FAILURES:")
        for f in FAILURES:
            print("  -", f)
        sys.exit(1)
    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG")
    print(f"wrote {out} {os.path.getsize(out)} bytes")

if __name__ == "__main__":
    main()
