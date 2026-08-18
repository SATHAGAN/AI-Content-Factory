import sys

try:
    import torch
except ImportError:
    print("PyTorch is not installed.")
    sys.exit(2)

print("PyTorch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("CUDA version:", torch.version.cuda)

if torch.cuda.is_available():
    print("GPU count:", torch.cuda.device_count())
    for i in range(torch.cuda.device_count()):
        print(f"GPU {i}:", torch.cuda.get_device_name(i))
        print(f"VRAM {i} GB:", round(torch.cuda.get_device_properties(i).total_memory / 1024**3, 2))
else:
    print("No CUDA GPU detected. Use a GPU worker machine for real video inference.")
