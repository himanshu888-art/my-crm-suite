import base64
import os
import pathlib
import sys
import time
from typing import List

import requests

ROOT = pathlib.Path(__file__).resolve().parent
SESSION = requests.Session()

TOKEN = os.environ.get("GITHUB_TOKEN")
if not TOKEN:
    raise SystemExit(
        "Error: GITHUB_TOKEN environment variable is not set. Export a GitHub token with repo creation scope and retry."
    )

SESSION.headers.update(
    {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "deploy-to-github-script",
    }
)


def get_github_user() -> str:
    response = SESSION.get("https://api.github.com/user")
    response.raise_for_status()
    return response.json()["login"]


def create_repo(owner: str, name: str, description: str = "") -> None:
    payload = {
        "name": name,
        "description": description,
        "private": False,
        "auto_init": False,
    }
    response = SESSION.post("https://api.github.com/user/repos", json=payload)
    if response.status_code == 422:
        print(f"Repository '{name}' already exists. Using existing repository.")
        return
    response.raise_for_status()
    print(f"Created repository: {owner}/{name}")


def get_file_sha(owner: str, repo: str, path: str):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = SESSION.get(url)
    if response.status_code == 200:
        return response.json()["sha"]
    return None


SKIP_PATTERNS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.db",
    "test.db",
    ".env",
}


def should_skip(path: pathlib.Path) -> bool:
    if any(part in SKIP_PATTERNS for part in path.parts):
        return True
    if path.name.startswith(".") and path.name not in {"README.md", ".gitignore", ".env.example"}:
        return False
    if path.is_dir():
        return False
    lower_name = path.name.lower()
    if lower_name.endswith(tuple(pattern.lstrip("*" ) for pattern in SKIP_PATTERNS if pattern.startswith("*"))):
        return True
    return False


def build_file_list(root: pathlib.Path) -> List[pathlib.Path]:
    files: List[pathlib.Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and not should_skip(path.relative_to(root)):
            files.append(path)
    return files


def upload_file(owner: str, repo: str, local_path: pathlib.Path, root: pathlib.Path) -> None:
    relative_path = str(local_path.relative_to(root)).replace("\\", "/")
    content = local_path.read_bytes()
    if len(content) > 100 * 1024 * 1024:
        print(f"Skipping large file: {relative_path}")
        return

    encoded = base64.b64encode(content).decode("utf-8")
    payload = {
        "message": f"Add {relative_path}",
        "content": encoded,
        "branch": "main",
    }

    sha = get_file_sha(owner, repo, relative_path)
    if sha:
        payload["sha"] = sha

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{relative_path}"
    response = SESSION.put(url, json=payload)
    response.raise_for_status()
    if sha:
        print(f"Updated {relative_path}")
    else:
        print(f"Created {relative_path}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python deploy_to_github.py <repo-name> [description]")
        raise SystemExit(1)

    repo_name = sys.argv[1].strip()
    description = " ".join(sys.argv[2:]).strip() or "AI CRM Automation Suite"

    owner = get_github_user()
    print(f"Authenticated as GitHub user: {owner}")
    create_repo(owner, repo_name, description)

    files = build_file_list(ROOT)
    print(f"Uploading {len(files)} files...")

    for index, file_path in enumerate(files, start=1):
        upload_file(owner, repo_name, file_path, ROOT)
        time.sleep(0.12)

    print(f"Deployment complete: https://github.com/{owner}/{repo_name}")


if __name__ == "__main__":
    main()
