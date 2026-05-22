import pandas as pd
import json
import os

def get_milestone_date(df: pd.DataFrame, state: str,
                        crop_pattern: str, stage: str,
                        threshold: int = 50) -> dict:
    """
    Real NASS data se milestone date nikalo.
    Example: Iowa corn 50% planted = kab hua?
    """
    mask = (
        (df["state_name"] == state) &
        (df["short_desc"].str.contains(crop_pattern, case=False)) &
        (df["short_desc"].str.contains(stage, case=False))
    )
    subset = df[mask].copy()
    if subset.empty:
        return {}

    subset["Value"] = pd.to_numeric(subset["Value"], errors="coerce")
    subset = subset.dropna(subset=["Value"])
    subset = subset.sort_values("week_ending")

    # Threshold cross karne wala pehla date
    crossed = subset[subset["Value"] >= threshold]
    if crossed.empty:
        return {}

    row = crossed.iloc[0]

    # Peak value bhi nikalo
    peak_row  = subset.loc[subset["Value"].idxmax()]
    start_row = subset[subset["Value"] >= 10]
    start_date = start_row.iloc[0]["week_ending"] if not start_row.empty else ""

    return {
        "state":        state,
        "crop":         crop_pattern,
        "stage":        stage,
        "threshold_pct": threshold,
        "threshold_date": row["week_ending"],
        "start_date":   start_date,
        "peak_value":   int(peak_row["Value"]),
        "peak_date":    peak_row["week_ending"],
        "year":         str(row["year"]),
        "all_data":     subset[["week_ending", "Value"]].to_dict("records")
    }


def build_temporal_qa_from_nass(df: pd.DataFrame) -> list[dict]:
    """
    Real NASS data se temporal QA pairs banao.
    Har pair mein actual 2023 dates hain.
    """
    queries = [
        # Corn
        ("IOWA",        "CORN",     "PLANTED",   50, "Corn",         "Iowa"),
        ("IOWA",        "CORN",     "HARVESTED", 50, "Corn",         "Iowa"),
        ("IOWA",        "CORN",     "EMERGED",   50, "Corn",         "Iowa"),
        ("ILLINOIS",    "CORN",     "PLANTED",   50, "Corn",         "Illinois"),
        ("ILLINOIS",    "CORN",     "HARVESTED", 50, "Corn",         "Illinois"),
        ("NEBRASKA",    "CORN",     "PLANTED",   50, "Corn",         "Nebraska"),
        ("NEBRASKA",    "CORN",     "HARVESTED", 50, "Corn",         "Nebraska"),
        # Winter Wheat
        ("KANSAS",      "WINTER",   "PLANTED",   50, "Winter Wheat", "Kansas"),
        ("KANSAS",      "WINTER",   "HARVESTED", 50, "Winter Wheat", "Kansas"),
        ("KANSAS",      "WINTER",   "EMERGED",   50, "Winter Wheat", "Kansas"),
        ("OKLAHOMA",    "WINTER",   "PLANTED",   50, "Winter Wheat", "Oklahoma"),
        ("OKLAHOMA",    "WINTER",   "HARVESTED", 50, "Winter Wheat", "Oklahoma"),
        # Soybeans
        ("IOWA",        "SOYBEANS", "PLANTED",   50, "Soybeans",     "Iowa"),
        ("IOWA",        "SOYBEANS", "HARVESTED", 50, "Soybeans",     "Iowa"),
        ("ILLINOIS",    "SOYBEANS", "PLANTED",   50, "Soybeans",     "Illinois"),
        ("ILLINOIS",    "SOYBEANS", "HARVESTED", 50, "Soybeans",     "Illinois"),
        # Cotton
        ("MISSISSIPPI", "COTTON",   "PLANTED",   50, "Cotton",       "Mississippi"),
        ("MISSISSIPPI", "COTTON",   "HARVESTED", 50, "Cotton",       "Mississippi"),
        # Potatoes
        ("IDAHO",       "POTATOES", "PLANTED",   50, "Potatoes",     "Idaho"),
        ("IDAHO",       "POTATOES", "HARVESTED", 50, "Potatoes",     "Idaho"),
    ]

    qa_pairs = []

    for state, crop_pat, stage, threshold, crop_name, state_name in queries:
        info = get_milestone_date(df, state, crop_pat, stage, threshold)
        if not info:
            print(f"  No data: {state} {crop_name} {stage}")
            continue

        year        = info["year"]
        thresh_date = info["threshold_date"]
        start_date  = info["start_date"]
        peak_val    = info["peak_value"]
        peak_date   = info["peak_date"]

        qid = f"NASS_{state}_{crop_pat}_{stage}".replace(" ", "_")

        # Q1 — 50% milestone date
        qa_pairs.append({
            "id":       f"{qid}_50pct",
            "category": "TEMPORAL",
            "severity": "MEDIUM",
            "question": (
                f"According to USDA NASS 2023 data, by what date "
                f"was 50% of {crop_name} crop {stage.lower()} "
                f"in {state_name}?"
            ),
            "ground_truth": (
                f"According to USDA NASS 2023 weekly crop progress, "
                f"50% of {crop_name} in {state_name} was "
                f"{stage.lower()} by {thresh_date}. "
                f"Activity started around {start_date}."
            ),
            "hallucination_trap": (
                f"LLMs often give approximate national averages "
                f"instead of actual {year} {state_name} data."
            ),
            "source":   "USDA_NASS_2023_REAL",
            "verified": True,
            "raw_data": info["all_data"][:5]
        })

        # Q2 — Season start question
        if start_date:
            qa_pairs.append({
                "id":       f"{qid}_start",
                "category": "TEMPORAL",
                "severity": "MEDIUM",
                "question": (
                    f"When did {crop_name} {stage.lower()} begin "
                    f"in {state_name} during the 2023 season, "
                    f"according to USDA NASS?"
                ),
                "ground_truth": (
                    f"USDA NASS 2023 data shows {crop_name} "
                    f"{stage.lower()} in {state_name} reached 10% "
                    f"by {start_date}, indicating season start. "
                    f"Reached 50% by {thresh_date}."
                ),
                "hallucination_trap": (
                    f"LLMs often confuse {stage.lower()} start "
                    f"dates across different states and years."
                ),
                "source":   "USDA_NASS_2023_REAL",
                "verified": True,
                "raw_data": info["all_data"][:3]
            })

        # Q3 — Peak/completion question
        qa_pairs.append({
            "id":       f"{qid}_peak",
            "category": "TEMPORAL",
            "severity": "LOW",
            "question": (
                f"What was the peak {stage.lower()} percentage "
                f"for {crop_name} in {state_name} in 2023, "
                f"and when was it reached?"
            ),
            "ground_truth": (
                f"USDA NASS 2023: {crop_name} in {state_name} "
                f"reached peak {stage.lower()} of {peak_val}% "
                f"by {peak_date}."
            ),
            "hallucination_trap": (
                f"LLMs cannot know exact weekly NASS "
                f"statistics for {year}."
            ),
            "source":   "USDA_NASS_2023_REAL",
            "verified": True,
            "raw_data": []
        })

    return qa_pairs


def build_pesticide_qa_from_pubchem(
    pubchem_path: str
) -> list[dict]:
    """
    PubChem data + EPA known actions se QA pairs banao.
    """
    # EPA actions — verified public record
    epa_actions = {
        "Chlorpyrifos": {
            "status":    "CANCELLED",
            "action":    "EPA cancelled all food tolerances August 2021",
            "crops":     ["corn", "apples", "citrus", "soybeans"],
            "year":      2021
        },
        "Carbofuran": {
            "status":    "CANCELLED",
            "action":    "EPA revoked all food tolerances 2009",
            "crops":     ["corn", "rice", "potatoes"],
            "year":      2009
        },
        "Aldicarb": {
            "status":    "CANCELLED",
            "action":    "Voluntarily cancelled by Bayer CropScience 2010",
            "crops":     ["citrus", "potatoes", "cotton"],
            "year":      2010
        },
        "Dimethoate": {
            "status":    "CANCELLED",
            "action":    "EPA cancelled blueberry tolerance 2016",
            "crops":     ["blueberries"],
            "year":      2016
        },
        "Methyl parathion": {
            "status":    "CANCELLED",
            "action":    "All food uses cancelled by EPA 2003",
            "crops":     ["wheat", "corn"],
            "year":      2003
        },
        "Glyphosate": {
            "status":    "APPROVED",
            "action":    "Approved, pre-harvest use on wheat 30 ppm MRL",
            "crops":     ["wheat", "soybeans", "corn"],
            "year":      None,
            "mrl_ppm":   30.0
        },
        "Atrazine": {
            "status":    "APPROVED",
            "action":    "Approved pre-emergent herbicide for corn",
            "crops":     ["corn", "sorghum"],
            "year":      None,
            "mrl_ppm":   0.1
        },
        "Paraquat": {
            "status":    "RESTRICTED",
            "action":    "Restricted Use Pesticide, certified applicator required",
            "crops":     ["soybeans", "cotton"],
            "year":      None,
            "mrl_ppm":   0.05
        },
        "Dicamba": {
            "status":    "APPROVED",
            "action":    "Approved for dicamba-tolerant soybean varieties",
            "crops":     ["soybeans"],
            "year":      None,
            "mrl_ppm":   0.1
        },
        "2,4-D": {
            "status":    "APPROVED",
            "action":    "Approved herbicide for broadleaf weed control",
            "crops":     ["wheat", "corn"],
            "year":      None,
            "mrl_ppm":   2.0
        },
    }

    qa_pairs = []

    try:
        pubchem_df = pd.read_csv(pubchem_path)
    except Exception:
        pubchem_df = pd.DataFrame()

    for pesticide, epa in epa_actions.items():
        status   = epa["status"]
        action   = epa["action"]
        crops    = epa["crops"]
        mrl      = epa.get("mrl_ppm", "N/A")

        # PubChem se molecular formula lo agar available
        formula = ""
        if not pubchem_df.empty:
            match = pubchem_df[
                pubchem_df["pesticide_name"] == pesticide
            ]
            if not match.empty:
                formula = match.iloc[0].get(
                    "molecular_formula", ""
                )

        for crop in crops:
            pid = f"{pesticide}_{crop}".replace(" ", "_")

            # Q1 — Current legal status
            qa_pairs.append({
                "id":       f"REG_{pid}",
                "category": "REGULATORY",
                "severity": "HIGH",
                "question": (
                    f"Is {pesticide} currently approved by the "
                    f"EPA for use on {crop} in the United States?"
                ),
                "ground_truth": (
                    f"{pesticide} is {status} for {crop} use. "
                    f"{action}. "
                    f"{'MRL: ' + str(mrl) + ' ppm.' if mrl != 'N/A' else 'No tolerance exists.'}"
                    f"{' Formula: ' + formula if formula else ''}"
                ),
                "hallucination_trap": (
                    f"LLMs trained before {epa.get('year', 'recent')} "
                    f"EPA action may incorrectly report {pesticide} "
                    f"as still approved for {crop}."
                ),
                "source":   "EPA_PUBLIC_RECORD",
                "verified": True
            })

            # Q2 — MRL question (agar approved hai)
            if status == "APPROVED" and mrl != "N/A":
                qa_pairs.append({
                    "id":       f"DOS_{pid}",
                    "category": "DOSAGE",
                    "severity": "HIGH",
                    "question": (
                        f"What is the EPA maximum residue limit "
                        f"(MRL) for {pesticide} on {crop}?"
                    ),
                    "ground_truth": (
                        f"EPA MRL for {pesticide} on {crop} is "
                        f"{mrl} ppm. Status: {status}. {action}."
                    ),
                    "hallucination_trap": (
                        f"LLMs often fabricate or confuse MRL "
                        f"values for {pesticide} on {crop}."
                    ),
                    "source":   "EPA_PUBLIC_RECORD",
                    "verified": True
                })

    return qa_pairs


if __name__ == "__main__":
    os.makedirs("datasets", exist_ok=True)

    print("=" * 55)
    print("AgriHallu-Bench — Real Data QA Builder")
    print("=" * 55)

    # 1. NASS real data se temporal QA
    print("\n[1] Building TEMPORAL QA from real NASS 2023 data...")
    nass_df = pd.read_csv("data/raw/nass_crop_progress.csv")
    temporal_qa = build_temporal_qa_from_nass(nass_df)
    print(f"    Generated: {len(temporal_qa)} temporal QA pairs")

    # 2. EPA/PubChem se regulatory + dosage QA
    print("\n[2] Building REGULATORY/DOSAGE QA from EPA records...")
    pesticide_qa = build_pesticide_qa_from_pubchem(
        "data/raw/pesticides_pubchem.csv"
    )
    print(f"    Generated: {len(pesticide_qa)} pesticide QA pairs")

    # Combine
    all_qa = temporal_qa + pesticide_qa

    # raw_data field remove karo JSON se (size kam karo)
    for qa in all_qa:
        qa.pop("raw_data", None)

    print(f"\nTotal QA pairs: {len(all_qa)}")

    # Save
    df = pd.DataFrame(all_qa)

    with open("datasets/agrihallu_v3_real.json", "w") as f:
        json.dump(all_qa, f, indent=2)

    df.to_csv("datasets/agrihallu_v3_real.csv", index=False)

    print("\nCategory breakdown:")
    print(df["category"].value_counts().to_string())
    print("\nSeverity breakdown:")
    print(df["severity"].value_counts().to_string())
    print("\nSource breakdown:")
    print(df["source"].value_counts().to_string())
    print("\nVerified data only:")
    print(df["verified"].value_counts().to_string())

    print("\nSaved:")
    print("  datasets/agrihallu_v3_real.json")
    print("  datasets/agrihallu_v3_real.csv")

    # Sample dikhaao
    print("\nSample QA (real NASS data):")
    nass_samples = [q for q in all_qa if "NASS" in q["source"]]
    if nass_samples:
        import json as j
        print(j.dumps(nass_samples[0], indent=2))