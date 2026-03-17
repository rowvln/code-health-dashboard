"""
Scoring Service

Transforms raw analysis data into:
- code health scores (0–100)
- human-readable labels
- prioritized recommendations

This is a rule-based system designed for clarity and explainability.
"""
from __future__ import annotations

from collections import Counter

SEVERITY_WEIGHTS = {
    "fatal": 10,
    "error": 8,
    "warning": 5,
    "refactor": 3,
    "convention": 1,
    "info": 0,
}


def score_file(issue_types: list[str], complexity: int) -> int:
    """
    Calculates a score based on:
    - severity-weighted issue penalties
    - complexity penalties

    Design choice:
    - start from 100 and subtract penalties
    - ensures scores are intuitive and comparable

    Future improvement:
    - weight different issue types differently per use case
    """
    score = 100
    score -= sum(SEVERITY_WEIGHTS.get(issue_type, 1) for issue_type in issue_types)

    if complexity >= 20:
        score -= 15
    elif complexity >= 10:
        score -= 8
    elif complexity >= 5:
        score -= 3

    return max(score, 0)


def get_score_label(score: int) -> str:
    if score >= 90:
        return "Excellent health"
    if score >= 75:
        return "Healthy with minor cleanup"
    if score >= 60:
        return "Fair, but needs improvement"
    if score >= 40:
        return "Needs noticeable revision"
    if score >= 20:
        return "Needs major revision"
    return "Critical condition"


def get_issue_label(issue_count: int) -> str:
    if issue_count == 0:
        return "No issues found"
    if issue_count <= 5:
        return "Low number of issues"
    if issue_count <= 15:
        return "Moderate number of issues"
    if issue_count <= 30:
        return "Heavy issue load"
    return "Very high issue load"


def get_complexity_label(complexity: int) -> str:
    if complexity <= 5:
        return "Easy to understand"
    if complexity <= 10:
        return "Mostly manageable"
    if complexity <= 20:
        return "Understanding takes extra effort"
    if complexity <= 30:
        return "Hard to follow and risky to change"
    return "Very difficult to maintain"


def build_recommendations(file_payloads: list[dict], severity_counter: Counter) -> list[str]:
    """
    Generates actionable recommendations based on:
    - highest issue counts
    - highest complexity
    - severity distribution

    This is a rule-based system (not AI-driven).

    Goal:
    - highlight the highest-impact improvements first
    - keep output understandable for non-technical users
    """
    recommendations = []
    sorted_files = sorted(file_payloads, key=lambda item: item["score"])

    highest_issue_file = max(file_payloads, key=lambda item: item["issues"], default=None)
    highest_complexity_file = max(file_payloads, key=lambda item: item["complexity"], default=None)

    if highest_issue_file and highest_issue_file["issues"] > 0:
        recommendations.append(
            f"Reduce the number of issues in {highest_issue_file['name']}. "
            f"It currently has {highest_issue_file['issues']} findings and offers one of the fastest paths to improving the overall score."
        )

    if highest_complexity_file and highest_complexity_file["complexity"] >= 10:
        recommendations.append(
            f"Refactor the most complex logic in {highest_complexity_file['name']}. "
            f"Its complexity score is {highest_complexity_file['complexity']}, which suggests the code may be harder to understand, test, and maintain."
        )

    if severity_counter.get("fatal", 0) + severity_counter.get("error", 0) > 0:
        recommendations.append(
            "Fix fatal and error-level issues first. These have the highest chance of causing broken behavior or unreliable results."
        )

    if severity_counter.get("warning", 0) > 0:
        recommendations.append(
            "Resolve warning-level issues next. They are often high-impact fixes that improve reliability and maintainability."
        )

    if severity_counter.get("convention", 0) > 0 or severity_counter.get("refactor", 0) > 0:
        recommendations.append(
            "Clean up naming, structure, and readability issues. These are usually fast wins that make the code easier for both current and future developers to work with."
        )

    if not recommendations:
        recommendations.append(
            "No major issues detected. The next step could be trend tracking over time to monitor whether code health improves or declines."
        )

    return recommendations[:5]


def build_score_payload(file_results: list[dict]) -> dict:
    payload_files = []
    severity_counter = Counter()
    issues_found = []

    for file_result in file_results:
        issue_types = [issue.get("type", "info") for issue in file_result["issues"]]
        severity_counter.update(issue_types)
        file_score = score_file(issue_types, file_result["complexity"])
        issue_count = len(file_result["issues"])
        complexity = file_result["complexity"]

        payload_files.append(
            {
                "name": file_result["name"],
                "score": file_score,
                "score_label": get_score_label(file_score),
                "issues": issue_count,
                "issues_label": get_issue_label(issue_count),
                "complexity": complexity,
                "complexity_label": get_complexity_label(complexity),
            }
        )

        for issue in file_result["issues"]:
            issues_found.append(
                {
                    "file": file_result["name"],
                    "line": issue.get("line", "—"),
                    "type": issue.get("type", "info"),
                    "message": issue.get("message", "No description provided"),
                }
            )

    overall_score = round(sum(item["score"] for item in payload_files) / len(payload_files), 0) if payload_files else 100
    total_issues = sum(item["issues"] for item in payload_files)
    average_complexity = round(sum(item["complexity"] for item in payload_files) / len(payload_files), 0) if payload_files else 0

    return {
        "score": int(overall_score),
        "score_label": get_score_label(int(overall_score)),
        "summary": {
            "issues": total_issues,
            "issues_label": get_issue_label(total_issues),
            "high_severity": severity_counter.get("fatal", 0) + severity_counter.get("error", 0),
            "files_analyzed": len(payload_files),
            "complexity": int(average_complexity),
            "complexity_label": get_complexity_label(int(average_complexity)),
        },
        "files": payload_files,
        "issues_found": issues_found,
        "recommendations": build_recommendations(payload_files, severity_counter),
    }