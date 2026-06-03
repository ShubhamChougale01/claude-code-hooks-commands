# Integration Guide: Claude Config Kit

Step-by-step instructions to integrate this config kit into your project.

---

## Prerequisites

- **Git repository** (required for portable root detection)
- **Claude Code** installed (or Cursor IDE)
- **Project structure:**
  ```
  your-project/
  ├── backend/           (Python + Alembic + SQLAlchemy)
  ├── frontend/          (Node.js + TypeScript/React)
  └── Documentation/     (or where your docs live)
  ```

---

## Step 1: Clone/Copy This Kit

**Option A: Clone as a submodule** (recommended for team projects)
```bash
cd your-project
git submodule add https://github.com/your-org/claude-config-kit.git .claude-kit
```

**Option B: Copy files directly**
```bash
cp -r claude-config-kit/.claude your-project/
cp -r claude-config-kit/.cursor your-project/
cp -r claude-config-kit/scripts your-project/
```

---

## Step 2: Make Hooks Executable

```bash
cd your-project
chmod +x .claude/hooks/lib/*.sh
chmod +x .claude/hooks/pre_tool/*.sh
chmod +x .claude/hooks/post_tool/*.sh
chmod +x .claude/hooks/stop/*.sh
```

---

## Step 3: Create `.claude/settings.local.json`

This file wires up hooks and permissions for **YOUR** project structure.

### Template (Copy and customize):

```json
{
  "permissions": {
    "allow": [
      "Bash(chmod +x .claude/hooks/lib/common.sh .claude/hooks/pre_tool/*.sh .claude/hooks/post_tool/*.sh)",
      "Bash(npx tsc *)",
      "Bash(uv run *)",
      "Bash(python \"scripts/generate_dashboard.py\")"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash \".claude/hooks/pre_tool/01_alembic_preflight.sh\""
          },
          {
            "type": "command",
            "command": "bash \".claude/hooks/pre_tool/03_branch_protection.sh\""
          },
          {
            "type": "command",
            "command": "bash \".claude/hooks/pre_tool/04_precommit_quality.sh\""
          }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash \".claude/hooks/pre_tool/02_migration_guard.sh\""
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash \".claude/hooks/post_tool/05_py_autoformat.sh\""
          },
          {
            "type": "command",
            "command": "bash \".claude/hooks/post_tool/06_ts_eslint_fix.sh\""
          },
          {
            "type": "command",
            "command": "bash \".claude/hooks/post_tool/07_ts_typecheck.sh\""
          },
          {
            "type": "command",
            "command": "bash \".claude/hooks/post_tool/08_model_schema_drift.sh\""
          },
          {
            "type": "command",
            "command": "bash \".claude/hooks/post_tool/09_migration_reminder.sh\""
          },
          {
            "type": "command",
            "command": "bash \".claude/hooks/post_tool/10_intent_action_sync.sh\""
          },
          {
            "type": "command",
            "command": "bash \".claude/hooks/post_tool/11_env_drift.sh\""
          },
          {
            "type": "command",
            "command": "bash \".claude/hooks/post_tool/12_dep_sync_reminder.sh\""
          },
          {
            "type": "command",
            "command": "bash \".claude/hooks/post_tool/13_api_sync.sh\""
          }
        ]
      }
    ]
  }
}
```

### What Each Section Does:

**`permissions.allow`** — Commands that Claude Code can run automatically (no prompt):
- `chmod` — Make hooks executable
- `npx tsc *` — TypeScript type-checking
- `uv run *` — Python commands via UV
- `python scripts/generate_dashboard.py` — Dashboard generation

**`hooks.PreToolUse`** — Run **before** a tool executes:
- On any `Bash` command: run pre-flight checks (alembic, branch protection, quality gates)
- On any `Edit|Write`: guard against editing migration files

**`hooks.PostToolUse`** — Run **after** a tool executes:
- On any `Edit|Write`: auto-format, type-check, drift detection

---

## Step 4: Install Dependencies

### Backend:

```bash
cd your-project/backend

# Install dev tools for autoformatting
uv add --dev black isort

# Verify Alembic is installed
uv list | grep alembic
```

### Frontend:

```bash
cd your-project/frontend

# Install dependencies (includes ESLint, TypeScript, etc.)
npm install
```

---

## Step 5: Test It Out

Open your project in Claude Code. Try:

1. **Edit a Python file in `backend/app/`**
   - You should see `[HOOK INFO] Auto-formatting...` in the terminal
   - File is auto-formatted with Black + isort

2. **Try `git push` to main**
   - Hook blocks it with `[HOOK BLOCK] Direct push to main/master is blocked`

3. **Edit a model file in `backend/app/models/`**
   - Hook warns if no migration was generated: `[HOOK WARN] Model '...' was edited but no new migration detected`

4. **Generate a dashboard** (if you have Documentation files):
   ```bash
   python backend/scripts/generate_dashboard.py
   ```
   - Opens an interactive HTML dashboard showing project health

---

## Step 6 (Optional): Customize Hook Behavior

### Disable a hook?

Comment out its entry in `.claude/settings.local.json`:

```json
// "command": "bash \".claude/hooks/post_tool/06_ts_eslint_fix.sh\""  // Disabled
```

### Change hook logic?

Edit the `.sh` file directly — hooks are just bash scripts.

Example: `08_model_schema_drift.sh` has a hardcoded model name mapping. To add/remove models:

```bash
declare -A MODEL_TO_SCHEMA
MODEL_TO_SCHEMA["your_model"]="your_schema"   # Add this
# MODEL_TO_SCHEMA["old_model"]="old_schema"  # Remove this
```

### Override project paths?

Set environment variables in your shell or `.env`:

```bash
export BACKEND_DIR=/path/to/custom/backend
export FRONTEND_DIR=/path/to/custom/frontend
export INTENT_PARSER_FILE=custom/path/to/intent_parser.py
export ACTION_EXECUTOR_FILE=custom/path/to/action_executor.py
```

---

## Troubleshooting

### "Hooks aren't running"

**Check 1:** Are they executable?
```bash
ls -la .claude/hooks/pre_tool/
# Should show: -rwxr-xr-x (x = executable)
```

**Check 2:** Is `settings.local.json` wired correctly?
- Open it and verify all hook command paths match your `bash` commands
- Make sure all paths are quoted properly

**Check 3:** Are you in a git repository?
```bash
git rev-parse --show-toplevel
# Should return your project root
```

### "black not installed"

```bash
cd backend && uv add --dev black isort
```

### "frontend/node_modules not found"

```bash
cd frontend && npm install
```

### Hook says "Project root not found"

The script uses `git rev-parse --show-toplevel` to find your project root. If this fails:

1. Make sure you're in a git repository: `git status`
2. Or set `BACKEND_DIR` and `FRONTEND_DIR` env vars explicitly

### ESLint failing on `[HOOK] Pre-commit quality gate FAILED`

Fix with:
```bash
cd frontend && npx eslint src --fix
```

### TypeScript errors in type-check hook

Fix with:
```bash
cd frontend && npx tsc --noEmit
# Review errors and update code
```

---

## Next Steps

- **Dashboard:** Run `python backend/scripts/generate_dashboard.py` to visualize project status
- **Skills:** Use `/db-migration-resolver` (Claude Code) to auto-fix migration conflicts
- **Frontend Design:** Use Claude Code in Cursor IDE for AI-guided UI design

---

## Questions?

Consult individual hook files (`.claude/hooks/**/*.sh`) — they're heavily commented. Or open an issue in the kit repository.
