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
            key = name.strip().lower()
            if key in names:
                problems.append(f"{where}: duplicate name '{name}'")
            names.add(key)
    return problems


def check_skins(config, site=SITE):
    """Returns a list of problems with a skins.json value; empty means valid. Each skin is
    a folder themes/<id>/theme.css; index.html must start on the default skin."""
    if not isinstance(config, dict):
        return ["skins.json must be an object"]
    skins = config.get("skins")
    if not isinstance(skins, list) or not skins:
        return ["skins.json 'skins' must be a non-empty list"]
    problems, ids = [], []
    for i, skin in enumerate(skins):
        where = f"skins.json entry {i}"
        sid = skin.get("id") if isinstance(skin, dict) else None
        label = skin.get("label") if isinstance(skin, dict) else None
        if not isinstance(sid, str) or not re.fullmatch(r"[a-z0-9_-]+", sid):
            problems.append(f"{where}: 'id' must be a folder name like 'dark'")
            continue
        if not isinstance(label, str) or not label.strip():
            problems.append(f"{where}: 'label' must be a non-empty string")
        if sid in ids:
            problems.append(f"{where}: duplicate id '{sid}'")
        ids.append(sid)
        if not (site / "themes" / sid / "theme.css").is_file():
            problems.append(f"{where}: themes/{sid}/theme.css is missing")
    default = config.get("default")
    if default not in ids:
        problems.append("skins.json 'default' must be one of the listed ids")
    elif (site / "index.html").exists():
        html = (site / "index.html").read_text()
        if f'href="themes/{default}/theme.css"' not in html:
            problems.append(f"index.html must link themes/{default}/theme.css (the default)")
    return problems


def check_index(site=SITE):
    """Every local file index.html links to must exist."""
    html = (site / "index.html").read_text()
    refs = re.findall(r'(?:src|href)="([^":#?]+)"', html)
    return [
        f"index.html refers to missing {ref}"
        for ref in refs
        if not (site / ref.lstrip("/")).exists()
    ]


def check_launcher(script=ROOT / "deploy" / "deploy-launcher.sh"):
    result = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
    return [f"deploy-launcher.sh: {result.stderr.strip()}"] if result.returncode else []


def main():
    try:
        apps = json.loads((SITE / "apps.json").read_text())
    except json.JSONDecodeError as err:
        problems = [f"apps.json is not valid JSON: {err}"]
    else:
        problems = check_apps(apps)
    try:
        problems += check_skins(json.loads((SITE / "skins.json").read_text()))
    except (OSError, json.JSONDecodeError) as err:
        problems.append(f"skins.json is not readable JSON: {err}")
    problems += check_index() + check_launcher()
    for problem in problems:
        print(problem, file=sys.stderr)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
