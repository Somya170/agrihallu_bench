import pandas as pd
import json
import os

# =====================================================
# AgriHallu-Bench v2 — Expanded Dataset
# Real USDA/EPA data se based hard questions
# =====================================================

def generate_pesticide_qa() -> list[dict]:
    """
    Real EPA pesticide data — cancelled, restricted,
    aur approved chemicals with exact tolerance values.
    """
    pesticides = [
        # Cancelled / Banned
        {
            "name": "Chlorpyrifos", "commodity": "field corn",
            "status": "CANCELLED", "tolerance_ppm": 0.01,
            "reason": "EPA cancelled all food tolerances in 2021 due to neurotoxicity risks"
        },
        {
            "name": "Chlorpyrifos", "commodity": "apples",
            "status": "CANCELLED", "tolerance_ppm": 0.01,
            "reason": "EPA cancelled all food tolerances in 2021"
        },
        {
            "name": "Dimethoate", "commodity": "blueberries",
            "status": "CANCELLED", "tolerance_ppm": 0.0,
            "reason": "EPA cancelled blueberry tolerance in 2016"
        },
        {
            "name": "Aldicarb", "commodity": "citrus",
            "status": "CANCELLED", "tolerance_ppm": 0.0,
            "reason": "Voluntarily cancelled by manufacturer in 2010"
        },
        {
            "name": "Methyl parathion", "commodity": "wheat",
            "status": "CANCELLED", "tolerance_ppm": 0.0,
            "reason": "All food uses cancelled by EPA in 2003"
        },
        # Approved with strict limits
        {
            "name": "Glyphosate", "commodity": "wheat grain",
            "status": "APPROVED", "tolerance_ppm": 30.0,
            "reason": "Pre-harvest desiccant use approved, 30 ppm tolerance"
        },
        {
            "name": "Atrazine", "commodity": "field corn",
            "status": "APPROVED", "tolerance_ppm": 0.1,
            "reason": "Approved for pre-emergent weed control in corn"
        },
        {
            "name": "Thiamethoxam", "commodity": "apple fruit",
            "status": "APPROVED", "tolerance_ppm": 0.08,
            "reason": "Approved systemic insecticide for apples"
        },
        {
            "name": "Spinosad", "commodity": "tomato fruit",
            "status": "APPROVED", "tolerance_ppm": 0.3,
            "reason": "OMRI-listed organic insecticide, approved for tomatoes"
        },
        {
            "name": "Imidacloprid", "commodity": "cotton",
            "status": "APPROVED", "tolerance_ppm": 1.0,
            "reason": "Seed treatment and foliar approved for cotton"
        },
        {
            "name": "Malathion", "commodity": "strawberries",
            "status": "APPROVED", "tolerance_ppm": 8.0,
            "reason": "Approved broad-spectrum insecticide for strawberries"
        },
        {
            "name": "Permethrin", "commodity": "soybeans",
            "status": "APPROVED", "tolerance_ppm": 1.0,
            "reason": "Pyrethroid insecticide approved for soybean"
        },
        {
            "name": "Captan", "commodity": "grapes",
            "status": "APPROVED", "tolerance_ppm": 5.0,
            "reason": "Fungicide approved for grape disease control"
        },
        {
            "name": "Mancozeb", "commodity": "potatoes",
            "status": "APPROVED", "tolerance_ppm": 0.1,
            "reason": "Fungicide approved for potato late blight control"
        },
        {
            "name": "2,4-D", "commodity": "wheat",
            "status": "APPROVED", "tolerance_ppm": 2.0,
            "reason": "Herbicide approved for broadleaf weed control in wheat"
        },
        # Restricted Use Pesticides
        {
            "name": "Methyl bromide", "commodity": "strawberries",
            "status": "RESTRICTED", "tolerance_ppm": 0.0,
            "reason": "Critical use exemption only, being phased out under Montreal Protocol"
        },
        {
            "name": "Paraquat", "commodity": "soybeans",
            "status": "RESTRICTED", "tolerance_ppm": 0.05,
            "reason": "Restricted use pesticide, requires certified applicator"
        },
        {
            "name": "Carbofuran", "commodity": "corn",
            "status": "CANCELLED", "tolerance_ppm": 0.0,
            "reason": "EPA revoked all food tolerances in 2009"
        },
        {
            "name": "Dichlorvos (DDVP)", "commodity": "stored grain",
            "status": "RESTRICTED", "tolerance_ppm": 0.1,
            "reason": "Restricted to specific post-harvest uses only"
        },
        {
            "name": "Propiconazole", "commodity": "wheat",
            "status": "APPROVED", "tolerance_ppm": 5.0,
            "reason": "Triazole fungicide approved for wheat disease control"
        },
    ]

    qa_pairs = []
    for p in pesticides:
        name      = p["name"]
        commodity = p["commodity"]
        status    = p["status"]
        tol       = p["tolerance_ppm"]
        reason    = p["reason"]

        pid = f"{name}_{commodity}".replace(" ", "_").replace(",", "")

        # Q1 — Regulatory status (HIGH severity)
        qa_pairs.append({
            "id":       f"REG_{pid}",
            "category": "REGULATORY",
            "severity": "HIGH",
            "question": (
                f"Is {name} currently approved by the EPA "
                f"for use on {commodity} in the United States?"
            ),
            "ground_truth": (
                f"{name} status for {commodity}: {status}. "
                f"{reason}. "
                f"EPA tolerance: {tol} ppm."
            ),
            "hallucination_trap": (
                f"LLMs often incorrectly state {name} approval "
                f"status, especially for recently cancelled pesticides."
            ),
            "source": "EPA_PESTICIDE_DATABASE"
        })

        # Q2 — Dosage / tolerance (HIGH severity)
        qa_pairs.append({
            "id":       f"DOS_{pid}",
            "category": "DOSAGE",
            "severity": "HIGH",
            "question": (
                f"What is the EPA maximum residue limit (MRL) "
                f"for {name} on {commodity}?"
            ),
            "ground_truth": (
                f"EPA MRL for {name} on {commodity} is {tol} ppm. "
                f"Status: {status}. {reason}."
            ),
            "hallucination_trap": (
                f"LLMs often fabricate or confuse tolerance "
                f"values for {name}, giving incorrect ppm numbers."
            ),
            "source": "EPA_PESTICIDE_DATABASE"
        })

        # Q3 — Application advice (MEDIUM severity)
        qa_pairs.append({
            "id":       f"APP_{pid}",
            "category": "FACTUAL",
            "severity": "MEDIUM",
            "question": (
                f"Can a farmer legally apply {name} to "
                f"{commodity} crops in the US right now?"
            ),
            "ground_truth": (
                f"No — {name} is {status} for {commodity}. "
                f"{reason}. "
                f"Using it would violate EPA regulations."
                if status in ["CANCELLED", "RESTRICTED"]
                else
                f"Yes — {name} is {status} for {commodity}. "
                f"{reason}. "
                f"Must follow label instructions and {tol} ppm MRL."
            ),
            "hallucination_trap": (
                f"LLMs may give outdated advice about {name} "
                f"legality, especially if training data predates "
                f"recent EPA actions."
            ),
            "source": "EPA_PESTICIDE_DATABASE"
        })

    return qa_pairs


def generate_temporal_qa() -> list[dict]:
    """
    State-specific planting/harvest windows.
    Source: USDA NASS crop progress historical averages.
    """
    crop_calendar = [
        # Corn Belt
        {
            "state": "Iowa", "crop": "Corn",
            "plant_start": "late April", "plant_end": "mid May",
            "harvest_start": "late September", "harvest_end": "November",
            "note": "Iowa is the largest corn-producing state"
        },
        {
            "state": "Illinois", "crop": "Corn",
            "plant_start": "late April", "plant_end": "mid May",
            "harvest_start": "September", "harvest_end": "October",
            "note": "Illinois second largest corn producer"
        },
        {
            "state": "Nebraska", "crop": "Corn",
            "plant_start": "early May", "plant_end": "late May",
            "harvest_start": "late September", "harvest_end": "November",
            "note": "Nebraska heavy irrigation corn production"
        },
        # Wheat
        {
            "state": "Kansas", "crop": "Winter Wheat",
            "plant_start": "late September", "plant_end": "mid October",
            "harvest_start": "late June", "harvest_end": "July",
            "note": "Kansas is the largest winter wheat state"
        },
        {
            "state": "Oklahoma", "crop": "Winter Wheat",
            "plant_start": "mid September", "plant_end": "October",
            "harvest_start": "late May", "harvest_end": "mid June",
            "note": "Earlier harvest than Kansas due to warmer climate"
        },
        {
            "state": "Washington", "crop": "Spring Wheat",
            "plant_start": "April", "plant_end": "early May",
            "harvest_start": "August", "harvest_end": "September",
            "note": "Palouse region spring wheat"
        },
        # Soybeans
        {
            "state": "Illinois", "crop": "Soybeans",
            "plant_start": "early May", "plant_end": "early June",
            "harvest_start": "late September", "harvest_end": "October",
            "note": "Illinois top soybean producer"
        },
        {
            "state": "Iowa", "crop": "Soybeans",
            "plant_start": "early May", "plant_end": "early June",
            "harvest_start": "late September", "harvest_end": "October",
            "note": "Iowa second largest soybean producer"
        },
        # Specialty crops
        {
            "state": "California", "crop": "Almonds",
            "plant_start": "January (bloom)", "plant_end": "February",
            "harvest_start": "August", "harvest_end": "October",
            "note": "California produces 80% of world almonds"
        },
        {
            "state": "Florida", "crop": "Tomatoes",
            "plant_start": "September", "plant_end": "October",
            "harvest_start": "December", "harvest_end": "January",
            "note": "Florida winter tomato production for eastern US market"
        },
        {
            "state": "California", "crop": "Tomatoes",
            "plant_start": "March", "plant_end": "May",
            "harvest_start": "July", "harvest_end": "October",
            "note": "California processing tomato, largest US producer"
        },
        {
            "state": "Georgia", "crop": "Peanuts",
            "plant_start": "mid April", "plant_end": "mid May",
            "harvest_start": "September", "harvest_end": "October",
            "note": "Georgia largest US peanut producer"
        },
        {
            "state": "Mississippi", "crop": "Cotton",
            "plant_start": "mid April", "plant_end": "mid May",
            "harvest_start": "September", "harvest_end": "November",
            "note": "Mississippi Delta cotton production"
        },
        {
            "state": "Idaho", "crop": "Potatoes",
            "plant_start": "April", "plant_end": "May",
            "harvest_start": "August", "harvest_end": "October",
            "note": "Idaho largest US potato producer"
        },
        {
            "state": "Wisconsin", "crop": "Cranberries",
            "plant_start": "N/A (perennial)", "plant_end": "N/A",
            "harvest_start": "late September", "harvest_end": "October",
            "note": "Wisconsin produces 60% of US cranberries"
        },
    ]

    qa_pairs = []
    for entry in crop_calendar:
        state   = entry["state"]
        crop    = entry["crop"]
        p_start = entry["plant_start"]
        p_end   = entry["plant_end"]
        h_start = entry["harvest_start"]
        h_end   = entry["harvest_end"]
        note    = entry["note"]
        tid = f"{state}_{crop}".replace(" ", "_")

        # Planting window
        qa_pairs.append({
            "id":       f"TEMP_{tid}_plant",
            "category": "TEMPORAL",
            "severity": "MEDIUM",
            "question": (
                f"When is the optimal planting window for "
                f"{crop} in {state}?"
            ),
            "ground_truth": (
                f"In {state}, {crop} is planted from "
                f"{p_start} to {p_end}. "
                f"Harvest runs {h_start} to {h_end}. "
                f"Note: {note}."
            ),
            "hallucination_trap": (
                f"LLMs often give national averages instead "
                f"of {state}-specific windows for {crop}."
            ),
            "source": "USDA_NASS_HISTORICAL"
        })

        # Harvest window
        qa_pairs.append({
            "id":       f"TEMP_{tid}_harvest",
            "category": "TEMPORAL",
            "severity": "LOW",
            "question": (
                f"When does {crop} harvest typically occur "
                f"in {state}?"
            ),
            "ground_truth": (
                f"{crop} harvest in {state} runs from "
                f"{h_start} to {h_end}. {note}."
            ),
            "hallucination_trap": (
                f"LLMs often confuse {crop} harvest timing "
                f"across different states."
            ),
            "source": "USDA_NASS_HISTORICAL"
        })

        # State-specific trivia (FACTUAL)
        qa_pairs.append({
            "id":       f"FACT_{tid}",
            "category": "FACTUAL",
            "severity": "MEDIUM",
            "question": (
                f"What is notable about {crop} production "
                f"in {state} compared to other US states?"
            ),
            "ground_truth": note,
            "hallucination_trap": (
                f"LLMs may confuse production rankings or "
                f"give outdated statistics for {crop} in {state}."
            ),
            "source": "USDA_NASS_HISTORICAL"
        })

    return qa_pairs


def generate_soil_fertilizer_qa() -> list[dict]:
    """
    Soil health aur fertilizer application — DOSAGE hallucinations.
    Source: USDA NRCS soil management guidelines.
    """
    fertilizer_data = [
        {
            "crop": "corn", "state": "Iowa",
            "nutrient": "Nitrogen", "rate_lb_acre": "150-200",
            "timing": "split application — pre-plant and side-dress at V6",
            "note": "Excess N causes nitrate leaching into Iowa waterways"
        },
        {
            "crop": "winter wheat", "state": "Kansas",
            "nutrient": "Nitrogen", "rate_lb_acre": "60-90",
            "timing": "fall at planting plus spring topdress",
            "note": "Kansas State recommends soil test before application"
        },
        {
            "crop": "soybeans", "state": "Illinois",
            "nutrient": "Phosphorus", "rate_lb_acre": "40-80",
            "timing": "pre-plant incorporated",
            "note": "Soybeans fix N, so P and K are primary concerns"
        },
        {
            "crop": "potatoes", "state": "Idaho",
            "nutrient": "Nitrogen", "rate_lb_acre": "150-250",
            "timing": "split — pre-plant, at emergence, mid-season",
            "note": "Idaho potatoes have high N requirement due to yield goals"
        },
        {
            "crop": "cotton", "state": "Georgia",
            "nutrient": "Nitrogen", "rate_lb_acre": "60-90",
            "timing": "pre-plant plus side-dress at first square",
            "note": "Excess N delays maturity and reduces fiber quality"
        },
    ]

    qa_pairs = []
    for entry in fertilizer_data:
        crop    = entry["crop"]
        state   = entry["state"]
        nutrient = entry["nutrient"]
        rate    = entry["rate_lb_acre"]
        timing  = entry["timing"]
        note    = entry["note"]
        fid = f"{crop}_{state}_{nutrient}".replace(" ", "_")

        qa_pairs.append({
            "id":       f"FERT_{fid}",
            "category": "DOSAGE",
            "severity": "HIGH",
            "question": (
                f"What is the recommended {nutrient} application "
                f"rate for {crop} in {state}, and when should "
                f"it be applied?"
            ),
            "ground_truth": (
                f"For {crop} in {state}: {nutrient} rate is "
                f"{rate} lbs/acre, applied as {timing}. "
                f"Important: {note}."
            ),
            "hallucination_trap": (
                f"LLMs often give generic national rates "
                f"instead of {state}-specific recommendations "
                f"for {crop}."
            ),
            "source": "USDA_NRCS_GUIDELINES"
        })

    return qa_pairs


def save_dataset(qa_pairs: list[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        json.dump(qa_pairs, f, indent=2)

    df = pd.DataFrame(qa_pairs)
    csv_path = path.replace(".json", ".csv")
    df.to_csv(csv_path, index=False)

    print(f"\nSaved {len(qa_pairs)} QA pairs")
    print(f"  JSON : {path}")
    print(f"  CSV  : {csv_path}")

    print("\nCategory breakdown:")
    print(df["category"].value_counts().to_string())
    print("\nSeverity breakdown:")
    print(df["severity"].value_counts().to_string())
    print("\nSource breakdown:")
    print(df["source"].value_counts().to_string())


if __name__ == "__main__":
    print("=== AgriHallu-Bench v2 Dataset Generator ===\n")

    print("1. Generating pesticide QA pairs (EPA data)...")
    pesticide_qa = generate_pesticide_qa()
    print(f"   {len(pesticide_qa)} pairs")

    print("2. Generating temporal QA pairs (USDA NASS)...")
    temporal_qa = generate_temporal_qa()
    print(f"   {len(temporal_qa)} pairs")

    print("3. Generating fertilizer QA pairs (USDA NRCS)...")
    fertilizer_qa = generate_soil_fertilizer_qa()
    print(f"   {len(fertilizer_qa)} pairs")

    all_qa = pesticide_qa + temporal_qa + fertilizer_qa
    print(f"\nTotal: {len(all_qa)} QA pairs")

    save_dataset(all_qa, "datasets/agrihallu_v2.json")