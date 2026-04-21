import pandas as pd
import glob
import os
import json


def load_results() -> tuple[pd.DataFrame, pd.DataFrame]:
    baseline_files = sorted(glob.glob("results/eval_llama3_FULL_*.csv"))
    rag_files      = sorted(glob.glob("results/eval_rag_FULL_*.csv"))

    if not baseline_files:
        raise FileNotFoundError("Baseline results nahi mili!")
    if not rag_files:
        raise FileNotFoundError("RAG results nahi mili!")

    baseline_df = pd.read_csv(baseline_files[-1])
    rag_df      = pd.read_csv(rag_files[-1])

    print(f"Baseline : {baseline_files[-1]} ({len(baseline_df)} rows)")
    print(f"RAG      : {rag_files[-1]} ({len(rag_df)} rows)")

    return baseline_df, rag_df


def table1_overall(b: pd.DataFrame, r: pd.DataFrame) -> str:
    """Table 1 — Overall comparison"""
    b_total = len(b)
    r_total = len(r)
    b_hall  = int(b["hallucinated"].sum())
    r_hall  = int(r["hallucinated"].sum())
    b_rate  = b_hall / b_total * 100
    r_rate  = r_hall / r_total * 100
    red     = b_rate - r_rate

    lines = [
        "",
        "Table 1: Overall Hallucination Rate — Baseline vs RAG",
        "=" * 62,
        f"{'System':<25} {'Questions':>10} {'Halluc.':>10} {'Rate%':>8}",
        "-" * 55,
        f"{'Llama-3.1 (Baseline)':<25} {b_total:>10} {b_hall:>10} {b_rate:>7.1f}%",
        f"{'Llama-3.1 + RAG':<25} {r_total:>10} {r_hall:>10} {r_rate:>7.1f}%",
        "-" * 55,
        f"{'Reduction':<25} {'':>10} {'':>10} {red:>7.1f}%",
        "",
        f"Relative improvement: {(red/b_rate*100):.1f}% fewer hallucinations",
    ]
    return "\n".join(lines)


def table2_by_category(b: pd.DataFrame, r: pd.DataFrame) -> str:
    """Table 2 — By hallucination category"""
    lines = [
        "",
        "Table 2: Hallucination Rate by Category",
        "=" * 62,
        f"{'Category':<15} {'Base_N':>8} {'Base%':>8} "
        f"{'RAG_N':>8} {'RAG%':>8} {'Reduc%':>9}",
        "-" * 62,
    ]

    for cat in sorted(b["category"].unique()):
        b_cat  = b[b["category"] == cat]
        r_cat  = r[r["category"] == cat]
        b_rate = b_cat["hallucinated"].mean() * 100
        r_rate = r_cat["hallucinated"].mean() * 100 if len(r_cat) > 0 else 0
        red    = b_rate - r_rate
        lines.append(
            f"{cat:<15} {len(b_cat):>8} {b_rate:>7.1f}% "
            f"{len(r_cat):>8} {r_rate:>7.1f}% {red:>8.1f}%"
        )

    return "\n".join(lines)


def table3_by_severity(b: pd.DataFrame, r: pd.DataFrame) -> str:
    """Table 3 — By severity"""
    lines = [
        "",
        "Table 3: Hallucination Rate by Severity",
        "=" * 62,
        f"{'Severity':<12} {'Base_N':>8} {'Base%':>8} "
        f"{'RAG_N':>8} {'RAG%':>8} {'Reduc%':>9}",
        "-" * 62,
    ]

    order = ["HIGH", "MEDIUM", "LOW"]
    for sev in order:
        b_sev  = b[b["severity"] == sev]
        r_sev  = r[r["severity"] == sev]
        if len(b_sev) == 0:
            continue
        b_rate = b_sev["hallucinated"].mean() * 100
        r_rate = r_sev["hallucinated"].mean() * 100 if len(r_sev) > 0 else 0
        red    = b_rate - r_rate
        lines.append(
            f"{sev:<12} {len(b_sev):>8} {b_rate:>7.1f}% "
            f"{len(r_sev):>8} {r_rate:>7.1f}% {red:>8.1f}%"
        )

    return "\n".join(lines)


def table4_examples(b: pd.DataFrame) -> str:
    """Table 4 — Hallucination examples for paper"""
    hall = b[b["hallucinated"] == True].copy()
    hall = hall.sort_values("confidence", ascending=False)

    lines = [
        "",
        "Table 4: Representative Hallucination Examples",
        "=" * 70,
    ]

    categories = ["REGULATORY", "DOSAGE", "FACTUAL", "TEMPORAL"]
    for cat in categories:
        cat_examples = hall[hall["category"] == cat].head(1)
        if cat_examples.empty:
            continue
        row = cat_examples.iloc[0]
        lines += [
            f"\n[{cat}] Severity: {row['severity']}",
            f"Q  : {row['question'][:75]}",
            f"GT : {row['ground_truth'][:75]}",
            f"LLM: {row['llm_response'][:75]}",
            f"Why: {row['explanation'][:75]}",
        ]

    return "\n".join(lines)


def save_latex_tables(b: pd.DataFrame, r: pd.DataFrame) -> None:
    """LaTeX format — journal submission ke liye"""
    rows = []
    for cat in sorted(b["category"].unique()):
        b_cat  = b[b["category"] == cat]
        r_cat  = r[r["category"] == cat]
        b_rate = b_cat["hallucinated"].mean() * 100
        r_rate = r_cat["hallucinated"].mean() * 100 if len(r_cat) > 0 else 0
        red    = b_rate - r_rate
        rows.append(
            f"{cat} & {len(b_cat)} & {b_rate:.1f}\\% & "
            f"{len(r_cat)} & {r_rate:.1f}\\% & "
            f"\\textbf{{{red:.1f}\\%}} \\\\"
        )

    latex = "\n".join([
        "\\begin{table}[h]",
        "\\centering",
        "\\caption{Hallucination Rate: Baseline vs RAG (AgriHallu-Bench)}",
        "\\label{tab:main_results}",
        "\\begin{tabular}{lrrrrrr}",
        "\\hline",
        "Category & Base N & Base\\% & RAG N & RAG\\% & Reduction \\\\ \\hline",
        *rows,
        "\\hline",
        "\\end{tabular}",
        "\\end{table}",
    ])

    with open("results/table_latex.tex", "w") as f:
        f.write(latex)
    print("LaTeX table saved: results/table_latex.tex")


if __name__ == "__main__":
    print("=== AgriHallu-Bench — Paper Tables Generator ===\n")

    os.makedirs("results", exist_ok=True)
    b, r = load_results()

    t1 = table1_overall(b, r)
    t2 = table2_by_category(b, r)
    t3 = table3_by_severity(b, r)
    t4 = table4_examples(b)

    all_tables = "\n".join([t1, t2, t3, t4])

    print(all_tables)

    # Save karo
    with open("results/paper_tables.txt", "w") as f:
        f.write(all_tables)
    print("\nTables saved: results/paper_tables.txt")

    save_latex_tables(b, r)

    # Summary JSON bhi
    summary = {
        "baseline_hall_rate": round(b["hallucinated"].mean() * 100, 1),
        "rag_hall_rate":       round(r["hallucinated"].mean() * 100, 1),
        "reduction_pp":        round(
            (b["hallucinated"].mean() - r["hallucinated"].mean()) * 100, 1
        ),
        "total_questions":     len(b),
        "categories":          sorted(b["category"].unique().tolist()),
    }
    with open("results/final_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("Summary saved: results/final_summary.json")