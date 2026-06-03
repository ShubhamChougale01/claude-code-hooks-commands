#!/usr/bin/env bash
# .claude/hooks/lib/common.sh (PORTABLE VERSION)
# Source at the top of every hook: source "$(dirname "$0")/../lib/common.sh"
#
# This version uses git to detect project root dynamically, making it portable
# across any project that uses git as its VCS. Customize via env vars if needed:
#   BACKEND_DIR=/path/to/backend
#   FRONTEND_DIR=/path/to/frontend

# ── Project paths ─────────────────────────────────────────────────────────────
# Detect project root via git (portable across project layouts)
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

# Default subdirectory names (customize via env vars if needed)
BACKEND_DIR="${BACKEND_DIR:-$PROJECT_ROOT/backend}"
FRONTEND_DIR="${FRONTEND_DIR:-$PROJECT_ROOT/frontend}"

# Windows venv uses Scripts/ not bin/
if [ -d "$BACKEND_DIR/.venv/Scripts" ]; then
  VENV_SCRIPTS="$BACKEND_DIR/.venv/Scripts"
else
  VENV_SCRIPTS="$BACKEND_DIR/.venv/bin"
fi

NODE_BIN="$FRONTEND_DIR/node_modules/.bin"

# ── stdin capture ─────────────────────────────────────────────────────────────
# Hooks receive JSON exactly once on stdin — read it all up front
HOOK_INPUT="$(cat)"

# ── JSON helpers ──────────────────────────────────────────────────────────────
# Uses venv Python to avoid jq dependency (not installed by default on Windows)

_py_exe() {
  if [ -f "$VENV_SCRIPTS/python.exe" ]; then
    echo "$VENV_SCRIPTS/python.exe"
  elif [ -f "$VENV_SCRIPTS/python" ]; then
    echo "$VENV_SCRIPTS/python"
  else
    echo "python3"
  fi
}

# json_get <top-level-field>
json_get() {
  local py; py="$(_py_exe)"
  printf '%s' "$HOOK_INPUT" | "$py" -c \
    "import sys,json; d=json.load(sys.stdin); print(d.get('$1',''))" 2>/dev/null || true
}

# json_input_get <tool_input sub-field>
json_input_get() {
  local py; py="$(_py_exe)"
  printf '%s' "$HOOK_INPUT" | "$py" -c \
    "import sys,json; d=json.load(sys.stdin); print((d.get('tool_input') or {}).get('$1',''))" 2>/dev/null || true
}

# ── Logging ───────────────────────────────────────────────────────────────────
# All output goes to stderr — stdout is reserved by Claude Code
hook_info()  { echo "[HOOK INFO]  $*" >&2; }
hook_warn()  { echo "[HOOK WARN]  $*" >&2; }
hook_block() { echo "[HOOK BLOCK] $*" >&2; }

# ── Path helpers ──────────────────────────────────────────────────────────────
# Normalize Windows backslashes to forward slashes
normalize_path() {
  echo "${1//\\//}"
}

# Convert MSYS/bash path to Windows native path for .exe tools
to_native_path() {
  cygpath -w "$1" 2>/dev/null || echo "$1"
}
