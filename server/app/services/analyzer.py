"""
Analyzer Service

This module is responsible for:
- handling uploaded files (.py or .zip)
- extracting zip archives into a temporary workspace
- filtering valid Python source files
- running static analysis tools (pylint + radon)
- normalizing results into a consistent structure

This acts as the core pipeline between raw code input and the scoring system.

Design notes:
- synchronous processing (MVP simplicity)
- defensive handling of malformed files and tool failures
- avoids analyzing system/metadata files (macOS, venv, etc.)

Future improvements:
- parallelize file analysis for performance
- support additional languages
- add background job processing (Celery / queue)
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
    - system folders (__MACOSX, .git, etc.)
    - dependency folders (venv, node_modules)
    - cache folders (__pycache__)
    - macOS metadata files (.DS_Store, ._*)

    Keeps:
    - valid Python source files (.py)

    This prevents unnecessary processing and avoids noise from non-source files.
    """
    parts = set(file_path.parts)
    name = file_path.name

    ignored_dirs = {
        "__MACOSX",
        ".git",
        "node_modules",
        "venv",
        ".venv",
        "__pycache__",
        "dist",
        "build",
        ".mypy_cache",
        ".pytest_cache",
    }

    if parts & ignored_dirs:
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
    Extracts and analyzes Python files from a zip archive.

    Workflow:
    1. extract zip into a temporary directory
    2. recursively scan for valid Python files
    3. apply filtering rules (_should_analyze_file)
    4. limit file count to keep performance predictable
    5. pass filtered files into analysis pipeline

    Design decisions:
    - uses TemporaryDirectory to avoid polluting filesystem
    - enforces a max file limit to prevent long-running requests

    Future improvements:
    - preserve folder structure in results
    - allow user-configurable file limits
    """
    with TemporaryDirectory() as temp_dir:
        extract_dir = Path(temp_dir) / "extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        python_files = sorted(
            [
                path for path in extract_dir.rglob("*")
                if path.is_file() and _should_analyze_file(path)
            ]
        )

        MAX_FILES = 100

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

        truncated = len(python_files) > MAX_FILES
        files_to_analyze = python_files[:MAX_FILES]

        result = _analyze_python_files(files_to_analyze)

        if truncated:
            result["recommendations"].insert(
                0,
                f"Only the first {MAX_FILES} Python files were analyzed to keep the MVP responsive."
            )

        return result

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
    Runs pylint on a given Python file.

    Returns:
    - list of normalized issues (type, message, line, etc.)

    Notes:
    - uses JSON output for structured parsing
    - timeout prevents a single file from blocking the entire request
    - does not fail the pipeline if pylint errors

    Future improvements:
    - support custom pylint configs (.pylintrc)
    - group issues by severity before returning
    """
    command = [
        shutil.which("pylint") or "pylint",
        str(file_path),
        "--output-format=json",
        "--score=n",
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return {
            "issues": [
                {
                    "type": "warning",
                    "message": "pylint analysis timed out for this file",
                    "line": "—",
                    "symbol": "timeout",
                    "message_id": "TIMEOUT",
                }
            ]
        }

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

    Returns:
    - maximum complexity value found in the file

    Notes:
    - radon output structure can vary → normalized defensively
    - timeout prevents long-running analysis on complex files

    Design choice:
    - using max complexity as a simple, interpretable signal

    Future improvements:
    - include average complexity
    - include per-function breakdown
    """
    command = [
        shutil.which("radon") or "radon",
        "cc",
        str(file_path),
        "-j",
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return {"complexity": 0}

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
    Executes analysis on a list of Python files.

    For each file:
    - run pylint (issue detection)
    - run radon (complexity measurement)
    - collect results into a unified structure

    Output:
    - passed into scoring layer to compute overall insights

    Performance note:
    - currently sequential (simpler for MVP)
    - could be parallelized in future for large inputs
    """
    file_results = []

    for index, file_path in enumerate(files, start=1):
        print(f"Analyzing file {index}/{len(files)}: {file_path}")
        pylint_result = _run_pylint(file_path)
        radon_result = _run_radon(file_path)

        file_results.append(
            {
                "name": file_path.name,
                "issues": pylint_result["issues"],
                "complexity": radon_result["complexity"],
            }
        )

    print("Finished analyzing all files")
    return build_score_payload(file_results)