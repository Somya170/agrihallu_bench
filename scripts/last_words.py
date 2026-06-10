with open('paper/agrihallubench_draft.md', 'r') as f:
    content = f.read()

# Intro expand
if "precision agriculture market" not in content:
    content = content.replace(
        "The US agricultural sector represents a $1.4 trillion industry, where incorrect AI recommendations can lead to crop losses, regulatory violations, and environmental harm.",
        """The US agricultural sector represents a $1.4 trillion industry, where incorrect AI recommendations can lead to crop losses, regulatory violations, and environmental harm. The precision agriculture market alone is projected to reach $12.8 billion by 2027, with LLM-powered advisory tools constituting a growing segment. Major platforms including John Deere Operations Center, Bayer Climate FieldView, and Corteva Agriscience are actively integrating conversational AI features — making hallucination safety evaluation an urgent research priority."""
    )
    print("Intro expanded")

# Related work expand
if "BioASQ" not in content:
    content = content.replace(
        "No prior work addresses agricultural advisory hallucinations specifically, leaving a critical gap for high-stakes domain deployment. Table 1 summarizes the comparison between AgriHallu-Bench and existing benchmarks across five dimensions: domain coverage, geographic specificity, regulatory grounding, real-world data integration, and RAG evaluation.",
        """No prior work addresses agricultural advisory hallucinations specifically, leaving a critical gap for high-stakes domain deployment. Domain-specific benchmarks exist for medicine (BioASQ, MedQA), law (LegalBench), and finance (FinQA) — but agriculture remains unaddressed despite its comparable economic scale and regulatory complexity. Table 1 summarizes the comparison between AgriHallu-Bench and existing benchmarks across five dimensions: domain coverage, geographic specificity, regulatory grounding, real-world data integration, and RAG evaluation."""
    )
    print("Related work expanded")

# Error analysis expand
if "false negative rate" not in content:
    content = content.replace(
        "This abstention behavior creates a false safety signal — the model appears accurate but provides no advisory value.",
        """This abstention behavior creates a false safety signal — the model appears accurate but provides no advisory value. We term this phenomenon pseudo-safety: a model that refuses all queries in a category will achieve 0% hallucination rate while being entirely useless. Evaluation frameworks that report only hallucination rate without abstention rate will systematically overestimate model reliability on year-specific agricultural queries. Future hallucination benchmarks should report both hallucination rate and response rate as complementary metrics."""
    )
    print("Error analysis expanded")

with open('paper/agrihallubench_draft.md', 'w') as f:
    f.write(content)

words = len(content.split())
print(f"\nFinal word count: {words}")
