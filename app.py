import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Maharashtra District Accessibility Map",
    layout="wide"
)

st.title("Maharashtra District Accessibility Map")

# --------------------------------------------------
# 1. READ EXCEL
# --------------------------------------------------

df = pd.read_excel(
    "sonu ojt.xlsx",
    sheet_name="Final Result"
)

# --------------------------------------------------
# 2. NEW DISTRICT NAMES
# --------------------------------------------------

new_names = {
    "Ahmednagar": "Ahilyanagar",
    "Aurangabad": "Chhatrapati Sambhajinagar",
    "Osmanabad": "Dharashiv"
}

# Excel मधील district names नवीन नावात बदलणे
df["Display District"] = df["District Name (district_name)"].replace(new_names)

# --------------------------------------------------
# 3. 3 ACCESSIBILITY LEVELS
# --------------------------------------------------

df["Accessibility Level"] = pd.cut(
    df["Overall Accessibility Score"],
    bins=[-float("inf"), 0.40, 0.60, float("inf")],
    labels=["Low", "Medium", "High"]
)

# --------------------------------------------------
# 4. READ GEOJSON
# --------------------------------------------------

with open("maharashtra.geojson", "r", encoding="utf-8") as f:
    geojson = json.load(f)

# --------------------------------------------------
# 5. DISTRICT LABEL POSITIONS
# --------------------------------------------------

def get_all_points(coords):
    points = []

    def extract(obj):
        if isinstance(obj, (list, tuple)):
            if len(obj) >= 2 and isinstance(obj[0], (int, float)):
                points.append((obj[0], obj[1]))
            else:
                for item in obj:
                    extract(item)

    extract(coords)
    return points


label_data = []

for feature in geojson["features"]:

    district_name = feature["properties"].get("district")

    geometry = feature["geometry"]

    points = get_all_points(geometry["coordinates"])

    if points:
        avg_lon = sum(p[0] for p in points) / len(points)
        avg_lat = sum(p[1] for p in points) / len(points)

        label_data.append({
            "District": district_name,
            "lon": avg_lon,
            "lat": avg_lat
        })

labels = pd.DataFrame(label_data)

# --------------------------------------------------
# 6. NEW NAMES FOR MAP LABELS
# --------------------------------------------------

labels["Display District"] = labels["District"].replace(new_names)

# --------------------------------------------------
# 7. MATCH RANK WITH DISTRICT
# --------------------------------------------------

labels = labels.merge(
    df[
        [
            "District Name (district_name)",
            "Rank"
        ]
    ],
    left_on="District",
    right_on="District Name (district_name)",
    how="left"
)

# --------------------------------------------------
# 8. CHOROPLETH MAP
# --------------------------------------------------

st.subheader("District Accessibility Map")

fig = px.choropleth(
    df,
    geojson=geojson,
    locations="District Name (district_name)",
    featureidkey="properties.district",
    color="Accessibility Level",

    hover_name="Display District",

    hover_data={
        "Overall Accessibility Score": ":.4f",
        "Rank": True,
        "Accessibility Level": True
    },

    color_discrete_map={
        "Low": "#F4A6A6",
        "Medium": "#FFD966",
        "High": "#70AD47"
    }
)

# --------------------------------------------------
# 9. DISTRICT NAME + RANK
# --------------------------------------------------

fig.add_trace(
    go.Scattergeo(
        lon=labels["lon"],
        lat=labels["lat"],

        text=[
            f"{name}<br>Rank: {rank}"
            for name, rank in zip(
                labels["Display District"],
                labels["Rank"]
            )
        ],

        mode="text",

        textfont=dict(
            size=8
        ),

        hoverinfo="text",

        hovertext=[
            f"{name}<br>Rank: {rank}"
            for name, rank in zip(
                labels["Display District"],
                labels["Rank"]
            )
        ],

        showlegend=False
    )
)

# --------------------------------------------------
# 10. MAP SETTINGS
# --------------------------------------------------

fig.update_geos(
    fitbounds="locations",
    visible=False
)

fig.update_layout(
    height=500,

    margin=dict(
        r=0,
        t=10,
        l=0,
        b=0
    )
)

# --------------------------------------------------
# 11. DISPLAY MAP
# --------------------------------------------------

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# 12. RESULT TABLE
# --------------------------------------------------

st.subheader("District Accessibility Result")

st.dataframe(
    df,
    use_container_width=True
)
