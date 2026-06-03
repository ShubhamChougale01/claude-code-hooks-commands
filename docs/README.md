# Claude Config Kit

A reusable, production-grade configuration package for Claude Code projects. Provides 14 quality hooks, custom skills, commands, and dashboard automation out of the box.

## What's Inside

**14 Automated Hooks:**
- Pre-tool: Alembic preflight backup, migration guards, branch protection, quality gates
- Post-tool: Python auto-formatting, TypeScript type-checking, model↔schema drift detection, intent↔action sync, env variable tracking, dependency reminders

**Custom Skills:**
- `db-migration-resolver` — Auto-detect and resolve Alembic/Django migration conflicts
- `frontend-design` (Cursor) — Production-grade UI design guidance

**Commands:**
- `/dashboard` — Generate interactive project status dashboard with live metrics

**Cross-Platform:**
- Works on Windows, macOS, and Linux
- Portable: uses git to detect project root (no hardcoded paths)
- Configurable: environment variables override defaults

---

## Quick Start

1. **Clone this kit** into your project:
   ```bash
   git clone https://github.com/your-org/claude-config-kit.git .claude-config
   ```

2. **Copy to your project's `.claude/` folder:**
   ```bash
   cp -r .claude-config/.claude/* your-project/.claude/
   cp -r .claude-config/.cursor/* your-project/.cursor/
   ```

3. **Update your `.claude/settings.local.json`** — see `INTEGRATION.md` for step-by-step instructions

4. **Make hooks executable:**
   ```bash
   chmod +x .claude/hooks/**/*.sh
   ```

That's it! Hooks will auto-activate when you work in Claude Code.

---

## Hook Reference

| # | Hook | Category | Triggers On |
|---|------|----------|-------------|
| 01 | `alembic_preflight.sh` | Backend | `alembic upgrade/downgrade` bash commands |
| 02 | `migration_guard.sh` | Backend | Attempts to edit `alembic/versions/*.py` files |
| 03 | `branch_protection.sh` | Shared | `git push` to main/master |
| 04 | `precommit_quality.sh` | Shared | `git commit` — TypeScript + ESLint + Black checks |
| 05 | `py_autoformat.sh` | Backend | Edit any `.py` file → Black + isort format |
| 06 | `ts_eslint_fix.sh` | Frontend | Edit any `.ts`/`.tsx` file → ESLint --fix |
| 07 | `ts_typecheck.sh` | Frontend | Edit files in `frontend/src/` → tsc --noEmit |
| 08 | `model_schema_drift.sh` | Backend | Edit model files → checks schema sync |
| 09 | `migration_reminder.sh` | Backend | Edit model files → reminds to generate migrations |
| 10 | `intent_action_sync.sh` | Backend (app-specific) | Edit intent/action service → sync checks |
| 11 | `env_drift.sh` | Backend | Edit `.env.example` → compares with `.env` |
| 12 | `dep_sync_reminder.sh` | Shared | Edit `pyproject.toml` / `package.json` |
| 13 | `api_sync.sh` | Shared | Edit backend route files → check frontend API clients |

---

## Configuration

### Default Directories

The kit assumes standard project layout:
```
your-project/
├── backend/
│   ├── .venv/
│   ├── app/
│   └── pyproject.toml
├── frontend/
│   ├── node_modules/
│   └── package.json
└── .claude/
    └── hooks/
```

### Custom Directories?

Set environment variables before running:

```bash
# Override backend directory
export BACKEND_DIR=/path/to/custom/backend

# Override frontend directory
export FRONTEND_DIR=/path/to/custom/frontend

# Override intent/action parser locations (for hook 10)
export INTENT_PARSER_FILE=services/intent_parser.py
export ACTION_EXECUTOR_FILE=services/action_executor.py
```

---

## Skills

### db-migration-resolver

Detects and automatically fixes Alembic/Django migration conflicts.

**When to use:**
- Your branch has conflicting migrations
- You're merging a PR with schema changes
- Migration files are out of sync

**How to use:**
```
/db-migration-resolver
```

### frontend-design (Cursor)

Guides creation of production-grade, distinctive UI components.

**Loaded automatically in Cursor IDE** — available when editing React/HTML/CSS.

---

## Dashboard

Generate an interactive HTML dashboard showing:
- Feature completion status
- Frontend/backend component health
- Active hooks and skills
- Roadmap and priorities

**Generate:**
```bash
cd backend && python scripts/generate_dashboard.py
```

Or via Claude Code:
```
/dashboard
```

**Output:** `dashboard/proj_dashboard_<TIMESTAMP>.html` — timestamped for history tracking

---

## Troubleshooting

**Hooks not running?**
- Ensure `.claude/settings.local.json` is wired with absolute paths (see `INTEGRATION.md`)
- Run `chmod +x .claude/hooks/**/*.sh` to make them executable
- Check hook output in Claude Code terminal (look for `[HOOK ...]` messages)

**"Project root not found"?**
- Your directory structure doesn't match the defaults, OR
- Not in a git repository (git is required for portable root detection)
- **Fix:** Set `BACKEND_DIR` and `FRONTEND_DIR` env vars explicitly

**"black not installed" warning?**
- Install via: `cd backend && uv add --dev black isort`

**"frontend/node_modules not found"?**
- Install via: `cd frontend && npm install`

---

## License

MIT. Use freely in your projects.

---

## Questions?

See `INTEGRATION.md` for step-by-step setup, or check individual hook files for logic.
