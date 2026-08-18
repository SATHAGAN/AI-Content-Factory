# Phase 6 — Real GPU Worker Deployment Foundation

## Goal

Move real video inference out of the API server and onto a GPU machine.

## Current implementation

```text
Web/API
   |
   v
Queue
   |
   v
GPU Worker :8080
   |
   v
Wan2.1 T2V 1.3B
   |
   v
scene.mp4
```

The worker is packaged as a CUDA container and exposes:
- `GET /health`
- `POST /generate`

## First model

The initial real video target is Wan2.1 T2V 1.3B.

The official Wan2.1 documentation reports approximately 8.19 GB VRAM for T2V-1.3B and recommends 480P for the 1.3B model. It also documents model offloading and CPU T5 options for a single RTX 4090. See the official repository:
https://github.com/Wan-Video/Wan2.1

## Your current computer

The previously supplied machine specification was:
- Intel Core i5
- 8 GB RAM
- no GPU specified

That machine should not be used for real Wan inference. The application remains CPU-compatible for development, while the GPU worker should run separately.

## GPU deployment requirements

For the first real test, use a Linux NVIDIA GPU machine with:
- NVIDIA driver
- NVIDIA Container Toolkit
- preferably >= 12 GB VRAM for comfortable experimentation
- 16+ GB system RAM preferred

The 8.19 GB figure is a model-level requirement reported by Wan; real deployments need additional memory headroom for the operating system, framework, buffers and other processes.

## Model download

```bash
bash scripts/download_wan_model.sh
```

For gated/private model access, authenticate with Hugging Face before downloading.

## Start worker

```bash
docker compose -f deploy/docker-compose.gpu.yml up --build
```

Then:

```bash
curl http://localhost:8080/health
```

## Important limitation

This development environment has no suitable NVIDIA GPU, so the actual Wan model was NOT downloaded or executed. We validate the worker code and deployment configuration statically.

The next phase should add:
1. durable Redis/worker execution
2. cloud object-storage upload
3. real GPU smoke test
4. real scene generation
5. TTS execution
6. FFmpeg synchronization
7. automatic audio/video quality checks
