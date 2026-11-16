"""Shared helpers for the CS model evaluation scripts."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCENARIO_DIR = ROOT / "scenarios"
OUTPUT_DIR = ROOT / "outputs"
SYSTEM_PROMPT_FILE = ROOT / "prompts" / "system.md"

# Short alias -> API model string. Edit here to test other models.
MODELS = {
    "fable": "claude-fable-5-2",
    "opus": "claude-opus-5-5",
    "sonnet": "claude-sonnet-5-5",
}

# Optional: USD price per million tokens, used to estimate cost in the summary.
# Fill these in from Anthropic's current pricing page, or leave as None to skip cost.
PRICES = {
    "fable": {"input": None, "output": None},
    "opus": {"input": None, "output": None},
    "sonnet": {"input": None, "output": None},
}

CRITERIA = ["diagnosis", "judgment", "actionability", "communication", "efficiency"]


def load_scenarios(only=None):
    """Return a list of scenario dicts: slug, title, notes, prompt."""
    scenarios = []
    for path in sorted(SCENARIO_DIR.glob("*.md")):
        if path.name.startswith("_"):
            continue
        slug = path.stem
        if only and slug not in only and not any(slug.startswith(o) for o in only):
            continue
        text = path.read_text(encoding="utf-8")
        title_match = re.search(r"^# (.+)$", text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else slug
        parts = re.split(r"^## Prompt\s*$", text, maxsplit=1, flags=re.MULTILINE)
        if len(parts) != 2:
            raise ValueError(f"{path.name} has no '## Prompt' section")
        notes_part = re.split(r"^## What a strong answer does\s*$", parts[0], maxsplit=1, flags=re.MULTILINE)
        notes = notes_part[1].strip() if len(notes_part) == 2 else ""
        scenarios.append({"slug": slug, "title": title, "notes": notes, "prompt": parts[1].strip()})
    return scenarios


def latest_run_dir():
    runs = sorted(p for p in OUTPUT_DIR.glob("run-*") if p.is_dir())
    if not runs:
        raise SystemExit("No runs found in outputs/. Run run_comparison.py first.")
    return runs[-1]


def resolve_run_dir(run):
    if run is None:
        return latest_run_dir()
    path = Path(run)
    if not path.is_absolute():
        path = OUTPUT_DIR / run
    if not path.is_dir():
        raise SystemExit(f"Run folder not found: {path}")
    return path


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
