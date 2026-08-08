import os
import subprocess
from pathlib import Path

import pytest

from src.utils.git import get_git_state


def run_git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def test_get_git_state_reports_commit_dirty_state_and_diff(tmp_path: Path) -> None:
    run_git(tmp_path, "init", "-q")
    run_git(tmp_path, "config", "user.name", "Test User")
    run_git(tmp_path, "config", "user.email", "test@example.com")
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("before\n", encoding="utf-8")
    run_git(tmp_path, "add", "tracked.txt")
    run_git(tmp_path, "commit", "-qm", "initial")

    clean = get_git_state(tmp_path)
    assert clean.commit is not None
    assert clean.dirty is False
    assert clean.diff == ""

    tracked.write_text("after\n", encoding="utf-8")
    dirty = get_git_state(tmp_path)
    assert dirty.commit == clean.commit
    assert dirty.dirty is True
    assert "-before" in dirty.diff
    assert "+after" in dirty.diff


def test_get_git_state_includes_untracked_files_without_head(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    run_git(repo, "init", "-q")
    (repo / "new.py").write_text("print('untracked')\n", encoding="utf-8")

    state = get_git_state(repo)

    assert state.commit is None
    assert state.dirty is True
    assert "new.py" in state.diff
    assert "+print('untracked')" in state.diff


def test_get_git_state_diff_reconstructs_tracked_and_untracked_changes(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    run_git(repo, "init", "-q")
    run_git(repo, "config", "user.name", "Test User")
    run_git(repo, "config", "user.email", "test@example.com")
    tracked = repo / "tracked.txt"
    tracked.write_text("before\n", encoding="utf-8")
    run_git(repo, "add", "tracked.txt")
    run_git(repo, "commit", "-qm", "initial")

    reconstruction = tmp_path / "reconstruction"
    subprocess.run(
        ["git", "clone", "-q", str(repo), str(reconstruction)],
        check=True,
        capture_output=True,
        text=True,
    )
    tracked.write_text("after\n", encoding="utf-8")
    (repo / "untracked.txt").write_text("new content\n", encoding="utf-8")
    binary_content = bytes(range(256))
    (repo / "untracked.bin").write_bytes(binary_content)

    state = get_git_state(repo)
    patch_path = tmp_path / "state.patch"
    patch_path.write_text(state.diff, encoding="utf-8")
    run_git(reconstruction, "apply", str(patch_path))

    assert (reconstruction / "tracked.txt").read_text(encoding="utf-8") == "after\n"
    assert (reconstruction / "untracked.txt").read_text(encoding="utf-8") == "new content\n"
    assert (reconstruction / "untracked.bin").read_bytes() == binary_content


def test_get_git_state_without_head_uses_latest_staged_file_content(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    run_git(repo, "init", "-q")
    staged = repo / "staged.txt"
    staged.write_text("staged version\n", encoding="utf-8")
    run_git(repo, "add", "staged.txt")
    staged.write_text("working-tree version\n", encoding="utf-8")

    state = get_git_state(repo)

    assert "+working-tree version" in state.diff
    assert "+staged version" not in state.diff


def test_get_git_state_preserves_non_utf8_untracked_filename(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    run_git(repo, "init", "-q")
    raw_name = b"bad-\xff.txt"
    file_descriptor = os.open(os.fsencode(repo) + b"/" + raw_name, os.O_WRONLY | os.O_CREAT)
    with os.fdopen(file_descriptor, "wb") as file:
        file.write(b"content\n")

    state = get_git_state(repo)
    reconstruction = tmp_path / "reconstruction"
    reconstruction.mkdir()
    run_git(reconstruction, "init", "-q")
    patch_path = tmp_path / "state.patch"
    patch_path.write_text(state.diff, encoding="utf-8", errors="surrogateescape")
    run_git(reconstruction, "apply", str(patch_path))

    reconstructed_names = os.listdir(os.fsencode(reconstruction))
    assert raw_name in reconstructed_names


def test_get_git_state_rejects_untracked_nested_git_repository(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    run_git(repo, "init", "-q")
    nested = repo / "nested"
    nested.mkdir()
    run_git(nested, "init", "-q")
    (nested / "code.py").write_text("print('nested')\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="nested Git repository"):
        get_git_state(repo)
