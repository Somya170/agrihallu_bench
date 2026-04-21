import pandas as pd
import json
import glob
import os


def load_latest_results() -> pd.DataFrame:
    files = sorted(glob.glob("results/eval_*.csv"))
    if not files:
        raise FileNotFoundError("Koi results nahi mili!")
    latest = files[-1]
    print(f"Loading: {latest}")
    return pd.read_csv(latest)


def summary_report(df: pd.DataFrame) -> dict:
    total        = len(df)
    hallucinated = int(df["hallucinated"].sum())
    hall_rate    = round(hallucinated / total * 100, 1)

    by_category = (
        df.groupby("category")["hallucinated"]
        .agg(["sum", "count"])
        .assign(rate=lambda x: (x["sum"] / x["count"] * 100).round(1))
        .rename(columns={"sum": "hallucinated", "count": "total", "rate": "rate_%"})
        .to_dict("index")
    )

    by_severity = (
        df.groupby("severity")["hallucinated"]
        .agg(["sum", "count"])
        .assign(rate=lambda x: (x["sum"] / x["count"] * 100).round(1))
        .rename(columns={"sum": "hallucinated", "count": "total", "rate": "rate_%"})
        .to_dict("index")
    )

    # Sabse common hallucination types
    hall_df = df[df["hallucinated"] == True]
    top_types = (
        hall_df["hallucination_type"]
        .value_counts()
        .head(5)
        .to_dict()
    )

    # High confidence hallucinations — ye paper ke liye best examples hain
    high_conf = (
        hall_df[hall_df["confidence"] >= 0.8]
        [["question", "ground_truth", "llm_response",
          "explanation", "category", "severity"]]
        .to_dict("records")
    )

    report = {
        "model":              df["model"].iloc[0],
        "total_questions":    total,
        "total_hallucinated": hallucinated,
        "hallucination_rate": hall_rate,
        "by_category":        by_category,
        "by_severity":        by_severity,
        "top_hallucination_types": top_types,
        "high_confidence_examples": high_conf[:5]
    }

    return report


def print_paper_ready_stats(report: dict) -> None:
    print("\n" + "="*60)
    print("PAPER-READY STATISTICS")
    print("="*60)

    print(f"\nModel       : {report['model']}")
    print(f"Dataset     : AgriHallu-Bench v2")
    print(f"Total QA    : {report['total_questions']}")
    print(f"Hallucinated: {report['total_hallucinated']}")
    print(f"Hall. Rate  : {report['hallucination_rate']}%")

    print("\n--- Table 1: Hallucination Rate by Category ---")
    print(f"{'Category':<15} {'Total':>8} {'Halluc.':>10} {'Rate%':>8}")
    print("-" * 45)
    for cat, stats in report["by_category"].items():
        print(
            f"{cat:<15} {stats['total']:>8} "
            f"{stats['hallucinated']:>10} {stats['rate_%']:>7}%"
        )

    print("\n--- Table 2: Hallucination Rate by Severity ---")
    print(f"{'Severity':<12} {'Total':>8} {'Halluc.':>10} {'Rate%':>8}")
    print("-" * 42)
    for sev, stats in report["by_severity"].items():
        print(
            f"{sev:<12} {stats['total']:>8} "
            f"{stats['hallucinated']:>10} {stats['rate_%']:>7}%"
        )

    print("\n--- Top Hallucination Types ---")
    for htype, count in report["top_hallucination_types"].items():
        print(f"  {htype:<20} : {count}")

    print("\n--- High Confidence Examples (for paper) ---")
    for i, ex in enumerate(report["high_confidence_examples"], 1):
        print(f"\n  Example {i} [{ex['category']} / {ex['severity']}]")
        print(f"  Q   : {ex['question'][:70]}...")
        print(f"  GT  : {ex['ground_truth'][:70]}...")
        print(f"  LLM : {ex['llm_response'][:70]}...")
        print(f"  Why : {ex['explanation']}")


if __name__ == "__main__":
    df     = load_latest_results()
    report = summary_report(df)

    # JSON save karo — paper writing ke liye
    os.makedirs("results", exist_ok=True)
    with open("results/summary_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("Summary saved: results/summary_report.json")

    print_paper_ready_stats(report)