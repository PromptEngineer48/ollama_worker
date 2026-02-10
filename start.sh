#!/bin/bash

echo "🚀 Starting Ollama..."
ollama serve &

echo "⏳ Waiting for Ollama background process..."
sleep 5

echo "🚀 Starting RunPod Handler..."
python3 -u handler.py
