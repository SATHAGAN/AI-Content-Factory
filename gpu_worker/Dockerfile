FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/workspace/hf-cache \
    TRANSFORMERS_CACHE=/workspace/hf-cache

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt

COPY requirements.txt /opt/requirements.txt
RUN python3 -m pip install --upgrade pip && \
    pip install -r /opt/requirements.txt

COPY app.py /opt/gpu_worker/app.py

ENV VIDEO_MODEL_ID=Wan-AI/Wan2.1-T2V-1.3B-Diffusers
ENV VIDEO_DEVICE=cuda
ENV WORK_ROOT=/workspace/ai-content-factory
ENV ENABLE_TTS=true
ENV TTS_MODEL_ID=Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice

EXPOSE 8080

CMD ["uvicorn", "gpu_worker.app:app", "--host", "0.0.0.0", "--port", "8080"]
