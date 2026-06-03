---
description: Generate and open the dynamic project status dashboard from feature.md and project_status.md
---

# Project Dashboard Command

Regenerate the comprehensive project status dashboard by parsing your documentation files and hooks configuration.

## Usage

```bash
python backend/scripts/generate_dashboard.py
```

Or in Claude Code CLI:

```
/dashboard
```

## What it does

1. **Reads documentation:**
   - `Documentation/project_status/project_status.md` — feature checklist, backend/frontend status
   - `Documentation/project_status/feature.md` — roadmap with feature statuses

2. **Extracts project infrastructure:**
   - `.claude/hooks/**/*.sh` — all 14 hooks with their purposes
   - `.claude/settings.local.json` — active hook wiring
   - Available Claude Code skills

3. **Generates HTML with 6 tabs:**
   - **Overview** — summary cards + project health
   - **Completed** — all Done features
   - **Gaps & Partials** — incomplete work
   - **Roadmap** — Next priorities
   - **Hooks & Skills** — infrastructure in use
   - **Plan** — Top 3–5 prioritized features with approach details

4. **Opens in browser** — `project_dashboard.html` appears at project root

## When to run

- After updating `project_status.md` or `feature.md`
- To check project health at a glance
- Before planning the next sprint
- To keep the dashboard current with code changes

## Notes

- No external dependencies required (uses Python stdlib only)
- Runs in ~1 second
- Completely overwrites previous `project_dashboard.html`
- Markdown table parsing uses regex; format must match existing pattern
