#!/usr/bin/env python3
"""Turn a run into blind review packets and an empty score sheet.

Each scenario's answers are shuffled and labeled Response A, B, C, so you can
score them without knowing which model wrote which. The answer key is saved to
blinding_key.json in the run folder. Don't open it until you've finished scoring.

Usage:
    python blind_review.py              # uses the latest run
    python blind_review.py --run run-20261116-120000
"""

import argparse
import csv
import json
import random
import string

from common import CRITERIA, load_scenarios, read_jsonl, resolve_run_dir


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", help="Run folder name (default: latest)")
    parser.add_argument("--seed", type=int, help="Random seed, only needed to reproduce a shuffle")
    args = parser.parse_args()

    run_dir = resolve_run_dir(args.run)
    key_path = run_dir / "blinding_key.json"
    sheet_path = run_dir / "scoring_sheet.csv"
    if sheet_path.exists():
        raise SystemExit(f"{sheet_path.name} already exists in this run. Delete it first if you really want to reshuffle.")

    rng = random.Random(args.seed)
    results = [r for r in read_jsonl(run_dir / "results.jsonl") if "error" not in r]
    scenario_info = {s["slug"]: s for s in load_scenarios()}
    review_dir = run_dir / "review"
    review_dir.mkdir(exist_ok=True)

    key = {}
    rows = []
    for slug in dict.fromkeys(r["scenario"] for r in results):
        models = [r["model"] for r in results if r["scenario"] == slug]
        rng.shuffle(models)
        labels = dict(zip(string.ascii_uppercase, models))
        key[slug] = labels

        info = scenario_info.get(slug, {})
        lines = [f"# {info.get('title', slug)}", ""]
        if info.get("notes"):
            lines += ["## Answer key: what a strong answer does", "", info["notes"], ""]
        lines += ["## Prompt the models received", "", (run_dir / slug / "_prompt.md").read_text(encoding="utf-8"), ""]
        for label, model in labels.items():
            answer = (run_dir / slug / f"{model}.md").read_text(encoding="utf-8")
            lines += ["---", "", f"## Response {label}", "", answer, ""]
            rows.append({"scenario": slug, "response": label, **{c: "" for c in CRITERIA}, "notes": ""})
        (review_dir / f"{slug}.md").write_text("\n".join(lines), encoding="utf-8")

    key_path.write_text(json.dumps(key, indent=2), encoding="utf-8")
    with open(sheet_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["scenario", "response", *CRITERIA, "notes"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Review packets: {review_dir}")
    print(f"Score sheet:    {sheet_path}")
    print("Score every row 1 to 5 using rubric.md, then run: python score_results.py")


if __name__ == "__main__":
    main()
