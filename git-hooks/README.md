# Git Code Review Hooks

Automated code review using Claude AI. Analyzes git diffs on every `git push` and blocks pushes with **CRITICAL** or **HIGH** severity issues.

---

## Severity Levels

| Level | Action | Examples |
|-------|--------|---------|
| [CRITICAL] | Blocks push | SQL injection, hardcoded secrets, DROP without WHERE, auth bypass |
| [HIGH] | Blocks push | N+1 queries, logic bugs, missing error handling in critical paths |
| [MEDIUM] | Warning only | Swallowed exceptions, resource leaks, complex functions |
| [LOW] | Info only | Missing docstrings, unused imports, style issues |

---

## Prerequisites

- Python 3.9+
- pip
- Git 2.x+

---

## Setup

### Step 1 — Get Claude API Key
1. Go to https://console.anthropic.com
2. Sign up → **API Keys** → **Create Key**
3. Copy the key

> No credits yet? You can still run and test everything using `--dry-run` mode (see below).

### Step 2 — Install Dependencies

**Windows:**
```powershell
pip install -r requirements.txt
```

**Linux / macOS:**
```bash
pip install -r requirements.txt
```

### Step 3 — Configure API Key

**Windows:**
```powershell
Copy-Item .env.example .env
# Edit .env and set: ANTHROPIC_API_KEY=sk-ant-your_key_here
```

**Linux / macOS:**
```bash
cp .env.example .env
# Edit .env and set: ANTHROPIC_API_KEY=sk-ant-your_key_here
```

---

## Local Hook Setup (Pre-Push)

Run from **your project repo root** (the repo you want to protect, not this one):

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File C:\path\to\code-review-hooks\scripts\install_local.ps1
```

**Linux / macOS:**
```bash
bash /path/to/code-review-hooks/scripts/install_local.sh
```

This copies the `pre-push` hook into your repo's `.git/hooks/`. From now on, every `git push` triggers an automatic code review.

> **Windows note:** The hook uses `python` (not `python3`). Make sure `python` is available in your PATH.

---

## Server Hook Setup (Post-Receive)

For **self-hosted Git** (Gitea, GitLab self-managed, GitHub Enterprise):

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_server.ps1 -RepoDir C:\path\to\repo.git -ProjectDir C:\path\to\code-review-hooks
```

**Linux / macOS:**
```bash
bash scripts/install_server.sh /path/to/repo.git /path/to/code-review-hooks
```

> **GitHub.com / GitLab.com (SaaS):** post-receive hooks are not supported.
> Use the GitHub Actions workflow below as the server-side enforcement layer instead.

### GitHub Actions Alternative
```yaml
# .github/workflows/code-review.yml
name: Code Review
on: [push, pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 2
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: git diff HEAD~1..HEAD | python src/run_review.py --hook=post-receive
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

---

## Testing Without API Key

Use `--dry-run` to simulate a full review with mock issues — no API key or credits needed:

**Windows:**
```powershell
python src\run_review.py --dry-run
```

**Linux / macOS:**
```bash
python src/run_review.py --dry-run
```

Expected output:
```
====================================================================
                     CODE REVIEW ANALYSIS
====================================================================

Summary: 4 issue(s) found
   [CRITICAL]: 1
   [HIGH]: 1
   [MEDIUM]: 1
   [LOW]: 1

[CRITICAL] ISSUES (BLOCKING):
[1] user_controller.py:45  [security]
    SQL injection risk - user input used directly in query
    ...

PUSH BLOCKED: Fix CRITICAL/HIGH issues before pushing.
```

Run unit tests (also no API key needed):
```powershell
python -m pytest tests/ -v
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | — | Required for real reviews (get from console.anthropic.com) |
| `REVIEW_MODEL` | `claude-haiku-4-5-20251001` | Claude model used for analysis |
| `BLOCK_ON_HIGH` | `true` | Block push on HIGH severity issues |
| `MAX_DIFF_LINES` | `500` | Truncate diffs larger than this line count |

---

## How It Works

```
git push
   └── pre-push hook triggers
         └── run_review.py
               ├── gets diff (git diff origin/HEAD..HEAD)
               ├── sends diff to Claude API
               ├── Claude returns JSON list of issues with severity
               ├── groups into CRITICAL / HIGH / MEDIUM / LOW
               ├── prints colored report to terminal
               └── exits 1 (block) if CRITICAL or HIGH found
                   exits 0 (allow) if only MEDIUM / LOW
```

---

## Emergency Bypass (Use Carefully)

If you need to push despite a hook block (e.g., production hotfix):
```bash
git push --no-verify
```
> This bypasses ALL hooks. Use only in genuine emergencies and document the reason in your commit message.
