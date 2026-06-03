import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from severity_detector import detect


def test_critical_blocks():
    issues = [{"severity": "CRITICAL", "category": "security", "file": "a.py", "line": 1,
               "message": "SQL injection", "code_snippet": "", "fix": ""}]
    result = detect(issues)
    assert result["should_block"] is True
    assert len(result["critical"]) == 1
    assert result["total"] == 1


def test_high_blocks_by_default():
    issues = [{"severity": "HIGH", "category": "performance", "file": "b.py", "line": 2,
               "message": "N+1 query", "code_snippet": "", "fix": ""}]
    result = detect(issues)
    assert result["should_block"] is True
    assert len(result["high"]) == 1


def test_medium_does_not_block():
    issues = [{"severity": "MEDIUM", "category": "error_handling", "file": "c.py", "line": 3,
               "message": "Swallowed exception", "code_snippet": "", "fix": ""}]
    result = detect(issues)
    assert result["should_block"] is False
    assert len(result["medium"]) == 1


def test_low_does_not_block():
    issues = [{"severity": "LOW", "category": "code_quality", "file": "d.py", "line": 4,
               "message": "Missing docstring", "code_snippet": "", "fix": ""}]
    result = detect(issues)
    assert result["should_block"] is False
    assert len(result["low"]) == 1


def test_empty_issues():
    result = detect([])
    assert result["should_block"] is False
    assert result["total"] == 0


def test_mixed_severities():
    issues = [
        {"severity": "CRITICAL", "category": "security", "file": "a.py", "line": 1, "message": "", "code_snippet": "", "fix": ""},
        {"severity": "MEDIUM",   "category": "error_handling", "file": "b.py", "line": 2, "message": "", "code_snippet": "", "fix": ""},
        {"severity": "LOW",      "category": "code_quality", "file": "c.py", "line": 3, "message": "", "code_snippet": "", "fix": ""},
    ]
    result = detect(issues)
    assert result["should_block"] is True
    assert result["total"] == 3


def test_unknown_severity_falls_to_low():
    issues = [{"severity": "UNKNOWN", "category": "other", "file": "x.py", "line": 1,
               "message": "something", "code_snippet": "", "fix": ""}]
    result = detect(issues)
    assert len(result["low"]) == 1
    assert result["should_block"] is False
