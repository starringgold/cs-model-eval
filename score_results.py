#!/usr/bin/env python3
"""Unblind your scores and write a summary of how each model did.

Usage:
    python score_results.py              # uses the latest run
    python score_results.py --run run-20261116-120000
"""

import argparse
import csv
import json
from collections import defaultdict
from statistics import mean

from common import CRITERIA, PRICES, read_jsonl, resolve_run_dir


def fmt(value, digits=2):
    return "n/a" if value is None else f"{value:.{digits}f}"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", help="Run folder name (default: latest)")
    args = parser.parse_args()

    run_dir = resolve_run_dir(args.run)
    key = json.loads((run_dir / "blinding_key.json").read_text(encoding="utf-8"))
    results = {(r["scenario"], r["model"]): r for r in read_jsonl(run_dir / "results.jsonl") if "error" not in r}

    scores = defaultdict(lambda: defaultdict(list))   # model -> criterion -> [scores]
    per_scenario = defaultdict(dict)                   # scenario -> model -> total
    notes = []
    missing = 0
    with open(run_dir / "scoring_sheet.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            model = key[row["scenario"]][row["response"]]
            values = []
            for c in CRITERIA:
                raw = (row.get(c) or "").strip()
                if not raw:
                    missing += 1
                    continue
                v = float(raw)
                if not 1 <= v <= 5:
                    raise SystemExit(f"Score out of range (1-5) in {row['scenario']} {row['response']} {c}: {raw}")
                scores[model][c].append(v)
                values.append(v)
            if values:
                per_scenario[row["scenario"]][model] = mean(values)
            if row.get("notes", "").strip():
                notes.append((row["scenario"], model, row["notes"].strip()))

    if missing:
        print(f"warning: {missing} empty score cells were skipped")

    models = sorted(scores, key=lambda m: -mean(v for c in CRITERIA for v in scores[m][c]))
    out = ["# Results summary", "", f"Run: `{run_dir.name}`", ""]

    out += ["## Average score by criterion (1 to 5)", "",
            "| Model | " + " | ".join(c.capitalize() for c in CRITERIA) + " | Overall |",
            "|---" * (len(CRITERIA) + 2) + "|"]
    for m in models:
        cells = [fmt(mean(scores[m][c])) if scores[m][c] else "n/a" for c in CRITERIA]
        overall = mean(v for c in CRITERIA for v in scores[m][c])
        out.append(f"| {m} | " + " | ".join(cells) + f" | **{fmt(overall)}** |")

    out += ["", "## Winner per scenario", "", "| Scenario | Winner | Scores |", "|---|---|---|"]
    for slug, model_scores in per_scenario.items():
        best = max(model_scores.values())
        winners = [m for m, s in model_scores.items() if s == best]
        detail = ", ".join(f"{m} {fmt(s)}" for m, s in sorted(model_scores.items(), key=lambda x: -x[1]))
        out.append(f"| {slug} | {' / '.join(winners)} | {detail} |")

    out += ["", "## Speed, length and cost", "",
            "| Model | Avg output tokens | Avg latency (s) | Est. total cost (USD) | Avg score per $ |", "|---|---|---|---|---|"]
    for m in models:
        rows = [r for (s, mm), r in results.items() if mm == m]
        avg_out = mean(r["output_tokens"] for r in rows) if rows else None
        avg_lat = mean(r["latency_s"] for r in rows) if rows else None
        price = PRICES.get(m, {})
        cost = None
        if rows and price.get("input") is not None and price.get("output") is not None:
            cost = sum(r["input_tokens"] * price["input"] + r["output_tokens"] * price["output"] for r in rows) / 1_000_000
        overall = mean(v for c in CRITERIA for v in scores[m][c])
        per_dollar = overall / cost if cost else None
        out.append(f"| {m} | {fmt(avg_out, 0)} | {fmt(avg_lat, 1)} | {fmt(cost, 4)} | {fmt(per_dollar, 1)} |")
    if all(p.get("input") is None for p in PRICES.values()):
        out += ["", "_Cost is n/a because PRICES in common.py is empty. Fill it in to compare cost._"]

    if notes:
        out += ["", "## Your notes", ""]
        out += [f"- **{s} / {m}:** {n}" for s, m, n in notes]

    summary_path = run_dir / "summary.md"
    summary_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))
    print(f"\nSaved to {summary_path}")


if __name__ == "__main__":
    main()
