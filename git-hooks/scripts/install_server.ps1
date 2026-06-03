# install_server.ps1 — Install post-receive hook on a self-hosted bare Git repo (Windows)
# Usage: powershell -ExecutionPolicy Bypass -File install_server.ps1 -RepoDir C:\path\to\repo.git -ProjectDir C:\path\to\code-review-hooks
#
# NOTE: For GitHub.com / GitLab.com (SaaS), post-receive hooks are not supported.
#       Use GitHub Actions or GitLab CI instead -- see README.md for CI setup guide.

param(
    [Parameter(Mandatory)][string]$RepoDir,
    [Parameter(Mandatory)][string]$ProjectDir
)

$HooksDir = Join-Path $RepoDir "hooks"

if (-not (Test-Path $HooksDir)) {
    Write-Error "ERROR: $RepoDir does not look like a bare Git repository (no hooks\ dir)"
    exit 1
}

Write-Host "Installing server-side post-receive hook..."
Write-Host "  Repo:    $RepoDir"
Write-Host "  Project: $ProjectDir"

# Install Python dependencies
Write-Host "-> Installing Python dependencies..."
pip3 install -r "$ProjectDir\requirements.txt" --quiet

# Copy and configure post-receive hook
Write-Host "-> Installing post-receive hook..."
$HookDest = Join-Path $HooksDir "post-receive"
Copy-Item "$ProjectDir\hooks\post-receive" $HookDest -Force

# Inject real PROJECT_DIR path into hook
(Get-Content $HookDest) -replace '/path/to/code-review-hooks', $ProjectDir.Replace('\', '/') |
    Set-Content $HookDest

Write-Host "`n  Set ANTHROPIC_API_KEY on the server:"
Write-Host "  [System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY','your_key','Machine')"
Write-Host "`n[OK] Server post-receive hook installed for $RepoDir"
