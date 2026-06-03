#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"

FILE_PATH="$(json_input_get path)"
[[ -z "$FILE_PATH" ]] && FILE_PATH="$(json_input_get file_path)"
FILE_PATH_NORM="$(normalize_path "$FILE_PATH")"

# Only backend/app/models/*.py
echo "$FILE_PATH_NORM" | grep -qE 'backend/app/models/[^/]+\.py$' || exit 0
echo "$FILE_PATH_NORM" | grep -q '__init__.py' && exit 0

MODEL_BASENAME="$(basename "$FILE_PATH_NORM" .py)"
VERSIONS_DIR="$BACKEND_DIR/alembic/versions"

PY_BIN="$VENV_SCRIPTS/python.exe"
[ -f "$PY_BIN" ] || PY_BIN="$VENV_SCRIPTS/python"
[ -f "$PY_BIN" ] || PY_BIN="python3"

NOW_EPOCH="$(date +%s)"
THRESHOLD=$((NOW_EPOCH - 60))
NEW_MIGRATION=""

# Check for any .py file in versions/ modified in the last 60 seconds
for f in "$VERSIONS_DIR"/*.py; do
  [ -f "$f" ] || continue
  [[ "$(basename "$f")" == "__init__.py" ]] && continue
  FILE_MTIME="$("$PY_BIN" -c "import os; print(int(os.path.getmtime(r'${f//\'/}')))" 2>/dev/null || echo 0)"
  if [ "$FILE_MTIME" -gt "$THRESHOLD" ]; then
    NEW_MIGRATION="$(basename "$f")"
    break
  fi
done

if [ -z "$NEW_MIGRATION" ]; then
  hook_warn "Model '$MODEL_BASENAME' was edited but no new Alembic migration detected in the last 60 seconds."
  echo "" >&2
  echo "  If you added/changed/removed columns, generate a migration:" >&2
  echo "    cd backend && .venv/Scripts/alembic.exe revision --autogenerate -m \"describe_change\"" >&2
  echo "" >&2
  exit 1
fi

hook_info "Migration reminder: new migration detected — '$NEW_MIGRATION'. Looks good."
exit 0
