#!/bin/bash
# Maintenance helper — Linux/macOS
# Usage: ./scripts/maintain.sh <command> [target]
# Commands: format, lint, security, complexity, deps, coverage, deadcode, all

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

python3 "$PROJECT_DIR/src/maintenance.py" "${1:-all}" "${2:-.}"
