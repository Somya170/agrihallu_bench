import pandas as pd
import json

df = pd.read_csv('data/raw/nass_crop_progress.csv')
planted = df[df['unit_desc'].str.contains('PLANTED', case=False, na=False)]

kb_entries = []

for (crop, state), group in planted.groupby(['query_commodity', 'query_state']):
    group = group.sort_values('week_ending')
    
    # Key milestones nikalo
    start_row  = group[group['Value'] >= 10].iloc[0]  if len(group[group['Value'] >= 10]) > 0  else None
    mid_row    = group[group['Value'] >= 50].iloc[0]  if len(group[group['Value'] >= 50]) > 0  else None
    peak_row   = group[group['Value'] >= 100].iloc[0] if len(group[group['Value'] >= 100]) > 0 else None

    start_date = start_row['week_ending'] if start_row is not None else 'unknown'
    mid_date   = mid_row['week_ending']   if mid_row   is not None else 'unknown'
    peak_date  = peak_row['week_ending']  if peak_row  is not None else 'unknown'

    state_lower = state.lower()
    crop_lower  = crop.lower()

    kb_id = f"kb_nass_2023_{state_lower.replace(' ','_')}_{crop_lower.replace(' ','_')}"

    text = (
        f"USDA NASS 2023 {state} {crop} planting progress: "
        f"Season started (10% planted) by {start_date}. "
        f"50% planted by {mid_date}. "
        f"100% planted by {peak_date}. "
        f"Source: USDA NASS 2023 Weekly Crop Progress."
    )

    keywords = [
        state_lower, crop_lower, "2023", "nass", "planted",
        "planting", "progress", "usda",
        start_date, mid_date, peak_date
    ]

    kb_entries.append({
        "id":       kb_id,
        "text":     text,
        "keywords": keywords
    })

    print(f"Generated: {kb_id}")
    print(f"  {text}")
    print()

# Save karo
with open('data/processed/nass_kb_entries.json', 'w') as f:
    json.dump(kb_entries, f, indent=2)

print(f"\nTotal entries generated: {len(kb_entries)}")
print("Saved: data/processed/nass_kb_entries.json")
