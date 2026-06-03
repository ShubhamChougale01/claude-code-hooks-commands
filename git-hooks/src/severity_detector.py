from config import CRITICAL, HIGH, MEDIUM, LOW, BLOCKING_SEVERITIES, BLOCK_ON_HIGH


def detect(issues: list) -> dict:
    grouped = {CRITICAL: [], HIGH: [], MEDIUM: [], LOW: []}

    for issue in issues:
        severity = issue.get("severity", "").upper()
        if severity in grouped:
            grouped[severity].append(issue)
        else:
            grouped[LOW].append(issue)

    has_blocking = bool(grouped[CRITICAL])
    if BLOCK_ON_HIGH:
        has_blocking = has_blocking or bool(grouped[HIGH])

    return {
        "critical": grouped[CRITICAL],
        "high": grouped[HIGH],
        "medium": grouped[MEDIUM],
        "low": grouped[LOW],
        "should_block": has_blocking,
        "total": sum(len(v) for v in grouped.values()),
    }
