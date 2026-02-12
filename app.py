import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

st.set_page_config(page_title="AI Subdivision App", layout="centered")

st.title("🏗️ AI Subdivision Planner (Starter)")

uploaded_file = st.file_uploader("Upload a property image", type=["jpg", "png"])

num_lots = st.slider("Number of lots", min_value=2, max_value=20, value=4)

if uploaded_file is not None:
    # Read image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    st.image(image, caption="Uploaded Property", use_container_width=True)

    # Simple segmentation
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    _, mask = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY_INV)

    # Create land polygon
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
                        (minx + i*width, miny + j*height),
                        (minx + (i+1)*width, miny + j*height),
                        (minx + (i+1)*width, miny + (j+1)*height),
                        (minx + i*width, miny + (j+1)*height),
                    ])
                    lots.append(lot)

        # Plot result
        fig, ax = plt.subplots(figsize=(6,6))
        ax.imshow(mask, cmap='gray')

        for lot in lots:
            x, y = lot.exterior.xy
            ax.plot(y, x, 'r')

        ax.axis("off")
        st.pyplot(fig)
    else:

        st.warning("Could not detect land area clearly. Try another image.")
        "remove Jupyter magic line"
