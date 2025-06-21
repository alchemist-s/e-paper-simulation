#!/bin/bash

# Path to your virtual environment
VENV_PATH="e-paper-env"

# Activate the venv
source "$VENV_PATH/bin/activate"

# Run FastAPI server as root (with environment preserved)
sudo -E uvicorn pixi_server:app --host 0.0.0.0 --port 8000