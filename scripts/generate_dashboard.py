#!/usr/bin/env python3
"""
Dynamic Project Status Dashboard Generator - ENHANCED VERSION

Generates a feature-rich dashboard with timestamped versions for tracking project evolution.
Shows Frontend, Backend, and System/Custom Hooks & Skills.

Usage: python scripts/generate_dashboard.py
"""

import json
import re
import webbrowser
from datetime import datetime
from pathlib import Path


def get_project_root():
    # Portable version: detect via git (works from anywhere in the repo)
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback: assume scripts/generate_dashboard.py is in scripts/ → parent/parent → project root
        return Path(__file__).parent.parent.parent


def read_file(path):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def read_hooks_from_directory():
    root = get_project_root()
    hooks_dir = root / ".claude" / "hooks"
    hooks_info = {}

    if not hooks_dir.exists():
        return hooks_info

    for hook_file in sorted(hooks_dir.rglob("*.sh")):
        if any(hook_file.name.startswith(str(i).zfill(2) + "_") for i in range(1, 15)):
            content = read_file(hook_file)
            purpose = ""
            for line in content.split("\n")[:20]:
                if "Purpose:" in line:
                    purpose = line.split("Purpose:", 1)[-1].strip().lstrip("#").strip()
                    break

            rel_path = hook_file.relative_to(hooks_dir)
            hooks_info[f"{rel_path.parent}/{hook_file.stem}"] = purpose or "Auto-check"

    return hooks_info


def parse_feature_section_zero():
    """Parse the §0 conversational-reminder requirements table from feature.md.

    Returns a list of dicts: {requirement, status, notes_excerpt} for each row
    in the §0 table (rows 30–33 today: time capture, early offset, mic auto-stop, TTS at fire).
    Empty list if file missing or table not found.
    """
    root = get_project_root()
    md = read_file(root / "Documentation" / "project_status" / "feature.md")
    if not md:
        return []
    # Find the §0 table: it starts at the "| Requirement | Expected behaviour | ..." header.
    lines = md.splitlines()
    rows: list[dict] = []
    in_table = False
    for line in lines:
        if line.startswith("| Requirement ") and "Status" in line:
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                break
            if line.startswith("|---") or line.startswith("|--"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            # Expected: requirement | expected | frontend | backend | status | notes
            if len(cells) < 6:
                continue
            req = cells[0].strip("* ").rstrip("*").strip()
            status = cells[4].replace("*", "").strip()
            notes = cells[5]
            # Trim the notes for the dashboard
            notes_excerpt = notes.split(".")[0].replace("*", "").strip()
            if len(notes_excerpt) > 180:
                notes_excerpt = notes_excerpt[:177] + "…"
            rows.append({"requirement": req, "status": status, "notes": notes_excerpt})
    return rows


def parse_all_status_rows() -> list[dict]:
    """Walk both status docs and return every markdown-table row that has a recognizable status.

    For each table whose first column-header looks like a feature/item ("Item", "Resource",
    "Requirement", "Capability"), capture the rows under the most recent `##`/`###` heading.
    Returns a list of dicts: {doc, section, item, status_raw, status_class, notes}.
    """
    root = get_project_root()
    out: list[dict] = []
    for doc_name in ("feature.md", "project_status.md"):
        text = read_file(root / "Documentation" / "project_status" / doc_name)
        if not text:
            continue
        section = ""
        in_table = False
        header_cells: list[str] = []
        status_idx = -1
        notes_idx = -1
        for raw in text.splitlines():
            line = raw.rstrip()
            if line.startswith("#"):
                section = line.lstrip("# ").strip()
                in_table = False
                continue
            if line.startswith("|---") or line.startswith("|--"):
                # separator under header — already configured indices
                continue
            if line.startswith("|"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if not in_table:
                    # This is a header row. Decide whether we care about this table.
                    header_cells = [c.lower() for c in cells]
                    status_idx = next(
                        (i for i, c in enumerate(header_cells) if "status" in c),
                        -1,
                    )
                    # Pick the rightmost free-text column as notes (often "Notes").
                    notes_idx = next(
                        (i for i, c in enumerate(header_cells) if "note" in c),
                        len(header_cells) - 1,
                    )
                    in_table = (
                        status_idx >= 0
                        and header_cells
                        and any(
                            k in header_cells[0]
                            for k in (
                                "item",
                                "resource",
                                "requirement",
                                "capability",
                                "feature",
                            )
                        )
                    )
                    continue
                # Body row
                if status_idx < 0 or status_idx >= len(cells):
                    continue
                status_raw = cells[status_idx].replace("*", "").strip()
                if not status_raw:
                    continue
                item = cells[0].replace("*", "").strip()
                notes = (
                    cells[notes_idx].replace("*", "").strip()
                    if 0 <= notes_idx < len(cells)
                    else ""
                )
                # Trim
                if len(notes) > 220:
                    notes = notes[:217] + "…"
                out.append(
                    {
                        "doc": doc_name,
                        "section": section,
                        "item": item,
                        "status_raw": status_raw,
                        "status_class": classify_status(status_raw),
                        "notes": notes,
                    }
                )
            else:
                in_table = False
    return out


def classify_status(status_text: str) -> str:
    """Map feature.md status strings to dashboard CSS class (done/partial/todo/next)."""
    s = status_text.lower()
    if "shipped" in s or "done" in s:
        return "done"
    if "partial" in s:
        return "partial"
    if "blocked" in s:
        return "todo"
    return "next"


def get_system_skills():
    return [
        ("db-migration-resolver", "Detects & resolves Alembic migration conflicts"),
        ("smart-onboarding", "AI Engineer Smart Onboarding Command"),
        ("dashboard", "Generate dynamic project status dashboard"),
        ("update-config", "Configure Claude Code harness via settings.json"),
        ("keybindings-help", "Customize keyboard shortcuts"),
        ("verify", "Verify code changes work by running app"),
        ("code-review", "Review current diff for correctness bugs"),
        ("fewer-permission-prompts", "Reduce permission prompts via allowlist"),
        ("loop", "Run prompt/command on recurring interval"),
        ("schedule", "Create scheduled remote agents (cron jobs)"),
        ("claude-api", "Build & optimize Claude API applications"),
        ("run", "Launch & drive project app"),
        ("init", "Initialize new CLAUDE.md"),
        ("review", "Review a pull request"),
        ("security-review", "Security review of pending changes"),
    ]


def get_custom_hooks_and_commands():
    root = get_project_root()

    hooks_info = read_hooks_from_directory()

    commands = []
    commands_dir = root / ".claude" / "commands"
    if commands_dir.exists():
        for cmd_file in commands_dir.glob("*.md"):
            commands.append(cmd_file.stem)

    return hooks_info, commands


def build_html_dashboard():
    # Get all data
    system_skills = get_system_skills()
    custom_hooks, custom_commands = get_custom_hooks_and_commands()

    # Build tables
    system_skills_html = "\n".join(
        [
            f"<tr><td><strong>{skill}</strong></td><td>{desc[:80]}</td></tr>"
            for skill, desc in system_skills
        ]
    )

    custom_hooks_html = "\n".join(
        [
            f"<tr><td><strong>{name}</strong></td><td>{purpose[:80]}</td></tr>"
            for name, purpose in sorted(custom_hooks.items())
        ]
    )

    custom_commands_html = "\n".join(
        [
            f"<tr><td><strong>{cmd}</strong></td><td>Custom slash command</td></tr>"
            for cmd in sorted(custom_commands)
        ]
    )

    gen_time = datetime.now().strftime("%b %d, %Y at %H:%M")

    # § 0 dynamic block — parsed from feature.md so the dashboard reflects doc updates.
    section_zero_rows = parse_feature_section_zero()
    if section_zero_rows:
        section_zero_html = "\n".join(
            f'<li class="status-item {classify_status(r["status"])}">'
            f'<span><strong>{r["requirement"]}</strong> — {r["notes"]}</span>'
            f'<span class="status-badge {classify_status(r["status"])}">{r["status"]}</span>'
            f"</li>"
            for r in section_zero_rows
        )
        done_count = sum(
            1 for r in section_zero_rows if classify_status(r["status"]) == "done"
        )
        section_zero_header_status = (
            f"All {len(section_zero_rows)} shipped ✓"
            if done_count == len(section_zero_rows)
            else f"{done_count} / {len(section_zero_rows)} shipped"
        )
    else:
        section_zero_html = (
            '<li class="status-item next"><span>§0 table not found in feature.md</span>'
            '<span class="status-badge next">Check docs</span></li>'
        )
        section_zero_header_status = "unknown"

    # ── Full doc-driven feature lists (Completed / Gaps tabs) ───────────────────
    all_rows = parse_all_status_rows()

    # Group by doc → section for readability.
    def _render_row(r: dict) -> str:
        loc = f"<span style='font-size:0.72em;color:#6b7280;font-weight:500;margin-left:6px;'>[{r['doc']} · {r['section'][:32]}]</span>"
        return (
            f'<li class="status-item {r["status_class"]}">'
            f'<span><strong>{r["item"]}</strong>{loc}'
            f'{("<br/><span style=\"font-size:0.85em;color:#4b5563;\">" + r["notes"] + "</span>") if r["notes"] else ""}'
            f"</span>"
            f'<span class="status-badge {r["status_class"]}">{r["status_raw"]}</span>'
            f"</li>"
        )

    completed_rows = [r for r in all_rows if r["status_class"] == "done"]
    gaps_rows = [r for r in all_rows if r["status_class"] != "done"]
    completed_html = "\n".join(_render_row(r) for r in completed_rows)
    gaps_html = "\n".join(_render_row(r) for r in gaps_rows)
    completed_count = len(completed_rows)
    gaps_count = len(gaps_rows)

    # Component Health row for Reminders / Voice is now also derived from § 0 status.
    reminders_status_class = (
        "done"
        if all(classify_status(r["status"]) == "done" for r in section_zero_rows)
        and section_zero_rows
        else "partial"
    )
    reminders_status_label = (
        "Shipped" if reminders_status_class == "done" else "Partial"
    )
    reminders_notes = (
        "Scheduler + §0 dialogue (time / offset / mic / TTS) all shipped"
        if reminders_status_class == "done"
        else "Scheduler/WS shipped; §0 dialogue TBD"
    )

    # Build complete HTML
    html = (
        """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Assistant - Project Status Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { scroll-behavior: smooth; }
        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 24px;
            color: #1f2937;
        }
        .container { max-width: 1400px; margin: 0 auto; }

        /* ── HEADER ── */
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
            padding: 48px 44px 44px;
            border-radius: 18px;
            margin-bottom: 24px;
            box-shadow: 0 20px 50px rgba(102,126,234,0.35);
            position: relative;
            overflow: hidden;
        }
        header::before {
            content: '';
            position: absolute;
            top: -80px; right: -80px;
            width: 380px; height: 380px;
            background: radial-gradient(circle, rgba(255,255,255,0.18) 0%, transparent 65%);
            border-radius: 50%;
            animation: pulse-glow 5s ease-in-out infinite;
            pointer-events: none;
        }
        header::after {
            content: '';
            position: absolute;
            bottom: -70px; left: -50px;
            width: 260px; height: 260px;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            border-radius: 50%;
            animation: pulse-glow 5s ease-in-out 2.5s infinite;
            pointer-events: none;
        }
        @keyframes pulse-glow {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.6; }
        }
        .header-content { position: relative; z-index: 1; }
        header h1 {
            color: white;
            margin-bottom: 10px;
            font-size: 2.8em;
            font-weight: 800;
            letter-spacing: -0.8px;
        }
        header p.header-subtitle {
            color: rgba(255,255,255,0.88);
            font-size: 1.05em;
            font-weight: 500;
            margin-bottom: 16px;
        }
        .header-tagline-badge {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            background: rgba(255,255,255,0.16);
            border: 1px solid rgba(255,255,255,0.30);
            color: rgba(255,255,255,0.95);
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.82em;
            font-weight: 600;
            letter-spacing: 0.3px;
        }
        .header-tagline-badge svg { width: 13px; height: 13px; vertical-align: middle; }
        .header-meta {
            position: absolute;
            bottom: 26px; right: 38px;
            z-index: 1;
            text-align: right;
        }
        .header-meta .gen-label {
            color: rgba(255,255,255,0.52);
            font-size: 0.70em;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            display: block;
            margin-bottom: 3px;
        }
        .header-meta .gen-time {
            color: rgba(255,255,255,0.92);
            font-size: 0.90em;
            font-weight: 700;
        }

        /* ── SUMMARY CARDS ── */
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }
        .summary-card {
            background: white;
            padding: 20px 20px 16px;
            border-radius: 16px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.06);
            border: 1.5px solid #f3f4f6;
            position: relative;
            cursor: pointer;
            user-select: none;
            transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1);
            overflow: hidden;
        }
        .summary-card::after {
            content: '';
            position: absolute;
            bottom: 0; left: 0; right: 0;
            height: 3px;
            border-radius: 0 0 14px 14px;
            opacity: 0;
            transition: opacity 0.25s ease;
        }
        .summary-card:hover { transform: translateY(-7px); box-shadow: 0 18px 40px rgba(0,0,0,0.12); }
        .summary-card:hover::after { opacity: 1; }
        .card-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 14px;
        }
        .card-icon-badge {
            width: 38px; height: 38px;
            border-radius: 11px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .card-icon-badge svg { width: 18px; height: 18px; }
        .card-label {
            font-size: 0.72em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.6px;
            color: #9ca3af;
        }
        .card-number {
            font-size: 2.9em;
            font-weight: 900;
            line-height: 1;
            letter-spacing: -1.5px;
            margin-bottom: 5px;
        }
        .card-desc {
            font-size: 0.80em;
            color: #9ca3af;
            font-weight: 500;
            margin-bottom: 14px;
            line-height: 1.4;
        }
        .card-footer {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .card-progress-bar {
            flex: 1;
            height: 4px;
            background: #f3f4f6;
            border-radius: 2px;
            overflow: hidden;
        }
        .card-progress-fill {
            height: 100%;
            border-radius: 2px;
            width: 0;
            transition: width 1.1s cubic-bezier(0.4,0,0.2,1) 0.3s;
        }
        .card-pct {
            font-size: 0.70em;
            font-weight: 700;
            color: #b0b8c4;
            white-space: nowrap;
        }
        .card-cta {
            display: block;
            margin-top: 12px;
            font-size: 0.71em;
            font-weight: 700;
            letter-spacing: 0.4px;
            text-transform: uppercase;
            opacity: 0;
            transform: translateY(4px);
            transition: all 0.2s ease;
        }
        .summary-card:hover .card-cta { opacity: 1; transform: translateY(0); }

        .summary-card.done   { border-color: #d1fae5; }
        .summary-card.done::after { background: #10b981; }
        .summary-card.done   .card-icon-badge { background: #d1fae5; color: #059669; }
        .summary-card.done   .card-number { color: #059669; }
        .summary-card.done   .card-progress-fill { background: #10b981; }
        .summary-card.done   .card-cta { color: #059669; }

        .summary-card.partial { border-color: #fef3c7; }
        .summary-card.partial::after { background: #f59e0b; }
        .summary-card.partial .card-icon-badge { background: #fef3c7; color: #d97706; }
        .summary-card.partial .card-number { color: #d97706; }
        .summary-card.partial .card-progress-fill { background: #f59e0b; }
        .summary-card.partial .card-cta { color: #d97706; }

        .summary-card.todo   { border-color: #fee2e2; }
        .summary-card.todo::after { background: #ef4444; }
        .summary-card.todo   .card-icon-badge { background: #fee2e2; color: #dc2626; }
        .summary-card.todo   .card-number { color: #dc2626; }
        .summary-card.todo   .card-progress-fill { background: #ef4444; }
        .summary-card.todo   .card-cta { color: #dc2626; }

        .summary-card.next   { border-color: #dbeafe; }
        .summary-card.next::after { background: #3b82f6; }
        .summary-card.next   .card-icon-badge { background: #dbeafe; color: #1d4ed8; }
        .summary-card.next   .card-number { color: #1d4ed8; }
        .summary-card.next   .card-progress-fill { background: #3b82f6; }
        .summary-card.next   .card-cta { color: #1d4ed8; }

        /* dark overrides for new card structure */
        body.dark .summary-card { background: #1f2937; border-color: #374151; }
        body.dark .summary-card.done    { border-color: #065f46; }
        body.dark .summary-card.partial { border-color: #78350f; }
        body.dark .summary-card.todo    { border-color: #7f1d1d; }
        body.dark .summary-card.next    { border-color: #1e3a8a; }
        body.dark .summary-card.done    .card-icon-badge { background: #052e16; color: #34d399; }
        body.dark .summary-card.partial .card-icon-badge { background: #2d1a00; color: #fbbf24; }
        body.dark .summary-card.todo    .card-icon-badge { background: #2d0a0a; color: #f87171; }
        body.dark .summary-card.next    .card-icon-badge { background: #0c1a3d; color: #60a5fa; }
        body.dark .card-desc { color: #6b7280; }
        body.dark .card-progress-bar { background: #374151; }

        /* ── TABS ── */
        .tabs {
            display: flex;
            gap: 2px;
            margin-bottom: 24px;
            flex-wrap: wrap;
            background: white;
            padding: 6px;
            border-radius: 14px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.07);
        }
        .tab-button {
            background: transparent;
            border: none;
            padding: 10px 15px;
            border-radius: 9px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s ease;
            color: #6b7280;
            font-size: 0.87em;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            position: relative;
            white-space: nowrap;
        }
        .tab-button svg { width: 14px; height: 14px; flex-shrink: 0; opacity: 0.7; }
        .tab-button:hover { color: #667eea; background: #f3f4f6; }
        .tab-button:hover svg { opacity: 1; }
        .tab-button.active { color: #667eea; background: #eef2ff; font-weight: 700; }
        .tab-button.active svg { opacity: 1; }
        .tab-button.active::after {
            content: '';
            position: absolute;
            bottom: 2px; left: 10px; right: 10px;
            height: 2px;
            background: #667eea;
            border-radius: 2px;
        }
        .tab-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: #f3f4f6;
            color: #6b7280;
            font-size: 0.68em;
            font-weight: 800;
            padding: 1px 6px;
            border-radius: 8px;
            min-width: 20px;
            transition: all 0.2s ease;
        }
        .tab-button.active .tab-badge { background: #c7d2fe; color: #3730a3; }

        /* ── TAB STICKY HEADER ── */
        .tab-sticky-header {
            position: sticky;
            top: 12px;
            z-index: 50;
            background: rgba(255,255,255,0.92);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 11px;
            padding: 11px 20px;
            margin-bottom: 18px;
            box-shadow: 0 4px 18px rgba(0,0,0,0.09);
            display: flex;
            align-items: center;
            justify-content: space-between;
            border: 1px solid rgba(229,231,235,0.9);
        }
        .tab-sticky-left { display:flex; align-items:center; gap:10px; }
        .tab-sticky-dot { width:10px; height:10px; border-radius:50%; background:#667eea; }
        .tab-sticky-title { font-size:0.98em; font-weight:700; color:#1f2937; }
        .tab-sticky-count {
            font-size: 0.80em;
            color: #6b7280;
            background: #f3f4f6;
            padding: 3px 12px;
            border-radius: 20px;
            font-weight: 600;
        }

        /* ── SECTIONS ── */
        .section {
            background: white;
            padding: 28px 30px;
            border-radius: 14px;
            margin-bottom: 20px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border-left: 4px solid #667eea;
        }
        .section h2 {
            color: #1f2937;
            margin-bottom: 20px;
            font-size: 1.3em;
            padding-bottom: 14px;
            border-bottom: 1px solid #f3f4f6;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .section h2::before {
            content: '';
            display: inline-block;
            width: 11px; height: 11px;
            background: #667eea;
            border-radius: 50%;
            flex-shrink: 0;
        }
        .section h3 { color:#374151; margin-top:22px; margin-bottom:12px; font-size:1.0em; font-weight:700; }

        /* ── STATUS ITEMS ── */
        .status-list { list-style: none; }
        .status-item {
            padding: 12px 16px 12px 38px;
            margin-bottom: 9px;
            border-radius: 9px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            transition: all 0.2s ease;
            position: relative;
            border: 1px solid transparent;
        }
        .status-item::before {
            content: '';
            position: absolute;
            left: 14px; top: 50%;
            transform: translateY(-50%);
            width: 8px; height: 8px;
            border-radius: 50%;
        }
        .status-item:hover { transform: translateX(5px); box-shadow: 0 2px 10px rgba(0,0,0,0.07); }
        .status-item.done    { background:#f0fdf4; border-color:#d1fae5; }
        .status-item.done::before    { background:#10b981; box-shadow:0 0 0 3px rgba(16,185,129,0.2); }
        .status-item.partial { background:#fffbef; border-color:#fde68a; }
        .status-item.partial::before { background:#f59e0b; box-shadow:0 0 0 3px rgba(245,158,11,0.2); }
        .status-item.todo    { background:#fef2f2; border-color:#fecaca; }
        .status-item.todo::before    { background:#ef4444; box-shadow:0 0 0 3px rgba(239,68,68,0.2); }
        .status-item.next    { background:#eff6ff; border-color:#bfdbfe; }
        .status-item.next::before    { background:#3b82f6; box-shadow:0 0 0 3px rgba(59,130,246,0.2); }

        /* ── BADGES ── */
        .status-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 78px;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75em;
            font-weight: 700;
            text-transform: uppercase;
            white-space: nowrap;
            letter-spacing: 0.5px;
            flex-shrink: 0;
        }
        .status-badge.done    { background:#d1fae5; color:#065f46; }
        .status-badge.partial { background:#fef3c7; color:#92400e; }
        .status-badge.todo    { background:#fee2e2; color:#991b1b; }
        .status-badge.next    { background:#dbeafe; color:#1e3a8a; }

        /* ── TABLES ── */
        .feature-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 18px;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #e5e7eb;
        }
        .feature-table th {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 13px 16px;
            text-align: left;
            font-weight: 700;
            color: white;
            font-size: 0.81em;
            text-transform: uppercase;
            letter-spacing: 0.7px;
        }
        .feature-table tbody tr:nth-child(odd)  { background: #ffffff; }
        .feature-table tbody tr:nth-child(even) { background: #f9fafb; }
        .feature-table td {
            padding: 13px 16px;
            border-bottom: 1px solid #f3f4f6;
            color: #374151;
            font-size: 0.93em;
        }
        .feature-table tbody tr:hover td { background: #eef2ff; transition: background 0.15s ease; }
        .feature-table tr:last-child td { border-bottom: none; }

        /* ── ANIMATIONS ── */
        .content { display: none; }
        .content.active { display: block; animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:translateY(0); } }

        /* ── THEME TOGGLE BUTTON ── */
        .theme-toggle {
            position: absolute;
            top: 20px; right: 20px;
            z-index: 10;
            background: rgba(255,255,255,0.18);
            border: 1px solid rgba(255,255,255,0.30);
            color: white;
            width: 40px; height: 40px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.25s ease;
        }
        .theme-toggle:hover { background: rgba(255,255,255,0.30); transform: scale(1.12); }
        .theme-toggle svg { width: 18px; height: 18px; }
        .icon-moon { display: block; }
        .icon-sun  { display: none; }

        /* ── BADGE VISIBILITY (light + dark) ── */
        .status-badge.done    { background:#166534; color:#bbf7d0; border:1px solid #16a34a; }
        .status-badge.partial { background:#78350f; color:#fde68a; border:1px solid #d97706; }
        .status-badge.todo    { background:#7f1d1d; color:#fecaca; border:1px solid #dc2626; }
        .status-badge.next    { background:#1e3a8a; color:#bfdbfe; border:1px solid #2563eb; }

        /* ── DARK MODE ── */
        body.dark {
            background: #0d1117;
            color: #c9d1d9;
        }
        body.dark .container > * { transition: background 0.3s, border-color 0.3s; }
        body.dark .theme-toggle { background: #21262d; border-color: #30363d; color: #58a6ff; }
        body.dark .theme-toggle:hover { background: #30363d; }
        body.dark .icon-moon { display: none; }
        body.dark .icon-sun  { display: block; }

        /* header stays same gradient — looks great on dark */

        /* cards */
        body.dark .summary-card { background: #161b22; border-color: #30363d; box-shadow: 0 0 0 1px #30363d; }
        body.dark .summary-card:hover { box-shadow: 0 8px 32px rgba(0,0,0,0.6); }
        body.dark .summary-card.done    { border-color: #238636; box-shadow: 0 0 0 1px #238636, 0 0 20px rgba(35,134,54,0.12); }
        body.dark .summary-card.partial { border-color: #d29922; box-shadow: 0 0 0 1px #d29922, 0 0 20px rgba(210,153,34,0.12); }
        body.dark .summary-card.todo    { border-color: #f85149; box-shadow: 0 0 0 1px #f85149, 0 0 20px rgba(248,81,73,0.12); }
        body.dark .summary-card.next    { border-color: #1f6feb; box-shadow: 0 0 0 1px #1f6feb, 0 0 20px rgba(31,111,235,0.12); }
        body.dark .summary-card.done    .card-icon-badge { background: #0d2818; color: #3fb950; }
        body.dark .summary-card.partial .card-icon-badge { background: #2d1900; color: #e3b341; }
        body.dark .summary-card.todo    .card-icon-badge { background: #2a0a0a; color: #ff7b72; }
        body.dark .summary-card.next    .card-icon-badge { background: #0a1f3d; color: #58a6ff; }
        body.dark .summary-card.done    .card-number { color: #3fb950; }
        body.dark .summary-card.partial .card-number { color: #e3b341; }
        body.dark .summary-card.todo    .card-number { color: #ff7b72; }
        body.dark .summary-card.next    .card-number { color: #58a6ff; }
        body.dark .summary-card.done    .card-cta { color: #3fb950; }
        body.dark .summary-card.partial .card-cta { color: #e3b341; }
        body.dark .summary-card.todo    .card-cta { color: #ff7b72; }
        body.dark .summary-card.next    .card-cta { color: #58a6ff; }
        body.dark .summary-card.done    ::after { background: #3fb950; }
        body.dark .summary-card.partial ::after { background: #e3b341; }
        body.dark .summary-card.todo    ::after { background: #ff7b72; }
        body.dark .summary-card.next    ::after { background: #58a6ff; }
        body.dark .card-label { color: #8b949e; }
        body.dark .card-desc  { color: #8b949e; }
        body.dark .card-pct   { color: #6e7681; }
        body.dark .card-progress-bar { background: #21262d; }

        /* tabs */
        body.dark .tabs { background: #161b22; border: 1px solid #30363d; box-shadow: none; }
        body.dark .tab-button { color: #8b949e; }
        body.dark .tab-button:hover { background: #21262d; color: #c9d1d9; }
        body.dark .tab-button.active { background: #0d2035; color: #58a6ff; font-weight: 700; }
        body.dark .tab-button.active::after { background: #58a6ff; }
        body.dark .tab-badge { background: #21262d; color: #8b949e; border: 1px solid #30363d; }
        body.dark .tab-button.active .tab-badge { background: #0d2035; color: #58a6ff; border-color: #1f6feb; }

        /* sticky header */
        body.dark .tab-sticky-header { background: rgba(13,17,23,0.95); border-color: #30363d; box-shadow: 0 1px 0 #30363d; }
        body.dark .tab-sticky-title  { color: #f0f6fc; }
        body.dark .tab-sticky-count  { background: #21262d; color: #8b949e; border: 1px solid #30363d; }

        /* sections */
        body.dark .section { background: #161b22; border-left-color: #388bfd; box-shadow: 0 1px 0 #30363d; }
        body.dark .section h2 { color: #f0f6fc; border-bottom-color: #21262d; }
        body.dark .section h2::before { background: #388bfd; }
        body.dark .section h3 { color: #c9d1d9; }
        body.dark .section p  { color: #8b949e !important; }

        /* status items */
        body.dark .status-item.done    { background: #0d2818; border-color: #238636; }
        body.dark .status-item.done::before    { background: #3fb950; box-shadow: 0 0 0 3px rgba(63,185,80,0.25); }
        body.dark .status-item.partial { background: #2d1900; border-color: #d29922; }
        body.dark .status-item.partial::before { background: #e3b341; box-shadow: 0 0 0 3px rgba(227,179,65,0.25); }
        body.dark .status-item.todo    { background: #2a0a0a; border-color: #f85149; }
        body.dark .status-item.todo::before    { background: #ff7b72; box-shadow: 0 0 0 3px rgba(255,123,114,0.25); }
        body.dark .status-item.next    { background: #0a1f3d; border-color: #1f6feb; }
        body.dark .status-item.next::before    { background: #58a6ff; box-shadow: 0 0 0 3px rgba(88,166,255,0.25); }
        body.dark .status-item span    { color: #c9d1d9; }
        body.dark .status-item:hover   { box-shadow: 0 2px 12px rgba(0,0,0,0.4); }

        /* badges — bright solid in dark mode */
        body.dark .status-badge.done    { background: #0d2818; color: #3fb950; border-color: #238636; }
        body.dark .status-badge.partial { background: #2d1900; color: #e3b341; border-color: #d29922; }
        body.dark .status-badge.todo    { background: #2a0a0a; color: #ff7b72; border-color: #f85149; }
        body.dark .status-badge.next    { background: #0a1f3d; color: #58a6ff; border-color: #1f6feb; }

        /* tables */
        body.dark .feature-table { border-color: #30363d; }
        body.dark .feature-table th { background: #21262d; color: #c9d1d9; letter-spacing: 0.8px; }
        body.dark .feature-table tbody tr:nth-child(odd)  { background: #161b22; }
        body.dark .feature-table tbody tr:nth-child(even) { background: #0d1117; }
        body.dark .feature-table td { color: #c9d1d9; border-bottom-color: #21262d; }
        body.dark .feature-table tbody tr:hover td { background: #1c2d44 !important; }

        /* ── RESPONSIVE ── */
        @media (max-width: 1100px) { .summary-grid { grid-template-columns: repeat(2,1fr); } }
        @media (max-width: 768px) {
            header { padding: 36px 24px 80px; }
            header h1 { font-size: 1.9em; }
            .header-meta { bottom: 20px; right: 24px; }
            .summary-grid { grid-template-columns: repeat(2,1fr); gap:14px; }
            .tab-button { font-size:0.82em; padding:9px 11px; }
            .section { padding: 20px; }
        }
        @media (max-width: 480px) {
            .summary-grid { grid-template-columns: 1fr; }
            .tabs { flex-direction: column; }
            .tab-button { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <button class="theme-toggle" onclick="toggleTheme()" title="Toggle dark / light mode">
                <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                <svg class="icon-sun"  viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
            </button>
            <div class="header-content">
                <h1>AI Assistant &mdash; Project Status Dashboard</h1>
                <p class="header-subtitle">Auto-generated technical dashboard with persistent version history</p>
                <span class="header-tagline-badge">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="22"/></svg>
                    AI Reminder Assistant
                </span>
            </div>
            <div class="header-meta">
                <span class="gen-label">Generated</span>
                <span class="gen-time">"""
        + gen_time
        + """</span>
            </div>
        </header>

        <div class="summary-grid">
            <div class="summary-card done" onclick="navigateToTab('completed')" title="View completed features">
                <div class="card-top">
                    <div class="card-icon-badge">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                    </div>
                    <span class="card-label">Completed</span>
                </div>
                <div class="card-number">13</div>
                <div class="card-desc">Features shipped end-to-end</div>
                <div class="card-footer">
                    <div class="card-progress-bar"><div class="card-progress-fill" data-pct="45"></div></div>
                    <span class="card-pct">45%</span>
                </div>
                <span class="card-cta">View all &rarr;</span>
            </div>
            <div class="summary-card partial" onclick="navigateToTab('gaps')" title="View partial implementations">
                <div class="card-top">
                    <div class="card-icon-badge">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M2 12h20"/><circle cx="12" cy="12" r="10"/></svg>
                    </div>
                    <span class="card-label">Partial</span>
                </div>
                <div class="card-number">5</div>
                <div class="card-desc">Core exists, gaps remain</div>
                <div class="card-footer">
                    <div class="card-progress-bar"><div class="card-progress-fill" data-pct="17"></div></div>
                    <span class="card-pct">17%</span>
                </div>
                <span class="card-cta">View gaps &rarr;</span>
            </div>
            <div class="summary-card todo" onclick="navigateToTab('gaps')" title="View todo items">
                <div class="card-top">
                    <div class="card-icon-badge">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
                    </div>
                    <span class="card-label">Todo</span>
                </div>
                <div class="card-number">8</div>
                <div class="card-desc">Not yet implemented</div>
                <div class="card-footer">
                    <div class="card-progress-bar"><div class="card-progress-fill" data-pct="28"></div></div>
                    <span class="card-pct">28%</span>
                </div>
                <span class="card-cta">View todos &rarr;</span>
            </div>
            <div class="summary-card next" onclick="navigateToTab('roadmap')" title="View priority roadmap">
                <div class="card-top">
                    <div class="card-icon-badge">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
                    </div>
                    <span class="card-label">Priority Next</span>
                </div>
                <div class="card-number">3</div>
                <div class="card-desc">Logical next increment</div>
                <div class="card-footer">
                    <div class="card-progress-bar"><div class="card-progress-fill" data-pct="10"></div></div>
                    <span class="card-pct">10%</span>
                </div>
                <span class="card-cta">View roadmap &rarr;</span>
            </div>
        </div>

        <div class="tabs">
            <button class="tab-button active" data-tab="overview" onclick="showTab(event, 'overview')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
                Overview
            </button>
            <button class="tab-button" data-tab="completed" onclick="showTab(event, 'completed')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                Completed <span class="tab-badge">{{COMPLETED_COUNT}}</span>
            </button>
            <button class="tab-button" data-tab="gaps" onclick="showTab(event, 'gaps')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                Gaps &amp; Partials <span class="tab-badge">{{GAPS_COUNT}}</span>
            </button>
            <button class="tab-button" data-tab="roadmap" onclick="showTab(event, 'roadmap')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
                Roadmap <span class="tab-badge">3</span>
            </button>
            <button class="tab-button" data-tab="frontend" onclick="showTab(event, 'frontend')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
                Frontend
            </button>
            <button class="tab-button" data-tab="backend" onclick="showTab(event, 'backend')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>
                Backend
            </button>
            <button class="tab-button" data-tab="hooks" onclick="showTab(event, 'hooks')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
                Hooks &amp; Skills <span class="tab-badge">29</span>
            </button>
        </div>

        <!-- OVERVIEW TAB -->
        <div id="overview" class="content active">
            <div class="tab-sticky-header">
                <div class="tab-sticky-left"><div class="tab-sticky-dot"></div><span class="tab-sticky-title">Overview</span></div>
                <span class="tab-sticky-count">Project health at a glance</span>
            </div>
            <div class="section">
                <h2>Project Summary</h2>
                <p style="margin-bottom: 20px; color: #666; line-height: 1.6;">
                    This is a <strong>voice-first AI assistant</strong> for managing reminders, tasks, events, and activity. The MVP is substantially complete with core voice pipeline, clarification loops, reminder scheduling, and real-time updates shipped. The next phase focuses on enhancing the <strong>§0 reminder dialogue</strong> (time capture → early offset offer → TTS-at-fire → mic auto-stop) plus profile/settings, event edit UI, and edge-case resilience.
                </p>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px;">
                    <div>
                        <h3>MVP Status</h3>
                        <ul class="status-list">
                            <li class="status-item done"><span>Core Voice Pipeline</span><span class="status-badge done">Done</span></li>
                            <li class="status-item done"><span>Clarification Sessions</span><span class="status-badge done">Done</span></li>
                            <li class="status-item done"><span>Reminder Scheduler + WS</span><span class="status-badge done">Done</span></li>
                            <li class="status-item done"><span>Auth + JWT Refresh</span><span class="status-badge done">Done</span></li>
                            <li class="status-item done"><span>Dashboard + All CRUD APIs</span><span class="status-badge done">Done</span></li>
                        </ul>
                    </div>

                    <div>
                        <h3>§0 Conversational Reminders <span style="font-size:0.6em;color:#6b7280;font-weight:500;">("""
        + section_zero_header_status
        + """)</span></h3>
                        <ul class="status-list">
                            """
        + section_zero_html
        + """
                        </ul>
                    </div>
                </div>

                <h2>Component Health by Domain</h2>
                <table class="feature-table">
                    <thead>
                        <tr>
                            <th>Domain</th>
                            <th>Backend</th>
                            <th>Frontend</th>
                            <th>Status</th>
                            <th>Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Authentication</strong></td>
                            <td><span class="status-badge done">Done</span></td>
                            <td><span class="status-badge done">Done</span></td>
                            <td><span class="status-badge done">Shipped</span></td>
                            <td>JWT + refresh, protected routes</td>
                        </tr>
                        <tr>
                            <td><strong>Voice</strong></td>
                            <td><span class="status-badge done">Done</span></td>
                            <td><span class="status-badge done">Done</span></td>
                            <td><span class="status-badge done">Shipped</span></td>
                            <td>STT/TTS/intent/executor, clarification loops</td>
                        </tr>
                        <tr>
                            <td><strong>Tasks</strong></td>
                            <td><span class="status-badge done">Done</span></td>
                            <td><span class="status-badge done">Done</span></td>
                            <td><span class="status-badge done">Shipped</span></td>
                            <td>Full CRUD via API + panel</td>
                        </tr>
                        <tr>
                            <td><strong>Events</strong></td>
                            <td><span class="status-badge done">Done</span></td>
                            <td><span class="status-badge partial">Partial</span></td>
                            <td><span class="status-badge partial">Partial</span></td>
                            <td>API complete; UI lacks edit wiring</td>
                        </tr>
                        <tr>
                            <td><strong>Reminders</strong></td>
                            <td><span class="status-badge """
        + reminders_status_class
        + """\">"""
        + ("Done" if reminders_status_class == "done" else "Partial")
        + """</span></td>
                            <td><span class="status-badge """
        + reminders_status_class
        + """\">"""
        + ("Done" if reminders_status_class == "done" else "Partial")
        + """</span></td>
                            <td><span class="status-badge """
        + reminders_status_class
        + """\">"""
        + reminders_status_label
        + """</span></td>
                            <td>"""
        + reminders_notes
        + """</td>
                        </tr>
                        <tr>
                            <td><strong>Real-time</strong></td>
                            <td><span class="status-badge done">Done</span></td>
                            <td><span class="status-badge done">Done</span></td>
                            <td><span class="status-badge done">Shipped</span></td>
                            <td>WS + APScheduler + toast/chime</td>
                        </tr>
                        <tr>
                            <td><strong>Activity</strong></td>
                            <td><span class="status-badge done">Done</span></td>
                            <td><span class="status-badge done">Done</span></td>
                            <td><span class="status-badge done">Shipped</span></td>
                            <td>Query + panel with clear option</td>
                        </tr>
                        <tr>
                            <td><strong>Profile/Settings</strong></td>
                            <td><span class="status-badge partial">Partial</span></td>
                            <td><span class="status-badge partial">Partial</span></td>
                            <td><span class="status-badge partial">Partial</span></td>
                            <td>Name + email only; timezone/prefs missing</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- COMPLETED TAB -->
        <div id="completed" class="content">
            <div class="tab-sticky-header">
                <div class="tab-sticky-left"><div class="tab-sticky-dot" style="background:#10b981"></div><span class="tab-sticky-title">Completed Features</span></div>
                <span class="tab-sticky-count">13 features shipped end-to-end</span>
            </div>
            <div class="section">
                <h2>Completed Features <span style="font-size:0.55em;color:#6b7280;font-weight:500;">(parsed from feature.md + project_status.md)</span></h2>
                <ul class="status-list">{{COMPLETED_ROWS}}</ul>
            </div>
        </div>

        <!-- GAPS & PARTIALS TAB -->
        <div id="gaps" class="content">
            <div class="tab-sticky-header">
                <div class="tab-sticky-left"><div class="tab-sticky-dot" style="background:#f59e0b"></div><span class="tab-sticky-title">Gaps &amp; Partials</span></div>
                <span class="tab-sticky-count">5 partial + 8 todo = 13 items remaining</span>
            </div>
            <div class="section">
                <h2>Gaps &amp; Partial Implementation <span style="font-size:0.55em;color:#6b7280;font-weight:500;">(parsed from feature.md + project_status.md)</span></h2>
                <ul class="status-list">{{GAPS_ROWS}}</ul>
            </div>
        </div>

        <!-- ROADMAP TAB -->
        <div id="roadmap" class="content">
            <div class="tab-sticky-header">
                <div class="tab-sticky-left"><div class="tab-sticky-dot" style="background:#3b82f6"></div><span class="tab-sticky-title">Priority Roadmap</span></div>
                <span class="tab-sticky-count">3 phases &mdash; §0 is the critical path</span>
            </div>
            <div class="section">
                <h2>Priority Roadmap</h2>
                <h3 style="color: #667eea; font-weight: 700;">Phase 1: §0 Conversational Reminders (CRITICAL)</h3>
                <p style="margin-bottom: 15px; color: #666;">This is the MVP's north star. Focus all voice/reminder work here until user acceptance complete.</p>
                <ul class="status-list">
                    <li class="status-item next"><span>1. Time capture dialogue - Enhance intent_parser to detect "time missing"</span><span class="status-badge next">Next</span></li>
                    <li class="status-item next"><span>2. Early offset offer - Branch to offset clarification after time resolved</span><span class="status-badge next">Next</span></li>
                    <li class="status-item next"><span>3. Mic auto-stop - Client detects terminal success → idle state</span><span class="status-badge next">Next</span></li>
                    <li class="status-item next"><span>4. TTS at fire - WS payload includes response_audio URL + text</span><span class="status-badge next">Next</span></li>
                    <li class="status-item next"><span>5. Acceptance tests - Validate example scripts from feature.md §0</span><span class="status-badge next">Next</span></li>
                </ul>

                <h3 style="color: #667eea; font-weight: 700; margin-top: 30px;">Phase 2: Profile Expansion & Event Edit (NEXT AFTER §0)</h3>
                <ul class="status-list">
                    <li class="status-item next"><span>1. Timezone selector - Add timezone field + Profile.tsx picker</span><span class="status-badge next">Next</span></li>
                    <li class="status-item next"><span>2. User preferences - Define MVP prefs (voice tone, notification style)</span><span class="status-badge next">Next</span></li>
                    <li class="status-item next"><span>3. Event edit UI - Wire SchedulePanel edit button → form modal</span><span class="status-badge next">Next</span></li>
                    <li class="status-item next"><span>4. Test & iterate - Cross-browser testing, timezone handling</span><span class="status-badge next">Next</span></li>
                </ul>

                <h3 style="color: #667eea; font-weight: 700; margin-top: 30px;">Phase 3: Edge Cases & Resilience (PARALLEL)</h3>
                <ul class="status-list">
                    <li class="status-item next"><span>1. Timeout handling - Add "taking longer..." skeleton + auto-retry</span><span class="status-badge next">Next</span></li>
                    <li class="status-item next"><span>2. Rate limit UX - Standardize 429 error + retry-after parsing</span><span class="status-badge next">Next</span></li>
                    <li class="status-item next"><span>3. 422 logging - Suppress validation errors from INFO stream</span><span class="status-badge next">Next</span></li>
                    <li class="status-item next"><span>4. High-confidence pre-confirm - Gate destructive actions with UX confirm</span><span class="status-badge next">Next</span></li>
                </ul>
            </div>
        </div>

        <!-- FRONTEND TAB -->
        <div id="frontend" class="content">
            <div class="tab-sticky-header">
                <div class="tab-sticky-left"><div class="tab-sticky-dot" style="background:#8b5cf6"></div><span class="tab-sticky-title">Frontend Status</span></div>
                <span class="tab-sticky-count">React 18 &bull; TypeScript &bull; Vite &bull; shadcn/ui</span>
            </div>
            <div class="section">
                <h2>Frontend Status</h2>
                <h3>Done</h3>
                <ul class="status-list">
                    <li class="status-item done"><span>MicButton + useVoiceAssistantFlow orchestration</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>ResultCard (success / clarification / error variants)</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>Home dashboard (Index.tsx) with all panels</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>TaskPanel, SchedulePanel, RemindersPanel, ActivityPanel</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>useRemindersWebSocket hook + toast alerts</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>Loading skeletons for all major panels</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>Dark mode toggle (AppThemeProvider + localStorage)</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>React 18 + Vite + TypeScript strict mode</span><span class="status-badge done">Done</span></li>
                </ul>
                <h3>Partial</h3>
                <ul class="status-list">
                    <li class="status-item partial"><span>Profile page: Shows name + email; no timezone/preferences UI</span><span class="status-badge partial">Partial</span></li>
                </ul>
                <h3>Todo / Next</h3>
                <ul class="status-list">
                    <li class="status-item next"><span>Schedule edit: SchedulePanel needs edit button + modal</span><span class="status-badge next">Next</span></li>
                    <li class="status-item next"><span>§0 Mic auto-stop: Auto-idle after terminal reminder success</span><span class="status-badge next">Next</span></li>
                    <li class="status-item next"><span>§0 Early offset UI: Accept 15/30 min choice in dialogue</span><span class="status-badge next">Next</span></li>
                    <li class="status-item todo"><span>Conversation history screen: New route to browse</span><span class="status-badge todo">Todo</span></li>
                    <li class="status-item todo"><span>Accessibility audit: Keyboard nav, ARIA labels</span><span class="status-badge todo">Todo</span></li>
                </ul>
            </div>
        </div>

        <!-- BACKEND TAB -->
        <div id="backend" class="content">
            <div class="tab-sticky-header">
                <div class="tab-sticky-left"><div class="tab-sticky-dot" style="background:#06b6d4"></div><span class="tab-sticky-title">Backend Status</span></div>
                <span class="tab-sticky-count">FastAPI &bull; PostgreSQL &bull; Deepgram &bull; Groq</span>
            </div>
            <div class="section">
                <h2>Backend Status</h2>
                <h3>Done</h3>
                <ul class="status-list">
                    <li class="status-item done"><span>FastAPI app, CORS, lifespan hooks</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>PostgreSQL + SQLAlchemy 2.0 async</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>Alembic migrations (3 versions)</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>Register / login / logout / refresh (JWT)</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>POST /api/process-voice with intent parsing</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>Deepgram STT/TTS via Pipecat</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>Groq intent parsing (JSON schema)</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>VoiceClarificationSession multi-turn loop</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>Tasks/Events/Reminders CRUD APIs</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>APScheduler + WebSocket /api/ws/reminders</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>GET /api/activity + GET /api/conversations</span><span class="status-badge done">Done</span></li>
                    <li class="status-item done"><span>Loguru structured logging</span><span class="status-badge done">Done</span></li>
                </ul>
                <h3>Partial</h3>
                <ul class="status-list">
                    <li class="status-item partial"><span>User preferences API: Schema exists, no prefs storage yet</span><span class="status-badge partial">Partial</span></li>
                </ul>
                <h3>Todo / Next</h3>
                <ul class="status-list">
                    <li class="status-item next"><span>TTS in WS payload: Audio URL on reminder fire</span><span class="status-badge next">Next</span></li>
                    <li class="status-item next"><span>User preferences API: Store timezone, voice style</span><span class="status-badge next">Next</span></li>
                    <li class="status-item todo"><span>Event conflict check: Overlap detection before create</span><span class="status-badge todo">Todo</span></li>
                    <li class="status-item todo"><span>Rate limit handling: Return 429 with Retry-After</span><span class="status-badge todo">Todo</span></li>
                </ul>
            </div>
        </div>

        <!-- HOOKS & SKILLS TAB -->
        <div id="hooks" class="content">
            <div class="tab-sticky-header">
                <div class="tab-sticky-left"><div class="tab-sticky-dot" style="background:#ec4899"></div><span class="tab-sticky-title">Hooks &amp; Skills</span></div>
                <span class="tab-sticky-count">15 system skills &bull; 14 custom hooks &bull; custom commands</span>
            </div>
            <div class="section">
                <h2>System Skills (Claude Code Built-in)</h2>
                <p style="margin-bottom: 15px; color: #666; font-size: 0.9em;">
                    Claude Code's built-in skills available in this project.
                </p>
                <table class="feature-table">
                    <thead>
                        <tr>
                            <th>Skill</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        + system_skills_html
        + """
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2>Custom Hooks (Project-Specific)</h2>
                <p style="margin-bottom: 15px; color: #666; font-size: 0.9em;">
                    Custom hooks created for this project. Run automatically on tool events (Bash, Edit, Write, Commit).
                </p>
                <table class="feature-table">
                    <thead>
                        <tr>
                            <th>Hook</th>
                            <th>Purpose</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        + custom_hooks_html
        + """
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2>Custom Commands (Project-Specific)</h2>
                <p style="margin-bottom: 15px; color: #666; font-size: 0.9em;">
                    Custom slash commands registered for this project.
                </p>
                <table class="feature-table">
                    <thead>
                        <tr>
                            <th>Command</th>
                            <th>Type</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        + custom_commands_html
        + """
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        (function() {
            if (localStorage.getItem('dashboard-theme') === 'dark') {
                document.body.classList.add('dark');
            }
        })();

        function toggleTheme() {
            var isDark = document.body.classList.toggle('dark');
            localStorage.setItem('dashboard-theme', isDark ? 'dark' : 'light');
        }

        function activateTab(tabName) {
            document.querySelectorAll('.content').forEach(function(c) { c.classList.remove('active'); });
            document.querySelectorAll('.tab-button').forEach(function(b) { b.classList.remove('active'); });
            document.getElementById(tabName).classList.add('active');
            var btn = document.querySelector('[data-tab="' + tabName + '"]');
            if (btn) btn.classList.add('active');
        }

        function showTab(event, tabName) { activateTab(tabName); }

        function navigateToTab(tabName) {
            activateTab(tabName);
            var tabs = document.querySelector('.tabs');
            if (tabs) window.scrollTo({ top: tabs.offsetTop - 20, behavior: 'smooth' });
        }

        function animateProgressBars() {
            document.querySelectorAll('.card-progress-fill').forEach(function(bar) {
                var pct = bar.getAttribute('data-pct');
                if (pct) { setTimeout(function() { bar.style.width = pct + '%'; }, 100); }
            });
        }

        document.addEventListener('DOMContentLoaded', animateProgressBars);
    </script>
</body>
</html>
"""
    )
    # Substitute doc-driven placeholders (Completed / Gaps tabs + tab badges).
    html = (
        html.replace("{{COMPLETED_ROWS}}", completed_html)
        .replace("{{GAPS_ROWS}}", gaps_html)
        .replace("{{COMPLETED_COUNT}}", str(completed_count))
        .replace("{{GAPS_COUNT}}", str(gaps_count))
    )
    return html


def main():
    root = get_project_root()

    # Create dashboard folder
    dashboard_dir = root / "dashboard"
    dashboard_dir.mkdir(exist_ok=True)

    # Generate HTML
    html = build_html_dashboard()

    # Save with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    timestamped_file = dashboard_dir / f"proj_dashboard_{timestamp}.html"
    timestamped_file.write_text(html, encoding="utf-8")
    print("[OK] Dashboard saved: " + str(timestamped_file))

    # Open in browser
    webbrowser.open(f"file://{timestamped_file.absolute()}")
    print("[OK] Opening in browser...")
    print("[INFO] All versions stored in: " + str(dashboard_dir))


if __name__ == "__main__":
    main()
