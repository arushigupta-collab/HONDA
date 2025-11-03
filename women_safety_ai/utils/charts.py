# women_safety_ai

from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure


def load_safety_df(path: str = "data/safety_index.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["reported_cases_per_100k"] = pd.to_numeric(df["reported_cases_per_100k"], errors="coerce")
    df["perceived_safety_index"] = pd.to_numeric(df["perceived_safety_index"], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["city", "age_group", "year", "perceived_safety_index"])
    return df


def plot_safety_by_city_age(
    df: pd.DataFrame,
    city: Optional[str] = None,
    age_group: Optional[str] = None,
) -> Figure:
    filtered = df.copy()
    if city:
        filtered = filtered[filtered["city"] == city]
    if age_group:
        filtered = filtered[filtered["age_group"] == age_group]

    fig = px.line(
        filtered,
        x="year",
        y="perceived_safety_index",
        color="city",
        line_group="age_group",
        hover_data=["age_group", "reported_cases_per_100k"],
        markers=True,
    )
    fig.update_layout(yaxis_title="Perceived Safety Index", xaxis_title="Year")
    return fig
