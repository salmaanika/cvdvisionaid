# core_logic.py

import numpy as np
import cv2

# Example model loading, replace with your actual model logic
def process_image(image_bytes):
    # Convert bytes to image
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Perform image processing and inference here
    # Placeholder logic: simply returning image dimensions as "detections"
    detections = {'width': img.shape[1], 'height': img.shape[0]}

    # Image processing (e.g., LMS filtering)
    processed_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Example processing

    return detections, processed_img
