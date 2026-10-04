import sqlite3
import requests

url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
params = {
    "query": "SELECT pl_name, hostname, disc_year, discoverymethod, pl_orbper, pl_bmasse, pl_rade, pl_eqt, sy_snum, sy_pnum FROM ps WHERE default_flag=1",
    "format": "json",
}
#default_flag=1 filters to one row per confirmed planet

response = requests.get(url, params=params)
planets = response.json()  #list of dicts

conn = sqlite3.connect("nasaexo.db")
cursor = conn.cursor()

for planet in planets:
  cursor.execute("""
    INSERT OR IGNORE INTO exoplanets
      (pl_name, hostname, disc_year, discoverymethod, pl_orbper, pl_bmasse, pl_rade, pl_eqt, sy_snum, sy_pnum)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
""", (
      planet["pl_name"],
      planet["hostname"],
      planet["disc_year"],
      planet["discoverymethod"],
      planet["pl_orbper"],
      planet["pl_bmasse"],
      planet["pl_rade"],
      planet["pl_eqt"],
      planet["sy_snum"],
      planet["sy_pnum"],
))
# VALUES (?, ?, ...) since this data is coming from an API response, not something typed myself

# since each dict has keys matching column names exactly pull values out with planet["pl_name"], planet["hostname"], etc.

conn.commit()
conn.close()

print(f"Fetched {len(planets)} planets from the API.")