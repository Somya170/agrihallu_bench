import json

with open('data/processed/nass_full_kb.json') as f:
    nass_entries = json.load(f)

with open('src/rag_pipeline.py') as f:
    content = f.read()

# Purane NASS entries remove karo pehle
import re
content = re.sub(
    r'\s*\{\s*"id":\s*"kb_nass_2023_[^}]+\},?\s*',
    '\n',
    content
)

# Naye full entries add karo
new_entries_str = ''
for entry in nass_entries:
    keywords_str = json.dumps(entry['keywords'])
    new_entries_str += f'''    {{
        "id": "{entry['id']}",
        "text": "{entry['text']}",
        "keywords": {keywords_str}
    }},
'''

insert_before = '\n]\n\n\ndef retrieve_context'
content = content.replace(
    insert_before,
    '\n' + new_entries_str + insert_before
)

with open('src/rag_pipeline.py', 'w') as f:
    f.write(content)

kb_count = content.count('"id": "kb_')
print(f"Total KB entries: {kb_count}")

# Quick test
import sys
sys.path.insert(0, '.')

# Reload module
import importlib
import src.rag_pipeline as rag_mod
importlib.reload(rag_mod)

test_qs = [
    "What was the peak harvested percentage for Corn in Iowa in 2023, and when was it reached?",
    "According to USDA NASS 2023 data, by what date was 50% of Corn crop planted in Iowa?",
    "When did Corn harvest begin in Illinois in 2023?",
]

print()
print("=== Retrieval Test ===")
for q in test_qs:
    ctx = rag_mod.retrieve_context(q)
    src = ctx.split('[Source:')[1].split(']')[0].strip() if '[Source:' in ctx else 'NONE'
    print(f"Q: {q[:65]}...")
    print(f"Source: {src}")
    print()
