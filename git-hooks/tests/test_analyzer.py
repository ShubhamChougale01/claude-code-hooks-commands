import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import analyzer


def test_dry_run_returns_mock_issues():
    issues = analyzer.analyze("", dry_run=True)
    assert isinstance(issues, list)
    assert len(issues) > 0


def test_dry_run_issue_has_required_fields():
    issues = analyzer.analyze("some diff content", dry_run=True)
    required = {"severity", "category", "file", "line", "message", "code_snippet", "fix"}
    for issue in issues:
        assert required.issubset(issue.keys()), f"Issue missing fields: {issue}"


def test_dry_run_severity_values_are_valid():
    valid = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
    issues = analyzer.analyze("diff", dry_run=True)
    for issue in issues:
        assert issue["severity"] in valid, f"Invalid severity: {issue['severity']}"


def test_dry_run_contains_all_severity_levels():
    issues = analyzer.analyze("diff", dry_run=True)
    severities = {i["severity"] for i in issues}
    assert "CRITICAL" in severities
    assert "HIGH" in severities
    assert "MEDIUM" in severities
    assert "LOW" in severities


def test_dry_run_ignores_diff_content():
    issues_a = analyzer.analyze("diff a", dry_run=True)
    issues_b = analyzer.analyze("completely different diff", dry_run=True)
    assert issues_a == issues_b
