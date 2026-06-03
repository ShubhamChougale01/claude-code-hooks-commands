#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"

FILE_PATH="$(json_input_get path)"
[[ -z "$FILE_PATH" ]] && FILE_PATH="$(json_input_get file_path)"
FILE_PATH_NORM="$(normalize_path "$FILE_PATH")"

# Only .py files inside backend/ (exclude venv, cache, migrations)
echo "$FILE_PATH_NORM" | grep -qE '\.py$' || exit 0
echo "$FILE_PATH_NORM" | grep -q 'backend/' || exit 0
echo "$FILE_PATH_NORM" | grep -qE '(\.venv|__pycache__|alembic/versions)/' && exit 0

BLACK_BIN="$VENV_SCRIPTS/black.exe"
ISORT_BIN="$VENV_SCRIPTS/isort.exe"

if [ ! -f "$BLACK_BIN" ]; then
  hook_warn "black not installed — run: cd backend && uv add --dev black isort"
  exit 0
fi

NATIVE_PATH="$(to_native_path "$FILE_PATH_NORM")"
hook_info "Auto-formatting: $NATIVE_PATH"

"$BLACK_BIN" --target-version py311 "$NATIVE_PATH" 2>&1 | while IFS= read -r line; do hook_info "black: $line"; done || true

if [ -f "$ISORT_BIN" ]; then
  "$ISORT_BIN" "$NATIVE_PATH" 2>&1 | while IFS= read -r line; do hook_info "isort: $line"; done || true
fi

exit 0
