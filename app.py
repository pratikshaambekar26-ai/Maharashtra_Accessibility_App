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


# ============================================================
# 2. READ GEOJSON
# ============================================================

with open("maharashtra.geojson", "r", encoding="utf-8") as f:
    geojson = json.load(f)


# ============================================================
# 3. NEW DISTRICT NAMES
# ============================================================

new_names = {
    "Ahmednagar": "Ahilyanagar",
    "Aurangabad": "Chhatrapati Sambhajinagar",
    "Osmanabad": "Dharashiv"
}


# ============================================================
# 4. CHANGE DISTRICT NAMES IN EXCEL
# ============================================================

df["District Name (district_name)"] = (
    df["District Name (district_name)"]
    .astype(str)
    .str.strip()
    .replace(new_names)
)


# ============================================================
# 5. CHANGE DISTRICT NAMES IN GEOJSON
# ============================================================

for feature in geojson["features"]:

    district = feature["properties"].get("district")

    if district in new_names:
        feature["properties"]["district"] = new_names[district]


# ============================================================
# 6. CREATE 3 ACCESSIBILITY LEVELS
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
# 7. EXTRACT DISTRICT CENTRE POINTS
# ============================================================

def get_all_points(coords):

    points = []

    def extract(obj):

        if isinstance(obj, (list, tuple)):

            if (
                len(obj) >= 2
                and isinstance(obj[0], (int, float))
                and isinstance(obj[1], (int, float))
            ):
                points.append(
                    (obj[0], obj[1])
                )

            else:

                for item in obj:
                    extract(item)

    extract(coords)

    return points


label_data = []


for feature in geojson["features"]:

    district_name = feature["properties"].get("district")

    geometry = feature["geometry"]

    points = get_all_points(
        geometry["coordinates"]
    )

    if points:

        avg_lon = sum(
            p[0] for p in points
        ) / len(points)

        avg_lat = sum(
            p[1] for p in points
        ) / len(points)

        label_data.append({
            "District": district_name,
            "lon": avg_lon,
            "lat": avg_lat
        })


labels = pd.DataFrame(label_data)


# ============================================================
# 8. MERGE RANK WITH MAP LABELS
# ============================================================

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


# ============================================================
# 9. MAP
# ============================================================

st.subheader("District Accessibility Map")


fig = px.choropleth(
    df,
    geojson=geojson,
    locations="District Name (district_name)",
    featureidkey="properties.district",
    color="Accessibility Level",

    color_discrete_map={
        "Low": "#8B0000",
        "Medium": "#B8860B",
        "High": "#006400"
    },

    hover_name="District Name (district_name)",

    hover_data={
        "Overall Accessibility Score": ":.4f",
        "Rank": True,
        "Accessibility Level": True
    }
)


# ============================================================
# 10. DISTRICT NAME + RANK ON MAP
# ============================================================

fig.add_trace(
    go.Scattergeo(

        lon=labels["lon"],
        lat=labels["lat"],

        text=[
            f"<b>{name}</b><br>Rank: {rank}"
            for name, rank in zip(
                labels["District"],
                labels["Rank"]
            )
        ],

        mode="text",

        textfont=dict(
            size=10,
            color="black"
        ),

        hoverinfo="text",

        hovertext=[
            f"{name}<br>Rank: {rank}"
            for name, rank in zip(
                labels["District"],
                labels["Rank"]
            )
        ],

        showlegend=False
    )
)


# ============================================================
# 11. MAP SIZE
# ============================================================

fig.update_geos(
    fitbounds="locations",
    visible=False,
    projection_scale=1
)


fig.update_layout(

    height=450,

    margin=dict(
        r=0,
        t=5,
        l=0,
        b=0
    ),

    legend=dict(
        title="Accessibility"
    )
)


# ============================================================
# 12. DISPLAY MAP
# ============================================================

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# 13. RESULT TABLE
# ============================================================

st.subheader("District Accessibility Result")


st.dataframe(
    df,
    use_container_width=True
)
