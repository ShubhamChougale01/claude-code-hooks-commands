#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../lib/common.sh"

TOOL_NAME="$(json_get tool_name)"
[[ "$TOOL_NAME" != "Bash" ]] && exit 0

CMD="$(json_input_get command)"

if ! echo "$CMD" | grep -q 'git push'; then
  exit 0
fi

# Block explicit push to main/master (covers: git push origin main, git push origin HEAD:main, git push --force origin main)
if echo "$CMD" | grep -qE 'git\s+push.*(HEAD:)?(main|master)\b'; then
  hook_block "Direct push to main/master is blocked."
  echo "" >&2
  echo "  Push to a feature or development branch, then open a pull request." >&2
  echo "" >&2
  exit 2
fi

# Also catch bare 'git push' when the current branch IS main/master
for REPO_DIR in "$BACKEND_DIR" "$FRONTEND_DIR"; do
  if [ -d "$REPO_DIR/.git" ]; then
    CURRENT_BRANCH="$(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '')"
    if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
      # Bare git push (no explicit remote branch specified)
      if echo "$CMD" | grep -qE '^git\s+push(\s+--\S+)*\s*$'; then
        hook_block "Current branch in '$(basename "$REPO_DIR")' is '$CURRENT_BRANCH'. Bare 'git push' would push to main/master."
        echo "" >&2
        echo "  Switch to a feature branch before pushing:" >&2
        echo "    git checkout -b feature/my-change" >&2
        echo "" >&2
        exit 2
      fi
    fi
  fi
done

exit 0
