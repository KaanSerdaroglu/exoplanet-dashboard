import sqlite3
import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Exoplanets — understand the magic of the universe!", page_icon="🌚", layout="wide")

conn = sqlite3.connect("nasaexo.db")
query = """ SELECT pl_name, hostname, pl_orbper, pl_rade, discoverymethod, disc_year, sy_snum, sy_pnum FROM exoplanets WHERE pl_orbper IS NOT NULL AND pl_rade IS NOT NULL; """
df = pd.read_sql_query(query, conn)
conn.close()

st.title("Exoplanet Explorer")
st.write(f"Showing {df.shape[0]} confirmed exoplanets")

# Multiselect: lets the user choose which discovery methods to show, defaulting to all of them selected
selected_methods = st.sidebar.multiselect(
    "Discovery methods to show",
    options=df["discoverymethod"].unique(),
    default=df["discoverymethod"].unique(),
)

# Slider: lets the user pick a min/max year range
year_range = st.sidebar.slider(
    "Discovery year range",
    min_value=int(df["disc_year"].min()),
    max_value=int(df["disc_year"].max()),
    value=(int(df["disc_year"].min()), int(df["disc_year"].max())),
)

# Search logic
search_name = st.sidebar.text_input("Search for a planet by name")

# Keep only rows matching both the selected methods and the selected year range
filtered_df = df[df["discoverymethod"].isin(selected_methods) & df["disc_year"].between(year_range[0], year_range[1])]

# This block only runs if the user has actually typed something
if search_name:
   filtered_df = filtered_df[filtered_df["pl_name"].str.contains(search_name, case=False, na=False)]

csv_data = filtered_df.to_csv(index=False)
st.sidebar.download_button(
   label=f"Download {filtered_df.shape[0]} planets as CSV",
   data=csv_data,
   file_name="filtered_exoplanets.csv",
   mime="text/csv",
)

col1, col2, col3 = st.columns(3)
col1.metric("Planets shown", filtered_df.shape[0])
col2.metric("Avg radius", round(filtered_df["pl_rade"].mean(), 2) if not filtered_df.empty else "N/A")
col3.metric("Avg orbital period", round(filtered_df["pl_orbper"].mean(), 1) if not filtered_df.empty else "N/A")

if search_name:
    display_df = filtered_df[["pl_name", "hostname", "discoverymethod", "disc_year", "pl_orbper", "pl_rade"]].reset_index(drop=True)
    display_df.columns = ["Planet Name", "Host Star", "Discovery Method", "Discovery Year", "Orbital Period (days)", "Radius (Earth Radii)"]
    st.dataframe(display_df)

st.markdown("---")

with st.expander("🔎 Planet Finder", expanded=True):

    finder_property = st.selectbox(
        "Find by",
        [
            "Largest radius",
            "Smallest radius",
            "Longest orbital period",
            "Shortest orbital period",
            "Earliest discovery",
            "Most recent discovery",
        ]
    )

    if not filtered_df.empty:

        if finder_property == "Largest radius":
            result = filtered_df.loc[filtered_df["pl_rade"].idxmax()]
            value = f"{result['pl_rade']:.2f} R⊕"

        elif finder_property == "Smallest radius":
            result = filtered_df.loc[filtered_df["pl_rade"].idxmin()]
            value = f"{result['pl_rade']:.2f} R⊕"

        elif finder_property == "Longest orbital period":
            result = filtered_df.loc[filtered_df["pl_orbper"].idxmax()]
            value = f"{result['pl_orbper']:.2f} days"

        elif finder_property == "Shortest orbital period":
            result = filtered_df.loc[filtered_df["pl_orbper"].idxmin()]
            value = f"{result['pl_orbper']:.2f} days"

        elif finder_property == "Earliest discovery":
            result = filtered_df.loc[filtered_df["disc_year"].idxmin()]
            value = str(int(result["disc_year"]))

        elif finder_property == "Most recent discovery":
            result = filtered_df.loc[filtered_df["disc_year"].idxmax()]
            value = str(int(result["disc_year"]))

        finder_col1, finder_col2, finder_col3 = st.columns(3)

        finder_col1.metric("Planet", result["pl_name"])
        finder_col2.metric(finder_property, value)
        finder_col3.metric("Host Star", result["hostname"])

    else:
        st.warning("No planets match the current filters.")

st.markdown("---")

# NASA Exoplanet Explorer
with st.expander("🌌 NASA Exoplanet Explorer", expanded=True):
    if not filtered_df.empty:
        planet_name = result["pl_name"]

        # Convert planet name into NASA URL format
        nasa_planet_name = (
            planet_name
            .lower()
            .replace(" ", "-")
        )

        nasa_url = (
            f"https://science.nasa.gov/exoplanet-catalog/"
            f"{nasa_planet_name}/"
        )

        st.write(
            f"Explore **{planet_name}** using NASA's Exoplanet Catalog"
        )

        st.link_button(
            "🚀 Open NASA Exoplanet Catalog",
            nasa_url
        )

        st.caption(
            "Interactive 3D visualization and planet information provided by NASA Science."
        )

    else:
        st.warning("No planet is available to explore.")

st.markdown("---")

# Planet Comparison
with st.expander("🪐 Planet Comparison", expanded=True):
    if filtered_df.empty:
        st.warning("No planets are available for comparison.")
    elif len(filtered_df) < 2:
        st.info("At least two planets are required for comparison.")
    else:

        comparison_options = filtered_df["pl_name"].drop_duplicates().tolist()

        selected_planets = st.multiselect(
            "Select 2–3 planets to compare",
            options=comparison_options,
            max_selections=3,
            placeholder="Choose planets..."
        )

        if len(selected_planets) >= 2:
            comparison_df = filtered_df[
                filtered_df["pl_name"].isin(selected_planets)
            ].copy()

            # Keep the selected order
            comparison_df["selection_order"] = pd.Categorical(
                comparison_df["pl_name"],
                categories=selected_planets,
                ordered=True
            )

            comparison_df = comparison_df.sort_values("selection_order")

            # Create comparison table
            comparison_table = comparison_df[
                [
                    "pl_name",
                    "hostname",
                    "discoverymethod",
                    "disc_year",
                    "pl_orbper",
                    "pl_rade",
                    "sy_pnum",
                ]
            ].copy()

            comparison_table.columns = [
                "Planet",
                "Host Star",
                "Discovery Method",
                "Discovery Year",
                "Orbital Period (days)",
                "Radius (R⊕)",
                "Planets in System",
            ]

            # Round numerical values
            comparison_table["Orbital Period (days)"] = (
                comparison_table["Orbital Period (days)"].round(2)
            )

            comparison_table["Radius (R⊕)"] = (
                comparison_table["Radius (R⊕)"].round(2)
            )

            st.dataframe(
                comparison_table,
                use_container_width=True,
                hide_index=True
            )

            # Visual comparison
            st.markdown("### 📊 Visual Comparison")

            chart_df = comparison_df[
                ["pl_name", "pl_orbper", "pl_rade"]
            ].copy()

            chart_df = chart_df.melt(
                id_vars="pl_name",
                var_name="Property",
                value_name="Value"
            )

            chart_df["Property"] = chart_df["Property"].replace({
                "pl_orbper": "Orbital Period",
                "pl_rade": "Radius"
            })

            fig_comparison = px.bar(
                chart_df,
                x="pl_name",
                y="Value",
                color="Property",
                barmode="group",
                labels={
                    "pl_name": "Planet",
                    "Value": "Value",
                    "Property": "Property"
                },
                template="plotly_dark"
            )

            for trace in fig_comparison.data:

                if trace.name == "Orbital Period":
                    trace.hovertemplate = (
                        "<b>%{x}</b><br>"
                        "Orbital Period: %{y:.2f} days"
                        "<extra></extra>"
                    )

                elif trace.name == "Radius":
                    trace.hovertemplate = (
                        "<b>%{x}</b><br>"
                        "Radius: %{y:.2f} R⊕"
                        "<extra></extra>"
                    )

            fig_comparison.update_layout(
                legend_title_text="",
                xaxis_title="",
                yaxis_title="Value",
            )

            st.plotly_chart(
                fig_comparison,
                use_container_width=True
            )

        else:
            st.info("Select at least two planets to compare.")

tab0, tab1, tab2, tab3, tab4 = st.tabs(["About", "Orbital Period vs Radius", "Discoveries per Year", "Radius Distribution", "Star Systems"])

with tab0:
  st.markdown(f"""
    ## About this project

    This dashboard explores **{df.shape[0]} confirmed exoplanets** (out of 6,372 in
    NASA's full archive — the rest are missing either an orbital period or radius
    measurement and are excluded here) from NASA's
    [Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/)

    Use the sidebar to filter by discovery method, year, or planet name, and the
    tools and tabs below to explore the data.

    ### Tools

    - **🔎 Planet Finder** — instantly surfaces the extreme in your current filtered
      selection (largest, smallest, longest/shortest orbit, earliest/most recent
      discovery).
    - **🌌 NASA Exoplanet Explorer** — links out to NASA's own catalog for whichever
      planet Planet Finder is currently showing.
    - **🪐 Planet Comparison** — pick 2–3 planets from the current filter and see
      them side by side, both as a table and a grouped bar chart.
    - **Download button** (sidebar) — exports whatever's currently filtered as CSV.

    ### What each tab shows

    - **Orbital Period vs Radius** — each point is one planet, colored by how it
        was discovered. Look at the lower-left: a cluster of large planets with very
        short orbital periods are "hot Jupiters" — gas giants that orbit extremely
        close to their star.
    - **Discoveries per Year** — how many planets were confirmed each year.
    - **Radius Distribution** — a histogram of planet sizes on a log scale.
    - **Star Systems** — how many planets/stars a typical system has, and whether
        planets in multi-star systems tend to differ in size from those orbiting a
        single star.

    ### Findings

    - **The "radius gap"**: this dataset shows a real dip in planet counts between
        roughly **1.7–2.0 Earth radii**, matching a genuine, actively-researched
        astrophysics phenomenon (sometimes called the Fulton gap, after
        *Fulton et al. 2017*). It's thought to mark the boundary between rocky
        super-Earths and gas-rich mini-Neptunes, possibly caused by
        atmospheric loss from stellar radiation.
    - **Discovery spikes in 2014 and 2016**: both trace back to the Kepler Space
        Telescope. Kepler found thousands of planet *candidates* faster than they
        could be confirmed one by one, so these years mark large batch-validation
        announcements rather than a smooth year-over-year increase.
    - **Hot Jupiters**: visible as a distinct cluster in the scatter plot —
        unusually large planets with unusually short orbital periods, a category
        that surprised astronomers when first discovered since it doesn't fit
        how our own solar system formed.
    - **Most systems are simple**: the large majority of confirmed systems have
        just one known planet and one star — multi-planet and multi-star systems
        exist but are the minority in this dataset (partly a real effect, partly a
        detection bias, since finding every planet in a system is harder than
        finding just one).

    ### Data & tools

    Built with Python, SQLite, pandas, Plotly, and Streamlit. Source code
    and the full pipeline (API fetch → database → analysis → this dashboard)
    available on [GitHub](#).
""")

with tab1:
  if filtered_df.empty:
      st.warning("No planets match the current filters.")
  else:
      fig = px.scatter(
          filtered_df,
          x="pl_orbper",
          y="pl_rade",
          color="discoverymethod",
          hover_name="pl_name",
          log_x=True,
          labels={
              "pl_orbper": "Orbital Period (days)",
              "pl_rade": "Planet Radius (Earth radii)",
              "discoverymethod": "Discovery Method",
          },
          template="plotly_dark",
      )
      fig.update_traces(
          hovertemplate="<b>%{hovertext}</b><br>Orbital Period: %{x:.2f} days<br>Radius: %{y:.2f} R⊕<extra></extra>"
      )
      st.plotly_chart(fig, use_container_width=True)

with tab2:
  if filtered_df.empty:
      st.warning("No planets match the current filters.")
  else:
      yearly_counts = filtered_df.groupby("disc_year").size().reset_index(name="count")
      fig2 = px.bar(
          yearly_counts,
          x="disc_year",
          y="count",
          labels={"disc_year": "Discovery Year", "count": "Number of Planets Discovered"},
          template="plotly_dark",
      )
      fig2.update_traces(
          hovertemplate="Year: %{x}<br>Discoveries: %{y}<extra></extra>"
      )
      st.plotly_chart(fig2, use_container_width=True)

with tab3:
  if filtered_df.empty:
      st.warning("No planets match the current filters.")
  elif filtered_df["pl_rade"].nunique() < 2:
     # .nunique() counts how many distinct values exist in a column
     st.info("Not enough distinct radius values in the current selection to show a distribution.")
  else:
      bins = np.logspace(np.log10(filtered_df["pl_rade"].min()), np.log10(filtered_df["pl_rade"].max()), 50)
      bin_midpoints = (bins[:-1] + bins[1:]) / 2  # one midpoint per bin, for plotting
      binned = pd.cut(filtered_df["pl_rade"], bins=bins, include_lowest=True)
      counts = binned.value_counts().sort_index()

      fig3 = px.bar(
          x=bin_midpoints,
          y=counts.values,
          labels={"x": "Planet Radius (Earth radii)", "y": "Number of Planets"},
          template="plotly_dark",
      )
      fig3.update_traces(
          hovertemplate="Radius: %{x:.2f} R⊕<br>Count: %{y}<extra></extra>"
      )
      fig3.update_layout(xaxis_type="log")
      st.plotly_chart(fig3, use_container_width=True)

with tab4:
    if filtered_df.empty:
        st.warning("No planets match the current filters.")
    else:
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("#### Planets per System")
            planets_per_system = filtered_df.groupby("sy_pnum").size().reset_index(name="count")
            planets_per_system["pct"] = (planets_per_system["count"] / planets_per_system["count"].sum() * 100).round(1)
            planets_per_system["sy_pnum"] = planets_per_system["sy_pnum"].astype(str)

            fig4 = px.bar(
                planets_per_system,
                x="sy_pnum",
                y="count",
                text=planets_per_system["pct"].astype(str) + "%",
                color="sy_pnum",
                color_discrete_sequence=px.colors.sequential.Plasma,
                template="plotly_dark",
            )
            fig4.update_traces(
                hovertemplate="Systems with this many planets: %{y}<br>Share: %{text}<extra></extra>",
                textposition="outside",
            )
            fig4.update_layout(
                xaxis_title="Planets in System",
                yaxis_title="Number of Systems",
                showlegend=False,
                title="How many planets do systems typically have?",
            )
            st.plotly_chart(fig4, use_container_width=True)

        with col_b:
            st.markdown("#### Single vs. Multi-Star Systems")
            filtered_df = filtered_df.copy()
            filtered_df["star_category"] = filtered_df["sy_snum"].apply(
                lambda n: "Single star" if n == 1 else "Multiple stars (binary/triple+)"
            )
            star_counts = filtered_df["star_category"].value_counts().reset_index()
            star_counts.columns = ["star_category", "count"]

            fig5 = px.pie(
                star_counts,
                names="star_category",
                values="count",
                hole=0.5,
                color_discrete_sequence=["#636EFA", "#EF553B"],
                template="plotly_dark",
            )
            fig5.update_traces(
                textinfo="percent+label",
                hovertemplate="%{label}<br>%{value} planets<extra></extra>",
                pull=[0, 0.08],
            )
            fig5.update_layout(
                showlegend=False,
                title="What fraction of planets orbit in multi-star systems?",
            )
            st.plotly_chart(fig5, use_container_width=True)

        st.markdown("#### Does being in a multi-star system relate to planet size?")
        fig6 = px.box(
            filtered_df,
            x="star_category",
            y="pl_rade",
            color="star_category",
            color_discrete_sequence=["#636EFA", "#EF553B"],
            template="plotly_dark",
            log_y=True,
            labels={"star_category": "", "pl_rade": "Planet Radius (Earth radii)"},
        )
        fig6.update_traces(
            hovertemplate="Radius: %{y:.2f} R⊕<extra></extra>"
        )
        fig6.update_layout(showlegend=False)
        st.plotly_chart(fig6, use_container_width=True)

# Streamlit treats the entire script as something to be replayed on every interaction, and widgets just remember their last value across reruns