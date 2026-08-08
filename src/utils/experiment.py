from __future__ import annotations

import csv
import copy
import json
import re
from pathlib import Path

import yaml

EXPERIMENT_ID_PATTERN = re.compile(r"^exp_(\d{3})_([a-z][a-z0-9]*(?:_[a-z0-9]+)*)$")
EXPERIMENT_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")


def validate_experiment_name(name: str) -> str:
    """Validate and return a lowercase snake_case experiment name."""
    if not EXPERIMENT_NAME_PATTERN.fullmatch(name):
        raise ValueError("experiment name must be lowercase snake_case")
    return name


def validate_experiment_id(experiment_id: str) -> str:
    """Validate and return an experiment ID."""
    if not EXPERIMENT_ID_PATTERN.fullmatch(experiment_id):
        raise ValueError("experiment ID must match exp_NNN_lowercase_snake_case")
    return experiment_id


def existing_experiment_ids(configs_dir: Path, registry_path: Path) -> set[str]:
    """Collect valid experiment IDs from config filenames and the registry."""
    experiment_ids = {
        path.stem
        for path in configs_dir.glob("*.yaml")
        if EXPERIMENT_ID_PATTERN.fullmatch(path.stem)
    }
    if registry_path.is_file():
        with registry_path.open(encoding="utf-8", newline="") as file:
            for row in csv.DictReader(file):
                experiment_id = (row.get("experiment_id") or "").strip()
                if EXPERIMENT_ID_PATTERN.fullmatch(experiment_id):
                    experiment_ids.add(experiment_id)
    return experiment_ids


def next_experiment_id(name: str, configs_dir: Path, registry_path: Path) -> str:
    """Return the next available sequential experiment ID."""
    validate_experiment_name(name)
    existing_ids = existing_experiment_ids(configs_dir, registry_path)
    numbers = [int(experiment_id.split("_", 2)[1]) for experiment_id in existing_ids]
    next_number = max(numbers, default=0) + 1
    if next_number > 999:
        raise ValueError("experiment sequence exhausted at exp_999")
    experiment_id = f"exp_{next_number:03d}_{name}"
    if experiment_id in existing_ids:
        raise FileExistsError(f"experiment already exists: {experiment_id}")
    return experiment_id


def load_experiment_config(config_path: Path) -> dict:
    """Load and minimally validate an experiment YAML file."""
    if not config_path.is_file():
        raise FileNotFoundError(f"config file not found: {config_path}")
    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ValueError(f"invalid YAML config: {config_path}") from error
    if not isinstance(config, dict):
        raise ValueError("config must be a mapping")
    experiment = config.get("experiment")
    if not isinstance(experiment, dict):
        raise ValueError("config experiment section must be a mapping")
    experiment_id = experiment.get("id")
    if not isinstance(experiment_id, str):
        raise ValueError("config experiment.id must be a string")
    validate_experiment_id(experiment_id)
    if config_path.stem != experiment_id:
        raise ValueError("config filename must match experiment.id")
    return config


def create_experiment_config(
    *,
    name: str,
    parent_experiment: str | None,
    configs_dir: Path,
    registry_path: Path,
) -> Path:
    """Create a self-contained config without overwriting an existing file."""
    experiment_id = next_experiment_id(name, configs_dir, registry_path)
    if parent_experiment is None:
        config: dict = {
            "experiment": {
                "id": experiment_id,
                "description": "TODO: describe this experiment",
                "hypothesis": "TODO: state the hypothesis",
                "notes": "TODO: describe the initial experiment",
                "parent_experiment": None,
                "role": "baseline" if experiment_id == "exp_001_baseline" else "candidate",
            }
        }
    else:
        validate_experiment_id(parent_experiment)
        parent_path = configs_dir / f"{parent_experiment}.yaml"
        config = copy.deepcopy(load_experiment_config(parent_path))
        config["experiment"].update(
            {
                "id": experiment_id,
                "description": "TODO: describe this experiment",
                "hypothesis": "TODO: state the hypothesis",
                "notes": "TODO: describe changes from the parent experiment",
                "parent_experiment": parent_experiment,
                "role": "candidate",
            }
        )

    configs_dir.mkdir(parents=True, exist_ok=True)
    output_path = configs_dir / f"{experiment_id}.yaml"
    with output_path.open("x", encoding="utf-8") as file:
        yaml.safe_dump(config, file, sort_keys=False, allow_unicode=True)
    return output_path


def is_completed_experiment(
    experiment_id: str, experiments_dir: Path, registry_path: Path
) -> bool:
    """Return whether an experiment is recorded as completed."""
    validate_experiment_id(experiment_id)
    metadata_path = experiments_dir / experiment_id / "metadata.json"
    if metadata_path.is_file():
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid experiment metadata: {metadata_path}") from error
        if isinstance(metadata, dict) and metadata.get("status") == "completed":
            return True

    if registry_path.is_file():
        with registry_path.open(encoding="utf-8", newline="") as file:
            for row in csv.DictReader(file):
                if (
                    row.get("experiment_id") == experiment_id
                    and row.get("status") == "completed"
                ):
                    return True
    return False
