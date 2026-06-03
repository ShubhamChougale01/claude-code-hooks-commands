#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"

FILE_PATH="$(json_input_get path)"
[[ -z "$FILE_PATH" ]] && FILE_PATH="$(json_input_get file_path)"
FILE_PATH_NORM="$(normalize_path "$FILE_PATH")"

# Only files inside frontend/src/
echo "$FILE_PATH_NORM" | grep -q 'frontend/src/' || exit 0
echo "$FILE_PATH_NORM" | grep -qE '(node_modules|dist)/' && exit 0

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  hook_warn "frontend/node_modules not found — skipping typecheck"
  exit 0
fi

hook_info "Running tsc --noEmit..."
TSC_OUT="$(cd "$FRONTEND_DIR" && npx --no-install tsc --noEmit -p tsconfig.app.json 2>&1)"
TSC_EXIT=$?

if [ $TSC_EXIT -ne 0 ]; then
  hook_warn "TypeScript errors detected:"
  echo "$TSC_OUT" | head -30 >&2
  exit 1
fi

hook_info "tsc: no type errors."
exit 0
