# HearthstoneOne AI - CUDA Training Container
# Supports Pascal GPUs (Compute Capability 6.1+) and newer
# CUDA 12.2 for compatibility with modern drivers

FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04

LABEL maintainer="HearthstoneOne AI"
LABEL description="AI Training Container with CUDA 12.2 support"

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Python version
ENV PYTHON_VERSION=3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-pip \
    python${PYTHON_VERSION}-venv \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VERSION} 1 \
    && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Install PyTorch with CUDA 12.1 support (compatible with CUDA 12.2)
RUN pip install --no-cache-dir \
    torch==2.2.0+cu121 \
    torchvision==0.17.0+cu121 \
    --index-url https://download.pytorch.org/whl/cu121

# Copy application code
COPY ai/ ./ai/
COPY training/ ./training/
COPY runtime/ ./runtime/
COPY simulator/ ./simulator/

# Create directories for models and data
RUN mkdir -p /app/models /app/data /app/logs

# Environment variables
ENV PYTHONPATH=/app
ENV CUDA_VISIBLE_DEVICES=0

# Default command: Start WebSocket server
CMD ["python", "runtime/websocket_server.py", "--host", "0.0.0.0", "--port", "9876"]
