from pathlib import Path


def test_gpu_worker_files_exist():
    assert Path("gpu_worker/app.py").exists()
    assert Path("gpu_worker/Dockerfile").exists()
    assert Path("deploy/docker-compose.gpu.yml").exists()


def test_gpu_worker_defaults_are_safe_for_first_gpu():
    text = Path("gpu_worker/app.py").read_text()
    assert "Wan-AI/Wan2.1-T2V-1.3B" in text
    assert "--offload_model" in text
    assert "--t5_cpu" in text
    assert "--sample_guide_scale" in text
