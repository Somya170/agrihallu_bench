with open('paper/agrihallubench_draft.md', 'r') as f:
    content = f.read()

if "food security" not in content:
    content = content.replace(
        "These real-world consequences motivate rigorous hallucination evaluation before deploying LLMs in agricultural advisory contexts.",
        """These real-world consequences motivate rigorous hallucination evaluation before deploying LLMs in agricultural advisory contexts. Food security implications extend beyond individual farm economics — systematic AI hallucination in agricultural advisory could contribute to regional crop failures, pesticide resistance through incorrect application guidance, and regulatory non-compliance at scale. As AI advisory tools democratize access to agronomic expertise for smallholder farmers who lack access to certified agronomists, the stakes of hallucination increase proportionally."""
    )
    print("Food security added")

if "inter-annotator" not in content:
    content = content.replace(
        "Several limitations of this work merit acknowledgment.",
        """Several limitations of this work merit acknowledgment. Our judge model (LLaMA-3.1-8B) was not validated against human expert annotations — inter-annotator agreement between the LLM judge and certified agronomists remains unmeasured. Additionally, our benchmark covers 9 state-crop combinations from a single growing season, limiting geographic and temporal generalizability."""
    )
    print("Limitations expanded")

with open('paper/agrihallubench_draft.md', 'w') as f:
    f.write(content)

words = len(content.split())
print(f"\nFinal word count: {words}")
