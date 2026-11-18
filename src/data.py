"""Dataset acquisition and quality checks for EduBridge AI."""
from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile
from urllib.request import Request, urlopen

import pandas as pd

UCI_ZIP_URL = "https://archive.ics.uci.edu/static/public/320/student+performance.zip"
TARGET_COLUMN = "G3"
LEAKAGE_COLUMNS = ["G1", "G2", "G3"]


def load_student_math() -> pd.DataFrame:
    """Download the official UCI archive and load the mathematics cohort."""
    request = Request(UCI_ZIP_URL, headers={"User-Agent": "EduBridgeAI/2.0 research-demo"})
    with urlopen(request, timeout=45) as response:
        archive_bytes = response.read()
    with ZipFile(BytesIO(archive_bytes)) as archive:
        candidates = [name for name in archive.namelist() if name.lower().endswith("student-mat.csv")]
        if not candidates:
            raise FileNotFoundError("student-mat.csv was not found in the official UCI archive.")
        with archive.open(candidates[0]) as csv_file:
            frame = pd.read_csv(csv_file, sep=";")
    if TARGET_COLUMN not in frame.columns:
        raise ValueError("The downloaded dataset does not contain the expected G3 target column.")
    return frame


def audit_dataset(frame: pd.DataFrame) -> dict:
    """Return transparent, JSON-serializable dataset quality information."""
    return {
        "rows": int(frame.shape[0]),
        "columns": int(frame.shape[1]),
        "duplicate_rows": int(frame.duplicated().sum()),
        "missing_cells": int(frame.isna().sum().sum()),
        "missing_by_column": {str(k): int(v) for k, v in frame.isna().sum().items()},
        "target_min": float(frame[TARGET_COLUMN].min()),
        "target_max": float(frame[TARGET_COLUMN].max()),
        "target_mean": round(float(frame[TARGET_COLUMN].mean()), 3),
        "below_threshold_count": int((frame[TARGET_COLUMN] < 10).sum()),
        "at_or_above_threshold_count": int((frame[TARGET_COLUMN] >= 10).sum()),
        "excluded_grade_columns": LEAKAGE_COLUMNS,
    }
