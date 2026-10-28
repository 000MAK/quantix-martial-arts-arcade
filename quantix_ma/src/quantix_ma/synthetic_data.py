from __future__ import annotations

import random
from typing import List

from .schema import BoutSequence, POSITION_STATES, validate_sequence


POSITION_PATHS = [
    ["standing_clinch", "guard", "half_guard", "side_control", "mount", "back_control", "submission_lock"],
    ["standing_clinch", "guard", "open_guard", "side_control", "mount", "reset", "guard"],
    ["standing_clinch", "guard", "half_guard", "guard", "side_control", "back_control", "submission_lock"],
    ["standing_clinch", "open_guard", "guard", "mount", "back_control", "reset", "guard"],
]

# Illustrative mean seconds per visit; not derived from real match footage.
MEAN_DWELL_SECONDS = {
    "standing_clinch": 25.0,
    "guard": 30.0,
    "open_guard": 20.0,
    "half_guard": 22.0,
    "side_control": 18.0,
    "mount": 15.0,
    "back_control": 20.0,
    "submission_lock": 8.0,
    "reset": 5.0,
}


def generate_bout_sequences(num_bouts: int = 40, seed: int = 42) -> List[BoutSequence]:
    rng = random.Random(seed)
    sequences: List[BoutSequence] = []

    for bout_index in range(num_bouts):
        path = POSITION_PATHS[rng.randrange(len(POSITION_PATHS))]
        variation = path[:]

        if rng.random() < 0.55:
            variation.append("reset")
            variation.append("guard")
        if rng.random() < 0.4:
            variation.append("back_control")
        if rng.random() < 0.3:
            variation.append("submission_lock")

        base_sequence = validate_sequence(variation)
        if rng.random() < 0.25:
            base_sequence.insert(0, "standing_clinch")
        if base_sequence and base_sequence[-1] != "submission_lock":
            base_sequence.append("reset")

        durations = [round(rng.expovariate(1.0 / MEAN_DWELL_SECONDS[state]), 1) for state in base_sequence]

        sequences.append(
            BoutSequence(
                athlete_id=f"athlete-{(bout_index % 12) + 1:02d}",
                bout_id=f"bout-{bout_index:03d}",
                discipline="bjj_no_gi",
                states=base_sequence,
                durations=durations,
                source="synthetic",
            )
        )

    return sequences


def summarize_state_counts(sequences: List[BoutSequence]):
    counts = {state: 0 for state in POSITION_STATES}
    for seq in sequences:
        for state in seq.states:
            counts[state] += 1
    return counts
