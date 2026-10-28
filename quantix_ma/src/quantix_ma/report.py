from __future__ import annotations

from html import escape
from pathlib import Path

from .markov_model import MarkovTransitionModel


def render_transition_report(
    model: MarkovTransitionModel,
    title: str = "Quantix BJJ Transition Report",
    data_source: str = "unknown",
    sequence_count: int = 0,
) -> str:
    states = model.states
    rows = []
    for current in states:
        probabilities = model.transition_matrix[current]
        rows.append(
            f"<tr><th>{escape(current)}</th>" +
            "".join(f"<td>{probabilities[next_state]:.3f}</td>" for next_state in states) +
            "</tr>"
        )

    dwell_rows = []
    for state in states:
        stats = model.dwell_times.get(state, {"visits": 0, "mean": 0.0, "max": 0.0})
        dwell_rows.append(
            f"<tr><th>{escape(state)}</th><td>{stats['visits']}</td>"
            f"<td>{stats['mean']:.2f}</td><td>{stats['max']:.2f}</td></tr>"
        )

    warning = ""
    if "synthetic" in data_source:
        warning = ('<div class="warn">Synthetic data: these numbers demonstrate the pipeline only '
                   'and say nothing about real athletes or matches.</div>')

    headers = "".join(f"<th>{escape(state)}</th>" for state in states)
    unit = escape(model.dwell_unit)
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\"/>
  <title>{escape(title)}</title>
  <style>
    body {{ font-family: Segoe UI, sans-serif; background: #0b1220; color: #edf4ff; margin: 32px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
    th, td {{ padding: 8px 10px; border: 1px solid #2c3a50; text-align: center; }}
    th {{ background: #111c2d; }}
    h1 {{ margin-bottom: 12px; }}
    h2 {{ margin-top: 32px; }}
    .meta {{ color: #a9bbcf; margin-bottom: 20px; }}
    .warn {{ background: #3a2a0b; border: 1px solid #a8741a; color: #ffd98a; padding: 10px 14px; }}
  </style>
</head>
<body>
  <h1>{escape(title)}</h1>
  <div class=\"meta\">Data source: {escape(data_source)} &middot; Sequences: {sequence_count} &middot; State count: {len(states)}</div>
  {warning}
  <h2>Jump-chain transition probabilities</h2>
  <table>
    <thead>
      <tr><th>From / To</th>{headers}</tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
  <h2>Dwell time per visit ({unit})</h2>
  <table>
    <thead>
      <tr><th>State</th><th>Visits</th><th>Mean</th><th>Max</th></tr>
    </thead>
    <tbody>
      {''.join(dwell_rows)}
    </tbody>
  </table>
</body>
</html>
"""


def write_report(
    model: MarkovTransitionModel,
    output_path: str | Path,
    data_source: str = "unknown",
    sequence_count: int = 0,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    html = render_transition_report(model, data_source=data_source, sequence_count=sequence_count)
    path.write_text(html, encoding="utf-8")
    return path
