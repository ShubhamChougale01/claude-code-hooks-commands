#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import analyzer
import severity_detector
import formatter


def get_diff_pre_push() -> str:
    try:
        result = subprocess.run(
            ["git", "diff", "origin/HEAD..HEAD"],
            capture_output=True, text=True
        )
        if result.returncode != 0 or not result.stdout.strip():
            result = subprocess.run(
                ["git", "diff", "HEAD~1..HEAD"],
                capture_output=True, text=True
            )
        return result.stdout
    except Exception as e:
        print(f"WARNING: Could not get diff: {e}", file=sys.stderr)
        return ""


def get_diff_post_receive(old: str, new: str) -> str:
    try:
        result = subprocess.run(
            ["git", "diff", old, new],
            capture_output=True, text=True
        )
        return result.stdout
    except Exception as e:
        print(f"WARNING: Could not get diff: {e}", file=sys.stderr)
        return ""


def main():
    parser = argparse.ArgumentParser(description="Git code review hook")
    parser.add_argument("--hook", choices=["pre-push", "post-receive"], default="pre-push")
    parser.add_argument("--dry-run", action="store_true", help="Use mock data, skip API call")
    parser.add_argument("--old", default="", help="Old commit hash (post-receive)")
    parser.add_argument("--new", default="", help="New commit hash (post-receive)")
    parser.add_argument("--ref", default="", help="Ref name (post-receive)")
    args = parser.parse_args()

    if args.hook == "pre-push":
        diff = get_diff_pre_push()
    else:
        diff = get_diff_post_receive(args.old, args.new)

    if not diff.strip() and not args.dry_run:
        print("No diff detected — skipping review.")
        sys.exit(0)

    issues = analyzer.analyze(diff, dry_run=args.dry_run)
    result = severity_detector.detect(issues)
    exit_code = formatter.print_report(result)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
