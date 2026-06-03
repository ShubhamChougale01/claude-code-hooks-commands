#!/bin/bash
# Installs pre-push hook into the current repo's .git/hooks/
# Run from the root of your project repo: bash /path/to/code-review-hooks/scripts/install_local.sh

set -e

HOOKS_SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GIT_HOOKS_DIR="$(git rev-parse --git-dir)/hooks"

echo "Installing code review hooks..."
echo "  Source: $HOOKS_SOURCE_DIR"
echo "  Target: $GIT_HOOKS_DIR"

# Install Python dependencies
echo ""
echo "→ Installing Python dependencies..."
pip install -r "$HOOKS_SOURCE_DIR/requirements.txt" --quiet

# Copy pre-push hook
echo "→ Installing pre-push hook..."
cp "$HOOKS_SOURCE_DIR/hooks/pre-push" "$GIT_HOOKS_DIR/pre-push"
chmod +x "$GIT_HOOKS_DIR/pre-push"

# Update PROJECT_DIR path inside the hook
sed -i "s|PROJECT_DIR=\".*\"|PROJECT_DIR=\"$HOOKS_SOURCE_DIR\"|g" "$GIT_HOOKS_DIR/pre-push" 2>/dev/null || true

# Create .env if it doesn't exist
if [ ! -f "$HOOKS_SOURCE_DIR/.env" ]; then
    cp "$HOOKS_SOURCE_DIR/.env.example" "$HOOKS_SOURCE_DIR/.env"
    echo ""
    echo "⚠️  Created .env from template."
    echo "   Edit $HOOKS_SOURCE_DIR/.env and set your ANTHROPIC_API_KEY"
else
    echo "→ .env already exists — skipping"
fi

echo ""
echo "✓ Local pre-push hook installed successfully!"
echo ""
echo "To test without an API key:"
echo "  python3 $HOOKS_SOURCE_DIR/src/run_review.py --dry-run"
echo ""
echo "To get your API key: https://console.anthropic.com"
