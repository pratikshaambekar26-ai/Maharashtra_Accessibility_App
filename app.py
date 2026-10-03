
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

# 1. READ EXCEL
df = pd.read_excel(
    "Accessibility Index By PCA Method.xlsx",
    sheet_name="Final Ranking"
)

# Rename columns for easy use
df = df.rename(columns={
    "District Name": "District",
    "Final Accessibility Score": "Score",
    "Accessibility Rank": "Rank"
})

df["Rank"] = pd.to_numeric(
    df["Rank"], errors="coerce"
).astype("Int64")

# 2. UPDATE DISTRICT NAMES
new_names = {
    "Ahmednagar": "Ahilyanagar",
    "Aurangabad": "Chhatrapati Sambhajinagar",
    "Osmanabad": "Dharashiv"
}

df["District"] = df["District"].replace(new_names)

# 3. READ GEOJSON
with open("maharashtra.geojson", "r", encoding="utf-8") as f:
    geojson = json.load(f)

for feature in geojson["features"]:
    old_name = feature["properties"].get("district")
    if old_name in new_names:
        feature["properties"]["district"] = new_names[old_name]

# 4. DISTRICT LABEL POSITIONS
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

# 5. MATCH RANK WITH DISTRICT
labels = labels.merge(
    df[["District", "Rank"]],
    on="District",
    how="left"
)

labels["Rank"] = pd.to_numeric(
    labels["Rank"], errors="coerce"
).astype("Int64")

# 6. ACCESSIBILITY LEVELS
df["Accessibility Level"] = pd.cut(
    df["Score"],
    bins=[-float("inf"), 0.40, 0.60, float("inf")],
    labels=["Low", "Medium", "High"]
)

# 7. CHOROPLETH MAP
st.subheader("District Accessibility Map")

fig = px.choropleth(
    df,
    geojson=geojson,
    locations="District",
    featureidkey="properties.district",
    color="Accessibility Level",
    hover_name="District",
    hover_data={
        "Score": ":.4f",
        "Rank": True,
        "Accessibility Level": True
    },
    color_discrete_map={
        "Low": "#FF0000",
        "Medium": "#B8860B",
        "High": "#006400"
    }
)

# 8. DISTRICT NAME AND RANK LABELS
fig.add_trace(
    go.Scattergeo(
        lon=labels["lon"],
        lat=labels["lat"],
        text=[
            (
                f"<b>{name}</b><br>Rank: {int(rank)}"
                if pd.notna(rank)
                else f"<b>{name}</b><br>Rank: No Data"
            )
            for name, rank in zip(
                labels["District"], labels["Rank"]
            )
        ],
        mode="text",
        textfont=dict(size=10, color="black"),
        hoverinfo="text",
        showlegend=False
    )
)

# 9. MAP SETTINGS
fig.update_geos(
    fitbounds="locations",
    visible=False
)

fig.update_layout(
    height=500,
    margin=dict(r=0, t=5, l=0, b=0)
)

# 10. DISPLAY MAP
st.plotly_chart(
    fig,
    use_container_width=True
)

# 11. RESULT TABLE
st.subheader("District Accessibility Result")

result_table = df[
    ["District", "Score", "Rank", "Accessibility Level"]
].sort_values("Rank")

st.dataframe(
    result_table,
    use_container_width=True
)

