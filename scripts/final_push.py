with open('paper/agrihallubench_draft.md', 'r') as f:
    content = f.read()

# Abstract expand
if "261 question-answer pairs" not in content:
    content = content.replace(
        "Our benchmark comprises 236 question-answer pairs spanning four hallucination categories: Factual, Dosage, Temporal, and Regulatory.",
        """Our benchmark comprises 261 question-answer pairs spanning four hallucination categories: Factual, Dosage, Temporal, and Regulatory, constructed from verified EPA pesticide registration data and USDA National Agricultural Statistics Service 2023 crop progress reports. Unlike existing benchmarks that rely on crowdsourced or model-generated ground truth, AgriHallu-Bench ground truth is derived exclusively from official regulatory and statistical sources, enabling objective hallucination detection against verifiable facts."""
    )
    print("Abstract expanded")

# Section 3.1 taxonomy expand
if "regulatory hallucinations are highest severity" not in content:
    content = content.replace(
        "Regulatory hallucinations involve citing cancelled, restricted, or state-banned chemicals as currently approved — for example, recommending chlorpyrifos for food crop use after its EPA cancellation in August 2021.",
        """Regulatory hallucinations involve citing cancelled, restricted, or state-banned chemicals as currently approved — for example, recommending chlorpyrifos for food crop use after its EPA cancellation in August 2021. Regulatory hallucinations are highest severity in our taxonomy because they expose farmers to direct legal liability under FIFRA, which imposes civil penalties up to $25,000 per violation for use of unregistered pesticides on food crops.

These four categories reflect distinct knowledge requirements: factual hallucinations indicate gaps in agronomic domain knowledge, dosage hallucinations indicate failure to internalize specific numerical label data, temporal hallucinations indicate insufficient geographic and seasonal specificity, and regulatory hallucinations indicate knowledge currency failures where training data predates regulatory changes."""
    )
    print("Taxonomy expanded")

# Section 6 expanded recommendations
if "deployment checklist" not in content:
    content = content.replace(
        "This hierarchy suggests a practical deployment recommendation: agricultural advisory systems should use reasoning-augmented large models with RAG grounding specifically for dosage and temporal queries, where parametric knowledge alone is insufficient regardless of model size.",
        """This hierarchy suggests a practical deployment recommendation: agricultural advisory systems should use reasoning-augmented large models with RAG grounding specifically for dosage and temporal queries, where parametric knowledge alone is insufficient regardless of model size.

We propose a deployment checklist for agricultural AI systems based on our findings. First, evaluate candidate models against AgriHallu-Bench before deployment — any model exceeding 10% regulatory hallucination rate should not be deployed without RAG grounding. Second, implement geographic metadata filtering in RAG retrieval to prevent state-level confusion. Third, integrate dynamic USDA NASS API feeds for temporal queries rather than relying on static planting window knowledge. Fourth, implement mandatory abstention for queries outside the knowledge base scope rather than allowing fallback to parametric knowledge."""
    )
    print("Recommendations expanded")

with open('paper/agrihallubench_draft.md', 'w') as f:
    f.write(content)

words = len(content.split())
print(f"\nFinal word count: {words}")
