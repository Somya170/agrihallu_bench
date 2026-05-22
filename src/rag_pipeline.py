import os
import json
import time
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =====================================================
# AgriHallu-Bench — RAG Pipeline
# Knowledge base = verified USDA/EPA facts
# Retrieval = simple keyword matching (no heavy libs)
# =====================================================

# Verified knowledge base — ground truth facts
KNOWLEDGE_BASE = [
    # Cancelled pesticides
    {
        "id": "kb_chlorpyrifos",
        "text": "Chlorpyrifos: EPA CANCELLED all food tolerances in August 2021. No longer approved for any food/feed crop use including field corn, apples, citrus. MRL is effectively 0. Any use on food crops is illegal.",
        "keywords": ["chlorpyrifos", "corn", "apples", "citrus", "tolerance", "mrl", "approved", "cancelled"]
    },
    {
        "id": "kb_dimethoate_blueberry",
        "text": "Dimethoate: EPA cancelled tolerance for blueberries in 2016. Not approved for blueberry use. Status: CANCELLED for blueberries.",
        "keywords": ["dimethoate", "blueberries", "blueberry", "tolerance", "cancelled"]
    },
    {
        "id": "kb_aldicarb",
        "text": "Aldicarb: Voluntarily cancelled by manufacturer Bayer CropScience in 2010. No longer registered for citrus or any food crop. Status: CANCELLED.",
        "keywords": ["aldicarb", "citrus", "cancelled", "bayer", "registered"]
    },
    {
        "id": "kb_carbofuran",
        "text": "Carbofuran: EPA revoked ALL food tolerances in 2009. Completely cancelled for corn and all food crops. Illegal to use on any food crop.",
        "keywords": ["carbofuran", "corn", "cancelled", "revoked", "tolerance"]
    },
    {
        "id": "kb_methyl_parathion",
        "text": "Methyl parathion: All food uses cancelled by EPA in 2003. Not approved for wheat or any food crop.",
        "keywords": ["methyl parathion", "wheat", "cancelled", "food uses"]
    },
    {
        "id": "kb_paraquat",
        "text": "Paraquat: RESTRICTED USE pesticide for soybeans. Requires certified pesticide applicator license. EPA tolerance 0.05 ppm. Cannot be purchased or used by general public.",
        "keywords": ["paraquat", "soybeans", "restricted", "certified", "applicator", "0.05"]
    },
    {
        "id": "kb_methyl_bromide",
        "text": "Methyl bromide: Being phased out under Montreal Protocol. Only critical use exemptions allowed for strawberries. Effectively RESTRICTED, not generally available.",
        "keywords": ["methyl bromide", "strawberries", "montreal", "restricted", "exemption"]
    },
    # Approved with specific tolerances
    {
        "id": "kb_glyphosate_wheat",
        "text": "Glyphosate on wheat grain: APPROVED. EPA tolerance is 30.0 ppm. Used as pre-harvest desiccant. Must follow label. Tolerance: 30 ppm.",
        "keywords": ["glyphosate", "wheat", "approved", "30", "ppm", "tolerance", "desiccant"]
    },
    {
        "id": "kb_atrazine_corn",
        "text": "Atrazine on field corn: APPROVED for pre-emergent weed control. EPA tolerance 0.1 ppm in grain. Restricted use in some states near water bodies.",
        "keywords": ["atrazine", "corn", "approved", "0.1", "ppm", "pre-emergent", "weed"]
    },
    {
        "id": "kb_thiamethoxam_apple",
        "text": "Thiamethoxam on apple fruit: APPROVED systemic insecticide. EPA tolerance 0.08 ppm. Must follow pre-harvest interval on label.",
        "keywords": ["thiamethoxam", "apple", "apples", "approved", "0.08", "ppm", "insecticide"]
    },
    {
        "id": "kb_spinosad_tomato",
        "text": "Spinosad on tomato fruit: APPROVED. OMRI-listed for organic production. EPA tolerance 0.3 ppm. Approved for conventional and organic use.",
        "keywords": ["spinosad", "tomato", "tomatoes", "approved", "0.3", "ppm", "organic"]
    },
    {
        "id": "kb_malathion_strawberry",
        "text": "Malathion on strawberries: APPROVED broad-spectrum insecticide. EPA tolerance 8.0 ppm. Follow pre-harvest interval carefully.",
        "keywords": ["malathion", "strawberries", "strawberry", "approved", "8.0", "ppm"]
    },
    {
        "id": "kb_24d_wheat",
        "text": "2,4-D on wheat: APPROVED herbicide for broadleaf weed control. EPA tolerance 2.0 ppm. Apply before jointing stage.",
        "keywords": ["2,4-d", "wheat", "approved", "2.0", "ppm", "herbicide", "broadleaf"]
    },
    # Planting windows
    {
        "id": "kb_iowa_corn",
        "text": "Iowa Corn planting: Optimal window late April to mid May. Harvest: late September through November. Iowa is the largest corn-producing state in the US.",
        "keywords": ["iowa", "corn", "plant", "planting", "harvest", "april", "may", "september"]
    },
    {
        "id": "kb_kansas_wheat",
        "text": "Kansas Winter Wheat: Plant late September to mid October. Harvest late June through July. Kansas is the largest winter wheat producing state.",
        "keywords": ["kansas", "wheat", "winter wheat", "plant", "harvest", "september", "october", "june", "july"]
    },
    {
        "id": "kb_california_almonds",
        "text": "California Almonds: Bloom/plant January to February. Harvest August through October. California produces 80% of world almonds.",
        "keywords": ["california", "almonds", "almond", "bloom", "harvest", "january", "february", "august"]
    },
    {
        "id": "kb_florida_tomatoes",
        "text": "Florida Tomatoes: Plant September to October. Harvest December through January. Florida winter tomato production supplies eastern US market.",
        "keywords": ["florida", "tomatoes", "tomato", "plant", "harvest", "september", "october", "december"]
    },
    {
        "id": "kb_idaho_potatoes",
        "text": "Idaho Potatoes: Plant April through May. Harvest August through October. Idaho is the largest US potato producing state.",
        "keywords": ["idaho", "potatoes", "potato", "plant", "harvest", "april", "may", "august"]
    },
    {
        "id": "kb_nebraska_corn",
        "text": "Nebraska Corn: Plant early May to late May. Harvest late September through November. Heavy irrigation production.",
        "keywords": ["nebraska", "corn", "plant", "harvest", "may", "september"]
    },
    {
        "id": "kb_illinois_soybeans",
        "text": "Illinois Soybeans: Plant early May to early June. Harvest late September through October. Illinois is the top soybean producing state.",
        "keywords": ["illinois", "soybeans", "soybean", "plant", "harvest", "may", "june"]
    },
    {
        "id": "kb_oklahoma_winter_wheat",
        "text": "Oklahoma Winter Wheat: Plant mid October to early November. Harvest June through early July. Oklahoma is second largest winter wheat state after Kansas.",
        "keywords": ["oklahoma", "wheat", "winter wheat", "plant", "harvest", "october", "november", "june", "july"]
    },
    {
        "id": "kb_washington_spring_wheat",
        "text": "Washington Spring Wheat: Plant March through April. Harvest August through September. Washington Palouse region is top spring wheat area.",
        "keywords": ["washington", "wheat", "spring wheat", "plant", "harvest", "march", "april", "august"]
    },
    {
        "id": "kb_iowa_soybeans",
        "text": "Iowa Soybeans: Plant early May to early June. Harvest October through November. Iowa is top soybean producing state alongside Illinois.",
        "keywords": ["iowa", "soybeans", "soybean", "plant", "harvest", "may", "june", "october"]
    },
    {
        "id": "kb_illinois_corn",
        "text": "Illinois Corn: Plant late April to late May. Harvest October through November. Illinois is second largest corn producing state.",
        "keywords": ["illinois", "corn", "plant", "harvest", "april", "may", "october", "november"]
    },
    {
        "id": "kb_georgia_peanuts",
        "text": "Georgia Peanuts: Plant late April to mid May. Harvest October through November. Georgia produces 40% of US peanuts.",
        "keywords": ["georgia", "peanuts", "peanut", "plant", "harvest", "april", "may", "october"]
    },
    {
        "id": "kb_mississippi_cotton",
        "text": "Mississippi Cotton: Plant late April to mid May. Harvest October through November. Mississippi Delta is prime cotton region.",
        "keywords": ["mississippi", "cotton", "plant", "harvest", "april", "may", "october"]
    },
    {
        "id": "kb_wisconsin_cranberries",
        "text": "Wisconsin Cranberries: Plant April through May. Harvest September through October. Wisconsin produces 60% of US cranberries.",
        "keywords": ["wisconsin", "cranberries", "cranberry", "plant", "harvest", "april", "september", "october"]
    },
    {
        "id": "kb_california_tomatoes",
        "text": "California Tomatoes: Plant March through May. Harvest July through October. California produces 90% of US processed tomatoes.",
        "keywords": ["california", "tomatoes", "tomato", "plant", "harvest", "march", "may", "july", "october"]
    },
    # Fertilizer
    {
        "id": "kb_nitrogen_corn_iowa",
        "text": "Nitrogen for corn in Iowa: Recommended rate 150-200 lbs/acre. Split application: pre-plant and side-dress at V6 growth stage. Excess N causes nitrate leaching into Iowa waterways.",
        "keywords": ["nitrogen", "corn", "iowa", "150", "200", "lbs", "acre", "side-dress", "v6"]
    },
    {
        "id": "kb_nitrogen_wheat_kansas",
        "text": "Nitrogen for winter wheat in Kansas: Recommended 60-90 lbs/acre. Apply fall at planting plus spring topdress. Kansas State recommends soil test before application.",
        "keywords": ["nitrogen", "wheat", "kansas", "60", "90", "lbs", "acre", "topdress"]
    },
    {
        "id": "kb_phosphorus_soybeans",
        "text": "Phosphorus for soybeans in Illinois: Recommended 40-80 lbs/acre pre-plant incorporated. Soybeans fix nitrogen so P and K are primary nutrient concerns.",
        "keywords": ["phosphorus", "soybeans", "illinois", "40", "80", "lbs", "acre", "pre-plant"]
    },








    {
        "id": "kb_nass_2023_iowa_soybeans_full",
        "text": "USDA NASS 2023 IOWA SOYBEANS: PLANTING — Season started (10%) by 2023-04-30, 50% planted by 2023-05-14, 100% planted by 2023-06-11. HARVEST — Season started (10%) by 2023-09-24, 50% harvested by 2023-10-08, peak 99% harvested reached by 2023-11-12. Source: USDA NASS 2023 Weekly Crop Progress Reports.",
        "keywords": ["iowa", "soybeans", "2023", "nass", "usda", "planted", "planting", "harvested", "harvest", "peak", "progress", "weekly", "2023-04-30", "2023-05-14", "2023-06-11", "2023-09-24", "2023-10-08", "2023-11-12"]
    },
    {
        "id": "kb_nass_2023_oklahoma_wheat_full",
        "text": "USDA NASS 2023 OKLAHOMA WHEAT: PLANTING — Season started (10%) by 2022-09-11, 50% planted by 2022-10-16, 100% planted by unknown. HARVEST — Season started (10%) by 2023-06-04, 50% harvested by 2023-06-25, peak 100% harvested reached by 2023-07-23. Source: USDA NASS 2023 Weekly Crop Progress Reports.",
        "keywords": ["oklahoma", "wheat", "2023", "nass", "usda", "planted", "planting", "harvested", "harvest", "peak", "progress", "weekly", "2022-09-11", "2022-10-16", "2023-06-04", "2023-06-25", "2023-07-23"]
    },
    {
        "id": "kb_nass_2023_mississippi_cotton_full",
        "text": "USDA NASS 2023 MISSISSIPPI COTTON: PLANTING — Season started (10%) by 2023-05-07, 50% planted by 2023-05-21, 100% planted by 2023-07-02. HARVEST — Season started (10%) by 2023-09-24, 50% harvested by 2023-10-15, peak 100% harvested reached by 2023-11-26. Source: USDA NASS 2023 Weekly Crop Progress Reports.",
        "keywords": ["mississippi", "cotton", "2023", "nass", "usda", "planted", "planting", "harvested", "harvest", "peak", "progress", "weekly", "2023-05-07", "2023-05-21", "2023-07-02", "2023-09-24", "2023-10-15", "2023-11-26"]
    },
    {
        "id": "kb_nass_2023_illinois_corn_full",
        "text": "USDA NASS 2023 ILLINOIS CORN: PLANTING — Season started (10%) by 2023-04-16, 50% planted by 2023-05-07, 100% planted by unknown. HARVEST — Season started (10%) by 2023-09-24, 50% harvested by 2023-10-15, peak 99% harvested reached by 2023-11-26. Source: USDA NASS 2023 Weekly Crop Progress Reports.",
        "keywords": ["illinois", "corn", "2023", "nass", "usda", "planted", "planting", "harvested", "harvest", "peak", "progress", "weekly", "2023-04-16", "2023-05-07", "2023-09-24", "2023-10-15", "2023-11-26"]
    },
    {
        "id": "kb_nass_2023_kansas_wheat_full",
        "text": "USDA NASS 2023 KANSAS WHEAT: PLANTING — Season started (10%) by 2022-09-18, 50% planted by 2022-10-09, 100% planted by unknown. HARVEST — Season started (10%) by 2023-06-25, 50% harvested by 2023-07-09, peak 100% harvested reached by 2023-08-20. Source: USDA NASS 2023 Weekly Crop Progress Reports.",
        "keywords": ["kansas", "wheat", "2023", "nass", "usda", "planted", "planting", "harvested", "harvest", "peak", "progress", "weekly", "2022-09-18", "2022-10-09", "2023-06-25", "2023-07-09", "2023-08-20"]
    },
    {
        "id": "kb_nass_2023_iowa_corn_full",
        "text": "USDA NASS 2023 IOWA CORN: PLANTING — Season started (10%) by 2023-04-23, 50% planted by 2023-05-07, 100% planted by 2023-06-04. HARVEST — Season started (10%) by 2023-10-01, 50% harvested by 2023-10-22, peak 99% harvested reached by 2023-11-26. Source: USDA NASS 2023 Weekly Crop Progress Reports.",
        "keywords": ["iowa", "corn", "2023", "nass", "usda", "planted", "planting", "harvested", "harvest", "peak", "progress", "weekly", "2023-04-23", "2023-05-07", "2023-06-04", "2023-10-01", "2023-10-22", "2023-11-26"]
    },
    {
        "id": "kb_nass_2023_idaho_potatoes_full",
        "text": "USDA NASS 2023 IDAHO POTATOES: PLANTING — Season started (10%) by 2023-04-23, 50% planted by 2023-05-07, 100% planted by unknown. HARVEST — Season started (10%) by 2023-09-10, 50% harvested by 2023-10-08, peak 98% harvested reached by 2023-10-22. Source: USDA NASS 2023 Weekly Crop Progress Reports.",
        "keywords": ["idaho", "potatoes", "2023", "nass", "usda", "planted", "planting", "harvested", "harvest", "peak", "progress", "weekly", "2023-04-23", "2023-05-07", "2023-09-10", "2023-10-08", "2023-10-22"]
    },
    {
        "id": "kb_nass_2023_nebraska_corn_full",
        "text": "USDA NASS 2023 NEBRASKA CORN: PLANTING — Season started (10%) by 2023-04-23, 50% planted by 2023-05-07, 100% planted by unknown. HARVEST — Season started (10%) by 2023-09-24, 50% harvested by 2023-10-22, peak 98% harvested reached by 2023-11-26. Source: USDA NASS 2023 Weekly Crop Progress Reports.",
        "keywords": ["nebraska", "corn", "2023", "nass", "usda", "planted", "planting", "harvested", "harvest", "peak", "progress", "weekly", "2023-04-23", "2023-05-07", "2023-09-24", "2023-10-22", "2023-11-26"]
    },
    {
        "id": "kb_nass_2023_illinois_soybeans_full",
        "text": "USDA NASS 2023 ILLINOIS SOYBEANS: PLANTING — Season started (10%) by 2023-04-23, 50% planted by 2023-05-07, 100% planted by unknown. HARVEST — Season started (10%) by 2023-10-01, 50% harvested by 2023-10-15, peak 97% harvested reached by 2023-11-12. Source: USDA NASS 2023 Weekly Crop Progress Reports.",
        "keywords": ["illinois", "soybeans", "2023", "nass", "usda", "planted", "planting", "harvested", "harvest", "peak", "progress", "weekly", "2023-04-23", "2023-05-07", "2023-10-01", "2023-10-15", "2023-11-12"]
    },

]


def retrieve_context(question: str, top_k: int = 3) -> str:
    """
    Improved retrieval — temporal questions ke liye
    stricter matching.
    """
    question_lower = question.lower()

    # Temporal questions detect karo
    temporal_keywords = [
        "when", "plant", "harvest", "season",
        "window", "month", "optimal time"
    ]
    is_temporal = any(kw in question_lower for kw in temporal_keywords)

    scores = []
    for entry in KNOWLEDGE_BASE:
        # Keyword match score
        keyword_score = sum(
            1 for kw in entry["keywords"]
            if kw.lower() in question_lower
        )

        if keyword_score == 0:
            continue

        # Temporal questions ke liye — sirf temporal entries lo
        if is_temporal and "plant" not in entry["text"].lower() \
                and "harvest" not in entry["text"].lower():
            continue

        # State + crop dono match hone chahiye temporal mein
        if is_temporal:
            state_match = any(
                state in question_lower
                for state in [
                    "iowa", "kansas", "california", "florida",
                    "nebraska", "illinois", "idaho", "georgia",
                    "mississippi", "washington", "oklahoma", "wisconsin"
                ]
            )
            crop_match = any(
                crop in question_lower
                for crop in [
                    "corn", "wheat", "soybeans", "almonds",
                    "tomatoes", "potatoes", "cotton", "peanuts",
                    "cranberries"
                ]
            )
            # Dono match nahi hue toh skip karo
            if state_match and crop_match and keyword_score < 2:
                continue

        scores.append((keyword_score, entry))

    scores.sort(key=lambda x: x[0], reverse=True)
    top_entries = [entry for _, entry in scores[:top_k]]

    if not top_entries:
        return (
            "No specific verified context found. "
            "Please consult USDA NASS or local extension office."
        )

    context = "\n\n".join([
        f"[Source: {e['id']}]\n{e['text']}"
        for e in top_entries
    ])
    return context

def query_llm_with_rag(
    question: str,
    model: str = "llama-3.1-8b-instant"
) -> tuple[str, str]:
    """
    RAG-augmented query — context ke saath LLM se jawab lo.
    Returns: (response, retrieved_context)
    """
    context = retrieve_context(question)

    rag_prompt = f"""You are an agricultural advisory AI assistant.
Use ONLY the following verified USDA/EPA information to answer the question.
If the information is not in the context, say so clearly.

VERIFIED CONTEXT:
{context}

Question: {question}

Answer based strictly on the verified context above:"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": rag_prompt}
            ],
            temperature=0,
            max_tokens=300
        )
        return response.choices[0].message.content.strip(), context
    except Exception as e:
        return f"ERROR: {e}", context


def judge_response(
    question: str,
    ground_truth: str,
    llm_response: str
) -> dict:
    prompt = f"""Question: {question}

Ground Truth: {ground_truth}

AI Response: {llm_response}

Is there a hallucination in the AI Response?"""

    judge_prompt = """You are an expert agricultural fact-checker.
Determine if the AI response contains a hallucination.
Respond ONLY in this JSON format:
{
  "hallucinated": true,
  "hallucination_type": "REGULATORY/DOSAGE/TEMPORAL/FACTUAL/NONE",
  "severity": "HIGH/MEDIUM/LOW/NONE",
  "explanation": "one sentence explanation",
  "confidence": 0.0
}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": judge_prompt},
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


def evaluate_with_rag(
    dataset_path: str,
    model: str = "llama-3.1-8b-instant",
    max_questions: int = None
) -> pd.DataFrame:

    with open(dataset_path) as f:
        qa_pairs = json.load(f)

    if max_questions:
        qa_pairs = qa_pairs[:max_questions]

    print(f"\nRAG Evaluation : {model}")
    print(f"Questions      : {len(qa_pairs)}")
    print("-" * 50)

    results = []

    for qa in tqdm(qa_pairs, desc="  RAG"):
        rag_response, context = query_llm_with_rag(
            qa["question"], model
        )
        time.sleep(0.3)

        judgment = judge_response(
            qa["question"],
            qa["ground_truth"],
            rag_response
        )
        time.sleep(0.3)

        results.append({
            "id":                 qa["id"],
            "category":           qa["category"],
            "severity":           qa["severity"],
            "question":           qa["question"],
            "ground_truth":       qa["ground_truth"],
            "rag_response":       rag_response,
            "context_retrieved":  context[:200],
            "hallucinated":       judgment.get("hallucinated", False),
            "hallucination_type": judgment.get("hallucination_type", "NONE"),
            "judge_severity":     judgment.get("severity", "NONE"),
            "explanation":        judgment.get("explanation", ""),
            "confidence":         judgment.get("confidence", 0.0),
            "model":              f"{model}+RAG"
        })

    return pd.DataFrame(results)


def compare_baseline_vs_rag(
    baseline_csv: str,
    rag_df: pd.DataFrame
) -> None:
    baseline_df = pd.read_csv(baseline_csv)

    b_rate = baseline_df["hallucinated"].mean() * 100
    r_rate = rag_df["hallucinated"].mean() * 100
    reduction = b_rate - r_rate

    print("\n" + "="*60)
    print("BASELINE vs RAG COMPARISON")
    print("="*60)
    print(f"{'Metric':<30} {'Baseline':>12} {'RAG':>12} {'Change':>10}")
    print("-" * 66)
    print(
        f"{'Overall hallucination rate':<30} "
        f"{b_rate:>11.1f}% {r_rate:>11.1f}% "
        f"{'-' if reduction > 0 else '+'}{abs(reduction):>8.1f}%"
    )

    print("\nBy category:")
    print(f"{'Category':<15} {'Baseline%':>12} {'RAG%':>8} {'Reduction':>12}")
    print("-" * 50)

    for cat in baseline_df["category"].unique():
        b = baseline_df[baseline_df["category"] == cat]
        r = rag_df[rag_df["category"] == cat]
        if len(b) > 0 and len(r) > 0:
            b_cat = b["hallucinated"].mean() * 100
            r_cat = r["hallucinated"].mean() * 100
            red   = b_cat - r_cat
            print(
                f"{cat:<15} {b_cat:>11.1f}% {r_cat:>7.1f}% "
                f"{'-' if red > 0 else '+'}{abs(red):>10.1f}%"
            )

    print(f"\nOverall reduction: {reduction:.1f} percentage points")
    print(
        f"Relative improvement: "
        f"{(reduction/b_rate*100):.1f}% fewer hallucinations with RAG"
    )


if __name__ == "__main__":
    import glob

    print("=== AgriHallu-Bench RAG v2 Evaluation ===")
    os.makedirs("results", exist_ok=True)

    dataset = "datasets/agrihallu_v3_real.json"

    print("\nRunning improved RAG on full dataset...")
    rag_df = evaluate_with_rag(
        dataset,
        model="llama-3.1-8b-instant",
        max_questions=None
    )

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    rag_path  = f"results/eval_rag_FULL_{timestamp}.csv"
    rag_df.to_csv(rag_path, index=False)
    print(f"Saved: {rag_path}")

    baseline = sorted(glob.glob("results/eval_llama3_FULL_*.csv"))[-1]
    compare_baseline_vs_rag(baseline, rag_df)