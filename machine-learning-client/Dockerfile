# Base image on previously-created image
FROM python:3.10-slim

# Set the working directory in the image
WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies - doing this first will speed up subsequent builds
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Create data directory for images
RUN mkdir -p /app/data

# Expose port for API
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "app.py"]
