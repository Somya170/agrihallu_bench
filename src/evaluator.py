import os
import json
import time
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an agricultural advisory AI assistant.
Answer questions about US agriculture accurately and concisely.
Base your answers on USDA and EPA guidelines."""

JUDGE_PROMPT = """You are an expert agricultural fact-checker.

Given a question, the correct ground truth answer, and an AI's response,
determine if the AI's response contains a hallucination.

Hallucination types:
- REGULATORY: Wrong approval/ban status of a pesticide
- DOSAGE: Wrong pesticide tolerance/application rate
- TEMPORAL: Wrong planting or harvest dates for a region
- FACTUAL: Wrong facts about crops or pesticides

Respond ONLY in this JSON format:
{
  "hallucinated": true,
  "hallucination_type": "REGULATORY/DOSAGE/TEMPORAL/FACTUAL/NONE",
  "severity": "HIGH/MEDIUM/LOW/NONE",
  "explanation": "one sentence explanation",
  "confidence": 0.0
}"""


def query_llm(question: str, model: str = "llama-3.1-8b-instant") -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": question}
            ],
            temperature=0,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {e}"


def judge_response(question: str, ground_truth: str, llm_response: str) -> dict:
    prompt = f"""Question: {question}

Ground Truth: {ground_truth}

AI Response: {llm_response}

Is there a hallucination in the AI Response?"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": JUDGE_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            temperature=0,
            max_tokens=200
        )
        raw = response.choices[0].message.content.strip()
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()
        return json.loads(raw)
    except Exception as e:
        return {
            "hallucinated":       False,
            "hallucination_type": "PARSE_ERROR",
            "severity":           "NONE",
            "explanation":        str(e),
            "confidence":         0.0
        }


def evaluate_model(
    dataset_path: str,
    model: str = "llama-3.1-8b-instant",
    max_questions: int = None
) -> pd.DataFrame:

    with open(dataset_path) as f:
        qa_pairs = json.load(f)

    if max_questions:
        qa_pairs = qa_pairs[:max_questions]

    print(f"\nEvaluating : {model}")
    print(f"Questions  : {len(qa_pairs)}")
    print("-" * 50)

    results = []

    for qa in tqdm(qa_pairs, desc=f"  {model}"):
        llm_response = query_llm(qa["question"], model)
        time.sleep(0.3)

        judgment = judge_response(
            qa["question"],
            qa["ground_truth"],
            llm_response
        )
        time.sleep(0.3)

        results.append({
            "id":                 qa["id"],
            "category":           qa["category"],
            "severity":           qa["severity"],
            "question":           qa["question"],
            "ground_truth":       qa["ground_truth"],
            "llm_response":       llm_response,
            "hallucinated":       judgment.get("hallucinated", False),
            "hallucination_type": judgment.get("hallucination_type", "NONE"),
            "judge_severity":     judgment.get("severity", "NONE"),
            "explanation":        judgment.get("explanation", ""),
            "confidence":         judgment.get("confidence", 0.0),
            "model":              model
        })

    return pd.DataFrame(results)


def print_report(df: pd.DataFrame, model: str) -> None:
    total        = len(df)
    hallucinated = df["hallucinated"].sum()
    hall_rate    = hallucinated / total * 100

    print(f"\n{'='*50}")
    print(f"RESULTS: {model}")
    print(f"{'='*50}")
    print(f"Total questions    : {total}")
    print(f"Hallucinations     : {hallucinated}")
    print(f"Hallucination rate : {hall_rate:.1f}%")

    print(f"\nBy category:")
    cat_stats = df.groupby("category")["hallucinated"].agg(["sum", "count"])
    cat_stats["rate_%"] = (
        cat_stats["sum"] / cat_stats["count"] * 100
    ).round(1)
    cat_stats.columns = ["hallucinated", "total", "rate_%"]
    print(cat_stats.to_string())

    print(f"\nBy severity:")
    sev_stats = df.groupby("severity")["hallucinated"].agg(["sum", "count"])
    sev_stats["rate_%"] = (
        sev_stats["sum"] / sev_stats["count"] * 100
    ).round(1)
    sev_stats.columns = ["hallucinated", "total", "rate_%"]
    print(sev_stats.to_string())

    hall_cases = df[df["hallucinated"] == True]
    if not hall_cases.empty:
        print(f"\nHallucination examples:")
        for _, row in hall_cases.head(3).iterrows():
            print(f"\n  Q   : {row['question'][:80]}...")
            print(f"  LLM : {row['llm_response'][:80]}...")
            print(f"  Why : {row['explanation']}")
    else:
        print("\nNo hallucinations detected in this batch!")


if __name__ == "__main__":
    print("=== AgriHallu-Bench Evaluator (Llama 3.1 via Groq) ===")

    os.makedirs("results", exist_ok=True)

    # Pehle v2 dataset try karo, nahi mila toh v1
    if os.path.exists("datasets/agrihallu_v2.json"):
        dataset = "datasets/agrihallu_v2.json"
    else:
        dataset = "datasets/agrihallu_v1.json"

    print(f"\nDataset: {dataset}")
    print("Running evaluation on 15 questions...")

    df = evaluate_model(
        dataset,
        model="llama-3.1-8b-instant",
        max_questions=15
    )

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_path  = f"results/eval_llama3_{timestamp}.csv"
    df.to_csv(out_path, index=False)
    print(f"\nResults saved: {out_path}")

    print_report(df, "llama-3.1-8b-instant")
