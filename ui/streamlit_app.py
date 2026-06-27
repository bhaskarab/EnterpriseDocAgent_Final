"""Run the primary Streamlit app from the repository root."""

import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[1] / "streamlit_app.py"), run_name="__main__")
