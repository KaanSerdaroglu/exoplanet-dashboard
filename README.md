# 🪐 Exoplanet Explorer

An interactive dashboard exploring NASA's full archive of confirmed exoplanets — built as an end-to-end data pipeline: fetch → store → analyze → visualize.

Built with Python, SQLite, pandas, Plotly, and Streamlit

## What it does

- Pulls ~6,372 confirmed exoplanets directly from NASA's [Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/) via their public TAP API (no auth required)
- Stores the data in a local SQLite database
- Serves an interactive Streamlit dashboard with:
  - Live filtering by discovery method, year range, and planet name search
  - A searchable/sortable results table with CSV export
  - A **Planet Finder** tool (largest/smallest, longest/shortest orbit, earliest/latest discovery in the current filter)
  - A **Planet Comparison** tool (side-by-side stats + chart for 2–3 chosen planets)
  - Direct links out to NASA's own catalog
  - Five analytical views: orbital period vs. radius, discoveries per year, radius distribution, and system-level stats (planets/stars per system)

## Findings

- **The "radius gap"**: a measurable dip in planet counts between ~1.7–2.0 Earth radii, matching the real, published "Fulton gap" (Fulton et al. 2017) — the boundary between rocky super-Earths and gas-rich mini-Neptunes.
- **Discovery spikes in 2014 and 2016**: both trace back to the Kepler Space Telescope's large batch-validation announcements, rather than steady year-over-year growth.
- **Hot Jupiters**: a visible cluster of large planets with very short orbital periods — gas giants orbiting extremely close to their star.

## Project structure

```
exoplanet_analyzer/
├── setup_db.py            # creates the SQLite schema
├── fetch_exoplanets.py    # pulls data from NASA's API and loads it into SQLite
├── app.py                 # the Streamlit dashboard
├── requirements.txt
├── legacy/
│   └── matplotlib_version.py   # an earlier static-chart draft, kept for reference
└── nasaexo.db              # generated locally — not tracked in this repo
```

## Running it locally

```bash
git clone https://github.com/KaanSerdaroglu/exoplanet-dashboard.git
cd exoplanet-dashboard

# create and activate a virtual environment (keeps dependencies isolated from the rest of your system)
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# install dependencies
python3 -m pip install -r requirements.txt
# if `python3`/`pip` aren't recognized, try `python` / `pip3` instead

python3 setup_db.py
python3 fetch_exoplanets.py
streamlit run app.py
# if `streamlit` isn't recognized as a command, use: python3 -m streamlit run app.py
```

When you're done, exit the virtual environment with `deactivate`.

## Data source

[NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/), operated by Caltech/IPAC under contract with NASA. Queried live via their public [TAP service](https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html) — no API key required.
