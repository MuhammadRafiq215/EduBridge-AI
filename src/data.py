"""Dataset acquisition and quality checks for EduBridge AI.

The current UCI download may contain a nested student.zip archive. This
loader searches both the outer and nested ZIP files before reporting failure.
"""
from __future__ import annotations

from io import BytesIO
from zipfile import BadZipFile, ZipFile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd

UCI_ZIP_URLS = (
    "https://archive.ics.uci.edu/static/public/320/student+performance.zip",
    "https://archive.ics.uci.edu/ml/machine-learning-databases/00320/student.zip",
)
UCI_ZIP_URL = UCI_ZIP_URLS[0]
TARGET_COLUMN = "G3"
LEAKAGE_COLUMNS = ["G1", "G2", "G3"]
DATASET_FILE = "student-mat.csv"


def _read_math_csv_from_zip(archive_bytes: bytes) -> pd.DataFrame | None:
    """Find student-mat.csv in a ZIP, including one or more nested ZIP files."""
    pending = [archive_bytes]
    visited = 0
    while pending and visited < 8:
        payload = pending.pop(0)
        visited += 1
        try:
            with ZipFile(BytesIO(payload)) as archive:
                members = archive.namelist()
                csv_candidates = [
                    name for name in members
                    if name.replace("\\", "/").rsplit("/", 1)[-1].lower() == DATASET_FILE
                ]
                if csv_candidates:
                    with archive.open(csv_candidates[0]) as csv_file:
                        frame = pd.read_csv(csv_file, sep=";")
                    if TARGET_COLUMN not in frame.columns:
                        raise ValueError(
                            "The UCI mathematics CSV was found, but its expected G3 target column is missing."
                        )
                    return frame
                nested_archives = [
                    name for name in members
                    if name.lower().endswith(".zip") and not name.startswith("__MACOSX/")
                ]
                for name in nested_archives:
                    with archive.open(name) as nested:
                        pending.append(nested.read())
        except BadZipFile:
            continue
    return None


def load_student_math() -> pd.DataFrame:
    """Download the official UCI archive and locate its nested mathematics CSV."""
    failures = []
    for url in UCI_ZIP_URLS:
        try:
            request = Request(
                url,
                headers={"User-Agent": "EduBridgeAI/3.0 research-demo"},
            )
            with urlopen(request, timeout=45) as response:
                archive_bytes = response.read()
            frame = _read_math_csv_from_zip(archive_bytes)
            if frame is not None:
                return frame
            failures.append(f"{url}: ZIP downloaded, but {DATASET_FILE} was not present in the archive.")
        except (HTTPError, URLError, TimeoutError, OSError, BadZipFile) as exc:
            failures.append(f"{url}: {type(exc).__name__}: {exc}")
    detail = " | ".join(failures)
    raise RuntimeError(
        "EduBridge could not retrieve the UCI mathematics dataset from its official archive locations. "
        "The downloader checks nested ZIP files and retries the official legacy archive. "
        f"Details: {detail}"
    )


def audit_dataset(frame: pd.DataFrame) -> dict:
    """Return transparent, JSON-serializable dataset quality information."""
    if TARGET_COLUMN not in frame.columns:
        raise ValueError(f"Dataset audit requires the {TARGET_COLUMN} target column.")
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
