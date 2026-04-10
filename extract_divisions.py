#!/usr/bin/env python3
"""Extract team numbers from PDFs and match with world ranking data"""
import pdfplumber
import json
import re
import os
import csv

data_dir = "vex-data"

pdfs = [
    ("arts", "arts-division-list-viqrc-elementary-school-2026-vex-robotics-world-championship.pdf", "Elementary"),
    ("engineering", "engineering-division-list-viqrc-elementary-school-2026-vex-robotics-world-championship.pdf", "Elementary"),
    ("math", "math-division-list-viqrc-elementary-school-2026-vex-robotics-world-championship.pdf", "Elementary"),
    ("science", "science-division-list-viqrc-elementary-school-2026-vex-robotics-world-championship.pdf", "Elementary"),
    ("technology", "technology-division-list-viqrc-elementary-school-2026-vex-robotics-world-championship.pdf", "Elementary"),
    ("design", "design-division-list-viqrc-middle-school-2026-vex-robotics-world-championship.pdf", "Middle School"),
    ("innovate", "innovate-division-list-viqrc-middle-school-2026-vex-robotics-world-championship.pdf", "Middle School"),
    ("opportunity", "opportunity-division-list-viqrc-middle-school-2026-vex-robotics-world-championship.pdf", "Middle School"),
    ("research", "research-division-list-viqrc-middle-school-2026-vex-robotics-world-championship.pdf", "Middle School"),
    ("spirit", "spirit-division-list-viqrc-middle-school-2026-vex-robotics-world-championship.pdf", "Middle School"),
]

# Load world ranking data
print("Loading world ranking data...")
rankings_es = {}
rankings_ms = {}

with open(f'{data_dir}/world-ranking-es.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        team_num = row['Team Number'].strip()
        rankings_es[team_num] = {
            'world_rank': int(row['Rank']),
            'score': int(row['Score']) if row['Score'] else 0,
            'auto_score': int(row['Autonomous Coding Skills']) if row['Autonomous Coding Skills'] else 0,
            'driver_score': int(row['Driver Skills']) if row['Driver Skills'] else 0,
            'team_name': row['Team Name'],
            'organization': row['Organization'],
            'region': row['Event Region']
        }

with open(f'{data_dir}/world-ranking-ms.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        team_num = row['Team Number'].strip()
        rankings_ms[team_num] = {
            'world_rank': int(row['Rank']),
            'score': int(row['Score']) if row['Score'] else 0,
            'auto_score': int(row['Autonomous Coding Skills']) if row['Autonomous Coding Skills'] else 0,
            'driver_score': int(row['Driver Skills']) if row['Driver Skills'] else 0,
            'team_name': row['Team Name'],
            'organization': row['Organization'],
            'region': row['Event Region']
        }

print(f"  Elementary: {len(rankings_es)} teams")
print(f"  Middle School: {len(rankings_ms)} teams")

# Process each PDF
all_divisions = {}

for div_code, pdf_name, grade in pdfs:
    pdf_path = os.path.join(data_dir, pdf_name)
    print(f"\n{'='*50}")
    print(f"Processing: {div_code} ({grade})")
    print('='*50)

    teams = []
    team_numbers_found = set()

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                # Find all team numbers in the text
                # Pattern: 4-5 digits optionally followed by a letter
                matches = re.findall(r'\b(\d{4,5}[A-Z]?)\b', text)

                for team_num in matches:
                    # Skip if it's likely not a team number (too common numbers)
                    if int(team_num.rstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ')) < 10:
                        continue
                    if team_num in team_numbers_found:
                        continue
                    team_numbers_found.add(team_num)

                    # Match with world ranking
                    rank_data = None
                    if grade == "Elementary" and team_num in rankings_es:
                        rank_data = rankings_es[team_num]
                    elif grade == "Middle School" and team_num in rankings_ms:
                        rank_data = rankings_ms[team_num]

                    if rank_data:
                        team_info = {
                            "number": team_num,
                            "name": rank_data['team_name'],
                            "organization": rank_data['organization'],
                            "region": rank_data['region'],
                            "division": div_code,
                            "grade": grade,
                            "world_rank": rank_data['world_rank'],
                            "score": rank_data['score'],
                            "auto_score": rank_data['auto_score'],
                            "driver_score": rank_data['driver_score'],
                            "is_magikid": "magikid" in rank_data['organization'].lower() or "magikid" in rank_data['team_name'].lower()
                        }
                    else:
                        team_info = {
                            "number": team_num,
                            "name": "Unknown",
                            "organization": "Unknown",
                            "region": "Unknown",
                            "division": div_code,
                            "grade": grade,
                            "world_rank": None,
                            "score": None,
                            "auto_score": None,
                            "driver_score": None,
                            "is_magikid": False
                        }

                    teams.append(team_info)

    except Exception as e:
        print(f"Error: {e}")

    # Sort by world rank (None ranks last)
    teams.sort(key=lambda x: x.get('world_rank', 99999) if x.get('world_rank') else 99999)

    # Count matched
    matched = sum(1 for t in teams if t['world_rank'])
    print(f"Total teams: {len(teams)}, Matched with world ranking: {matched}")

    # Show magikid teams
    magikid = [t for t in teams if t['is_magikid']]
    if magikid:
        print(f"Magikid teams: {len(magikid)}")
        for t in magikid[:5]:
            print(f"  {t['number']}: {t['name']} (Rank #{t['world_rank']}, {t['score']}pts)")

    all_divisions[div_code] = {
        "grade": grade,
        "total_teams": len(teams),
        "teams": teams
    }

# Save all data
output = {
    "divisions": all_divisions,
    "last_updated": "2026-04-09"
}

with open(f'{data_dir}/all-divisions.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n\n{'='*50}")
print("SUMMARY")
print('='*50)
total = sum(d['total_teams'] for d in all_divisions.values())
print(f"Total divisions: {len(all_divisions)}")
print(f"Total teams: {total}")
for div, data in all_divisions.items():
    print(f"  {div}: {data['total_teams']} teams")
print(f"\nSaved to: {data_dir}/all-divisions.json")
