# Maintenance helper — Windows PowerShell
# Usage: .\scripts\maintain.ps1 <command> [target]
# Commands: format, lint, security, complexity, deps, coverage, deadcode, all

param(
    [Parameter(Position=0)]
    [ValidateSet("format","lint","security","complexity","deps","coverage","deadcode","all")]
    [string]$Command = "all",

    [Parameter(Position=1)]
    [string]$Target = "."
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

python "$ProjectDir\src\maintenance.py" $Command $Target
