# When is the top model worth it? Claude models on real customer success work

A small, honest evaluation of three Claude models (Fable 5.2, Opus 5.5 and Sonnet 5.5) on the kind of judgment-heavy work customer success managers do every day: churn saves, stalled onboardings, executive escalations, expansion calls and portfolio triage.

The question isn't "which model is best?" It's **"which tasks actually need the most capable model, and where does a faster, cheaper one do just as well?"** That's the decision every team rolling out AI has to make.

## How it works

1. **Same input for every model.** Each scenario is sent to each model with an identical system prompt and user prompt.
2. **Blind scoring.** Answers are shuffled and labeled A, B, C. I score them against a rubric before I know which model wrote which.
3. **Unblind and compare.** Scores are matched back to models, alongside output length, speed and estimated cost.

## Scenarios

| # | Scenario | What it tests |
|---|---|---|
| 01 | Churn risk: champion left, usage falling | Root-cause diagnosis, save planning, exec outreach |
| 02 | Stalled onboarding: CRM integration blocker | Technical troubleshooting, expectation reset |
| 03 | Executive escalation after an outage | Ownership without overpromising, internal escalation |
| 04 | Expansion opportunity with mixed signals | Saying "not yet" to a big deal, sequencing |
| 05 | Portfolio triage from account data | Reading numbers, spotting hidden risk |

All scenarios use a fictional product (Tidewell) and fictional companies. Scenarios based on my own experience are fully anonymized; no real customer data is used anywhere.

## Run it yourself

Requires Python 3.9+ and an Anthropic API key.

```bash
pip install -r requirements.txt
cp .env.example .env            # then paste your API key into .env

python run_comparison.py --dry-run   # optional: test the pipeline for free
python run_comparison.py             # 5 scenarios x 3 models = 15 API calls
python blind_review.py               # creates review packets + empty score sheet
# open outputs/<run>/review/*.md, score in outputs/<run>/scoring_sheet.csv
python score_results.py              # unblinds and writes outputs/<run>/summary.md
```

Useful options:

- `--scenarios 01 03` runs only some scenarios
- `--models fable sonnet` runs only some models
- Model IDs, and optional prices for cost estimates, live in `common.py`

## Add a scenario

Copy `scenarios/_template.md` to a new file like `06-short-name.md`. Everything under `## Prompt` is sent to the models; the `## What a strong answer does` section is the scoring key and is never shown to them.

## Scoring

See [rubric.md](rubric.md). Five criteria, each scored 1 to 5: diagnosis, judgment, actionability, communication and efficiency.

## Limitations

- One run per model per scenario. Model outputs vary between runs, so small score differences aren't meaningful.
- One scorer (me). Blind scoring reduces bias but doesn't remove it.
- Five to seven scenarios is a sample, not a benchmark. The goal is practical insight, not a leaderboard.

## Results

_Coming soon._
