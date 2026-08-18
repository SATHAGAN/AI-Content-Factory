FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt

COPY requirements.txt /opt/requirements.txt
RUN python3 -m pip install --upgrade pip && \
    pip install -r /opt/requirements.txt

RUN git clone --depth 1 https://github.com/Wan-Video/Wan2.1.git /opt/Wan2.1

COPY app.py /opt/gpu_worker/app.py

ENV VIDEO_MODEL_ID=Wan-AI/Wan2.1-T2V-1.3B
ENV VIDEO_MODEL_BACKEND=wan-cli
ENV WAN_REPO=/opt/Wan2.1
ENV WAN_CKPT=/models/Wan2.1-T2V-1.3B

EXPOSE 8080

CMD ["uvicorn", "gpu_worker.app:app", "--host", "0.0.0.0", "--port", "8080"]
