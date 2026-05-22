import json

# NASS entries load karo
with open('data/processed/nass_kb_entries.json') as f:
    nass_entries = json.load(f)

# rag_pipeline.py read karo
with open('src/rag_pipeline.py') as f:
    content = f.read()

# Check — already injected hai kya
if 'kb_nass_2023' in content:
    print("Already injected! Skipping.")
else:
    # KNOWLEDGE_BASE list ke end mein add karo
    # Last entry ke baad, closing bracket se pehle
    insert_before = '\n]\n\n\ndef retrieve_context'
    
    new_entries_str = ''
    for entry in nass_entries:
        keywords_str = json.dumps(entry['keywords'])
        new_entries_str += f'''    {{
        "id": "{entry['id']}",
        "text": "{entry['text']}",
        "keywords": {keywords_str}
    }},
'''
    
    content = content.replace(
        insert_before,
        '\n' + new_entries_str + insert_before
    )
    
    with open('src/rag_pipeline.py', 'w') as f:
        f.write(content)
    
    print(f"Injected {len(nass_entries)} NASS entries!")

# Verify
kb_count = content.count('"id": "kb_')
print(f"Total KB entries now: {kb_count}")

# Quick test
from src.rag_pipeline import retrieve_context
test_qs = [
    "According to USDA NASS 2023 data, by what date was 50% of Corn crop planted in Iowa?",
    "When did Corn planted begin in Iowa during the 2023 season, according to USDA NASS?",
    "When did Soybeans planting begin in Iowa in 2023?",
]

print()
print("=== Retrieval Test ===")
for q in test_qs:
    ctx = retrieve_context(q)
    src = ctx.split('[Source:')[1].split(']')[0].strip() if '[Source:' in ctx else 'NONE'
    print(f"Q: {q[:60]}...")
    print(f"Source: {src}")
    print()
