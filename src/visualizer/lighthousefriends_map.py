from __future__ import annotations

import json
import os

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from cartopy.io import shapereader

# --- Paths ---
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
INPUT = os.path.join(ROOT, "data", "processed", "lighthousefriends_latlongs.json")
OUT_PNG = os.path.join(ROOT, "maps", "lighthousefriends_map_conus.png")
OUT_SVG = os.path.join(ROOT, "maps", "lighthousefriends_map_conus.svg")

# --- Data ---
with open(INPUT, "r", encoding="utf-8") as f:
    records = json.load(f)


# Plot only points inside a simple CONUS bbox
# (roughly: west=-125, east=-66.5, south=24, north=50)
def in_conus(lon, lat):
    return -125 <= lon <= -66.5 and 24 <= lat <= 50


lons = []
lats = []
for r in records:
    lon = r.get("longitude")
    lat = r.get("latitude")
    if lon is None or lat is None:
        continue
    if in_conus(lon, lat):
        lons.append(lon)
        lats.append(lat)

# --- Map setup ---
proj = ccrs.AlbersEqualArea(
    central_longitude=-96, central_latitude=37.5, standard_parallels=(29.5, 45.5)
)
pc = ccrs.PlateCarree()

fig = plt.figure(figsize=(14, 9), facecolor="#030304")
ax = plt.axes(projection=proj)
OCEAN_COLOR = "#030304"  # nearly black
ax.set_facecolor(OCEAN_COLOR)  # nearly black for CAN/MEX and ocean
ax.set_extent([-125, -66.5, 23, 50], crs=pc)

# --- Draw only Lower 48 land using admin_1 states/provinces ---
# Load Natural Earth "admin_1_states_provinces" (1:50m) and filter to USA lower 48
shp = shapereader.natural_earth(
    resolution="50m", category="cultural", name="admin_1_states_provinces"
)
reader = shapereader.Reader(shp)
geoms = []
for rec in reader.records():
    props = rec.attributes
    # Keep only USA states
    if props.get("adm0_a3") != "USA":
        continue
    name = (props.get("name") or "").lower()
    # Skip Alaska, Hawaii, Puerto Rico, and other non-CONUS areas
    if name in ("alaska", "hawaii", "puerto rico"):
        continue
    # Optional: skip small offshore territories if they appear
    geoms.append(rec.geometry)

# Fill the selected states as the only visible land
ax.add_geometries(
    geoms,
    crs=pc,
    facecolor="#000000",  # black fill for continental US land
    edgecolor="#060607",  # subtle state borders
    linewidth=0.4,
    zorder=1,
)

# Optional: a faint coastline line (helps along seaboard)
coast = cfeature.NaturalEarthFeature(
    "physical", "coastline", "50m", edgecolor="#030304", facecolor="none"
)
ax.add_feature(coast, linewidth=0.6, zorder=2)

# --- Glow dots (white/yellow vibe without specifying colors) ---
# Outer halo
# ax.scatter(
#     lons, lats, s=200, transform=pc, alpha=0.01, linewidths=0, zorder=10, c="#fafad2"
# )
# # Middle halo
# ax.scatter(
#     lons, lats, s=100, transform=pc, alpha=0.02, linewidths=0, zorder=11, c="#fafad2"
# )
zorder = 10
# Halo glows
for size in range(1600, 40, -40):
    ax.scatter(
        lons,
        lats,
        s=size,
        transform=pc,
        alpha=0.03 / (size / 40),
        linewidths=0,
        zorder=zorder,
        c="#73730d",
    )
    zorder += 1


# Core
ax.scatter(
    lons, lats, s=5, transform=pc, alpha=1.0, linewidths=0, zorder=zorder, c="#fafad2"
)

# plt.title("U.S. Lighthouses — Lower 48 (glow map)", color="#e6e6e6", pad=16)
# plt.annotate(
#     "Data: lighthousefriends.com   Base: Natural Earth (public domain)",
#     xy=(1.0, 0.01),
#     xycoords="axes fraction",
#     ha="right",
#     va="bottom",
#     color="#70757d",
#     fontsize=9,
# )

os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
plt.savefig(
    OUT_PNG, dpi=250, bbox_inches="tight", facecolor="#ffffff", pad_inches=-0.01
)
plt.savefig(OUT_SVG, bbox_inches="tight", facecolor="#ffffff", pad_inches=-0.01)
print(f"wrote {OUT_PNG}\nwrote {OUT_SVG}")
plt.savefig(
    OUT_SVG,
    bbox_inches="tight",
    facecolor="#ffffff",
    pad_inches=-0.01,
)
print(f"wrote {OUT_PNG}\nwrote {OUT_SVG}")
