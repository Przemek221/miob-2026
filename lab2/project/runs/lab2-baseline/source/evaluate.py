"""Compare saved predictions with reference labels; do not train or predict."""
import argparse
import json
from pathlib import Path

from components import ROOT, load_split, read_predictions, score_predictions, sha, write_json


def evaluate(run, reference):
    if (run / "metrics.json").exists() or (run / "evaluation-metadata.json").exists():
        raise ValueError("Evaluation already exists; do not overwrite evidence.")
    predictions, _ = read_predictions(run)
    rows = load_split(reference)
    result = score_predictions(predictions, rows)
    write_json(run / "metrics.json", result)
    write_json(run / "evaluation-metadata.json", {
        "reference_data": reference, "reference_sha256": sha(ROOT / "data" / (reference + ".csv")),
        "predictions_sha256": sha(run / "predictions.csv"),
    })
    print(json.dumps(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--reference", choices=("train", "validation"), required=True)
    args = parser.parse_args()
    try:
        evaluate(args.run, args.reference)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Error: {error}\n")
