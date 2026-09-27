import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="Maharashtra District Accessibility Map",
    layout="wide"
)

st.title("Maharashtra District Accessibility Map")


# ============================================================
# 1. READ EXCEL
# ============================================================

df = pd.read_excel(
    "sonu ojt.xlsx",
    sheet_name="Final Result"
)

# District names clean
df["District Name (district_name)"] = (
    df["District Name (district_name)"]
    .astype(str)
    .str.strip()
)


# ============================================================
# 2. NEW DISTRICT NAMES
# ============================================================

new_names = {
    "Ahmednagar": "Ahilyanagar",
    "Aurangabad": "Chhatrapati Sambhajinagar",
    "Osmanabad": "Dharashiv"
}

# Excel मधील district names update
df["District Name (district_name)"] = (
    df["District Name (district_name)"]
    .replace(new_names)
)


# ============================================================
# 3. READ GEOJSON
# ============================================================

with open(
    "maharashtra.geojson",
    "r",
    encoding="utf-8"
) as f:

    geojson = json.load(f)


# ============================================================
# 4. UPDATE GEOJSON DISTRICT NAMES
# ============================================================

for feature in geojson["features"]:

    old_name = feature["properties"].get("district")

    if old_name is not None:

        old_name = str(old_name).strip()

        if old_name in new_names:

            feature["properties"]["district"] = (
                new_names[old_name]
            )


# ============================================================
# 5. CREATE 3 ACCESSIBILITY LEVELS
# ============================================================

df["Accessibility Level"] = pd.cut(

    df["Overall Accessibility Score"],

    bins=[
        -float("inf"),
        0.40,
        0.60,
        float("inf")
    ],

    labels=[
        "Low",
        "Medium",
        "High"
    ]
)


# ============================================================
# 6. FIND
