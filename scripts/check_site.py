"""Checks run by CI and before every merge. Standard library only.

    python3 scripts/check_site.py
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
REQUIRED = ("name", "url", "description")
ALLOWED = set(REQUIRED) | {"icon"}


def check_apps(apps):
    """Returns a list of problems with an apps.json value; empty means valid."""
    if not isinstance(apps, list) or not apps:
        return ["apps.json must be a non-empty list"]
    problems, names = [], set()
    for i, app in enumerate(apps):
        where = f"apps.json entry {i}"
        if not isinstance(app, dict):
            problems.append(f"{where}: must be an object")
            continue
        for key in REQUIRED:
            if not isinstance(app.get(key), str) or not app[key].strip():
                problems.append(f"{where}: '{key}' must be a non-empty string")
        for key in sorted(set(app) - ALLOWED):
            problems.append(f"{where}: unknown key '{key}'")
        if "icon" in app and not isinstance(app["icon"], str):
            problems.append(f"{where}: 'icon' must be a string")
        url = app.get("url")
        if isinstance(url, str):
            parsed = urlparse(url)
            if parsed.scheme != "https" or not parsed.netloc:
                problems.append(f"{where}: url must be an absolute https:// URL")
        name = app.get("name")
        if isinstance(name, str):
            if name.lower() in names:
                problems.append(f"{where}: duplicate name '{name}'")
            names.add(name.lower())
    return problems


def check_index():
    """Every local file index.html links to must exist."""
    html = (SITE / "index.html").read_text()
    refs = re.findall(r'(?:src|href)="([^":#?]+)"', html)
    return [f"index.html refers to missing {ref}" for ref in refs if not (SITE / ref).exists()]


def check_launcher():
    script = ROOT / "deploy" / "deploy-launcher.sh"
    result = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
    return [f"deploy-launcher.sh: {result.stderr.strip()}"] if result.returncode else []


def main():
    try:
        apps = json.loads((SITE / "apps.json").read_text())
    except json.JSONDecodeError as err:
        problems = [f"apps.json is not valid JSON: {err}"]
    else:
        problems = check_apps(apps)
    problems += check_index() + check_launcher()
    for problem in problems:
        print(problem, file=sys.stderr)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
