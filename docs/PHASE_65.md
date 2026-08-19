# Phase 65 — Production End-to-End Integration

## Goal

Connect the deployed FastAPI application to a real GPU-backed Wan2.1 + Qwen3-TTS worker and make the generated MP4 reviewable before approval.

## Runtime architecture

```text
Render Web Service
  ├─ FastAPI
  ├─ PostgreSQL
  └─ generation_jobs
          │
          │ HTTPS + X-Worker-Token
          ▼
GPU Worker
  ├─ Wan2.1 T2V 1.3B (Diffusers)
  ├─ Qwen3-TTS 0.6B (optional)
  ├─ FFmpeg
  └─ generated MP4
          │
          │ download
          ▼
Render artifact directory
          │
          ▼
Manual approval
```

## Why a GPU worker is required

The Render Free web service is intentionally kept as the API/control plane. Wan2.1 T2V generation requires CUDA and the Wan model documentation reports about 8.19 GB VRAM for the 1.3B model. The repository therefore must not attempt real video inference inside the 512 MB Render Free service.

## GPU worker deployment

The repository includes `gpu_worker/Dockerfile`. It uses CUDA 12.4, FFmpeg, Diffusers and Qwen3-TTS. The worker downloads the Wan model into `HF_HOME` on first use and keeps generated artifacts under `WORK_ROOT`.

A GPU host such as Runpod can deploy this container. Runpod supports custom Docker images for Serverless endpoints and GPU Pods. Use a persistent volume for the Hugging Face cache and worker output when using a Pod.

Required worker environment variables:

- `GPU_WORKER_TOKEN`
- `VIDEO_MODEL_ID=Wan-AI/Wan2.1-T2V-1.3B-Diffusers`
- `VIDEO_DEVICE=cuda`
- `ENABLE_TTS=true`
- `TTS_MODEL_ID=Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice`
- `WORK_ROOT=/workspace/ai-content-factory`
- `HF_HOME=/workspace/hf-cache`

Required Render environment variables:

- `PIPELINE_MODE=production`
- `GPU_WORKER_URL=https://...`
- `GPU_WORKER_TOKEN=<same secret as worker>`
- `ARTIFACT_ROOT=artifacts/jobs`

## Safety behavior

The production worker never reports successful generation merely because a job was queued. If the GPU worker is missing, unreachable, returns an error, or returns an empty artifact, the generation job becomes `failed` with the actual error message.

A successful generation reaches `awaiting_approval` only after a non-empty MP4 has been downloaded.

## Review API

- `GET /api/v1/workspace/jobs/{job_id}/artifact`
- `POST /api/v1/workspace/jobs/{job_id}/approve`
- `POST /api/v1/workspace/jobs/{job_id}/reject`

Publishing remains a separate operation and is not triggered automatically by approval.
