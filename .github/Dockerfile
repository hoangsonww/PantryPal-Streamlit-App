# Dockerfile
# Use official slim Python 3.9 image
FROM python:3.9-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Streamlit server settings
ENV STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501

# Working directory
WORKDIR /app

# Install any system dependencies (if needed)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (to leverage Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Default command to run the app
CMD ["streamlit", "run", "app.py"]
