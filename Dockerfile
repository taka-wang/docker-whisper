# Use the official NVIDIA CUDA image as the base image
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    wget unzip \
    python3 \
    python3-pip \
    firefox \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/requirements.txt

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Create directories to store the models
RUN mkdir -p /models/faster-whisper-medium /models/faster-whisper-large-v2

# Download the large-v2 model using wget to the specified directory
RUN wget -O /models/faster-whisper-large-v2/config.json https://huggingface.co/guillaumekln/faster-whisper-large-v2/resolve/main/config.json && \
    wget -O /models/faster-whisper-large-v2/model.bin https://huggingface.co/guillaumekln/faster-whisper-large-v2/resolve/main/model.bin && \
    wget -O /models/faster-whisper-large-v2/tokenizer.json https://huggingface.co/guillaumekln/faster-whisper-large-v2/resolve/main/tokenizer.json && \
    wget -O /models/faster-whisper-large-v2/vocabulary.txt https://huggingface.co/guillaumekln/faster-whisper-large-v2/resolve/main/vocabulary.txt

# Download the medium model using wget to the specified directory
RUN wget -O /models/faster-whisper-medium/config.json https://huggingface.co/guillaumekln/faster-whisper-medium/resolve/main/config.json && \
    wget -O /models/faster-whisper-medium/model.bin https://huggingface.co/guillaumekln/faster-whisper-medium/resolve/main/model.bin && \
    wget -O /models/faster-whisper-medium/tokenizer.json https://huggingface.co/guillaumekln/faster-whisper-medium/resolve/main/tokenizer.json && \
    wget -O /models/faster-whisper-medium/vocabulary.txt https://huggingface.co/guillaumekln/faster-whisper-medium/resolve/main/vocabulary.txt

# Download the binary
RUN wget https://github.com/Purfview/whisper-standalone-win/releases/download/faster-whisper/Whisper-Faster_r160_linux.zip \
    && unzip Whisper-Faster_r160_linux.zip -d /tmp/whisper-faster \
    && cp /tmp/whisper-faster/Whisper-Faster/whisper-faster /usr/local/bin/ \
    && chmod +x /usr/local/bin/whisper-faster \
    && rm -rf /tmp/whisper-faster Whisper-Faster_r160_linux.zip

COPY *.py /app/
COPY run.sh /app/

# Run script
CMD ["python3", "app.py"]
