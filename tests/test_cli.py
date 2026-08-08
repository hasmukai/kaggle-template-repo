import subprocess
from pathlib import Path

import yaml

from scripts.make_submission import main as make_submission_main
from scripts.new_experiment import main as new_experiment_main
from scripts.run_experiment import main as run_experiment_main


REGISTRY_HEADER = (
    "experiment_id,parent_experiment,description,hypothesis,status,role,cv_scheme,"
    "cv_score,cv_std,model,num_trials,duration_sec,git_commit,git_dirty,created_at\n"
)


def initialize_root(root: Path) -> None:
    subprocess.run(
        ["git", "init", "-q"], cwd=root, check=True, capture_output=True, text=True
    )
    (root / "configs").mkdir()
    (root / "experiments").mkdir()
    (root / "experiments" / "experiments.csv").write_text(
        REGISTRY_HEADER, encoding="utf-8"
    )


def test_new_experiment_cli_creates_initial_config(tmp_path: Path) -> None:
    initialize_root(tmp_path)

    assert new_experiment_main(["--name", "baseline"], root=tmp_path) == 0

    config_path = tmp_path / "configs" / "exp_001_baseline.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert config["experiment"]["id"] == "exp_001_baseline"
    assert config["experiment"]["parent_experiment"] is None


def test_run_experiment_cli_refuses_completed_experiment(
    tmp_path: Path, capsys
) -> None:
    initialize_root(tmp_path)
    config_path = tmp_path / "configs" / "exp_001_baseline.yaml"
    config_path.write_text("experiment:\n  id: exp_001_baseline\n", encoding="utf-8")
    result_dir = tmp_path / "experiments" / "exp_001_baseline"
    result_dir.mkdir()
    (result_dir / "metadata.json").write_text(
        '{"status": "completed"}\n', encoding="utf-8"
    )

    assert run_experiment_main(["--config", str(config_path)], root=tmp_path) == 2
    assert "completed experiment will not be overwritten" in capsys.readouterr().err


def test_pipeline_entry_points_validate_then_report_not_implemented(
    tmp_path: Path, capsys
) -> None:
    initialize_root(tmp_path)
    config_path = tmp_path / "configs" / "exp_001_baseline.yaml"
    config_path.write_text("experiment:\n  id: exp_001_baseline\n", encoding="utf-8")

    assert run_experiment_main(["--config", str(config_path)], root=tmp_path) == 0
    assert "experiment pipeline is not implemented yet" in capsys.readouterr().out

    assert make_submission_main(
        ["--experiment", "exp_001_baseline"], root=tmp_path
    ) == 0
    assert "submission pipeline is not implemented yet" in capsys.readouterr().out

    assert make_submission_main(["--experiment", "exp_999_missing"], root=tmp_path) == 2
    assert "experiment not found" in capsys.readouterr().err
