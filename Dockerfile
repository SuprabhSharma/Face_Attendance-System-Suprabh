FROM python:3.10-slim

# Install system dependencies required for dlib, face_recognition, and git
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Expose the server port (Gunicorn defaults to binding here)
EXPOSE 5000

# Specify the command to run on container start
# We increase the timeout to 120s to ensure heavy FaceNet processing doesn't crash a worker early
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 2 run:app"]
