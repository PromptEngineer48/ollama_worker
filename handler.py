import runpod
import requests
import time
import os
import subprocess

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen3-coder-next:latest"

# ------------------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------------------
def is_ollama_ready():
    """Check if Ollama server is up and running."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def ensure_model_exists(model_name):
    """
    Check if the model exists locally. If not, pull it.
    This handles the 'Cold Start' scenario where the model isn't baked in.
    """
    try:
        # List installed models
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            models = [m['name'] for m in response.json().get('models', [])]
            # Normalize model names to handle tags (e.g. 'llama3:latest' vs 'llama3')
            if any(model_name in m for m in models):
                print(f"✅ Model '{model_name}' found locally.")
                return True
        
        print(f"⚠️ Model '{model_name}' not found. Pulling... (This may take time)")
        # Trigger pull
        pull_response = requests.post(f"{OLLAMA_BASE_URL}/api/pull", json={"name": model_name}, stream=True)
        for line in pull_response.iter_lines():
            if line:
                print(f"Pulling: {line.decode('utf-8')}")
        
        print(f"✅ Model '{model_name}' pulled successfully.")
        return True
    except Exception as e:
        print(f"❌ Error checking/pulling model: {e}")
        return False

# ------------------------------------------------------------------------------
# HANDLER
# ------------------------------------------------------------------------------
def handler(event):
    """
    RunPod Handler for Ollama.
    Input format:
    {
        "input": {
            "model": "llama3",
            "prompt": "Why is the sky blue?",
            "stream": false,
            "options": { ... }
        }
    }
    """
    input_data = event.get("input", {})
    
    # 1. Parse Input
    model = input_data.get("model", DEFAULT_MODEL)
    prompt = input_data.get("prompt")
    messages = input_data.get("messages") # Support chat format
    api_endpoint = "/api/chat" if messages else "/api/generate"
    
    if not prompt and not messages:
        return {"error": "Missing 'prompt' or 'messages' in input."}

    # 2. Ensure Model Exists (Handling Cold Starts)
    if not ensure_model_exists(model):
        return {"error": f"Failed to load/pull model '{model}'"}

    # 3. Construct Payload
    payload = {
        "model": model,
        "stream": False,  # Serverless functions usually prefer non-streaming response unless using specific streaming support
    }
    if prompt:
        payload["prompt"] = prompt
    if messages:
        payload["messages"] = messages
    
    # Pass through other options
    if "options" in input_data:
        payload["options"] = input_data["options"]

    # 4. Call Ollama
    try:
        t0 = time.time()
        response = requests.post(f"{OLLAMA_BASE_URL}{api_endpoint}", json=payload)
        t1 = time.time()
        
        if response.status_code == 200:
            result = response.json()
            result["_inference_time"] = t1 - t0
            return result
        else:
            return {"error": f"Ollama API Error: {response.text}"}

    except Exception as e:
        return {"error": str(e)}

# ------------------------------------------------------------------------------
# INITIALIZATION
# ------------------------------------------------------------------------------
# Wait for Ollama to start before accepting requests
print("⏳ Waiting for Ollama to start...")
start_time = time.time()
while not is_ollama_ready():
    time.sleep(1)
    if time.time() - start_time > 60:
        print("❌ Ollama failed to start within 60 seconds.")
        # We don't exit here, we let the handler try, maybe it's just slow.
        break

print("✅ Ollama is ready!")

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
