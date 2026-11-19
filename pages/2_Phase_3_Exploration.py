"""Streamlit multipage entry point; re-execute the standalone workspace on navigation."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parents[1] / "phase3.py"), run_name="__main__")
