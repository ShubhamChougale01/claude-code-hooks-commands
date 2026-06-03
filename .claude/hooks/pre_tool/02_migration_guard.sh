#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"

# Edit tool uses "path", Write uses "path", MultiEdit uses "file_path"
FILE_PATH="$(json_input_get path)"
[[ -z "$FILE_PATH" ]] && FILE_PATH="$(json_input_get file_path)"

FILE_PATH_NORM="$(normalize_path "$FILE_PATH")"

# Match alembic/versions/*.py — block edits, migrations are immutable
if echo "$FILE_PATH_NORM" | grep -qE 'alembic/versions/[^/]+\.py$'; then
  hook_block "Migration files in alembic/versions/ are IMMUTABLE and must not be edited."
  echo "" >&2
  echo "  To fix a bad migration, create a new one instead:" >&2
  echo "    cd backend && alembic revision -m \"fix_description\"" >&2
  echo "" >&2
  exit 2
fi

exit 0
