# Use a CUDA-enabled base image from RunPod to ensure driver compatibility
FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0

WORKDIR /app

# 1. Install Ollama
# We use the official install script
RUN curl -fsSL https://ollama.com/install.sh | sh

# 2. Install Python Dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 3. Copy Application Code
COPY handler.py .
COPY start.sh .

# 4. Make start script executable
RUN chmod +x start.sh

# 5. Start
CMD ["./start.sh"]
