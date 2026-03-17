from app.services.scoring import score_file


def test_score_file_reduces_score_for_issues_and_complexity():
    score = score_file(["error", "warning", "convention"], 12)
    assert score < 100
    assert score >= 0
