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
    page_icon="🗺️",
    layout="wide"
)

st.title("Maharashtra District Accessibility Map")


# ============================================================
# 1. READ ENTROPY METHOD EXCEL
# ============================================================

df = pd.read_excel(
    "Accessibility_Index_Entropy_Method (1).xlsx",
    sheet_name="Ranking"
)


# ============================================================
# 2. SELECT REQUIRED COLUMNS
# ============================================================

df = df[
    [
        "District",
        "Accessibility_Score",
        "Rank"
    ]
].copy()


# ============================================================
# 3. RENAME COLUMNS
# ============================================================

df = df.rename(columns={
    "Accessibility_Score": "Score"
})


# ============================================================
# 4. CLEAN SCORE AND RANK
# ============================================================

df["Score"] = pd.to_numeric(
    df["Score"],
    errors="coerce"
)

df["Rank"] = pd.to_numeric(
    df["Rank"],
    errors="coerce"
).astype("Int64")


# ============================================================
# 5. UPDATE DISTRICT NAMES
# ============================================================

new_names = {
    "Ahmednagar": "Ahilyanagar",
    "Aurangabad": "Chhatrapati Sambhajinagar",
    "Osmanabad": "Dharashiv"
}

df["District"] = df["District"].replace(new_names)


# ============================================================
# 6. ACCESSIBILITY LEVEL
# ============================================================

df["Accessibility Level"] = pd.cut(
    df["Score"],
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
# 7. READ MAHARASHTRA GEOJSON
# ============================================================

with open(
    "maharashtra.geojson",
    "r",
    encoding="utf-8"
) as f:
    geojson = json.load(f)


# ============================================================
# 8. UPDATE GEOJSON DISTRICT NAMES
# ============================================================

for feature in geojson["features"]:

    old_name = feature["properties"].get("district")

    if old_name in new_names:
        feature["properties"]["district"] = new_names[old_name]


# ============================================================
# 9. GET DISTRICT LABEL POSITIONS
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


# ============================================================
# 10. CREATE LABEL DATA
# ============================================================

label_data = []

for feature in geojson["features"]:

    district_name = feature["properties"].get(
        "district"
    )

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
# 11. MATCH RANK WITH DISTRICT
# ============================================================

labels = labels.merge(
    df[["District", "Rank"]],
    on="District",
    how="left"
)

labels["Rank"] = pd.to_numeric(
    labels["Rank"],
    errors="coerce"
).astype("Int64")


# ============================================================
# 12. MAP
# ============================================================

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

        "Low": "#B22222",

        "Medium": "#B8860B",

        "High": "#006400"

    }
)


# ============================================================
# 13. DISTRICT NAME + RANK ON MAP
# ============================================================

label_text = []

for name, rank in zip(
    labels["District"],
    labels["Rank"]
):

    if pd.notna(rank):

        label_text.append(
            f"<b>{name}</b><br>Rank: {int(rank)}"
        )

    else:

        label_text.append(
            f"<b>{name}</b><br>Rank: No Data"
        )


fig.add_trace(

    go.Scattergeo(

        lon=labels["lon"],

        lat=labels["lat"],

        text=label_text,

        mode="text",

        textfont=dict(

            size=9,

            color="black",

            family="Arial"
        ),

        hoverinfo="text",

        showlegend=False
    )
)


# ============================================================
# 14. MAP SETTINGS
# ============================================================

fig.update_geos(

    fitbounds="locations",

    visible=False,

    projection_type="mercator"
)


fig.update_layout(

    height=700,

    margin=dict(
        r=10,
        t=10,
        l=10,
        b=10
    ),

    legend=dict(
        title="Accessibility Level"
    )
)


# ============================================================
# 15. DISPLAY MAP
# ============================================================

st.plotly_chart(

    fig,

    use_container_width=True,

    config={
        "displayModeBar": True,
        "scrollZoom": True
    }
)


# ============================================================
# 16. ACCESSIBILITY LEVEL INFORMATION
# ============================================================

st.subheader("Accessibility Level")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        "🟢 **High** — Score > 0.60"
    )

with col2:
    st.markdown(
        "🟡 **Medium** — Score 0.40–0.60"
    )

with col3:
    st.markdown(
        "🔴 **Low** — Score ≤ 0.40"
    )


# ============================================================
# 17. RESULT TABLE
# ============================================================

st.subheader(
    "District Accessibility Result"
)


result_table = df[
    [
        "District",
        "Score",
        "Rank",
        "Accessibility Level"
    ]
].sort_values(
    "Rank"
)


result_table["Score"] = result_table[
    "Score"
].round(4)


st.dataframe(

    result_table,

    use_container_width=True,

    hide_index=True
)
