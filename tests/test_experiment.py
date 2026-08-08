import csv
from pathlib import Path

import pytest
import yaml

from src.utils.experiment import (
    create_experiment_config,
    existing_experiment_ids,
    load_experiment_config,
    next_experiment_id,
    validate_experiment_name,
)


@pytest.mark.parametrize(
    "name",
    ["baseline", "add_feature_x", "model2_baseline"],
)
def test_validate_experiment_name_accepts_lowercase_snake_case(name: str) -> None:
    assert validate_experiment_name(name) == name


@pytest.mark.parametrize(
    "name",
    ["Add_feature", "add-feature", "_baseline", "baseline_", "two__words", "123_model"],
)
def test_validate_experiment_name_rejects_invalid_names(name: str) -> None:
    with pytest.raises(ValueError, match="lowercase snake_case"):
        validate_experiment_name(name)


def test_next_experiment_id_uses_configs_and_registry(tmp_path: Path) -> None:
    configs_dir = tmp_path / "configs"
    configs_dir.mkdir()
    (configs_dir / "exp_002_config_only.yaml").write_text("", encoding="utf-8")

    registry_path = tmp_path / "experiments.csv"
    with registry_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["experiment_id"])
        writer.writeheader()
        writer.writerow({"experiment_id": "exp_004_registry_only"})

    assert existing_experiment_ids(configs_dir, registry_path) == {
        "exp_002_config_only",
        "exp_004_registry_only",
    }
    assert next_experiment_id("new_test", configs_dir, registry_path) == "exp_005_new_test"


def test_create_experiment_config_copies_parent_and_resets_definition(tmp_path: Path) -> None:
    configs_dir = tmp_path / "configs"
    configs_dir.mkdir()
    parent_id = "exp_001_baseline"
    parent_config = {
        "experiment": {
            "id": parent_id,
            "description": "old description",
            "hypothesis": "old hypothesis",
            "notes": "old notes",
            "parent_experiment": None,
            "role": "baseline",
        },
        "model": {"name": "future-model", "params": {"depth": 3}},
    }
    (configs_dir / f"{parent_id}.yaml").write_text(
        yaml.safe_dump(parent_config, sort_keys=False), encoding="utf-8"
    )
    registry_path = tmp_path / "experiments.csv"
    registry_path.write_text("experiment_id\n", encoding="utf-8")

    output_path = create_experiment_config(
        name="add_feature_x",
        parent_experiment=parent_id,
        configs_dir=configs_dir,
        registry_path=registry_path,
    )

    created = yaml.safe_load(output_path.read_text(encoding="utf-8"))
    assert output_path.name == "exp_002_add_feature_x.yaml"
    assert created["experiment"] == {
        "id": "exp_002_add_feature_x",
        "description": "TODO: describe this experiment",
        "hypothesis": "TODO: state the hypothesis",
        "notes": "TODO: describe changes from the parent experiment",
        "parent_experiment": parent_id,
        "role": "candidate",
    }
    assert created["model"] == parent_config["model"]

    original_text = output_path.read_text(encoding="utf-8")
    second_path = create_experiment_config(
        name="add_feature_x",
        parent_experiment=parent_id,
        configs_dir=configs_dir,
        registry_path=registry_path,
    )
    assert second_path.name == "exp_003_add_feature_x.yaml"
    assert output_path.read_text(encoding="utf-8") == original_text


def test_load_experiment_config_rejects_malformed_and_mismatched_config(
    tmp_path: Path,
) -> None:
    malformed = tmp_path / "exp_001_baseline.yaml"
    malformed.write_text("experiment: []\n", encoding="utf-8")
    with pytest.raises(ValueError, match="experiment.*mapping"):
        load_experiment_config(malformed)

    mismatched = tmp_path / "exp_001_baseline.yaml"
    mismatched.write_text(
        "experiment:\n  id: exp_002_other\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="filename"):
        load_experiment_config(mismatched)
