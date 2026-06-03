# Implementation Changes: Line-by-Line What Updates

## 🎯 Quick Reference: New vs Updated vs Unchanged Files

```
📁 .claude/
├── config.template.json          [NEW] Team defaults template
├── config.local.template.json    [NEW] User overrides template
├── .envrc.template               [NEW] Optional env vars
├── settings.template.json        [UPDATED] Now references hook registry
├── hooks/
│   ├── lib/
│   │   ├── common.sh             [UPDATED] Read configs, smart fallback
│   │   └── config_loader.sh      [NEW] Config parsing utilities
│   ├── pre_tool/
│   │   ├── 01_alembic_preflight.sh     [UPDATED] Add config check
│   │   ├── 02_migration_guard.sh       [UPDATED] Add config check
│   │   ├── 03_branch_protection.sh     [UPDATED] Add config check
│   │   └── 04_precommit_quality.sh     [UPDATED] Add config check
│   └── post_tool/
│       ├── 05_py_autoformat.sh         [UPDATED] Add config + tool check
│       ├── 06_ts_eslint_fix.sh         [UPDATED] Add config + tool check
│       ├── 07_ts_typecheck.sh          [UPDATED] Add config + tool check
│       └── ... (all 13 hooks)          [UPDATED] Same pattern
│
├── commands/
│   └── dashboard.md              [UPDATED] Link to new /smart-setup

📁 scripts/
├── setup.sh                      [NEW] Interactive setup wizard
├── detect_project.py             [NEW] Auto-detect structure
├── detect_tools.py               [NEW] Check available tools
├── generate_config.py            [NEW] Create config files
├── onboarding.py                 [NEW] Role-based guides
├── generate_dashboard.py         [UPDATED] Use dynamic configs

📁 docs/
├── SETUP.md                      [NEW] Step-by-step user guide
├── DEVELOPER_GUIDE.md            [NEW] Backend dev onboarding
├── FRONTEND_GUIDE.md             [NEW] Frontend dev onboarding
├── DEVOPS_GUIDE.md               [NEW] DevOps/SRE guide
├── TEAM_ADMIN_GUIDE.md           [NEW] Team lead guide
└── TROUBLESHOOTING.md            [NEW] FAQ + common issues

📁 examples/
├── config.fullstack.json         [NEW] Fullstack project example
├── config.backend_only.json      [NEW] Backend-only example
├── config.monorepo.json          [NEW] Monorepo example
├── config.nextjs.json            [NEW] Next.js template
└── config.django_react.json      [NEW] Django + React template

📄 README.md                      [UPDATED] Link to SETUP.md
📄 INTEGRATION.md                 [UPDATED] Simplified (setup.sh does it)
```

---

## 📝 Detailed Changes Per File

### **1. NEW: `.claude/config.template.json`**

**Purpose:** Team-wide defaults (checked into git)

```json
{
  "schema_version": "1.0",
  "project_info": {
    "name": "my-project",
    "type": "fullstack",
    "description": "Your project description"
  },
  "detection": {
    "backend_folders": ["backend", "api", "server", "src/backend"],
    "frontend_folders": ["frontend", "web", "apps/web", "client"],
    "docs_folders": ["docs", "Documentation"],
    "venv_type": "venv",
    "node_manager": "npm"
  },
  "tools": {
    "python": {
      "version": "3.11+",
      "formatters": ["black", "ruff"],
      "linters": ["pylint", "flake8"],
      "type_checkers": ["mypy"]
    },
    "typescript": {
      "linters": ["eslint"],
      "formatters": ["prettier"],
      "type_checkers": ["tsc"]
    },
    "database": {
      "type": "alembic",
      "migrations_path": "alembic/versions"
    },
    "git": {
      "branch_protection": true,
      "require_pr": true
    }
  },
  "hooks": {
    "enabled_hooks": [
      "01_alembic_preflight",
      "03_branch_protection",
      "04_precommit_quality",
      "05_py_autoformat",
      "06_ts_eslint_fix",
      "07_ts_typecheck"
    ],
    "disabled_hooks": [
      "08_model_schema_drift",
      "09_migration_reminder",
      "10_intent_action_sync"
    ],
    "skip_on_wip": true
  },
  "dashboard": {
    "enabled": true,
    "docs_path": "Documentation/project_status",
    "include_metrics": ["features", "hooks", "team"]
  }
}
```

---

### **2. NEW: `.claude/config.local.template.json`**

**Purpose:** User personalization (.gitignore this!)

```json
{
  "user": {
    "name": "Alice",
    "email": "alice@example.com",
    "role": "backend"
  },
  "paths": {
    "project_root": "/Users/alice/projects/myapp",
    "backend_dir": "{{AUTO}}",
    "frontend_dir": "{{AUTO}}"
  },
  "tool_overrides": {
    "python.formatter": "black",
    "python.version_check": true,
    "typescript.typecheck_strict": false,
    "skip_hooks": ["09_migration_reminder"]
  },
  "env_vars": {
    "PYTHONPATH": "",
    "NODE_ENV": "development"
  },
  "performance": {
    "parallel_hooks": true,
    "hook_timeout_seconds": 30
  }
}
```

---

### **3. NEW: `.claude/lib/config_loader.sh`**

**Purpose:** Load and parse config with fallbacks

```bash
#!/usr/bin/env bash
# .claude/hooks/lib/config_loader.sh
# Loads dynamic configuration with smart fallbacks

# ── Configuration loading order ──────────────────────────────────
load_config() {
  local config_file="$1"
  
  if [ ! -f "$config_file" ]; then
    echo "{}"
    return 1
  fi
  
  cat "$config_file"
}

# ── JSON parsing (using Python since jq not available on Windows) ─
json_parse() {
  local json_string="$1"
  local key_path="$2"
  
  python3 -c "
import sys, json
try:
    data = json.loads('$json_string')
    for key in '$key_path'.split('.'):
        data = data.get(key, {})
    print(str(data).strip('\"'))
except:
    print('')
" 2>/dev/null
}

# ── Get config value with precedence ──────────────────────────────
get_config_value() {
  local key="$1"
  
  # Priority: env var > config.local.json > config.json > default
  
  # 1. Check environment variable
  local env_var="${key//./_}" # Convert path.to.key → path_to_key
  env_var=$(echo "$env_var" | tr '[:lower:]' '[:upper:]')
  if [ -n "${!env_var:-}" ]; then
    echo "${!env_var}"
    return 0
  fi
  
  # 2. Load from config.local.json
  if [ -f "$PROJECT_ROOT/.claude/config.local.json" ]; then
    local value=$(json_parse "$(cat "$PROJECT_ROOT/.claude/config.local.json")" "$key")
    if [ -n "$value" ] && [ "$value" != "{}" ]; then
      echo "$value"
      return 0
    fi
  fi
  
  # 3. Load from config.json
  if [ -f "$PROJECT_ROOT/.claude/config.json" ]; then
    local value=$(json_parse "$(cat "$PROJECT_ROOT/.claude/config.json")" "$key")
    if [ -n "$value" ] && [ "$value" != "{}" ]; then
      echo "$value"
      return 0
    fi
  fi
  
  # 4. Return empty (caller will use default)
  echo ""
  return 1
}

# ── Check if hook is enabled ────────────────────────────────────
is_hook_enabled() {
  local hook_id="$1"
  
  local cfg_file="$PROJECT_ROOT/.claude/config.json"
  [ ! -f "$cfg_file" ] && return 0  # Default: enabled if no config
  
  local enabled=$(json_parse "$(cat "$cfg_file")" "hooks.enabled_hooks")
  
  if echo "$enabled" | grep -q "$hook_id"; then
    return 0  # Enabled
  else
    return 1  # Disabled
  fi
}

# ── Check if tool is available ───────────────────────────────────
tool_exists() {
  local tool="$1"
  
  # Check in PATH
  command -v "$tool" >/dev/null 2>&1 && return 0
  
  # Check in venv
  if [ -f "$VENV_SCRIPTS/${tool}.exe" ]; then
    return 0
  fi
  if [ -f "$VENV_SCRIPTS/$tool" ]; then
    return 0
  fi
  
  # Check in node_modules
  if [ -x "$NODE_BIN/$tool" ]; then
    return 0
  fi
  
  return 1
}

# ── Detect backend folder ────────────────────────────────────────
detect_backend_dir() {
  # Try config first
  local configured=$(get_config_value "detection.backend_folders")
  if [ -n "$configured" ]; then
    # Take first folder in list
    echo "$configured" | head -n1
    return 0
  fi
  
  # Auto-detect common patterns
  for pattern in "backend" "api" "server" "src/backend" "services"; do
    if [ -d "$PROJECT_ROOT/$pattern" ]; then
      echo "$pattern"
      return 0
    fi
  done
  
  # Default
  echo "backend"
  return 1
}

# ── Detect frontend folder ───────────────────────────────────────
detect_frontend_dir() {
  local configured=$(get_config_value "detection.frontend_folders")
  if [ -n "$configured" ]; then
    echo "$configured" | head -n1
    return 0
  fi
  
  for pattern in "frontend" "web" "apps/web" "client" "src/frontend"; do
    if [ -d "$PROJECT_ROOT/$pattern" ]; then
      echo "$pattern"
      return 0
    fi
  done
  
  echo "frontend"
  return 1
}

# ── Get configured tool ───────────────────────────────────────
get_tool() {
  local tool_type="$1"  # e.g., "python.formatter"
  
  # Check user override first
  local override=$(get_config_value "tool_overrides.$tool_type")
  [ -n "$override" ] && echo "$override" && return 0
  
  # Check team default
  local default=$(get_config_value "tools.$tool_type")
  [ -n "$default" ] && echo "$default" && return 0
  
  # Hard default
  case "$tool_type" in
    "python.formatter") echo "black" ;;
    "typescript.linter") echo "eslint" ;;
    *) echo "" ;;
  esac
}
```

---

### **4. UPDATED: `.claude/hooks/lib/common.sh`**

**Changes:** Add config loading at top

```bash
#!/usr/bin/env bash
# .claude/hooks/lib/common.sh (PORTABLE VERSION)
# Source at the top of every hook: source "$(dirname "$0")/../lib/common.sh"

# ── Project paths ─────────────────────────────────────────────────
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

# ── NEW: Load configuration system ────────────────────────────────
source "$(dirname "$0")/config_loader.sh"

# ── Detect and set paths (with config fallback) ───────────────────
BACKEND_DIR="${BACKEND_DIR:-}"
FRONTEND_DIR="${FRONTEND_DIR:-}"

if [ -z "$BACKEND_DIR" ]; then
  BACKEND_DIR="$PROJECT_ROOT/$(detect_backend_dir)"
fi

if [ -z "$FRONTEND_DIR" ]; then
  FRONTEND_DIR="$PROJECT_ROOT/$(detect_frontend_dir)"
fi

# ── Windows venv handling ────────────────────────────────────────
if [ -d "$BACKEND_DIR/.venv/Scripts" ]; then
  VENV_SCRIPTS="$BACKEND_DIR/.venv/Scripts"
else
  VENV_SCRIPTS="$BACKEND_DIR/.venv/bin"
fi

NODE_BIN="$FRONTEND_DIR/node_modules/.bin"

# ── Rest of common.sh (unchanged) ────────────────────────────────
HOOK_INPUT="$(cat)"
_py_exe() { ... }
json_get() { ... }
hook_info() { ... }
# ... (rest stays the same)
```

---

### **5. UPDATED: `.claude/hooks/post_tool/05_py_autoformat.sh`**

**Before:**
```bash
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"

FILE_PATH="$(json_input_get path)"
[[ -z "$FILE_PATH" ]] && FILE_PATH="$(json_input_get file_path)"
FILE_PATH_NORM="$(normalize_path "$FILE_PATH")"

echo "$FILE_PATH_NORM" | grep -qE '\.py$' || exit 0
echo "$FILE_PATH_NORM" | grep -q 'backend/' || exit 0
echo "$FILE_PATH_NORM" | grep -qE '(\.venv|__pycache__|alembic/versions)/' && exit 0

BLACK_BIN="$VENV_SCRIPTS/black.exe"
ISORT_BIN="$VENV_SCRIPTS/isort.exe"

if [ ! -f "$BLACK_BIN" ]; then
  hook_warn "black not installed"
  exit 0
fi

"$BLACK_BIN" --target-version py311 "$NATIVE_PATH" 2>&1
```

**After:**
```bash
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"

# ── NEW: Check if hook is enabled ────────────────────────────────
is_hook_enabled "05_py_autoformat" || exit 0

FILE_PATH="$(json_input_get path)"
[[ -z "$FILE_PATH" ]] && FILE_PATH="$(json_input_get file_path)"
FILE_PATH_NORM="$(normalize_path "$FILE_PATH")"

# ── Only .py files inside backend/ ────────────────────────────────
echo "$FILE_PATH_NORM" | grep -qE '\.py$' || exit 0
echo "$FILE_PATH_NORM" | grep -q "$BACKEND_DIR" || exit 0
echo "$FILE_PATH_NORM" | grep -qE '(\.venv|__pycache__|alembic/versions)/' && exit 0

# ── NEW: Use configured tool instead of hardcoding ─────────────────
FORMATTER=$(get_tool "python.formatter")
if [ -z "$FORMATTER" ]; then
  hook_warn "No Python formatter configured"
  exit 0
fi

case "$FORMATTER" in
  "black")
    if ! tool_exists "black"; then
      hook_warn "Black not installed — run: cd $BACKEND_DIR && uv add --dev black"
      exit 0
    fi
    hook_info "Auto-formatting with Black: $FILE_PATH_NORM"
    black --target-version py311 "$FILE_PATH_NORM" 2>&1 || true
    ;;
  "ruff")
    if ! tool_exists "ruff"; then
      hook_warn "Ruff not installed — run: cd $BACKEND_DIR && pip install ruff"
      exit 0
    fi
    hook_info "Auto-formatting with Ruff: $FILE_PATH_NORM"
    ruff format "$FILE_PATH_NORM" 2>&1 || true
    ;;
esac

# ── Run isort if available ────────────────────────────────────────
if tool_exists "isort"; then
  isort "$FILE_PATH_NORM" 2>&1 || true
fi

exit 0
```

---

### **6. UPDATED: `.claude/hooks/post_tool/06_ts_eslint_fix.sh`**

**Before:**
```bash
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"

FILE_PATH="$(json_input_get path)"
[[ -z "$FILE_PATH" ]] && FILE_PATH="$(json_input_get file_path)"
FILE_PATH_NORM="$(normalize_path "$FILE_PATH")"

echo "$FILE_PATH_NORM" | grep -qE '\.(ts|tsx)$' || exit 0
echo "$FILE_PATH_NORM" | grep -q 'frontend/' || exit 0
echo "$FILE_PATH_NORM" | grep -qE '(node_modules|dist)/' && exit 0

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  hook_warn "frontend/node_modules not found"
  exit 0
fi

NATIVE_PATH="$(to_native_path "$FILE_PATH_NORM")"
hook_info "ESLint --fix: $NATIVE_PATH"

cd "$FRONTEND_DIR"
npx --no-install eslint --fix "$NATIVE_PATH" 2>&1 || true

exit 0
```

**After:**
```bash
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"

# ── NEW: Check if hook is enabled ────────────────────────────────
is_hook_enabled "06_ts_eslint_fix" || exit 0

FILE_PATH="$(json_input_get path)"
[[ -z "$FILE_PATH" ]] && FILE_PATH="$(json_input_get file_path)"
FILE_PATH_NORM="$(normalize_path "$FILE_PATH")"

# ── Only .ts/.tsx files inside frontend/ ─────────────────────────
echo "$FILE_PATH_NORM" | grep -qE '\.(ts|tsx)$' || exit 0
echo "$FILE_PATH_NORM" | grep -q "$FRONTEND_DIR" || exit 0
echo "$FILE_PATH_NORM" | grep -qE '(node_modules|dist)/' && exit 0

# ── NEW: Check frontend directory exists ─────────────────────────
if [ ! -d "$FRONTEND_DIR" ]; then
  hook_warn "Frontend directory not found at $FRONTEND_DIR — skipping ESLint"
  exit 0
fi

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  hook_info "Dependencies not installed — run: cd $FRONTEND_DIR && npm install"
  exit 0
fi

# ── Check if ESLint is available ─────────────────────────────────
if ! tool_exists "eslint"; then
  hook_warn "ESLint not found in $FRONTEND_DIR/node_modules"
  exit 0
fi

NATIVE_PATH="$(to_native_path "$FILE_PATH_NORM")"
hook_info "ESLint --fix: $NATIVE_PATH"

cd "$FRONTEND_DIR"
npx --no-install eslint --fix "$NATIVE_PATH" 2>&1 || true

exit 0
```

---

### **7. NEW: `setup.sh` (Main Entry Point)**

**Location:** Root of kit

```bash
#!/usr/bin/env bash
# setup.sh — Interactive setup for Claude Config Kit
# Makes the kit work for ANY project in 2 minutes

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
  echo -e "${BLUE}╭─────────────────────────────────────────────────╮${NC}"
  echo -e "${BLUE}│  🚀 Claude Config Kit Setup Wizard             │${NC}"
  echo -e "${BLUE}╰─────────────────────────────────────────────────╯${NC}"
  echo ""
}

print_success() {
  echo -e "${GREEN}✓${NC} $1"
}

print_error() {
  echo -e "${RED}✗${NC} $1"
}

# Step 1: Detect project structure
print_header
echo "Step 1: Detecting project structure..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

python3 "$SCRIPT_DIR/scripts/detect_project.py" > /tmp/project_detected.json
PROJECT_TYPE=$(jq -r '.project_type' /tmp/project_detected.json)
BACKEND_DIR=$(jq -r '.backend_dir' /tmp/project_detected.json)
FRONTEND_DIR=$(jq -r '.frontend_dir' /tmp/project_detected.json)

print_success "Detected: $PROJECT_TYPE"
echo "  Backend:  $BACKEND_DIR"
echo "  Frontend: $FRONTEND_DIR"

# Step 2: Detect tools
echo ""
echo "Step 2: Checking available tools..."

python3 "$SCRIPT_DIR/scripts/detect_tools.py" > /tmp/tools_detected.json
HAS_PYTHON=$(jq -r '.python_tools | length' /tmp/tools_detected.json)
HAS_JS=$(jq -r '.js_tools | length' /tmp/tools_detected.json)

print_success "Found $(jq -r '.python_tools | keys[]' /tmp/tools_detected.json | wc -l) Python tools"
print_success "Found $(jq -r '.js_tools | keys[]' /tmp/tools_detected.json | wc -l) Node tools"

# Step 3: Interactive selection
echo ""
echo "Step 3: Confirm or customize..."
read -p "  Project type correct? [$PROJECT_TYPE] " -r
PROJECT_TYPE="${REPLY:-$PROJECT_TYPE}"

# Step 4: Generate configs
echo ""
echo "Step 4: Generating configurations..."

python3 "$SCRIPT_DIR/scripts/generate_config.py" \
  --project-type "$PROJECT_TYPE" \
  --backend "$BACKEND_DIR" \
  --frontend "$FRONTEND_DIR" \
  --tools-file /tmp/tools_detected.json

print_success "Created .claude/config.json (team defaults)"
print_success "Created .claude/config.local.json (user preferences)"
print_success "Created .claude/settings.local.json (hooks wired)"

# Step 5: Make hooks executable
echo ""
echo "Step 5: Finalizing setup..."

chmod +x "$SCRIPT_DIR"/.claude/hooks/lib/*.sh 2>/dev/null || true
chmod +x "$SCRIPT_DIR"/.claude/hooks/pre_tool/*.sh 2>/dev/null || true
chmod +x "$SCRIPT_DIR"/.claude/hooks/post_tool/*.sh 2>/dev/null || true

print_success "Hooks made executable"

# Step 6: Summary
echo ""
echo -e "${GREEN}╭─────────────────────────────────────────────────╮${NC}"
echo -e "${GREEN}│  ✅ Setup Complete!                            │${NC}"
echo -e "${GREEN}├─────────────────────────────────────────────────┤${NC}"
echo -e "${GREEN}│  Next Steps:                                    │${NC}"
echo -e "${GREEN}│  1. Open Claude Code: claude code .             │${NC}"
echo -e "${GREEN}│  2. Edit Python/TypeScript to test hooks        │${NC}"
echo -e "${GREEN}│  3. Read: docs/SETUP.md or docs/[ROLE]_GUIDE.md│${NC}"
echo -e "${GREEN}╰─────────────────────────────────────────────────╯${NC}"
```

---

### **8. NEW: `scripts/detect_project.py`**

```python
#!/usr/bin/env python3
"""Auto-detect project structure from filesystem"""

import json
from pathlib import Path

def detect():
    """Return project detection results"""
    cwd = Path.cwd()
    
    # Detect backend
    backend_patterns = ['backend', 'api', 'server', 'src/backend']
    backend = next(
        (p for p in backend_patterns if (cwd / p).is_dir()),
        'backend'
    )
    
    # Detect frontend  
    frontend_patterns = ['frontend', 'web', 'apps/web', 'client']
    frontend = next(
        (p for p in frontend_patterns if (cwd / p).is_dir()),
        'frontend'
    )
    
    # Determine project type
    has_backend = (cwd / backend).is_dir()
    has_frontend = (cwd / frontend).is_dir()
    
    if has_backend and has_frontend:
        project_type = "fullstack"
    elif has_backend:
        project_type = "backend_only"
    elif has_frontend:
        project_type = "frontend_only"
    else:
        project_type = "unknown"
    
    return {
        "project_type": project_type,
        "backend_dir": str(backend),
        "frontend_dir": str(frontend),
        "has_backend": has_backend,
        "has_frontend": has_frontend
    }

if __name__ == "__main__":
    print(json.dumps(detect(), indent=2))
```

---

### **9. UPDATED: `scripts/generate_dashboard.py`**

**Add at top:**
```python
import json

def load_config():
    """Load team config"""
    cfg = Path(".claude") / "config.json"
    if cfg.exists():
        return json.loads(cfg.read_text())
    return {}

def get_enabled_hooks(config):
    """Only show enabled hooks"""
    enabled = config.get("hooks", {}).get("enabled_hooks", [])
    return [h for h in all_hooks if h.id in enabled]

# In HTML generation:
config = load_config()
enabled_hooks = get_enabled_hooks(config)
# Only iterate over enabled_hooks instead of all_hooks
```

---

### **10. UPDATED: `README.md`**

**Before:**
```markdown
## Quick Start

1. Clone this kit into your project...
2. Copy to your project's `.claude/` folder...
3. Update `.claude/settings.local.json`...
```

**After:**
```markdown
## Quick Start (2 Minutes)

1. Clone the kit:
   ```bash
   git clone https://github.com/your-org/claude-config-kit .claude-kit
   ```

2. Run setup:
   ```bash
   cd .claude-kit && bash setup.sh
   ```

3. Done! Hooks auto-work in Claude Code:
   ```bash
   cd .. && claude code .
   ```

**For detailed docs:** See [SETUP.md](docs/SETUP.md) or role-specific guides.
```

---

## 📊 Summary of Changes

| File | Type | Key Changes |
|------|------|------------|
| `config.template.json` | NEW | Team-wide defaults (checked in) |
| `config.local.template.json` | NEW | User personalization template |
| `.envrc.template` | NEW | Optional env var setup |
| `lib/common.sh` | UPDATED | Load config + smart fallback |
| `lib/config_loader.sh` | NEW | Config parsing + tool detection |
| `pre_tool/*.sh` (4 files) | UPDATED | Check `is_hook_enabled()` first |
| `post_tool/*.sh` (9 files) | UPDATED | Use dynamic config + tool checks |
| `setup.sh` | NEW | Interactive wizard (main entry) |
| `detect_project.py` | NEW | Auto-detect folder structure |
| `detect_tools.py` | NEW | Check available tools |
| `generate_config.py` | NEW | Create config files |
| `onboarding.py` | NEW | Generate role-based guides |
| `generate_dashboard.py` | UPDATED | Use dynamic config |
| `README.md` | UPDATED | Link to SETUP.md |

---

## ⚡ Testing Each Change

```bash
# Test 1: Config loading
$ bash -x .claude/hooks/lib/config_loader.sh
# Should output current config values without errors

# Test 2: Project detection
$ python3 scripts/detect_project.py
# Should output valid JSON with correct paths

# Test 3: Tool detection
$ python3 scripts/detect_tools.py
# Should find installed tools

# Test 4: Setup wizard
$ bash setup.sh
# Should guide user through setup (non-interactive mode for testing)
$ bash setup.sh --non-interactive
# Should auto-detect and configure

# Test 5: Hook execution
$ echo '{"tool_input":{"path":"src/test.py"}}' | bash .claude/hooks/post_tool/05_py_autoformat.sh
# Should check config and skip/run appropriately
```

---

## 🎯 Verification Checklist

After implementation:

- [ ] `setup.sh` runs without errors
- [ ] Auto-detects at least 5 different project structures
- [ ] Generates valid `config.json` and `config.local.json`
- [ ] All 14 hooks read and use config values
- [ ] Hooks gracefully skip if disabled in config
- [ ] Hooks warn (not fail) if tools missing
- [ ] Dashboard only shows enabled hooks
- [ ] Role-based guides auto-generate
- [ ] Works on Windows, macOS, Linux
- [ ] `.gitignore` includes config.local.json

