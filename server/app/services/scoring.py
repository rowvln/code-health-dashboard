"""
Scoring Service

Transforms raw analysis data into:
- code health scores (0–100)
- human-readable labels
- prioritized recommendations

This layer is intentionally rule-based to ensure:
- explainability (no "black box" logic)
- consistency across runs
- ease of iteration and extension

Design philosophy:
- deterministic scoring
- simple mental model (start at 100, subtract penalties)
- outputs that are understandable to both technical and non-technical users

Future improvements:
- configurable scoring weights
- project-specific scoring profiles
- AI-assisted recommendation layer
"""
from __future__ import annotations

from collections import Counter

# Maps issue severity → penalty weight
# Higher severity = larger impact on score
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
    Computes a code health score for a single file.

    Scoring model:
    - start from 100
    - subtract severity-weighted issue penalties
    - subtract complexity penalties based on thresholds

    Why this approach:
    - keeps scoring intuitive (higher = better)
    - easy to explain to non-technical users
    - avoids hidden or unpredictable weighting

    Complexity penalties:
    - 5+   → small penalty
    - 10+  → moderate penalty
    - 20+  → high penalty

    Future improvements:
    - dynamic scoring weights
    - per-project scoring calibration
    """
    score = 100

    # subtract issue penalties
    score -= sum(SEVERITY_WEIGHTS.get(issue_type, 1) for issue_type in issue_types)

    # subtract complexity penalties
    if complexity >= 20:
        score -= 15
    elif complexity >= 10:
        score -= 8
    elif complexity >= 5:
        score -= 3

    # prevent negative scores
    return max(score, 0)


def get_score_label(score: int) -> str:
    """
    Converts numeric score → human-readable interpretation.

    Goal:
    - make results understandable at a glance
    - bridge technical metrics with business-friendly language
    """
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
    """
    Interprets total issue count into a readable label.
    """
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
    """
    Interprets complexity score into maintainability guidance.

    Helps answer:
    - "How hard is this code to understand or modify?"
    """
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
    Generates prioritized, actionable recommendations.

    Inputs:
    - file-level data (issues + complexity)
    - aggregated severity distribution

    Strategy:
    - identify highest-impact problems first
    - focus on "quick wins" + "big risks"
    - limit output to top 3–5 recommendations

    Important:
    - rule-based (not AI-generated)
    - deterministic and explainable

    Why this matters:
    - helps users understand *what to do next*
    - bridges analysis → action
    """
    recommendations = []

    # identify worst offenders
    highest_issue_file = max(file_payloads, key=lambda item: item["issues"], default=None)
    highest_complexity_file = max(file_payloads, key=lambda item: item["complexity"], default=None)

    # issue-based recommendation
    if highest_issue_file and highest_issue_file["issues"] > 0:
        recommendations.append(
            f"Reduce the number of issues in {highest_issue_file['name']}. "
            f"It currently has {highest_issue_file['issues']} findings and offers one of the fastest paths to improving the overall score."
        )

    # complexity-based recommendation
    if highest_complexity_file and highest_complexity_file["complexity"] >= 10:
        recommendations.append(
            f"Refactor the most complex logic in {highest_complexity_file['name']}. "
            f"Its complexity score is {highest_complexity_file['complexity']}, which suggests the code may be harder to understand, test, and maintain."
        )

    # severity-based recommendations
    if severity_counter.get("fatal", 0) + severity_counter.get("error", 0) > 0:
        recommendations.append(
            "Fix fatal and error-level issues first. These have the highest risk of causing failures or incorrect behavior."
        )

    if severity_counter.get("warning", 0) > 0:
        recommendations.append(
            "Resolve warning-level issues next. These often represent meaningful improvements to reliability and maintainability."
        )

    if severity_counter.get("convention", 0) > 0 or severity_counter.get("refactor", 0) > 0:
        recommendations.append(
            "Clean up naming, structure, and readability issues. These are usually fast wins that improve developer experience."
        )

    # fallback
    if not recommendations:
        recommendations.append(
            "No major issues detected. Consider adding trend tracking to monitor how code health evolves over time."
        )

    return recommendations[:5]


def build_score_payload(file_results: list[dict]) -> dict:
    """
    Transforms raw analysis results into a frontend-ready payload.

    Responsibilities:
    - compute per-file scores + labels
    - aggregate overall metrics
    - flatten issue data for display
    - generate recommendations

    Output is designed for:
    - dashboard rendering
    - easy consumption by UI components
    """
    payload_files = []
    severity_counter = Counter()
    issues_found = []

    for file_result in file_results:
        # extract issue types for scoring
        issue_types = [issue.get("type", "info") for issue in file_result["issues"]]

        # update global severity distribution
        severity_counter.update(issue_types)

        # compute file-level metrics
        file_score = score_file(issue_types, file_result["complexity"])
        issue_count = len(file_result["issues"])
        complexity = file_result["complexity"]

        # build file summary
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

        # flatten issues for UI rendering
        for issue in file_result["issues"]:
            issues_found.append(
                {
                    "file": file_result["name"],
                    "line": issue.get("line", "—"),
                    "type": issue.get("type", "info"),
                    "message": issue.get("message", "No description provided"),
                }
            )

    # aggregate metrics
    overall_score = round(
        sum(item["score"] for item in payload_files) / len(payload_files), 0
    ) if payload_files else 100

    total_issues = sum(item["issues"] for item in payload_files)

    average_complexity = round(
        sum(item["complexity"] for item in payload_files) / len(payload_files), 0
    ) if payload_files else 0

    # final payload
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