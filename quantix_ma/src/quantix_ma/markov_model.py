from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from .schema import BoutSequence, POSITION_STATES


class MarkovTransitionModel:
    """Semi-Markov model: an embedded jump chain plus per-state dwell times.

    Consecutive repeats of a state are one episode, so the jump chain has no
    self-transitions; time spent in a state is captured by the dwell summary.
    """

    def __init__(self, states: Sequence[str] | None = None, pseudocount: float = 1.0):
        self.states = list(states or POSITION_STATES)
        self.pseudocount = pseudocount
        self.transition_counts = {state: {next_state: 0.0 for next_state in self.states} for state in self.states}
        self.transition_matrix = {state: {next_state: 0.0 for next_state in self.states} for state in self.states}
        self.dwell_times: Dict[str, Dict[str, float]] = {}
        self.dwell_unit = "steps"

    def fit(self, sequences: Iterable[BoutSequence]) -> None:
        sequences = list(sequences)
        for sequence in sequences:
            episode_states = [state for state, _, _ in sequence.episodes()]
            for current, nxt in zip(episode_states, episode_states[1:]):
                self.transition_counts[current][nxt] += 1.0

        for current in self.states:
            targets = [nxt for nxt in self.states if nxt != current]
            total = sum(self.transition_counts[current][nxt] for nxt in targets) + self.pseudocount * len(targets)
            for nxt in self.states:
                if nxt == current or total == 0:
                    self.transition_matrix[current][nxt] = 0.0
                else:
                    self.transition_matrix[current][nxt] = (
                        self.transition_counts[current][nxt] + self.pseudocount
                    ) / total

        self.dwell_times = self.summarize_dwell_times(sequences)

    def predict_next_state(self, current_state: str) -> Dict[str, float]:
        if current_state not in self.transition_matrix:
            raise ValueError(f"Unknown current state '{current_state}'")
        return dict(self.transition_matrix[current_state])

    def summarize_dwell_times(self, sequences: Iterable[BoutSequence]) -> Dict[str, Dict[str, float]]:
        """Mean and max time per visit for each state.

        Uses seconds when every sequence has durations, otherwise step counts.
        """
        sequences = list(sequences)
        timed = bool(sequences) and all(seq.durations is not None for seq in sequences)
        self.dwell_unit = "seconds" if timed else "steps"

        dwell_times = defaultdict(list)
        for sequence in sequences:
            for state, seconds, steps in sequence.episodes():
                dwell_times[state].append(seconds if timed else float(steps))

        summary = {}
        for state in self.states:
            values = dwell_times.get(state, [])
            summary[state] = {
                "visits": len(values),
                "mean": round(sum(values) / len(values), 3) if values else 0.0,
                "max": round(max(values), 3) if values else 0.0,
            }
        return summary

    def best_transitions(self, top_n: int = 5) -> List[tuple[str, str, float]]:
        ranked = []
        for current in self.states:
            for nxt, prob in self.transition_matrix[current].items():
                ranked.append((current, nxt, prob))
        ranked.sort(key=lambda item: item[2], reverse=True)
        return ranked[:top_n]

    def save(self, path: str | Path) -> None:
        json_path = Path(path)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "states": self.states,
            "matrix": self.transition_matrix,
            "dwell_unit": self.dwell_unit,
            "dwell_times": self.dwell_times,
            "best_transitions": [
                {"from": start, "to": end, "probability": round(probability, 4)}
                for start, end, probability in self.best_transitions(top_n=12)
            ],
        }
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path):
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        model = cls(states=payload["states"])
        model.transition_matrix = payload["matrix"]
        model.dwell_unit = payload.get("dwell_unit", "steps")
        model.dwell_times = payload.get("dwell_times", {})
        return model
