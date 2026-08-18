import os
from app.services.visuals.mock import MockVisualProvider

def create_visual_provider(provider=None, **kwargs):
    name=(provider or os.getenv("VISUAL_PROVIDER","mock")).lower()
    if name=="mock": return MockVisualProvider(kwargs.get("output_root","artifacts/visuals"))
    raise RuntimeError(f"Visual provider '{name}' is not configured yet")
