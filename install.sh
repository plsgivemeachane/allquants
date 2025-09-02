#!/bin/bash

# Install some pip lib that require like torch, transformers, datasets
sudo apt-get install -y build-essential python3-dev python3-pip python3-venv
pip install torch transformers datasets accelerate huggingface_hub rich mistral-common sentencepiece

# Install dependencies
pip install -r requirements.txt