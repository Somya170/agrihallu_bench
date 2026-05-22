import pandas as pd
import json

df = pd.read_csv('data/raw/nass_crop_progress.csv')

planted   = df[df['unit_desc'] == 'PCT PLANTED']
harvested = df[df['unit_desc'] == 'PCT HARVESTED']

kb_entries = []

all_combos = set(
    [(r['query_commodity'], r['query_state']) for _, r in planted.iterrows()] +
    [(r['query_commodity'], r['query_state']) for _, r in harvested.iterrows()]
)

for (crop, state) in all_combos:
    p = planted[(planted['query_commodity']==crop) & (planted['query_state']==state)].sort_values('week_ending')
    h = harvested[(harvested['query_commodity']==crop) & (harvested['query_state']==state)].sort_values('week_ending')

    # Planting milestones
    p_start = p[p['Value'] >= 10].iloc[0]['week_ending']  if len(p[p['Value'] >= 10])  > 0 else 'unknown'
    p_50    = p[p['Value'] >= 50].iloc[0]['week_ending']  if len(p[p['Value'] >= 50])  > 0 else 'unknown'
    p_peak  = p[p['Value'] >= 100].iloc[0]['week_ending'] if len(p[p['Value'] >= 100]) > 0 else 'unknown'

    # Harvest milestones
    h_start = h[h['Value'] >= 10].iloc[0]['week_ending'] if len(h[h['Value'] >= 10]) > 0 else 'unknown'
    h_50    = h[h['Value'] >= 50].iloc[0]['week_ending'] if len(h[h['Value'] >= 50]) > 0 else 'unknown'
    h_peak  = h[h['Value'] >= 90].iloc[0]['week_ending'] if len(h[h['Value'] >= 90]) > 0 else 'unknown'
    h_max   = int(h['Value'].max()) if len(h) > 0 else 0
    h_max_date = h[h['Value'] == h['Value'].max()].iloc[0]['week_ending'] if len(h) > 0 else 'unknown'

    state_lower = state.lower()
    crop_lower  = crop.lower()
    kb_id = f"kb_nass_2023_{state_lower.replace(' ','_')}_{crop_lower.replace(' ','_')}_full"

    text = (
        f"USDA NASS 2023 {state} {crop}: "
        f"PLANTING — Season started (10%) by {p_start}, "
        f"50% planted by {p_50}, 100% planted by {p_peak}. "
        f"HARVEST — Season started (10%) by {h_start}, "
        f"50% harvested by {h_50}, "
        f"peak {h_max}% harvested reached by {h_max_date}. "
        f"Source: USDA NASS 2023 Weekly Crop Progress Reports."
    )

    keywords = [
        state_lower, crop_lower, "2023", "nass", "usda",
        "planted", "planting", "harvested", "harvest",
        "peak", "progress", "weekly",
        p_start, p_50, p_peak,
        h_start, h_50, h_max_date
    ]

    kb_entries.append({
        "id": kb_id,
        "text": text,
        "keywords": [k for k in keywords if k != 'unknown']
    })

    print(f"Generated: {kb_id}")
    print(f"  {text[:120]}...")
    print()

with open('data/processed/nass_full_kb.json', 'w') as f:
    json.dump(kb_entries, f, indent=2)

print(f"\nTotal: {len(kb_entries)} entries")
print("Saved: data/processed/nass_full_kb.json")
