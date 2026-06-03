import json
import os
import sys
from colorama import init, Fore, Style

init(autoreset=True)

ICONS = {
    "CRITICAL": f"{Fore.RED}[CRITICAL]{Style.RESET_ALL}",
    "HIGH":     f"{Fore.YELLOW}[HIGH]{Style.RESET_ALL}",
    "MEDIUM":   f"{Fore.CYAN}[MEDIUM]{Style.RESET_ALL}",
    "LOW":      f"{Fore.WHITE}[LOW]{Style.RESET_ALL}",
}

DIVIDER = "-" * 68


def print_report(result: dict) -> int:
    critical = result["critical"]
    high     = result["high"]
    medium   = result["medium"]
    low      = result["low"]
    total    = result["total"]
    block    = result["should_block"]

    print(f"\n{Fore.CYAN}{'='*68}")
    print(f"{'  CODE REVIEW ANALYSIS':^68}")
    print(f"{'='*68}{Style.RESET_ALL}\n")

    print(f"Summary: {total} issue(s) found")
    print(f"   {ICONS['CRITICAL']}: {len(critical)}")
    print(f"   {ICONS['HIGH']}: {len(high)}")
    print(f"   {ICONS['MEDIUM']}: {len(medium)}")
    print(f"   {ICONS['LOW']}: {len(low)}")

    _print_section("CRITICAL", critical)
    _print_section("HIGH", high)
    _print_section("MEDIUM", medium)
    _print_section("LOW", low)

    print(f"\n{DIVIDER}")
    if block:
        print(f"{Fore.RED}PUSH BLOCKED: Fix CRITICAL/HIGH issues before pushing.{Style.RESET_ALL}")
    else:
        if total > 0:
            print(f"{Fore.GREEN}PUSH ALLOWED -- review warnings above before merging.{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}PUSH ALLOWED -- no issues found.{Style.RESET_ALL}")

    _save_report(result)

    return 1 if block else 0


def _print_section(severity: str, issues: list):
    if not issues:
        return
    label = "BLOCKING" if severity in ("CRITICAL", "HIGH") else "WARNINGS"
    print(f"\n{DIVIDER}")
    print(f"{ICONS[severity]} ISSUES ({label}):")
    for i, issue in enumerate(issues, 1):
        file_ref  = issue.get("file", "unknown")
        line      = issue.get("line", "?")
        message   = issue.get("message", "")
        snippet   = issue.get("code_snippet", "")
        fix       = issue.get("fix", "")
        category  = issue.get("category", "")

        print(f"\n[{i}] {file_ref}:{line}  [{category}]")
        print(f"    {message}")
        if snippet:
            print(f"    Code:  {Fore.RED}{snippet}{Style.RESET_ALL}")
        if fix:
            print(f"    Fix:   {Fore.GREEN}{fix}{Style.RESET_ALL}")


def _save_report(result: dict):
    report_path = os.path.join(".git", "code-review-report.json")
    try:
        with open(report_path, "w") as f:
            json.dump(result, f, indent=2)
    except OSError:
        pass
