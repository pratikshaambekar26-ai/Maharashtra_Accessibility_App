import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.title("Maharashtra District Accessibility Map")

file = st.file_uploader("Upload Excel File", type=["xlsx"])

if file is not None:

    df = pd.read_excel(file, sheet_name="Final Result")

    with open("maharashtra.geojson", "r", encoding="utf-8") as f:
        geojson = json.load(f)

    st.subheader("District Accessibility Map")

    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="District Name (district_name)",
        featureidkey="properties.district",
        color="Overall Accessibility Score",
        hover_name="District Name (district_name)",
        hover_data={
            "Overall Accessibility Score": True,
            "Rank": True
        },
        color_continuous_scale="Viridis"
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig.update_layout(
        height=700,
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("District Accessibility Result")

    st.dataframe(df)