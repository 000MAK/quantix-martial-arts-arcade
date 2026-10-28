# Quantix Martial Arts Analytics

This project is a lightweight research prototype for modeling martial-arts state transitions using Markov chains and semi-Markov dwell-time summaries.

The first working use case is BJJ No-Gi positional flow analysis.

## Project structure

- `src/quantix_ma` - Python package
- `data/` - training data and outputs
- `notebooks/` - optional analysis notebooks

## Quick start

```bash
cd f:\İndirilenler\games\quantix_ma
set PYTHONPATH=src
python -m quantix_ma.train
```

The training pipeline loads labeled sequences from `data/bjj_sequences.csv` or `data/bjj_sequences.json` when present. Otherwise it runs on synthetic sequences generated in memory; these are never written into `data/`, and the summary and HTML report are marked `synthetic`. `data/samples/` holds a synthetic example of the JSON format.

Run the tests with:

```bash
python -m unittest discover -s tests
```

## Data format

JSON: `{"sequences": [{"athlete_id", "bout_id", "discipline", "states": [...], "durations": [...], "source"}]}`

CSV: columns `athlete_id,bout_id,discipline,states,durations,source`, with `states` and `durations` pipe-separated (`guard|mount`, `12|20`).

`durations` (seconds per state, optional) must match `states` in length. Consecutive repeats of a state are merged into one episode. Dwell times are reported in seconds when every sequence has durations, otherwise in steps.

## Included prototype

- synthetic or CSV/JSON sequence loading for BJJ-style positional episodes
- semi-Markov model: jump-chain transition matrix (no self-loops) plus per-state dwell times
- dwell-time summary by state (visits, mean, max)
- export of transition model to JSON
- HTML transition report generation
- baseline pipeline that is ready for replacement with real ADCC/IBJJF labeling

## Planned expansion

- MediaPipe pose extraction
- GLMM normalization for athlete/bout effects
- injury-risk modeling
- coach dashboards and HTML reports
- 100-discipline taxonomy and cross-discipline comparisons
