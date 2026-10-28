"""Quantix martial arts analytics package."""

__all__ = ["MarkovTransitionModel", "load_sequences", "run_pipeline"]


def __getattr__(name):
    if name == "MarkovTransitionModel":
        from .markov_model import MarkovTransitionModel
        return MarkovTransitionModel
    if name == "load_sequences":
        from .data_loader import load_sequences
        return load_sequences
    if name == "run_pipeline":
        from .pipeline import run_pipeline
        return run_pipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
