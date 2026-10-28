"""Shared helpers: content discovery, front matter, Open WebUI session."""
import os
import pathlib
import re
import sys
import time

import requests
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


def content_files(folder: pathlib.Path) -> list[pathlib.Path]:
    """Markdown files that are real content (no templates, no READMEs)."""
    return sorted(
        p for p in folder.rglob("*.md")
        if not p.name.startswith("_") and p.name.lower() != "readme.md"
    )


def split_front_matter(text: str) -> tuple[dict, str]:
    m = FRONT_MATTER.match(text)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, text[m.end():]


def webui_session() -> tuple[requests.Session, str]:
    """Wait for Open WebUI, sign in as admin (creating the first admin if needed)."""
    base = os.environ.get("WEBUI_URL", "http://localhost:3000").rstrip("/")
    s = requests.Session()

    for _ in range(90):
        try:
            if s.get(f"{base}/health", timeout=5).ok:
                break
        except requests.ConnectionError:
            pass
        time.sleep(2)
    else:
        sys.exit(f"Open WebUI not reachable at {base}")

    creds = {"email": os.environ["ADMIN_EMAIL"], "password": os.environ["ADMIN_PASSWORD"]}
    r = s.post(f"{base}/api/v1/auths/signin", json=creds)
    if not r.ok:
        # First run: the first account created becomes admin.
        r = s.post(f"{base}/api/v1/auths/signup", json={"name": "NEXR Admin", **creds})
        if not r.ok or r.json().get("role") != "admin":
            sys.exit(
                "Could not sign in as admin. Check ADMIN_EMAIL / ADMIN_PASSWORD "
                "(an admin already exists; a pending account may have been created and can be deleted)."
            )
    s.headers["Authorization"] = f"Bearer {r.json()['token']}"
    return s, base
