# Base Image: Python 3.10 Slim (Lightweight)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV (libGL)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the Flask port
EXPOSE 5000

# Command to run the application
# We use python app.py for simplicity, but gunicorn is better for prod
CMD ["python", "app.py"]
