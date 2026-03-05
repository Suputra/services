# /// script
# dependencies = ["fastapi", "uvicorn"]
# ///
"""HTTP file service for s-term mounts — run with: uv run files.py"""

from fastapi import FastAPI, Request, Response
from pathlib import Path
import re
import subprocess
import uvicorn

MOUNTS = {
    "daily": "/home/saahas/saah.as/content/private/daily",
}

app = FastAPI()

SAFE_NAME_RE = re.compile(r"^[a-zA-Z0-9._-]+$")


def is_safe_filename(name: str) -> bool:
    if not name or not SAFE_NAME_RE.match(name):
        return False
    if name.startswith(".") or ".." in name:
        return False
    return True


def resolve_mount(mount: str) -> Path | None:
    base = MOUNTS.get(mount)
    if base is None:
        return None
    return Path(base)


def resolve_file(mount: str, name: str) -> Path | None:
    base = resolve_mount(mount)
    if base is None or not is_safe_filename(name):
        return None
    path = (base / name).resolve()
    if path.parent != base.resolve():
        return None
    return path


def find_git_root(path: Path) -> Path | None:
    current = path if path.is_dir() else path.parent
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return None


@app.get("/mounts")
async def list_mounts():
    return list(MOUNTS.keys())


@app.get("/m/{mount}/files")
async def list_files(mount: str):
    base = resolve_mount(mount)
    if base is None:
        return Response("unknown mount", status_code=404)
    if not base.exists():
        return []
    files = []
    for f in sorted(base.iterdir()):
        if f.is_file() and not f.name.startswith("."):
            files.append({"name": f.name, "size": f.stat().st_size})
    return files


@app.get("/m/{mount}/files/{name}")
async def get_file(mount: str, name: str):
    path = resolve_file(mount, name)
    if path is None:
        return Response("bad name", status_code=400)
    if not path.exists():
        return Response("", media_type="text/plain")
    return Response(path.read_text(encoding="utf-8"), media_type="text/plain")


@app.put("/m/{mount}/files/{name}")
async def put_file(mount: str, name: str, request: Request):
    path = resolve_file(mount, name)
    if path is None:
        return Response("bad name", status_code=400)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = await request.body()
    path.write_text(body.decode("utf-8"), encoding="utf-8")
    return {"ok": True, "size": len(body)}


@app.post("/m/{mount}/push")
async def push_mount(mount: str):
    base = resolve_mount(mount)
    if base is None:
        return Response("unknown mount", status_code=404)
    git_root = find_git_root(base)
    if git_root is None:
        return Response("no git repo", status_code=400)
    try:
        subprocess.run(["git", "add", "-A"], cwd=git_root, check=True, capture_output=True, timeout=10)
        result = subprocess.run(
            ["git", "commit", "-m", "update from s-term"],
            cwd=git_root, capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            if "nothing to commit" in result.stdout:
                return {"ok": True, "msg": "nothing to commit"}
            return Response(f"commit failed: {result.stderr}", status_code=500)
        result = subprocess.run(
            ["git", "push"],
            cwd=git_root, capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return Response(f"push failed: {result.stderr}", status_code=500)
        return {"ok": True, "msg": "pushed"}
    except subprocess.TimeoutExpired:
        return Response("timeout", status_code=500)
    except Exception as e:
        return Response(str(e), status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8200)
