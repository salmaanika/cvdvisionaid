import io
import json
import requests
import numpy as np
import streamlit as st
from PIL import Image
from io import BytesIO

APP_TITLE = "VISION AID: Color Perception Enhancement System for Color Blind Users"
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

# =============================
# Helper Functions
# =============================
def is_allowed(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTS

def pil_to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
    """Convert a PIL image to bytes."""
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()

def cvd_suffix(cvd_type: str) -> str:
    return "raw" if cvd_type == "None" else cvd_type.lower()

# =============================
# User Interface Class
# =============================
class UserInterface:
    def __init__(self):
        st.session_state.setdefault("filterButtonState", False)
        st.session_state.setdefault("cvdType", "None")
        st.session_state.setdefault("cvdIntensity", 1.0)

    @property
    def filterButtonState(self) -> bool:
        return bool(st.session_state.get("filterButtonState", False))

    @property
    def cvdType(self) -> str:
        return str(st.session_state.get("cvdType", "None"))

    @property
    def cvdIntensity(self) -> float:
        return float(st.session_state.get("cvdIntensity", 1.0))

    def selectCVDType(self, cvd_type: str):
        st.session_state["cvdType"] = cvd_type

    def setCVDIntensity(self, intensity: float):
        st.session_state["cvdIntensity"] = float(intensity)

    def toggleFilters(self):
        st.session_state["filterButtonState"] = not self.filterButtonState

    def displayOutput(self, title: str, image_rgb: np.ndarray, label: str | None = None):
        st.subheader(title)
        st.image(Image.fromarray(image_rgb), use_container_width=True)
        if label:
            st.write(label)

# =============================
# Main Function
# =============================
def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)

    ui = UserInterface()

    # ---- Sidebar: Configure CVD Type, thresholds (User -> UserInterface)
    with st.sidebar:
        st.header("Input Source")
        source = st.radio("Choose input", ["Upload Image", "Live Camera"], index=0)

        st.header("CVD Type")
        cvd_type = st.selectbox("Select CVD type", ["None", "Protanopia", "Deuteranopia", "Tritanopia"], index=0)
        ui.selectCVDType(cvd_type)

        st.header("CVD Intensity")
        intensity = st.slider("Intensity", 0.0, 1.0, float(ui.cvdIntensity), 0.05)
        ui.setCVDIntensity(float(intensity))

        st.divider()
        if st.button("Reload model / clear cache", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # ---- Capture Frame (UserInterface captures frame)
    image_name = "camera.png"
    image_pil: Image.Image
    image_bytes: bytes

    if source == "Upload Image":
        uploaded = st.file_uploader("Upload image", type=[e[1:] for e in ALLOWED_EXTS])
        if not uploaded:
            st.stop()
        if not is_allowed(uploaded.name):
            st.error(f"Unsupported file. Allowed: {sorted(ALLOWED_EXTS)}")
            st.stop()

        image_name = uploaded.name
        image_bytes = uploaded.getvalue()
        image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    else:
        cam = st.camera_input("Capture image from camera")
        if not cam:
            st.stop()

        image_name = "camera.png"
        image_bytes = cam.getvalue()
        image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    base = image_name.split('.')[0]

    # ---- ML detection: Call FastAPI backend for inference
    api_url = "https://your-heroku-app.herokuapp.com/predict"  # Replace with your FastAPI URL
    files = {'file': image_bytes}
    response = requests.post(api_url, files=files)

    if response.status_code == 200:
        data = response.json()
        detections = data.get('detections', [])
        annotated_rgb = np.array(data.get('processed_image', []))  # Processed image received from FastAPI
        
        # ---- Display Results
        ui.displayOutput("Annotated Image", annotated_rgb, label="Detections: " + json.dumps(detections))

    else:
        st.error("Failed to get response from API.")

    # ---- Apply Color Correction Filter if enabled
    if ui.filterButtonState and ui.cvdType != "None":
        # Apply color correction logic here using LMS matrices (if applicable)
        # For demonstration, let's assume we have a function `apply_color_correction`
        corrected_image = apply_color_correction(annotated_rgb, ui.cvdType, ui.cvdIntensity)
        ui.displayOutput("Filtered Image", corrected_image)

    # ---- Download Buttons (RAW and FILTERED)
    st.subheader("Download")

    # RAW Image (Annotated)
    raw_img_name = f"{base}_annotated.png"
    st.download_button(
        label="Download RAW annotated image",
        data=pil_to_bytes(Image.fromarray(annotated_rgb), fmt="PNG"),
        file_name=raw_img_name,
        mime="image/png",
    )

    if ui.filterButtonState and ui.cvdType != "None":
        filtered_img_name = f"{base}_filtered_{ui.cvdType}.png"
        st.download_button(
            label=f"Download FILTERED annotated image ({ui.cvdType})",
            data=pil_to_bytes(Image.fromarray(corrected_image), fmt="PNG"),
            file_name=filtered_img_name,
            mime="image/png",
        )

def apply_color_correction(image: np.ndarray, cvd_type: str, intensity: float) -> np.ndarray:
    """
    Apply a color correction (simulating color vision deficiencies).
    Replace this with actual LMS matrix and color correction code.
    """
    # Example: For now, just adjust the image brightness based on intensity
    return np.clip(image * intensity, 0, 255).astype(np.uint8)

if __name__ == "__main__":
    main()
