from __future__ import annotations

from .pipeline import run_pipeline


def main() -> None:
    summary = run_pipeline()
    print(summary)


if __name__ == "__main__":
    main()
