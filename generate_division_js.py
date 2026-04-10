#!/usr/bin/env python3
"""Generate JavaScript code for division teams from extracted data"""
import json

with open('vex-data/all-divisions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Build the JS data structure
js_lines = ["// VIQRC Division Teams - Extracted from official PDFs and matched with world rankings"]
js_lines.append("// Last updated: 2026-04-09")
js_lines.append("const viqrcDivisionTeams = {")

divisions = data['divisions']

# Elementary divisions
js_lines.append("  'Elementary School': {")
for div in ['arts', 'engineering', 'math', 'science', 'technology']:
    if div in divisions:
        teams = divisions[div]['teams']
        js_lines.append(f"    '{div.capitalize()}': [")

        for t in teams[:80]:  # Top 80 per division
            # Escape special characters in name
            name = t['name'].replace("'", "\\'").replace('"', '\\"')
            org = t['organization'].replace("'", "\\'").replace('"', '\\"')

            js_lines.append(f"      {{ num: '{t['number']}', name: '{name}', org: '{org}', region: '{t['region']}', skillRank: {t['world_rank'] if t['world_rank'] else 'null'}, score: {t['score'] if t['score'] else 0}, autoScore: {t['auto_score'] if t['auto_score'] else 0}, driverScore: {t['driver_score'] if t['driver_score'] else 0}, magikid: {'true' if t['is_magikid'] else 'false'} }},")

        js_lines.append("    ],")

js_lines.append("  },")

# Middle School divisions
js_lines.append("  'Middle School': {")
for div in ['design', 'innovate', 'opportunity', 'research', 'spirit']:
    if div in divisions:
        teams = divisions[div]['teams']
        js_lines.append(f"    '{div.capitalize()}': [")

        for t in teams[:80]:
            name = t['name'].replace("'", "\\'").replace('"', '\\"')
            org = t['organization'].replace("'", "\\'").replace('"', '\\"')

            js_lines.append(f"      {{ num: '{t['number']}', name: '{name}', org: '{org}', region: '{t['region']}', skillRank: {t['world_rank'] if t['world_rank'] else 'null'}, score: {t['score'] if t['score'] else 0}, autoScore: {t['auto_score'] if t['auto_score'] else 0}, driverScore: {t['driver_score'] if t['driver_score'] else 0}, magikid: {'true' if t['is_magikid'] else 'false'} }},")

        js_lines.append("    ],")

js_lines.append("  }")
js_lines.append("};")

# Print the JS
print('\n'.join(js_lines))

# Also save a lookup map for team -> division
lookup = {}
for div, data in divisions.items():
    for t in data['teams']:
        lookup[t['number']] = {
            'division': div,
            'grade': data['grade'],
            'world_rank': t['world_rank'],
            'score': t['score']
        }

# Save lookup
with open('vex-data/team-division-lookup.json', 'w', encoding='utf-8') as f:
    json.dump(lookup, f, ensure_ascii=False, indent=2)

print("\n\n// Team to Division Lookup saved to vex-data/team-division-lookup.json")
