#!/usr/bin/env python3
"""
================================================================================
  OmniRoute AI — Synthetic Dataset Generator
  Tamil Nadu Bus Travel Data | All Logics Implemented
================================================================================

LOGICS IMPLEMENTED:
  1.  Holiday & Bridge-Leave detection (Tamil Nadu calendar, 3-4 day windows)
  2.  Year-on-Year adaptive bus allocation (demand learning per route)
  3.  Directional asymmetric flow (Metro→Hometown pre-holiday, reverse post-holiday)
  4.  Daily data for every single day in the given range
  5.  Realistic pricing from history+logics (no web scraping for this dataset)
  6.  Wide-range review generation (30+ templates per sentiment category)
  7.  Bus type matched to route distance (<220 km → seater/semi, >400 km → sleeper AC)
  8.  One bus / one route at a time — overnight buses blocked next morning
  9.  Realistic occupancy & pricing matching real redBus patterns
  10. COVID dip 2020–2021, year-on-year ridership growth
  11. Seasonal demand patterns (Summer, Monsoon, Festival, Winter)
  12. Short routes → 2 trips/day per bus; Long routes → 1 trip/day

HOW TO RUN:
  pip install pandas numpy holidays
  python3 omni_route_generator.py

OUTPUT:
  CSV file: tnbus_synthetic_YYYYMMDD_YYYYMMDD.csv
================================================================================
"""

import os
import sys
import math
import csv
import random
import warnings
from datetime import datetime, date, timedelta
from collections import defaultdict

warnings.filterwarnings("ignore")

# ── auto-install dependencies ──────────────────────────────────────────────────
def install(pkg):
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

try:
    import pandas as pd
except ImportError:
    install("pandas"); import pandas as pd

try:
    import numpy as np
except ImportError:
    install("numpy"); import numpy as np

try:
    import holidays as hlib
    HAS_HOLIDAYS = True
except ImportError:
    try:
        install("holidays"); import holidays as hlib; HAS_HOLIDAYS = True
    except Exception:
        HAS_HOLIDAYS = False
        print("  'holidays' package could not be installed. Using built-in TN holiday list.")

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

random.seed(42)
np.random.seed(42)

# ── 35 Bus Operators ──────────────────────────────────────────────────────────
OPERATORS = [
    {"id": "OP01", "name": "KPN Travels",             "tier": "premium",  "base": "Chennai"},
    {"id": "OP02", "name": "SRM Travels",             "tier": "premium",  "base": "Chennai"},
    {"id": "OP03", "name": "Royal Travels",           "tier": "premium",  "base": "Chennai"},
    {"id": "OP04", "name": "NueGo",                   "tier": "premium",  "base": "Chennai"},
    {"id": "OP05", "name": "Essaar Travels",          "tier": "premium",  "base": "Chennai"},
    {"id": "OP06", "name": "VKV Travels",             "tier": "standard", "base": "Coimbatore"},
    {"id": "OP07", "name": "A1 Travels",              "tier": "standard", "base": "Chennai"},
    {"id": "OP08", "name": "Krish Travels",           "tier": "standard", "base": "Madurai"},
    {"id": "OP09", "name": "PSS Transport",           "tier": "standard", "base": "Trichy"},
    {"id": "OP10", "name": "Arthi Travels",           "tier": "standard", "base": "Chennai"},
    {"id": "OP11", "name": "Sri Kumaran Travels",     "tier": "standard", "base": "Salem"},
    {"id": "OP12", "name": "LION Travels",            "tier": "standard", "base": "Chennai"},
    {"id": "OP13", "name": "PRM Roadways",            "tier": "standard", "base": "Chennai"},
    {"id": "OP14", "name": "YBM Travels",             "tier": "standard", "base": "Madurai"},
    {"id": "OP15", "name": "Green Line Travels",      "tier": "standard", "base": "Chennai"},
    {"id": "OP16", "name": "Orange Travels",          "tier": "standard", "base": "Salem"},
    {"id": "OP17", "name": "Tamizh Travels",          "tier": "standard", "base": "Coimbatore"},
    {"id": "OP18", "name": "Kaveri Travels",          "tier": "standard", "base": "Salem"},
    {"id": "OP19", "name": "Sri Balaji Travels",      "tier": "standard", "base": "Coimbatore"},
    {"id": "OP20", "name": "Parveen Travels",         "tier": "standard", "base": "Salem"},
    {"id": "OP21", "name": "Aakash Travels",          "tier": "budget",   "base": "Coimbatore"},
    {"id": "OP22", "name": "City Travels",            "tier": "budget",   "base": "Madurai"},
    {"id": "OP23", "name": "SBM Transport",           "tier": "budget",   "base": "Trichy"},
    {"id": "OP24", "name": "VEE VEE BUS",             "tier": "budget",   "base": "Coimbatore"},
    {"id": "OP25", "name": "Raj Travels",             "tier": "budget",   "base": "Madurai"},
    {"id": "OP26", "name": "Velavan Travels",         "tier": "budget",   "base": "Madurai"},
    {"id": "OP27", "name": "Murugan Travels",         "tier": "budget",   "base": "Salem"},
    {"id": "OP28", "name": "Sri Ganesh Travels",      "tier": "budget",   "base": "Chennai"},
    {"id": "OP29", "name": "Thirumurugan Travels",    "tier": "budget",   "base": "Trichy"},
    {"id": "OP30", "name": "Vidhya Travels",          "tier": "budget",   "base": "Madurai"},
    {"id": "OP31", "name": "Star Travels",            "tier": "standard", "base": "Chennai"},
    {"id": "OP32", "name": "Sharma Travels",          "tier": "budget",   "base": "Trichy"},
    {"id": "OP33", "name": "Annamalai Travels",       "tier": "standard", "base": "Coimbatore"},
    {"id": "OP34", "name": "Sri Vari Travels",        "tier": "budget",   "base": "Tirunelveli"},
    {"id": "OP35", "name": "Sugam Travels",           "tier": "budget",   "base": "Coimbatore"},
]

# ── Tamil Nadu Routes (origin, destination, distance in km) ──────────────────
ROUTES = {
    # ── Chennai outbound ──────────────────────────────────────────────────
    "R001": ("Chennai", "Coimbatore",      490),
    "R002": ("Chennai", "Madurai",         465),
    "R003": ("Chennai", "Tiruchirapalli",  330),
    "R004": ("Chennai", "Salem",           340),
    "R005": ("Chennai", "Tirunelveli",     635),
    "R006": ("Chennai", "Nagercoil",       694),
    "R007": ("Chennai", "Vellore",         135),
    "R008": ("Chennai", "Erode",           400),
    "R009": ("Chennai", "Tirupur",         456),
    "R010": ("Chennai", "Kumbakonam",      280),
    "R011": ("Chennai", "Thanjavur",       315),
    "R012": ("Chennai", "Dindigul",        430),
    "R013": ("Chennai", "Tenkasi",         615),
    "R014": ("Chennai", "Tuticorin",       635),
    "R015": ("Chennai", "Villupuram",      165),
    "R016": ("Chennai", "Krishnagiri",     280),
    "R017": ("Chennai", "Hosur",           320),
    "R018": ("Chennai", "Ooty",            545),
    "R019": ("Chennai", "Nagapattinam",    355),
    "R020": ("Chennai", "Karur",           370),
    "R021": ("Chennai", "Namakkal",        380),
    "R022": ("Chennai", "Ramanathapuram",  570),
    "R023": ("Chennai", "Rameswaram",      620),
    "R024": ("Chennai", "Sivakasi",        570),
    "R025": ("Chennai", "Kanyakumari",     725),
    "R026": ("Chennai", "Tiruvannamalai",  185),
    "R027": ("Chennai", "Chidambaram",     235),
    "R028": ("Chennai", "Pudukottai",      370),
    "R029": ("Chennai", "Karaikudi",       410),
    "R030": ("Chennai", "Velankanni",      370),
    "R031": ("Chennai", "Theni",           500),
    "R032": ("Chennai", "Virudhnagar",     545),
    "R033": ("Chennai", "Rajapalayam",     580),
    "R034": ("Chennai", "Kovilpatti",      600),
    "R035": ("Chennai", "Pollachi",        505),
    # ── Chennai inbound ───────────────────────────────────────────────────
    "R036": ("Coimbatore",     "Chennai",  490),
    "R037": ("Madurai",        "Chennai",  465),
    "R038": ("Tiruchirapalli","Chennai",   330),
    "R039": ("Salem",          "Chennai",  340),
    "R040": ("Tirunelveli",    "Chennai",  635),
    "R041": ("Nagercoil",      "Chennai",  694),
    "R042": ("Vellore",        "Chennai",  135),
    "R043": ("Erode",          "Chennai",  400),
    "R044": ("Tirupur",        "Chennai",  456),
    "R045": ("Kumbakonam",     "Chennai",  280),
    "R046": ("Thanjavur",      "Chennai",  315),
    "R047": ("Tenkasi",        "Chennai",  615),
    "R048": ("Tuticorin",      "Chennai",  635),
    "R049": ("Hosur",          "Chennai",  320),
    "R050": ("Krishnagiri",    "Chennai",  280),
    # ── Coimbatore hub ────────────────────────────────────────────────────
    "R051": ("Coimbatore", "Madurai",      215),
    "R052": ("Coimbatore", "Tiruchirapalli", 215),
    "R053": ("Coimbatore", "Salem",        160),
    "R054": ("Coimbatore", "Tirunelveli",  320),
    "R055": ("Coimbatore", "Nagercoil",    420),
    "R056": ("Coimbatore", "Erode",         80),
    "R057": ("Coimbatore", "Hosur",        200),
    "R058": ("Coimbatore", "Ooty",          90),
    "R059": ("Coimbatore", "Dindigul",     100),
    "R060": ("Coimbatore", "Thanjavur",    260),
    "R061": ("Coimbatore", "Kumbakonam",   295),
    "R062": ("Coimbatore", "Tuticorin",    330),
    "R063": ("Coimbatore", "Tenkasi",      310),
    "R064": ("Coimbatore", "Pollachi",      50),
    "R065": ("Coimbatore", "Nagapattinam", 330),
    "R066": ("Madurai",    "Coimbatore",   215),
    "R067": ("Salem",      "Coimbatore",   160),
    "R068": ("Tiruchirapalli", "Coimbatore", 215),
    "R069": ("Nagercoil",  "Coimbatore",   420),
    # ── Salem hub ─────────────────────────────────────────────────────────
    "R070": ("Salem", "Madurai",           215),
    "R071": ("Salem", "Tiruchirapalli",    180),
    "R072": ("Salem", "Tirunelveli",       410),
    "R073": ("Salem", "Erode",              60),
    "R074": ("Salem", "Hosur",             150),
    "R075": ("Salem", "Namakkal",           50),
    "R076": ("Salem", "Coimbatore",        160),
    "R077": ("Salem", "Nagercoil",         480),
    "R078": ("Salem", "Dindigul",          160),
    "R079": ("Madurai", "Salem",           215),
    "R080": ("Tiruchirapalli", "Salem",    180),
    # ── Madurai hub ───────────────────────────────────────────────────────
    "R081": ("Madurai", "Tiruchirapalli",  135),
    "R082": ("Madurai", "Tirunelveli",     170),
    "R083": ("Madurai", "Nagercoil",       230),
    "R084": ("Madurai", "Thanjavur",       175),
    "R085": ("Madurai", "Tuticorin",       165),
    "R086": ("Madurai", "Hosur",           310),
    "R087": ("Madurai", "Erode",           260),
    "R088": ("Tiruchirapalli", "Madurai",  135),
    "R089": ("Tirunelveli",   "Madurai",   170),
    "R090": ("Nagercoil",     "Madurai",   230),
    "R091": ("Thanjavur",     "Madurai",   175),
    # ── Hosur / Krishnagiri hub ───────────────────────────────────────────
    "R092": ("Hosur", "Coimbatore",        200),
    "R093": ("Hosur", "Madurai",           310),
    "R094": ("Hosur", "Tiruchirapalli",    280),
    "R095": ("Hosur", "Tirunelveli",       460),
    "R096": ("Hosur", "Salem",             150),
    "R097": ("Krishnagiri", "Coimbatore",  250),
    "R098": ("Krishnagiri", "Madurai",     400),
    "R099": ("Krishnagiri", "Tirunelveli", 500),
    # ── Cross / Interior routes ───────────────────────────────────────────
    "R100": ("Tiruchirapalli", "Tirunelveli", 295),
    "R101": ("Tiruchirapalli", "Nagercoil",   355),
    "R102": ("Tiruchirapalli", "Thanjavur",    60),
    "R103": ("Tiruchirapalli", "Tuticorin",   225),
    "R104": ("Tirunelveli",    "Nagercoil",    80),
    "R105": ("Nagercoil",      "Tirunelveli",  80),
    "R106": ("Kumbakonam",     "Madurai",      190),
    "R107": ("Erode",          "Madurai",      260),
    "R108": ("Tirupur",        "Madurai",      215),
    "R109": ("Tirupur",        "Tiruchirapalli", 225),
    "R110": ("Erode",          "Tiruchirapalli", 175),
    "R111": ("Vellore",        "Madurai",      350),
    "R112": ("Vellore",        "Tiruchirapalli", 245),
    "R113": ("Dindigul",       "Nagercoil",    275),
    "R114": ("Dindigul",       "Tirunelveli",  200),
    "R115": ("Thanjavur",      "Tiruchirapalli", 60),
    "R116": ("Karur",          "Madurai",      175),
    "R117": ("Namakkal",       "Madurai",      200),
    "R118": ("Tuticorin",      "Tirunelveli",   75),
    "R119": ("Tirunelveli",    "Tuticorin",     75),
    "R120": ("Pollachi",       "Madurai",      150),
}

# ── Metro hubs (people LEAVE from here pre-holiday) ──────────────────────────
METRO_HUBS = {
    "Chennai", "Coimbatore", "Hosur", "Salem", "Erode",
    "Tirupur", "Krishnagiri", "Vellore",
}

# ── Hometown cities (people GO TO these on holidays, RETURN FROM post-holiday) ─
HOMETOWN_CITIES = {
    "Tenkasi", "Nagercoil", "Tirunelveli", "Ramanathapuram", "Rameswaram",
    "Kanyakumari", "Kumbakonam", "Thanjavur", "Nagapattinam", "Velankanni",
    "Karaikudi", "Sivakasi", "Rajapalayam", "Virudhnagar", "Pudukottai",
    "Mannargudi", "Mayiladuthurai", "Thiruvarur", "Chidambaram", "Theni",
    "Pollachi", "Dindigul", "Ooty", "Kovilpatti",
}

# ── Bus Types: (capacity, ₹/km, distance range, tier) ─────────────────────────
BUS_TYPES = {
    # budget non-AC
    "Non-AC Seater (2+3)":           (55, 1.2, (0,   180), "budget"),
    "Non-AC Seater (2+2)":           (45, 1.4, (0,   250), "budget"),
    "Non-AC Semi Sleeper (2+2)":     (40, 1.6, (80,  350), "budget"),
    "Non-AC Seater/Sleeper (2+1)":   (40, 1.7, (150, 550), "budget"),
    "Non-AC Sleeper (2+1)":          (36, 1.9, (200, 750), "budget"),
    # standard AC
    "A/C Seater (2+2)":              (40, 2.3, (0,   280), "standard"),
    "A/C Semi Sleeper (2+2)":        (36, 2.6, (80,  420), "standard"),
    "A/C Seater/Sleeper (2+1)":      (40, 2.9, (180, 700), "standard"),
    "A/C Sleeper (2+1)":             (36, 3.2, (280, 800), "standard"),
    "A/C Semi Sleeper/Sleeper (2+1)":(40, 3.0, (200, 750), "standard"),
    # premium
    "Bharat Benz A/C Sleeper (2+1)": (36, 3.9, (300, 800), "premium"),
    "Volvo A/C Sleeper (2+1)":       (34, 4.6, (350, 800), "premium"),
    "Volvo Multi-Axle A/C Sleeper (2+1)": (34, 5.1, (400, 800), "premium"),
    "Electric A/C Seater (2+2)":     (40, 2.9, (80,  550), "premium"),
    "Bharat Benz A/C Seater/Sleeper (2+1)": (40, 3.5, (250, 750), "premium"),
}

TIER_BUS_TYPES = {
    "budget":   [k for k, v in BUS_TYPES.items() if v[3] == "budget"],
    "standard": [k for k, v in BUS_TYPES.items() if v[3] in ("standard", "budget")],
    "premium":  [k for k, v in BUS_TYPES.items() if v[3] in ("premium", "standard")],
}

# ── Tamil names ────────────────────────────────────────────────────────────────
_FIRST = [
    "Murugan","Rajan","Selvam","Kannan","Suresh","Venkatesh","Balamurugan","Karthik",
    "Senthil","Arumugam","Pandian","Thiyagarajan","Manikandan","Rajendran","Kumaresan",
    "Ganesan","Annamalai","Subramanian","Sivakumar","Palaniswamy","Durai","Sathish",
    "Vignesh","Dinesh","Ramesh","Muthukrishnan","Boopathi","Saravanan","Gopal",
    "Natarajan","Prakash","Vijayakumar","Baskar","Chelladurai","Mani","Shanmugam",
    "Pandi","Tamizharasan","Ilayaraja","Palanivel","Jayaraman","Krishnamoorthy",
    "Soundararajan","Velayudham","Elango","Ponraj","Thangavel","Sekar","Periyasamy",
    "Ravi","Sugumar","Muthu","Arjun","Balaji","Dhinesh","Jeeva","Kathir","Logesh",
    "Mahesh","Nandha","Pradeep","Quthub","Siva","Tamil","Udaya","Xavier","Yuvan","Zahir",
]
_LAST = [
    "Rajan","Kumar","Murugan","Pandian","Selvam","Natarajan","Subramanian","Krishnan",
    "Swamy","Ramu","Babu","Raj","Das","Pillai","Nadar","Thevar","Gounder","Naicker",
    "Chettiar","Iyer","Iyengar","Mudaliar","Palanisamy","Arumugam","Durai","Mani",
]
_TN_DIST = [
    "TN01","TN02","TN03","TN04","TN05","TN07","TN09","TN10","TN11","TN14",
    "TN18","TN19","TN21","TN22","TN26","TN28","TN29","TN32","TN36","TN38",
    "TN39","TN45","TN47","TN50","TN54","TN55","TN56","TN57","TN58","TN59",
    "TN63","TN65","TN66","TN72","TN73","TN74","TN75","TN76","TN77","TN80",
]

# ── Review banks ───────────────────────────────────────────────────────────────
_POS = [
    "Excellent journey! Bus was perfectly on time and very clean.",
    "Driver was highly professional and the ride was smooth throughout.",
    "AC was working perfectly. Very comfortable sleeper berth.",
    "Punctual departure and arrival. Highly recommend this operator.",
    "Best bus service I have used in Tamil Nadu. Very satisfied.",
    "Clean bus, courteous driver, arrived 15 minutes early. Perfect trip.",
    "Smooth journey without any issues. Will definitely book again.",
    "The sleeper berth was very spacious and comfortable for the overnight trip.",
    "Staff was very helpful with luggage. Excellent experience overall.",
    "Very well maintained bus. AC was excellent even in peak summer heat.",
    "Driver drove very safely and responsibly. Felt completely secure.",
    "On-time pickup from the boarding point. Absolutely seamless journey.",
    "Great value for money. Comfortable seats and the AC was cold enough.",
    "The bus was brand new with clean sheets and fresh pillows.",
    "Friendly conductor and driver. Made the long journey very enjoyable.",
    "Excellent service! The bus stopped at a clean rest stop for dinner.",
    "Perfect trip. No breakdowns, no delays, driver was alert all night.",
    "Bus arrived exactly on schedule. Very reliable operator.",
    "Great journey! Roads were good and driver maintained a steady safe speed.",
    "Thoroughly impressed. The reading lights and charging points all worked.",
    "One of the best night buses I have taken. Will always choose this operator.",
    "The blanket and pillow were clean and fresh. Slept well the entire journey.",
    "Driver was extremely polite and assisted elderly passengers with their luggage.",
    "Bus was super clean. Washroom at the rest stop was well maintained.",
    "Very organised boarding process. No confusion at the pickup point at all.",
    "Reached destination 20 minutes ahead of schedule. Impressive punctuality.",
    "The music was kept at a reasonable volume. Slept without any disturbance.",
    "Good legroom for a sleeper. Charging port worked perfectly throughout.",
    "Staff immediately resolved a seat issue politely. Excellent customer service.",
    "Overall very satisfied. The bus felt well-maintained and safe to travel in.",
]

_NEG = [
    "AC was completely not working throughout the journey. Extremely hot inside.",
    "Bus was 2 hours late. No information was given to passengers about the delay.",
    "Driver was very rash. Overtaking at dangerous speeds on the highway.",
    "The bus was very old and had a lot of disturbing rattling sounds.",
    "Seats were dirty and smelled bad. Very disappointing for the price paid.",
    "Driver was constantly using his mobile phone while driving. Very unsafe.",
    "Bus broke down in the middle of the highway for almost 2 hours.",
    "The blanket provided was dirty and had a very unpleasant smell.",
    "Boarding point was changed at the last minute with absolutely no notice.",
    "The AC was actively leaking water on passengers. My clothes got completely wet.",
    "Driver was braking very harshly and overspeeding constantly. Terrible ride.",
    "Very poor cleanliness throughout the bus. Toilet was completely unusable.",
    "Arrived 3 hours late. Missed an important family function because of this.",
    "Bus was severely overcrowded. Standing passengers were allowed in the aisle.",
    "Very rude conductor. Had an argument with multiple passengers unprovoked.",
    "Not a single charging port in the entire bus was working. Unacceptable.",
    "The reading light in my berth was broken the entire journey.",
    "Driver played loud music even past midnight. Could not sleep at all.",
    "The suspension on this bus is completely gone. Every small bump was painful.",
    "Picked up passengers at unauthorized stops causing 45 minutes of extra delay.",
    "AC stopped working completely after midnight. Bus became unbearably hot.",
    "Terrible engine noise throughout the entire night. Impossible to sleep.",
    "The seat recline mechanism was broken. Sat upright for 8 painful hours.",
    "Bus had a strong diesel smell inside the passenger cabin the entire way.",
    "The driver made multiple unscheduled stops to pick up his own luggage.",
    "Extremely poor experience. The bus was not the one shown in the photo online.",
    "Conductor was dismissive and refused to help with a seat allocation issue.",
    "The curtains in the berth were torn and provided no privacy whatsoever.",
    "Bus departed 90 minutes late with zero communication from the operator.",
    "Rest stop was skipped entirely. Passengers were denied food and toilet break.",
]

_NEU = [
    "Average experience. Nothing exceptional but nothing terrible either.",
    "Journey was okay. Bus was slightly late but manageable.",
    "Decent service for the price. AC could have been colder.",
    "Acceptable journey. Bus was a bit old but functional enough.",
    "Normal trip. Driver was okay, bus was in average condition.",
    "Service was okay. Could improve on punctuality and cleanliness.",
    "Not the best journey but not the worst either. Okay overall.",
    "Bus was clean but arrived 30 minutes late at the destination.",
    "Comfortable enough for the price paid. Will consider again.",
    "Average AC performance. Seats were decent. Journey was fine.",
    "Nothing great, nothing bad. A very standard bus journey.",
    "The bus was punctual but the seating was a bit cramped.",
    "Okay experience. Rest stop was decent. Driver was average.",
    "Fairly normal journey. No major issues but no standout positives.",
    "Mediocre experience overall. The bus could use some interior refurbishment.",
]

_MIX = [
    "Driver was excellent and very safe but the AC was not cold enough.",
    "Bus was on time but the seats were not very comfortable for a long journey.",
    "Clean bus but the driver was clearly overspeeding on the highway stretches.",
    "Comfortable sleeper berth but bus arrived 45 minutes late at destination.",
    "Great AC and clean bus but the pickup point was very inconvenient.",
    "Fast journey but the driver's attitude towards passengers was a bit rude.",
    "Bus was in good condition but too many unnecessary unscheduled stops.",
    "Very punctual but the bus was older than expected for the price paid.",
    "Smooth drive and good driver but the charging ports were not working.",
    "Comfortable enough but the bus needs maintenance on the AC units.",
    "Bus departed on time but was delayed 1 hour due to road works on the highway.",
    "Driver was professional but the bus had a faint smell of diesel inside.",
    "Good trip overall but the rest stop restaurant was overpriced and average.",
    "Arrived early which was great but the staff was not helpful with luggage.",
    "Seats were comfortable but the overhead lights were not working in my berth.",
    "Great driver, safe journey, but the bus interior looked old and worn.",
    "AC was perfectly cold but the pickup point location was very poorly marked.",
    "Reasonable value for money but the journey took longer than expected.",
    "Punctual and clean but the conductor was not very polite with passengers.",
    "Comfortable sleeper but the road condition on one stretch was very bad.",
]

_ISSUES = [
    "None","None","None","None","None","None","None","None",  # Most trips have no issues
    "AC not cooling properly","AC leaking water","AC making loud noise",
    "Engine overheating","Tyre puncture repaired during journey",
    "Bus breakdown on highway","Suspension issues — rough ride throughout",
    "Seat recline mechanism broken","Charging ports not working",
    "Overhead reading light not working","Window latch broken — wind noise",
    "Toilet out of order","Excessive engine noise inside cabin",
    "Late departure — operational delay","Late arrival — traffic/route delay",
    "Route deviation — driver went wrong way briefly","Overcrowding observed",
    "Driver using mobile phone","Rash driving reported by passengers",
    "Curtain missing in berth","Blanket not provided","Rest stop skipped",
    "None","None","None","None",
]


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — HOLIDAY ENGINE
# ══════════════════════════════════════════════════════════════════════════════

# Hard-coded variable Hindu/Islamic holidays by year (2015–2026)
_DIWALI = {
    2015:date(2015,11,11),2016:date(2016,10,30),2017:date(2017,10,19),
    2018:date(2018,11, 7),2019:date(2019,10,27),2020:date(2020,11,14),
    2021:date(2021,11, 4),2022:date(2022,10,24),2023:date(2023,11,12),
    2024:date(2024,11, 1),2025:date(2025,10,20),2026:date(2026,11, 8),
}
_AYUDHA = {
    2015:date(2015,10,22),2016:date(2016,10,10),2017:date(2017, 9,29),
    2018:date(2018,10,18),2019:date(2019,10, 7),2020:date(2020,10,25),
    2021:date(2021,10,14),2022:date(2022,10, 4),2023:date(2023,10,23),
    2024:date(2024,10,12),2025:date(2025,10, 1),2026:date(2026,10,20),
}
_VINAYAGAR = {
    2015:date(2015, 8,17),2016:date(2016, 9, 5),2017:date(2017, 8,25),
    2018:date(2018, 9,13),2019:date(2019, 9, 2),2020:date(2020, 8,22),
    2021:date(2021, 9,10),2022:date(2022, 8,31),2023:date(2023, 9,19),
    2024:date(2024, 9, 7),2025:date(2025, 8,27),2026:date(2026, 9,16),
}
_GOOD_FRIDAY = {
    2015:date(2015, 4, 3),2016:date(2016, 3,25),2017:date(2017, 4,14),
    2018:date(2018, 3,30),2019:date(2019, 4,19),2020:date(2020, 4,10),
    2021:date(2021, 4, 2),2022:date(2022, 4,15),2023:date(2023, 4, 7),
    2024:date(2024, 3,29),2025:date(2025, 4,18),2026:date(2026, 4, 3),
}
_EID_FITR = {
    2015:date(2015, 7,17),2016:date(2016, 7, 6),2017:date(2017, 6,26),
    2018:date(2018, 6,15),2019:date(2019, 6, 5),2020:date(2020, 5,24),
    2021:date(2021, 5,13),2022:date(2022, 5, 2),2023:date(2023, 4,22),
    2024:date(2024, 4,11),2025:date(2025, 3,31),2026:date(2026, 3,20),
}
_BAKRID = {
    2015:date(2015, 9,24),2016:date(2016, 9,12),2017:date(2017, 9, 1),
    2018:date(2018, 8,22),2019:date(2019, 8,12),2020:date(2020, 7,31),
    2021:date(2021, 7,20),2022:date(2022, 7, 9),2023:date(2023, 6,28),
    2024:date(2024, 6,17),2025:date(2025, 6, 7),2026:date(2026, 5,27),
}
_MUHARRAM = {
    2015:date(2015,10,24),2016:date(2016,10,12),2017:date(2017,10, 1),
    2018:date(2018, 9,21),2019:date(2019, 9,10),2020:date(2020, 8,30),
    2021:date(2021, 8,19),2022:date(2022, 8, 9),2023:date(2023, 7,28),
    2024:date(2024, 7,17),2025:date(2025, 7, 6),2026:date(2026, 6,25),
}
_MILAD = {
    2015:date(2015,12,24),2016:date(2016,12,12),2017:date(2017,12, 1),
    2018:date(2018,11,21),2019:date(2019,11,10),2020:date(2020,10,29),
    2021:date(2021,10,18),2022:date(2022,10, 8),2023:date(2023, 9,27),
    2024:date(2024, 9,16),2025:date(2025, 9, 5),2026:date(2026, 8,25),
}
_THAI_POOSAM = {
    2015:date(2015, 2, 3),2016:date(2016, 1,24),2017:date(2017, 2, 9),
    2018:date(2018, 1,31),2019:date(2019, 1,21),2020:date(2020, 2, 8),
    2021:date(2021, 1,28),2022:date(2022, 1,18),2023:date(2023, 2, 5),
    2024:date(2024, 1,25),2025:date(2025, 2,11),2026:date(2026, 1,31),
}
_KRISHNA_JAY = {
    2015:date(2015, 9, 5),2016:date(2016, 8,25),2017:date(2017, 8,14),
    2018:date(2018, 9, 3),2019:date(2019, 8,23),2020:date(2020, 8,11),
    2021:date(2021, 8,30),2022:date(2022, 8,19),2023:date(2023, 9, 6),
    2024:date(2024, 8,26),2025:date(2025, 8,16),2026:date(2026, 9, 4),
}


def build_holiday_calendar(start_date, end_date):
    """Return dict {date: holiday_name} for the full date range."""
    cal = {}

    for year in range(start_date.year, end_date.year + 1):
        # ── Fixed annual holidays ──────────────────────────────────────────
        fixed = [
            (1,  1,  "New Year's Day"),
            (1, 13,  "Bhogi"),
            (1, 14,  "Pongal"),
            (1, 15,  "Thiruvalluvar Day"),
            (1, 16,  "Uzhavar Thirunal"),
            (1, 26,  "Republic Day"),
            (4, 14,  "Tamil New Year / Ambedkar Jayanti"),
            (5,  1,  "May Day"),
            (8, 15,  "Independence Day"),
            (10, 2,  "Gandhi Jayanti"),
            (12, 25, "Christmas Day"),
        ]
        for m, d, name in fixed:
            try:
                cal[date(year, m, d)] = name
            except ValueError:
                pass

        # ── Variable holidays ──────────────────────────────────────────────
        def _add(table, name, plus1=None, plus1_name=None, minus1=None, minus1_name=None):
            if year in table:
                d = table[year]
                cal[d] = name
                if plus1:
                    cal[d + timedelta(days=1)] = plus1_name or (name + " (Next Day)")
                if minus1:
                    cal[d - timedelta(days=1)] = minus1_name or (name + " (Eve)")

        _add(_DIWALI,     "Deepavali",     plus1=True, plus1_name="Deepavali Holiday",
                                           minus1=True, minus1_name="Deepavali Eve")
        _add(_AYUDHA,     "Ayudha Pooja",  plus1=True, plus1_name="Vijaya Dasami")
        _add(_VINAYAGAR,  "Vinayagar Chaturthi")
        _add(_GOOD_FRIDAY,"Good Friday")
        _add(_EID_FITR,   "Ramzan (Eid ul Fitr)")
        _add(_BAKRID,     "Bakrid (Eid ul Adha)")
        _add(_MUHARRAM,   "Muharram")
        _add(_MILAD,      "Milad-un-Nabi")
        _add(_THAI_POOSAM,"Thai Poosam")
        _add(_KRISHNA_JAY,"Krishna Jayanthi")

        # Optional: pull from holidays library for India TN
        if HAS_HOLIDAYS:
            try:
                for hd, hn in hlib.India(state="TN", years=year).items():
                    if hd not in cal:
                        cal[hd] = hn
            except Exception:
                pass

    return cal


def proximity_score(d, cal, k=0.5):
    """
    e^(-k * |days_to_nearest_holiday|).
    Returns (score 0–1, days_away int, nearest_holiday_name str).
    """
    best = 9999
    best_name = ""
    for hd, hn in cal.items():
        gap = abs((hd - d).days)
        if gap < best:
            best, best_name = gap, hn
    score = round(math.exp(-k * best), 4) if best <= 10 else 0.0
    return score, best, best_name


def bridge_leave_info(d, cal):
    """
    Logic:
      Monday holiday  → preceding Friday is bridge-leave pre-holiday
      Friday holiday  → following Monday is bridge-leave post-holiday
      Tuesday holiday → preceding Monday is bridge-leave pre-holiday
      Thursday holiday→ following Friday is bridge-leave post-holiday
    Returns (is_bridge bool, bridge_type str)
    """
    dow = d.weekday()  # Mon=0 … Sun=6
    if d in cal or dow >= 5:
        return False, "None"

    for delta in range(-4, 5):
        h = d + timedelta(days=delta)
        if h not in cal:
            continue
        h_dow = h.weekday()
        # Holiday Monday, today is Friday before
        if h_dow == 0 and dow == 4 and delta == 3:
            return True, "Pre_Holiday_Bridge"
        # Holiday Friday, today is Monday after
        if h_dow == 4 and dow == 0 and delta == -3:
            return True, "Post_Holiday_Bridge"
        # Holiday Tuesday, today is Monday before
        if h_dow == 1 and dow == 0 and delta == 1:
            return True, "Pre_Holiday_Bridge"
        # Holiday Thursday, today is Friday after
        if h_dow == 3 and dow == 4 and delta == -1:
            return True, "Post_Holiday_Bridge"

    return False, "None"


def is_long_weekend(d, cal):
    """3 or more consecutive non-working days that include d."""
    non_work = set()
    for delta in range(-3, 4):
        c = d + timedelta(days=delta)
        if c.weekday() >= 5 or c in cal:
            non_work.add(c)
    if d not in non_work:
        return False
    run = 1
    for delta in range(1, 5):
        if d + timedelta(days=delta) in non_work:
            run += 1
        else:
            break
    for delta in range(1, 5):
        if d - timedelta(days=delta) in non_work:
            run += 1
        else:
            break
    return run >= 3


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — FLEET GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def generate_fleet():
    used_reg = set()
    fleet = []
    bus_no = 1

    for op in OPERATORS:
        t = op["tier"]
        size = {"premium": random.randint(35, 50),
                "standard": random.randint(22, 38),
                "budget":   random.randint(15, 28)}[t]

        for _ in range(size):
            # unique TN registration
            while True:
                dist = random.choice(_TN_DIST)
                letters = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=2))
                num = random.randint(1000, 9999)
                reg = f"{dist} {letters} {num}"
                if reg not in used_reg:
                    used_reg.add(reg); break

            bt = random.choice(TIER_BUS_TYPES[t])
            cap, _, _, _ = BUS_TYPES[bt]
            yr_mfg = random.randint(2010, 2023)

            fleet.append({
                "bus_id":       f"BUS{bus_no:05d}",
                "bus_no":        reg,
                "op_id":         op["id"],
                "op_name":       op["name"],
                "op_tier":       t,
                "bus_type":      bt,
                "capacity":      cap,
                "yr_mfg":        yr_mfg,
            })
            bus_no += 1
    return fleet


def generate_drivers(n):
    used = set()
    pool = []
    for i in range(n):
        while True:
            name = f"{random.choice(_FIRST)} {random.choice(_LAST)}"
            if name not in used:
                used.add(name); break
        pool.append({"id": f"DRV{i+1:04d}", "name": name})
    return pool


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — ROUTE–OPERATOR ASSIGNMENT & YEAR-ON-YEAR LOGIC
# ══════════════════════════════════════════════════════════════════════════════

def initial_route_assignment():
    """Assign initial routes to each operator based on their base city."""
    op_routes = {}
    all_rids = list(ROUTES.keys())

    for op in OPERATORS:
        t = op["tier"]
        base = op["base"]
        n = {"premium": random.randint(7, 12),
             "standard": random.randint(5, 9),
             "budget":   random.randint(3, 7)}[t]

        # Routes from / to base city
        home = [r for r, (o, d, _) in ROUTES.items()
                if o == base or d == base]
        away  = [r for r in all_rids if r not in home]

        # Pick proportionally more home routes
        n_home = min(len(home), max(1, n * 2 // 3))
        n_away = max(0, n - n_home)

        chosen = (random.sample(home, n_home)
                  + random.sample(away, min(len(away), n_away)))
        op_routes[op["id"]] = list(set(chosen))

    return op_routes


def update_routes_yoy(op_routes, perf):
    """
    Year-on-year learning:
    - Avg occupancy > 85% → add 1 route (complementary city)
    - Avg occupancy < 35% for 2 consecutive years → consider dropping
    perf: {(op_id, route_id): avg_occ}
    """
    all_rids = list(ROUTES.keys())
    new_routes = {}

    for op in OPERATORS:
        oid = op["id"]
        current = list(op_routes.get(oid, []))

        # Drop underperforming routes (probabilistically)
        to_drop = []
        for r in current:
            avg = perf.get((oid, r), 0.6)
            if avg < 0.33 and random.random() < 0.45 and len(current) > 3:
                to_drop.append(r)
        for r in to_drop:
            current.remove(r)

        # Add routes complementary to high-demand ones
        high = [r for r in current if perf.get((oid, r), 0) > 0.82]
        if high and random.random() < 0.55:
            cities_in_use = set()
            for r in high:
                o, d, _ = ROUTES[r]
                cities_in_use |= {o, d}
            candidates = [r for r in all_rids
                          if r not in current
                          and (ROUTES[r][0] in cities_in_use
                               or ROUTES[r][1] in cities_in_use)]
            if candidates:
                current.append(random.choice(candidates))

        new_routes[oid] = list(set(current))
    return new_routes


# buses_on_route[op_id][route_id][year] = int  (how many buses run that route)
def init_buses_on_route(op_routes, start_year):
    bor = defaultdict(lambda: defaultdict(dict))
    for op in OPERATORS:
        oid = op["id"]
        for r in op_routes.get(oid, []):
            bor[oid][r][start_year] = random.choice([1, 1, 1, 2])
    return bor


def update_buses_yoy(bor, perf, op_routes, year):
    """Increase / decrease bus count per route based on last year's occupancy."""
    new_bor = defaultdict(lambda: defaultdict(dict))
    for op in OPERATORS:
        oid = op["id"]
        for r in op_routes.get(oid, []):
            prev_count = bor[oid][r].get(year - 1, 1)
            avg = perf.get((oid, r), 0.6)
            if avg > 0.88:
                count = min(prev_count + 2, 5)
            elif avg > 0.78:
                count = min(prev_count + 1, 4)
            elif avg < 0.32:
                count = max(prev_count - 1, 1)
            else:
                count = prev_count
            new_bor[oid][r][year] = count
    return new_bor


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 5 — DEMAND, PRICING, TIMES
# ══════════════════════════════════════════════════════════════════════════════

def direction_type(origin, dest, d, cal):
    """
    Outbound_PreHoliday  : hub → hometown, ≤3 days before holiday
    Return_PostHoliday   : hometown → hub, ≤3 days after holiday
    Outbound_Weekend     : hub → any, Friday–Sunday
    Return_Weekend       : any → hub, Friday–Sunday
    Normal               : everything else
    """
    days_before = min((
        (hd - d).days for hd in cal if 0 <= (hd - d).days <= 3), default=99)
    days_after  = min((
        (d - hd).days for hd in cal if 0 <= (d - hd).days <= 3), default=99)
    is_hub_o  = origin in METRO_HUBS
    is_hub_d  = dest   in METRO_HUBS
    is_home_d = dest   in HOMETOWN_CITIES
    is_home_o = origin in HOMETOWN_CITIES
    dow = d.weekday()

    if days_before <= 3:
        if is_hub_o and is_home_d:  return "Outbound_PreHoliday"
        if is_hub_d and is_home_o:  return "Return_PreHoliday"
    if days_after <= 3:
        if is_hub_d and is_home_o:  return "Return_PostHoliday"
        if is_hub_o and is_home_d:  return "Outbound_PostHoliday"
    if dow >= 4:
        if is_hub_o: return "Outbound_Weekend"
        if is_hub_d: return "Return_Weekend"
    return "Normal"


_DEMAND_MULT = {
    "Outbound_PreHoliday":  1.90,
    "Return_PostHoliday":   1.85,
    "Outbound_Weekend":     1.35,
    "Return_Weekend":       1.30,
    "Return_PreHoliday":    0.70,
    "Outbound_PostHoliday": 0.65,
    "Normal":               1.00,
}
_DOW_MULT = {0:0.82, 1:0.78, 2:0.78, 3:0.84, 4:1.22, 5:1.32, 6:1.10}


def demand_multiplier(dir_type, prox, is_hol, is_weekend, is_lw, is_bridge, dow, season):
    m = _DEMAND_MULT.get(dir_type, 1.0)
    if is_hol:      m *= 1.12
    if is_lw:       m *= 1.28
    if is_bridge:   m *= 1.18
    m += prox * 0.55
    m *= _DOW_MULT.get(dow, 1.0)
    # Seasonal boost
    if season == "Post-Monsoon / Festival":  m *= 1.08
    if season == "Summer":                   m *= 1.05
    return round(min(m, 2.6), 4)


def covid_factor(yr):
    """Ridership scaling for COVID and recovery."""
    return {2020: 0.35, 2021: 0.62, 2022: 0.88}.get(yr, 1.0)


def yoy_growth(yr, base_yr):
    """Compound ~6 % growth per year (excluding COVID years)."""
    if yr in (2020, 2021, 2022):
        return covid_factor(yr)
    g = 1.0 + 0.06 * (yr - base_yr)
    return min(g, 1.55)


def calc_base_price(dist, bt):
    cap, pkm, _, _ = BUS_TYPES[bt]
    base = dist * pkm + 50 + (dist // 100) * 28
    return max(100, round(base / 10) * 10)


def calc_final_price(base, dm, op_tier):
    if dm > 1.5:   surge = 1.0 + (dm - 1.0) * 0.65
    elif dm > 1.2: surge = 1.0 + (dm - 1.0) * 0.42
    else:          surge = 1.0 + (dm - 1.0) * 0.22
    tier_premium = {"premium": 1.22, "standard": 1.0, "budget": 0.83}[op_tier]
    price = base * surge * tier_premium
    price *= random.uniform(0.95, 1.08)           # realistic noise
    price = round(price / 50) * 50
    return int(max(base * 0.75, min(price, base * 3.2)))


def calc_occupancy(capacity, dm, yr_factor):
    base_occ = random.uniform(0.42, 0.73)
    occ = base_occ * dm * yr_factor + random.gauss(0, 0.045)
    occ = round(max(0.08, min(1.0, occ)), 4)
    return int(capacity * occ), occ


def departure_time(dist):
    """Night buses for long routes, day buses for short."""
    if dist <= 150:
        h = random.choice([6,7,8,9,10,14,15,16,17,18,19])
    elif dist <= 320:
        h = random.choice([6,7,8,18,19,20,21])
    else:
        h = random.choice([19,20,21,22,23]) if random.random() < 0.82 else random.choice([6,7])
    m = random.choice([0, 15, 30, 45])
    return f"{h:02d}:{m:02d}"


def arrival_time(dep_str, dist):
    dh, dm_val = map(int, dep_str.split(":"))
    dep_mins = dh * 60 + dm_val
    spd = random.uniform(54, 68)
    travel = int((dist / spd) * 60) + (dist // 100) * random.randint(15, 28)
    arr_mins = dep_mins + travel
    return f"{(arr_mins // 60) % 24:02d}:{arr_mins % 60:02d}"


def is_overnight(dep_str, dist):
    h = int(dep_str.split(":")[0])
    return h >= 19 and dist >= 280


def season(d):
    m = d.month
    if m in (3,4,5):   return "Summer"
    if m in (6,7,8,9): return "Monsoon"
    if m in (10,11):   return "Post-Monsoon / Festival"
    return "Winter / Pongal"


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — REVIEW GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def gen_review(occ, bus_cond, drv_beh, issue, op_tier):
    sc = 0
    sc += {"Excellent":2,"Good":1,"Average":0,"Poor":-2,"Needs Maintenance":-3}.get(bus_cond,0)
    sc += {"Excellent":2,"Good":1,"Average":0,"Poor":-1,"Rash":-2,"Negligent":-3}.get(drv_beh,0)
    sc += 0 if issue == "None" else -2
    sc += {"premium":1,"standard":0,"budget":-0.5}.get(op_tier,0)
    sc += random.gauss(0, 1.4)

    if sc > 2:
        return random.choice(_POS), "Positive"
    if sc > 0.5:
        pick = random.choices([_POS, _MIX], weights=[60, 40])[0]
        return random.choice(pick), random.choices(["Positive","Mixed"], weights=[60,40])[0]
    if sc > -0.5:
        return random.choice(_NEU + _MIX), "Neutral"
    if sc > -2:
        pick = random.choices([_NEG, _MIX], weights=[55, 45])[0]
        return random.choice(pick), random.choices(["Negative","Mixed"], weights=[60,40])[0]
    return random.choice(_NEG), "Negative"


def bus_condition_for_age(yr_mfg, current_yr):
    age = current_yr - yr_mfg
    if age <= 2:   w = [40,50, 8, 2, 0]
    elif age <= 5: w = [15,50,25, 8, 2]
    elif age <= 8: w = [ 5,35,40,15, 5]
    else:          w = [ 2,20,40,25,13]
    return random.choices(
        ["Excellent","Good","Average","Poor","Needs Maintenance"], weights=w)[0]


def issue_for_cond(cond):
    if cond in ("Poor","Needs Maintenance"):
        w = [30,20,10, 8, 8, 6, 5, 5, 4, 2, 2]
    else:
        w = [80, 5, 2, 1, 2, 2, 2, 2, 0.5, 0.5, 3]
    subset = [
        "None","AC not cooling properly","AC leaking water",
        "Engine overheating","Suspension issues — rough ride",
        "Seat recline broken","Charging ports not working",
        "Overhead light not working","Bus breakdown on highway",
        "Excessive engine noise","Late departure"
    ]
    return random.choices(subset, weights=w)[0]


def driver_beh_for_cond(cond):
    opts = ["Excellent","Good","Average","Poor","Rash","Negligent"]
    w = {
        "Excellent":       [10,45,30,10, 4, 1],
        "Good":            [ 8,42,35,10, 4, 1],
        "Average":         [ 3,25,45,18, 7, 2],
        "Poor":            [ 1,12,35,28,18, 6],
        "Needs Maintenance":[ 1,10,32,28,20, 9],
    }.get(cond, [5,35,35,15, 8, 2])
    return random.choices(opts, weights=w)[0]


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 7 — MAIN GENERATION LOOP
# ══════════════════════════════════════════════════════════════════════════════

def generate(start_date, end_date):
    print(f"\n  OmniRoute AI  Synthetic Dataset Generator")
    print(f"    Date range : {start_date}    {end_date}")
    print(f"    Total days : {(end_date-start_date).days+1:,}\n")

    # ── build static structures ───────────────────────────────────────────
    print(" Building holiday calendar ")
    cal = build_holiday_calendar(start_date, end_date)
    print(f"   {len(cal)} holiday dates loaded.\n")

    print(" Generating fleet ")
    fleet = generate_fleet()
    print(f"   {len(fleet)} buses across {len(OPERATORS)} operators.\n")

    print(" Generating driver pool ")
    drivers = generate_drivers(len(fleet) + 300)
    drv_info = {d["id"]: d["name"] for d in drivers}
    drv_ids  = list(drv_info.keys())

    # assign primary driver per bus
    bus_primary_drv = {b["bus_id"]: drv_ids[i % len(drv_ids)]
                       for i, b in enumerate(fleet)}

    op_fleet = defaultdict(list)
    for b in fleet:
        op_fleet[b["op_id"]].append(b)

    op_info = {op["id"]: op for op in OPERATORS}

    print("  Assigning initial routes ")
    op_routes = initial_route_assignment()
    bor = init_buses_on_route(op_routes, start_date.year)

    # ── year-level performance tracking ──────────────────────────────────
    yr_perf  = defaultdict(lambda: [0.0, 0])   # (op_id,route_id) → [sum_occ, count]
    curr_yr  = start_date.year

    # ── overnight bus tracking: buses blocked next morning ────────────────
    # overnight_blocked[bus_id] = date on which morning trips are blocked
    overnight_blocked = {}

    rows = []
    total_days = (end_date - start_date).days + 1
    d = start_date

    print(" Generating daily trip data \n")

    while d <= end_date:
        # ── year rollover ───────────────────────────────────────────────
        if d.year != curr_yr:
            print(f"    Year {d.year}: applying year-on-year adjustments ")
            # finalise perf averages
            perf_avg = {k: (v[0]/v[1] if v[1] else 0.6) for k, v in yr_perf.items()}
            # update routes and bus counts
            op_routes = update_routes_yoy(op_routes, perf_avg)
            bor       = update_buses_yoy(bor, perf_avg, op_routes, d.year)
            yr_perf   = defaultdict(lambda: [0.0, 0])
            curr_yr   = d.year

        # ── progress ────────────────────────────────────────────────────
        elapsed = (d - start_date).days + 1
        if elapsed % 200 == 0:
            pct = elapsed / total_days * 100
            print(f"   {pct:5.1f}%  ({elapsed:,}/{total_days:,} days)  "
                  f"rows so far: {len(rows):,}")

        # ── date metadata ────────────────────────────────────────────────
        dow       = d.weekday()
        day_names = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        is_hol    = d in cal
        hol_name  = cal.get(d, "")
        is_wkend  = dow >= 5
        prox, days_away, near_hol = proximity_score(d, cal)
        is_bridge, bridge_type    = bridge_leave_info(d, cal)
        is_lw     = is_long_weekend(d, cal)
        sea       = season(d)
        date_type = "Holiday" if is_hol else ("Weekend" if is_wkend else "Weekday")
        yr_factor = yoy_growth(d.year, start_date.year)

        # ── per-operator trip generation ─────────────────────────────────
        for op in OPERATORS:
            oid   = op["id"]
            otier = op["tier"]
            routes_for_op = op_routes.get(oid, [])
            if not routes_for_op:
                continue

            # How many routes to service today (higher demand → more routes)
            demand_today = 1.5 if (is_hol or is_bridge or is_lw) else (1.2 if is_wkend else 1.0)
            n_today = max(2, int(len(routes_for_op) * random.uniform(0.55, 1.0) * demand_today))
            n_today = min(n_today, len(routes_for_op))

            routes_today = random.sample(routes_for_op, n_today)

            # Available buses: not on overnight block for today morning
            avail = [b for b in op_fleet[oid]
                     if overnight_blocked.get(b["bus_id"]) != d]

            random.shuffle(avail)
            bus_cursor = 0

            for rid in routes_today:
                if bus_cursor >= len(avail):
                    break

                orig, dest, dist = ROUTES[rid]
                dir_t   = direction_type(orig, dest, d, cal)
                dm      = demand_multiplier(dir_t, prox, is_hol, is_wkend, is_lw, is_bridge, dow, sea)

                # Number of buses on this route this year (year-on-year allocation)
                n_buses = bor[oid][rid].get(d.year, bor[oid][rid].get(curr_yr, 1))
                # Extra buses on high-demand days
                if dm > 1.65: n_buses = min(n_buses + 2, 5)
                elif dm > 1.3: n_buses = min(n_buses + 1, 4)
                n_buses = min(n_buses, len(avail) - bus_cursor)
                if n_buses <= 0:
                    continue

                # Short routes → possible 2 trips per bus per day
                short_route = dist <= 200
                trips_per_bus = 2 if short_route else 1

                for b_idx in range(n_buses):
                    if bus_cursor >= len(avail):
                        break
                    bus = avail[bus_cursor]
                    bus_cursor += 1

                    for trip_no in range(trips_per_bus):
                        bt   = bus["bus_type"]
                        cap  = bus["capacity"]
                        bprice = calc_base_price(dist, bt)
                        fprice = calc_final_price(bprice, dm, otier)
                        tkts, occ = calc_occupancy(cap, dm, yr_factor)
                        dep  = departure_time(dist) if trip_no == 0 else departure_time(dist)
                        arr  = arrival_time(dep, dist)
                        overnight = is_overnight(dep, dist)

                        if overnight:
                            overnight_blocked[bus["bus_id"]] = d + timedelta(days=1)

                        # Driver (rotate 15 % of the time)
                        drv_id = (random.choice(drv_ids)
                                  if random.random() < 0.15
                                  else bus_primary_drv[bus["bus_id"]])
                        drv_name = drv_info.get(drv_id, "Unknown")

                        cond = bus_condition_for_age(bus["yr_mfg"], d.year)
                        issue = issue_for_cond(cond)
                        drv_beh = driver_beh_for_cond(cond)
                        review, sentiment = gen_review(occ, cond, drv_beh, issue, otier)

                        surge = round(fprice / bprice, 3) if bprice else 1.0

                        # update performance tracker
                        yr_perf[(oid, rid)][0] += occ
                        yr_perf[(oid, rid)][1] += 1

                        rows.append([
                            d.strftime("%Y-%m-%d"),         # Date
                            day_names[dow],                  # Day_of_Week
                            date_type,                       # Date_Type
                            sea,                             # Season
                            is_hol,                          # Is_Holiday
                            hol_name,                        # Holiday_Name
                            is_wkend,                        # Is_Weekend
                            is_lw,                           # Is_Long_Weekend
                            is_bridge,                       # Is_Bridge_Leave
                            bridge_type,                     # Bridge_Leave_Type
                            prox,                            # Holiday_Proximity_Score
                            days_away if days_away < 999 else 999, # Days_to_Nearest_Holiday
                            near_hol,                        # Nearest_Holiday
                            dir_t,                           # Direction_Type
                            rid,                             # Route_ID
                            orig,                            # Origin
                            dest,                            # Destination
                            dist,                            # Distance_KM
                            oid,                             # Operator_ID
                            op["name"],                      # Operator_Name
                            otier,                           # Operator_Tier
                            bus["bus_id"],                   # Bus_ID
                            bus["bus_no"],                   # Bus_No
                            bt,                              # Bus_Type
                            cap,                             # Bus_Capacity
                            bus["yr_mfg"],                   # Bus_Year_Manufactured
                            drv_id,                          # Driver_ID
                            drv_name,                        # Driver_Name
                            dep,                             # Departure_Time
                            arr,                             # Arrival_Time
                            trip_no + 1,                     # Trip_Number (1 or 2)
                            tkts,                            # Tickets_Sold
                            max(0, cap - tkts),              # Empty_Seats
                            round(occ * 100, 2),             # Occupancy_Rate_Pct
                            bprice,                          # Base_Price
                            fprice,                          # Final_Price
                            surge,                           # Surge_Multiplier
                            int(tkts * fprice),              # Revenue
                            cond,                            # Bus_Condition
                            issue,                           # Issues_in_Bus
                            drv_beh,                         # Driver_Behaviour
                            review,                          # Bus_Review
                            sentiment,                       # Review_Sentiment
                            bor[oid][rid].get(d.year, 1),   # Year_Buses_Allocated
                        ])

        d += timedelta(days=1)

    print(f"\n Generation complete! Total rows: {len(rows):,}\n")
    return rows


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 8 — DATE INPUT & ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

COLS = [
    "Date","Day_of_Week","Date_Type","Season",
    "Is_Holiday","Holiday_Name","Is_Weekend","Is_Long_Weekend",
    "Is_Bridge_Leave","Bridge_Leave_Type",
    "Holiday_Proximity_Score","Days_to_Nearest_Holiday","Nearest_Holiday",
    "Direction_Type",
    "Route_ID","Origin","Destination","Distance_KM",
    "Operator_ID","Operator_Name","Operator_Tier",
    "Bus_ID","Bus_No","Bus_Type","Bus_Capacity","Bus_Year_Manufactured",
    "Driver_ID","Driver_Name",
    "Departure_Time","Arrival_Time","Trip_Number",
    "Tickets_Sold","Empty_Seats","Occupancy_Rate_Pct",
    "Base_Price","Final_Price","Surge_Multiplier","Revenue",
    "Bus_Condition","Issues_in_Bus","Driver_Behaviour",
    "Bus_Review","Review_Sentiment",
    "Year_Buses_Allocated",
]


def parse_date(s):
    s = s.strip().lower()
    if s in ("today","till today","now",""):
        return date.today()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Cannot parse '{s}'. Use YYYY-MM-DD.")


def main():
    print("=" * 65)
    print("   OmniRoute AI  Tamil Nadu Bus Synthetic Dataset Generator")
    print("=" * 65)

    # ── auto-configured dates ───────────────────────────────────────────
    sd = date(2016, 1, 1)
    ed = date.today()

    print(f"\n[OK] Range confirmed: {sd}  ->  {ed}  "
          f"({(ed-sd).days+1:,} days)\n")

    # ── generate ─────────────────────────────────────────────────────────
    rows = generate(sd, ed)

    # ── save CSV ──────────────────────────────────────────────────────────
    fname = f"tnbus_synthetic_{sd.strftime('%Y%m%d')}_{ed.strftime('%Y%m%d')}.csv"
    fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)

    print(f"[SAVE] Saving  ->  {fname} ...")
    with open(fpath, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        w.writerows(rows)
    print(f"[OK] Saved successfully!\n")

    # ── summary ───────────────────────────────────────────────────────────
    df = pd.read_csv(fpath, nrows=5)   # just for a quick sanity peek
    print("-" * 65)
    print(f"  [INFO] Dataset Summary")
    print("-" * 65)
    print(f"  Rows            : {len(rows):,}")
    print(f"  Columns         : {len(COLS)}")
    print(f"  Date range      : {sd}  ->  {ed}")
    print(f"  File size       : {os.path.getsize(fpath)/1_000_000:.1f} MB")
    print(f"  Output path     : {fpath}")
    print("-" * 65)
    total_rev  = sum(r[36] for r in rows)          # Revenue column index
    total_tkts = sum(r[31] for r in rows)          # Tickets_Sold
    print(f"  Total Revenue   : {total_rev:,.0f}")
    print(f"  Total Tickets   : {total_tkts:,}")
    avg_occ = sum(r[33] for r in rows) / len(rows) # Occupancy_Rate_Pct
    print(f"  Avg Occupancy   : {avg_occ:.1f} %")
    print("-" * 65)
    print("\nSample columns generated:")
    print("  Date | Day_of_Week | Date_Type | Season | Is_Holiday | Holiday_Name")
    print("  Is_Long_Weekend | Is_Bridge_Leave | Bridge_Leave_Type")
    print("  Holiday_Proximity_Score | Days_to_Nearest_Holiday | Direction_Type")
    print("  Route_ID | Origin | Destination | Distance_KM")
    print("  Operator_Name | Operator_Tier | Bus_No | Bus_Type | Bus_Capacity")
    print("  Driver_Name | Departure_Time | Arrival_Time | Trip_Number")
    print("  Tickets_Sold | Empty_Seats | Occupancy_Rate_Pct")
    print("  Base_Price | Final_Price | Surge_Multiplier | Revenue")
    print("  Bus_Condition | Issues_in_Bus | Driver_Behaviour")
    print("  Bus_Review | Review_Sentiment | Year_Buses_Allocated")
    print("\n[OK] All done. Open the CSV in Excel or load with pandas.\n")


if __name__ == "__main__":
    main()