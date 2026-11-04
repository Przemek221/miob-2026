"""Shared data and artifact primitives. No experiment workflow is selected here."""
import csv
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parent
FEATURES = ["free_rate", "money_rate", "remove_rate", "exclamation_rate", "dollar_rate", "capital_run_mean"]
THRESHOLD = 0.5
BASELINE_C = 0.01
SOURCE_FILES = ("components.py", "train.py", "predict.py", "evaluate.py", "check_run.py")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_rows(path):
    with Path(path).open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or any(r["label"] not in ("ham", "spam") for r in rows):
        raise ValueError("Expected nonempty labeled messages.")
    if len({r["message_id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate message identifiers.")
    return rows


def matrix(rows):
    # Explicit allowlist: neither label, ID nor raw text enters the model.
    return np.array([[float(row[name]) for name in FEATURES] for row in rows])


def labels(rows):
    return np.array([int(row["label"] == "spam") for row in rows])


def load_split(name):
    path = ROOT / "data" / (name + ".csv")
    manifest = json.loads((ROOT / "data/manifest.json").read_text())
    if sha(path) != manifest["files"][path.name]["sha256"]:
        raise ValueError("Data differs from the supplied split: " + name)
    return read_rows(path)


def counts(y, predicted):
    tp = sum(int(a == 1 and b == 1) for a, b in zip(y, predicted))
    tn = sum(int(a == 0 and b == 0) for a, b in zip(y, predicted))
    fp = sum(int(a == 0 and b == 1) for a, b in zip(y, predicted))
    fn = sum(int(a == 1 and b == 0) for a, b in zip(y, predicted))
    return {"n": len(y), "tp": tp, "tn": tn, "fp": fp, "fn": fn, "errors": fp + fn}


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_model(run):
    meta = read_json(run / "metadata.json")
    config = read_json(run / "config.json")
    if sha(run / "model.joblib") != meta["model_sha256"] or sha(run / "config.json") != meta["config_sha256"]:
        raise ValueError("Model or configuration changed after training.")
    if config != {"model": "StandardScaler + LogisticRegression", "C": BASELINE_C,
                  "features": FEATURES, "threshold": THRESHOLD}:
        raise ValueError("This lab uses one fixed model configuration.")
    if set(meta["source_sha256"]) != set(SOURCE_FILES):
        raise ValueError("Incomplete source record.")
    for name, digest in meta["source_sha256"].items():
        if sha(run / "source" / name) != digest or sha(ROOT / name) != digest:
            raise ValueError("Source changed after training: " + name)
    training = load_split(meta["training_data"])
    if sha(ROOT / "data" / (meta["training_data"] + ".csv")) != meta["train_sha256"]:
        raise ValueError("Training data changed.")
    # Load only trusted models generated in this course environment.
    model = joblib.load(run / "model.joblib")
    if model[-1].C != BASELINE_C or int(model[0].n_samples_seen_) != meta["train_rows"] or len(training) != meta["train_rows"]:
        raise ValueError("Model and training record disagree.")
    return model, meta


def read_predictions(run):
    with (run / "predictions.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    ids = [r["message_id"] for r in rows]
    if not rows or len(ids) != len(set(ids)):
        raise ValueError("Expected nonempty, unique predictions.")
    if any(r["prediction"] not in ("ham", "spam") for r in rows):
        raise ValueError("Invalid predicted label.")
    meta = read_json(run / "prediction-metadata.json")
    if sha(run / "predictions.csv") != meta["predictions_sha256"]:
        raise ValueError("Predictions changed after generation.")
    return rows, meta


def score_predictions(predictions, references):
    reference_by_id = {r["message_id"]: r["label"] for r in references}
    if {r["message_id"] for r in predictions} != set(reference_by_id):
        raise ValueError("Predictions and reference labels describe different messages.")
    actual = [int(reference_by_id[r["message_id"]] == "spam") for r in predictions]
    predicted = [int(r["prediction"] == "spam") for r in predictions]
    return counts(actual, predicted)
