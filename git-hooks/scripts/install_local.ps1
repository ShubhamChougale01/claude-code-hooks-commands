# install_local.ps1 — Run from your project repo root (Windows)
# Usage: powershell -ExecutionPolicy Bypass -File \path\to\code-review-hooks\scripts\install_local.ps1

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir  = Split-Path -Parent $ScriptDir
$GitHooksDir = Join-Path (git rev-parse --git-dir) "hooks"

Write-Host "Installing code review hooks..."
Write-Host "  Source: $ProjectDir"
Write-Host "  Target: $GitHooksDir"

# Install Python dependencies
Write-Host "`n-> Installing Python dependencies..."
pip install -r "$ProjectDir\requirements.txt" --quiet

# Copy pre-push hook
Write-Host "-> Installing pre-push hook..."
Copy-Item "$ProjectDir\hooks\pre-push" "$GitHooksDir\pre-push" -Force

# Create .env if it doesn't exist
$EnvFile = "$ProjectDir\.env"
if (-not (Test-Path $EnvFile)) {
    Copy-Item "$ProjectDir\.env.example" $EnvFile
    Write-Host "`n  Created .env from template."
    Write-Host "  Edit $EnvFile and set your ANTHROPIC_API_KEY"
} else {
    Write-Host "-> .env already exists -- skipping"
}

Write-Host "`n[OK] Local pre-push hook installed!"
Write-Host "`nTo test without an API key:"
Write-Host "  python $ProjectDir\src\run_review.py --dry-run"
Write-Host "`nTo get your API key: https://console.anthropic.com"
