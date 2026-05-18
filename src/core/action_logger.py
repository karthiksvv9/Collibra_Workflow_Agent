from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.core.config import settings


def log_action(action: str, status: str = "ok", detail: Any | None = None) -> Path:
    """Append a timestamped JSONL action record under output/action_logs."""
    log_dir = settings.paths.output_dir / "action_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    path = log_dir / f"actions-{now.strftime('%Y%m%d')}.jsonl"
    record = {
        "timestamp": now.isoformat(),
        "action": str(action),
        "status": str(status),
        "detail": _safe_detail(detail),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True, default=str) + "\n")
    return path


def _safe_detail(detail: Any | None) -> Any:
    if detail is None:
        return {}
    if isinstance(detail, (str, int, float, bool)):
        text = str(detail)
        return text[:8000] + ("..." if len(text) > 8000 else "")
    try:
        encoded = json.dumps(detail, ensure_ascii=True, default=str)
        if len(encoded) > 12000:
            return {"truncated_json": encoded[:12000]}
        return json.loads(encoded)
    except Exception:
        text = str(detail)
        return text[:8000] + ("..." if len(text) > 8000 else "")
