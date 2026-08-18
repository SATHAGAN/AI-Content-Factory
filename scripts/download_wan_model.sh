#!/usr/bin/env bash
set -euo pipefail

MODEL_DIR="${1:-models/Wan2.1-T2V-1.3B}"
mkdir -p "$MODEL_DIR"

python -m pip install -U "huggingface_hub[cli]"
huggingface-cli download Wan-AI/Wan2.1-T2V-1.3B --local-dir "$MODEL_DIR"

echo "Model downloaded to $MODEL_DIR"
