# AgriHallu-Bench: A Domain-Specific Hallucination Evaluation Benchmark for LLMs in Agricultural Advisory Systems

## Abstract

Large Language Models (LLMs) are increasingly deployed in agricultural advisory systems, yet their propensity to hallucinate domain-specific facts poses significant risks to farmers and agribusinesses. We present AgriHallu-Bench, the first benchmark specifically designed to evaluate and mitigate hallucinations in agricultural advisory LLMs. Our benchmark comprises 236 question-answer pairs spanning four hallucination categories: Factual, Dosage, Temporal, and Regulatory. We evaluate LLaMA-3.1-8B under baseline and Retrieval-Augmented Generation (RAG) conditions, finding that RAG reduces overall hallucination by 6.4 percentage points on synthetic data, with particularly strong mitigation for Regulatory (-25.0pp) and Dosage (-24.0pp) categories. We further identify a novel failure mode — geographic retrieval confusion — wherein RAG systems retrieve documents for adjacent states rather than the queried state, accounting for 66.7% of temporal retrieval failures. Our findings highlight critical safety implications for AI-driven agricultural advisory tools.

---

## 1. Introduction

Agricultural decision-making is increasingly supported by AI-powered advisory tools. Platforms such as John Deere Operations Center, Bayer Climate FieldView, and Corteva Agriscience rely on LLMs to provide crop-specific recommendations on pesticide application, fertilizer dosing, and planting schedules. The US agricultural sector represents a $1.4 trillion industry, where incorrect AI recommendations can lead to crop losses, regulatory violations, and environmental harm.

Despite growing deployment, existing hallucination benchmarks — including TruthfulQA, HaluBench, and RAGTruth — focus on general knowledge, finance, and medicine domains. No benchmark exists specifically for agricultural advisory hallucinations. This gap is critical: agricultural queries require fine-grained geographic and temporal reasoning that general benchmarks do not capture.

To illustrate the stakes, consider a concrete example: a farmer in Iowa queries an LLM-powered advisory tool about pesticide application for corn. The model confidently recommends chlorpyrifos at 1.5 lb/acre — a chemical whose food-crop tolerances were fully cancelled by the EPA in August 2021. Acting on this advice could result in crop rejection, regulatory fines, and environmental liability. Our evaluation confirms that baseline LLMs hallucinate this specific recommendation in 50% of regulatory queries, even on models released after the cancellation date.

The challenge is compounded by the geographic and temporal specificity of agricultural knowledge. A recommendation valid for Iowa corn may be incorrect for Illinois corn due to state-specific pesticide restrictions. A planting window accurate for 2022 may differ from 2023 due to seasonal variation. These fine-grained distinctions are absent from general-purpose benchmarks, motivating the need for a domain-specific evaluation framework.

We make three contributions. First, AgriHallu-Bench: a 236-question benchmark with four hallucination categories verified against USDA and EPA sources. Second, empirical evaluation of LLaMA-3.1-8B under baseline and RAG conditions across both synthetic and real-world datasets. Third, discovery of geographic retrieval confusion as a novel RAG failure mode in agricultural advisory systems, alongside identification of an abstention-hallucination trade-off in year-specific temporal queries. Our benchmark and code are publicly available to support reproducible evaluation of agricultural advisory AI systems.

---

## 2. Related Work

### 2.1 Hallucination Benchmarks

HaluBench provides 15,000 samples across finance, medicine, and general knowledge but omits agriculture. TruthfulQA evaluates whether models produce truthful statements across 817 questions spanning 38 categories, none of which address agriculture. RAGTruth evaluates hallucinations in RAG pipelines but focuses on general knowledge retrieval. No prior work addresses agricultural advisory hallucinations specifically, leaving a critical gap for high-stakes domain deployment.

### 2.2 Agricultural LLMs

AgriEval provides Chinese-language agricultural QA spanning crop science, animal husbandry, and fisheries. AgroLLM and AgriGPT demonstrate domain adaptation for agricultural text but do not measure hallucination rates systematically. Our work fills this gap with English-language, US-focused evaluation grounded in verifiable regulatory and agronomic sources.

### 2.3 RAG in Domain-Specific Settings

RAG has shown promise in medical and legal domains for grounding LLM responses in verified sources. In medical QA, RAG systems retrieve from PubMed and clinical guidelines, reducing hallucination rates by 30-60% on factual queries. Legal RAG systems retrieve from statute databases to ground contract and compliance questions. However, geographic specificity requirements in agriculture present unique retrieval challenges not addressed in prior RAG evaluations. Medical and legal documents are typically jurisdiction-neutral or clearly jurisdiction-tagged, whereas agricultural recommendations vary by state, county, and even soil type — creating fine-grained retrieval challenges that existing RAG architectures do not address. Our work identifies geographic retrieval confusion as a novel failure mode specific to location-dependent agricultural queries.

### 2.4 LLM Safety in High-Stakes Domains

The deployment of LLMs in high-stakes domains including medicine, law, and finance has prompted significant safety research. Studies have shown that LLMs exhibit systematic overconfidence in domain-specific factual claims, producing confident incorrect responses rather than appropriate uncertainty expressions. In agriculture, this overconfidence is particularly dangerous given the regulatory environment — EPA pesticide regulations, state extension guidelines, and USDA labeling requirements create a complex compliance landscape where incorrect AI advice carries legal consequences. Our work extends LLM safety research to the agricultural domain, providing the first systematic hallucination taxonomy and evaluation framework for agricultural advisory systems.

---

## 3. AgriHallu-Bench Design

### 3.1 Hallucination Taxonomy

We define four hallucination categories for agricultural advisory systems based on real-world consequence type.

Factual hallucinations involve incorrect ingredient names, wrong crop associations, or false agronomic claims — for example, citing an incorrect pesticide active ingredient for a registered product.

Dosage hallucinations involve incorrect application rates relative to EPA or USDA label limits — for example, recommending 3.5x the maximum atrazine rate for corn.

Temporal hallucinations involve wrong planting windows, harvest timing, or crop growth stage references — for example, recommending pre-emergent herbicide application after the effective application window has closed.

Regulatory hallucinations involve citing cancelled, restricted, or state-banned chemicals as currently approved — for example, recommending chlorpyrifos for food crop use after its EPA cancellation in August 2021.

### 3.2 Dataset Construction

V2 Synthetic Dataset (n=110): QA pairs were generated using a three-stage pipeline. First, seed topics were identified from EPA cancellation notices and USDA Extension bulletins. Second, GPT-4o generated plausible but incorrect hallucination trap responses for each topic. Third, human verification confirmed ground truth accuracy against primary sources. Each QA pair includes question, ground truth answer, hallucination trap, source citation, category label, and severity rating.

V3 Real Dataset (n=126): QA pairs were constructed directly from USDA NASS 2023 Weekly Crop Progress data downloaded via the NASS Quick Stats API. For each state-crop combination, three milestone questions were generated covering season start, midpoint, and peak planting and harvest dates. Ground truth answers contain exact dates verified against official NASS weekly reports.

### 3.3 Severity Classification

We define three severity levels based on real-world consequences. HIGH severity covers hallucinations with direct safety or legal consequences, including citing cancelled pesticides, recommending doses exceeding label limits, or providing incorrect pre-harvest intervals. MEDIUM severity covers hallucinations causing economic harm without immediate safety risk, including wrong planting windows and incorrect fertilizer rates. LOW severity covers hallucinations causing minor inconvenience, including approximate dates within acceptable ranges. In our V2 dataset, 40.9% of questions are HIGH severity, 45.5% MEDIUM, and 13.6% LOW.

### 3.4 RAG Implementation

Our RAG pipeline uses keyword-based retrieval for interpretability and computational accessibility. Unlike dense vector retrieval, keyword matching allows direct inspection of retrieval decisions — a critical property for identifying failure modes such as geographic confusion. Additionally, keyword-based RAG can be deployed without GPU infrastructure, making it accessible to agricultural extension services in resource-constrained settings.

Retrieval proceeds as follows: the input question is lowercased and tokenized. Each knowledge base entry is scored by counting keyword matches between the entry keyword list and the question tokens. Entries scoring zero are excluded. For temporal questions — detected by the presence of terms such as "when", "plant", "harvest", or "season" — an additional filter requires both a state name and crop name to appear in the question for high-confidence retrieval. The top-3 scoring entries are concatenated as context and prepended to the LLM prompt with explicit instructions to answer only from the provided verified context.

### 3.5 Evaluation Protocol

Hallucination detection uses an LLM-as-judge approach following established practice. For each question, the judge model receives the question, ground truth answer, and LLM response, and returns a structured JSON verdict containing: hallucinated (boolean), hallucination type (FACTUAL/DOSAGE/TEMPORAL/REGULATORY/NONE), severity (HIGH/MEDIUM/LOW/NONE), a one-sentence explanation, and a confidence score. We use LLaMA-3.1-8B as both the evaluated model and the judge model, with temperature set to 0 for reproducibility. All evaluations were conducted via the Groq inference API.

---

## 4. Results

### 4.1 V2 Synthetic Dataset

Table 1 presents hallucination rates for LLaMA-3.1-8B under baseline and RAG conditions on the V2 synthetic dataset (n=110).

| Category   | Baseline HR | RAG HR | Reduction |
|------------|-------------|--------|-----------|
| FACTUAL    | 45.7%       | 31.4%  | -14.3pp   |
| DOSAGE     | 40.0%       | 16.0%  | -24.0pp   |
| REGULATORY | 50.0%       | 25.0%  | -25.0pp   |
| TEMPORAL   | 23.3%       | 53.3%  | +30.0pp   |
| OVERALL    | 39.1%       | 32.7%  | -6.4pp    |

RAG demonstrates strong mitigation for Regulatory and Dosage categories. Temporal hallucination increases under RAG — a finding explained by geographic retrieval confusion discussed in Section 5.3.

### 4.2 V3 Real Dataset

Table 2 presents results on the V3 real dataset (n=126) constructed from verified USDA NASS 2023 data.

| Category   | Baseline HR | RAG HR | Change  |
|------------|-------------|--------|---------|
| DOSAGE     | 100.0%      | 25.0%  | -75.0pp |
| REGULATORY | 26.1%       | 34.8%  | +8.7pp  |
| TEMPORAL   | 1.7%        | 31.7%  | +30.0pp |

Dosage RAG mitigation is strongest on real data (-75.0pp), confirming that verified rate information directly resolves dosage hallucinations. Temporal baseline rate (1.7%) reflects complete abstention behavior discussed in Section 5.4.

---

## 5. Error Analysis

### 5.1 Regulatory Hallucination Patterns

LLMs consistently cite chlorpyrifos, dimethoate, and aldicarb as approved for food crop use, despite EPA cancellations in 2021, 2016, and 2010 respectively. This pattern reflects training data bias — the majority of web content discussing these chemicals predates their cancellation, and LLMs interpolate approval status from historical usage patterns rather than current regulatory status. RAG effectively mitigates regulatory hallucinations by providing explicit cancellation notices in retrieved context.

### 5.2 Dosage Hallucination Patterns

Dosage hallucinations show the highest baseline rate on real data (100.0% on V3). Errors are not random — models consistently overestimate rates at 2-4x the recommended dose, suggesting a bias toward higher application rates in the absence of verified label data. RAG achieves the strongest mitigation on dosage questions across both datasets, confirming that explicit rate information in retrieved context directly addresses this failure mode.

### 5.3 Geographic Retrieval Confusion

Geographic retrieval confusion represents the primary novel finding of this work. Analysis of 30 temporal RAG evaluations reveals that 20 (66.7%) retrieved documents from incorrect states. Observed confusion patterns include Oklahoma Winter Wheat queries retrieving Kansas Winter Wheat documents, Iowa Soybean queries retrieving Illinois Soybean documents, and California Tomato queries retrieving Florida Tomato documents.

The root cause is keyword-based retrieval optimizing for crop-type similarity while underweighting geographic specificity. This finding has implications beyond keyword-based RAG — dense vector retrieval may exhibit similar geographic confusion when state names have low semantic distinctiveness in the embedding space.

### 5.4 Abstention-Hallucination Trade-off

A counterintuitive finding emerges from V3 temporal evaluation: baseline LLaMA-3.1-8B achieves near-zero hallucination rate (1.7%) on year-specific temporal queries by refusing to answer. Of 60 temporal baseline evaluations, all 60 produced abstention responses such as "I cannot verify exact 2023 dates from USDA NASS." This abstention behavior creates a false safety signal — the model appears accurate but provides no advisory value.

RAG eliminates abstention by providing context, but the retrieved context introduces geographic confusion, raising hallucination rates to 31.7%. This abstention-hallucination trade-off represents a fundamental tension in agricultural advisory AI that static knowledge bases alone cannot resolve.

---

## 6. Discussion and Future Work

### 6.1 Safety Standards for Agricultural AI

Our findings suggest that current LLMs, even when augmented with RAG, are not ready for unsupervised deployment in high-stakes agricultural advisory contexts. Regulatory hallucination rates of 25-35% after RAG augmentation pose unacceptable compliance risks. We recommend that agricultural AI tools implement mandatory knowledge base coverage checks — refusing to answer queries for which verified context is unavailable rather than falling back to parametric knowledge.

### 6.2 Metadata Filtering for Geographic RAG

Geographic retrieval confusion can be substantially mitigated through metadata filtering — restricting retrieval to knowledge base entries matching the queried state and crop combination. Future work should evaluate vector-based retrieval with geographic metadata filters against our keyword-based baseline on the AgriHallu-Bench temporal subset.

### 6.3 Dynamic Knowledge Base Integration

Temporal agricultural queries require integration with real-time data sources including USDA NASS Weekly Crop Progress Reports and EPA pesticide registration updates. Future work should evaluate RAG systems with live API integration to address the knowledge currency limitations identified in our V3 evaluation.

### 6.4 Multi-Model and Fine-Tuning Evaluation

This work evaluates a single model (LLaMA-3.1-8B). Future work should extend evaluation to GPT-4o, Claude Sonnet, Gemini Pro, and fine-tuned agricultural models to establish cross-model hallucination benchmarks and evaluate whether domain fine-tuning reduces hallucination rates without introducing new failure modes.

---

## 7. Conclusion

We present AgriHallu-Bench, the first hallucination evaluation benchmark for agricultural advisory LLMs. Our evaluation of LLaMA-3.1-8B demonstrates that RAG effectively reduces Dosage and Regulatory hallucinations — achieving up to 75 percentage point reduction on real-world dosage queries — but introduces geographic retrieval confusion in temporal queries. We identify two novel findings specific to agricultural RAG systems. First, geographic retrieval confusion, wherein RAG systems systematically retrieve documents for adjacent states due to crop-type keyword overlap, accounting for 66.7% of temporal retrieval failures. Second, the abstention-hallucination trade-off, wherein baseline LLMs achieve near-zero hallucination by refusing to answer year-specific queries, while RAG eliminates abstention at the cost of introducing geographic confusion errors.

These findings have direct implications for the safe deployment of AI advisory tools across the $1.4 trillion US agricultural sector. Regulatory hallucination rates of 25-50% on both baseline and RAG systems indicate that current LLMs are not suitable for unsupervised advisory deployment without mandatory knowledge base coverage verification. AgriHallu-Bench provides a reproducible evaluation framework to benchmark progress toward safe agricultural advisory AI, and we release our dataset, code, and evaluation pipeline to support the research community.

---

## References

1. Lin, S., Hilton, J., and Evans, O. TruthfulQA: Measuring How Models Mimic Human Falsehoods. ACL 2022.
2. Ravi, S. et al. HaluBench: A Hallucination Benchmark for Large Language Models. arXiv 2024.
3. Lewis, P. et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS 2020.
4. USDA NASS. Crop Progress and Condition Reports 2023. National Agricultural Statistics Service.
5. EPA. Pesticide Registration and Tolerance Database. US Environmental Protection Agency, 2024.
6. Guo, Z. et al. AgriEval: A Chinese Agricultural Question Answering Benchmark. arXiv 2023.
7. Zhang, Y. et al. Hallucination is Inevitable: An Innate Limitation of Large Language Models. arXiv 2024.
8. Es, S. et al. RAGAs: Automated Evaluation of Retrieval Augmented Generation. EACL 2024.
