# Use the official NVIDIA CUDA image as the base image
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC

# Install necessary dependencies
RUN apt-get update \
    && apt-get install -y \
        wget \
        unzip \
        git \
        python3 \
        python3-pip \
        firefox \
        ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Function to create directories and download model files
RUN download_model() { \
    mkdir -p "/models/$1" && \
    wget -O "/models/$1/config.json" "https://huggingface.co/guillaumekln/$1/resolve/main/config.json" && \
    wget -O "/models/$1/model.bin" "https://huggingface.co/guillaumekln/$1/resolve/main/model.bin" && \
    wget -O "/models/$1/tokenizer.json" "https://huggingface.co/guillaumekln/$1/resolve/main/tokenizer.json" && \
    wget -O "/models/$1/vocabulary.txt" "https://huggingface.co/guillaumekln/$1/resolve/main/vocabulary.txt"; \
} && \
    download_model faster-whisper-large-v2 && \
    download_model faster-whisper-medium

# Download and install the Whisper binary
RUN wget -O /tmp/whisper-faster.zip "https://github.com/Purfview/whisper-standalone-win/releases/download/faster-whisper/Whisper-Faster_r160_linux.zip" \
    && unzip /tmp/whisper-faster.zip -d /tmp/whisper-faster \
    && mv /tmp/whisper-faster/Whisper-Faster/whisper-faster /usr/local/bin/ \
    && chmod +x /usr/local/bin/whisper-faster \
    && rm -rf /tmp/whisper-faster /tmp/whisper-faster.zip

# Copy Python scripts
COPY *.py .

# Copy run script
COPY run.sh .

# Run script
CMD ["python3", "app.py"]
