# Lab 2 — compose one spam classification experiment

Start with the Polish `assignment.md`. This project supplies separate Python scripts, not an end-to-end experiment command. With your agent, decide how to combine them to answer the task's question. Understand and agree on that plan before running the experiment. You do not need to implement or modify code.

## Setup

Open this `project` directory in the coding-agent application. Run commands here. Use Python 3.14 for the checked setup (macOS). Other Python versions and platforms require a pilot. No GPU is needed. Installation requires internet; experiment data are local.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

On Windows use `py -3 -m venv .venv` and `.venv\Scripts\python.exe` instead of `.venv/bin/python`. Use the environment's interpreter for all commands below. Ask the agent for help if setup fails; report the actual error to your instructor if blocked.

## Available data and model

- `data/train.csv`: the supplied training partition (180 messages).
- `data/validation.csv`: a separate partition (60 messages).
- `data/README.md`: feature meanings, partition roles, source and limitations.
- `components.py`: data loading, feature selection and artifact helpers; no full experiment procedure.

The model is fixed: scaling plus logistic regression, C=0.01, six numeric features and threshold 0.5. C is a training setting; varying it belongs to lab 3. The model receives neither the reference label, ID nor full email text as features. The label is the known answer; ID links a prediction to its original message. `p_spam` is a probability estimate, not a guarantee. Values at least 0.5 produce the predicted label `spam`.

## Script reference — choose operations for your plan

This is an inventory, not an execution sequence. Each script supports `--help`, for example `.venv/bin/python predict.py --help`. Replace `python` with your environment's interpreter when constructing commands.

| Script | Required arguments | What it does — and does not do |
|---|---|---|
| `check_run.py` | `--run` experiment directory | Checks complete artifacts against the lab's held-out evaluation goal. Does not create missing results. |
| `evaluate.py` | `--run` experiment directory; `--reference` dataset name | Joins existing predictions to reference labels by ID and writes mistake counts. Does not fit a model or generate predictions. |
| `predict.py` | `--run` experiment directory; `--data` dataset name | Uses the saved model to write predictions. Does not fit again or calculate mistake counts. |
| `train.py` | `--data` dataset name; `--out` new experiment directory | Fits the fixed model and its scaling on the chosen rows. Saves the model and configuration, but no predictions or quality score. |

Dataset names are `train` or `validation`, without the path or `.csv`. `--run` refers to the directory containing the model and that experiment's artifacts; `--out` creates it. Choose its name under `runs/`. All scripts for one experiment use that same directory. Inspect the input/output contracts and decide which dataset each operation needs; a permitted argument is not necessarily a suitable methodological choice.

The scripts will not overwrite an existing artifact. If a real failure prevents completion, retain the partial result and use a new directory when repeating the same experiment. This is not permission to search for better settings. A nonzero exit means the operation failed; a large mistake count is not an execution failure.

`predict.py` selects only feature columns even though the source CSV also contains labels. Its output has **no reference labels**. `evaluate.py` needs a separate reference argument; matching requires the same message IDs, not merely the same number of rows. It can calculate training-set mistakes too, so its successful execution alone does not establish evaluation on unseen messages.

## Artifacts you can inspect

| Artifact | Meaning |
|---|---|
| `config.json`, `model.joblib` | Fixed configuration and fitted model. Load only trusted course-generated models. |
| `metadata.json`, `source/` | Training dataset, hashes, runtime versions and source snapshot. |
| `predictions.csv` | Message ID, probability estimate and predicted label; find the reference label and full message in the source data by ID. |
| `prediction-metadata.json` | Which dataset and saved model generated the predictions. |
| `metrics.json`, `evaluation-metadata.json` | Mistake counts and the reference data used to calculate them. |

`tp`: spam predicted spam; `tn`: ham predicted ham; `fp`: ham predicted spam; `fn`: spam predicted ham. `errors = fp + fn`. Errors are weighted equally for this exercise; real-world costs can differ.

`check_run.py` checks the recorded model, data, source and predictions, recomputes counts, and rejects evaluation on training messages. PASS does not establish model usefulness, absence of every possible data leak, or performance on new populations. It does not assess your understanding or whether you planned before execution.

Prepared unit tests check fixed code examples, not your experiment's quality. Run them using `.venv/bin/python -m unittest discover -s tests -v`. Both tests and the checker are Python programs the agent runs through its terminal tool. Do not change code, data, dependencies or tests to obtain PASS.

## Tiny worked example

| Reference | Predicted | Meaning |
|---|---|---|
| ham | ham | TN |
| ham | spam | FP: legitimate mail diverted to spam |
| spam | ham | FN: spam left in the inbox |
| spam | spam | TP |

This example has two errors. One type may be absent in your real experiment; do not invent a missing example. No minimum predictive quality is required.

Technical references: [scikit-learn LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html), [data leakage and preprocessing](https://scikit-learn.org/stable/common_pitfalls.html). Reading the full API documentation is not required.
