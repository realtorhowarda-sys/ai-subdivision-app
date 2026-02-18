# ---------- Land Subdivision Planner (Length + Angle) ----------
import streamlit as st
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import math

# ---------- Page Setup ----------
st.set_page_config(page_title="Land Subdivision Planner", layout="wide")
st.title("🏗️ Land Subdivision Planner")

st.write(
    "Define a parcel by entering side lengths and angles.\n\n"
    "**Angle convention:** 0° = East, 90° = North, 180° = West, 270° = South."
)

# ---------- Sidebar Inputs ----------
st.sidebar.header("Land Outline (Length + Angle)")

num_sides = st.sidebar.slider("Number of sides", 3, 10, 4)

sides = []
for i in range(num_sides):
    st.sidebar.subheader(f"Side {i + 1}")
    length = st.sidebar.number_input(
        f"Length (meters) – Side {i + 1}",
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

# ---------- Build Polygon Points ----------
points = [(0.0, 0.0)]
x, y = 0.0, 0.0

for length, angle in sides:
    rad = math.radians(angle)
    dx = length * math.cos(rad)
    dy = length * math.sin(rad)
    x += dx
    y += dy
    points.append((x, y))

# ---------- Closure Error (Fix #2) ----------
dx = points[-1][0] - points[0][0]
dy = points[-1][1] - points[0][1]
closure_error = (dx**2 + dy**2) ** 0.5

st.markdown(f"**Closure error:** {closure_error:.2f} meters")

# ---------- Close Polygon ----------
if points[-1] != points[0]:
    points.append(points[0])

# ---------- Build Polygon with Auto‑Fix (Fix #1) ----------
raw_polygon = Polygon(points)
land_poly = raw_polygon.buffer(0)

# ---------- Plot ----------
fig, ax = plt.subplots(figsize=(7, 6))
xs, ys = zip(*points)
ax.plot(xs, ys, color="black", linewidth=2, marker="o")

ax.set_aspect("equal")
ax.set_xlabel("Meters (X)")
ax.set_ylabel("Meters (Y)")
ax.set_title("Land Outline")

st.pyplot(fig, clear_figure=True)

# ---------- Validation Output ----------
if not land_poly.is_valid:
    st.error("❌ Polygon is invalid (self‑intersecting or overlapping).")
else:
    st.success("✅ Polygon is valid and ready for subdivision.")

st.markdown(f"**Area:** {land_poly.area:,.2f} m²")
st.markdown(f"**Perimeter:** {land_poly.length:,.2f} m")
