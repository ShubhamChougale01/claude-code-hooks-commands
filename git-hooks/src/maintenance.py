#!/usr/bin/env python3
"""
Helper commands for code maintenance tasks.
Run via: python src/maintenance.py <command> [target]
"""

import subprocess
import sys
import os
import argparse
from colorama import init, Fore, Style

init(autoreset=True)

DIVIDER = "-" * 68


def _run(cmd: list, label: str) -> int:
    print(f"\n{Fore.CYAN}{DIVIDER}")
    print(f"  {label}")
    print(f"{DIVIDER}{Style.RESET_ALL}")
    result = subprocess.run(cmd, text=True)
    return result.returncode


def _run_capture(cmd: list, label: str) -> tuple[int, str]:
    print(f"\n{Fore.CYAN}{DIVIDER}")
    print(f"  {label}")
    print(f"{DIVIDER}{Style.RESET_ALL}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout + result.stderr
    print(output)
    return result.returncode, output


def cmd_format(target: str = ".") -> int:
    """Auto-format Python code with black."""
    return _run(["black", target], f"FORMAT  —  black {target}")


def cmd_lint(target: str = ".") -> int:
    """Lint with flake8 (style + errors)."""
    return _run(["flake8", target, "--max-line-length=100"], f"LINT  —  flake8 {target}")


def cmd_security(target: str = ".") -> int:
    """Scan for security issues with bandit."""
    return _run(["bandit", "-r", target, "-ll"], f"SECURITY  —  bandit {target}")


def cmd_complexity(target: str = ".") -> int:
    """Report cyclomatic complexity with radon."""
    _run(["radon", "cc", target, "-s", "-a"], f"COMPLEXITY  —  radon cc {target}")
    return _run(["radon", "mi", target, "-s"], f"MAINTAINABILITY  —  radon mi {target}")


def cmd_deps() -> int:
    """List outdated and vulnerable dependencies."""
    rc1, _ = _run_capture(["pip", "list", "--outdated"], "OUTDATED DEPENDENCIES")
    rc2 = _run(["pip-audit"], "DEPENDENCY VULNERABILITIES  —  pip-audit")
    return rc1 or rc2


def cmd_coverage(target: str = "src") -> int:
    """Run tests with coverage report."""
    return _run(
        ["pytest", "--cov=" + target, "--cov-report=term-missing", "-v"],
        f"TEST COVERAGE  —  pytest --cov={target}",
    )


def cmd_deadcode(target: str = ".") -> int:
    """Find unused code with vulture."""
    return _run(["vulture", target], f"DEAD CODE  —  vulture {target}")


def cmd_all(target: str = ".") -> int:
    """Run all maintenance checks in sequence."""
    print(f"\n{Fore.CYAN}{'='*68}")
    print(f"{'  FULL MAINTENANCE RUN':^68}")
    print(f"{'='*68}{Style.RESET_ALL}")

    results = {}
    results["format"]     = cmd_format(target)
    results["lint"]       = cmd_lint(target)
    results["security"]   = cmd_security(target)
    results["complexity"] = cmd_complexity(target)
    results["deadcode"]   = cmd_deadcode(target)
    results["deps"]       = cmd_deps()
    results["coverage"]   = cmd_coverage(target)

    print(f"\n{Fore.CYAN}{'='*68}")
    print(f"{'  MAINTENANCE SUMMARY':^68}")
    print(f"{'='*68}{Style.RESET_ALL}")

    all_passed = True
    for name, rc in results.items():
        status = f"{Fore.GREEN}PASS{Style.RESET_ALL}" if rc == 0 else f"{Fore.YELLOW}WARN{Style.RESET_ALL}"
        print(f"  {name:<15} {status}")
        if rc != 0:
            all_passed = False

    print()
    if all_passed:
        print(f"{Fore.GREEN}All checks passed.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Some checks reported issues — review output above.{Style.RESET_ALL}")

    return 0 if all_passed else 1


COMMANDS = {
    "format":     (cmd_format,     "Auto-format Python code with black"),
    "lint":       (cmd_lint,       "Lint with flake8 (style + errors)"),
    "security":   (cmd_security,   "Scan for security issues with bandit"),
    "complexity": (cmd_complexity, "Report cyclomatic complexity with radon"),
    "deps":       (cmd_deps,       "List outdated & vulnerable dependencies"),
    "coverage":   (cmd_coverage,   "Run tests with coverage report"),
    "deadcode":   (cmd_deadcode,   "Find unused code with vulture"),
    "all":        (cmd_all,        "Run all maintenance checks"),
}


def main():
    parser = argparse.ArgumentParser(
        description="Code maintenance helper commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(f"  {k:<12} {v[1]}" for k, v in COMMANDS.items()),
    )
    parser.add_argument(
        "command",
        choices=list(COMMANDS.keys()),
        help="Maintenance command to run",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Directory or file to analyze (default: current directory)",
    )
    args = parser.parse_args()

    fn, _ = COMMANDS[args.command]
    # deps command takes no target
    if args.command == "deps":
        sys.exit(fn())
    else:
        sys.exit(fn(args.target))


if __name__ == "__main__":
    main()
