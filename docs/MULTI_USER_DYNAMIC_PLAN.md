# Multi-User Dynamic Configuration Plan
**Making the Claude Config Kit work seamlessly for any user, any project, any tech stack**

---

## 🎯 Vision
A new user clones the kit → runs **one setup command** → hooks auto-adapt to their project → gets custom guidance. No manual config editing, no hardcoded paths, no friction.

---

## 📊 Current Pain Points → Solutions

| Problem | Today | After Changes |
|---------|-------|---|
| New user must edit `.claude/settings.local.json` manually | ❌ Manual | ✅ Auto-generated |
| Hooks fail silently if project structure differs | ❌ Breaks | ✅ Auto-detect + adapt |
| All 14 hooks run even if not applicable | ❌ Noise | ✅ Only run relevant ones |
| No guidance on what tools to install | ❌ Trial/error | ✅ Auto-check + recommendations |
| Works only if `backend/`, `frontend/` folders exist | ❌ Rigid | ✅ Dynamic detection |
| Dashboard assumes Documentation folder | ❌ Breaks | ✅ Smart path detection |

---

## 🚀 User Onboarding Flow (What Users Will Do)

### **Step 1: Get the Kit** (5 seconds)
```bash
# Option A: Clone into their project
git clone https://github.com/your-org/claude-config-kit.git .claude-kit
cd .claude-kit && bash setup.sh

# Option B: Add as submodule
git submodule add https://github.com/your-org/claude-config-kit.git .claude-kit
cd .claude-kit && bash setup.sh

# Option C: Download as template
# Download ZIP → unzip → bash setup.sh
```

### **Step 2: Run Interactive Setup** (2 minutes)
```bash
bash setup.sh

# Wizard asks:
# ✓ Project type? (fullstack, backend-only, frontend-only, monorepo, other)
# ✓ Backend folder? (auto-detected: /backend, /api, /server, /src, etc.)
# ✓ Frontend folder? (auto-detected: /frontend, /web, /apps/web, etc.)
# ✓ Python tools available? (Black, isort, Ruff)
# ✓ Frontend tools available? (ESLint, Prettier, TypeScript)
# ✓ Database? (Alembic/SQLAlchemy, Prisma, Sequelize, none)
# ✓ Which hooks to enable? (shows 14, user selects)
# ✓ Custom documentation paths?
```

### **Step 3: Auto-Generated Setup** (10 seconds)
```
✅ Generated .claude/config.json (team defaults)
✅ Generated .claude/config.local.json (user preferences)
✅ Generated .claude/settings.local.json (hooks wired)
✅ Generated .claude/.envrc (optional: env var exports)
✅ Verified tools: Black ✓ ESLint ✓ TypeScript ✓ Alembic ✗ (warning)
✅ Ready to use! Opening onboarding guide...
```

### **Step 4: Get Started** (Immediate)
User opens Claude Code in their project → hooks work automatically → dashboard opens → done!

---

## 📁 New File Structure

```
claude-config-kit/
├── setup.sh                          ← NEW: Interactive setup wizard
├── scripts/
│   ├── detect_project.py            ← NEW: Auto-detect project structure
│   ├── detect_tools.py              ← NEW: Verify installed tools
│   ├── generate_config.py           ← NEW: Create config files
│   ├── generate_dashboard.py        ← UPDATED: Use dynamic configs
│   └── onboarding.py                ← NEW: Generate role-based guides
├── .claude/
│   ├── hooks/
│   │   ├── lib/
│   │   │   ├── common.sh            ← UPDATED: Read configs, smart paths
│   │   │   └── config_loader.sh     ← NEW: Config parsing utilities
│   │   ├── pre_tool/
│   │   │   ├── 01_alembic_preflight.sh     ← UPDATED: Optional if no DB
│   │   │   ├── 02_migration_guard.sh       ← UPDATED: Optional
│   │   │   ├── 03_branch_protection.sh     ← UPDATED: Adaptive
│   │   │   ├── 04_precommit_quality.sh     ← UPDATED: Skip if no tools
│   │   │   └── ...
│   │   └── post_tool/
│   │       ├── 05_py_autoformat.sh         ← UPDATED: Skip if no Black
│   │       ├── 06_ts_eslint_fix.sh         ← UPDATED: Skip if no ESLint
│   │       └── ...
│   ├── config.template.json         ← NEW: Team defaults (checked in)
│   ├── config.local.template.json   ← NEW: User local (not checked in)
│   ├── .envrc.template              ← NEW: Optional env setup
│   └── settings.template.json       ← UPDATED: References hook registry
├── docs/
│   ├── SETUP.md                     ← NEW: Step-by-step user guide
│   ├── DEVELOPER_GUIDE.md           ← NEW: For Python/backend devs
│   ├── FRONTEND_GUIDE.md            ← NEW: For React/TypeScript devs
│   ├── DEVOPS_GUIDE.md              ← NEW: For infra/DevOps roles
│   ├── TEAM_ADMIN_GUIDE.md          ← NEW: For team leads
│   └── TROUBLESHOOTING.md           ← NEW: Common issues
├── examples/
│   ├── config.fullstack.json        ← NEW: Fullstack project example
│   ├── config.backend_only.json     ← NEW: Backend-only example
│   ├── config.monorepo.json         ← NEW: Monorepo example
│   └── config.nextjs.json           ← NEW: Next.js specific
└── README.md                        ← UPDATED: Link to setup.sh
```

---

## 🔧 Key Changes to Commands & Hooks

### **1. Config System** (NEW)

#### **`.claude/config.template.json`** (Checked in)
```json
{
  "project_type": "fullstack",  // auto-detected by setup.sh
  "detection": {
    "backend_folders": ["backend", "api", "server"],
    "frontend_folders": ["frontend", "web", "apps/web"],
    "docs_folders": ["docs", "Documentation"],
    "venv_type": "venv"  // venv | poetry | uv | conda
  },
  "tools": {
    "python": {
      "formatters": ["black", "ruff"],
      "linters": ["pylint", "flake8"]
    },
    "typescript": {
      "linters": ["eslint"],
      "formatters": ["prettier"]
    },
    "database": {
      "type": "alembic",  // alembic | prisma | sequelize | none
      "migrations_path": "alembic/versions"
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
    ]
  },
  "dashboard": {
    "enabled": true,
    "docs_path": "Documentation/project_status",
    "include_metrics": ["features", "hooks", "team"]
  }
}
```

#### **`.claude/config.local.json`** (User's machine, not checked in)
```json
{
  "user": {
    "name": "Alice",
    "role": "backend",  // backend | frontend | fullstack | devops
    "preferred_hooks": ["03_branch_protection", "04_precommit_quality"]
  },
  "paths": {
    "backend_dir": "/Users/alice/projects/myapp/backend",
    "frontend_dir": "/Users/alice/projects/myapp/frontend"
  },
  "tool_overrides": {
    "python.formatter": "ruff",  // Override default
    "skip_typecheck": true  // Skip TS checks
  },
  "env_vars": {
    "PYTHONPATH": "/custom/path"
  }
}
```

#### **`.claude/.envrc`** (NEW, optional)
```bash
# Direnv setup for automatic environment loading
export BACKEND_DIR="$(git rev-parse --show-toplevel)/backend"
export FRONTEND_DIR="$(git rev-parse --show-toplevel)/frontend"
export CLAUDE_CONFIG_MODE="dynamic"  # Signals dynamic config is active
```

---

### **2. Updated `lib/common.sh`** (Core changes)

**Before:**
```bash
BACKEND_DIR="${BACKEND_DIR:-$PROJECT_ROOT/backend}"
FRONTEND_DIR="${FRONTEND_DIR:-$PROJECT_ROOT/frontend}"
```

**After:**
```bash
# Load dynamic config with smart fallbacks
source "$(dirname "$0")/config_loader.sh"

# Try in order: env var → config.local.json → config.json → auto-detect → default
detect_and_set_paths() {
  # 1. Check env vars first (user can override with export)
  if [ -n "${BACKEND_DIR:-}" ]; then
    return 0
  fi
  
  # 2. Load from config.local.json (user preferences)
  local local_cfg="$PROJECT_ROOT/.claude/config.local.json"
  if [ -f "$local_cfg" ]; then
    BACKEND_DIR=$(json_get_from_file "$local_cfg" "paths.backend_dir" || true)
    [ -n "$BACKEND_DIR" ] && return 0
  fi
  
  # 3. Load from config.json (team defaults)
  local team_cfg="$PROJECT_ROOT/.claude/config.json"
  if [ -f "$team_cfg" ]; then
    local detection=$(json_get_from_file "$team_cfg" "detection.backend_folders" || true)
    BACKEND_DIR=$(auto_detect_folder "$detection" || true)
    [ -n "$BACKEND_DIR" ] && return 0
  fi
  
  # 4. Auto-detect common patterns
  BACKEND_DIR=$(auto_detect_common_backend_folders || true)
  
  # 5. Fall back to default
  BACKEND_DIR="${PROJECT_ROOT}/backend"
}

detect_and_set_paths
```

---

### **3. Updated Hook System** (Smart conditional execution)

**New `config_loader.sh`:**
```bash
# Check if a hook should run based on config
should_run_hook() {
  local hook_id="$1"  # e.g., "05_py_autoformat"
  local cfg="$PROJECT_ROOT/.claude/config.json"
  
  # Check if explicitly disabled
  if grep -q "\"$hook_id\"" "$cfg" | grep -q "disabled_hooks"; then
    return 1
  fi
  
  # Check if required tool exists
  case "$hook_id" in
    05_py_autoformat) [ -x "$(which black)" ] || [ -x "$VENV_SCRIPTS/black.exe" ] ;;
    06_ts_eslint_fix) [ -d "$FRONTEND_DIR/node_modules/eslint" ] ;;
    07_ts_typecheck) [ -d "$FRONTEND_DIR/node_modules/typescript" ] ;;
    *) return 0 ;;
  esac
}

# New: detect_and_validate_tool
tool_available() {
  local tool="$1"
  command -v "$tool" >/dev/null 2>&1 || \
  [ -x "$VENV_SCRIPTS/$tool.exe" ] || \
  [ -x "$VENV_SCRIPTS/$tool" ]
}
```

**Updated `05_py_autoformat.sh`:**
```bash
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"
source "$(dirname "$0")/../lib/config_loader.sh"

# Early exit if not configured
should_run_hook "05_py_autoformat" || exit 0

FILE_PATH="$(json_input_get path)"
[[ -z "$FILE_PATH" ]] && FILE_PATH="$(json_input_get file_path)"
FILE_PATH_NORM="$(normalize_path "$FILE_PATH")"

# Smart backend dir detection
if [ ! -d "$BACKEND_DIR" ]; then
  hook_warn "Backend directory not found at $BACKEND_DIR — skipping py autoformat"
  exit 0
fi

# Check if file is in backend
echo "$FILE_PATH_NORM" | grep -q "$BACKEND_DIR" || exit 0

# Only format if tool is available
if ! tool_available "black"; then
  hook_info "black not installed — run: cd $BACKEND_DIR && uv add --dev black isort"
  exit 0
fi

# Rest of hook logic...
```

---

### **4. New Setup Wizard** (`setup.sh`)

```bash
#!/usr/bin/env bash
# Interactive setup wizard for new users

cat << 'EOF'
╭─────────────────────────────────────────────────────────╮
│   🚀 Claude Config Kit Setup Wizard                    │
│   Auto-configures hooks for YOUR project               │
╰─────────────────────────────────────────────────────────╯
EOF

# Step 1: Project detection
echo "Detecting your project structure..."
python3 scripts/detect_project.py > /tmp/project_detected.json

PROJECT_TYPE=$(jq -r '.project_type' /tmp/project_detected.json)
BACKEND_DIR=$(jq -r '.backend_dir' /tmp/project_detected.json)
FRONTEND_DIR=$(jq -r '.frontend_dir' /tmp/project_detected.json)

echo "✓ Detected: $PROJECT_TYPE"
echo "  Backend: $BACKEND_DIR"
echo "  Frontend: $FRONTEND_DIR"

# Step 2: Tool detection
echo ""
echo "Checking available tools..."
python3 scripts/detect_tools.py > /tmp/tools_detected.json

PYTHON_TOOLS=$(jq -r '.python_tools[]' /tmp/tools_detected.json)
JS_TOOLS=$(jq -r '.js_tools[]' /tmp/tools_detected.json)

echo "✓ Found: $PYTHON_TOOLS"
echo "✓ Found: $JS_TOOLS"

# Step 3: Interactive selections (if needed)
read -p "Project type correct? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
  # Let user choose from list
  echo "Select project type:"
  select opt in "fullstack" "backend-only" "frontend-only" "monorepo"; do
    PROJECT_TYPE="$opt"
    break
  done
fi

# Step 4: Generate configs
echo ""
echo "Generating configurations..."
python3 scripts/generate_config.py \
  --project-type "$PROJECT_TYPE" \
  --backend "$BACKEND_DIR" \
  --frontend "$FRONTEND_DIR" \
  --tools-detected /tmp/tools_detected.json

echo "✓ Created .claude/config.json"
echo "✓ Created .claude/config.local.json"
echo "✓ Created .claude/settings.local.json"

# Step 5: Make hooks executable
chmod +x .claude/hooks/lib/*.sh
chmod +x .claude/hooks/pre_tool/*.sh
chmod +x .claude/hooks/post_tool/*.sh
echo "✓ Hooks made executable"

# Step 6: Generate onboarding guide
python3 scripts/onboarding.py --role fullstack > /tmp/ONBOARDING_GUIDE.md
echo ""
echo "✓ Generated personalized onboarding guide"

echo ""
cat << 'EOF'
╭─────────────────────────────────────────────────────────╮
│   ✅ Setup Complete!                                   │
│                                                         │
│   Next steps:                                           │
│   1. Open Claude Code: claude code .                   │
│   2. Edit a Python/TypeScript file to test hooks      │
│   3. Try: /dashboard                                   │
│                                                         │
│   Questions? See docs/SETUP.md or docs/[ROLE]_GUIDE.md│
╰─────────────────────────────────────────────────────────╯
EOF
```

---

### **5. New Auto-Detection Scripts** (Python)

**`scripts/detect_project.py`** (NEW)
```python
#!/usr/bin/env python3
"""Auto-detect project structure"""

import json
import os
from pathlib import Path

def detect_backend():
    """Find backend folder by common patterns"""
    patterns = ['backend', 'api', 'server', 'src/backend']
    for pattern in patterns:
        if Path(pattern).is_dir():
            return str(Path(pattern).resolve())
    return None

def detect_frontend():
    """Find frontend folder by common patterns"""
    patterns = ['frontend', 'web', 'apps/web', 'apps/frontend', 'client', 'src/frontend']
    for pattern in patterns:
        if Path(pattern).is_dir():
            return str(Path(pattern).resolve())
    return None

def detect_project_type():
    """Determine project type"""
    has_backend = detect_backend() is not None
    has_frontend = detect_frontend() is not None
    
    if has_backend and has_frontend:
        return "fullstack"
    elif has_backend:
        return "backend_only"
    elif has_frontend:
        return "frontend_only"
    else:
        return "unknown"

# Output JSON for setup.sh to parse
result = {
    "project_type": detect_project_type(),
    "backend_dir": detect_backend() or "backend",
    "frontend_dir": detect_frontend() or "frontend"
}
print(json.dumps(result, indent=2))
```

**`scripts/detect_tools.py`** (NEW)
```python
#!/usr/bin/env python3
"""Detect installed tools and versions"""

import json
import subprocess

def check_tool(cmd):
    """Return version if tool exists, else None"""
    try:
        result = subprocess.run([cmd, '--version'], 
                              capture_output=True, text=True)
        return result.stdout.strip().split('\n')[0]
    except:
        return None

# Check Python tools
python_tools = {}
for tool in ['black', 'isort', 'ruff', 'pylint']:
    python_tools[tool] = check_tool(tool) is not None

# Check JS tools
js_tools = {}
for tool in ['node', 'npm', 'npx', 'eslint', 'prettier']:
    js_tools[tool] = check_tool(tool) is not None

# Check database tools
db_tools = {}
for tool in ['alembic', 'prisma', 'sequelize']:
    db_tools[tool] = check_tool(tool) is not None

result = {
    "python_tools": {k: v for k, v in python_tools.items() if v},
    "js_tools": {k: v for k, v in js_tools.items() if v},
    "db_tools": {k: v for k, v in db_tools.items() if v}
}
print(json.dumps(result, indent=2))
```

---

### **6. Updated Dashboard** (`generate_dashboard.py`)

**Changes:**
```python
def get_config():
    """Load dynamic config"""
    cfg_file = get_project_root() / ".claude" / "config.json"
    if cfg_file.exists():
        return json.loads(cfg_file.read_text())
    return {}

def get_enabled_hooks(config):
    """Only show enabled hooks in dashboard"""
    enabled = config.get("hooks", {}).get("enabled_hooks", [])
    # Filter hook list to only enabled ones
    return [h for h in all_hooks if h.id in enabled]

def get_project_paths(config):
    """Read paths from config"""
    return {
        "backend": config.get("detection", {}).get("backend_folders", ["backend"])[0],
        "frontend": config.get("detection", {}).get("frontend_folders", ["frontend"])[0]
    }

# Updated sections in HTML:
# - Only show hooks that are enabled
# - Show which tools are available/missing
# - Show personalized welcome for user's role
```

---

### **7. Role-Based Onboarding Guides** (NEW)

**`scripts/onboarding.py`:**
```python
#!/usr/bin/env python3
"""Generate role-specific onboarding guide"""

import argparse

guides = {
    "backend": """
# Backend Developer Quick Start

## Your Hooks
- ✓ Alembic preflight (migration checks)
- ✓ Auto-format: Black + isort
- ✓ Branch protection
- ✓ Pre-commit quality gates

## Common Tasks
1. Edit a model → hook reminds to create migration
2. Edit a view → Black auto-formats code
3. Run migrations → Alembic preflight validates
4. Commit → Quality gate checks tests pass

## Skip a Hook
Edit `.claude/config.local.json`:
```json
{"tool_overrides": {"skip_hooks": ["09_migration_reminder"]}}
```

## Troubleshooting
- Black not found? → cd backend && uv add --dev black
- Alembic error? → /db-migration-resolver
""",
    
    "frontend": """
# Frontend Developer Quick Start

## Your Hooks
- ✓ ESLint --fix
- ✓ TypeScript type-check
- ✓ Auto-format on save
- ✓ Branch protection

## Common Tasks
1. Edit .tsx → TypeScript validates
2. Edit .ts → ESLint auto-fixes style
3. Commit → Pre-commit quality checks
4. Push → Branch protection prevents main push

## Skip a Hook
Edit `.claude/config.local.json`:
```json
{"tool_overrides": {"skip_typecheck": true}}
```

## Troubleshooting
- ESLint not found? → cd frontend && npm install
- Type errors? → npx tsc --noEmit
""",

    "fullstack": """
# Full-Stack Developer Quick Start

You have ALL hooks available. They auto-adapt to what you're editing.

- Editing .py? → Black + isort
- Editing .tsx? → ESLint + TypeScript
- Editing models? → Migration checks
- Pushing? → Branch protection + quality gates

See Backend Developer or Frontend Developer guides for role-specific details.
"""
}

parser = argparse.ArgumentParser()
parser.add_argument("--role", default="fullstack")
args = parser.parse_args()

print(guides.get(args.role, guides["fullstack"]))
```

---

## 📋 Implementation Checklist

### **Phase 1: Infrastructure** (Week 1)
- [ ] Create `config.template.json` with all options documented
- [ ] Create `config.local.template.json` for user overrides
- [ ] Create `config_loader.sh` with config parsing + fallback logic
- [ ] Update `lib/common.sh` to use new config system
- [ ] Create `.gitignore` entries for `config.local.json`, `.envrc`

### **Phase 2: Auto-Detection** (Week 1-2)
- [ ] Write `detect_project.py` (backend/frontend folder detection)
- [ ] Write `detect_tools.py` (tool availability checking)
- [ ] Write `detect_database.py` (Alembic vs Prisma vs Sequelize vs none)
- [ ] Write `generate_config.py` (create config files from detection)
- [ ] Test on 5+ different project structures

### **Phase 3: Setup Wizard** (Week 2)
- [ ] Write `setup.sh` (interactive flow)
- [ ] Add validation (does generated config work?)
- [ ] Add recovery (if detection fails, allow manual input)
- [ ] Test on Windows + macOS + Linux

### **Phase 4: Smart Hooks** (Week 2-3)
- [ ] Update all 14 hooks to check configs before running
- [ ] Add tool availability checks (graceful skip if missing)
- [ ] Add conditional logic per project type
- [ ] Test each hook with multiple tool configurations

### **Phase 5: Documentation & Guides** (Week 3)
- [ ] Update `README.md` → link to `SETUP.md`
- [ ] Create `docs/SETUP.md` (step-by-step user guide)
- [ ] Create `docs/DEVELOPER_GUIDE.md`, `FRONTEND_GUIDE.md`, etc.
- [ ] Create `docs/TROUBLESHOOTING.md` with FAQ
- [ ] Create example configs for 5+ project types

### **Phase 6: Onboarding Automation** (Week 3)
- [ ] Write `onboarding.py` (role-based guides)
- [ ] Auto-open guide after setup
- [ ] Create `docs/[ROLE]_GUIDE.md` files
- [ ] Integration with Claude Code skill system

### **Phase 7: Dashboard & Commands** (Week 4)
- [ ] Update `generate_dashboard.py` to read from config
- [ ] Add "Hook Status" section (enabled/disabled, available/missing)
- [ ] Add "Project Health" showing tool availability
- [ ] Create `/smart-setup` skill (trigger setup.sh from Claude Code)

### **Phase 8: Testing & QA** (Week 4)
- [ ] Integration tests (setup.sh + hooks on test projects)
- [ ] Cross-platform tests (Windows, macOS, Linux)
- [ ] Edge cases (monorepo, microservices, custom layouts)
- [ ] User acceptance testing with 3-5 real users

---

## 📦 Distribution & Getting Started

### **For End Users (New Members)**

**Option 1: Quick Start (2 minutes)**
```bash
# Clone kit
git clone https://github.com/your-org/claude-config-kit.git .claude-kit

# Setup (interactive)
cd .claude-kit
bash setup.sh

# Open Claude Code
cd ..
claude code .
```

**Option 2: Submodule (Team)**
```bash
# Add to team project
git submodule add https://github.com/your-org/claude-config-kit.git .claude-kit

# New member onboards
cd .claude-kit && bash setup.sh
```

**Option 3: Automated (CI/CD)**
```yaml
# In GitHub Actions or GitLab CI, auto-run setup on first clone
- name: Setup Claude Config Kit
  if: ${{ !fileExists('.claude/config.json') }}
  run: bash .claude-kit/setup.sh --non-interactive
```

### **For Team Admins**

1. **Create org-wide config template:**
   ```bash
   cp .claude/config.template.json .claude/config.json
   # Edit with team defaults, commit
   git add .claude/config.json
   git commit -m "Add team Claude config kit settings"
   ```

2. **Document in onboarding:**
   - Add to employee wiki: "Run `bash .claude-kit/setup.sh` after cloning"
   - Link to `docs/SETUP.md` in README
   - Link to role-specific guides in Slack

3. **Monitor hook usage:**
   - Dashboard shows enabled hooks per project
   - Can export hook stats for team health report

---

## 🎯 Benefits After Implementation

| User Type | Before | After |
|-----------|--------|-------|
| **New Developer** | 1-2 hours manual setup | 2 mins automated setup |
| **Project Lead** | Manual documentation | Auto-generated dashboard |
| **DevOps/Admin** | Copy configs to each repo | Define once, inherit to all |
| **Tool Support** | "Install Black manually" | Auto-detects + guides install |
| **Multi-Project Dev** | Different hooks per project | One kit, all projects adapted |

---

## 🔐 Safety & Validation

- **Config validation:** On load, check all paths exist + all tools referenced are compatible
- **Hook rollback:** If a hook fails, it warns but doesn't block (fail-safe)
- **Version compatibility:** Config includes `schema_version` field for future migrations
- **Testing:** Every project gets a test run of all enabled hooks before they activate

---

## 📝 Summary: What Changes in Commands & Hooks

| Component | Current | New |
|-----------|---------|-----|
| **`lib/common.sh`** | Fixed paths | Config-driven + smart fallback |
| **All 14 hooks** | Hardcoded checks | Read config + conditional execute |
| **`settings.json`** | Manual template | Auto-generated by setup.sh |
| **New: `config.json`** | — | Team defaults (checked in) |
| **New: `config.local.json`** | — | User overrides (.gitignore'd) |
| **Dashboard** | Static docs paths | Reads from config |
| **New: `setup.sh`** | — | Interactive wizard (2 mins) |
| **New: `detect_*.py`** | — | Auto-detect project structure |
| **New: Onboarding guides** | — | Role-specific (auto-generated) |

---

**Next Step:** Start with **Phase 1 & 2** (infrastructure + auto-detection) → Have real user test → Iterate
