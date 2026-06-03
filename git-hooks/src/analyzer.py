import json
import os
import sys
from config import REVIEW_MODEL, SYSTEM_PROMPT, MAX_DIFF_LINES


DRY_RUN_MOCK = {
    "issues": [
        {
            "severity": "CRITICAL",
            "category": "security",
            "file": "user_controller.py",
            "line": 45,
            "message": "[DRY-RUN] SQL injection risk — user input used directly in query",
            "code_snippet": "cursor.execute(f\"SELECT * FROM users WHERE id={user_id}\")",
            "fix": "Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))"
        },
        {
            "severity": "HIGH",
            "category": "performance",
            "file": "order_service.py",
            "line": 78,
            "message": "[DRY-RUN] N+1 query pattern — DB query inside loop",
            "code_snippet": "for order in orders: items = db.query(Item).filter(order_id=order.id)",
            "fix": "Batch load with: items = db.query(Item).filter(Item.order_id.in_([o.id for o in orders]))"
        },
        {
            "severity": "MEDIUM",
            "category": "error_handling",
            "file": "utils.py",
            "line": 34,
            "message": "[DRY-RUN] Swallowed exception — caught but not logged",
            "code_snippet": "except Exception: pass",
            "fix": "Add logging: except Exception as e: logger.warning(f'Failed: {e}')"
        },
        {
            "severity": "LOW",
            "category": "code_quality",
            "file": "helpers.py",
            "line": 12,
            "message": "[DRY-RUN] Missing docstring on public function calculate_tax()",
            "code_snippet": "def calculate_tax(amount, rate):",
            "fix": "Add docstring explaining parameters and return value"
        }
    ]
}


def analyze(diff: str, dry_run: bool = False) -> list:
    if dry_run:
        return DRY_RUN_MOCK["issues"]

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. Add it to your .env file.", file=sys.stderr)
        print("       Run with --dry-run to test without an API key.", file=sys.stderr)
        sys.exit(1)

    diff_lines = diff.splitlines()
    if len(diff_lines) > MAX_DIFF_LINES:
        diff = "\n".join(diff_lines[:MAX_DIFF_LINES])
        diff += f"\n\n[Diff truncated at {MAX_DIFF_LINES} lines]"

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=REVIEW_MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"Review this git diff:\n\n{diff}"}
            ]
        )
        raw = response.content[0].text.strip()
        parsed = json.loads(raw)
        return parsed.get("issues", [])

    except json.JSONDecodeError as e:
        print(f"WARNING: Could not parse Claude response as JSON: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"ERROR: Claude API call failed: {e}", file=sys.stderr)
        sys.exit(1)
