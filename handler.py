import runpod
import requests

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "glm-4.7-flash:latest"

# ------------------------------------------------------------------------------
# SIMPLE HANDLER
# ------------------------------------------------------------------------------
def handler(event):
    """
    Minimal RunPod Handler.
    Forwards 'input' directly to Ollama.
    """
    input_data = event.get("input", {})
    
    # Validation
    if not input_data:
        return {"error": "No input provided"}

    # Set default model if not provided
    if "model" not in input_data:
        input_data["model"] = DEFAULT_MODEL
    
    # Disable streaming for serverless (unless you implement a streaming handler)
    input_data["stream"] = False

    # Determine endpoint (Chat vs Generate)
    endpoint = "/api/chat" if "messages" in input_data else "/api/generate"

    try:
        # Call Ollama
        response = requests.post(f"{OLLAMA_BASE_URL}{endpoint}", json=input_data)
        
        # Return JSON result
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Ollama Error: {response.text}"}

    except Exception as e:
        return {"error": str(e)}

# ------------------------------------------------------------------------------
# START
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
