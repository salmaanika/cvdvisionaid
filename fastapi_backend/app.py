# streamlit-frontend/app.py

import streamlit as st
import requests
from PIL import Image
import io

st.title("Object Detection App")

# Upload an image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Display the uploaded image in Streamlit
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Send the image to FastAPI backend for prediction
    files = {'file': uploaded_file.getvalue()}
    response = requests.post("https://your-heroku-app.herokuapp.com/predict", files=files)

    if response.status_code == 200:
        data = response.json()
        st.write(f"Prediction: {data['detections']}")
        # You can display the processed image or handle it however you want
        # If the processed image is an array, you might need to convert it back to an image format.
        processed_image = Image.open(io.BytesIO(data['processed_image']))
        st.image(processed_image, caption="Processed Image")
    else:
        st.write("Error: Unable to get predictions.")
