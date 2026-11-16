"""Punkt wejścia CLI: ``python -m src.cli <komenda>``.

Komendy:
    baseline   E2: model odniesienia (DummyClassifier) + CV, artifacts/baseline.json
    cv         E3–E4: walidacja krzyżowa wybranego modelu na train
    ablate     E4: ablacja wariantów cech/modeli na train
    train      E6: trening trzech modeli na pełnym train + zapis artifacts/models/*.joblib
    evaluate   E6: JEDNORAZOWA ocena na validation.csv, artifacts/metrics.json + raporty
    predict    ponowne użycie zapisanego modelu (bez trenowania)

Zasada: `validation.csv` czytamy wyłącznie w ``evaluate``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from . import data, evaluate, model
from .config import ARTIFACTS_DIR, DATA_DIR, N_SPLITS, SEED


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m src.cli",
        description=(
            "Klasyfikator spamu (spam/ham) trenowany wyłącznie na kolumnie 'text' "
            "z data/train.csv. Zbiór validation.csv oceniany jest tylko raz, na końcu."
        ),
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Tryb offline: pipeline nie wykonuje żadnych żądań sieciowych (domyślnie włączony).",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<komenda>")
    subparsers.required = True

    baseline = subparsers.add_parser(
        "baseline",
        help="Model odniesienia: DummyClassifier(strategy='most_frequent') + CV na train.",
    )
    _add_common_options(baseline)

    cv = subparsers.add_parser(
        "cv",
        help="Walidacja krzyżowa modelu na train (bez dotykania validation.csv).",
    )
    _add_common_options(cv)
    cv.add_argument(
        "--model", choices=sorted(model.MODEL_FACTORIES), default="v1", help="Który model CV-ować."
    )
    cv.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Ścieżka wyniku (domyślnie artifacts/cv_<model>.json).",
    )

    ablate = subparsers.add_parser(
        "ablate",
        help="Ablacja wariantów cech/modeli (E4) — CV na train, zapis artifacts/ablation.json.",
    )
    _add_common_options(ablate)
    ablate.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Ścieżka wyniku (domyślnie artifacts/ablation.json).",
    )

    train = subparsers.add_parser(
        "train",
        help="Trenuje modele A/B/C na train i zapisuje je do artifacts/models/.",
    )
    _add_common_options(train)

    evaluation = subparsers.add_parser(
        "evaluate",
        help="Jednorazowa ocena zapisanych modeli na validation.csv.",
    )
    _add_common_options(evaluation)

    predict = subparsers.add_parser(
        "predict",
        help="Klasyfikuje nowy tekst zapisanym modelem (bez trenowania).",
    )
    _add_common_options(predict)
    predict.add_argument(
        "--model",
        choices=list(model.SAVED_MODELS),
        default="v2",
        help="Który zapisany model użyć (domyślnie v2).",
    )
    predict.add_argument(
        "--text",
        default=None,
        help="Pojedyncza wiadomość (dla wielu użyj --file).",
    )
    predict.add_argument(
        "--file",
        type=Path,
        default=None,
        help="Plik CSV z kolumną 'text' albo plik TXT (wiadomości rozdzielone linią '---').",
    )

    return parser


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR, help="Katalog z CSV (tylko odczyt).")
    parser.add_argument(
        "--artifacts-dir", type=Path, default=ARTIFACTS_DIR, help="Katalog na wyniki i modele."
    )
    parser.add_argument("--seed", type=int, default=SEED, help="Ziarno losowania.")
    parser.add_argument(
        "--n-splits", type=int, default=N_SPLITS, help="Liczba foldów walidacji krzyżowej."
    )


def _models_dir(artifacts_dir: Path) -> Path:
    return Path(artifacts_dir) / "models"


def run_baseline(args: argparse.Namespace) -> int:
    """E2: baseline na `train` (CV), zapis ``artifacts/baseline.json``."""
    train = data.load_csv(args.data_dir / "train.csv", "train.csv")

    cv = model.cross_validate_estimator(
        model.build_baseline, train, n_splits=args.n_splits, seed=args.seed
    )
    payload = {
        "stage": "E2",
        "model": "DummyClassifier(strategy='most_frequent')",
        "seed": args.seed,
        "positive_label": data.LABELS[1],
        "data": {
            "file": "train.csv",
            "rows": int(len(train)),
            "label_counts": data.label_counts(train),
        },
        "cv": cv,
        "notes": (
            "Baseline przewiduje zawsze klasę większościową (ham), więc "
            "precision/recall/F1 dla spam wynoszą 0, a ROC-AUC/PR-AUC są "
            "nieinformacyjne (stały score). To podłoga dla modeli właściwych."
        ),
    }
    path = evaluate.save_json(payload, Path(args.artifacts_dir) / "baseline.json")

    summary = cv["summary"]["f1_spam"]
    accuracy = cv["summary"]["accuracy"]
    print(
        f"baseline: f1_spam={summary['mean']:.3f}±{summary['std']:.3f} "
        f"accuracy={accuracy['mean']:.3f}±{accuracy['std']:.3f} "
        f"({cv['n_splits']}-fold, seed={args.seed}) -> {path}"
    )
    return 0


def run_cv(args: argparse.Namespace) -> int:
    """E3–E4: walidacja krzyżowa modelu na `train`, zapis ``artifacts/cv_<model>.json``."""
    train = data.load_csv(args.data_dir / "train.csv", "train.csv")
    factory = model.MODEL_FACTORIES[args.model]

    cv = model.cross_validate_estimator(factory, train, n_splits=args.n_splits, seed=args.seed)
    payload = {
        "stage": "E3" if args.model == "v1" else "E4",
        "model_key": args.model,
        "model": model.MODEL_DESCRIPTIONS[args.model],
        "seed": args.seed,
        "positive_label": data.LABELS[1],
        "data": {
            "file": "train.csv",
            "rows": int(len(train)),
            "label_counts": data.label_counts(train),
        },
        "cv": cv,
        "threshold": None,
    }
    output = args.output or (Path(args.artifacts_dir) / f"cv_{args.model}.json")
    path = evaluate.save_json(payload, output)

    summary = cv["summary"]
    print(
        f"cv[{args.model}]: f1_spam={summary['f1_spam']['mean']:.3f}±{summary['f1_spam']['std']:.3f} "
        f"precision_spam={summary['precision_spam']['mean']:.3f} "
        f"recall_spam={summary['recall_spam']['mean']:.3f} "
        f"pr_auc={_fmt(summary['pr_auc']['mean'])} "
        f"accuracy={summary['accuracy']['mean']:.3f} "
        f"({cv['n_splits']}-fold, seed={args.seed}) -> {path}"
    )
    return 0


def _fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def run_ablate(args: argparse.Namespace) -> int:
    """E4: ablacja — który element daje przyrost F1(spam) na CV?"""
    train = data.load_csv(args.data_dir / "train.csv", "train.csv")

    rows: list[dict] = []
    details: dict[str, dict] = {}
    for key in model.ABLATION_VARIANTS:
        cv = model.cross_validate_estimator(
            model.MODEL_FACTORIES[key], train, n_splits=args.n_splits, seed=args.seed
        )
        summary = cv["summary"]
        rows.append(
            {
                "model": key,
                "description": model.MODEL_DESCRIPTIONS[key]["name"],
                "f1_spam": summary["f1_spam"]["mean"],
                "f1_spam_std": summary["f1_spam"]["std"],
                "precision_spam": summary["precision_spam"]["mean"],
                "recall_spam": summary["recall_spam"]["mean"],
                "pr_auc": summary["pr_auc"]["mean"],
                "roc_auc": summary["roc_auc"]["mean"],
                "accuracy": summary["accuracy"]["mean"],
            }
        )
        details[key] = cv
        print(
            f"  {key:9s} f1={_fmt(summary['f1_spam']['mean'])}"
            f"±{_fmt(summary['f1_spam']['std'])} prec={_fmt(summary['precision_spam']['mean'])}"
            f" rec={_fmt(summary['recall_spam']['mean'])} pr_auc={_fmt(summary['pr_auc']['mean'])}"
        )

    payload = {
        "stage": "E4",
        "seed": args.seed,
        "positive_label": data.LABELS[1],
        "data": {
            "file": "train.csv",
            "rows": int(len(train)),
            "label_counts": data.label_counts(train),
        },
        "baseline_f1_spam": 0.0,
        "table": rows,
        "cv": details,
        "notes": (
            "Ablacja na train (5-fold). Warianty różnią się tylko reprezentacją: "
            "v1=TF-IDF word+NB, v1_lr=TF-IDF word+LogReg, v2_char=+char 3-5, "
            "v2=+cechy inżynieryjne, v2_svc=LinearSVC. Brak cech zakazanych: "
            "wejściem jest wyłącznie kolumna text."
        ),
    }
    path = evaluate.save_json(
        payload, args.output or (Path(args.artifacts_dir) / "ablation.json")
    )
    print(f"ablation -> {path}")
    return 0


def run_train(args: argparse.Namespace) -> int:
    """E6a: trening modeli A/B/C na całym `train` + zapis do ``artifacts/models/``.

    Hiperparametry są te z E4 (E5 pominięty decyzją prowadzącego), próg jest
    domyślny i **zapisywany razem z modelem**, żeby ponowne użycie było spójne
    z oceną.
    """
    train = data.load_csv(args.data_dir / "train.csv", "train.csv")
    models_dir = _models_dir(args.artifacts_dir)
    saved: dict[str, dict] = {}

    for key in model.SAVED_MODELS:
        pipeline = model.MODEL_FACTORIES[key]()
        pipeline.fit(train["text"], train["label"])
        threshold = model.DEFAULT_THRESHOLDS[key]
        path = model.save_model(
            models_dir / f"{key}.joblib",
            model_key=key,
            pipeline=pipeline,
            threshold=threshold,
            training_rows=len(train),
        )
        saved[key] = {
            "file": f"models/{key}.joblib",
            "threshold": threshold,
            "score": model.score_kind(pipeline),
            "config": model.MODEL_DESCRIPTIONS[key],
            "n_features": int(_n_features(pipeline)),
        }
        print(f"  zapisano {path} (próg={threshold})")

    payload = {
        "stage": "E6",
        "seed": args.seed,
        "positive_label": data.LABELS[1],
        "trained_on": {
            "file": "train.csv",
            "rows": int(len(train)),
            "label_counts": data.label_counts(train),
        },
        "models": saved,
        "hyperparameter_search": "pominięty (E5 świadomie odpuszczony) — parametry z E4",
        "threshold_selection": "brak dostrajania — progi domyślne zapisane z modelem",
        "cv_reference": {
            "file": "cv_v2.json",
            "f1_spam": 0.951,
            "source": "E4 ablation.json / cv_v2.json",
        },
    }
    path = evaluate.save_json(payload, Path(args.artifacts_dir) / "training.json")
    print(f"trening -> {path}")
    return 0


def _n_features(pipeline) -> int:
    """Liczba kolumn wejściowych do klasyfikatora (diagnostyka)."""
    try:
        return int(pipeline.named_steps["clf"].n_features_in_)
    except (AttributeError, KeyError):
        return -1


def _error_rows(validation: pd.DataFrame, labels, scores) -> pd.DataFrame:
    """Błędne predykcje: ID, prawda, predykcja, score i krótki fragment tematu."""
    table = pd.DataFrame(
        {
            "message_id": validation["message_id"].to_numpy(),
            "true_label": validation["label"].to_numpy(),
            "predicted_label": labels,
            "score_spam": scores,
            "subject": [
                line.splitlines()[0][:160] if line else ""
                for line in validation["text"].to_numpy()
            ],
        }
    )
    return table[table["true_label"] != table["predicted_label"]].reset_index(drop=True)


def run_evaluate(args: argparse.Namespace) -> int:
    """E6b: **jednorazowa** ocena zapisanych modeli na `validation.csv`.

    Zapisuje ``artifacts/metrics.json`` (baseline + trzy modele + seed),
    macierze pomyłek i listy błędnych predykcji per model oraz wspólną
    tabelę predykcji dla walidacji.
    """
    train = data.load_csv(args.data_dir / "train.csv", "train.csv")
    validation = data.load_csv(args.data_dir / "validation.csv", "validation.csv")

    bundles = {
        key: model.load_model(_models_dir(args.artifacts_dir) / f"{key}.joblib")
        for key in model.SAVED_MODELS
    }

    # Baseline: dopasowany na train, oceniony na tych samych wierszach walidacji.
    baseline = model.build_baseline().fit(train["text"], train["label"])
    baseline_pred = baseline.predict(validation["text"])
    baseline_report = evaluate.report(validation["label"], baseline_pred, None)

    artifacts_dir = Path(args.artifacts_dir)
    model_reports: dict[str, dict] = {}
    predictions = pd.DataFrame(
        {
            "message_id": validation["message_id"].to_numpy(),
            "true_label": validation["label"].to_numpy(),
        }
    )
    errors_summary: dict[str, int] = {}

    for key, bundle in bundles.items():
        labels, scores = model.predict_bundle(bundle, validation["text"])
        report = evaluate.report(
            validation["label"], labels, scores, threshold=bundle["threshold"]
        )
        # Spójność: etykiety z progu muszą zgadzać się z predict() pipeline'u.
        direct = bundle["pipeline"].predict(validation["text"])
        report["predict_consistent"] = bool((direct == labels).all())
        report["model_key"] = key
        report["model_name"] = bundle["model_name"]
        model_reports[key] = report

        predictions[f"{key}_pred"] = labels
        predictions[f"{key}_score"] = scores

        evaluate.save_confusion_matrix_csv(
            report["confusion_matrix"], artifacts_dir / f"confusion_matrix_{key}.csv"
        )
        errors = _error_rows(validation, labels, scores)
        errors.to_csv(artifacts_dir / f"errors_{key}.csv", index=False, encoding="utf-8")
        errors_summary[key] = int(len(errors))

        print(
            f"  {key:7s} f1_spam={report['f1_spam']:.3f} "
            f"prec={report['precision_spam']:.3f} rec={report['recall_spam']:.3f} "
            f"acc={report['accuracy']:.3f} pr_auc={_fmt(report['pr_auc'])} "
            f"błędów={len(errors)} (próg={bundle['threshold']})"
        )

    predictions.to_csv(artifacts_dir / "predictions_validation.csv", index=False, encoding="utf-8")

    final_model = "v2"
    payload = {
        "stage": "E6",
        "seed": args.seed,
        "positive_label": data.LABELS[1],
        "evaluated_file": "validation.csv",
        "evaluation_runs": 1,
        "n_validation_rows": int(len(validation)),
        "label_counts": data.label_counts(validation),
        "threshold_selection": "brak (E5 pominięty); próg domyślny zapisany z modelem",
        "final_model": final_model,
        "baseline": {
            "model": "DummyClassifier(strategy='most_frequent')",
            "threshold": 0.5,
            "report": baseline_report,
        },
        "models": model_reports,
        "errors_count": errors_summary,
        "files": {
            "training": "training.json",
            "predictions": "predictions_validation.csv",
            "confusion_matrices": [f"confusion_matrix_{key}.csv" for key in model_reports],
            "errors": [f"errors_{key}.csv" for key in model_reports],
            "models": [f"models/{key}.joblib" for key in model_reports],
        },
        "notes": (
            "Ocena wykonana raz, po zamrożeniu modeli zapisanych w artifacts/models/. "
            "Modele trenowane wyłącznie na train.csv; validation.csv użyte tylko tutaj. "
            "Wynik na małym, historycznym zbiorze (2003) — nie przenosi się wprost "
            "na współczesną pocztę."
        ),
    }
    path = evaluate.save_json(payload, artifacts_dir / "metrics.json")
    print(f"ocena -> {path}")
    return 0


def _load_predict_texts(args: argparse.Namespace) -> list[str]:
    texts: list[str] = []
    if args.text:
        texts.append(args.text)
    if args.file:
        path = Path(args.file)
        if path.suffix.lower() == ".csv":
            frame = pd.read_csv(path, dtype=str, keep_default_na=False)
            if "text" not in frame.columns:
                raise SystemExit(f"Plik {path} nie ma kolumny 'text'")
            texts.extend(frame["text"].tolist())
        else:
            content = path.read_text(encoding="utf-8")
            texts.extend(part.strip("\n") for part in content.split("\n---\n") if part.strip())
    return texts


def run_predict(args: argparse.Namespace) -> int:
    """Klasyfikacja nowego tekstu zapisanym modelem — bez trenowania i bez danych z data/."""
    texts = _load_predict_texts(args)
    if not texts:
        raise SystemExit("Podaj --text albo --file")

    bundle = model.load_model(_models_dir(args.artifacts_dir) / f"{args.model}.joblib")
    labels, scores = model.predict_bundle(bundle, texts)
    print(f"model={args.model} threshold={bundle['threshold']} score={bundle['score']}")
    for index, (label, score, text) in enumerate(zip(labels, scores, texts), start=1):
        first_line = text.splitlines()[0][:80] if text else ""
        print(f"{index:3d}. {label:4s} score={score:.4f}  {first_line}")
    return 0


COMMANDS = {
    "baseline": run_baseline,
    "cv": run_cv,
    "ablate": run_ablate,
    "train": run_train,
    "evaluate": run_evaluate,
    "predict": run_predict,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = COMMANDS.get(args.command)
    if handler is None:
        parser.error(f"komenda '{args.command}' nie jest jeszcze zaimplementowana")
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
