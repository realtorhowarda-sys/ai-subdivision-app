import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import torch
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator

# ---------- Helper Functions ----------

def clean_mask(mask):
    """Remove noise and fill holes in a binary mask."""
    mask = (mask > 0).astype(np.uint8) * 255
    kernel = np.ones((5, 5), np.uint8)
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    cleaned = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    return cleaned


def mask_to_polygons(mask, min_area=5000):
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    polygons = []
    for cnt in contours:
        if len(cnt) >= 3:
            poly = Polygon(cnt.squeeze())
            if poly.area >= min_area:
                polygons.append(poly)

    return polygons


@st.cache_resource(show_spinner=False)
def load_sam():
    sam = sam_model_registry["vit_b"](
        checkpoint="models/sam_vit_b_01ec64.pth"
    )
    sam.to("cpu")
    return SamAutomaticMaskGenerator(sam)

# ---------- Page Setup ----------
st.set_page_config(page_title="AI Subdivision Mapper", layout="wide")
st.title("🏗️ AI Subdivision Mapper")
st.write(
    "Upload an image of a property and view detected land areas "
    "and a conceptual subdivision layout."
)

# ---------- Sidebar ----------
st.sidebar.title("Controls")
num_lots = st.sidebar.slider("Number of lots", 2, 40, 8)

# ---------- File Upload ----------
uploaded_file = st.file_uploader(
    "Upload property image (JPEG or PNG)", type=["jpg", "png"]
)

# ---------- Main Logic ----------
if uploaded_file is not None:
    use_sam = st.checkbox("Enable AI segmentation (SAM)", value=False)

    # Decode image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    st.image(image, caption="Uploaded Property Image", width="stretch")

    # --- Segmentation ---
    if use_sam:
        with st.spinner("🤖 Running AI segmentation (this may take up to 30s)..."):
            mask_generator = load_sam()
            sam_masks = mask_generator.generate(image)

        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        for m in sam_masks:
            mask[m["segmentation"]] = 255

        st.subheader("AI Segmentation (SAM)")

    else:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        _, mask = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY_INV)

        st.subheader("Simple Mask (No AI)")

    mask = clean_mask(mask)
    st.image(mask, width="stretch")

    # --- Polygon Detection ---
    polygons = mask_to_polygons(mask)

    if polygons:
        land_poly = max(polygons, key=lambda p: p.area)

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(mask, cmap="gray")
        x, y = land_poly.exterior.xy
        ax.plot(x, y, color="yellow", linewidth=2)
        ax.axis("off")
        st.subheader("Detected Buildable Land Area")
        st.pyplot(fig)

    else:
        st.warning("No buildable land regions detected.")

else:
    st.info("👉 Upload a property image to begin.")







