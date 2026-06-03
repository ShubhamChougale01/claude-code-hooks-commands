# claude-code-hooks-commands

A unified toolkit of Claude Code hooks and Git hooks for automated code quality enforcement — featuring pre/post tool hooks for formatting, schema sync, and branch protection, plus an AI-powered pre-push reviewer that uses the Claude API to catch critical issues before they reach your repository.

## What's Inside

### `.claude/hooks/` — Claude Code Hooks
Hooks that run automatically during Claude Code tool execution.

**Pre-tool (preventive checks before changes):**
- `01_alembic_preflight.sh` — Backup DB before alembic migrations
- `02_migration_guard.sh` — Prevent direct edits to migration files
- `03_branch_protection.sh` — Block direct pushes to main/master
- `04_precommit_quality.sh` — TypeScript + ESLint + Black quality gate

**Post-tool (auto-fixes after changes):**
- `05_py_autoformat.sh` — Auto-format `.py` files with Black + isort
- `06_ts_eslint_fix.sh` — Auto-fix `.ts/.tsx` with ESLint
- `07_ts_typecheck.sh` — Type-check TypeScript with tsc
- `08_model_schema_drift.sh` — Detect model ↔ schema sync issues
- `09_migration_reminder.sh` — Remind to generate migration after model edits
- `10_intent_action_sync.sh` — Sync intent/action services
- `11_env_drift.sh` — Compare `.env` vs `.env.example`
- `12_dep_sync_reminder.sh` — Remind about pip/npm install after dependency edits
- `13_api_sync.sh` — Check backend routes ↔ frontend API clients

### `.claude/commands/`
- `dashboard.md` — Interactive project status dashboard command (`/dashboard`)

### `git-hooks/` — AI-Powered Git Review Hooks
Git-level hooks (pre-push / post-receive) that use the Claude API to analyze diffs and block pushes containing critical or high-severity issues.

- Detects CRITICAL / HIGH / MEDIUM / LOW severity issues in diffs
- Blocks pushes on CRITICAL/HIGH (configurable)
- Works as `pre-push` (local) or `post-receive` (server/self-hosted Git)
- Cross-platform: Windows, macOS, Linux

See [`git-hooks/README.md`](git-hooks/README.md) for setup.

### `scripts/`
- `generate_dashboard.py` — HTML dashboard generator

### `docs/`
Extended documentation covering architecture, implementation guide, multi-user setup, and integration steps.

## Setup

### Claude Code Hooks
Copy `.claude/` into your project root. Claude Code will auto-discover and run the hooks.

```bash
cp -r .claude/ /your/project/.claude/
```

### Git AI Review Hook
```bash
cd git-hooks
cp .env.example .env      # add your ANTHROPIC_API_KEY
# Linux/macOS
bash scripts/install_local.sh
# Windows
powershell scripts/install_local.ps1
```

## Flow

```
Developer edits file
      ↓
Claude Code post-tool hooks run (auto-format, sync checks)
      ↓
Developer commits
      ↓
pre-commit quality gate runs
      ↓
Developer pushes
      ↓
git-hooks AI review runs (Claude API diff analysis)
      ↓
Push succeeds only if no CRITICAL/HIGH issues found
```
