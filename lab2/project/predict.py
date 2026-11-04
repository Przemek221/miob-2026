"""Use a saved model on selected messages; labels are not passed to the model."""
import argparse
import csv
from pathlib import Path

from components import ROOT, THRESHOLD, load_model, load_split, matrix, sha, write_json


def predict(run, data):
    if (run / "predictions.csv").exists() or (run / "prediction-metadata.json").exists():
        raise ValueError("Predictions already exist; do not overwrite evidence.")
    model, training_meta = load_model(run)
    rows = load_split(data)
    probabilities = model.predict_proba(matrix(rows))[:, 1]
    with (run / "predictions.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["message_id", "p_spam", "prediction"])
        for row, score in zip(rows, probabilities):
            writer.writerow([row["message_id"], float(score), "spam" if score >= THRESHOLD else "ham"])
    write_json(run / "prediction-metadata.json", {
        "prediction_data": data, "data_sha256": sha(ROOT / "data" / (data + ".csv")),
        "model_sha256": training_meta["model_sha256"], "predictions_sha256": sha(run / "predictions.csv"),
    })
    print(f"Saved {len(rows)} predictions to {run}. No model fitting or quality evaluation performed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--data", choices=("train", "validation"), required=True)
    args = parser.parse_args()
    try:
        predict(args.run, args.data)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Error: {error}\n")
