#!/usr/bin/env python3
"""Export FastAPI OpenAPI schema to sdks/openapi/scaleplane.openapi.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
OUT = ROOT / "sdks" / "openapi" / "scaleplane.openapi.json"


def main() -> int:
    sys.path.insert(0, str(BACKEND))
    from app.main import app  # noqa: PLC0415

    OUT.parent.mkdir(parents=True, exist_ok=True)
    schema = app.openapi()
    OUT.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
