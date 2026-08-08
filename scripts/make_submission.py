from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.experiment import validate_experiment_id


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a competition submission.")
    parser.add_argument("--experiment", required=True, help="source experiment ID")
    return parser


def main(argv: list[str] | None = None, *, root: Path = ROOT) -> int:
    args = build_parser().parse_args(argv)
    try:
        experiment_id = validate_experiment_id(args.experiment)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    config_exists = (root / "configs" / f"{experiment_id}.yaml").is_file()
    result_exists = (root / "experiments" / experiment_id).is_dir()
    if not config_exists and not result_exists:
        print(f"error: experiment not found: {experiment_id}", file=sys.stderr)
        return 2

    print("submission pipeline is not implemented yet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
