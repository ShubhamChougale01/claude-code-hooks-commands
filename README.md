# 🪝 Claude Code Hooks & Commands

> **A unified toolkit of Claude Code hooks, custom commands, and AI-powered Git hooks — drop them into any project to enforce code quality automatically.**

[![Hooks](https://img.shields.io/badge/Claude%20Code%20Hooks-13%20Production%20Ready-brightgreen?style=flat-square)](https://github.com/ShubhamChougale01/claude-code-hooks-commands)
[![Git Hooks](https://img.shields.io/badge/Git%20Hooks-AI%20Powered-blue?style=flat-square)](https://github.com/ShubhamChougale01/claude-code-hooks-commands)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange?style=flat-square)](https://github.com/ShubhamChougale01/claude-code-hooks-commands)

---

## What Is This?

This repo contains two complementary systems that work at different layers of your development workflow:

- **Claude Code Hooks** — 13 shell hooks that run automatically inside Claude Code before and after every tool execution. They auto-format files, guard migrations, block bad pushes, sync schemas, and more — without you asking.
- **AI-Powered Git Hooks** — Pre-push and post-receive hooks that use the Claude API to review your full diff and block pushes with critical or high-severity issues before they reach your repo.

Together, they form a **continuous quality enforcement pipeline** from the moment you edit a file to the moment you push to GitHub.

---

## What's Inside

| Layer | Type | Count | What It Does |
|-------|------|-------|--------------|
| 🔵 **Claude Code** | Pre-tool hooks | 4 | Preventive checks before Claude edits files |
| 🟢 **Claude Code** | Post-tool hooks | 9 | Auto-fixes and sync checks after edits |
| 💬 **Claude Code** | Custom command | 1 | `/dashboard` — interactive project status |
| 🔴 **Git** | Pre-push / Post-receive | 2 | AI-powered diff review via Claude API |

---

## ⚡ Quick Setup (2 Steps)

### Step 1 — Clone this repo

```bash
git clone https://github.com/ShubhamChougale01/claude-code-hooks-commands.git
```

### Step 2 — Copy the `.claude` folder into your project

```bash
# Mac / Linux
cp -r claude-code-hooks-commands/.claude /your-project/.claude

# Windows (PowerShell)
Copy-Item -Recurse claude-code-hooks-commands\.claude /your-project/.claude
```

Open your project in Claude Code — hooks and commands are live immediately.

> **Tip:** To set up the Git AI review hook too, follow the [Git Hooks Setup](#-git-hooks-setup) section below.

---

## Claude Code Hooks

### 🔵 Pre-Tool Hooks — run before Claude edits a file

These are preventive. They check conditions and block operations that would cause problems downstream.

---

#### `01_alembic_preflight.sh`

**What it does:** Automatically backs up your database before any Alembic `upgrade` or `downgrade` command runs.

**Why it matters:** Migration failures on production data are irreversible. This gives you a restore point every time.

**Triggers on:** Any tool call involving `alembic upgrade` or `alembic downgrade`

---

#### `02_migration_guard.sh`

**What it does:** Blocks direct edits to Alembic or Django migration files.

**Why it matters:** Hand-editing migration files causes branching conflicts and schema drift. Changes to models should generate new migrations, not patch old ones.

**Triggers on:** Any file write targeting a `migrations/` directory

---

#### `03_branch_protection.sh`

**What it does:** Prevents direct pushes to `main` or `master` branches.

**Why it matters:** Direct pushes bypass code review. This forces all changes through feature branches and PRs.

**Triggers on:** Any `git push` targeting `main` or `master`

---

#### `04_precommit_quality.sh`

**What it does:** Runs TypeScript type checks, ESLint, and Black formatting validation before every commit.

**Why it matters:** Catches type errors and lint violations before they enter version history — not after CI fails.

**Triggers on:** Any `git commit` command

---

### 🟢 Post-Tool Hooks — run after Claude edits a file

These are reactive. They auto-fix and sync issues the moment a file is changed.

---

#### `05_py_autoformat.sh`

**What it does:** Automatically runs Black + isort on every `.py` file Claude edits.

**Why it matters:** No more "formatting commit" noise. Python files are always clean on write.

**Triggers on:** Any `.py` file saved by Claude

---

#### `06_ts_eslint_fix.sh`

**What it does:** Runs ESLint with `--fix` on every `.ts` or `.tsx` file Claude edits.

**Why it matters:** Auto-fixes the class of lint issues that don't require judgment — imports, spacing, unused vars.

**Triggers on:** Any `.ts` / `.tsx` file saved by Claude

---

#### `07_ts_typecheck.sh`

**What it does:** Runs `tsc --noEmit` after TypeScript file edits to surface type errors immediately.

**Why it matters:** Type errors caught at edit time are free to fix. Type errors caught at CI time cost a pipeline run and context switch.

**Triggers on:** Any `.ts` / `.tsx` file saved by Claude

---

#### `08_model_schema_drift.sh`

**What it does:** Compares your ORM models against your database schema and flags any drift.

**Why it matters:** Models and schemas silently diverging is one of the most common causes of runtime errors in backend services.

**Triggers on:** Any model file edit (e.g., `models.py`, `schema.py`)

---

#### `09_migration_reminder.sh`

**What it does:** After a model file is edited, prompts you to generate a new migration if none exists for the change.

**Why it matters:** It's easy to forget to run `alembic revision` or `makemigrations`. This makes it impossible to miss.

**Triggers on:** Any ORM model file edit

---

#### `10_intent_action_sync.sh`

**What it does:** Checks that intent and action service definitions stay in sync after edits to either.

**Why it matters:** Mismatched intent/action pairs cause silent runtime failures in agent-based or event-driven architectures.

**Triggers on:** Intent or action service file edits

---

#### `11_env_drift.sh`

**What it does:** Diffs `.env` against `.env.example` and flags any variables present in one but not the other.

**Why it matters:** `.env.example` out of sync with `.env` is a silent onboarding breaker and a common source of "works on my machine" bugs.

**Triggers on:** Any edit to `.env` or `.env.example`

---

#### `12_dep_sync_reminder.sh`

**What it does:** After edits to `requirements.txt`, `package.json`, or `pyproject.toml`, reminds you to run `pip install` or `npm install`.

**Why it matters:** Forgetting to install after dependency changes causes confusing import errors that waste debugging time.

**Triggers on:** `requirements.txt`, `package.json`, `pyproject.toml` edits

---

#### `13_api_sync.sh`

**What it does:** Checks that backend route definitions and frontend API client calls stay in sync after edits to either.

**Why it matters:** Route renames or signature changes on the backend break frontend callers silently until runtime.

**Triggers on:** Backend route files or frontend API client file edits

---

### 💬 Custom Command — `/dashboard`

Run `/dashboard` inside any Claude Code session to generate an interactive project status report:

- ✅ Open tasks and blockers
- ✅ Recent file changes and their impact
- ✅ Migration and schema health
- ✅ Dependency sync status
- ✅ Environment drift summary

```
/dashboard
```

---

## 🔴 Git Hooks Setup

The `git-hooks/` folder contains an AI-powered pre-push reviewer that uses the Claude API to analyze your diff before it reaches remote.

### How It Works

```
git push
    ↓
pre-push hook intercepts the push
    ↓
Diff sent to Claude API (claude-haiku)
    ↓
Issues scored: CRITICAL / HIGH / MEDIUM / LOW
    ↓
CRITICAL or HIGH → push blocked with explanation
MEDIUM / LOW     → warning printed, push proceeds
```

### Install (Local — pre-push)

```bash
# Mac / Linux
cd git-hooks
cp .env.example .env          # add your ANTHROPIC_API_KEY
bash scripts/install_local.sh

# Windows (PowerShell)
cd git-hooks
Copy-Item .env.example .env   # add your ANTHROPIC_API_KEY
powershell scripts/install_local.ps1
```

### Install (Server — post-receive)

```bash
# Mac / Linux
bash scripts/install_server.sh

# Windows (PowerShell)
powershell scripts/install_server.ps1
```

### What It Catches

| Severity | Examples | Push Blocked? |
|----------|----------|---------------|
| 🔴 CRITICAL | Hardcoded secrets, SQL injection, auth bypass | ✅ Yes |
| 🟠 HIGH | Missing error handling, N+1 queries, data loss risk | ✅ Yes |
| 🟡 MEDIUM | Code smells, naming issues, missing validation | ⚠️ Warning only |
| 🟢 LOW | Style suggestions, minor improvements | ℹ️ Info only |

### Dry Run (no API key required)

```bash
DRY_RUN=true git push
```

---

## Full Development Flow

```
Developer edits a file in Claude Code
          ↓
Post-tool hooks fire instantly
  • .py file? → Black + isort applied
  • .ts file? → ESLint fix + tsc type check
  • model file? → schema drift check + migration reminder
  • .env file? → drift check vs .env.example
  • dep file? → install reminder
          ↓
Developer commits
  • Pre-tool hook fires → TypeScript + ESLint + Black quality gate
          ↓
Developer pushes
  • Git pre-push hook fires → Claude API diff review
  • CRITICAL/HIGH issues → push blocked with explanation
  • MEDIUM/LOW → warning printed
          ↓
Push reaches remote only if all gates pass
```

---

## Folder Structure

```
claude-code-hooks-commands/
├── .claude/
│   ├── hooks/
│   │   ├── lib/
│   │   │   └── common.sh              # Shared utilities (project root detection, JSON helpers)
│   │   ├── pre_tool/                  # Hooks that run before Claude tool calls
│   │   │   ├── 01_alembic_preflight.sh
│   │   │   ├── 02_migration_guard.sh
│   │   │   ├── 03_branch_protection.sh
│   │   │   └── 04_precommit_quality.sh
│   │   └── post_tool/                 # Hooks that run after Claude tool calls
│   │       ├── 05_py_autoformat.sh
│   │       ├── 06_ts_eslint_fix.sh
│   │       ├── 07_ts_typecheck.sh
│   │       ├── 08_model_schema_drift.sh
│   │       ├── 09_migration_reminder.sh
│   │       ├── 10_intent_action_sync.sh
│   │       ├── 11_env_drift.sh
│   │       ├── 12_dep_sync_reminder.sh
│   │       └── 13_api_sync.sh
│   └── commands/
│       └── dashboard.md               # /dashboard command definition
├── git-hooks/                         # AI-powered Git review hooks
│   ├── hooks/
│   │   ├── pre-push                   # Local pre-push reviewer
│   │   └── post-receive               # Server-side reviewer
│   ├── src/                           # Python review engine
│   │   ├── run_review.py
│   │   ├── analyzer.py
│   │   ├── severity_detector.py
│   │   ├── formatter.py
│   │   └── config.py
│   ├── scripts/                       # Install scripts (Windows + Linux/macOS)
│   │   ├── install_local.sh/.ps1
│   │   └── install_server.sh/.ps1
│   ├── .env.example
│   └── README.md
├── scripts/
│   └── generate_dashboard.py          # Dashboard HTML generator
├── docs/                              # Extended documentation
│   ├── START_HERE.md
│   ├── QUICK_REFERENCE.md
│   ├── EXECUTIVE_SUMMARY.md
│   ├── MULTI_USER_DYNAMIC_PLAN.md
│   ├── USER_FLOW_DIAGRAM.md
│   ├── IMPLEMENTATION_CHANGES.md
│   ├── INTEGRATION.md
│   └── DOCUMENTATION_INDEX.md
└── README.md
```

---

## Requirements

- [Claude Code](https://claude.ai/code) (CLI, desktop app, or IDE extension)
- An active Claude account (Pro or higher recommended)
- For Claude Code hooks: Bash available in your environment (Git Bash on Windows)
- For Python auto-format hook: Python 3.8+ with `black` and `isort` installed
- For TypeScript hooks: Node.js with `typescript` and `eslint` installed
- For Git AI review hook: Python 3.8+, `anthropic` Python package, and an `ANTHROPIC_API_KEY`

---

## FAQ

**Do the Claude Code hooks work on Windows?**
Yes. The hooks use `common.sh` for portable path handling. Run them via Git Bash or WSL.

**Can I use just the Claude Code hooks without the Git hooks?**
Yes. Copy only the `.claude/` folder into your project. The `git-hooks/` folder is completely independent.

**Can I use just the Git hooks without Claude Code?**
Yes. The `git-hooks/` folder works in any Git repo — it doesn't require Claude Code.

**Will hooks modify my files without asking?**
The post-tool hooks (Black, ESLint) auto-apply safe formatting fixes. The Git AI reviewer blocks pushes but never modifies files. Everything that could be destructive (migrations, schema changes) shows a warning and asks for your approval first.

**Can I disable a specific hook?**
Yes. Make the hook script exit 0 immediately, or remove it from the `pre_tool/` or `post_tool/` directory.

**How much does the Git AI review cost?**
It uses `claude-haiku` which is the most cost-efficient model. A typical diff review costs less than $0.001.

**Can I add my own hooks?**
Yes. Add a shell script to `pre_tool/` or `post_tool/` following the numbering convention. Use `common.sh` for shared utilities.

---

## Contributing

Found a bug or want to add a hook? Open an issue or submit a PR. Hooks follow a simple structure — a shell script in `pre_tool/` or `post_tool/` that sources `lib/common.sh` for shared utilities.

---

## License

MIT — free to use, modify, and distribute.

---

<p align="center">Built for engineers who want their code quality enforced automatically — not manually.</p>
