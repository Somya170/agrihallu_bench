# AgriHallu-Bench — Key Findings

## Dataset
- V2 Synthetic: 110 QA pairs (FACTUAL, DOSAGE, TEMPORAL, REGULATORY)
- V3 Real NASS: 126 QA pairs (verified USDA 2023 data)

## Main Results (V2 — Primary Findings)
| Category   | Baseline | RAG   | Reduction |
|------------|----------|-------|-----------|
| FACTUAL    | 45.7%    | 31.4% | -14.3pp   |
| DOSAGE     | 40.0%    | 16.0% | -24.0pp   |
| REGULATORY | 50.0%    | 25.0% | -25.0pp   |
| TEMPORAL   | 23.3%    | 53.3% | +30.0pp * |
| OVERALL    | 39.1%    | 32.7% | -6.4pp    |

## Novel Finding — Geographic Retrieval Failure
- 66.7% temporal failures = wrong state document retrieved
- RAG retrieves Iowa doc for Oklahoma question
- Solution: metadata filtering by state+crop

## V3 Limitation
- Baseline abstention rate 100% on temporal
- RAG forces answer but judge marks partial answers as hallucination
- Finding: LLMs need dynamic real-time NASS data, not static KB
