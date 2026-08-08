from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.experiment import create_experiment_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a new experiment config.")
    parser.add_argument("--from", dest="parent_experiment", help="parent experiment ID")
    parser.add_argument("--name", required=True, help="lowercase snake_case name")
    return parser


def main(argv: list[str] | None = None, *, root: Path = ROOT) -> int:
    args = build_parser().parse_args(argv)
    try:
        output_path = create_experiment_config(
            name=args.name,
            parent_experiment=args.parent_experiment,
            configs_dir=root / "configs",
            registry_path=root / "experiments" / "experiments.csv",
        )
    except (FileExistsError, FileNotFoundError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(f"created {output_path.relative_to(root)}")
    print("edit experiment.description, hypothesis, and notes before running it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
