"""Read-only structural and hash checks for the TabICLv2 explanation artifact."""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml.schema import FEATURES, ROOT, digest


RESULT = ROOT / "ml" / "experiments" / "tabicl_v2" / "explanation_pilot" / "result.json"
PROTOCOL = ROOT / "docs" / "tabicl_explanation_protocol.md"
RUNNER = ROOT / "scripts" / "research_tabicl_explanation.py"
SOURCE = ROOT / "data" / "raw" / "extention of Z-Alizadeh sani dataset.xlsx"
CHECKPOINT = ROOT / ".venv-tabicl" / "checkpoints" / "tabicl-classifier-v2-20260212.ckpt"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    require(result["complete"] is True, "The explanation run is incomplete.")
    require(result["source_workbook_sha256"] == digest(SOURCE), "Source workbook hash changed.")
    require(result["protocol_sha256"] == digest(PROTOCOL), "Frozen protocol hash changed.")
    require(result["runner_sha256"] == digest(RUNNER), "Runner hash changed.")
    require(result["checkpoint"]["sha256"] == digest(CHECKPOINT), "Checkpoint hash changed.")
    require(len(result["explanations"]) == 12, "Expected exactly 12 target/profile/seed explanations.")

    seen: set[tuple[str, str, int]] = set()
    max_reconstruction = 0.0
    for row in result["explanations"]:
        key = (row["target"], row["profile_name"], int(row["model_seed"]))
        require(key not in seen, f"Duplicate explanation case: {key}.")
        seen.add(key)
        explanation = row["explanation"]
        attribution = explanation["attributions_probability_points"]
        require(set(attribution) == set(FEATURES), f"Feature attribution schema differs for {key}.")
        require(len(explanation["permutation_orders_feature_names"]) == 4, f"Expected four paths for {key}.")
        for path in explanation["permutation_orders_feature_names"]:
            require(len(path) == len(FEATURES) and set(path) == set(FEATURES), f"Invalid permutation for {key}.")
        difference = float(explanation["profile_probability"] - explanation["mean_background_probability"])
        residual = abs(sum(float(value) for value in attribution.values()) - difference)
        recorded = float(explanation["maximum_absolute_reconstruction_residual"])
        require(residual <= 1e-8 and recorded <= 1e-8, f"Attribution does not reconstruct for {key}: {residual}.")
        for path_record in explanation["permutation_path_reconstruction_residuals"]:
            path_residual = abs(float(path_record["sum_minus_path_probability_difference"]))
            require(path_residual <= 1e-8, f"Permutation path does not telescope for {key}: {path_residual}.")
            max_reconstruction = max(max_reconstruction, path_residual)
        max_reconstruction = max(max_reconstruction, residual)
        require(all(math.isfinite(float(value)) for value in attribution.values()), f"Non-finite attribution for {key}.")

    expected = {
        (target, profile, int(seed))
        for target in ("cad", "lad", "lcx")
        for profile in result["profiles"]
        for seed in result["model_seeds"]
    }
    require(seen == expected, "Expected target/profile/model-seed cases are missing.")
    require(len(result["cache_parity_checks"]) == 6, "Expected six cached/uncached parity checks.")
    require(len(result["cross_seed_stability"]) == 6, "Expected six cross-seed comparisons.")

    print(json.dumps({
        "verified": True,
        "cases": len(seen),
        "cache_comparisons": len(result["cache_parity_checks"]),
        "maximum_cache_probability_difference": max(
            float(row["maximum_absolute_probability_difference"]) for row in result["cache_parity_checks"]
        ),
        "maximum_reconstruction_residual": max_reconstruction,
        "source_protocol_runner_checkpoint_hashes_match": True,
    }, indent=2))


if __name__ == "__main__":
    main()
