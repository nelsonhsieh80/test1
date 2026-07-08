"""Entry point for the latest generated price extractor."""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).parent / "final_runs" / "run_1" / "final_script.py"), run_name="__main__")
