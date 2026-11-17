import json
import re
import shutil

def run_update():
    # 1. Load PLAYERS and NARRATIVES from build_complete_actual_retentions_dossier
    from build_complete_actual_retentions_dossier import PLAYERS, NARRATIVES

    # Save to evaluated_targets_2027.json
    with open("evaluated_targets_2027.json", "w", encoding="utf-8") as f:
        json.dump(PLAYERS, f, indent=2)
    print("Saved evaluated_targets_2027.json successfully.")

    # Prepare dashboard format
    dashboard_players = []
    for p in PLAYERS:
        narr = NARRATIVES.get(p["name"], {})
        est_price = f"₹{p['price_cr']:.2f} Cr" if p["price_cr"] is not None else "₹0.30 - 0.80 Cr"
        dp = {
            "rank": p["rank"],
            "name": p["name"],
            "id": p["id"],
            "category": p["category"],
            "role": p["role"],
            "team26": p["team26"],
            "apps26": p["apps26"],
            "price_cr": p["price_cr"] if p["price_cr"] is not None else 0.30,
            "est_price": est_price,
            "status": "Available (Uncapped Pool)",
            "overseas": False,
            "country": "India",
            "capped": False,
            "hand": p["hand"],
            "primary_mode": p["primary_mode"],
            "is_allrounder": p.get("is_allrounder", False),
            "bat": p["bat"],
            "bowl": p["bowl"],
            "yearly_bat": p["yearly_bat"],
            "yearly_bowl": p["yearly_bowl"],
            "bat_logs": p["bat_logs"],
            "bowl_logs": p["bowl_logs"],
            "file_name": p["file_name"],
            "narrative": {
                "summary": narr.get("summary", ""),
                "why_rr": narr.get("why_rr", ""),
                "stats_panel": narr.get("stats_panel", []),
                "strategic_note": narr.get("note", "")
            }
        }
        dashboard_players.append(dp)

    players_json = json.dumps(dashboard_players)

    rr_bat_retained = [
        {"name": "Dhruv Jurel", "role": "Wicketkeeper-Finisher", "p_score": 86.4, "p_runs": 348, "p_sr": 158.2, "p_avg": 34.8, "verdict": "Retained core finisher (₹14.0 Cr)"},
        {"name": "Riyan Parag", "role": "Middle-Order Anchor / Off-Spin", "p_score": 85.0, "p_runs": 573, "p_sr": 149.2, "p_avg": 44.1, "verdict": "Retained No. 4 anchor & vice-captain (₹14.0 Cr)"},
        {"name": "Ravindra Jadeja", "role": "All-Phase Finisher / SLA", "p_score": 84.2, "p_runs": 410, "p_sr": 142.5, "p_avg": 35.0, "verdict": "Retained veteran all-rounder (₹18.0 Cr)"},
        {"name": "Vaibhav Suryavanshi", "role": "Top-Order Batter", "p_score": 75.0, "p_runs": 120, "p_sr": 138.0, "p_avg": 24.0, "verdict": "Retained U19 prodigy (₹1.1 Cr)"},
        {"name": "Shubham Dubey", "role": "Middle-Order Hitter", "p_score": 72.0, "p_runs": 95, "p_sr": 145.0, "p_avg": 19.0, "verdict": "Retained power hitter (₹5.8 Cr)"}
    ]

    rr_bowl_retained = [
        {"name": "Mohammed Shami", "role": "Seam Spearhead", "p_score": 88.0, "p_econ": 8.12, "w_per_ov": 0.65, "dot_pct": 46.2, "verdict": "Frontline strike seamer (Traded In from LSG)"},
        {"name": "Jofra Archer", "role": "Express Strike Pacer", "p_score": 87.5, "p_econ": 7.95, "w_per_ov": 0.68, "dot_pct": 48.0, "verdict": "Retained frontline pacer (₹12.5 Cr)"},
        {"name": "Sandeep Sharma", "role": "Death-Overs Specialist", "p_score": 86.8, "p_econ": 8.15, "w_per_ov": 0.58, "dot_pct": 44.5, "verdict": "Retained death closer (₹4.0 Cr)"},
        {"name": "Ravi Bishnoi", "role": "Lead Wrist-Spinner", "p_score": 85.5, "p_econ": 7.80, "w_per_ov": 0.55, "dot_pct": 42.0, "verdict": "Retained lead leg-spinner (₹11.0 Cr)"},
        {"name": "Nandre Burger", "role": "Left-Arm Express Seamer", "p_score": 81.0, "p_econ": 8.65, "w_per_ov": 0.60, "dot_pct": 40.5, "verdict": "Retained overseas left-arm strike (₹0.5 Cr)"}
    ]

    ipl_squads_retained = [
        {"team": "Rajasthan Royals", "abbr": "RR", "total": 17, "os": 5, "cut_req": "8 Slots Open (3 OS)", "squeeze_targets": "Targets: Mahipal Lomror, Atharwa Taide, Kuldeep Sen, Akash Madhwal"},
        {"team": "Chennai Super Kings", "abbr": "CSK", "total": 19, "os": 6, "cut_req": "6 Slots Open (2 OS)", "squeeze_targets": "Retained Samson (Traded from RR), Gaikwad, Mhatre"},
        {"team": "Mumbai Indians", "abbr": "MI", "total": 17, "os": 6, "cut_req": "8 Slots Open (2 OS)", "squeeze_targets": "Retained Bumrah, Rohit, Raghu Sharma, Ashwani Kumar"},
        {"team": "Royal Challengers Bengaluru", "abbr": "RCB", "total": 21, "os": 6, "cut_req": "4 Slots Open (2 OS)", "squeeze_targets": "Released Mahipal Lomror, Retained Kohli, Patidar"},
        {"team": "Kolkata Knight Riders", "abbr": "KKR", "total": 16, "os": 6, "cut_req": "9 Slots Open (2 OS)", "squeeze_targets": "Retained Rinku, Narine, Russell, Chakaravarthy"},
        {"team": "Sunrisers Hyderabad", "abbr": "SRH", "total": 17, "os": 6, "cut_req": "8 Slots Open (2 OS)", "squeeze_targets": "Released Taide, Suchith; Retained Klaasen, Cummins"},
        {"team": "Delhi Capitals", "abbr": "DC", "total": 14, "os": 4, "cut_req": "11 Slots Open (4 OS)", "squeeze_targets": "Released Porel, Lalit; Retained KL Rahul, Axar"},
        {"team": "Gujarat Titans", "abbr": "GT", "total": 23, "os": 7, "cut_req": "2 Slots Open (1 OS)", "squeeze_targets": "Released Shahrukh Khan; Retained Gill, Rashid"},
        {"team": "Punjab Kings", "abbr": "PBKS", "total": 19, "os": 7, "cut_req": "6 Slots Open (1 OS)", "squeeze_targets": "Released Wadhera, Dubey; Retained Iyer, Hardik"},
        {"team": "Lucknow Super Giants", "abbr": "LSG", "total": 17, "os": 5, "cut_req": "8 Slots Open (3 OS)", "squeeze_targets": "Released Mankad, Hangargekar; Retained Pooran, Curran"}
    ]

    with open("RR_Auction_Dashboard.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Safe regex replacement using lambda
    html = re.sub(r'const PLAYERS = \[.*?\];\n', lambda m: f'const PLAYERS = {players_json};\n', html, flags=re.DOTALL)
    html = re.sub(r'const RR_BAT = \[.*?\];\n', lambda m: f'const RR_BAT = {json.dumps(rr_bat_retained)};\n', html, flags=re.DOTALL)
    html = re.sub(r'const RR_BOWL = \[.*?\];\n', lambda m: f'const RR_BOWL = {json.dumps(rr_bowl_retained)};\n', html, flags=re.DOTALL)
    html = re.sub(r'const IPL_SQUADS = \[.*?\];\n', lambda m: f'const IPL_SQUADS = {json.dumps(ipl_squads_retained)};\n', html, flags=re.DOTALL)

    new_label_config = """  const labelConfig = {
    "Mahipal Lomror": { text: "Mahipal Lomror", ha: "center", va: "bottom", dx: 0, dy: -18 },
    "Atharwa Taide": { text: "Atharwa Taide", ha: "right", va: "center", dx: -16, dy: 0 },
    "Anmolpreet Singh": { text: "Anmolpreet", ha: "left", va: "center", dx: 16, dy: 0 },
    "M Shahrukh Khan": { text: "M. Shahrukh", ha: "left", va: "center", dx: 16, dy: 0 },
    "Prerak Mankad": { text: "Prerak Mankad", ha: "right", va: "center", dx: -16, dy: 0 },
    "Abishek Porel": { text: "Abishek Porel", ha: "right", va: "center", dx: -16, dy: -4 },
    "Narayan Jagadeesan": { text: "N. Jagadeesan", ha: "right", va: "center", dx: -16, dy: 4 },
    "Lalit Yadav": { text: "Lalit Yadav", ha: "left", va: "center", dx: 16, dy: -4 },
    "Hrithik Shokeen": { text: "Hrithik Shokeen", ha: "right", va: "center", dx: -16, dy: 0 },
    "Nehal Wadhera": { text: "Nehal Wadhera", ha: "center", va: "bottom", dx: 0, dy: -18 },
    "Jagadeesha Suchith": { text: "J. Suchith", ha: "left", va: "center", dx: 16, dy: 0 },
    "Murugan Ashwin": { text: "M. Ashwin", ha: "left", va: "center", dx: 16, dy: 0 },
    "Kuldeep Sen": { text: "Kuldeep Sen", ha: "left", va: "center", dx: 16, dy: 0 },
    "Praveen Dubey": { text: "Praveen Dubey", ha: "right", va: "center", dx: -16, dy: 0 },
    "Simarjeet Singh": { text: "Simarjeet Singh", ha: "left", va: "center", dx: 16, dy: 0 },
    "Rajvardhan Hangargekar": { text: "Hangargekar", ha: "left", va: "center", dx: 16, dy: 0 },
    "Akash Madhwal": { text: "Akash Madhwal", ha: "left", va: "center", dx: 16, dy: -4 },
    "Kumar Kartikeya Singh": { text: "K. Kartikeya", ha: "right", va: "center", dx: -16, dy: 0 },
    "Darshan Nalkande": { text: "Darshan Nalkande", ha: "left", va: "center", dx: 16, dy: 0 },
    "KM Asif": { text: "KM Asif", ha: "right", va: "center", dx: -16, dy: 0 }
  };"""

    html = re.sub(r'  const labelConfig = \{.*?\n  \};', lambda m: new_label_config, html, flags=re.DOTALL)

    # Adjust canvas dimensions for un-stretched, sharp rendering
    html = html.replace(
        'const displayHeight = Math.min(580, Math.max(460, Math.round(displayWidth * 0.46)));',
        'const displayHeight = Math.min(620, Math.max(500, Math.round(displayWidth * 0.48)));'
    )

    with open("RR_Auction_Dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)

    shutil.copyfile("RR_Auction_Dashboard.html", "index.html")
    print("Dashboard and index.html successfully updated!")

if __name__ == "__main__":
    run_update()
