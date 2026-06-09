# AgriHallu-Bench

A domain-specific hallucination evaluation benchmark for LLMs in agricultural advisory systems.

## Dataset
- V2 Synthetic: 135 QA pairs (FACTUAL, DOSAGE, TEMPORAL, REGULATORY)
- V3 Real: 126 QA pairs (USDA NASS 2023 verified)

## Models Evaluated
| Model | Overall HR |
|-------|-----------|
| LLaMA-3.1-8B | 39.1% |
| LLaMA-3.3-70B | 9.1% |
| LLaMA-4-Scout | 4.5% |
| Qwen3-32B | 0.0% |

## Key Findings
- Geographic retrieval confusion — 66.7% temporal RAG failures
- Reasoning models achieve near-zero hallucination
- Dosage hallucination most persistent across model sizes

## Setup
```bash
pip install -r requirements.txt
cp .env.example .env  # Add GROQ_API_KEY
python src/evaluator.py
```

## Citation
Coming soon — paper under review
