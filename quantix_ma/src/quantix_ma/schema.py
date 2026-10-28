from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Tuple

POSITION_STATES = [
    "standing_clinch",
    "guard",
    "open_guard",
    "half_guard",
    "side_control",
    "mount",
    "back_control",
    "submission_lock",
    "reset",
]

STATE_TO_INDEX = {state: idx for idx, state in enumerate(POSITION_STATES)}


@dataclass
class BoutSequence:
    athlete_id: str
    bout_id: str
    discipline: str
    states: List[str] = field(default_factory=list)
    # Seconds spent in each entry of `states`; None when the source has no timing.
    durations: Optional[List[float]] = None
    source: str = "labeled"

    def to_state_indices(self) -> List[int]:
        return [STATE_TO_INDEX[state] for state in self.states]

    def episodes(self) -> List[Tuple[str, float, int]]:
        """Collapse consecutive repeats into (state, seconds, steps) episodes."""
        episodes: List[Tuple[str, float, int]] = []
        for index, state in enumerate(self.states):
            seconds = self.durations[index] if self.durations is not None else 0.0
            if episodes and episodes[-1][0] == state:
                _, prev_seconds, prev_steps = episodes[-1]
                episodes[-1] = (state, prev_seconds + seconds, prev_steps + 1)
            else:
                episodes.append((state, seconds, 1))
        return episodes


def ensure_valid_state(state: str) -> str:
    if state not in STATE_TO_INDEX:
        raise ValueError(f"Unsupported state '{state}'")
    return state


def validate_sequence(sequence: Iterable[str]) -> List[str]:
    cleaned = [ensure_valid_state(state) for state in sequence]
    return cleaned


def validate_durations(durations: Optional[Iterable[float]], states: List[str]) -> Optional[List[float]]:
    if durations is None:
        return None
    cleaned = [float(value) for value in durations]
    if len(cleaned) != len(states):
        raise ValueError(f"Expected {len(states)} durations, got {len(cleaned)}")
    if any(value < 0 for value in cleaned):
        raise ValueError("Durations must be non-negative seconds")
    return cleaned
