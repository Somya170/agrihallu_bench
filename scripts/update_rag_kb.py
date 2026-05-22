import re

with open('src/rag_pipeline.py', 'r') as f:
    content = f.read()

# New KB entries
new_entries = '''    {
        "id": "kb_oklahoma_winter_wheat",
        "text": "Oklahoma Winter Wheat: Plant mid October to early November. Harvest June through early July. Oklahoma is second largest winter wheat state after Kansas.",
        "keywords": ["oklahoma", "wheat", "winter wheat", "plant", "harvest", "october", "november", "june", "july"]
    },
    {
        "id": "kb_washington_spring_wheat",
        "text": "Washington Spring Wheat: Plant March through April. Harvest August through September. Washington Palouse region is top spring wheat area.",
        "keywords": ["washington", "wheat", "spring wheat", "plant", "harvest", "march", "april", "august"]
    },
    {
        "id": "kb_iowa_soybeans",
        "text": "Iowa Soybeans: Plant early May to early June. Harvest October through November. Iowa is top soybean producing state alongside Illinois.",
        "keywords": ["iowa", "soybeans", "soybean", "plant", "harvest", "may", "june", "october"]
    },
    {
        "id": "kb_illinois_corn",
        "text": "Illinois Corn: Plant late April to late May. Harvest October through November. Illinois is second largest corn producing state.",
        "keywords": ["illinois", "corn", "plant", "harvest", "april", "may", "october", "november"]
    },
    {
        "id": "kb_georgia_peanuts",
        "text": "Georgia Peanuts: Plant late April to mid May. Harvest October through November. Georgia produces 40% of US peanuts.",
        "keywords": ["georgia", "peanuts", "peanut", "plant", "harvest", "april", "may", "october"]
    },
    {
        "id": "kb_mississippi_cotton",
        "text": "Mississippi Cotton: Plant late April to mid May. Harvest October through November. Mississippi Delta is prime cotton region.",
        "keywords": ["mississippi", "cotton", "plant", "harvest", "april", "may", "october"]
    },
    {
        "id": "kb_wisconsin_cranberries",
        "text": "Wisconsin Cranberries: Plant April through May. Harvest September through October. Wisconsin produces 60% of US cranberries.",
        "keywords": ["wisconsin", "cranberries", "cranberry", "plant", "harvest", "april", "september", "october"]
    },
    {
        "id": "kb_california_tomatoes",
        "text": "California Tomatoes: Plant March through May. Harvest July through October. California produces 90% of US processed tomatoes.",
        "keywords": ["california", "tomatoes", "tomato", "plant", "harvest", "march", "may", "july", "october"]
    },'''

# kb_illinois_soybeans ke baad insert karo
insert_after = '"keywords": ["illinois", "soybeans", "soybean", "plant", "harvest", "may", "june"]\n    },'
content = content.replace(insert_after, insert_after + '\n' + new_entries)

with open('src/rag_pipeline.py', 'w') as f:
    f.write(content)

print("Knowledge base updated!")

# Verify
import importlib.util
spec = importlib.util.spec_from_file_location("rag", "src/rag_pipeline.py")
# Count KB entries
kb_count = content.count('"id": "kb_')
print(f"Total KB entries now: {kb_count}")
