#!/bin/bash

# /home/alshahed/e-paper-simulation/e-paper-env/bin/uvicorn

# Navigate to your project directory
cd /home/alshahed/e-paper-simulation

# Run uvicorn using full path inside the venv
sudo /home/alshahed/e-paper-simulation/e-paper-env/bin/uvicorn pixi_server:app --host 0.0.0.0 --port 8000