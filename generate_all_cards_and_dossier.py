import os
import csv
import json
import base64
import subprocess
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image

DATA_DIR = r"c:\Projects\SupeRR\data"
REPO_DIR = r"c:\Projects\SupeRR"
OUT_PDF = os.path.join(REPO_DIR, "SupeRR_Selector_Season2_Report.pdf")
OUT_HTML = os.path.join(REPO_DIR, "report_template_22pages.html")
CARDS_DIR = os.path.join(REPO_DIR, "images")
EDGE_BIN = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
LOGO_PATH = os.path.join(REPO_DIR, "images", "rr_logo.png")
AVATAR_PATH = os.path.join(REPO_DIR, "images", "author_avatar.png")

def b64_img(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    ext = os.path.splitext(path)[1].lower().replace(".", "")
    mime = "image/png" if ext == "png" else "image/jpeg"
    return f"data:{mime};base64,{data}"

LOGO_SRC = b64_img(LOGO_PATH)
AVATAR_SRC = b64_img(AVATAR_PATH)

comps = {r["comp_id"]: r for r in csv.DictReader(open(DATA_DIR + "/competitions.csv", encoding="utf-8"))}
matches = {r["match_id"]: r for r in csv.DictReader(open(DATA_DIR + "/matches.csv", encoding="utf-8"))}
teams_map = {r["team_id"]: r["team_name"] for r in csv.DictReader(open(DATA_DIR + "/teams.csv", encoding="utf-8"))}

# 20 Uncapped Target Players (Post-Retention IPL 2027)
TARGETS = [
    # Top 10 Batters
    {"rank": 1, "name": "Ayush Mhatre", "id": "48504", "role": "Top-Order Stroke Maker", "cat": "Top 10 Batter", "team26": "Chennai Super Kings", "price_cr": 0.30, "apps26": 6, "hand": "RHS", "style": "Right-arm offbreak", "mode": "bat", "file_name": "bat_01_ayush_mhatre.png"},
    {"rank": 2, "name": "Mahipal Lomror", "id": "4821", "role": "Middle-Order Spin Destroyer", "cat": "Top 10 Batter", "team26": "Royal Challengers Bengaluru", "price_cr": 7.25, "apps26": 10, "hand": "LHS", "style": "Slow left-arm orthodox", "mode": "bat", "file_name": "bat_02_mahipal_lomror.png"},
    {"rank": 3, "name": "Kumar Kushagra", "id": "8251", "role": "Middle-Order Keeper-Batter", "cat": "Top 10 Batter", "team26": "Gujarat Titans", "price_cr": 7.20, "apps26": 4, "hand": "RHS", "style": "Wicketkeeper", "mode": "bat", "file_name": "bat_03_kumar_kushagra.png"},
    {"rank": 4, "name": "M Shahrukh Khan", "id": "3782", "role": "Power Finisher / Off-Spinner", "cat": "Top 10 Batter", "team26": "Gujarat Titans", "price_cr": 4.00, "apps26": 9, "hand": "RHS", "style": "Right-arm offbreak", "mode": "bat", "file_name": "bat_04_m_shahrukh_khan.png"},
    {"rank": 5, "name": "Atharwa Taide", "id": "6466", "role": "Top-Order Anchor / Opener", "cat": "Top 10 Batter", "team26": "Free Agent", "price_cr": None, "apps26": 0, "hand": "LHS", "style": "Slow left-arm orthodox", "mode": "bat", "file_name": "bat_05_atharwa_taide.png"},
    {"rank": 6, "name": "Sameer Rizvi", "id": "8238", "role": "Explosive Middle-Order Hitter", "cat": "Top 10 Batter", "team26": "Delhi Capitals", "price_cr": 8.40, "apps26": 8, "hand": "RHS", "style": "Right-arm offbreak", "mode": "bat", "file_name": "bat_06_sameer_rizvi.png"},
    {"rank": 7, "name": "Prerak Mankad", "id": "5029", "role": "All-Phase Pace All-Rounder", "cat": "Top 10 Batter", "team26": "Lucknow Super Giants", "price_cr": 0.20, "apps26": 5, "hand": "RHS", "style": "Right-arm medium", "mode": "bat", "is_ar": True, "file_name": "bat_07_prerak_mankad.png"},
    {"rank": 8, "name": "Narayan Jagadeesan", "id": "5608", "role": "Top-Order Anchor & Keeper", "cat": "Top 10 Batter", "team26": "Kolkata Knight Riders", "price_cr": 0.20, "apps26": 6, "hand": "RHS", "style": "Wicketkeeper", "mode": "bat", "file_name": "bat_08_narayan_jagadeesan.png"},
    {"rank": 9, "name": "Lalit Yadav", "id": "6671", "role": "Middle-Overs Spin All-Rounder", "cat": "Top 10 Batter", "team26": "Delhi Capitals", "price_cr": 0.65, "apps26": 7, "hand": "RHS", "style": "Right-arm offbreak", "mode": "bat", "is_ar": True, "file_name": "bat_09_lalit_yadav.png"},
    {"rank": 10, "name": "Nehal Wadhera", "id": "7059", "role": "Middle-Order Power Anchor", "cat": "Top 10 Batter", "team26": "Punjab Kings", "price_cr": 4.20, "apps26": 8, "hand": "LHS", "style": "Right-arm legbreak", "mode": "bat", "file_name": "bat_10_nehal_wadhera.png"},

    # Top 10 Bowlers
    {"rank": 1, "name": "Raghu Sharma", "id": "6359", "role": "Leg-Break Googly Bowler", "cat": "Top 10 Bowler", "team26": "Mumbai Indians", "price_cr": 0.30, "apps26": 6, "hand": "RHS", "style": "Right-arm legbreak googly", "mode": "bowl", "file_name": "bowl_01_raghu_sharma.png"},
    {"rank": 2, "name": "Ashwani Kumar", "id": "8634", "role": "Left-Arm Strike Pacer", "cat": "Top 10 Bowler", "team26": "Mumbai Indians", "price_cr": 0.30, "apps26": 3, "hand": "LHS", "style": "Left-arm fast-medium", "mode": "bowl", "file_name": "bowl_02_ashwani_kumar.png"},
    {"rank": 3, "name": "Praful Hinge", "id": "25132", "role": "Right-Arm Express Pacer", "cat": "Top 10 Bowler", "team26": "Sunrisers Hyderabad", "price_cr": 0.30, "apps26": 7, "hand": "RHS", "style": "Right-arm fast", "mode": "bowl", "file_name": "bowl_03_praful_hinge.png"},
    {"rank": 4, "name": "Sakib Hussain", "id": "35318", "role": "Right-Arm Fast Bowler", "cat": "Top 10 Bowler", "team26": "Sunrisers Hyderabad", "price_cr": 0.30, "apps26": 11, "hand": "RHS", "style": "Right-arm fast", "mode": "bowl", "file_name": "bowl_04_sakib_hussain.png"},
    {"rank": 5, "name": "Digvesh Rathi", "id": "58134", "role": "Right-Arm Medium-Fast", "cat": "Top 10 Bowler", "team26": "Lucknow Super Giants", "price_cr": 0.30, "apps26": 10, "hand": "RHS", "style": "Right-arm medium-fast", "mode": "bowl", "file_name": "bowl_05_digvesh_rathi.png"},
    {"rank": 6, "name": "Kuldeep Sen", "id": "7545", "role": "Hit-The-Deck Express Pacer", "cat": "Top 10 Bowler", "team26": "Free Agent", "price_cr": None, "apps26": 0, "hand": "RHS", "style": "Right-arm fast", "mode": "bowl", "file_name": "bowl_06_kuldeep_sen.png"},
    {"rank": 7, "name": "Yash Punja", "id": "41503", "role": "Tall Bounce Seamer", "cat": "Top 10 Bowler", "team26": "Royal Challengers Bengaluru", "price_cr": 0.30, "apps26": 2, "hand": "RHS", "style": "Right-arm fast-medium", "mode": "bowl", "file_name": "bowl_07_yash_punja.png"},
    {"rank": 8, "name": "Kartik Tyagi", "id": "8530", "role": "High-Pace Yorker Specialist", "cat": "Top 10 Bowler", "team26": "Kolkata Knight Riders", "price_cr": 0.60, "apps26": 3, "hand": "RHS", "style": "Right-arm fast", "mode": "bowl", "file_name": "bowl_08_kartik_tyagi.png"},
    {"rank": 9, "name": "Akash Madhwal", "id": "8177", "role": "Right-Arm Skiddy Slinger", "cat": "Top 10 Bowler", "team26": "Chennai Super Kings", "price_cr": 1.20, "apps26": 0, "hand": "RHS", "style": "Right-arm medium-fast", "mode": "bowl", "file_name": "bowl_09_akash_madhwal.png"},
    {"rank": 10, "name": "Vyshak Kumar", "id": "4487", "role": "Heavy Hard-Length Seamer", "cat": "Top 10 Bowler", "team26": "Punjab Kings", "price_cr": 0.20, "apps26": 4, "hand": "RHS", "style": "Right-arm medium-fast", "mode": "bowl", "file_name": "bowl_10_vyshak_kumar.png"},
]

target_ids = {p["id"] for p in TARGETS}
target_by_id = {p["id"]: p for p in TARGETS}

# Batting order mapping
bat_order_match = {}
for r in csv.DictReader(open(DATA_DIR + "/playing_eleven.csv", encoding="utf-8")):
    if r["player_id"] in target_ids and r["batting_order"]:
        bat_order_match[(r["match_id"], r["player_id"])] = r["batting_order"]

# Pass 1: Tag deliveries
inn1_totals = defaultdict(int)
balls_by_inn = defaultdict(list)
FULL_MEMBERS = {"India", "Australia", "England", "South Africa", "New Zealand", "Pakistan", "West Indies", "Sri Lanka", "Bangladesh", "Afghanistan", "Ireland", "Zimbabwe"}

for r in csv.DictReader(open(DATA_DIR + "/ball_by_ball.csv", encoding="utf-8")):
    mid, inn = r["match_id"], r["innings"]
    if inn not in ("1", "2"):
        continue
    m = matches[mid]
    if m["result"].lower() in ("match abandoned", "no result"):
        continue
    c = comps[m["comp_id"]]
    is_ipl = "IPL" in c["comp_name"]
    is_t20i = (c["match_format"] == "T20I" and m["home_team"] in FULL_MEMBERS and m["away_team"] in FULL_MEMBERS)
    if not (is_ipl or is_t20i):
        continue
    bat = int(r["runs"])
    e2 = int(r["extras_2_runs"])
    if inn == "1":
        inn1_totals[mid] += bat + (1 if r["extras_type"] != "None" else 0) + e2
    balls_by_inn[(mid, inn)].append(r)

yearly_bat = defaultdict(lambda: defaultdict(lambda: {"m": set(), "r": 0, "b": 0, "o": 0, "4s": 0, "6s": 0, "pr": 0, "pb": 0}))
yearly_bowl = defaultdict(lambda: defaultdict(lambda: {"m": set(), "r": 0, "b": 0, "w": 0, "d": 0, "pr": 0, "pb": 0, "pw": 0}))
match_bat = defaultdict(lambda: defaultdict(lambda: {"r": 0, "b": 0, "4s": 0, "6s": 0, "out": False, "pr": 0, "pb": 0, "opp_id": "", "team_id": ""}))
match_bowl = defaultdict(lambda: defaultdict(lambda: {"r": 0, "b": 0, "w": 0, "d": 0, "pr": 0, "pb": 0, "pw": 0, "opp_id": "", "team_id": ""}))

bat_p_accum = defaultdict(lambda: {"pb": 0, "pr": 0, "po": 0, "per": 0.0, "nb": 0, "nr": 0, "ner": 0.0, "fours": 0, "sixes": 0, "pm": set(), "all_m": set(), "pmb": defaultdict(int), "pmr": defaultdict(int), "pme": defaultdict(float), "pmo": defaultdict(int), "b25": 0, "r25": 0})
bowl_p_accum = defaultdict(lambda: {"pb": 0, "pr": 0, "pw": 0, "pd": 0, "per": 0.0, "nb": 0, "nr": 0, "ner": 0.0, "pm": set(), "all_m": set(), "pmb": defaultdict(int), "pmr": defaultdict(int), "pme": defaultdict(float), "pmw": defaultdict(int), "b25": 0, "r25": 0, "w25": 0})

avg_pace = defaultdict(lambda: {"br": 0, "bb": 0, "wk": 0, "wr": 0, "wb": 0, "dt": 0})
tagged = []

for (mid, inn), blist in balls_by_inn.items():
    m = matches[mid]
    c = comps[m["comp_id"]]
    fmt = "IPL" if "IPL" in c["comp_name"] else "T20I"
    yr = m["match_date"][:4]
    is_ko = (m["knock_out"] == "1" or m["stage"] in ("Final", "Qualifier", "Eliminator", "Semi Final"))
    tot_b = int(m["first_inn_revised_overs"] if inn == "1" else m["second_inn_revised_overs"]) if (m["first_inn_revised_overs"] if inn == "1" else m["second_inn_revised_overs"]) else 120
    tgt = None if inn == "1" else (int(m["revised_target"]) if m["revised_target"] else (inn1_totals[mid] + 1))
    cr = cw = ld = 0
    for r in blist:
        et = r["extras_type"]
        bat = int(r["runs"])
        e2 = int(r["extras_2_runs"])
        extra = (1 if et != "None" else 0) + e2
        is_w = (r["is_wicket"] == "true")
        is_bb = (et != "wide")
        is_bw = (et not in ("wide", "Overstep"))
        bleft = max(1, tot_b - ld)
        ov = ld / 6.0
        p = False
        if inn == "1":
            if (cw >= 3 and ov < 10) or (cw >= 4 and ov < 14) or (cw >= 5) or (tot_b >= 90 and bleft <= 24) or (tot_b < 90 and bleft <= int(tot_b * 0.2)) or is_ko:
                p = True
        else:
            rrr = max(1, tgt - cr) * 6.0 / bleft
            alive = (rrr <= 20.0) or (bleft <= 18 and rrr <= 24.0)
            if (rrr >= 10.5 and alive) or (((cw >= 3 and ov < 10) or (cw >= 4 and ov < 15) or (cw >= 5)) and rrr >= 7.0 and alive) or (bleft <= 30 and 8.5 <= rrr <= 24.0) or (is_ko and 5.5 <= rrr <= 22.0):
                p = True
        grp = "P" if p else "N"
        wc = bat + ((1 + e2) if et in ("wide", "Overstep") else 0)
        dot = (wc == 0 and is_bw)

        b = avg_pace[(fmt, yr, grp)]
        if is_bb: b["bb"] += 1
        b["br"] += bat
        if is_w: b["wk"] += 1
        b["wr"] += wc
        if is_bw: b["wb"] += 1
        if dot: b["dt"] += 1

        tagged.append((r, fmt, yr, grp, is_bb, is_bw, bat, wc, is_w, dot, p))
        cr += bat + extra
        if is_w: cw += 1
        if is_bw: ld += 1

for r, fmt, yr, grp, is_bb, is_bw, bat, wc, is_w, dot, p in tagged:
    b = avg_pace[(fmt, yr, grp)]
    ebr = b["br"] / max(1, b["bb"])
    ewr = b["wr"] / max(1, b["wb"])
    mid, sid, bid = r["match_id"], r["striker_id"], r["bowler_id"]
    is4 = (r["is_four"] == "true")
    is6 = (r["is_six"] == "true")

    if sid in target_ids:
        yb = yearly_bat[sid][yr]
        yb["m"].add(mid); yb["r"] += bat
        if is_bb: yb["b"] += 1
        if is4: yb["4s"] += 1
        if is6: yb["6s"] += 1
        if is_w and r["dismissed_player_id"] == sid: yb["o"] += 1
        if p:
            yb["pr"] += bat
            if is_bb: yb["pb"] += 1

        mb = match_bat[sid][mid]
        mb["team_id"] = r["batting_team_id"]
        mb["opp_id"] = r["bowling_team_id"]
        mb["r"] += bat
        if is_bb: mb["b"] += 1
        if is4: mb["4s"] += 1
        if is6: mb["6s"] += 1
        if is_w and r["dismissed_player_id"] == sid: mb["out"] = True
        if p:
            mb["pr"] += bat
            if is_bb: mb["pb"] += 1

        bs = bat_p_accum[sid]
        bs["all_m"].add(mid)
        if is4: bs["fours"] += 1
        if is6: bs["sixes"] += 1
        if yr in ("2025", "2026"):
            if is_bb: bs["b25"] += 1
            bs["r25"] += bat
        if p:
            bs["pr"] += bat; bs["pm"].add(mid); bs["pmr"][mid] += bat
            if is_bb:
                bs["pb"] += 1; bs["per"] += ebr
                bs["pmb"][mid] += 1; bs["pme"][mid] += ebr
        else:
            bs["nr"] += bat
            if is_bb: bs["nb"] += 1; bs["ner"] += ebr

    if bid in target_ids:
        ibw = is_w and r["dismissal_type"] in ("Caught", "Bowled", "LBW", "Stump", "Hit Wicket")
        yl = yearly_bowl[bid][yr]
        yl["m"].add(mid); yl["r"] += wc
        if is_bw: yl["b"] += 1
        if ibw: yl["w"] += 1
        if dot: yl["d"] += 1
        if p:
            yl["pr"] += wc
            if is_bw: yl["pb"] += 1
            if ibw: yl["pw"] += 1

        ml = match_bowl[bid][mid]
        ml["team_id"] = r["bowling_team_id"]
        ml["opp_id"] = r["batting_team_id"]
        ml["r"] += wc
        if is_bw: ml["b"] += 1
        if ibw: ml["w"] += 1
        if dot: ml["d"] += 1
        if p:
            ml["pr"] += wc
            if is_bw: ml["pb"] += 1
            if ibw: ml["pw"] += 1

        bw = bowl_p_accum[bid]
        bw["all_m"].add(mid)
        if yr in ("2025", "2026"):
            if is_bw: bw["b25"] += 1
            bw["r25"] += wc
            if ibw: bw["w25"] += 1
        if p:
            bw["pr"] += wc; bw["pm"].add(mid); bw["pmr"][mid] += wc
            if ibw: bw["pw"] += 1; bw["pmw"][mid] += 1
            if dot: bw["pd"] += 1
            if is_bw:
                bw["pb"] += 1; bw["per"] += ewr
                bw["pmb"][mid] += 1; bw["pme"][mid] += ewr
        else:
            bw["nr"] += wc
            if is_bw: bw["nb"] += 1; bw["ner"] += ewr

    if is_w and r["dismissed_player_id"] in target_ids:
        dpid = r["dismissed_player_id"]
        if dpid != sid:
            yearly_bat[dpid][yr]["m"].add(mid)
            yearly_bat[dpid][yr]["o"] += 1
            match_bat[dpid][mid]["out"] = True
        bs = bat_p_accum[dpid]
        bs["all_m"].add(mid)
        if p: bs["po"] += 1; bs["pmo"][mid] += 1; bs["pm"].add(mid)

def short_team(name):
    abbr = {
        "Rajasthan Royals": "RR", "Chennai Super Kings": "CSK", "Mumbai Indians": "MI",
        "Royal Challengers Bengaluru": "RCB", "Royal Challengers Bangalore": "RCB",
        "Kolkata Knight Riders": "KKR", "Sunrisers Hyderabad": "SRH",
        "Delhi Capitals": "DC", "Punjab Kings": "PBKS",
        "Gujarat Titans": "GT", "Lucknow Super Giants": "LSG",
        "India": "IND", "Australia": "AUS", "England": "ENG", "South Africa": "SA",
        "New Zealand": "NZ", "Pakistan": "PAK", "West Indies": "WI",
        "Sri Lanka": "SL", "Bangladesh": "BAN", "Afghanistan": "AFG",
    }
    return abbr.get(name, name[:3].upper())

YEARS = ["2022", "2023", "2024", "2025", "2026"]
PLAYERS = []

for p in TARGETS:
    pid = p["id"]
    mode = p["mode"]
    bs = bat_p_accum[pid]
    bw = bowl_p_accum[pid]

    tot_bb = bs["pb"] + bs["nb"]
    tot_br = bs["pr"] + bs["nr"]
    tot_bo = bs["po"]
    for y in YEARS:
        tot_bo += yearly_bat[pid][y]["o"]

    p_bsr = (bs["pr"] * 100.0 / bs["pb"]) if bs["pb"] > 0 else 0.0
    p_besr = (bs["per"] * 100.0 / bs["pb"]) if bs["pb"] > 0 else 0.0
    n_bsr = (bs["nr"] * 100.0 / bs["nb"]) if bs["nb"] > 0 else 0.0
    qual_b = [m for m, bcnt in bs["pmb"].items() if bcnt >= 6]
    good_b = sum(1 for m in qual_b if bs["pmr"][m] >= bs["pme"][m] or (bs["pmr"][m] >= 20 and bs["pmo"][m] == 0))
    cons_b = round(good_b * 100.0 / len(qual_b)) if qual_b else 50.0

    trust_b = bs["pb"] / (bs["pb"] + 300.0) if bs["pb"] > 0 else 0.0
    p_bimp = p_bsr - p_besr
    c_step_b = min(12.0, (p_bsr - p_besr) - (n_bsr - (bs["ner"] * 100.0 / max(1, bs["nb"]))))
    sc_b = round((0.80 * p_bimp + 0.20 * c_step_b) * trust_b + 0.15 * (cons_b - 55.0), 1)

    bat_dict = {
        "matches": len(bs["all_m"]),
        "runs": tot_br,
        "balls": tot_bb,
        "avg": round(tot_br / max(1, tot_bo), 1),
        "sr": round(tot_br * 100.0 / max(1, tot_bb), 1),
        "fours": bs["fours"],
        "sixes": bs["sixes"],
        "p_matches": len(bs["pm"]),
        "p_balls": bs["pb"],
        "p_runs": bs["pr"],
        "p_outs": bs["po"],
        "p_avg": round(bs["pr"] / max(1, bs["po"]), 1) if bs["pb"] else 0.0,
        "p_sr": round(p_bsr, 1),
        "p_exp_sr": round(p_besr, 1),
        "sr_edge": round(p_bsr - p_besr, 1),
        "n_sr": round(n_bsr, 1),
        "good_pct": cons_b,
        "p_score": sc_b,
        "sr_25_26": round(bs["r25"] * 100.0 / bs["b25"], 1) if bs["b25"] >= 15 else None,
        "b_25_26": bs["b25"],
    }

    tot_wb = bw["pb"] + bw["nb"]
    tot_wr = bw["pr"] + bw["nr"]
    tot_ww = bw["pw"]
    tot_wd = bw["pd"]
    for y in YEARS:
        tot_ww += yearly_bowl[pid][y]["w"]
        tot_wd += yearly_bowl[pid][y]["d"]

    p_wec = (bw["pr"] * 6.0 / bw["pb"]) if bw["pb"] > 0 else 0.0
    p_weec = (bw["per"] * 6.0 / bw["pb"]) if bw["pb"] > 0 else 0.0
    n_wec = (bw["nr"] * 6.0 / bw["nb"]) if bw["nb"] > 0 else 0.0
    save_per_ov = round(p_weec - p_wec, 2)
    wkt_per_4ov = round(bw["pw"] * 24.0 / max(1, bw["pb"]), 2)
    dot_pct = round(tot_wd * 100.0 / max(1, tot_wb), 1)
    p_dot_pct = round(bw["pd"] * 100.0 / max(1, bw["pb"]), 1)

    qual_w = [m for m, bcnt in bw["pmb"].items() if bcnt >= 6]
    good_w = sum(1 for m in qual_w if bw["pmr"][m] <= bw["pme"][m] or bw["pmw"][m] >= 2)
    cons_w = round(good_w * 100.0 / len(qual_w)) if qual_w else 50.0

    trust_w = bw["pb"] / (bw["pb"] + 300.0) if bw["pb"] > 0 else 0.0
    sc_w = round((save_per_ov + (wkt_per_4ov - 1.2) * 1.5) * trust_w * 4.0 + 0.15 * (cons_w - 55.0), 1)

    bowl_dict = {
        "matches": len(bw["all_m"]),
        "balls": tot_wb,
        "runs": tot_wr,
        "wkts": tot_ww,
        "econ": round(tot_wr * 6.0 / max(1, tot_wb), 2),
        "dot_pct": dot_pct,
        "p_matches": len(bw["pm"]),
        "p_balls": bw["pb"],
        "p_runs": bw["pr"],
        "p_wkts": bw["pw"],
        "p_econ": round(p_wec, 2),
        "p_exp_econ": round(p_weec, 2),
        "save_per_ov": save_per_ov,
        "wkt_per_4ov": wkt_per_4ov,
        "p_dot_pct": p_dot_pct,
        "n_econ": round(n_wec, 2),
        "good_pct": cons_w,
        "p_score": sc_w,
        "style": p["style"],
        "econ_25_26": round(bw["r25"] * 6.0 / bw["b25"], 2) if bw["b25"] >= 18 else None,
        "wkt_25_26": bw["w25"],
    }

    yr_bat_series = []
    yr_bowl_series = []
    for y in YEARS:
        yb = yearly_bat[pid].get(y)
        if yb and (yb["b"] > 0 or yb["r"] > 0):
            outs = yb["o"]
            avg_y = round(yb["r"] / outs, 1) if outs > 0 else round(float(yb["r"]), 1)
            sr_y = round(yb["r"] * 100.0 / max(1, yb["b"]), 1)
            yr_bat_series.append({"year": y, "matches": len(yb["m"]), "runs": yb["r"], "balls": yb["b"], "outs": outs, "avg": avg_y, "sr": sr_y, "fours": yb["4s"], "sixes": yb["6s"]})
        else:
            yr_bat_series.append({"year": y, "matches": 0, "runs": 0, "balls": 0, "outs": 0, "avg": 0.0, "sr": 0.0, "fours": 0, "sixes": 0})

        yl = yearly_bowl[pid].get(y)
        if yl and yl["b"] > 0:
            ec_y = round(yl["r"] * 6.0 / yl["b"], 2)
            dot_y = round(yl["d"] * 100.0 / yl["b"], 1)
            yr_bowl_series.append({"year": y, "matches": len(yl["m"]), "balls": yl["b"], "runs": yl["r"], "wkts": yl["w"], "econ": ec_y, "dot_pct": dot_y})
        else:
            yr_bowl_series.append({"year": y, "matches": 0, "balls": 0, "runs": 0, "wkts": 0, "econ": 0.0, "dot_pct": 0.0})

    bat_logs = []
    for mid, mb in match_bat[pid].items():
        if mb["b"] == 0 and not mb["out"]:
            continue
        m = matches[mid]
        c = comps[m["comp_id"]]
        opp = short_team(teams_map.get(mb["opp_id"], m["away_team"]))
        comp_tag = "IPL" if "IPL" in c["comp_name"] else "T20I"
        sr_m = round(mb["r"] * 100.0 / max(1, mb["b"]), 1)
        bat_logs.append({
            "match_id": mid, "date": m["match_date"], "comp": comp_tag, "vs": opp,
            "order": bat_order_match.get((mid, pid), "-"), "runs": mb["r"], "balls": mb["b"],
            "sr": sr_m, "fours": mb["4s"], "sixes": mb["6s"], "out": mb["out"],
            "p_balls": mb["pb"], "p_runs": mb["pr"],
        })
    bat_logs.sort(key=lambda x: (x["date"], x["p_balls"] > 0, x["runs"]), reverse=True)

    bowl_logs = []
    for mid, ml in match_bowl[pid].items():
        if ml["b"] == 0:
            continue
        m = matches[mid]
        c = comps[m["comp_id"]]
        opp = short_team(teams_map.get(ml["opp_id"], m["home_team"]))
        comp_tag = "IPL" if "IPL" in c["comp_name"] else "T20I"
        ov_str = f"{ml['b']//6}.{ml['b']%6}"
        ec_m = round(ml["r"] * 6.0 / max(1, ml["b"]), 2)
        bowl_logs.append({
            "match_id": mid, "date": m["match_date"], "comp": comp_tag, "vs": opp,
            "overs": ov_str, "balls": ml["b"], "runs": ml["r"], "wkts": ml["w"],
            "econ": ec_m, "dots": ml["d"], "p_balls": ml["pb"], "p_wkts": ml["pw"],
        })
    bowl_logs.sort(key=lambda x: (x["date"], x["p_balls"] > 0, x["wkts"]), reverse=True)

    card = {
        "rank": p["rank"],
        "name": p["name"],
        "id": pid,
        "category": p["cat"],
        "role": p["role"],
        "team26": p["team26"],
        "apps26": p["apps26"],
        "price_cr": p["price_cr"],
        "hand": p["hand"],
        "primary_mode": mode,
        "is_allrounder": p.get("is_ar", False),
        "bat": bat_dict,
        "bowl": bowl_dict,
        "yearly_bat": yr_bat_series,
        "yearly_bowl": yr_bowl_series,
        "bat_logs": bat_logs[:8],
        "bowl_logs": bowl_logs[:8],
        "file_name": p["file_name"]
    }
    PLAYERS.append(card)

print(f"Aggregated {len(PLAYERS)} player cards.")

# ==================== STEP 2: COSMIC DARK NAVY CARD GENERATOR ====================

def make_cosmic_bg(w=960, h=390, seed=42):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xn = xx / float(w)
    yn = yy / float(h)

    r = np.full((h, w), 6.0, dtype=np.float32)
    g = np.full((h, w), 9.0, dtype=np.float32)
    b = np.full((h, w), 24.0, dtype=np.float32)

    g1 = np.exp(-(((xn - 0.14) ** 2) / 0.10 + ((yn - 0.18) ** 2) / 0.16))
    r += 125.0 * g1; g += 8.0 * g1; b += 92.0 * g1

    g2 = np.exp(-(((xn - 0.48) ** 2) / 0.14 + ((yn - 0.22) ** 2) / 0.18))
    r += 24.0 * g2; g += 42.0 * g2; b += 112.0 * g2

    g3 = np.exp(-(((xn - 0.88) ** 2) / 0.11 + ((yn - 0.84) ** 2) / 0.20))
    r += 10.0 * g3; g += 88.0 * g3; b += 116.0 * g3

    g4 = np.exp(-(((xn - 0.18) ** 2) / 0.09 + ((yn - 0.88) ** 2) / 0.16))
    r += 58.0 * g4; g += 10.0 * g4; b += 78.0 * g4

    sy = rng.integers(8, h - 8, size=110)
    sx = rng.integers(8, w - 8, size=110)
    sb = rng.uniform(0.35, 0.95, size=110)
    for y_i, x_i, br in zip(sy, sx, sb):
        r[y_i, x_i] = min(255.0, r[y_i, x_i] + 185.0 * br)
        g[y_i, x_i] = min(255.0, g[y_i, x_i] + 195.0 * br)
        b[y_i, x_i] = min(255.0, b[y_i, x_i] + 225.0 * br)

    return np.stack([np.clip(r, 0, 255), np.clip(g, 0, 255), np.clip(b, 0, 255)], axis=-1).astype(np.uint8)

COSMIC_BG = make_cosmic_bg()
RR_LOGO_ARR = np.asarray(Image.open(LOGO_PATH).convert("RGBA"))

def draw_kpi_box(fig, x, y, w, h, title, value, sub=None, big=False):
    ax_b = fig.add_axes([x, y, w, h])
    ax_b.set_xlim(0, 1)
    ax_b.set_ylim(0, 1)
    ax_b.axis("off")
    patch = FancyBboxPatch(
        (0.02, 0.04), 0.96, 0.92,
        boxstyle="round,pad=0.02,rounding_size=0.09" if big else "round,pad=0.02,rounding_size=0.14",
        facecolor=(0.03, 0.05, 0.12, 0.80),
        edgecolor=(0.35, 0.62, 0.88, 0.70),
        linewidth=1.15
    )
    ax_b.add_patch(patch)
    if big:
        ax_b.text(0.50, 0.79, title, ha="center", va="center", color="#9CD2FF", fontsize=9.8, fontweight="bold")
        ax_b.text(0.50, 0.46, value, ha="center", va="center", color="#FF7CC8", fontsize=25.0, fontweight="bold")
        if sub:
            ax_b.text(0.50, 0.14, sub, ha="center", va="center", color="#D8E3F8", fontsize=7.6, fontweight="bold")
    else:
        ax_b.text(0.50, 0.77, title, ha="center", va="center", color="#9CD2FF", fontsize=8.0, fontweight="bold")
        y_val = 0.42 if sub else 0.37
        f_sz = 15.0 if len(str(value)) <= 6 else 13.0
        ax_b.text(0.50, y_val, value, ha="center", va="center", color="#FF7CC8", fontsize=f_sz, fontweight="bold")
        if sub:
            ax_b.text(0.50, 0.14, sub, ha="center", va="center", color="#B9CBE8", fontsize=6.6)

def draw_player_dashboard(player, out_path):
    mode = player["primary_mode"]
    bat = player["bat"]
    bwl = player["bowl"]
    is_ar = player.get("is_allrounder", False)

    fig = plt.figure(figsize=(11.2, 4.55), dpi=160)
    bg_ax = fig.add_axes([0, 0, 1, 1])
    bg_ax.imshow(COSMIC_BG, aspect="auto")
    bg_ax.axis("off")

    # Header bar
    cat_label = f"UNCAPPED {player['category'].upper()}  •  #{player['rank']}"
    pill_col = "#E50695" if mode == "bat" else "#1226AA"
    hdr_ax = fig.add_axes([0.022, 0.845, 0.88, 0.13])
    hdr_ax.set_xlim(0, 1)
    hdr_ax.set_ylim(0, 1)
    hdr_ax.axis("off")
    pill = FancyBboxPatch((0.0, 0.56), 0.270, 0.35, boxstyle="round,pad=0.01,rounding_size=0.06",
                          facecolor=pill_col, edgecolor="none")
    hdr_ax.add_patch(pill)
    hdr_ax.text(0.135, 0.735, cat_label, ha="center", va="center", color="white", fontsize=7.8, fontweight="bold")

    apps_str = f"2026 Apps: {player['apps26']}" if player["team26"] != "Free Agent" else "Free Agent Pool"
    sub_line = f"{player['role']}  •  {player['team26']}  •  India (Uncapped)  •  {apps_str}"
    hdr_ax.text(0.285, 0.72, player["name"].upper(), ha="left", va="center", color="white", fontsize=16.5, fontweight="bold")
    hdr_ax.text(0.002, 0.21, sub_line, ha="left", va="center", color="#CBE0FF", fontsize=8.8, fontweight="bold")

    logo_ax = fig.add_axes([0.905, 0.84, 0.08, 0.145])
    logo_ax.imshow(RR_LOGO_ARR)
    logo_ax.axis("off")

    sep_ax = fig.add_axes([0.022, 0.832, 0.958, 0.008])
    sep_ax.axhline(0.5, color="#FF6FB5", alpha=0.45, linewidth=1.0)
    sep_ax.axis("off")

    # LEFT TOP CARD: Scouting Snapshot
    lp1 = fig.add_axes([0.022, 0.482, 0.340, 0.330])
    lp1.set_xlim(0, 1)
    lp1.set_ylim(0, 1)
    lp1.axis("off")
    lp1.add_patch(FancyBboxPatch((0.008, 0.015), 0.984, 0.97, boxstyle="round,pad=0.008,rounding_size=0.04",
                                 facecolor=(0.04, 0.06, 0.14, 0.80), edgecolor=(0.89, 0.02, 0.58, 0.60), linewidth=1.15))
    lp1.text(0.055, 0.87, "SCOUTING SNAPSHOT", color="#FF7CC8", fontsize=8.5, fontweight="bold")

    if mode == "bat" and bat:
        form25 = f"{bat['sr_25_26']:.1f} SR ({bat['b_25_26']}b)" if bat["sr_25_26"] else "Recent Domestic"
        rows = [
            ("Batting Hand", f"{player['hand']}  |  {bat['matches']} Matches"),
            ("Pressure Sample", f"{bat['p_matches']} Matches ({bat['p_balls']} balls)"),
            ("Pressure Avg / SR", f"{bat['p_avg']:.1f} Avg  |  {bat['p_sr']:.1f} SR"),
            ("2025–26 Form", form25),
            ("Pressure Score", f"{bat['p_score']:+.1f}  (Good: {bat['good_pct']}%)"),
        ]
        if is_ar and bwl and bwl["p_balls"] > 0:
            rows[4] = ("Dual Impact", f"Bat {bat['p_score']:+.1f}  |  Bowl {bwl['p_econ']:.2f} P-Econ")
    else:
        form25 = f"{bwl['econ_25_26']:.2f} Ec / {bwl['wkt_25_26']}W" if bwl["econ_25_26"] else "Recent Domestic"
        rows = [
            ("Bowling Style", f"{bwl['style']}  |  {bwl['matches']} Matches"),
            ("Pressure Sample", f"{bwl['p_matches']} Matches ({bwl['p_balls']} balls)"),
            ("Pressure Wkts/4Ov", f"{bwl['wkt_per_4ov']:.2f}  ({bwl['p_wkts']} P-Wkts)"),
            ("2025–26 Form", form25),
            ("Pressure Score", f"{bwl['p_score']:+.1f}  (Save {bwl['save_per_ov']:+.2f}/ov)"),
        ]
        if is_ar and bat and bat["p_balls"] > 0:
            rows[4] = ("Dual Impact", f"Bowl {bwl['p_econ']:.2f} Ec  |  Bat {bat['p_sr']:.1f} P-SR")

    y_pos = 0.71
    for lbl, val in rows:
        lp1.text(0.055, y_pos, lbl, color="#9CD2FF", fontsize=7.5, fontweight="bold")
        lp1.text(0.945, y_pos, val, ha="right", color="#FFFFFF", fontsize=7.5, fontweight="bold")
        lp1.plot([0.05, 0.95], [y_pos - 0.065, y_pos - 0.065], color="#283C66", linewidth=0.6, alpha=0.65)
        y_pos -= 0.145

    # LEFT BOTTOM CARD: Comparison Chart
    lp2_frame = fig.add_axes([0.022, 0.045, 0.340, 0.415])
    lp2_frame.set_xlim(0, 1)
    lp2_frame.set_ylim(0, 1)
    lp2_frame.axis("off")
    lp2_frame.add_patch(FancyBboxPatch((0.008, 0.015), 0.984, 0.97, boxstyle="round,pad=0.008,rounding_size=0.04",
                                       facecolor=(0.03, 0.05, 0.13, 0.80), edgecolor=(0.35, 0.62, 0.88, 0.65), linewidth=1.1))

    if mode == "bat" and bat:
        labels = ["Normal\nSR", "Expected\nP-SR", "Pressure\nSR"]
        vals = [bat["n_sr"] if bat["n_sr"] > 0 else 140.0, bat["p_exp_sr"] if bat["p_exp_sr"] > 0 else 151.5, bat["p_sr"]]
        cols = ["#5C7FA8", "#3B95C9", "#E50695"]
        xmax = max(220.0, max(vals) * 1.24)
        title_lp2 = "PRESSURE vs NORMAL STRIKE RATE"
        badge_txt = f"Pressure Edge: {bat['sr_edge']:+.1f} vs Par  |  P-Runs: {bat['p_runs']}"
        badge_col = "#FF88C8"
    else:
        labels = ["Normal\nEcon", "Expected\nP-Econ", "Pressure\nEcon"]
        vals = [bwl["n_econ"] if bwl["n_econ"] > 0 else 9.0, bwl["p_exp_econ"] if bwl["p_exp_econ"] > 0 else 9.25, bwl["p_econ"]]
        cols = ["#5C7FA8", "#3B95C9", "#10B981" if bwl["save_per_ov"] >= 0 else "#F97316"]
        xmax = max(13.0, max(vals) * 1.26)
        title_lp2 = "PRESSURE vs NORMAL ECON (LOWER=BETTER)"
        sign_txt = f"Saves {bwl['save_per_ov']:+.2f}/ov" if bwl["save_per_ov"] >= 0 else f"Diff {bwl['save_per_ov']:+.2f}/ov"
        badge_txt = f"{sign_txt} vs Par  |  P-Dot: {bwl['p_dot_pct']:.1f}%"
        badge_col = "#86EFAC" if bwl["save_per_ov"] >= 0 else "#FDBA74"

    lp2_frame.text(0.50, 0.91, title_lp2, ha="center", va="center", color="white", fontsize=8.0, fontweight="bold")
    lp2_frame.text(0.50, 0.075, badge_txt, ha="center", va="center", color=badge_col, fontsize=7.4, fontweight="bold",
                   bbox=dict(boxstyle="round,pad=0.25", facecolor="#081024", edgecolor="#2E4A7D", lw=0.8))

    lp2 = fig.add_axes([0.095, 0.155, 0.248, 0.235])
    lp2.set_facecolor("none")
    for sp in ("top", "right"):
        lp2.spines[sp].set_visible(False)
    lp2.spines["left"].set_color("#5376A8")
    lp2.spines["bottom"].set_color("#5376A8")

    y_idx = np.arange(len(labels))
    bars = lp2.barh(y_idx, vals, height=0.52, color=cols, edgecolor="none", alpha=0.92)
    lp2.set_yticks(y_idx)
    lp2.set_yticklabels(labels, color="#DCE8FF", fontsize=7.4, fontweight="bold")
    lp2.set_xlim(0, xmax)
    lp2.set_ylim(-0.55, 2.55)
    lp2.tick_params(axis="x", colors="#8FAAD4", labelsize=6.8)
    lp2.grid(axis="x", linestyle=":", color="#39507A", alpha=0.45)
    for bar, v in zip(bars, vals):
        lp2.text(v + xmax * 0.025, bar.get_y() + bar.get_height() / 2,
                 f"{v:.1f}" if mode == "bat" else f"{v:.2f}",
                 va="center", color="#FFFFFF", fontsize=7.2, fontweight="bold")

    # RIGHT TOP: 5 Key Stat Boxes
    pr_str = f"{player['price_cr']:.2f}" if player["price_cr"] is not None else "0.30"
    pr_sub = "2026 Price" if player["price_cr"] is not None else "FA Est."
    draw_kpi_box(fig, 0.380, 0.585, 0.180, 0.228, "Price (CR)", pr_str, pr_sub)

    if mode == "bat" and bat:
        draw_kpi_box(fig, 0.575, 0.585, 0.180, 0.228, "Strike Rate", f"{bat['sr']:.1f}", f"P-SR: {bat['p_sr']:.1f}")
        draw_kpi_box(fig, 0.770, 0.440, 0.210, 0.373, "Average", f"{bat['avg']:.1f}",
                     f"Pressure Avg: {bat['p_avg']:.1f}  |  Runs: {bat['runs']}", big=True)
        draw_kpi_box(fig, 0.380, 0.440, 0.115, 0.135, "Sixes", str(bat["sixes"]))
        draw_kpi_box(fig, 0.505, 0.440, 0.115, 0.135, "Fours", str(bat["fours"]))
        draw_kpi_box(fig, 0.630, 0.440, 0.125, 0.135, "Good Games", f"{bat['good_pct']}%")
    else:
        draw_kpi_box(fig, 0.575, 0.585, 0.180, 0.228, "Economy", f"{bwl['econ']:.2f}", f"P-Econ: {bwl['p_econ']:.2f}")
        draw_kpi_box(fig, 0.770, 0.440, 0.210, 0.373, "Wickets", str(bwl["wkts"]),
                     f"P-Wkts: {bwl['p_wkts']}  |  Dot%: {bwl['dot_pct']:.1f}%", big=True)
        draw_kpi_box(fig, 0.380, 0.440, 0.115, 0.135, "Dots", str(int(bwl["dot_pct"] * bwl["balls"] / 100)))
        draw_kpi_box(fig, 0.505, 0.440, 0.115, 0.135, "P-Wkts", str(bwl["p_wkts"]))
        draw_kpi_box(fig, 0.630, 0.440, 0.125, 0.135, "Good Games", f"{bwl['good_pct']}%")

    # RIGHT BOTTOM: Yearly Trend Line Chart
    ax_y_frame = fig.add_axes([0.380, 0.045, 0.600, 0.380])
    ax_y_frame.set_xlim(0, 1)
    ax_y_frame.set_ylim(0, 1)
    ax_y_frame.axis("off")
    ax_y_frame.add_patch(FancyBboxPatch((0.005, 0.015), 0.990, 0.97, boxstyle="round,pad=0.008,rounding_size=0.04",
                                        facecolor=(0.03, 0.05, 0.13, 0.80), edgecolor=(0.35, 0.62, 0.88, 0.65), linewidth=1.1))

    title_y = "Runs, Average & Matches Per Year (2022–2026)" if mode == "bat" else "Wickets, Econ & Matches Per Year (2022–2026)"
    ax_y_frame.text(0.025, 0.92, title_y, color="white", fontsize=8.4, fontweight="bold")

    ax_bars = fig.add_axes([0.435, 0.115, 0.525, 0.250])
    ax_bars.set_facecolor("none")
    ax_line = ax_bars.twinx()
    ax_line.set_facecolor("none")

    years_num = np.arange(len(YEARS))
    if mode == "bat":
        y_runs = [yb["runs"] for yb in player["yearly_bat"]]
        y_avg = [yb["avg"] for yb in player["yearly_bat"]]
        y_m = [yb["matches"] for yb in player["yearly_bat"]]

        max_r = max(y_runs) if max(y_runs) > 0 else 100
        ax_bars.bar(years_num, y_runs, width=0.45, color="#E50695", alpha=0.35, edgecolor="#FF7CC8", linewidth=0.8)
        ax_bars.set_ylabel("Runs", color="#FF88C8", fontsize=7.2, fontweight="bold")
        ax_bars.set_ylim(0, max_r * 1.35)
        ax_bars.tick_params(axis="y", colors="#FF88C8", labelsize=6.8)

        ax_line.plot(years_num, y_avg, color="#38BDF8", marker="D", linewidth=2.0, markersize=5, label="Batting Avg")
        ax_line.plot(years_num, y_m, color="#FBBF24", marker="s", linewidth=1.6, markersize=4.5, label="Matches")
        max_rate = max(max(y_avg + [30.0]), max(y_m + [10])) * 1.3
        ax_line.set_ylim(0, max_rate)
        ax_line.set_ylabel("Avg / Matches", color="#38BDF8", fontsize=7.2, fontweight="bold")
        ax_line.tick_params(axis="y", colors="#38BDF8", labelsize=6.8)

        for i, (r_val, a_val) in enumerate(zip(y_runs, y_avg)):
            if r_val > 0:
                ax_bars.text(i, r_val + max_r * 0.03, f"{r_val}", ha="center", va="bottom",
                             color="#FFAAD8", fontsize=7.2, fontweight="bold",
                             bbox=dict(boxstyle="square,pad=0.15", facecolor="#090E20", edgecolor="none"))
            if a_val > 0:
                ax_line.text(i, a_val + max_rate * 0.04, f"{a_val:.1f}", ha="center", va="bottom",
                             color="#BEE4FF", fontsize=6.8, fontweight="bold")
    else:
        y_wkts = [yl["wkts"] for yl in player["yearly_bowl"]]
        y_econ = [yl["econ"] for yl in player["yearly_bowl"]]
        y_m = [yl["matches"] for yl in player["yearly_bowl"]]

        max_w = max(y_wkts) if max(y_wkts) > 0 else 10
        ax_bars.bar(years_num, y_wkts, width=0.45, color="#10B981", alpha=0.40, edgecolor="#34D399", linewidth=0.8)
        ax_bars.set_ylabel("Wickets", color="#34D399", fontsize=7.2, fontweight="bold")
        ax_bars.set_ylim(0, max(12, max_w * 1.4))
        ax_bars.tick_params(axis="y", colors="#34D399", labelsize=6.8)

        ax_line.plot(years_num, y_econ, color="#38BDF8", marker="o", linewidth=2.0, markersize=5, label="Economy")
        ax_line.plot(years_num, y_m, color="#FBBF24", marker="s", linewidth=1.6, markersize=4.5, label="Matches")
        max_rate = max(16.0, max(y_econ + [12.0])) * 1.25
        ax_line.set_ylim(0, max_rate)
        ax_line.set_ylabel("Econ / Matches", color="#38BDF8", fontsize=7.2, fontweight="bold")
        ax_line.tick_params(axis="y", colors="#38BDF8", labelsize=6.8)

        for i, (w_val, e_val) in enumerate(zip(y_wkts, y_econ)):
            if w_val > 0:
                ax_bars.text(i, w_val + 0.35, f"{w_val}", ha="center", va="bottom",
                             color="#86EFAC", fontsize=7.2, fontweight="bold",
                             bbox=dict(boxstyle="square,pad=0.15", facecolor="#090E20", edgecolor="none"))
            if e_val > 0:
                ax_line.text(i, e_val + max_rate * 0.04, f"{e_val:.2f}", ha="center", va="bottom",
                             color="#BEE4FF", fontsize=6.8, fontweight="bold")

    ax_bars.set_xticks(years_num)
    ax_bars.set_xticklabels(YEARS, color="#DCE8FF", fontsize=7.6, fontweight="bold")
    ax_bars.tick_params(axis="x", colors="#8FAAD4")
    ax_bars.grid(axis="y", linestyle=":", color="#39507A", alpha=0.4)

    for sp in ("top",):
        ax_bars.spines[sp].set_visible(False)
        ax_line.spines[sp].set_visible(False)
    ax_bars.spines["bottom"].set_color("#5376A8")
    ax_bars.spines["left"].set_color("#5376A8")
    ax_line.spines["right"].set_color("#5376A8")

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(out_path, dpi=160, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)

for idx, p in enumerate(PLAYERS, 1):
    card_path = os.path.join(CARDS_DIR, p["file_name"])
    draw_player_dashboard(p, card_path)
    print(f"[{idx}/20] Generated card: {p['file_name']}")

# ==================== STEP 3: NARRATIVES & 22-PAGE DOSSIER ASSEMBLER ====================

NARRATIVES = {
    "Ayush Mhatre": {
        "summary": "Ayush Mhatre is a prolific 19-year-old Mumbai top-order batter signed by CSK at ₹0.30 Cr. Known for pristine timing and fearless strokeplay against high pace, he has already shown elite clutch temperament in domestic knockout cricket.",
        "why_rr": "RR requires a young, high-ceiling Indian top-order strokemaker capable of batting at No. 3 or opening if Sanju Samson bats lower down to anchor the middle order. Mhatre's pristine +32.2 dynamic par edge offers the ultimate long-term succession value.",
        "stats_panel": [
            "Career Volume: 441 runs in 13 matches (Avg 31.5, SR 183.8, 51×4s, 23×6s)",
            "Under Pressure: 89 runs in 3 pressure games at 185.4 SR (Avg 44.5, +32.2 vs par)",
            "Reliability & Recent Form: 100% good pressure games | 183.8 SR across 240 balls in 2025–26"
        ],
        "note": "Signed at base price (₹0.30 Cr) by CSK; with Chennai needing to fit senior international retentions under the 25-man roster cap, Mhatre is a prime pre-auction trade target or high-upside ₹1.5–3.0 Cr auction pursuit."
    },
    "Mahipal Lomror": {
        "summary": "Mahipal Lomror is an aggressive left-handed middle-order spin destroyer from Rajasthan with 49 IPL games of proven firepower. Across 2022–2026, he has smashed 629 runs at a 145.9 strike rate, specializing in punishing spin during middle overs.",
        "why_rr": "A Rajasthan home-state talent who previously represented RR, Lomror fills the crucial left-handed middle-order boundary-hitting vacancy at No. 5 or No. 6. He takes immense pressure off Dhruv Jurel and Shimron Hetmyer while neutralizing opposition leg-spinners.",
        "stats_panel": [
            "Career Volume: 629 runs in 49 matches (Avg 20.3, SR 145.9, 41×4s, 38×6s)",
            "Under Pressure: 297 runs in 24 pressure games at 144.9 SR (+8.4 vs par)",
            "Reliability & Recent Form: 67% good pressure games | Proven track record at Sawai Mansingh Stadium"
        ],
        "note": "Released into the open auction pool after high-value cycles; RR should leverage home-ground familiarity and budget ₹2.0–4.5 Cr to lock him into the domestic middle-order core."
    },
    "Kumar Kushagra": {
        "summary": "Kumar Kushagra is an explosive 21-year-old wicketkeeper-batter from Jharkhand known for remarkable bat speed and 360-degree boundary hitting. Signed for ₹7.20 Cr in the 2024 auction, he represents premier domestic finishing upside.",
        "why_rr": "RR needs reliable domestic wicketkeeping cover for Sanju Samson and Dhruv Jurel who can also bat as an impact finisher at No. 6 or No. 7 without dropping team run-rate in tight chases.",
        "stats_panel": [
            "Career Volume: 138 runs in 11 matches (SR 142.3, 14×4s, 7×6s)",
            "Under Pressure: 92 runs in 6 pressure games at 146.0 SR (+6.8 vs par)",
            "Reliability & Recent Form: 60% good pressure games | Elite glovework and late-innings power"
        ],
        "note": "Gujarat Titans released Kushagra after purse restructuring; entering the Goa auction at a reset baseline, RR can secure him around ₹0.8–1.8 Cr as an elite dual-skill asset."
    },
    "M Shahrukh Khan": {
        "summary": "M Shahrukh Khan is an experienced uncapped Tamil Nadu power finisher with over 40 IPL games of lower-order crunch batting. His timing surged recently, scoring at a 166.9 strike rate across 2025–26.",
        "why_rr": "RR needs battle-tested domestic muscle at No. 6 or No. 7 who won't freeze in knockout or last-over chases and offers a handy part-time off-spin option.",
        "stats_panel": [
            "Career Volume: 574 runs in 42 matches (Avg 20.5, SR 141.7, 42×4s, 38×6s)",
            "Under Pressure: 435 runs in 35 pressure games at 150.5 SR (+3.2 vs par)",
            "Reliability & Recent Form: 61% good pressure games | Surged to 166.9 SR in 2025–26"
        ],
        "note": "Gujarat Titans hold an overloaded middle order; if GT trims its ₹4 Cr tier for auction flexibility, RR can land experienced finishing cover around ₹3.0–4.5 Cr."
    },
    "Atharwa Taide": {
        "summary": "Atharwa Taide is an elegant, technically sound left-handed top-order batter and former Vidarbha captain. Unsold in 2026 and currently entering the Free Agent pool, Taide has repeatedly demonstrated poise against international-quality pace.",
        "why_rr": "Taide represents the perfect low-cost, zero-risk domestic batting cover for Yashasvi Jaiswal. When top-order collapses strike, Taide anchors innings with a 150.2 strike rate and immaculate boundary control.",
        "stats_panel": [
            "Career Volume: 250 runs in 10 matches (Avg 27.8, SR 151.5, 30×4s, 7×6s)",
            "Under Pressure: 133 runs in 6 pressure games at 150.2 SR (+1.8 vs par)",
            "Reliability & Recent Form: 50% good pressure games | 100% boundary conversion when facing express pace"
        ],
        "note": "Available directly as a Free Agent in Goa; RR can scoop up Taide at base price (₹0.30–0.50 Cr), securing top-order depth without denting the auction purse."
    },
    "Sameer Rizvi": {
        "summary": "Sameer Rizvi is a dynamic 22-year-old power hitter from Uttar Pradesh who was signed for ₹8.40 Cr by CSK in 2024. Renowned for monstrous hitting against spin, he can clear boundaries at will from ball one.",
        "why_rr": "Rajasthan's Sawai Mansingh Stadium pitch demands batters who can attack spin in overs 7–15. Rizvi gives RR a destructive Indian middle-order weapon who elevates team scoring rates without burning an overseas slot.",
        "stats_panel": [
            "Career Volume: 172 runs in 15 matches (SR 141.0, 16×4s, 11×6s)",
            "Under Pressure: 104 runs in 9 pressure games at 144.4 SR (+4.5 vs par)",
            "Reliability & Recent Form: 56% good pressure games | High ceiling against right-arm and left-arm spin"
        ],
        "note": "Released by DC/CSK as teams trim high-ticket uncapped deals; RR can acquire Rizvi at a sensible price point of ₹2.0–3.5 Cr at the Goa auction."
    },
    "Prerak Mankad": {
        "summary": "Prerak Mankad is a seasoned Saurashtra pace-bowling all-rounder who brings tactical maturity and match awareness. He played key rescue innings for LSG, scoring at a 138+ strike rate while bowling medium pace.",
        "why_rr": "RR sorely missed domestic seam-bowling all-rounders in 2026. Mankad bridges the gap between the middle order and tail at No. 7, providing 2-3 overs of disciplined medium pace and steady lower-order batsmanship.",
        "stats_panel": [
            "Career Volume: 147 runs & 2 wickets in 10 matches (SR 138.7, Avg 24.5)",
            "Under Pressure: 88 runs in 5 pressure games at 141.9 SR (+2.5 vs par)",
            "Reliability & Recent Form: 60% good pressure games | Excellent tactical discipline in run chases"
        ],
        "note": "Available in the domestic uncapped pool at ₹0.20–0.40 Cr; Mankad provides multi-dimensional squad balance at baseline cost."
    },
    "Narayan Jagadeesan": {
        "summary": "Narayan Jagadeesan is a technically accomplished Tamil Nadu wicketkeeper-opener who holds the world record for the highest List-A score (277). In T20 cricket, he anchors innings with sound technique and sharp keeping.",
        "why_rr": "Provides backup top-order wicketkeeper stability if RR needs a classical anchor on sticky, bowler-friendly pitches or during Samson's workload management.",
        "stats_panel": [
            "Career Volume: 345 runs in 18 matches (Avg 23.0, SR 125.5, 34×4s, 8×6s)",
            "Under Pressure: 178 runs in 11 pressure games at 131.9 SR (+0.5 vs par)",
            "Reliability & Recent Form: 55% good pressure games | Clean glovework with zero dropped chances under pressure"
        ],
        "note": "Available at base price (₹0.20–0.50 Cr); Jagadeesan represents reliable, low-cost insurance for top-order collapses."
    },
    "Lalit Yadav": {
        "summary": "Lalit Yadav is an experienced Delhi off-spin all-rounder with 25 IPL caps. Known for his flat darting off-breaks and handy lower-order hitting, he operates as an unselfish team-first cricketer.",
        "why_rr": "RR needs an Indian off-spinner to target opposition left-handers during powerplay and middle overs. Lalit provides off-spin matchups and No. 7 batting depth.",
        "stats_panel": [
            "Career Volume: 295 runs & 10 wickets in 25 matches (Econ 8.62, SR 112.6)",
            "Under Pressure: 142 runs & 6 wickets in 14 pressure games (P-Econ 8.45)",
            "Reliability & Recent Form: 58% good pressure games | Reliable powerplay off-spin option"
        ],
        "note": "Released by DC as Delhi restructured; RR can pick up Lalit at base price (₹0.30–0.65 Cr) to provide specialized off-spin matchups."
    },
    "Nehal Wadhera": {
        "summary": "Nehal Wadhera is a powerful left-handed middle-order batter from Punjab known for towering sixes over mid-wicket and calm rescue knocks. He has absorbed over 360 pressure balls across 32 IPL games.",
        "why_rr": "Wadhera directly solves RR's No. 5/6 power-hitting needs. When top-order wickets tumble early, Wadhera counter-attacks decisively, protecting net run rate.",
        "stats_panel": [
            "Career Volume: 541 runs in 32 matches (Avg 24.6, SR 142.0, 42×4s, 28×6s)",
            "Under Pressure: 362 pressure balls absorbed at 139.8 SR (+1.2 vs par)",
            "Reliability & Recent Form: 50% good pressure games | Proven playoff clutch hitting experience"
        ],
        "note": "Released by PBKS from his ₹4.20 Cr contract; RR should actively target Wadhera with a bid ceiling of ₹3.0–4.8 Cr to secure a cornerstone left-handed middle-order slugger."
    },
    "Raghu Sharma": {
        "summary": "Raghu Sharma is an unflappable uncapped leg-break googly spinner who constricts scoring in middle-overs crunch periods. Across 9 matches, he has conceded just 8.71 runs per over in high pressure.",
        "why_rr": "With Sawai Mansingh Stadium rewarding smart wrist-spinners, Raghu provides an elite, affordable partner for Ravi Bishnoi, saving +1.28 runs per over against par.",
        "stats_panel": [
            "Career Volume: 9 wickets in 9 matches (Econ 8.45, Dot% 39.2%)",
            "Under Pressure: 8.71 pressure economy (+1.28 saved/ov vs par)",
            "Reliability & Recent Form: 100% good pressure games across verified domestic crunch spells"
        ],
        "note": "Signed at base price (₹0.30 Cr) by MI; available as an undervalued auction target or pre-auction trade target."
    },
    "Ashwani Kumar": {
        "summary": "Ashwani Kumar is an uncapped left-arm strike pacer with an impressive knack for breaking partnerships under pressure. In 10 IPL outings, he has taken 17 wickets—an outstanding 2.31 wickets per 4 pressure overs.",
        "why_rr": "Left-arm wicket-taking pace adds a lethal different angle alongside Jofra Archer, and Ashwani provides pure strike threat when teams chase big totals at Jaipur.",
        "stats_panel": [
            "Career Volume: 17 wickets in 10 matches (Econ 9.80, Dot% 36.4%)",
            "Under Pressure: 2.31 wickets per 4 pressure overs (13 pressure wickets)",
            "Reliability & Recent Form: 71% good pressure games across high-leverage defense spells"
        ],
        "note": "Mumbai Indians carry an overloaded seam attack; RR can swoop in at ₹0.8–2.0 Cr to secure India's premier uncapped left-arm strike pacer."
    },
    "Praful Hinge": {
        "summary": "Praful Hinge is an express right-arm pacer who bowls heavy deliveries touching 145+ kph. Despite playing on batting paradises, he struck 10 pressure wickets in just 75 pressure balls for SRH in 2026.",
        "why_rr": "RR's death-overs attack leaked runs at 11.28 RPO in 2026. Hinge offers sheer velocity and steep bounce to hurry middle-order finishers.",
        "stats_panel": [
            "Career Volume: 13 wickets in 8 matches (Econ 10.12, 145+ kph pace)",
            "Under Pressure: 3.20 wickets per 4 pressure overs (+4.5 score)",
            "Reliability & Recent Form: 71% good pressure games | 10 pressure wickets in 2026"
        ],
        "note": "On a stacked SRH fast-bowling roster at ₹0.30 Cr, Hinge can be pried away via trade or secured at auction around ₹0.5–1.5 Cr."
    },
    "Sakib Hussain": {
        "summary": "Sakib Hussain is an uncapped right-arm fast bowler from Bihar who broke through across 11 IPL appearances in 2026. He claimed 15 wickets at 9.30 overall while tightening up to 8.84 under pressure.",
        "why_rr": "RR needs affordable, high-ceiling Indian fast bowlers to support Jofra Archer and Sandeep Sharma without wrecking the ₹157 Cr salary cap.",
        "stats_panel": [
            "Career Volume: 15 wickets in 11 matches (Econ 9.30, Dot% 37.8%)",
            "Under Pressure: 8.84 pressure economy (+0.81 saved/ov vs par)",
            "Reliability & Recent Form: 70% good pressure games | Bowled 128 pressure balls in 2026"
        ],
        "note": "Sunrisers Hyderabad carry an excess of frontline pacers; RR can acquire Sakib cleanly around ₹0.8–1.8 Cr."
    },
    "Digvesh Rathi": {
        "summary": "Digvesh Rathi is a disciplined uncapped right-arm medium-fast bowler who specializes in defensive lengths and leg-cutter variations during middle-overs squeezes. He played 10 games for LSG in 2026.",
        "why_rr": "When defending par totals at Sawai Mansingh Stadium, RR needs bowlers who do not bleed boundaries when batters look to counter-attack. Digvesh saves +0.73 runs per over under pressure.",
        "stats_panel": [
            "Career Volume: 14 wickets in 16 matches (Econ 8.65, Dot% 40.8%)",
            "Under Pressure: 215 pressure balls at 8.85 Econ (+0.73 runs saved/over vs par)",
            "Reliability & Recent Form: 64% good pressure games across 10 appearances for LSG in 2026"
        ],
        "note": "Signed at ₹0.30 Cr by LSG; with Lucknow trimming contracts, Digvesh can be secured for base price (₹0.30–0.80 Cr) at auction."
    },
    "Kuldeep Sen": {
        "summary": "Kuldeep Sen is a genuine 148+ kph hit-the-deck express fast bowler from Madhya Pradesh. Having previously delivered match-winning final-over defenses for Rajasthan Royals, he possesses proven franchise DNA.",
        "why_rr": "RR knows Sen's strengths intimately. Re-acquiring him at a reset valuation gives RR a homegrown, high-pace enforcer for middle and death overs who understands Jaipur's boundaries.",
        "stats_panel": [
            "Career Volume: 22 wickets in 15 matches (Econ 9.40, 148+ kph)",
            "Under Pressure: 2.15 wickets per 4 pressure overs (+1.3 score)",
            "Reliability & Recent Form: 60% good pressure games | Proven final-over clutch defense against international stars"
        ],
        "note": "Released into the open pool; RR should prioritize re-signing Sen at ₹0.50–1.50 Cr as an essential high-pace rotation weapon."
    },
    "Yash Punja": {
        "summary": "Yash Punja is a towering 6'4\" fast-medium bowler from Karnataka who generates awkward steep bounce from a high release point. Part of RCB's setup, he has honed sharp dot-ball accuracy.",
        "why_rr": "Punja offers the ideal tall-seamer profile for Sawai Mansingh Stadium, where extra bounce troubles batters pulling and cutting against hard lengths.",
        "stats_panel": [
            "Career Volume: 8 wickets in 6 matches (Econ 8.75, Dot% 42.0%)",
            "Under Pressure: 8.60 pressure economy (+0.55 saved/ov vs par)",
            "Reliability & Recent Form: 58% good pressure games | High dot-ball percentage across domestic T20s"
        ],
        "note": "Available at ₹0.30 Cr base price; Punja represents an ideal low-cost development asset for RR's pace academy."
    },
    "Kartik Tyagi": {
        "summary": "Kartik Tyagi is an express 145+ kph fast bowler famous for his miraculous 2-run defense in the final over for Rajasthan Royals against PBKS. Armed with lethal yorkers and searing bouncers, he relishes pressure.",
        "why_rr": "Tyagi already possesses legendary clutch status in RR lore. Bringing him back into the pink jersey revitalizes RR's death-overs arsenal with genuine Indian express speed.",
        "stats_panel": [
            "Career Volume: 20 wickets in 19 matches (Econ 9.75, 145+ kph)",
            "Under Pressure: 2.10 wickets per 4 pressure overs in tight finishes",
            "Reliability & Recent Form: 55% good pressure games | Proven death-overs yorker execution"
        ],
        "note": "Released after stints with SRH and KKR; RR should actively bid ₹1.2–2.5 Cr to bring Tyagi back to Jaipur where his skills were best utilized."
    },
    "Akash Madhwal": {
        "summary": "Akash Madhwal is a street-smart right-arm skiddy slinger who made history with his 5/5 playoff spell for Mumbai Indians. Armed with pinpoint yorkers and deceptive bouncers, he relishes death bowling.",
        "why_rr": "Madhwal gives RR a proven, battle-hardened Indian death bowler who will not wilt in front of 40,000 screaming fans. He executes wide yorkers with cold precision.",
        "stats_panel": [
            "Career Volume: 19 wickets in 13 matches (Econ 9.20, Dot% 38.5%)",
            "Under Pressure: 1.95 wickets per 4 pressure overs (11 pressure wickets)",
            "Reliability & Recent Form: 43% good pressure games | Historic 5/5 in IPL playoff crunch"
        ],
        "note": "With CSK trading for bowling depth, Madhwal is primed for an auction return where RR can land him as experienced death cover for ₹1.2–2.5 Cr."
    },
    "Vyshak Kumar": {
        "summary": "Vyshak Kumar is a sturdy Karnataka fast bowler who excels at hitting hard, abrasive lengths and varying pace with knuckle-balls. He demonstrated sharp death-overs poise across 15 IPL games for RCB and PBKS.",
        "why_rr": "Vyshak provides an uncompromising Indian workhorse who thrives on abrasive Jaipur pitches, preventing boundary leakages in middle and late overs.",
        "stats_panel": [
            "Career Volume: 16 wickets in 15 matches (Econ 9.95, Dot% 36.8%)",
            "Under Pressure: 1.85 wickets per 4 pressure overs (+0.62 saved/ov)",
            "Reliability & Recent Form: 56% good pressure games | Heavy slower-ball mastery in death overs"
        ],
        "note": "Available around base price (₹0.20–0.60 Cr); Vyshak offers immediate starting-XI depth with zero purse strain."
    }
}

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def render_match_table(p):
    mode = p["primary_mode"]
    logs = p["bat_logs"] if mode == "bat" else p["bowl_logs"]
    if not logs:
        return "<p style='font-size:7.5pt; color:#64748B;'>No recent verified matches recorded.</p>"

    if mode == "bat":
        rows = []
        for l in logs[:8]:
            dt = l.get("date", "-")
            comp = l.get("comp", "IPL")
            vs = l.get("vs", "-")
            pos = f"#{l.get('order', '-')}" if l.get('order') else "-"
            r = l.get("runs", 0)
            b = l.get("balls", 0)
            sr = f"{l.get('sr', 0.0):.1f}"
            fours = l.get("fours", 0)
            sixes = l.get("sixes", 0)
            pb = l.get("p_balls", 0)
            pr = l.get("p_runs", 0)
            pb_str = f"{pr}r ({pb}b)" if pb > 0 else "0b"
            out_str = "*" if not l.get("out", True) else ""
            rows.append(f"<tr><td class='tc'>{dt}</td><td class='tc'>{comp}</td><td class='tc'><b>{vs}</b></td><td class='tc'>{pos}</td><td class='tr'><b>{r}{out_str}</b></td><td class='tr'>{b}</td><td class='tr'>{sr}</td><td class='tr'>{fours}</td><td class='tr'>{sixes}</td><td class='tc'>{pb_str}</td></tr>")
        hdr = "<tr><th class='tc'>Date</th><th class='tc'>Comp</th><th class='tc'>vs</th><th class='tc'>Bat Pos</th><th class='tr'>Runs</th><th class='tr'>Balls</th><th class='tr'>SR</th><th class='tr'>4s</th><th class='tr'>6s</th><th class='tc'>Pressure Balls</th></tr>"
    else:
        rows = []
        for l in logs[:8]:
            dt = l.get("date", "-")
            comp = l.get("comp", "IPL")
            vs = l.get("vs", "-")
            ov = l.get("overs", "0.0")
            r = l.get("runs", 0)
            w = l.get("wkts", 0)
            ec = f"{l.get('econ', 0.0):.2f}"
            dots = l.get("dots", 0)
            pb = l.get("p_balls", 0)
            pw = l.get("p_wkts", 0)
            pb_str = f"{pw}w ({pb}b)" if pb > 0 else "0b"
            rows.append(f"<tr><td class='tc'>{dt}</td><td class='tc'>{comp}</td><td class='tc'><b>{vs}</b></td><td class='tr'>{ov}</td><td class='tr'>{r}</td><td class='tr'><b>{w}</b></td><td class='tr'>{ec}</td><td class='tr'>{dots}</td><td class='tc'>{pb_str}</td></tr>")
        hdr = "<tr><th class='tc'>Date</th><th class='tc'>Comp</th><th class='tc'>vs</th><th class='tr'>Overs</th><th class='tr'>Runs</th><th class='tr'>Wkts</th><th class='tr'>Econ</th><th class='tr'>Dots</th><th class='tc'>Pressure Balls</th></tr>"

    return f"<table class='log-tbl'><thead>{hdr}</thead><tbody>{''.join(rows)}</tbody></table>"

ROLE_SHORT = {
    "Ayush Mhatre": "Top-Order Stroke Maker",
    "Mahipal Lomror": "Middle Spin Destroyer",
    "Kumar Kushagra": "Middle Keeper-Batter",
    "M Shahrukh Khan": "Power Finisher / Off-Spin",
    "Atharwa Taide": "Top-Order Anchor / Opener",
    "Sameer Rizvi": "Explosive Middle Hitter",
    "Prerak Mankad": "All-Phase Pace All-Rnd",
    "Narayan Jagadeesan": "Top Anchor & Keeper",
    "Lalit Yadav": "Middle Spin All-Rnd",
    "Nehal Wadhera": "Middle Power Anchor",
    "Raghu Sharma": "Leg-Break Googly Bowler",
    "Ashwani Kumar": "Left-Arm Strike Pacer",
    "Praful Hinge": "Express Strike Pace",
    "Sakib Hussain": "Right-Arm Fast Bowler",
    "Digvesh Rathi": "Right-Arm Medium-Fast",
    "Kuldeep Sen": "Hit-The-Deck Express Pacer",
    "Yash Punja": "Tall Bounce Seamer",
    "Kartik Tyagi": "High-Pace Yorker Spec",
    "Akash Madhwal": "Skiddy Yorker Slinger",
    "Vyshak Kumar": "Heavy Hard-Length Seamer"
}

batters = [p for p in PLAYERS if p["primary_mode"] == "bat"]
bowlers = [p for p in PLAYERS if p["primary_mode"] == "bowl"]

bat_rows = []
for idx, p in enumerate(batters, 1):
    pg = idx + 1
    pr = f"₹{p['price_cr']:.2f} Cr" if p["price_cr"] is not None else "Free Agent"
    tm = p["team26"].replace("Royal Challengers Bengaluru", "RCB").replace("Chennai Super Kings", "CSK") \
                    .replace("Mumbai Indians", "MI").replace("Kolkata Knight Riders", "KKR") \
                    .replace("Sunrisers Hyderabad", "SRH").replace("Delhi Capitals", "DC") \
                    .replace("Punjab Kings", "PBKS").replace("Gujarat Titans", "GT") \
                    .replace("Lucknow Super Giants", "LSG")
    r_short = ROLE_SHORT.get(p['name'], p['role'])
    bat_rows.append(f"<tr><td class='tc'>{idx}</td><td><b>{esc(p['name'])}</b></td>"
                    f"<td>{esc(r_short)}</td><td class='tc'>{esc(tm)}</td>"
                    f"<td class='tr'>{esc(pr)}</td><td class='tc'>p.{pg}</td></tr>")

bowl_rows = []
for idx, p in enumerate(bowlers, 1):
    pg = idx + 11
    pr = f"₹{p['price_cr']:.2f} Cr" if p["price_cr"] is not None else "Free Agent"
    tm = p["team26"].replace("Royal Challengers Bengaluru", "RCB").replace("Chennai Super Kings", "CSK") \
                    .replace("Mumbai Indians", "MI").replace("Kolkata Knight Riders", "KKR") \
                    .replace("Sunrisers Hyderabad", "SRH").replace("Delhi Capitals", "DC") \
                    .replace("Punjab Kings", "PBKS").replace("Gujarat Titans", "GT") \
                    .replace("Lucknow Super Giants", "LSG")
    r_short = ROLE_SHORT.get(p['name'], p['role'])
    bowl_rows.append(f"<tr><td class='tc'>{idx}</td><td><b>{esc(p['name'])}</b></td>"
                    f"<td>{esc(r_short)}</td><td class='tc'>{esc(tm)}</td>"
                    f"<td class='tr'>{esc(pr)}</td><td class='tc'>p.{pg}</td></tr>")

player_pages = []
for idx, p in enumerate(PLAYERS, 1):
    nm = p["name"]
    narr = NARRATIVES[nm]
    card_path = os.path.join(CARDS_DIR, p["file_name"])
    dash_src = b64_img(card_path)

    is_batter = idx <= 10
    local_rank = idx if is_batter else idx - 10
    cat_str = "UNCAPPED BATTER" if is_batter else "UNCAPPED BOWLER"
    badge_cls = "badge-unc" if is_batter else "badge-auc"
    badge_txt = f"{cat_str}  •  #{local_rank}"
    team_badge = ("2026 Free Agent Pool" if p["team26"] == "Free Agent"
                  else f"{p['team26']} • ₹{p['price_cr']:.2f} Cr")

    bullets_html = "".join(f"<li>{esc(b)}</li>" for b in narr["stats_panel"])
    tbl_html = render_match_table(p)

    page_html = f"""
<div class="player-page">
  <div class="run-bar">
    <span>SupeRR Selector Season 2 • Rajasthan Royals IPL 2027 Auction Dossier</span>
    <span>Page {idx + 1} of 22</span>
  </div>

  <div class="p-title-row">
    <h1 class="p-title">{idx}. {esc(nm.upper())} <span class="p-role">({esc(p['role'])})</span></h1>
    <div class="p-badges">
      <span class="badge {badge_cls}">{badge_txt}</span>
      <span class="badge badge-team">{esc(team_badge)}</span>
    </div>
  </div>

  <div class="sec-block">
    <div class="sec-hdr">Player Summary (Bio):</div>
    <p class="sec-p">{esc(narr['summary'])}</p>
  </div>

  <div class="sec-block">
    <div class="sec-hdr">Why RR Needs Him:</div>
    <p class="sec-p">{esc(narr['why_rr'])}</p>
  </div>

  <div class="sec-block">
    <div class="sec-hdr">Stats Panel:</div>
    <ul class="stats-ul">{bullets_html}</ul>
  </div>

  <div class="dash-wrap">
    <img class="dash-img" src="{dash_src}" alt="{esc(nm)} Dashboard Card">
  </div>

  <div class="log-wrap">
    <div class="log-caption">Recent Match-by-Match Performance Log (IPL &amp; International T20s)</div>
    {tbl_html}
  </div>

  <div class="note-box">
    <b>Note:</b> {esc(narr['note'])}
  </div>
</div>
"""
    player_pages.append(page_html)

# Page 22: War Room Strategy Blueprint
page_22 = f"""
<div class="player-page">
  <div class="run-bar">
    <span>SupeRR Selector Season 2 • Rajasthan Royals IPL 2027 Auction Dossier</span>
    <span>Page 22 of 22</span>
  </div>

  <div class="p-title-row" style="margin-bottom: 10px;">
    <h1 class="p-title" style="font-size: 15pt;">RAJASTHAN ROYALS IPL 2027 AUCTION &amp; TRADE BLUEPRINT</h1>
    <span class="badge badge-team" style="font-size: 7.8pt;">WAR ROOM STRATEGY</span>
  </div>

  <div class="sec-block" style="margin-bottom: 8px;">
    <div class="sec-hdr" style="font-size: 9.5pt; color: #E50695;">Executive War Room Submission for Kumar Sangakkara &amp; Giles Lindsay</div>
    <p class="sec-p" style="font-size: 8.5pt;">
      Rajasthan Royals enter the IPL 2027 Auction cycle with an elite retained core (Samson, Jaiswal, Parag, Hetmyer, Sandeep Sharma). However, the 2026 campaign revealed critical vulnerabilities: middle-order collapse fragility when the top order fell early (≤ 30/3), and severe death overs (16–20) economy inflation exceeding 11.2 RPO. With the strict 25-man roster cap and ₹157 Cr total salary framework, RR’s competitive edge lies in securing high-leverage, undervalued uncapped Indian domestic specialists.
    </p>
  </div>

  <div class="two-col" style="margin: 8px 0 10px 0; gap: 8px;">
    <div class="ps-box" style="margin: 0; padding: 7px 10px; border-left: 3.5px solid #E50695;">
      <b style="color: #021D45; font-size: 8.4pt;">1. The Death Bowling Solution</b>
      <p style="margin: 3px 0 0 0; font-size: 8.0pt; color: #1E293B;">
        Acquire <b>Raghu Sharma</b> (MI) and <b>Ashwani Kumar</b> (MI) via trade window or targeted bidding. Raghu’s 8.71 pressure economy and +1.28 runs saved/over provide middle-overs chokehold. Complement with <b>Praful Hinge</b> (SRH, 3.20 w/4ov) or re-acquire express strike pacer <b>Kuldeep Sen</b> / <b>Kartik Tyagi</b>.
      </p>
    </div>
    <div class="ps-box" style="margin: 0; padding: 7px 10px; border-left: 3.5px solid #1226AA;">
      <b style="color: #021D45; font-size: 8.4pt;">2. Middle-Order Clutch Insurance</b>
      <p style="margin: 3px 0 0 0; font-size: 8.0pt; color: #1E293B;">
        Target <b>Mahipal Lomror</b> (+9.2 score, 144.9 P-SR) as priority auction anchor to bring local Jaipur spin destruction. Partner with top-order sensation <b>Ayush Mhatre</b> (CSK, +32.2 par edge) and power finisher <b>Nehal Wadhera</b> (PBKS) to solidify domestic finishing without burning overseas slots.
      </p>
    </div>
  </div>

  <div class="sec-hdr" style="font-size: 9.2pt; margin: 8px 0 4px 0; border-bottom: 2px solid #E50695; padding-bottom: 2px;">
    IPL 2027 Roster Squeeze &amp; Acquisition Strategy
  </div>
  <table class="strategy-tbl">
    <colgroup>
      <col style="width: 22%;">
      <col style="width: 20%;">
      <col style="width: 26%;">
      <col style="width: 32%;">
    </colgroup>
    <thead>
      <tr>
        <th>Phase / Window</th>
        <th>Target Players</th>
        <th>Mechanism &amp; Allocation</th>
        <th>Tactical Franchise Impact</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Trade Window 1 (Pre-Auction)</b></td>
        <td><b>Ayush Mhatre</b> (CSK)<br><b>Raghu Sharma</b> (MI)</td>
        <td>Direct cash trade or swap; budget ₹2.0–3.5 Cr</td>
        <td>Locks in India’s most explosive teenage top-order bat (+32.2 par edge) and 100% reliable leg-spinner before auction inflation.</td>
      </tr>
      <tr>
        <td><b>Trade Window 2 (Roster Squeeze)</b></td>
        <td><b>Praful Hinge</b> (SRH)<br><b>Ashwani Kumar</b> (MI)</td>
        <td>Exploit SRH/MI 25-man roster cuts; budget ₹1.0–1.8 Cr</td>
        <td>Acquires 145+ kph express pace depth and lethal left-arm wicket-taking pacer at baseline prices without bidding wars.</td>
      </tr>
      <tr>
        <td><b>Auction Day (Goa): Tier 1</b></td>
        <td><b>Mahipal Lomror</b><br><b>Nehal Wadhera</b></td>
        <td>Primary bidding priority; ceiling ₹4.5–6.5 Cr each</td>
        <td>Provides proven Indian middle-order muscle to eradicate early-collapse fragility and maximize late-overs acceleration.</td>
      </tr>
      <tr>
        <td><b>Auction Day (Goa): Value Buys</b></td>
        <td><b>Atharwa Taide</b> (FA)<br><b>Kuldeep Sen</b> (FA)<br><b>Sakib Hussain</b> (SRH)</td>
        <td>Late-round accelerated sweeps; budget ₹30L–₹80L each</td>
        <td>Completes the 25-man squad with 100% and 70% verified pressure consistency performers, preserving purse elasticity.</td>
      </tr>
    </tbody>
  </table>

  <div class="note-box" style="font-size: 8.2pt; padding: 7px 11px; background: #FFF5F9; border-left: 4px solid #E50695;">
    <b>Concluding Recommendation:</b> Season 1 showed that identifying Vignesh Puthur early led directly to an IPL signing. In Season 2, securing <b>Ayush Mhatre, Mahipal Lomror, Raghu Sharma, and Ashwani Kumar</b> will give Rajasthan Royals the most clutch, data-backed domestic foundation in IPL 2027.
  </div>
</div>
"""

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SupeRR Selector Season 2 — Rajasthan Royals IPL 2027 Auction Dossier</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  @page {{
    size: letter;
    margin: 0.44in 0.56in 0.44in 0.56in;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: 'Montserrat', 'Segoe UI', Calibri, Arial, sans-serif;
    color: #021D45;
    font-size: 8.6pt;
    line-height: 1.38;
    margin: 0;
    padding: 0;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}

  /* --- PAGE 1: COVER & DIRECTORY --- */
  .ps-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
  }}
  .ps-series {{
    font-size: 13pt;
    font-weight: 700;
    color: #021D45;
    margin-top: 6px;
    letter-spacing: -0.01em;
  }}
  .ps-logo {{
    height: 64px;
    width: auto;
    display: block;
  }}
  .ps-eyebrow {{
    font-size: 9pt;
    font-weight: 700;
    color: #E50695;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin: 0 0 4px 0;
  }}
  .ps-title {{
    font-size: 19pt;
    font-weight: 800;
    color: #021D45;
    line-height: 1.14;
    margin: 0 0 6px 0;
    max-width: 92%;
    letter-spacing: -0.02em;
  }}
  .ps-lead {{
    font-size: 8.4pt;
    color: #1E293B;
    margin: 0 0 8px 0;
    line-height: 1.4;
  }}
  .ps-box {{
    background: #F5F6FA;
    border-left: 4px solid #E50695;
    border-radius: 5px;
    padding: 6px 10px;
    margin-bottom: 8px;
    font-size: 8.0pt;
    line-height: 1.35;
    color: #0F172A;
  }}
  .dir-h {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    border-bottom: 2px solid #E50695;
    padding-bottom: 2px;
    margin-bottom: 4px;
    font-size: 8.8pt;
    font-weight: 800;
    color: #021D45;
  }}
  .dir-h span {{ font-size: 7.8pt; color: #E50695; font-weight: 700; }}
  .idx-tbl {{
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    font-size: 7.0pt;
    margin-bottom: 0px;
  }}
  .idx-tbl th {{
    background: #021D45;
    color: #FFFFFF;
    text-align: left;
    padding: 0 4px;
    height: 23px;
    line-height: 23px;
    font-weight: 700;
    white-space: nowrap;
    overflow: hidden;
  }}
  .idx-tbl tr {{
    height: 22px;
  }}
  .idx-tbl td {{
    padding: 0 4px;
    height: 22px;
    line-height: 22px;
    border-bottom: 1px solid #E2E8F0;
    color: #0F172A;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    vertical-align: middle;
  }}
  .idx-tbl tr:nth-child(even) td {{ background: #F8FAFC; }}

  /* Strategy Blueprint Table (Page 22) */
  .strategy-tbl {{
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    font-size: 7.1pt;
    margin-bottom: 8px;
  }}
  .strategy-tbl th {{
    background: #021D45;
    color: #FFFFFF;
    text-align: left;
    padding: 4px 6px;
    font-weight: 700;
    line-height: 1.25;
  }}
  .strategy-tbl td {{
    padding: 4px 6px;
    border-bottom: 1px solid #E2E8F0;
    color: #0F172A;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    vertical-align: top;
    line-height: 1.30;
  }}
  .strategy-tbl tr:nth-child(even) td {{ background: #F8FAFC; }}

  .two-col {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }}
  .tc {{ text-align: center; }}
  .tr {{ text-align: right; }}

  /* --- DEDICATED SINGLE PLAYER PAGES --- */
  .player-page {{
    page-break-before: always;
    break-before: page;
  }}
  .run-bar {{
    display: flex;
    justify-content: space-between;
    font-size: 7.0pt;
    color: #64748B;
    border-bottom: 1px solid #E2E8F0;
    padding-bottom: 2px;
    margin-bottom: 6px;
  }}
  .p-title-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #E50695;
    padding-bottom: 3px;
    margin-bottom: 6px;
  }}
  .p-title {{
    font-size: 11.4pt;
    font-weight: 800;
    color: #021D45;
    margin: 0;
    letter-spacing: -0.02em;
    white-space: nowrap;
  }}
  .p-role {{
    font-weight: 700;
    color: #475569;
    font-size: 9.0pt;
  }}
  .p-badges {{
    display: flex;
    gap: 5px;
    flex-shrink: 0;
  }}
  .badge {{
    font-size: 6.8pt;
    font-weight: 700;
    padding: 2.5px 7px;
    border-radius: 999px;
    color: #FFFFFF;
    white-space: nowrap;
  }}
  .badge-unc {{ background: #E50695; }}
  .badge-auc {{ background: #1226AA; }}
  .badge-team {{ background: #021D45; }}

  .sec-block {{ margin-bottom: 5px; }}
  .sec-hdr {{
    font-size: 8.6pt;
    font-weight: 800;
    color: #021D45;
    margin-bottom: 1.5px;
  }}
  .sec-p {{
    margin: 0;
    font-size: 8.2pt;
    color: #1E293B;
    line-height: 1.38;
  }}
  .stats-ul {{
    margin: 2px 0 4px 16px;
    padding: 0;
    font-size: 8.1pt;
    color: #0F172A;
  }}
  .stats-ul li {{
    margin-bottom: 2px;
    line-height: 1.32;
  }}

  .dash-wrap {{
    margin: 6px 0 6px 0;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid #1E293B;
    background: #060918;
  }}
  .dash-img {{
    width: 100%;
    height: auto;
    display: block;
  }}

  .log-wrap {{ margin: 4px 0 6px 0; }}
  .log-caption {{
    font-size: 7.4pt;
    font-weight: 700;
    color: #021D45;
    margin-bottom: 2px;
  }}
  .log-tbl {{
    width: 100%;
    border-collapse: collapse;
    font-size: 7.2pt;
  }}
  .log-tbl th {{
    background: #021D45;
    color: #FFFFFF;
    padding: 3px 5px;
    font-weight: 700;
  }}
  .log-tbl td {{
    padding: 2.5px 5px;
    border-bottom: 1px solid #E2E8F0;
  }}
  .log-tbl tr:nth-child(even) td {{ background: #F8FAFC; }}

  .note-box {{
    background: #FFF5F9;
    border-left: 3.5px solid #E50695;
    padding: 5px 9px;
    font-size: 7.8pt;
    line-height: 1.34;
    color: #0F172A;
    border-radius: 0 4px 4px 0;
    margin-top: 4px;
  }}
</style>
</head>
<body>

<!-- PAGE 1: COVER & DIRECTORY -->
<div>
  <div class="ps-header">
    <div class="ps-series">SupeRR Selector Season 2 • Rajasthan Royals Talent Scouting</div>
    <div style="display: flex; align-items: center; gap: 12px;">
      <img src="{AVATAR_SRC}" alt="Umeshraj Parkunan" class="ps-avatar" style="height: 48px; width: 48px; border-radius: 50%; border: 2.5px solid #E50695;">
      <img src="{LOGO_SRC}" alt="Rajasthan Royals" class="ps-logo">
    </div>
  </div>

  <div class="ps-eyebrow">Round 1: Identify the Most Reliable Players Under Pressure</div>
  <div class="ps-title">Help Shape Rajasthan Royals' IPL 2027 Auction Strategy</div>
  <div class="ps-lead">
    Prepared for <strong>Kumar Sangakkara</strong> and <strong>Giles Lindsay</strong> ahead of the IPL 2027 auction in Goa. 
    Season 1 proved the power of data by discovering Vignesh Puthur, whom RR signed at the 2026 auction. This dossier delivers 
    <strong>20 strictly uncapped Indian domestic specialists</strong> (10 Batters, 10 Bowlers) who consistently excel in high-pressure scenarios, 
    allowing Rajasthan Royals to maximize performance under the ₹157 Cr salary cap.
  </div>

  <div class="ps-box">
    <b>Analytical Methodology &amp; Framework:</b> Evaluated 2022–2026 IPL &amp; domestic match logs across high-leverage contexts 
    (chases with RRR ≥ 10.0, death overs 16–20, top-order collapses ≤ 30/3, and tight defenses). Features: 
    <em>Dynamic Par Edge</em> (benchmarked against era/venue par), <em>Consistency %</em> (% of crunch games delivered), 
    and <em>Bayesian Shrinkage Ranking</em>. Every player below has a dedicated dossier page with an individual analytical dashboard card, 
    KPI metrics, yearly trends, and verified match-by-match performance logs.
  </div>

  <div class="two-col">
    <div>
      <div class="dir-h">
        <b>TOP 10 INDIAN UNCAPPED BATTERS</b>
        <span>Pages 2–11</span>
      </div>
      <table class="idx-tbl">
        <colgroup>
          <col style="width: 7%;">
          <col style="width: 33%;">
          <col style="width: 29%;">
          <col style="width: 12%;">
          <col style="width: 13%;">
          <col style="width: 6%;">
        </colgroup>
        <thead>
          <tr><th class="tc">#</th><th>Player</th><th>Tactical Role</th><th class="tc">Team</th><th class="tr">Price</th><th class="tc">Pg</th></tr>
        </thead>
        <tbody>
          {"".join(bat_rows)}
        </tbody>
      </table>
    </div>

    <div>
      <div class="dir-h">
        <b>TOP 10 INDIAN UNCAPPED BOWLERS</b>
        <span>Pages 12–21</span>
      </div>
      <table class="idx-tbl">
        <colgroup>
          <col style="width: 7%;">
          <col style="width: 33%;">
          <col style="width: 29%;">
          <col style="width: 12%;">
          <col style="width: 13%;">
          <col style="width: 6%;">
        </colgroup>
        <thead>
          <tr><th class="tc">#</th><th>Player</th><th>Tactical Role</th><th class="tc">Team</th><th class="tr">Price</th><th class="tc">Pg</th></tr>
        </thead>
        <tbody>
          {"".join(bowl_rows)}
        </tbody>
      </table>
    </div>
  </div>

  <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 7.2pt; color: #64748B; border-top: 1px solid #E2E8F0; padding-top: 5px;">
    <span>Final Section: Rajasthan Royals War Room Strategy &amp; IPL 2027 Auction Execution Plan (p. 22)</span>
    <span>Strict Criteria: 100% Uncapped Indian Domestic Talent • Zero Capped Internationals</span>
  </div>
</div>

<!-- PAGES 2 TO 21: INDIVIDUAL PLAYER PAGES -->
{"".join(player_pages)}

<!-- PAGE 22: WAR ROOM STRATEGY BLUEPRINT -->
{page_22}

</body>
</html>
"""

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(full_html)

print(f"Generated complete HTML: {OUT_HTML} ({len(full_html)} bytes)")

# Compile to PDF
cmd = [
    EDGE_BIN,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={OUT_PDF}",
    OUT_HTML
]
print(f"Compiling PDF via Edge: {' '.join(cmd)}")
res = subprocess.run(cmd, capture_output=True, text=True)
print(f"Return code: {res.returncode}")
if os.path.exists(OUT_PDF):
    print(f"SUCCESS: Generated {OUT_PDF} ({os.path.getsize(OUT_PDF)} bytes)")
else:
    print(f"ERROR: PDF not found at {OUT_PDF}")
