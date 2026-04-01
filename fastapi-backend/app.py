import io
import json
from fastapi import FastAPI, UploadFile, File
from PIL import Image
import numpy as np
from ultralytics import YOLO
from io import BytesIO

app = FastAPI()

# Path to the pre-trained YOLO model
MODEL_PATH = "best.pt"

# ==============================
# Helper Functions
# ==============================

def pil_to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
    """Convert a PIL image to bytes."""
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()

def load_yolo_model(path: str) -> YOLO:
    """Load and return the YOLO model."""
    return YOLO(path)

def detections_json_bytes(detections: list) -> bytes:
    """Convert detections to JSON bytes."""
    return (json.dumps(detections, indent=2, ensure_ascii=False) + "\n").encode("utf-8")

# ==============================
# Image Inference Endpoint
# ==============================

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Predict using the YOLO model and return the result."""
    # Read image file
    image_bytes = await file.read()
    
    # Convert the image to a PIL Image
    image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Load YOLO model (it is cached on subsequent calls)
    model = load_yolo_model(MODEL_PATH)
    
    # Run inference
    results = model.predict(source=image_pil, conf=0.25, iou=0.45, verbose=False)

    # Annotate image
    annotated_rgb = np.array(results[0].plot(pil=True))  # Plot the detected objects on the image
    
    # Extract detections
    detections = []
    for b in results[0].boxes:
        cls = int(b.cls[0])
        detections.append(
            {
                "box": b.xyxy[0].tolist(),
                "confidence": float(b.conf[0]),
                "class_id": cls,
                "class_name": model.names.get(cls, str(cls)),
            }
        )

    # Convert annotated image to bytes
    annotated_image_bytes = pil_to_bytes(Image.fromarray(annotated_rgb), fmt="PNG")

    # Return the results
    return {
        "detections": detections,
        "processed_image": annotated_image_bytes,
    }
