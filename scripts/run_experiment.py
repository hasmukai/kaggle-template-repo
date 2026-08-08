from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.experiment import is_completed_experiment, load_experiment_config
from src.utils.git import GitState, get_git_state


@dataclass(frozen=True)
class ExecutionContext:
    config: dict
    experiment_id: str
    git: GitState


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one CV experiment.")
    parser.add_argument("--config", required=True, type=Path, help="experiment YAML")
    return parser


def prepare_execution(config_path: Path, root: Path) -> ExecutionContext:
    """Validate immutable inputs and collect provenance before the future pipeline."""
    config = load_experiment_config(config_path)
    experiment_id = config["experiment"]["id"]
    registry_path = root / "experiments" / "experiments.csv"
    if is_completed_experiment(experiment_id, root / "experiments", registry_path):
        raise FileExistsError(
            f"completed experiment will not be overwritten: {experiment_id}"
        )
    return ExecutionContext(
        config=config,
        experiment_id=experiment_id,
        git=get_git_state(root),
    )


def run_pipeline(context: ExecutionContext) -> None:
    """Future extension point: preprocessing -> features -> CV -> persistence."""
    del context
    print("experiment pipeline is not implemented yet")


def main(argv: list[str] | None = None, *, root: Path = ROOT) -> int:
    args = build_parser().parse_args(argv)
    config_path = args.config
    if not config_path.is_absolute():
        config_path = root / config_path
    try:
        context = prepare_execution(config_path, root)
    except (FileExistsError, FileNotFoundError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    run_pipeline(context)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
