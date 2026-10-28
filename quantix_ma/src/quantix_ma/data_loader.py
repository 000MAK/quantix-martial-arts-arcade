from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List

from .schema import BoutSequence, validate_durations, validate_sequence
from .synthetic_data import generate_bout_sequences


def _split_pipe(value) -> List[str]:
    return [part.strip() for part in str(value or "").split("|") if part.strip()]


def _load_csv_sequences(path: Path) -> List[BoutSequence]:
    sequences: List[BoutSequence] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            sequence = validate_sequence(_split_pipe(row.get("states")))
            raw_durations = _split_pipe(row.get("durations"))
            sequences.append(
                BoutSequence(
                    athlete_id=row.get("athlete_id", "athlete-unknown"),
                    bout_id=row.get("bout_id", "bout-unknown"),
                    discipline=row.get("discipline", "bjj_no_gi"),
                    states=sequence,
                    durations=validate_durations(raw_durations or None, sequence),
                    source=row.get("source") or "labeled",
                )
            )
    return sequences


def _load_json_sequences(path: Path) -> List[BoutSequence]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload if isinstance(payload, list) else payload.get("sequences", [])
    sequences: List[BoutSequence] = []
    for item in records:
        states = validate_sequence(item.get("states", []))
        sequences.append(
            BoutSequence(
                athlete_id=item.get("athlete_id", "athlete-unknown"),
                bout_id=item.get("bout_id", "bout-unknown"),
                discipline=item.get("discipline", "bjj_no_gi"),
                states=states,
                durations=validate_durations(item.get("durations"), states),
                source=item.get("source", "labeled"),
            )
        )
    return sequences


def load_sequences(data_dir: str | Path | None = None, allow_synthetic: bool = True) -> List[BoutSequence]:
    """Load labeled sequences from data_dir, falling back to in-memory synthetic data.

    Synthetic sequences are never written into data_dir, so they cannot later be
    mistaken for labeled match data. Each sequence carries its `source`.
    """
    data_root = Path(data_dir) if data_dir is not None else Path(__file__).resolve().parents[2] / "data"
    csv_path = data_root / "bjj_sequences.csv"
    json_path = data_root / "bjj_sequences.json"

    if csv_path.exists():
        return _load_csv_sequences(csv_path)
    if json_path.exists():
        return _load_json_sequences(json_path)

    if not allow_synthetic:
        raise FileNotFoundError(f"No bjj_sequences.csv or bjj_sequences.json in {data_root}")
    return generate_bout_sequences(num_bouts=80, seed=11)
