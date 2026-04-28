---
description: Standardize the Machine Learning operational flow, including experiment tracking, model export, and reproducibility.
---

# MLOps Workflow

## Index
1. [Experiment Tracking](#1-experiment-tracking)
2. [Model Exporting](#2-model-exporting)

---

## 1 Experiment Tracking
- ***Instruction***: Save all training runs in structured directories with timestamps and training metrics.
- ***Visuals***: None
- ***File References***: None

Structure: `models/experiments/run_YYYYMMDD_HHMMSS/`
- Every run MUST contain a `metrics.json` file logging loss, accuracy, and hyperparameters.
- Weights must be saved as `best_model.pt` and `last_model.pt`.

[←Index](#index)

## 2 Model Exporting
- ***Instruction***: For production inference, always export the final `.pt` PyTorch model to ONNX format.
- ***Visuals***: None
- ***File References***:
    - Edit [src/api/cli.py](../src/api/cli.py) to ensure the `export` command targets ONNX.

Command to export:
```bash
python src/main.py export models/experiments/run_XXX/best_model.pt models/production/model.onnx
```

[←Index](#index)
