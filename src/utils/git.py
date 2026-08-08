from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GitState:
    commit: str | None
    dirty: bool
    diff: str


def _run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=check,
        capture_output=True,
        text=True,
        errors="surrogateescape",
    )


def _untracked_diff(repo: Path) -> str:
    """Return binary-safe patches that create every non-ignored untracked file."""
    untracked = _run_git(
        repo, "ls-files", "--others", "--exclude-standard", "-z"
    ).stdout.split("\0")
    patches: list[str] = []
    for relative_path in filter(None, untracked):
        untracked_path = repo / relative_path.rstrip("/")
        if untracked_path.is_dir() and (untracked_path / ".git").exists():
            raise RuntimeError(
                "cannot capture untracked nested Git repository: "
                f"{relative_path.rstrip('/')}"
            )
        result = _run_git(
            repo,
            "diff",
            "--no-index",
            "--binary",
            "--",
            "/dev/null",
            relative_path,
            check=False,
        )
        if result.returncode not in (0, 1):
            raise RuntimeError(f"failed to capture untracked file: {relative_path}")
        patches.append(result.stdout)
    return "".join(patches)


def get_git_state(repo: Path) -> GitState:
    """Return the current commit, dirty state, and reproducible working-tree diff."""
    inside = _run_git(repo, "rev-parse", "--is-inside-work-tree", check=False)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        raise RuntimeError(f"not a Git working tree: {repo}")

    commit_result = _run_git(repo, "rev-parse", "--verify", "HEAD", check=False)
    commit = commit_result.stdout.strip() if commit_result.returncode == 0 else None
    status = _run_git(repo, "status", "--porcelain").stdout
    if commit is None:
        empty_tree = _run_git(repo, "hash-object", "-t", "tree", "/dev/null").stdout.strip()
        tracked_diff = _run_git(repo, "diff", empty_tree, "--binary", "--").stdout
    else:
        tracked_diff = _run_git(repo, "diff", "HEAD", "--binary", "--").stdout
    diff = tracked_diff + _untracked_diff(repo)
    return GitState(commit=commit, dirty=bool(status.strip()), diff=diff)
