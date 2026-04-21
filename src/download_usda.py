import requests
import pandas as pd
import os
import json
from dotenv import load_dotenv

load_dotenv()

# USDA ERS API — free, no key needed for basic endpoints
USDA_BASE = "https://api.ers.usda.gov/data/arms/surveydata"

# Crop planting dates by state — NASS quickstats API
NASS_BASE = "https://quickstats.nass.usda.gov/api/api_GET/"
NASS_KEY  = os.getenv("NASS_API_KEY", "DEMO_KEY")

def download_crop_progress(state: str, crop: str, year: int) -> pd.DataFrame:
    """
    USDA NASS se crop progress data download karo.
    Example: Iowa mein corn ki planting dates.
    """
    params = {
        "key":          NASS_KEY,
        "source_desc":  "SURVEY",
        "sector_desc":  "CROPS",
        "commodity_desc": crop.upper(),
        "statisticcat_desc": "PROGRESS",
        "state_name":   state.upper(),
        "year":         year,
        "format":       "JSON"
    }

    print(f"Downloading {crop} progress data for {state} {year}...")
    resp = requests.get(NASS_BASE, params=params, timeout=30)

    if resp.status_code == 200:
        data = resp.json()
        if "data" in data:
            df = pd.DataFrame(data["data"])
            print(f"  Got {len(df)} rows")
            return df
        else:
            print(f"  No data found: {data.get('error', 'unknown')}")
            return pd.DataFrame()
    else:
        print(f"  Error {resp.status_code}")
        return pd.DataFrame()


def download_pdp_sample() -> pd.DataFrame:
    """
    USDA Pesticide Data Program — sample data load karo.
    Local CSV se (manually downloaded).
    """
    pdp_path = "data/pdp_sample.csv"

    if os.path.exists(pdp_path):
        df = pd.read_csv(pdp_path)
        print(f"PDP data loaded: {len(df)} rows")
        return df
    else:
        print("PDP file nahi mili — creating sample placeholder...")
        # Abhi ke liye sample data banate hain
        sample = pd.DataFrame({
            "commodity":      ["CORN", "WHEAT", "SOYBEANS", "APPLES", "TOMATOES"],
            "pesticide_name": ["Chlorpyrifos", "Glyphosate", "Atrazine",
                               "Thiamethoxam", "Spinosad"],
            "epa_tolerance_ppm": [0.01, 0.1, 0.02, 0.08, 0.3],
            "status":         ["CANCELLED", "APPROVED", "APPROVED",
                               "APPROVED", "APPROVED"],
            "crop_use":       ["field corn", "wheat grain", "soybeans",
                               "apple fruit", "tomato fruit"]
        })
        os.makedirs("data", exist_ok=True)
        sample.to_csv(pdp_path, index=False)
        print(f"Sample PDP data saved: {pdp_path}")
        return sample


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    # 1. PDP pesticide data
    pdp_df = download_pdp_sample()
    print("\nPDP sample:")
    print(pdp_df.head())

    # 2. Crop progress — free NASS data (DEMO_KEY se limited)
    corn_df = download_crop_progress("IOWA", "CORN", 2023)
    if not corn_df.empty:
        corn_df.to_csv("data/corn_progress_iowa_2023.csv", index=False)
        print("\nCorn progress sample:")
        print(corn_df[["state_name", "commodity_desc",
                        "short_desc", "Value"]].head())

    print("\nData download complete!")