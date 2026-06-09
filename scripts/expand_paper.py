with open('paper/agrihallubench_draft.md', 'r') as f:
    content = f.read()

# Expansion 1 — Introduction
old1 = "The consequences of agricultural AI hallucination"
if old1 not in content:
    content = content.replace(
        "This gap is critical: agricultural queries require fine-grained geographic and temporal reasoning that general benchmarks do not capture.",
        """This gap is critical: agricultural queries require fine-grained geographic and temporal reasoning that general benchmarks do not capture.

The consequences of agricultural AI hallucination extend beyond inconvenience. A farmer acting on a hallucinated pesticide recommendation faces EPA fines up to $25,000 per violation under FIFRA. A wrong nitrogen rate causes nitrate leaching into waterways. A wrong harvest timing causes crop rejection at the grain elevator. These real-world consequences motivate rigorous hallucination evaluation before deploying LLMs in agricultural advisory contexts."""
    )
    print("Expansion 1 done")

# Expansion 2 — Related Work 2.4
old2 = "### 2.4 LLM Safety"
if old2 not in content:
    content = content.replace(
        "Our work identifies geographic retrieval confusion as a novel failure mode specific to location-dependent agricultural queries. We show that 66.7% of temporal RAG failures stem from retrieving documents for geographically adjacent states — a failure mode with no equivalent in medical or legal RAG systems where jurisdiction is typically unambiguous.",
        """Our work identifies geographic retrieval confusion as a novel failure mode specific to location-dependent agricultural queries. We show that 66.7% of temporal RAG failures stem from retrieving documents for geographically adjacent states — a failure mode with no equivalent in medical or legal RAG systems where jurisdiction is typically unambiguous.

### 2.4 LLM Safety in High-Stakes Domains

The deployment of LLMs in high-stakes domains has prompted significant safety research. Studies show that LLMs exhibit systematic overconfidence in domain-specific factual claims, producing confident incorrect responses rather than appropriate uncertainty. Our work extends this line of research to the agricultural domain, providing the first systematic evidence that model size and reasoning augmentation substantially reduce domain-specific hallucination rates."""
    )
    print("Expansion 2 done")

# Expansion 3 — Dataset table
old3 = "Table 2 summarizes"
if old3 not in content:
    content = content.replace(
        "All HIGH severity ratings were independently verified against USDA Extension Service guidelines.",
        """All HIGH severity ratings were independently verified against USDA Extension Service guidelines.

Table 2 summarizes AgriHallu-Bench dataset statistics across both versions.

| Attribute | V2 Synthetic | V3 Real |
|-----------|-------------|---------|
| Total QA pairs | 135 | 126 |
| Categories | 4 | 3 |
| HIGH severity | 40.9% | 38.1% |
| MEDIUM severity | 45.5% | 47.6% |
| Verified source | EPA/USDA Extension | USDA NASS 2023 |
| Ground truth type | Regulatory/Agronomic | Exact dates |"""
    )
    print("Expansion 3 done")

# Expansion 4 — Finding 4 + Combined Analysis
old4 = "Finding 4"
if old4 not in content:
    content = content.replace(
        "Figure 4 illustrates the multi-model comparison across all categories.",
        """Figure 4 illustrates the multi-model comparison across all categories.

**Finding 4 — Reasoning augmentation outperforms RAG on factual queries.** Qwen3-32B achieves 0.0% hallucination without RAG, outperforming LLaMA-3.1-8B+RAG (32.7% overall) by a substantial margin. This suggests that for factual and regulatory queries, reasoning-augmented models may be more effective than RAG-augmented smaller models.

### 4.4 Combined Analysis

Figure 4 reveals a clear hierarchy of agricultural advisory reliability. Small baseline models show unacceptably high hallucination rates. RAG augmentation improves overall performance but introduces geographic confusion in temporal queries. Large models substantially reduce hallucination but retain dosage errors. Reasoning models achieve near-zero hallucination on verified knowledge queries.

This hierarchy suggests a practical deployment recommendation: agricultural advisory systems should use reasoning-augmented large models with RAG grounding specifically for dosage and temporal queries, where parametric knowledge alone is insufficient regardless of model size.""",
        1
    )
    print("Expansion 4 done")

with open('paper/agrihallubench_draft.md', 'w') as f:
    f.write(content)

words = len(content.split())
print(f"\nTotal words: {words}")
