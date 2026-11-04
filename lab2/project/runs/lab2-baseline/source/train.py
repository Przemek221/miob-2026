"""Fit the supplied fixed model on a selected labeled dataset; save no predictions."""
import argparse
from pathlib import Path
import platform
import shutil
import warnings

import joblib
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from components import ROOT, FEATURES, THRESHOLD, BASELINE_C, SOURCE_FILES, labels, load_split, matrix, sha, write_json


def train(data, out):
    if out.exists():
        raise ValueError("Output directory already exists; preserve earlier evidence.")
    rows = load_split(data)
    model = make_pipeline(StandardScaler(), LogisticRegression(C=BASELINE_C, solver="lbfgs", max_iter=2000, random_state=2026))
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        model.fit(matrix(rows), labels(rows))
    out.mkdir(parents=True, exist_ok=False)
    joblib.dump(model, out / "model.joblib")
    write_json(out / "config.json", {"model": "StandardScaler + LogisticRegression", "C": BASELINE_C,
                                    "features": FEATURES, "threshold": THRESHOLD})
    (out / "source").mkdir()
    for name in SOURCE_FILES:
        shutil.copyfile(ROOT / name, out / "source" / name)
    write_json(out / "metadata.json", {
        "training_data": data, "train_sha256": sha(ROOT / "data" / (data + ".csv")),
        "train_rows": len(rows), "model_sha256": sha(out / "model.joblib"),
        "config_sha256": sha(out / "config.json"),
        "source_sha256": {name: sha(ROOT / name) for name in SOURCE_FILES},
        "python": platform.python_version(), "sklearn": sklearn.__version__,
    })
    print(f"Saved fitted model to {out}; training rows: {len(rows)}. Quality has not been evaluated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", choices=("train", "validation"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        train(args.data, args.out)
    except (ValueError, OSError, ConvergenceWarning) as error:
        parser.exit(1, f"Error: {error}\n")
