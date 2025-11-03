# women_safety_ai

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


DATA_PATH = Path("data") / "safety_index.csv"


def normalize_and_merge_demo(path: Optional[str] = None) -> pd.DataFrame:
    """
    Demo normalizer for local CSV. Ensures numeric dtypes, clamps perceived safety,
    drops missing rows, and writes the cleaned file back to disk.
    """

    csv_path = Path(path) if path else DATA_PATH
    df = pd.read_csv(csv_path)

    df["reported_cases_per_100k"] = pd.to_numeric(df["reported_cases_per_100k"], errors="coerce")
    df["perceived_safety_index"] = (
        pd.to_numeric(df["perceived_safety_index"], errors="coerce").clip(0, 1)
    )
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["city", "age_group", "year", "reported_cases_per_100k", "perceived_safety_index"])

    df.to_csv(csv_path, index=False)
    return df


def fetch_data_gov_in(dataset_id: str) -> pd.DataFrame:
    """
    TODO: Implement integration with data.gov.in datasets.
    Place any future API keys or tokens in environment variables, not in code.
    """
    raise NotImplementedError("TODO: implement fetch_data_gov_in once API access details are added.")


def fetch_safecity_json() -> pd.DataFrame:
    """
    TODO: Add SafeCity open data ingestion.
    Use environment variables or Streamlit secrets for any authentication in future versions.
    """
    raise NotImplementedError("TODO: implement fetch_safecity_json when endpoint details are available.")
