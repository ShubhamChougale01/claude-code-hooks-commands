#!/bin/bash
# Installs post-receive hook on a self-hosted bare Git repository
# Usage: bash install_server.sh /path/to/repo.git /path/to/code-review-hooks
#
# NOTE: For GitHub.com / GitLab.com (SaaS), post-receive hooks are not supported.
#       Use GitHub Actions or GitLab CI instead — see README.md for CI setup guide.

set -e

REPO_DIR="$1"
PROJECT_DIR="$2"

if [ -z "$REPO_DIR" ] || [ -z "$PROJECT_DIR" ]; then
    echo "Usage: bash install_server.sh /path/to/repo.git /path/to/code-review-hooks"
    exit 1
fi

if [ ! -d "$REPO_DIR/hooks" ]; then
    echo "ERROR: $REPO_DIR does not look like a bare Git repository (no hooks/ dir)"
    exit 1
fi

echo "Installing server-side post-receive hook..."
echo "  Repo:    $REPO_DIR"
echo "  Project: $PROJECT_DIR"

# Install Python dependencies on server
echo "→ Installing Python dependencies..."
pip3 install -r "$PROJECT_DIR/requirements.txt" --quiet

# Copy and configure post-receive hook
echo "→ Installing post-receive hook..."
cp "$PROJECT_DIR/hooks/post-receive" "$REPO_DIR/hooks/post-receive"
chmod +x "$REPO_DIR/hooks/post-receive"

# Inject real PROJECT_DIR path
sed -i "s|PROJECT_DIR=\"/path/to/code-review-hooks\"|PROJECT_DIR=\"$PROJECT_DIR\"|g" \
    "$REPO_DIR/hooks/post-receive"

# Remind about API key
echo ""
echo "⚠️  Set ANTHROPIC_API_KEY on the server:"
echo "   echo 'export ANTHROPIC_API_KEY=your_key_here' >> /etc/environment"
echo "   OR add it directly in $REPO_DIR/hooks/post-receive"
echo ""
echo "✓ Server post-receive hook installed for $REPO_DIR"
