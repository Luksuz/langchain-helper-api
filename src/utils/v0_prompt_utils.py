from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple, List


def get_v0_prompt_dir() -> Path:
    # repo_root/src/utils/... -> repo_root
    return Path(__file__).resolve().parents[2] / "v0_prompt"


def load_v0_prompt_files() -> Dict[str, str]:
    """Load all .md files in v0_prompt directory as {filename: content}."""
    prompt_dir = get_v0_prompt_dir()
    files: Dict[str, str] = {}
    if not prompt_dir.exists():
        return files
    for md_file in sorted(prompt_dir.glob("*.md")):
        try:
            files[md_file.name] = md_file.read_text(encoding="utf-8")
        except Exception:
            continue
    return files


def summarize_for_selection(filename: str, content: str, max_chars: int = 240) -> str:
    """Produce a short, human-readable one-liner summary for selection display.

    Uses the first heading/lines and truncates to max_chars.
    """
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    if not lines:
        return filename
    # Prefer first non-empty line (often a title like '### /generate — ...')
    summary = lines[0]
    # If a 'Use this' line exists shortly after, append it
    for ln in lines[1:4]:
        if ln.lower().startswith("use this"):
            summary = f"{summary} | {ln}"
            break
    if len(summary) > max_chars:
        summary = summary[: max_chars - 3] + "..."
    return f"{filename}: {summary}"


