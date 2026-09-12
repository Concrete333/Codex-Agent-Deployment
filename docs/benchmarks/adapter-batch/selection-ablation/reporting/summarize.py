"""Offline accounting adapter for this nested suite; no model calls."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import experiment

fixture = experiment.shared.load()
# The reused summarizer resolves its accounting library relative to HERE.
# Keep its canonical library path without changing the frozen experiment driver.
experiment.shared.HERE = experiment.HERE.parent
experiment.shared.summarize(fixture)
