import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

os.makedirs('paper/figures', exist_ok=True)

# Figure 1 — V2 Baseline vs RAG
categories = ['FACTUAL', 'DOSAGE', 'REGULATORY', 'TEMPORAL']
baseline   = [45.7, 40.0, 50.0, 23.3]
rag        = [31.4, 16.0, 25.0, 53.3]

x = np.arange(len(categories))
width = 0.35

fig, ax = plt.subplots(figsize=(8, 5))
bars1 = ax.bar(x - width/2, baseline, width, label='Baseline', color='#d62728', alpha=0.85)
bars2 = ax.bar(x + width/2, rag,      width, label='RAG',      color='#2ca02c', alpha=0.85)

ax.set_xlabel('Hallucination Category', fontsize=12)
ax.set_ylabel('Hallucination Rate (%)', fontsize=12)
ax.set_title('Figure 1: Baseline vs RAG Hallucination Rate\n(V2 Synthetic Dataset, n=110)', fontsize=13)
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend(fontsize=11)
ax.set_ylim(0, 70)
ax.axhline(y=0, color='black', linewidth=0.5)

# Value labels
for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{bar.get_height():.1f}%', ha='center', va='bottom', fontsize=9)
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{bar.get_height():.1f}%', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('paper/figures/fig1_baseline_vs_rag.png', dpi=300, bbox_inches='tight')
plt.close()
print("Figure 1 saved!")

# Figure 2 — Geographic Retrieval Confusion
fig, ax = plt.subplots(figsize=(7, 5))

labels  = ['Correct State\nRetrieved', 'Wrong State\nRetrieved']
sizes   = [33.3, 66.7]
colors  = ['#2ca02c', '#d62728']
explode = [0, 0.08]

wedges, texts, autotexts = ax.pie(
    sizes, explode=explode, labels=labels,
    colors=colors, autopct='%1.1f%%',
    startangle=90, textprops={'fontsize': 12}
)
autotexts[0].set_fontsize(13)
autotexts[1].set_fontsize(13)

ax.set_title('Figure 2: Geographic Retrieval Confusion\nin Temporal RAG Queries (n=30)', fontsize=13)
plt.tight_layout()
plt.savefig('paper/figures/fig2_geographic_confusion.png', dpi=300, bbox_inches='tight')
plt.close()
print("Figure 2 saved!")

# Figure 3 — Dosage RAG improvement V2 vs V3
fig, ax = plt.subplots(figsize=(7, 5))

datasets  = ['V2 Synthetic', 'V3 Real Data']
baseline_d = [40.0, 100.0]
rag_d      = [16.0, 25.0]

x = np.arange(len(datasets))
bars1 = ax.bar(x - width/2, baseline_d, width, label='Baseline', color='#d62728', alpha=0.85)
bars2 = ax.bar(x + width/2, rag_d,      width, label='RAG',      color='#2ca02c', alpha=0.85)

ax.set_ylabel('Hallucination Rate (%)', fontsize=12)
ax.set_title('Figure 3: DOSAGE Category — RAG Effectiveness\nAcross V2 and V3 Datasets', fontsize=13)
ax.set_xticks(x)
ax.set_xticklabels(datasets, fontsize=12)
ax.legend(fontsize=11)
ax.set_ylim(0, 115)

for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{bar.get_height():.1f}%', ha='center', va='bottom', fontsize=10)
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{bar.get_height():.1f}%', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('paper/figures/fig3_dosage_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print("Figure 3 saved!")

print()
print("All figures saved in paper/figures/")
print("Resolution: 300 DPI — journal ready!")
