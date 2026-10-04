"""
Early draft — static matplotlib charts, created before the project moved to
an interactive Plotly + Streamlit dashboard (see app.py). Kept here to show
the project's progression, not meant to be run as part of the current pipeline.
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

conn = sqlite3.connect("nasaexo.db")

query = """SELECT pl_orbper, pl_rade, discoverymethod FROM exoplanets WHERE pl_orbper IS NOT NULL AND pl_rade IS NOT NULL;"""

df = pd.read_sql_query(query, conn)

# Get the list of distinct discovery methods present in the data so that we can plot each one as its own color
methods = df["discoverymethod"].unique()

# One scatter call per method, matplotlib auto-assigns each a different color and adds it to the legend via label=method
for method in methods:
  # Boolean indexing: keep only the rows where discoverymethod matches this specific method same idea as a SQL WHERE clause, just done in pandas instead
  subset = df[df["discoverymethod"] == method]
  # alpha=0.6 makes points semi-transparent, so overlapping points show up as darker patches 
  plt.scatter(subset["pl_orbper"], subset["pl_rade"], label=method, alpha=0.6)

# Quick sanity checks in the terminal
print(df.head())
print(df.shape)

plt.xlabel("Orbital Period (days)")
plt.ylabel("Planet Radius (Earth radii)")
plt.title("Exoplanet Orbital Period vs Radius")

# Orbital periods range from under a day to tens of thousands of days - a linear axis would crush almost everything into the left edge
plt.xscale("log")

plt.legend()
plt.show()

# Setting the bar chart 
query2 = """SELECT disc_year, COUNT(*) AS num_discoveries FROM exoplanets GROUP BY disc_year ORDER BY disc_year;"""
df = pd.read_sql_query(query2, conn)
print(df.head())
print(df.shape)

plt.figure()
plt.bar(df["disc_year"], df["num_discoveries"])

plt.xlabel("Discovery Year")
plt.ylabel("Number of Planets Discovered")
plt.title("Exoplanet Discoveries Per Year")
plt.show()

# Setting the histogram
query3 = """ SELECT pl_rade FROM exoplanets WHERE pl_rade IS NOT NULL; """
df = pd.read_sql_query(query3, conn)
conn.close()
print(df.head())
print(df.shape)

plt.figure()
bins = np.logspace(np.log10(df["pl_rade"].min()), np.log10(df["pl_rade"].max()), 50)
plt.hist(df["pl_rade"], bins=bins)
plt.xscale("log")

plt.xlabel("Planet Radius (Earth radii)")
plt.ylabel("Number of Planets")
plt.title("Distribution of Exoplanet Radii")
plt.show()
