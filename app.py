# ---------- Simple Land Outline Subdivision App ----------
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon, box

# ---------- Page Setup ----------
st.set_page_config(page_title="Land Subdivision Planner", layout="wide")
st.title("🏗️ Land Subdivision Planner")
st.write(
    "Define the outline of a parcel by entering side lengths. "
    "The app draws the shape and performs a simple equal‑sized subdivision."
)

# ---------- Land Dimensions Input ----------
st.sidebar.header("Land Outline Input")

# For simplicity, start with a rectangular outline.
length = st.sidebar.number_input("Length of Land (meters)", min_value=1.0, value=100.0)
width = st.sidebar.number_input("Width of Land (meters)", min_value=1.0, value=60.0)

# Number of desired subdivisions
rows = st.sidebar.slider("Number of Rows", 1, 10, 2)
cols = st.sidebar.slider("Number of Columns", 1, 10, 3)

# ---------- Build the Land Polygon ----------
# The coordinates (0,0) → (length, width)
outline = box(0, 0, length, width)

# Calculate lot size
lot_length = length / cols
lot_width = width / rows

# ---------- Build Sub‑lots ----------
lots = []
for i in range(cols):
    for j in range(rows):
        x0 = i * lot_length
        y0 = j * lot_width
        x1 = x0 + lot_length
        y1 = y0 + lot_width
        lot = box(x0, y0, x1, y1)
        lots.append(lot)

# ---------- Visualize the Land and Subdivisions ----------
fig, ax = plt.subplots(figsize=(7, 5))
x, y = outline.exterior.xy
ax.plot(x, y, color="black", linewidth=2, label="Land Outline")

for lot in lots:
    x, y = lot.exterior.xy
    ax.plot(x, y, color="blue", linewidth=0.8)

ax.set_aspect("equal")
ax.set_xlabel("Meters (X)")
ax.set_ylabel("Meters (Y)")
ax.set_title("Simple Land Subdivision")
ax.legend()
st.pyplot(fig, clear_figure=True)

# ---------- Summary ----------
total_area = outline.area
lot_area = lots[0].area if lots else 0
st.markdown(f"**Total Land Area:** {total_area:,.2f} m²")
st.markdown(f"**Each Lot Area:** {lot_area:,.2f} m²")
st.markdown(f"**Number of Lots:** {len(lots)}")








