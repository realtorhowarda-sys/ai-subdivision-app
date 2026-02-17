import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import torch
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator

def clean_mask(mask):
    from shapely.geometry import Polygon

def mask_to_polygons(mask, min_area=5000):
    """
    Convert a binary mask to Shapely polygons.
    Keeps only polygons larger than min_area.
    """
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
    """
    Clean a binary land mask:
    - Remove small noise
    - Fill holes
    """
    # Ensure mask is binary
    mask = (mask > 0).astype(np.uint8) * 255

    # Remove small noise (opening)
    kernel = np.ones((5, 5), np.uint8)
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Fill holes (closing)
    cleaned = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)

    return cleaned
# ---------- Page Setup ----------
st.set_page_config(page_title="AI Subdivision Mapper", layout="wide")
st.title("🏗️ AI Subdivision Mapper")
st.write("Upload an image of a property and view detected land areas "
         "and a conceptual subdivision layout. (Beta version)")

# ---------- Sidebar Controls ----------
st.sidebar.title("Controls")
num_lots = st.sidebar.slider("Number of lots", 2, 40, 8)

# ---------- File Upload ----------
uploaded_file = st.file_uploader("Upload property image (JPEG or PNG)", type=["jpg", "png"])

# ---------- Load Model Function ----------
@st.cache_resource(show_spinner=False)
def load_sam_model():
    """Load the Segment Anything model once and reuse across runs."""
    sam_checkpoint = "models/sam_vit_b_01ec64.pth"
    model_type = "vit_b"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
    sam.to(device=device)
    mask_generator = SamAutomaticMaskGenerator(sam)
    return mask_generator, device

@st.cache_resource(show_spinner=False)
def load_sam():
    sam = sam_model_registry["vit_b"](
        checkpoint="models/sam_vit_b_01ec64.pth"
    )
    sam.to("cpu")  # CPU-only for stability
    return SamAutomaticMaskGenerator(sam)
         # ---------- Main Logic ----------
if uploaded_file is not None:
    # ✅ STEP 3: SAM toggle (appears after upload)
    use_sam = st.checkbox("Enable AI segmentation (SAM)", value=False)

    # Decode the uploaded file to an image array
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    st.image(image, caption="Uploaded Property Image", use_container_width=True)

    if use_sam:
        with st.spinner("🤖 Running AI segmentation (this may take up to 30s)..."):
            mask_generator = load_sam()
            sam_masks = mask_generator.generate(image)

        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        for m in sam_masks:
            mask[m["segmentation"]] = 255

        st.subheader("AI Segmentation (SAM)")
        st.image(mask, use_container_width=True)

    else:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        _, mask = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY_INV)

        st.subheader("Simple Mask (No AI)")
        st.image(mask, use_container_width=True)

else:
    st.info("👉 Upload a property image to begin.")
# ---------- Main Logic ----------
if uploaded_file is not None:
           # ✅ STEP 3: SAM toggle (always visible after upload)
    use_sam = st.checkbox("Enable AI segmentation (SAM)", value=False)

    # Decode image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    st.image(image, caption="Uploaded Image", use_container_width=True)
    # 1. Decode the uploaded file to an image array
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    st.image(image, caption="Uploaded Property Image", use_container_width=True)
         # 2. Segmentation choice (safe)
use_sam = st.checkbox("Enable AI segmentation (SAM)", value=False)

if use_sam:
    with st.spinner("🤖 Running AI segmentation (this may take up to 30s)..."):
        mask_generator = load_sam()
        sam_masks = mask_generator.generate(image)

    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    for m in sam_masks:
        mask[m["segmentation"]] = 255
             mask = clean_mask(mask)

    st.subheader("AI Segmentation (SAM)")
    st.image(mask, use_container_width=True)

else:
    # Fast fallback (no AI)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    _, mask = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY_INV)
         mask = clean_mask(mask)

    st.subheader("Simple Mask (No AI)")
    st.image(mask, use_container_width=True)

    # 3. Generate a very simple conceptual subdivision grid
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
        st.subheader("Generated Conceptual Subdivision Layout")
        st.pyplot(fig)
    else:
        st.warning("AI segmentation found very little usable land; try another image.")
else:
    st.info("👉 Upload a clear aerial or satellite image to start.")






