from __future__ import annotations

from pathlib import Path


def load_v0_context() -> str:
    root = Path(__file__).resolve().parents[2]
    v0_path = root / "v0_prompt.md"
    if not v0_path.exists():
        return ""
    return v0_path.read_text(encoding="utf-8")


