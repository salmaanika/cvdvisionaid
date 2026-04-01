import requests
from PIL import Image

# This section should replace where you run YOLO inference locally in Streamlit.
# Instead of running the inference locally, send the image to FastAPI.

# Replace this block with the part where the user uploads an image or uses the camera
uploaded_file = st.file_uploader("Upload image", type=[e[1:] for e in ALLOWED_EXTS])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Send the image to FastAPI backend (Heroku URL here)
    api_url = "https://your-heroku-app.herokuapp.com/predict"  # Replace with your actual FastAPI URL
    files = {'file': uploaded_file.getvalue()}
    response = requests.post(api_url, files=files)

    if response.status_code == 200:
        # Handle the response from FastAPI
        data = response.json()
        detections = data.get('detections', [])
        annotated_rgb = np.array(data.get('processed_image', []))  # Make sure to handle the image data properly
        text_label = feedback.generateTextLabel(detections)

        # Display the annotated image and the detection results
        st.subheader("Results")
        st.image(Image.fromarray(annotated_rgb), caption="Processed Image", use_container_width=True)
        st.write(text_label)
    else:
        st.error(f"Failed to get response from API. Status code: {response.status_code}")
