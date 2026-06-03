#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"

FILE_PATH="$(json_input_get path)"
[[ -z "$FILE_PATH" ]] && FILE_PATH="$(json_input_get file_path)"
FILE_PATH_NORM="$(normalize_path "$FILE_PATH")"

# Only backend/app/api/routes/*.py (not __init__.py)
echo "$FILE_PATH_NORM" | grep -qE 'backend/app/api/routes/[^/]+\.py$' || exit 0
echo "$FILE_PATH_NORM" | grep -q '__init__.py' && exit 0

ROUTE_BASENAME="$(basename "$FILE_PATH_NORM" .py)"

# Routes without a frontend API client counterpart
SKIP_ROUTES="ws mcp conversations"
echo "$SKIP_ROUTES" | grep -qw "$ROUTE_BASENAME" && {
  hook_info "API sync: '$ROUTE_BASENAME' has no frontend API client mapping — skipping."
  exit 0
}

# Backend route file → frontend API client filename
declare -A ROUTE_TO_FRONTEND
ROUTE_TO_FRONTEND["tasks"]="tasks.ts"
ROUTE_TO_FRONTEND["reminders"]="reminders.ts"
ROUTE_TO_FRONTEND["events"]="events.ts"
ROUTE_TO_FRONTEND["auth"]="auth.ts"
ROUTE_TO_FRONTEND["voice"]="voice.ts"
ROUTE_TO_FRONTEND["activity"]="activity.ts"

FRONTEND_FILE_NAME="${ROUTE_TO_FRONTEND[$ROUTE_BASENAME]:-}"
if [ -z "$FRONTEND_FILE_NAME" ]; then
  hook_info "API sync: no mapping defined for '$ROUTE_BASENAME' — skipping."
  exit 0
fi

ROUTE_FILE="$BACKEND_DIR/app/api/routes/${ROUTE_BASENAME}.py"
FRONTEND_API_FILE="$FRONTEND_DIR/src/api/$FRONTEND_FILE_NAME"

if [ ! -f "$FRONTEND_API_FILE" ]; then
  hook_warn "Frontend API file not found: src/api/$FRONTEND_FILE_NAME"
  exit 1
fi

# Extract route paths from backend (e.g. @router.get("/tasks/{id}") → /tasks/)
# Strip path params for comparison
BACKEND_PATHS="$(grep -E '@router\.\w+\("' "$ROUTE_FILE" 2>/dev/null \
  | grep -Eo '"[^"]+"' | tr -d '"' \
  | sed 's/{[^}]*}//g' | sed 's|/$||' | sort -u || true)"

# Extract API path strings from frontend client
FRONTEND_CONTENT="$(cat "$FRONTEND_API_FILE")"

MISSING=""
while IFS= read -r path; do
  [ -z "$path" ] && continue
  # Build what the full path should look like in the frontend (with /api prefix)
  FULL_PATH="/api${path}"
  FULL_PATH_NORM="${FULL_PATH%/}"
  # Check if this path (or a template variant) appears in the frontend file
  PATH_BASE="$(echo "$FULL_PATH_NORM" | sed 's|/$||')"
  if ! echo "$FRONTEND_CONTENT" | grep -qF "$PATH_BASE"; then
    MISSING="${MISSING}\n  - ${FULL_PATH_NORM} (backend route not found in frontend/src/api/${FRONTEND_FILE_NAME})"
  fi
done <<< "$BACKEND_PATHS"

if [ -n "$MISSING" ]; then
  hook_warn "Frontend↔Backend API drift after editing '$ROUTE_BASENAME.py':"
  printf "%b\n" "$MISSING" >&2
  echo "  Consider updating frontend/src/api/${FRONTEND_FILE_NAME}" >&2
  exit 1
fi

hook_info "API sync: frontend/src/api/${FRONTEND_FILE_NAME} appears in sync with backend routes."
exit 0
