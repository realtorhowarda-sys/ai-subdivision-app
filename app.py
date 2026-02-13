# ---------- app.py ----------
import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

# --- Page setup ---
st.set_page_config(page_title="AI Subdivision Mapper", layout="wide")
st.title("🏗️ AI Subdivision Mapper (Base Version)")
st.write("Upload an image of a property and preview a preliminary subdivision layout.")

# --- Sidebar controls ---
st.sidebar.title("Controls")
num_lots = st.sidebar.slider("Number of lots", 2, 40, 8)

# --- File uploader ---
uploaded_file = st.file_uploader("Upload a property image (JPEG or PNG)", type=["jpg", "png"])

# --- Processing logic ---
if uploaded_file is not None:
    # Decode image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    st.image(image, caption="Original Property Image", use_container_width=True)

    # -----  Basic segmentation placeholder -----
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # Simple threshold to separate rough land
    _, mask = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY_INV)

    # Display segmentation preview
    st.subheader("Detected Land (placeholder segmentation)")
    st.image(mask, use_container_width=True, caption="Land mask (to be replaced with real AI segmentation)")

    # -----  Subdivision logic -----
    coords = np.column_stack(np.where(mask > 0))
    if len(coords) > 10:
        polygon = Polygon(coords)
        minx, miny, maxx, maxy = polygon.bounds

        cols = int(np.sqrt(num_lots))
        rows = int(np.ceil(num_lots / cols))
        width = (maxx - minx) / cols
        height = (maxy - miny) / rows

        lots = []
        for i in range(cols):
            for j in range(rows):
                if len(lots) < num_lots:
                    lot = Polygon([
                        (minx + i * width, miny + j * height),
                        (minx + (i + 1) * width, miny + j * height),
                        (minx + (i + 1) * width, miny + (j + 1) * height),
                        (minx + i * width, miny + (j + 1) * height)
                    ])
                    lots.append(lot)

        # Draw the lots
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(mask, cmap="gray")
        for lot in lots:
            x, y = lot.exterior.xy
            ax.plot(y, x, 'r', linewidth=1)
        ax.axis("off")
        st.subheader("Generated Subdivision Layout")
        st.pyplot(fig)
    else:
        st.warning("Could not detect usable land area.")
else:
    st.info("Upload an aerial or satellite image to start.")
# ---------- end app.py ----------
