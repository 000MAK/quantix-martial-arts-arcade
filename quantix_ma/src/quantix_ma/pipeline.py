from __future__ import annotations

import json
from pathlib import Path

from .data_loader import load_sequences
from .markov_model import MarkovTransitionModel
from .report import write_report


def run_pipeline(data_dir: str | Path | None = None, output_dir: str | Path | None = None) -> dict:
    data_root = Path(data_dir) if data_dir is not None else Path(__file__).resolve().parents[2] / "data"
    output_root = Path(output_dir) if output_dir is not None else data_root / "outputs"
    output_root.mkdir(parents=True, exist_ok=True)

    sequences = load_sequences(data_root)
    data_source = ",".join(sorted({seq.source for seq in sequences})) or "none"
    model = MarkovTransitionModel()
    model.fit(sequences)

    model_path = output_root / "transition_model.json"
    report_path = output_root / "transition_report.html"
    write_report(model, report_path, data_source=data_source, sequence_count=len(sequences))
    model.save(model_path)

    summary = {
        "data_source": data_source,
        "sequence_count": len(sequences),
        "state_count": len(model.states),
        "best_transitions": [
            {"from": start, "to": end, "probability": round(probability, 4)}
            for start, end, probability in model.best_transitions(top_n=6)
        ],
        "dwell_unit": model.dwell_unit,
        "dwell_time_summary": model.dwell_times,
        "model_path": str(model_path),
        "report_path": str(report_path),
    }
    return summary


def main() -> None:
    summary = run_pipeline()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
