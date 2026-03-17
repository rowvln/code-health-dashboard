"""
Analyzer Service

Handles:
- file ingestion (.py or .zip)
- extraction of zip archives
- running static analysis tools (pylint, radon)
- normalizing results into a structured format

This acts as the bridge between raw tooling output and the scoring system.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from .scoring import build_score_payload


def _should_analyze_file(file_path: Path) -> bool:
    """
    Determines whether a file should be included in analysis.

    Filters out:
    - macOS metadata folders (__MACOSX)
    - hidden system files (.DS_Store)
    - AppleDouble metadata files (._*)

    Keeps:
    - valid Python source files (.py), including underscore-prefixed modules
    """
    parts = file_path.parts
    name = file_path.name

    if "__MACOSX" in parts:
        return False

    if name == ".DS_Store":
        return False

    if name.startswith("._"):
        return False

    return file_path.suffix.lower() == ".py"


def analyze_path(file_path: Path) -> dict:
    if file_path.suffix.lower() == ".zip":
        return _analyze_zip(file_path)
    return _analyze_python_files([file_path])


def _analyze_zip(zip_path: Path) -> dict:
    """
    Extracts and analyzes all valid Python files from a zip archive.

    Notes:
    - Uses a temporary directory to avoid polluting the project
    - Recursively scans extracted contents
    - Filters out system/metadata files
    - Future improvement: preserve relative paths for better file identification
    """
    with TemporaryDirectory() as temp_dir:
        extract_dir = Path(temp_dir) / "extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        python_files = [
            path for path in extract_dir.rglob("*")
            if path.is_file() and _should_analyze_file(path)
        ]

        if not python_files:
            return {
                "score": 0,
                "score_label": "No valid Python files found",
                "summary": {
                    "issues": 0,
                    "issues_label": "No issues found",
                    "high_severity": 0,
                    "files_analyzed": 0,
                    "complexity": 0,
                    "complexity_label": "No complexity to analyze",
                },
                "files": [],
                "issues_found": [],
                "recommendations": [
                    "Upload a .py file or a .zip that contains valid Python source files."
                ],
            }

        return _analyze_python_files(python_files)


def _normalize_pylint_issue(issue: dict) -> dict:
    return {
        "type": issue.get("type", "info"),
        "message": issue.get("message", "No description provided"),
        "line": issue.get("line", "—"),
        "symbol": issue.get("symbol", ""),
        "message_id": issue.get("message-id", ""),
    }


def _run_pylint(file_path: Path) -> dict:
    """
    Runs pylint on a given file and returns normalized issue data.

    Notes:
    - Uses JSON output format for structured parsing
    - Does not fail on lint errors (check=False)
    - Future improvement: support configuration via .pylintrc
    """
    command = [
        shutil.which("pylint") or "pylint",
        str(file_path),
        "--output-format=json",
        "--score=n",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)

    if not completed.stdout.strip():
        return {"issues": []}

    try:
        raw_issues = json.loads(completed.stdout)
        issues = [_normalize_pylint_issue(issue) for issue in raw_issues]
    except json.JSONDecodeError:
        issues = []

    return {"issues": issues}


def _run_radon(file_path: Path) -> dict:
    """
    Runs radon to calculate cyclomatic complexity.

    Notes:
    - Handles inconsistent JSON structures returned by radon
    - Falls back gracefully if parsing fails
    - Uses max complexity as a representative metric

    Future improvement:
    - include average complexity
    - include per-function breakdown
    """
    command = [
        shutil.which("radon") or "radon",
        "cc",
        str(file_path),
        "-j",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)

    if not completed.stdout.strip():
        return {"complexity": 0}

    try:
        data = json.loads(completed.stdout)

        entries = data.get(str(file_path))

        if entries is None and isinstance(data, dict) and data:
            entries = next(iter(data.values()))

        if isinstance(entries, dict):
            entries = [entries]
        elif not isinstance(entries, list):
            entries = []

        max_complexity = max(
            (
                entry.get("complexity", 0)
                for entry in entries
                if isinstance(entry, dict)
            ),
            default=0,
        )

    except json.JSONDecodeError:
        max_complexity = 0

    return {"complexity": max_complexity}


def _analyze_python_files(files: list[Path]) -> dict:
    """
    Runs analysis on a list of Python files.

    Workflow:
    - run pylint (issues)
    - run radon (complexity)
    - aggregate results into a unified payload

    Future improvement:
    - parallelize analysis for performance
    """
    file_results = []

    for file_path in files:
        pylint_result = _run_pylint(file_path)
        radon_result = _run_radon(file_path)

        file_results.append(
            {
                "name": file_path.name,
                "issues": pylint_result["issues"],
                "complexity": radon_result["complexity"],
            }
        )

    return build_score_payload(file_results)