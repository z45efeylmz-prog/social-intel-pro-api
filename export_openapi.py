import sys
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.main import app
from fastapi.openapi.utils import get_openapi

spec = get_openapi(
    title=app.title,
    version=app.version,
    openapi_version=app.openapi_version,
    description=app.description,
    routes=app.routes
)

target_path = os.path.join(ROOT, "openapi.json")
with open(target_path, "w", encoding="utf-8") as f:
    json.dump(spec, f, indent=2)

print(f"[PASS] openapi.json generated at {target_path} (Endpoints: {len(spec.get('paths', {}))})")
