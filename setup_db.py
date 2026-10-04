import sqlite3

conn = sqlite3.connect("nasaexo.db")
cursor = conn.cursor()
print("Connected succesfully")

cursor.execute("""
CREATE TABLE IF NOT EXISTS exoplanets (
    pl_name   TEXT PRIMARY KEY,
    hostname  TEXT,
    disc_year INTEGER,
    discoverymethod TEXT,
    pl_orbper REAL,
    pl_bmasse REAL,
    pl_rade   REAL,
    pl_eqt  INTEGER,
    sy_snum INTEGER,
    sy_pnum INTEGER
)
 """)

# pl_name	--> planet name
# hostname -->	the star it orbits
# disc_year	--> year discovered
# discoverymethod	
# pl_orbper	--> orbital period, in days
# pl_bmasse	--> planet mass, in Earth masses
# pl_rade	--> planet radius, in Earth radii
# pl_eqt	--> equilibrium temperature, in Kelvin
# sy_snum	--> number of stars in that system
# sy_pnum	--> number of planets in that system

conn.commit()
conn.close()
print("Table created")