#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"

FILE_PATH="$(json_input_get path)"
[[ -z "$FILE_PATH" ]] && FILE_PATH="$(json_input_get file_path)"
FILE_PATH_NORM="$(normalize_path "$FILE_PATH")"

if echo "$FILE_PATH_NORM" | grep -q 'backend/pyproject\.toml$'; then
  hook_warn "pyproject.toml was modified — sync dependencies to apply changes:"
  echo "  cd backend && uv sync" >&2
  exit 1
fi

if echo "$FILE_PATH_NORM" | grep -qE 'frontend/package\.json$'; then
  hook_warn "package.json was modified — install dependencies to apply changes:"
  echo "  cd frontend && npm install" >&2
  exit 1
fi

exit 0
