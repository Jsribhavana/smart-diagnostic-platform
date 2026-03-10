from __future__ import annotations
import joblib
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, roc_curve, auc, accuracy_score, f1_score, precision_score, recall_score, classification_report
from .preprocess import load_and_clean, make_splits
from .utils import ROOT, ensure_dirs


def evaluate_artifacts(data_path: Path | None = None):
    df = load_and_clean(data_path=data_path)
    X_train, X_test, y_train, y_test, preprocessor, smote, numeric, categorical = make_splits(df)
    # Load saved
    model = joblib.load(ROOT / 'models' / 'stacking_model.pkl')
    scaler = joblib.load(ROOT / 'models' / 'scaler.pkl')

    X_test_proc = scaler.transform(X_test)
    y_proba = model.predict_proba(X_test_proc)[:, 1]
    y_pred = (y_proba >= 0.5).astype(int)

    # Calculate metrics for final stacking model
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)

    # Calculate metrics for each base learner in the stacking model (e.g. xgboost, lightgbm, catboost)
    base_metrics = {}
    if hasattr(model, "named_estimators_"):
        for name, estimator in model.named_estimators_.items():
            # Some estimators may not implement predict_proba
            try:
                y_proba_base = estimator.predict_proba(X_test_proc)[:, 1]
                y_pred_base = (y_proba_base >= 0.5).astype(int)
            except AttributeError:
                y_pred_base = estimator.predict(X_test_proc)

            base_acc = accuracy_score(y_test, y_pred_base)
            base_prec = precision_score(y_test, y_pred_base)
            base_rec = recall_score(y_test, y_pred_base)
            base_f1 = f1_score(y_test, y_pred_base)

            base_metrics[name] = {
                "accuracy": base_acc,
                "precision": base_prec,
                "recall": base_rec,
                "f1": base_f1,
            }

    # ROC curve for AUC calculation
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    roc_auc = auc(fpr, tpr)
    
    # Print metrics
    print("\n" + "="*60)
    print("MODEL PERFORMANCE METRICS")
    print("="*60)
    print(f"Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"F1 Score:  {f1:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print("="*60)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("="*60 + "\n")

    # Print base learner metrics if available
    if base_metrics:
        print("BASE LEARNER METRICS (EACH ALGORITHM)")
        print("-" * 60)
        for name, m in base_metrics.items():
            print(
                f"{name.upper():<8} -> "
                f"Accuracy: {m['accuracy']:.4f} ({m['accuracy']*100:.2f}%), "
                f"Precision: {m['precision']:.4f}, "
                f"Recall: {m['recall']:.4f}, "
                f"F1: {m['f1']:.4f}"
            )
        print("=" * 60 + "\n")

    # Save metrics to file
    ensure_dirs()
    report_dir = ROOT / 'report'
    with open(report_dir / 'model_accuracy.txt', 'w') as f:
        f.write("="*60 + "\n")
        f.write("MODEL PERFORMANCE METRICS\n")
        f.write("="*60 + "\n")
        f.write(f"Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)\n")
        f.write(f"F1 Score:  {f1:.4f}\n")
        f.write(f"Precision: {precision:.4f}\n")
        f.write(f"Recall:    {recall:.4f}\n")
        f.write(f"ROC-AUC:   {roc_auc:.4f}\n")
        f.write("="*60 + "\n\n")
        f.write("Classification Report:\n")
        f.write(classification_report(y_test, y_pred))
        f.write("="*60 + "\n\n")

        if base_metrics:
            f.write("BASE LEARNER METRICS (EACH ALGORITHM)\n")
            f.write("-" * 60 + "\n")
            for name, m in base_metrics.items():
                f.write(
                    f"{name.upper():<8} -> "
                    f"Accuracy: {m['accuracy']:.4f} ({m['accuracy']*100:.2f}%), "
                    f"Precision: {m['precision']:.4f}, "
                    f"Recall: {m['recall']:.4f}, "
                    f"F1: {m['f1']:.4f}\n"
                )
            f.write("=" * 60 + "\n")
    
    print(f"Metrics saved to: {report_dir / 'model_accuracy.txt'}\n")

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(4, 4))
    plt.imshow(cm, cmap='Blues')
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    for (i, j), val in np.ndenumerate(cm):
        plt.text(j, i, int(val), ha='center', va='center')
    plt.tight_layout()
    plt.savefig(ROOT / 'report' / 'confusion_matrix.png')
    plt.close()

    # ROC curve (fpr, tpr already calculated above)
    plt.figure(figsize=(5, 4))
    plt.plot(fpr, tpr, label=f'ROC curve (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(ROOT / 'report' / 'roc_curve.png')
    plt.close()


if __name__ == '__main__':
    evaluate_artifacts()