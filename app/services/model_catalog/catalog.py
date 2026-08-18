from __future__ import annotations

from app.services.model_catalog.models import ModelSpec, V1ModelProfile


CATALOG={
    "qwen3_30b_a3b_instruct": ModelSpec(
        model_id="Qwen/Qwen3-30B-A3B-Instruct-2507",
        provider="huggingface",
        task="llm",
        license="Apache-2.0",
        min_gpu_vram_gb=24,
        remote_recommended=True,
        capabilities=("long_context","reasoning","multilingual","structured_output"),
    ),
    "wan2_2_ti2v_5b": ModelSpec(
        model_id="Wan-AI/Wan2.2-TI2V-5B",
        provider="huggingface",
        task="video",
        min_gpu_vram_gb=16,
        remote_recommended=True,
        capabilities=("text_to_video","image_to_video"),
        notes="Good V1 candidate for scene-level generation; exact VRAM depends on resolution/quantization/runtime.",
    ),
    "wan2_1_t2v_1_3b": ModelSpec(
        model_id="Wan-AI/Wan2.1-T2V-1.3B-Diffusers",
        provider="huggingface",
        task="video",
        min_gpu_vram_gb=8,
        remote_recommended=True,
        capabilities=("text_to_video",),
        notes="Lower-resource fallback for integration testing; quality may be below larger models.",
    ),
    "qwen3_tts": ModelSpec(
        model_id="Qwen/Qwen3-TTS",
        provider="huggingface",
        task="tts",
        remote_recommended=True,
        capabilities=("speech_synthesis","multilingual","voice_control"),
        notes="Model identifier should be pinned to the exact Qwen3-TTS checkpoint selected for deployment.",
    ),
    "mock_qa": ModelSpec(
        model_id="mock-qa-v1",
        provider="local",
        task="qa",
        capabilities=("contract_checks","deterministic_smoke_test"),
    ),
}


DEFAULT_V1=V1ModelProfile(
    llm=CATALOG["qwen3_30b_a3b_instruct"],
    video=CATALOG["wan2_2_ti2v_5b"],
    tts=CATALOG["qwen3_tts"],
    qa=CATALOG["mock_qa"],
)


def get_model(key: str) -> ModelSpec:
    try:
        return CATALOG[key]
    except KeyError as exc:
        raise KeyError(f"Unknown model catalog key: {key}") from exc


def list_models(task: str | None = None) -> list[ModelSpec]:
    models=list(CATALOG.values())
    if task:
        models=[m for m in models if m.task==task]
    return models
