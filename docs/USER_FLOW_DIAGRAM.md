# User Flow Diagram: From Getting Kit to Using It

## 🎬 Current Flow (Manual & Tedious)

```
New User Gets Kit
      ↓
   ❌ Read README (confused about config)
      ↓
   ❌ Manually copy .claude/ folder
      ↓
   ❌ Edit .claude/settings.local.json (hardcoded paths)
      ↓
   ❌ Edit .claude/settings.local.json (remove/add hooks)
      ↓
   ❌ Fails because backend/ folder doesn't exist
      ↓
   ❌ Tries to run hooks manually
      ↓
   ❌ "Black not installed" error
      ↓
   😤 Gives up or wastes 1-2 hours
```

---

## ✨ New Flow (Automated & Smart)

```
┌─────────────────────────────────────────────────────────────────┐
│ NEW USER GETS KIT                                               │
│ git clone https://github.com/org/claude-config-kit .claude-kit  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                  bash setup.sh (2 minutes)
                        ↙         ↘
                       /           \
                      ↓             ↓
           ┌──────────────────┐  ┌──────────────────┐
           │ Auto-Detect      │  │ Check Tools      │
           │                  │  │                  │
           │ • Backend folder │  │ • Black ✓        │
           │ • Frontend       │  │ • ESLint ✓       │
           │ • Database type  │  │ • TypeScript ✓   │
           │ • Project type   │  │ • Alembic ✗      │
           └──────────────────┘  └──────────────────┘
                      ↓                    ↓
                      └────────────┬───────┘
                                   ↓
                   ┌────────────────────────────┐
                   │ Suggest Configurations     │
                   │                            │
                   │ • Use Black for Python ✓   │
                   │ • Use ESLint for TS ✓      │
                   │ • Skip Alembic (not found) │
                   │ • Enable branch protection │
                   └────────────────────────────┘
                                   ↓
                   ┌────────────────────────────┐
                   │ User Confirms (or Edits)   │
                   │                            │
                   │ Project type: fullstack ✓  │
                   │ Enable hooks: 7/14 ✓       │
                   └────────────────────────────┘
                                   ↓
           ┌─────────────────────────────────────────┐
           │ SYSTEM GENERATES                        │
           │                                         │
           │ ✓ .claude/config.json (team defaults)  │
           │ ✓ .claude/config.local.json (personal) │
           │ ✓ .claude/settings.local.json (wired)  │
           │ ✓ Make hooks executable                │
           └─────────────────────────────────────────┘
                                   ↓
           ┌─────────────────────────────────────────┐
           │ ✨ READY TO USE                         │
           │                                         │
           │ "Next: Open Claude Code"                │
           │ claude code .                           │
           └─────────────────────────────────────────┘
                                   ↓
           ┌─────────────────────────────────────────┐
           │ Opens personalized role-based guide     │
           │                                         │
           │ 📖 BACKEND_GUIDE.md                    │
           │    • Your hooks (migration checks, etc)│
           │    • Common tasks                       │
           │    • Troubleshooting                    │
           └─────────────────────────────────────────┘
                                   ↓
                    User edits code in Claude Code
                                   ↓
           ┌─────────────────────────────────────────┐
           │ HOOKS AUTO-RUN (No Configuration!)      │
           │                                         │
           │ Edit models/migrate.py →               │
           │   Hook: Alembic preflight (detects config)│
           │   Hook: Black auto-format (checks if enabled)
           │                                         │
           │ Edit src/Button.tsx →                  │
           │   Hook: ESLint --fix (reads config)    │
           │   Hook: TypeScript check (runs)        │
           │                                         │
           │ git commit →                           │
           │   Hook: Pre-commit quality gate        │
           │                                         │
           │ git push →                             │
           │   Hook: Branch protection ✓            │
           └─────────────────────────────────────────┘
                                   ↓
                    🎉 Everything works, user happy!
```

---

## 🏗️ Technical Architecture

### **Config Resolution Pipeline**

```
Hook execution (e.g., 05_py_autoformat.sh)
            ↓
Source config_loader.sh
            ↓
    ┌───────────────────────────────┐
    │ Load configs in order:        │
    ├───────────────────────────────┤
    │ 1. Environment variables      │
    │    $BACKEND_DIR               │
    ├───────────────────────────────┤
    │ 2. .claude/config.local.json  │
    │    (User overrides)           │
    ├───────────────────────────────┤
    │ 3. .claude/config.json        │
    │    (Team defaults)            │
    ├───────────────────────────────┤
    │ 4. Auto-detect patterns       │
    │    (common folder names)      │
    ├───────────────────────────────┤
    │ 5. Default fallback           │
    │    (backend/, frontend/)      │
    └───────────────────────────────┘
            ↓
    Resolved paths + config
            ↓
    Execute hook logic
```

### **Hook Execution Filter**

```
Hook start (e.g., 05_py_autoformat.sh)
            ↓
    should_run_hook "05_py_autoformat"?
            ↓
         ┌──────────────────────┐
         │ Check config.json    │
         │ Is it enabled?       │
         └──────────────────────┘
            ↙        ↖
          NO        YES
          ↓          ↓
       Exit     Check tool
                (black exists?)
                 ↙        ↖
               NO        YES
               ↓          ↓
            Exit      Run hook
                        ↓
                   Format & exit
```

---

## 📂 File Dependency Map

```
User's Project
├── .claude-kit/                    ← Kit submodule/clone
│   ├── setup.sh                    ← User runs this ONCE
│   ├── scripts/
│   │   ├── detect_project.py       ← Scans project structure
│   │   ├── detect_tools.py         ← Finds installed tools
│   │   ├── generate_config.py      ← Creates config files
│   │   ├── onboarding.py           ← Generates guides
│   │   └── generate_dashboard.py   ← Updated to use configs
│   └── .claude/
│       ├── config.template.json    ← Checked in (team defaults)
│       └── hooks/
│           └── lib/
│               ├── common.sh       ← Updated (read configs)
│               └── config_loader.sh ← NEW
│
├── .claude/                        ← Generated for each user
│   ├── config.json                 ← Team defaults (checked in)
│   ├── config.local.json           ← User preferences (git-ignored)
│   ├── settings.local.json         ← Auto-generated hooks config
│   ├── .envrc                      ← Optional env vars
│   └── hooks/                      ← Symlink or copy from kit
│       ├── lib/
│       │   ├── common.sh           ← Updated
│       │   └── config_loader.sh    ← NEW
│       ├── pre_tool/               ← Updated (use config)
│       └── post_tool/              ← Updated (use config)
│
└── README.md                       ← Updated (link to setup.sh)
```

---

## 👥 Different User Journeys

### **Journey 1: Fresh Developer (New to Company)**

```
1. Clone repo + submodule
   git clone <project>
   cd <project>
   
2. Run setup (ONCE)
   bash .claude-kit/setup.sh
   → "What's your role?" Backend
   → Auto-detects backend/ frontend/
   → Finds Python 3.11, Black, isort
   → Enables: 7 hooks relevant to backend
   
3. Get started
   Read: docs/BACKEND_GUIDE.md (personalized)
   Open: claude code .
   
4. Work normally
   Edit models.py → hooks run automatically
   Commit → quality gates check
   
✨ NO manual config, NO tool installation required
```

### **Journey 2: Experienced Dev (Switching Teams)**

```
1. Clone project into new directory
   cd ~/projects && git clone <project>
   
2. Setup (2 mins)
   bash .claude-kit/setup.sh
   → Auto-detects everything
   → Suggests fullstack (since has backend + frontend)
   → Asks to confirm
   
3. Customize (optional)
   Edit .claude/config.local.json
   {"tool_overrides": {"skip_typecheck": true}}
   
4. Done!
   Hooks skip typecheck, run everything else
   
✨ Smart defaults save time, customizable if needed
```

### **Journey 3: DevOps/Team Lead**

```
1. Setup once in main repo
   bash .claude-kit/setup.sh
   → Choose team-wide settings
   → Enable hooks: branch protection, quality gates
   
2. Check in config.json
   git add .claude/config.json
   git commit "Add team Claude kit config"
   
3. Every team member gets defaults
   When they run setup.sh, they inherit:
   • Team hooks configuration
   • Project structure detection
   • Tool requirements
   
4. Monitor
   /dashboard shows:
   • Team hook stats
   • Tool availability across team
   • Which hooks are actively used
   
✨ Define once, scale to whole team
```

---

## 🔄 Update Flows

### **Team Updates Kit (New Hook)**

```
Git repo (main)
    ↓
.claude-kit gets new hook
    ↓
Team admin: git pull (or submodule update)
    ↓
Team admin: update config.json with new hook
    ↓
git push
    ↓
All team members: git pull
    ↓
setup.sh detects new hook (optional)
    ↓
Choose to enable or disable
    ↓
Config updated, hooks work
```

### **User Customizes Setup**

```
User runs: setup.sh
    ↓
Auto-detects config
    ↓
User confirms/edits
    ↓
Generates: config.local.json
    ↓
Generates: settings.local.json
    ↓
Sets env vars (optional .envrc)
    ↓
User can edit config.local.json anytime
    ↓
Hooks automatically use new config
    ↓
No restart needed!
```

---

## 📊 Decision Tree: Does Hook Run?

```
User edits src/Button.tsx
    ↓
Claude Code triggers PostToolUse hook
    ↓
06_ts_eslint_fix.sh starts
    ↓
    should_run_hook "06_ts_eslint_fix"?
    ↓
    ├─ Is it in enabled_hooks? 
    │  ├─ No → EXIT (skip)
    │  └─ Yes ↓
    ├─ Is tool available? (eslint exists)
    │  ├─ No → WARN + EXIT (tool missing)
    │  └─ Yes ↓
    ├─ Is file in right folder? (frontend/)
    │  ├─ No → EXIT (wrong folder)
    │  └─ Yes ↓
    ├─ Should we skip this file? (.prettierignore)
    │  ├─ No → EXIT (ignored)
    │  └─ Yes ↓
    └─ RUN HOOK ✓
         └─ npx eslint --fix src/Button.tsx
         └─ Output: "Fixed 3 lint errors"
```

---

## 📈 Success Metrics

| Metric | Before | After |
|--------|--------|-------|
| **Time to Setup** | 1-2 hours | 2 minutes |
| **Manual Config Edits** | 5-10 | 0 (auto) |
| **Tool Installation Issues** | Common | Guided + graceful |
| **Hook Misconfiguration** | Frequent | Prevented by validation |
| **New User Onboarding** | 2-3 hours | 30 mins |
| **Team Standardization** | Low | High (one config) |
| **Cross-Platform Support** | Fragile | Robust |

---

## 🎯 Three-Step User Summary

### **For All Users**

```
STEP 1: Get Kit
$ git clone https://github.com/org/claude-config-kit .claude-kit

STEP 2: Run Setup
$ bash .claude-kit/setup.sh
   (auto-detects, auto-configures, 2 minutes)

STEP 3: Use in Claude Code
$ claude code .
   (hooks work automatically, no further config needed)
```

**That's it!** Everything else is optional customization.
