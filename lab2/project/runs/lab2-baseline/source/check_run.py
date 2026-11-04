"""Check whether saved artifacts support this lab's held-out evaluation."""
import argparse
from pathlib import Path

import numpy as np

from components import ROOT, THRESHOLD, load_model, load_split, matrix, read_json, read_predictions, sha


def check(run):
    model, training_meta = load_model(run)
    predictions, prediction_meta = read_predictions(run)
    evaluation_meta = read_json(run / "evaluation-metadata.json")
    training = load_split(training_meta["training_data"])
    rows = load_split(prediction_meta["prediction_data"])
    assert not ({r["message_id"] for r in training} & {r["message_id"] for r in rows}), "Evaluation messages were used for training"
    assert training_meta["training_data"] == "train", "Use the supplied training partition for fitting"
    assert prediction_meta["prediction_data"] == evaluation_meta["reference_data"] == "validation", "Expected evaluation of the supplied held-out partition"
    assert prediction_meta["data_sha256"] == evaluation_meta["reference_sha256"] == sha(ROOT / "data/validation.csv"), "Wrong evaluation data"
    assert prediction_meta["model_sha256"] == training_meta["model_sha256"], "Wrong model identity"
    assert evaluation_meta["predictions_sha256"] == sha(run / "predictions.csv"), "Evaluation uses different predictions"
    assert len(predictions) == len(rows), "Missing predictions"
    probabilities = model.predict_proba(matrix(rows))[:, 1]
    actual = {"tp": 0, "tn": 0, "fp": 0, "fn": 0}
    for row, prediction, score in zip(rows, predictions, probabilities):
        assert prediction["message_id"] == row["message_id"], "Wrong message/order"
        assert np.isclose(float(prediction["p_spam"]), score, rtol=0, atol=1e-12), "Score/model disagreement"
        expected = "spam" if score >= THRESHOLD else "ham"
        assert prediction["prediction"] == expected, "Wrong class decision"
        key = ("tp" if expected == "spam" else "fn") if row["label"] == "spam" else ("fp" if expected == "spam" else "tn")
        actual[key] += 1
    actual.update(n=len(rows), errors=actual["fp"] + actual["fn"])
    assert read_json(run / "metrics.json") == actual, "Metrics disagree with predictions"
    print("PASS: artifacts support evaluation of the fixed model on the supplied held-out messages.")
    return actual


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    try:
        check(args.run)
    except (AssertionError, ValueError, KeyError, OSError) as error:
        parser.exit(1, f"FAIL: {error}\n")
