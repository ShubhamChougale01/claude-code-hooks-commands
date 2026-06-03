#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"

TOOL_NAME="$(json_get tool_name)"
[[ "$TOOL_NAME" != "Bash" ]] && exit 0

CMD="$(json_input_get command)"

# Only activate for alembic upgrade or downgrade
if ! echo "$CMD" | grep -qE 'alembic\s+(upgrade|downgrade)'; then
  exit 0
fi

VERSIONS_DIR="$BACKEND_DIR/alembic/versions"
BACKUP_BASE="$BACKEND_DIR/alembic/backups"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="$BACKUP_BASE/schema_${TIMESTAMP}"

mkdir -p "$BACKUP_DIR"

if [ -d "$VERSIONS_DIR" ]; then
  FILE_COUNT=$(find "$VERSIONS_DIR" -maxdepth 1 -name "*.py" 2>/dev/null | wc -l | tr -d ' ')
  cp -r "$VERSIONS_DIR/." "$BACKUP_DIR/" 2>/dev/null || true
  hook_info "Alembic pre-flight: backed up $FILE_COUNT migration file(s) → alembic/backups/schema_${TIMESTAMP}/"
else
  hook_warn "Alembic versions dir not found at $VERSIONS_DIR"
fi

exit 0
