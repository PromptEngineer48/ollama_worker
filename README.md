# Serverless Ollama Worker

This directory contains the code to run an Ollama instance as a RunPod Serverless worker.

## Files
- `Dockerfile`: Defines the environment (Ollama + Python + Dependencies).
- `handler.py`: The python script that handles RunPod events and talks to Ollama.
- `start.sh`: Shell script to launch Ollama in the background within the container.
- `requirements.txt`: Python dependencies.

## Deployment Steps

RunPod Serverless requires a **Docker Image**. You cannot point it directly to a GitHub repo (unless you have a CI/CD pipeline set up).

### 1. Build the Docker Image
Run this command in this directory:
```bash
docker build -t <your-dockerhub-username>/ollama-worker:v1 .
```
*Replace `<your-dockerhub-username>` with your actual Docker Hub username.*

### 2. Push to Docker Hub
```bash
docker push <your-dockerhub-username>/ollama-worker:v1
```

### 3. Create RunPod Endpoint
1. Go to **RunPod Console** > **Serverless** > **New Endpoint**.
2. **Container Image**: `<your-dockerhub-username>/ollama-worker:v1`
3. **Container Disk**: Give it enough space for models (e.g., 10GB+).
4. **Environment Variables**: None strictly required for this basic setup, but you can add `OLLAMA_ORIGINS="*"` if needed.
5. **FlashBoot**: Optional, helps with start times.

## How it Works
1. When RunPod receives a request, it starts this container.
2. `start.sh` launches `ollama serve`.
3. `handler.py` starts and checks if the requested model (default `qwen3-coder-next`) exists.
4. If the model is missing (first run), it **pulls** it automatically (Cold Start will be longer).
5. It processes the prompt and returns the text.

## API Request Format
To test your endpoint, send this JSON:
```json
{
  "input": {
    "model": "qwen3-coder-next:latest",
    "prompt": "Write a Python function to sum two numbers."
  }
}
```
