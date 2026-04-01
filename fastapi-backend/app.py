# app.py

from fastapi import FastAPI, UploadFile, File
from core_logic import process_image
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()
    detections, processed_img = process_image(image_bytes)
    response = {
        "detections": detections,
        "processed_image": processed_img.tolist()  # Example, depends on your data
    }
    return JSONResponse(content=response)
