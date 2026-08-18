import os
import sys
import urllib.request

url = os.getenv("GPU_WORKER_URL", "http://localhost:8080")
try:
    with urllib.request.urlopen(url + "/health", timeout=10) as response:
        print(response.read().decode())
except Exception as exc:
    print("GPU worker is not reachable:", exc)
    sys.exit(1)
