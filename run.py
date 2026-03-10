from __future__ import annotations
from pathlib import Path
from src.train_model import train_and_save
from src.evaluate import evaluate_artifacts
from src.utils import ensure_dirs, default_dataset_path


def main():
    ensure_dirs()
    data_path = default_dataset_path()
    print(f"Using dataset: {data_path}")
    acc, f1, roc = train_and_save(data_path=data_path)
    print("Evaluating and generating plots...")
    evaluate_artifacts(data_path=data_path)
    print("Done. Artifacts saved in models/ and report/.")


if __name__ == '__main__':
    main()