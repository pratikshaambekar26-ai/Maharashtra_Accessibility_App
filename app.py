fig = px.choropleth(
    df,
    geojson=geojson,
    locations="District Name (district_name)",
    featureidkey="properties.district",
    color="Accessibility Level",
    hover_name="District Name (district_name)",
    hover_data={
        "Overall Accessibility Score": ":.4f",
        "Rank": True,
        "Accessibility Level": True
    },
    color_discrete_map={
        "Low": "#8B0000",
        "Medium": "#B8860B",
        "High": "#006400"
    }
)

fig.add_trace(
    go.Scattergeo(
        lon=labels["lon"],
        lat=labels["lat"],
        text=[
            f"{name}<br>Rank: {rank}"
            for name, rank in zip(
                labels["District"],
                labels["Rank"]
            )
        ],
        mode="text",
        textfont=dict(
            size=11,
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

fig.update_geos(
    fitbounds="locations",
    visible=False,
    projection_scale=1
)

fig.update_layout(
    height=420,
    margin=dict(
        r=0,
        t=5,
        l=0,
        b=0
    )
)


     
        
