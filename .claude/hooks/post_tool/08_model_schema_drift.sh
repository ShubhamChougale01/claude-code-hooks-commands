#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"

FILE_PATH="$(json_input_get path)"
[[ -z "$FILE_PATH" ]] && FILE_PATH="$(json_input_get file_path)"
FILE_PATH_NORM="$(normalize_path "$FILE_PATH")"

# Only backend/app/models/*.py (not __init__.py)
echo "$FILE_PATH_NORM" | grep -qE 'backend/app/models/[^/]+\.py$' || exit 0
echo "$FILE_PATH_NORM" | grep -q '__init__.py' && exit 0

MODEL_BASENAME="$(basename "$FILE_PATH_NORM" .py)"

# Model filename → schema filename mapping
declare -A MODEL_TO_SCHEMA
MODEL_TO_SCHEMA["task"]="task"
MODEL_TO_SCHEMA["reminder"]="reminder"
MODEL_TO_SCHEMA["calendar_event"]="event"
MODEL_TO_SCHEMA["user"]="user"
MODEL_TO_SCHEMA["conversation"]="conversation"
MODEL_TO_SCHEMA["activity_log"]="activity"
MODEL_TO_SCHEMA["voice_clarification_session"]="voice"
MODEL_TO_SCHEMA["auth_session"]=""

SCHEMA_NAME="${MODEL_TO_SCHEMA[$MODEL_BASENAME]:-__UNKNOWN__}"

if [ -z "$SCHEMA_NAME" ]; then
  hook_info "Model '$MODEL_BASENAME' has no schema mapping — skipping drift check."
  exit 0
fi

if [ "$SCHEMA_NAME" = "__UNKNOWN__" ]; then
  hook_info "No schema mapping defined for '$MODEL_BASENAME' — skipping drift check."
  exit 0
fi

MODEL_FILE="$BACKEND_DIR/app/models/${MODEL_BASENAME}.py"
SCHEMA_FILE="$BACKEND_DIR/app/schemas/${SCHEMA_NAME}.py"

if [ ! -f "$SCHEMA_FILE" ]; then
  hook_warn "Expected schema file not found: app/schemas/${SCHEMA_NAME}.py"
  exit 0
fi

PY_BIN="$VENV_SCRIPTS/python.exe"
[ -f "$PY_BIN" ] || PY_BIN="$VENV_SCRIPTS/python"
[ -f "$PY_BIN" ] || PY_BIN="python3"

# Extract Mapped column field names from model (lines like: "    field_name: Mapped[")
MODEL_FIELDS="$(grep -E '^\s+\w+:\s+Mapped\[' "$MODEL_FILE" 2>/dev/null \
  | sed 's/:.*//' | sed 's/^[[:space:]]*//' | sort || true)"

# Extract fields from the *Out Pydantic class via AST
SCHEMA_FIELDS="$("$PY_BIN" - "$SCHEMA_FILE" <<'EOF' 2>/dev/null
import ast, sys
try:
    src = open(sys.argv[1]).read()
    tree = ast.parse(src)
    fields = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.endswith('Out'):
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    fields.append(item.target.id)
    print('\n'.join(sorted(fields)))
except Exception:
    pass
EOF
)"

# Relationship field names (ORM internals — not API fields)
RELATION_FIELDS="user tasks reminders events sessions conversations activity_logs voice_clarification_sessions"

MISSING=""
while IFS= read -r field; do
  [ -z "$field" ] && continue
  # Skip relationship and private fields
  echo "$RELATION_FIELDS" | grep -qw "$field" && continue
  [[ "$field" == _* ]] && continue
  if ! echo "$SCHEMA_FIELDS" | grep -q "^${field}$"; then
    MISSING="${MISSING}\n  - ${field}"
  fi
done <<< "$MODEL_FIELDS"

if [ -n "$MISSING" ]; then
  hook_warn "Model→Schema drift in '$MODEL_BASENAME' (fields in model missing from ${SCHEMA_NAME}.py *Out class):"
  printf "%b\n" "$MISSING" >&2
  echo "  Update app/schemas/${SCHEMA_NAME}.py or confirm the omission is intentional." >&2
  exit 1
fi

hook_info "Drift check: no drift detected for '$MODEL_BASENAME' ↔ '${SCHEMA_NAME}.py'."
exit 0
