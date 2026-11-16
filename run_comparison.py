#!/usr/bin/env python3
"""Send every scenario to every model with the same prompt and save the answers.

Usage:
    python run_comparison.py                     # all scenarios, all models
    python run_comparison.py --scenarios 01 03   # only scenarios starting with 01 or 03
    python run_comparison.py --models fable opus # only some models
    python run_comparison.py --dry-run           # test the pipeline without calling the API
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

from common import MODELS, OUTPUT_DIR, SYSTEM_PROMPT_FILE, load_scenarios

MAX_TOKENS = 4000


def load_env_file():
    """Load ANTHROPIC_API_KEY from a .env file if python-dotenv is installed."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass


def call_model(client, model_id, system_prompt, user_prompt):
    start = time.perf_counter()
    response = client.messages.create(
        model=model_id,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    latency = time.perf_counter() - start
    text = "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
    return {
        "text": text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "stop_reason": response.stop_reason,
        "latency_s": round(latency, 2),
    }


def fake_call(alias, scenario):
    """Placeholder output for --dry-run."""
    time.sleep(0.05)
    text = f"[DRY RUN] Placeholder answer from {alias} for '{scenario['title']}'."
    return {"text": text, "input_tokens": 500, "output_tokens": 800,
            "stop_reason": "end_turn", "latency_s": 0.05}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scenarios", nargs="*", help="Scenario slugs or number prefixes to run")
    parser.add_argument("--models", nargs="*", choices=list(MODELS), help="Model aliases to run")
    parser.add_argument("--dry-run", action="store_true", help="Do not call the API; write placeholder outputs")
    args = parser.parse_args()

    scenarios = load_scenarios(args.scenarios)
    if not scenarios:
        sys.exit("No scenarios matched.")
    aliases = args.models or list(MODELS)
    system_prompt = SYSTEM_PROMPT_FILE.read_text(encoding="utf-8").strip()

    client = None
    if not args.dry_run:
        load_env_file()
        if not os.environ.get("ANTHROPIC_API_KEY"):
            sys.exit("ANTHROPIC_API_KEY is not set. Put it in a .env file or export it in your shell.")
        import anthropic
        client = anthropic.Anthropic()

    run_dir = OUTPUT_DIR / datetime.now().strftime("run-%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True)
    results_path = run_dir / "results.jsonl"
    (run_dir / "config.json").write_text(json.dumps({
        "models": {a: MODELS[a] for a in aliases},
        "scenarios": [s["slug"] for s in scenarios],
        "max_tokens": MAX_TOKENS,
        "system_prompt": system_prompt,
        "dry_run": args.dry_run,
    }, indent=2), encoding="utf-8")

    total = len(scenarios) * len(aliases)
    done = 0
    with open(results_path, "w", encoding="utf-8") as results_file:
        for scenario in scenarios:
            scenario_dir = run_dir / scenario["slug"]
            scenario_dir.mkdir()
            (scenario_dir / "_prompt.md").write_text(scenario["prompt"], encoding="utf-8")
            for alias in aliases:
                done += 1
                print(f"[{done}/{total}] {scenario['slug']} -> {alias} ...", end=" ", flush=True)
                record = {"scenario": scenario["slug"], "model": alias, "model_id": MODELS[alias]}
                try:
                    if args.dry_run:
                        result = fake_call(alias, scenario)
                    else:
                        result = call_model(client, MODELS[alias], system_prompt, scenario["prompt"])
                    (scenario_dir / f"{alias}.md").write_text(result.pop("text"), encoding="utf-8")
                    record.update(result)
                    print(f"ok ({record['output_tokens']} tokens, {record['latency_s']}s)")
                    if record["stop_reason"] == "max_tokens":
                        print("    warning: answer was cut off at MAX_TOKENS")
                except Exception as exc:  # keep going if one call fails
                    record["error"] = f"{type(exc).__name__}: {exc}"
                    print(f"FAILED: {record['error']}")
                results_file.write(json.dumps(record) + "\n")
                results_file.flush()

    print(f"\nDone. Outputs saved in {run_dir}")
    print("Next step: python blind_review.py")


if __name__ == "__main__":
    main()
