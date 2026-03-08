FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install system dependencies
COPY Aptfile /app/Aptfile
RUN apt-get update && apt-get install -y $(cat Aptfile)

# Copy the rest of the app
COPY . .

# Expose port 8501 for Streamlit
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app.py"]
