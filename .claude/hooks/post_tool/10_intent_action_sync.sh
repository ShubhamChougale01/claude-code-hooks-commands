#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"

FILE_PATH="$(json_input_get path)"
[[ -z "$FILE_PATH" ]] && FILE_PATH="$(json_input_get file_path)"
FILE_PATH_NORM="$(normalize_path "$FILE_PATH")"

# Only intent_parser.py or action_executor.py
echo "$FILE_PATH_NORM" | grep -qE '(intent_parser|action_executor)\.py$' || exit 0

# Configurable via environment variables (for use in different project layouts)
INTENT_FILE="${INTENT_PARSER_FILE:-$BACKEND_DIR/app/services/intent_parser.py}"
EXECUTOR_FILE="${ACTION_EXECUTOR_FILE:-$BACKEND_DIR/app/services/action_executor.py}"

[ -f "$INTENT_FILE" ]  || { hook_warn "intent_parser.py not found"; exit 0; }
[ -f "$EXECUTOR_FILE" ] || { hook_warn "action_executor.py not found"; exit 0; }

# Extract intent enum values — look for ALL_CAPS strings (e.g. "CREATE_TASK") in intent_parser
DEFINED_INTENTS="$(grep -Eo '"[A-Z][A-Z_]{3,}"' "$INTENT_FILE" \
  | tr -d '"' \
  | grep -vE '^(IST|UTC|JSON|API|STT|TTS|STR|INT|URL|HTTP|SQL|LLM|MCP|WS|APP|ENV|DB|JWT|UUID)$' \
  | sort -u || true)"

# Extract handled action strings from action_executor.py
# Matches: action == "CREATE_TASK"
HANDLED_ACTIONS="$(grep -Eo 'action\s*==\s*"[A-Z_]+"' "$EXECUTOR_FILE" 2>/dev/null \
  | grep -Eo '"[A-Z_]+"' | tr -d '"' || true)"
# Also: action in {"A", "B", ...}
HANDLED_ACTIONS="$HANDLED_ACTIONS
$(grep -E 'action\s+in\s+\{' "$EXECUTOR_FILE" 2>/dev/null \
  | grep -Eo '"[A-Z_]+"' | tr -d '"' || true)"
HANDLED_SORTED="$(echo "$HANDLED_ACTIONS" | sort -u | grep -v '^$')"

# Find defined intents with no handler
MISSING_HANDLERS=""
while IFS= read -r intent; do
  [ -z "$intent" ] && continue
  if ! echo "$HANDLED_SORTED" | grep -q "^${intent}$"; then
    MISSING_HANDLERS="${MISSING_HANDLERS}\n  - ${intent} (in intent_parser, no handler in action_executor)"
  fi
done <<< "$DEFINED_INTENTS"

REPORT=""
[ -n "$MISSING_HANDLERS" ] && REPORT="${REPORT}\nIntents with no handler:${MISSING_HANDLERS}"

if [ -n "$REPORT" ]; then
  hook_warn "Intent↔Action completeness mismatch:"
  printf "%b\n" "$REPORT" >&2
  exit 1
fi

INTENT_COUNT="$(echo "$DEFINED_INTENTS" | grep -c . || echo 0)"
hook_info "Intent↔Action check: all $INTENT_COUNT intent types have handlers."
exit 0
