#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"

FILE_PATH="$(json_input_get path)"
[[ -z "$FILE_PATH" ]] && FILE_PATH="$(json_input_get file_path)"
FILE_PATH_NORM="$(normalize_path "$FILE_PATH")"

# Only trigger on .env.example
echo "$FILE_PATH_NORM" | grep -q '\.env\.example$' || exit 0

ENV_EXAMPLE="$BACKEND_DIR/.env.example"
ENV_FILE="$BACKEND_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
  hook_warn "No .env file found at backend/.env — cannot compare against .env.example"
  exit 1
fi

# Extract KEY names: skip comments, cut at = sign
get_keys() {
  grep -v '^\s*#' "$1" | grep '=' | sed 's/=.*//' | sed 's/^[[:space:]]*//' | grep -E '^[A-Za-z_][A-Za-z0-9_]*$' | sort -u
}

EXAMPLE_KEYS="$(get_keys "$ENV_EXAMPLE")"
ACTUAL_KEYS="$(get_keys "$ENV_FILE")"

MISSING=""
while IFS= read -r key; do
  [ -z "$key" ] && continue
  if ! echo "$ACTUAL_KEYS" | grep -q "^${key}$"; then
    MISSING="${MISSING}\n  - ${key}"
  fi
done <<< "$EXAMPLE_KEYS"

if [ -n "$MISSING" ]; then
  hook_warn ".env.example drift: keys in .env.example MISSING from backend/.env:"
  printf "%b\n" "$MISSING" >&2
  echo "  Add missing keys to backend/.env before running the server." >&2
else
  hook_info "ENV drift check: backend/.env is in sync with .env.example."
fi

exit 0
