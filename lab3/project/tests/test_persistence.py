"""Testy zapisu/odczytu modeli i pętli train -> evaluate (bramka E6).

Wszystkie testy używają danych syntetycznych albo kopii train w ``tmp_path``.
Prawdziwy `validation.csv` jest oceniany wyłącznie przez ``src.cli evaluate``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src import cli, data, model


def _synthetic_frame() -> pd.DataFrame:
    rows = []
    for index in range(24):
        if index % 3 == 0:
            text = f"Subject: win ${index} prize!!!\n\nClick http://1.2.3.4/offer now, free viagra"
            label = "spam"
        else:
            text = f"Subject: meeting notes {index}\n\nSee you at noon, project update."
            label = "ham"
        rows.append({"message_id": f"id-{index}", "text": text, "label": label})
    return pd.DataFrame(rows)


@pytest.mark.parametrize("key", model.SAVED_MODELS)
def test_model_roundtrip_preserves_predictions(tmp_path, key: str) -> None:
    frame = _synthetic_frame()
    pipeline = model.MODEL_FACTORIES[key]()
    pipeline.fit(frame["text"], frame["label"])
    expected = pipeline.predict(frame["text"])

    path = model.save_model(
        tmp_path / f"{key}.joblib",
        model_key=key,
        pipeline=pipeline,
        threshold=model.DEFAULT_THRESHOLDS[key],
        training_rows=len(frame),
    )
    bundle = model.load_model(path)
    labels, scores = model.predict_bundle(bundle, frame["text"])

    assert bundle["model_key"] == key
    assert bundle["trained_on"]["rows"] == len(frame)
    assert len(scores) == len(frame)
    assert (labels == expected).all()


def test_saved_bundle_contains_threshold_and_versions(tmp_path) -> None:
    frame = _synthetic_frame()
    pipeline = model.build_pipeline_v2().fit(frame["text"], frame["label"])
    bundle = model.load_model(
        model.save_model(
            tmp_path / "m.joblib", "v2", pipeline, threshold=0.5, training_rows=len(frame)
        )
    )
    assert bundle["threshold"] == 0.5
    assert bundle["positive_label"] == "spam"
    assert bundle["score"] == "predict_proba"
    assert set(bundle["versions"]) == {"python", "scikit_learn", "joblib"}


def test_threshold_changes_labels(tmp_path) -> None:
    frame = _synthetic_frame()
    pipeline = model.build_pipeline_v2().fit(frame["text"], frame["label"])
    bundle = model.load_model(
        model.save_model(tmp_path / "m.joblib", "v2", pipeline, 0.5, len(frame))
    )
    _, scores = model.predict_bundle(bundle, frame["text"])
    strict = dict(bundle, threshold=1.01)
    permissive = dict(bundle, threshold=-0.01)

    assert (model.predict_bundle(strict, frame["text"])[0] == "ham").all()
    assert (model.predict_bundle(permissive, frame["text"])[0] == "spam").all()
    assert scores.max() <= 1.0


def test_svc_threshold_uses_decision_function(tmp_path) -> None:
    frame = _synthetic_frame()
    pipeline = model.build_pipeline_v2_svc().fit(frame["text"], frame["label"])
    bundle = model.load_model(
        model.save_model(tmp_path / "svc.joblib", "v2_svc", pipeline, 0.0, len(frame))
    )
    assert bundle["score"] == "decision_function"
    labels, scores = model.predict_bundle(bundle, frame["text"])
    assert (labels == pipeline.predict(frame["text"])).all()
    assert np.issubdtype(scores.dtype, np.floating)


def test_load_model_rejects_incomplete_bundle(tmp_path) -> None:
    import joblib

    path = tmp_path / "broken.joblib"
    joblib.dump({"pipeline": None}, path)
    with pytest.raises(ValueError, match="nie ma pól"):
        model.load_model(path)


def test_pipeline_guard_blocks_dataframe_with_metadata() -> None:
    frame = _synthetic_frame()
    pipeline = model.build_pipeline_v2().fit(frame["text"], frame["label"])
    with pytest.raises(ValueError):
        pipeline.predict(frame[["message_id", "text"]])


def test_train_and_evaluate_write_expected_artifacts(tmp_path) -> None:
    """Cała ścieżka E6 na kopii danych w tmp_path (prawdziwa walidacja nietknięta)."""
    frame = _synthetic_frame()
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    train = frame.iloc[:16].reset_index(drop=True)
    validation = frame.iloc[16:].reset_index(drop=True)
    train.to_csv(data_dir / "train.csv", index=False, encoding="utf-8")
    validation.to_csv(data_dir / "validation.csv", index=False, encoding="utf-8")
    artifacts = tmp_path / "artifacts"

    assert cli.main(["train", "--data-dir", str(data_dir), "--artifacts-dir", str(artifacts)]) == 0
    for key in model.SAVED_MODELS:
        assert (artifacts / "models" / f"{key}.joblib").is_file()

    assert cli.main(["evaluate", "--data-dir", str(data_dir), "--artifacts-dir", str(artifacts)]) == 0
    for name in (
        "metrics.json",
        "predictions_validation.csv",
        "confusion_matrix_v2.csv",
        "errors_v2.csv",
        "training.json",
    ):
        assert (artifacts / name).is_file(), name

    import json

    metrics = json.loads((artifacts / "metrics.json").read_text(encoding="utf-8"))
    assert metrics["baseline"]["report"]["f1_spam"] == 0.0
    assert set(metrics["models"]) == set(model.SAVED_MODELS)
    assert metrics["evaluation_runs"] == 1
    assert all(report["predict_consistent"] for report in metrics["models"].values())

    predictions = pd.read_csv(artifacts / "predictions_validation.csv")
    assert len(predictions) == len(validation)


def test_predict_command_uses_saved_model(tmp_path, capsys) -> None:
    frame = _synthetic_frame()
    pipeline = model.build_pipeline_v2().fit(frame["text"], frame["label"])
    model.save_model(
        tmp_path / "models" / "v2.joblib", "v2", pipeline, 0.5, len(frame)
    )
    assert cli.main(
        [
            "predict",
            "--artifacts-dir",
            str(tmp_path),
            "--text",
            "Subject: free prize!!! click http://1.2.3.4/",
        ]
    ) == 0
    output = capsys.readouterr().out
    assert "model=v2" in output
    assert "score=" in output
