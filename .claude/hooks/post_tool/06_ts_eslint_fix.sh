#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"

FILE_PATH="$(json_input_get path)"
[[ -z "$FILE_PATH" ]] && FILE_PATH="$(json_input_get file_path)"
FILE_PATH_NORM="$(normalize_path "$FILE_PATH")"

# Only .ts/.tsx files inside frontend/ (exclude node_modules, dist)
echo "$FILE_PATH_NORM" | grep -qE '\.(ts|tsx)$' || exit 0
echo "$FILE_PATH_NORM" | grep -q 'frontend/' || exit 0
echo "$FILE_PATH_NORM" | grep -qE '(node_modules|dist)/' && exit 0

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  hook_warn "frontend/node_modules not found — skipping eslint fix"
  exit 0
fi

NATIVE_PATH="$(to_native_path "$FILE_PATH_NORM")"
hook_info "ESLint --fix: $NATIVE_PATH"

# cd to frontend so eslint.config.js is found
cd "$FRONTEND_DIR"
npx --no-install eslint --fix "$NATIVE_PATH" 2>&1 | while IFS= read -r line; do hook_info "eslint: $line"; done || true

exit 0
