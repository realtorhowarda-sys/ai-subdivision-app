# ---------- Land Subdivision Planner (Length + Angle) ----------
import streamlit as st
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import math

# ---------- Page Setup ----------
st.set_page_config(page_title="Land Subdivision Planner", layout="wide")
st.title("🏗️ Land Subdivision Planner")

st.write(
    "Define a parcel by entering side lengths and angles. "
    "Angles are measured in degrees (0° = East, 90° = North)."
)

# ---------- Sidebar Inputs ----------
st.sidebar.header("Land Outline")

num_sides = st.sidebar.slider("Number of sides", 3, 10, 4)

sides = []
for i in range(num_sides):
    st.sidebar.subheader(f"Side {i + 1}")
    length = st.sidebar.number_input(
        f"Length (m) – Side {i + 1}",
        min_value=1.0,
        value=50.0,
        key=f"len_{i}",
    )
    angle = st.sidebar.number_input(
        f"Angle (degrees) – Side {i + 1}",
        min_value=0.0,
        max_value=360.0,
        value=90.0,
        key=f"ang_{i}",
    )
    sides.append((length, angle))

# ---------- Build Polygon ----------
points = [(0.0, 0.0)]
x, y = 0.0, 0.0

for length, angle in sides:
    rad = math.radians(angle)
    dx = length * math.cos(rad)
    dy = length * math.sin(rad)
    x += dx
    y += dy
    points.append((x, y))

# Close polygon
points.append(points[0])

land_poly = Polygon(points)

# ---------- Plot ----------
fig, ax = plt.subplots(figsize=(7, 6))

xs, ys = zip(*points)
ax.plot(xs, ys, color="black", linewidth=2, marker="o")

ax.set_aspect("equal")
ax.set_xlabel("Meters (X)")
ax.set_ylabel("Meters (Y)")
ax.set_title("Land Outline")

st.pyplot(fig, clear_figure=True)

# ---------- Validation ----------
if not land_poly.is_valid:
    st.warning("⚠️ Polygon is invalid (self‑intersection or overlap).")
else:
    st.success("✅ Polygon is valid.")

st.markdown(f"**Area:** {land_poly.area:,.2f} m²")
st.markdown(f"**Perimeter:** {land_poly.length:,.2f} m")
