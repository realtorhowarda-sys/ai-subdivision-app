# ---------- Land Subdivision Planner (Length + Angle) ----------
from shapely.geometry import box
from shapely.ops import unary_union
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

st.sidebar.header("Subdivision")
num_lots = st.sidebar.slider("Number of lots", 2, 20, 6)

def subdivide_polygon_vertical(poly, n_lots):
    """
    Subdivide a polygon into n_lots using vertical strips.
    Returns a list of lot polygons.
    """
    minx, miny, maxx, maxy = poly.bounds
    width = (maxx - minx) / n_lots

    lots = []
    for i in range(n_lots):
        x0 = minx + i * width
        x1 = minx + (i + 1) * width
        strip = box(x0, miny, x1, maxy)

        piece = poly.intersection(strip)
        if not piece.is_empty:
            if piece.geom_type == "Polygon":
                lots.append(piece)
            else:
                # Handle MultiPolygon by merging
                lots.append(unary_union(piece))

    return lots

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

    # --- Subdivision ---
    lots = subdivide_polygon_vertical(land_poly, num_lots)

    # --- Plot lots ---
    fig2, ax2 = plt.subplots(figsize=(7, 6))

    # Land outline
    x, y = land_poly.exterior.xy
    ax2.plot(x, y, color="black", linewidth=2)

    # Lots
    for i, lot in enumerate(lots, start=1):
        lx, ly = lot.exterior.xy
        ax2.plot(lx, ly, linewidth=1)
        cx, cy = lot.centroid.xy
        ax2.text(cx[0], cy[0], str(i), ha="center", va="center")

    ax2.set_aspect("equal")
    ax2.set_title("Subdivision Layout")
    ax2.set_xlabel("Meters (X)")
    ax2.set_ylabel("Meters (Y)")

    st.pyplot(fig2, clear_figure=True)

    # --- Summary ---
    areas = [lot.area for lot in lots]
    st.markdown(f"**Number of Lots:** {len(lots)}")
    st.markdown(f"**Average Lot Area:** {sum(areas)/len(areas):,.2f} m²")

st.markdown(f"**Area:** {land_poly.area:,.2f} m²")
st.markdown(f"**Perimeter:** {land_poly.length:,.2f} m")


