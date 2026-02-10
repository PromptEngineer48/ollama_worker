# Use a known working CUDA-enabled base image from previous demo
FROM runpod/pytorch:0.7.0-cu1241-torch240-ubuntu2004

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

