#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"

TOOL_NAME="$(json_get tool_name)"
[[ "$TOOL_NAME" != "Bash" ]] && exit 0

CMD="$(json_input_get command)"

if ! echo "$CMD" | grep -q 'git commit'; then
  exit 0
fi

ERRORS=()
WARNINGS=()

# ── TypeScript typecheck ──────────────────────────────────────────────────────
hook_info "Pre-commit gate: running tsc --noEmit..."
if [ -d "$FRONTEND_DIR/node_modules" ]; then
  TSC_OUT="$(cd "$FRONTEND_DIR" && npx --no-install tsc --noEmit -p tsconfig.app.json 2>&1)" || {
    ERRORS+=("TypeScript errors:\n${TSC_OUT}")
  }
else
  WARNINGS+=("frontend/node_modules not found — skipping TypeScript check")
fi

# ── ESLint ────────────────────────────────────────────────────────────────────
hook_info "Pre-commit gate: running eslint..."
if [ -d "$FRONTEND_DIR/node_modules" ]; then
  ESLINT_OUT="$(cd "$FRONTEND_DIR" && npx --no-install eslint "src" --max-warnings=0 2>&1)" || {
    ERRORS+=("ESLint errors:\n${ESLINT_OUT}")
  }
else
  WARNINGS+=("frontend/node_modules not found — skipping ESLint check")
fi

# ── Black check ───────────────────────────────────────────────────────────────
hook_info "Pre-commit gate: running black --check..."
BLACK_BIN="$VENV_SCRIPTS/black.exe"
if [ -f "$BLACK_BIN" ]; then
  BLACK_OUT="$(cd "$BACKEND_DIR" && "$BLACK_BIN" --check --target-version py311 app/ 2>&1)" || {
    ERRORS+=("Python formatting issues (run black to fix):\n${BLACK_OUT}")
  }
else
  WARNINGS+=("black not installed — run: cd backend && uv add --dev black isort")
fi

# ── Report ────────────────────────────────────────────────────────────────────
for w in "${WARNINGS[@]:-}"; do
  [ -n "$w" ] && hook_warn "$w"
done

if [ ${#ERRORS[@]} -gt 0 ]; then
  hook_block "Pre-commit quality gate FAILED — fix these before committing:"
  echo "" >&2
  for e in "${ERRORS[@]}"; do
    printf "%b\n" "$e" >&2
    echo "────────────────────────────────────────" >&2
  done
  exit 2
fi

hook_info "Pre-commit quality gate passed."
exit 0
