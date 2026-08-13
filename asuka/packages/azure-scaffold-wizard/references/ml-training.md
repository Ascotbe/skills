# ML Training & Inference — Scaffold Pattern

This reference file defines the scaffold pattern for **machine learning training and inference** projects using Azure Machine Learning.

---

## Type-Specific Questions

| # | Question | Guidance |
|---|---|---|
| M1 | **ML framework?** | `PyTorch` (default), `TensorFlow/Keras`, `scikit-learn`, `Hugging Face Transformers`. |
| M2 | **Task type?** | `Classification`, `Regression`, `NLP/Text`, `Computer Vision`, `Recommendation`, `Custom`. |
| M3 | **Training compute?** | `CPU` (default for small models), `GPU` (for deep learning). Drives AML compute SKU. |
| M4 | **Dataset location?** | `Azure Blob Storage` (default), `Azure Data Lake`, `Local files` (for dev). |
| M5 | **Model registry?** | `Azure ML Model Registry` (default), `MLflow Model Registry`. |
| M6 | **Inference endpoint type?** | `Managed Online Endpoint` (default, real-time), `Batch Endpoint`, `Container Apps` (custom). |
| M7 | **Experiment tracking?** | `MLflow` (default, integrated with AML), `Weights & Biases`, `TensorBoard`. |
| M8 | **Hyperparameter tuning?** | `None` (default), `Azure ML Sweep`, `Optuna`. |

---

## Project Folder Structure

```
<project-slug>/
├── src/
│   ├── __init__.py
│   ├── config.py                   # Training configuration
│   ├── data/
│   │   ├── __init__.py
│   │   ├── dataset.py              # Dataset loading and preprocessing
│   │   ├── transforms.py           # Data augmentation / feature engineering
│   │   └── splits.py               # Train/val/test splitting
│   ├── models/
│   │   ├── __init__.py
│   │   ├── architecture.py         # Model definition (from M1, M2)
│   │   └── losses.py               # Custom loss functions (if needed)
│   ├── training/
│   │   ├── __init__.py
│   │   ├── trainer.py              # Training loop
│   │   ├── evaluate.py             # Evaluation metrics
│   │   └── callbacks.py            # Training callbacks (early stopping, checkpointing)
│   ├── inference/
│   │   ├── __init__.py
│   │   ├── predict.py              # Inference logic
│   │   ├── preprocess.py           # Input preprocessing for inference
│   │   └── postprocess.py          # Output postprocessing
│   └── utils/
│       ├── __init__.py
│       └── metrics.py              # Custom metrics
│
├── scripts/
│   ├── train.py                    # CLI entry point for training
│   ├── evaluate.py                 # CLI entry point for evaluation
│   ├── register_model.py           # Register trained model in registry
│   └── deploy_endpoint.py          # Deploy model to managed endpoint
│
├── pipelines/                      # Azure ML pipeline definitions
│   ├── training_pipeline.yaml      # AML pipeline: data prep → train → evaluate → register
│   └── components/
│       ├── data_prep.yaml
│       ├── train.yaml
│       └── evaluate.yaml
│
├── environments/                   # Azure ML environment definitions
│   ├── training.yaml               # Conda/pip environment for training
│   └── inference.yaml              # Inference environment (minimal dependencies)
│
├── notebooks/                      # Jupyter notebooks for exploration
│   ├── 01_data_exploration.ipynb
│   ├── 02_model_prototyping.ipynb
│   └── 03_evaluation_analysis.ipynb
│
├── tests/
│   ├── __init__.py
│   ├── test_dataset.py
│   ├── test_model.py
│   └── test_inference.py
│
└── data/
    └── sample/                     # Small sample dataset for testing
```

---

## Source File Patterns

### Training Script

```python
# scripts/train.py
import argparse
import mlflow
from src.config import TrainingConfig
from src.data.dataset import load_dataset
from src.models.architecture import create_model
from src.training.trainer import Trainer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", required=True)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    config = TrainingConfig(
        data_path=args.data_path,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        output_dir=args.output_dir,
    )

    mlflow.autolog()

    with mlflow.start_run():
        # Load data
        train_data, val_data = load_dataset(config.data_path)

        # Create model
        model = create_model(config)

        # Train
        trainer = Trainer(model, config)
        metrics = trainer.train(train_data, val_data)

        # Log metrics
        mlflow.log_metrics(metrics)

        # Save model
        model_path = f"{config.output_dir}/model"
        trainer.save(model_path)
        mlflow.log_artifact(model_path)

        print(f"Training complete. Metrics: {metrics}")

if __name__ == "__main__":
    main()
```

### Inference Endpoint

```python
# src/inference/predict.py
import os
import json
import logging
from .preprocess import preprocess_input
from .postprocess import postprocess_output

logger = logging.getLogger(__name__)

# Global model reference (loaded once)
_model = None

def init():
    """Load the model — called once when the endpoint starts."""
    global _model
    model_path = os.environ.get("AZUREML_MODEL_DIR", "model")
    # Load model based on framework (M1)
    # For PyTorch: _model = torch.load(f"{model_path}/model.pt")
    # For scikit-learn: _model = joblib.load(f"{model_path}/model.pkl")
    logger.info(f"Model loaded from {model_path}")

def run(raw_data: str) -> str:
    """Score a request — called for each inference request."""
    data = json.loads(raw_data)

    # Preprocess
    inputs = preprocess_input(data)

    # Predict
    predictions = _model.predict(inputs)

    # Postprocess
    results = postprocess_output(predictions)

    return json.dumps(results)
```

### AML Pipeline Definition

```yaml
# pipelines/training_pipeline.yaml
$schema: https://azuremlschemas.azureedge.net/latest/pipelineJob.schema.json
type: pipeline
display_name: <project-name>-training-pipeline

settings:
  default_compute: azureml:<compute-name>

jobs:
  data_prep:
    type: command
    component: file:./components/data_prep.yaml
    inputs:
      raw_data:
        type: uri_folder
        path: azureml:<dataset-name>@latest

  train:
    type: command
    component: file:./components/train.yaml
    inputs:
      train_data: ${{parent.jobs.data_prep.outputs.processed_data}}
      epochs: 10
      learning_rate: 0.001

  evaluate:
    type: command
    component: file:./components/evaluate.yaml
    inputs:
      model: ${{parent.jobs.train.outputs.model}}
      test_data: ${{parent.jobs.data_prep.outputs.test_data}}
```

---

## Bicep Modules Required

- `monitoring.bicep` (always)
- `ml-workspace.bicep` — Azure ML workspace + associated resources
- `storage.bicep` — for datasets and model artifacts
- `container-registry.bicep` — for custom training/inference environments

If M3 = GPU:
- Compute cluster with GPU SKUs (configured in ML workspace)

If M6 = Container Apps:
- `container-apps-env.bicep` + `container-app.bicep`

### `infra/modules/ml-workspace.bicep`

```bicep
param location string
param tags object
param workspaceName string
param storageAccountId string
param appInsightsId string
param containerRegistryId string

resource workspace 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: workspaceName
  location: location
  tags: tags
  identity: { type: 'SystemAssigned' }
  properties: {
    storageAccount: storageAccountId
    applicationInsights: appInsightsId
    containerRegistry: containerRegistryId
    publicNetworkAccess: 'Enabled'
  }
}

output workspaceId string = workspace.id
output workspaceName string = workspace.name
output principalId string = workspace.identity.principalId
```

---

## Type-Specific Quality Checklist

- [ ] Training script accepts all hyperparameters as CLI arguments
- [ ] MLflow experiment tracking logs metrics, parameters, and artifacts
- [ ] Model can be loaded and run inference without Azure dependencies (for local testing)
- [ ] Dataset loading handles missing data and edge cases
- [ ] Train/val/test split is reproducible (fixed random seed)
- [ ] Evaluation metrics are appropriate for the task type (M2)
- [ ] Inference endpoint has `init()` and `run()` functions per AML contract
- [ ] Environment definitions pin all dependency versions
- [ ] Sample data in `data/sample/` exercises the full pipeline
- [ ] Notebooks are numbered and ordered for a logical exploration flow
- [ ] Model registration script tags the model with metrics and training run ID
