import requests
import pandas as pd
import json
import time
import os
from tqdm import tqdm

# =====================================================
# Real data sources:
# 1. EPA Pesticide database (real tolerances)
# 2. USDA NASS QuickStats API (real crop calendars)
# 3. AgXQA dataset (HuggingFace se)
# 4. USDA Extension publications
# =====================================================

NASS_KEY = os.getenv("NASS_API_KEY", "CC4FBF67-C4D3-3868-92D5-7F2C058F0989")


# ─────────────────────────────────────────
# Source 1: EPA OPP Pesticide Tolerances
# Real chemical + commodity + ppm data
# ─────────────────────────────────────────
def fetch_epa_tolerances() -> pd.DataFrame:
    """
    EPA tolerance database se real pesticide data.
    URL: https://www.ecfr.gov/api (free, no key)
    """
    print("\n[1] Fetching EPA pesticide tolerance data...")

    # EPA eCFR API — 40 CFR Part 180 = pesticide tolerances
    url = "https://www.ecfr.gov/api/versioner/v1/titles/40/structure.json"

    try:
        resp = requests.get(url, timeout=30)
        print(f"    eCFR API status: {resp.status_code}")
    except Exception as e:
        print(f"    eCFR API failed: {e}")

    # Fallback: EPA OPP tolerance database CSV
    # Direct download from EPA
    epa_url = (
        "https://www.epa.gov/sites/default/files/2015-07/"
        "documents/tolerances_commodities.csv"
    )
    try:
        print("    Trying EPA tolerance CSV...")
        resp = requests.get(epa_url, timeout=30)
        if resp.status_code == 200:
            from io import StringIO
            df = pd.read_csv(StringIO(resp.text))
            print(f"    Got {len(df)} tolerance records")
            return df
    except Exception as e:
        print(f"    EPA CSV failed: {e}")

    # Second fallback: PubChem pesticide data
    print("    Using PubChem pesticide API...")
    return fetch_pubchem_pesticides()


def fetch_pubchem_pesticides() -> pd.DataFrame:
    """
    PubChem se real pesticide chemical data.
    Free API, no key needed.
    """
    # Real pesticides with known EPA actions
    pesticide_cids = {
        "Chlorpyrifos":      2730,
        "Glyphosate":        3496,
        "Atrazine":          2256,
        "Carbofuran":        2566,
        "Paraquat":          15938,
        "Malathion":         4004,
        "Permethrin":        40326,
        "Imidacloprid":      86418,
        "Thiamethoxam":      213784,
        "Spinosad":          443059,
        "Mancozeb":          15933,
        "Captan":            8606,
        "Propiconazole":     43234,
        "2,4-D":             1486,
        "Aldicarb":          9570,
        "Dimethoate":        3082,
        "Methyl parathion":  4130,
        "Dicamba":           3030,
        "Metolachlor":       24486,
        "Pendimethalin":     38479,
    }

    records = []
    print(f"    Fetching {len(pesticide_cids)} pesticides from PubChem...")

    for name, cid in tqdm(pesticide_cids.items(), desc="    PubChem"):
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/JSON"
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                compound = data["PC_Compounds"][0]
                props = {
                    p["urn"]["label"]: p["value"].get(
                        "sval", p["value"].get("fval", "")
                    )
                    for p in compound.get("props", [])
                    if "label" in p.get("urn", {})
                }
                records.append({
                    "pesticide_name": name,
                    "cid":            cid,
                    "molecular_formula": props.get("Molecular Formula", ""),
                    "iupac_name":     props.get("IUPAC Name", ""),
                    "source":         "PubChem"
                })
            time.sleep(0.2)
        except Exception as e:
            print(f"    Failed {name}: {e}")

    df = pd.DataFrame(records)
    print(f"    Got {len(df)} pesticide records from PubChem")
    return df


# ─────────────────────────────────────────
# Source 2: USDA NASS — Real Crop Calendar
# ─────────────────────────────────────────
def fetch_nass_crop_progress() -> pd.DataFrame:
    """
    USDA NASS QuickStats — real crop progress data.
    """
    print("\n[2] Fetching USDA NASS crop progress data...")

    base_url = "https://quickstats.nass.usda.gov/api/api_GET/"

    # Crops aur states jo fetch karenge
    queries = [
        {"commodity": "CORN",     "state": "IOWA",       "year": 2023},
        {"commodity": "CORN",     "state": "ILLINOIS",   "year": 2023},
        {"commodity": "CORN",     "state": "NEBRASKA",   "year": 2023},
        {"commodity": "WHEAT",    "state": "KANSAS",     "year": 2023},
        {"commodity": "WHEAT",    "state": "OKLAHOMA",   "year": 2023},
        {"commodity": "SOYBEANS", "state": "ILLINOIS",   "year": 2023},
        {"commodity": "SOYBEANS", "state": "IOWA",       "year": 2023},
        {"commodity": "COTTON",   "state": "MISSISSIPPI","year": 2023},
        {"commodity": "POTATOES", "state": "IDAHO",      "year": 2023},
        {"commodity": "TOMATOES", "state": "CALIFORNIA", "year": 2022},
    ]

    all_records = []

    for q in tqdm(queries, desc="    NASS queries"):
        params = {
            "key":               NASS_KEY,
            "source_desc":       "SURVEY",
            "sector_desc":       "CROPS",
            "commodity_desc":    q["commodity"],
            "statisticcat_desc": "PROGRESS",
            "state_name":        q["state"],
            "year":              q["year"],
            "format":            "JSON"
        }
        try:
            resp = requests.get(base_url, params=params, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                if "data" in data and data["data"]:
                    records = data["data"]
                    for r in records:
                        r["query_commodity"] = q["commodity"]
                        r["query_state"]     = q["state"]
                    all_records.extend(records)
                    print(
                        f"    {q['state']} {q['commodity']}: "
                        f"{len(records)} records"
                    )
                else:
                    print(
                        f"    {q['state']} {q['commodity']}: "
                        f"no data"
                    )
            else:
                print(
                    f"    {q['state']} {q['commodity']}: "
                    f"HTTP {resp.status_code}"
                )
            time.sleep(0.5)
        except Exception as e:
            print(f"    Failed {q}: {e}")

    if all_records:
        df = pd.DataFrame(all_records)
        print(f"\n    Total NASS records: {len(df)}")
        return df
    return pd.DataFrame()


# ─────────────────────────────────────────
# Source 3: AgXQA Dataset (HuggingFace)
# Real agricultural extension QA pairs
# ─────────────────────────────────────────
def fetch_agxqa_dataset() -> pd.DataFrame:
    """
    AgXQA — US agricultural extension QA benchmark.
    Michigan State University ka real dataset.
    """
    print("\n[3] Fetching AgXQA dataset from HuggingFace...")

    try:
        import subprocess
        result = subprocess.run(
            ["pip", "install", "datasets", "-q"],
            capture_output=True
        )

        from datasets import load_dataset
        dataset = load_dataset(
            "MSU-CECO/AgXQA",
            trust_remote_code=True
        )

        records = []
        for split in dataset.keys():
            for item in dataset[split]:
                records.append({
                    "question":  item.get("question", ""),
                    "context":   item.get("context", ""),
                    "answer":    item.get("answers", {}).get(
                        "text", [""]
                    )[0] if item.get("answers") else "",
                    "source":    "AgXQA",
                    "split":     split
                })

        df = pd.DataFrame(records)
        print(f"    AgXQA records: {len(df)}")
        return df

    except Exception as e:
        print(f"    AgXQA failed: {e}")
        print("    Trying direct HuggingFace download...")
        return fetch_agxqa_direct()


def fetch_agxqa_direct() -> pd.DataFrame:
    """AgXQA direct download fallback."""
    urls = [
        "https://huggingface.co/datasets/MSU-CECO/AgXQA/resolve/main/data/train.json",
        "https://huggingface.co/datasets/MSU-CECO/AgXQA/resolve/main/train.json",
    ]

    for url in urls:
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    df = pd.DataFrame([data])
                print(f"    AgXQA direct: {len(df)} records")
                return df
        except Exception as e:
            print(f"    Failed: {e}")

    print("    AgXQA not available, skipping...")
    return pd.DataFrame()


# ─────────────────────────────────────────
# Source 4: KisanVaani Agriculture QA
# HuggingFace pe available — 175k rows
# ─────────────────────────────────────────
def fetch_kisanvaani_qa() -> pd.DataFrame:
    """
    KisanVaani agricultural QA dataset.
    English agriculture questions — crop, pest, soil.
    """
    print("\n[4] Fetching KisanVaani QA dataset...")

    try:
        from datasets import load_dataset
        dataset = load_dataset(
            "KisanVaani/agriculture-qa-english-only",
            split="train"
        )

        # Pehle 2000 records lo — US-relevant filter karenge
        us_keywords = [
            "corn", "wheat", "soybean", "cotton", "potato",
            "tomato", "apple", "pesticide", "herbicide",
            "fungicide", "fertilizer", "nitrogen", "epa",
            "usda", "crop", "harvest", "planting", "yield"
        ]

        records = []
        for item in dataset:
            q = str(item.get("question", "")).lower()
            a = str(item.get("answer", "")).lower()

            # US-relevant questions filter karo
            if any(kw in q or kw in a for kw in us_keywords):
                records.append({
                    "question": item.get("question", ""),
                    "answer":   item.get("answer", ""),
                    "source":   "KisanVaani"
                })

            if len(records) >= 2000:
                break

        df = pd.DataFrame(records)
        print(f"    KisanVaani US-relevant: {len(df)} records")
        return df

    except Exception as e:
        print(f"    KisanVaani failed: {e}")
        return pd.DataFrame()


# ─────────────────────────────────────────
# Main: Sab sources se data collect karo
# ─────────────────────────────────────────
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    os.makedirs("data/raw", exist_ok=True)

    print("=" * 55)
    print("AgriHallu-Bench — Real Data Collector")
    print("=" * 55)

    # 1. EPA / PubChem pesticide data
    pesticide_df = fetch_pubchem_pesticides()
    if not pesticide_df.empty:
        pesticide_df.to_csv(
            "data/raw/pesticides_pubchem.csv", index=False
        )
        print(f"\nSaved: data/raw/pesticides_pubchem.csv")

    # 2. USDA NASS crop progress
    nass_df = fetch_nass_crop_progress()
    if not nass_df.empty:
        nass_df.to_csv(
            "data/raw/nass_crop_progress.csv", index=False
        )
        print(f"Saved: data/raw/nass_crop_progress.csv")

    # 3. AgXQA dataset
    agxqa_df = fetch_agxqa_dataset()
    if not agxqa_df.empty:
        agxqa_df.to_csv(
            "data/raw/agxqa_dataset.csv", index=False
        )
        print(f"Saved: data/raw/agxqa_dataset.csv")

    # 4. KisanVaani QA
    kisan_df = fetch_kisanvaani_qa()
    if not kisan_df.empty:
        kisan_df.to_csv(
            "data/raw/kisanvaani_qa.csv", index=False
        )
        print(f"Saved: data/raw/kisanvaani_qa.csv")

    # Summary
    print("\n" + "=" * 55)
    print("COLLECTION SUMMARY")
    print("=" * 55)
    for name, df in [
        ("PubChem pesticides", pesticide_df),
        ("NASS crop progress", nass_df),
        ("AgXQA dataset",      agxqa_df),
        ("KisanVaani QA",      kisan_df),
    ]:
        status = f"{len(df)} records" if not df.empty else "FAILED"
        print(f"  {name:<25}: {status}")