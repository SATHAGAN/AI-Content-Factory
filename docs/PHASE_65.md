# Phase 65 — Production End-to-End Integration

## Goal

Connect the FastAPI control plane to a real GPU-backed Wan2.1 + Qwen3-TTS worker and make the generated MP4 reviewable before approval.

## Runtime architecture

```text
Render Web Service
  ├─ FastAPI
  ├─ PostgreSQL
  └─ generation_jobs
          │
          │ HTTPS + X-Worker-Token
          ▼
Dedicated CUDA GPU Worker
  ├─ Wan2.1 T2V 1.3B (Diffusers)
  ├─ Qwen3-TTS 0.6B
  ├─ FFmpeg
  └─ generated MP4
          │
          │ authenticated download
          ▼
Render artifact directory
          │
          ▼
Manual approval
          │
          ▼
Separate publishing operation
```

## Why a GPU worker is required

The Render web service is the API/control plane. Real Wan2.1 inference must run on a CUDA GPU and must not be attempted inside the 512 MB Render Free service.

## GPU worker deployment

The repository includes `gpu_worker/Dockerfile` and `gpu_worker/app.py`. The worker exposes:

- `GET /health`
- `POST /generate-video`
- `GET /download?path=...`

The worker uses a shared secret through `X-Worker-Token`.

A GPU host such as Runpod can deploy this container. Use a persistent volume for the Hugging Face cache and worker output when using a long-lived GPU Pod.

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
- `LLM_PROVIDER=mock` for the deterministic planner smoke test, or `openai-compatible` for a real LLM
- `LLM_BASE_URL=...` when using an OpenAI-compatible provider
- `LLM_MODEL_ID=...` when using an OpenAI-compatible provider
- `LLM_API_KEY=...` when required by the provider

## Production behavior

The production worker:

1. Loads the project from PostgreSQL.
2. Builds a validated scene plan.
3. Sends all scenes to the authenticated GPU worker.
4. Waits for Wan2.1 video generation and Qwen3-TTS narration.
5. Downloads the final MP4.
6. Persists the artifact path and model metadata.
7. Changes the job to the approval stage only after a non-empty MP4 exists.
8. Never publishes automatically from the generation worker.

If the GPU worker is missing, unreachable, returns an error, or returns an empty artifact, the generation job becomes `failed` with the actual error message. This prevents the previous false-success behavior.

## Review API

- `GET /api/v1/workspace/jobs/{job_id}` — job state and artifact metadata
- `GET /api/v1/workspace/jobs/{job_id}/video` — authenticated MP4 stream
- `POST /api/v1/workspace/jobs/{job_id}/approval` — approve or reject

Approval does not publish the video. Publishing remains a separate explicit operation.

## First production test

Use a 30-second English short with 3–4 scenes. Keep `auto_publish=false`. Verify the MP4 visually and listen to the narration before enabling any publishing workflow.
