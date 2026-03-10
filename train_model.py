from __future__ import annotations
import joblib
import numpy as np
from pathlib import Path
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import StackingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
try:
    from catboost import CatBoostClassifier  # optional
    _HAS_CATBOOST = True
except ImportError:
    CatBoostClassifier = None  # type: ignore
    _HAS_CATBOOST = False
from .preprocess import load_and_clean, make_splits
from .utils import ensure_dirs, ROOT


def build_base_learners():
    xgb = XGBClassifier(
        n_estimators=300, max_depth=5, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9, reg_lambda=1.0,
        eval_metric='logloss', n_jobs=1, random_state=42
    )
    lgb = LGBMClassifier(
        n_estimators=400, num_leaves=31, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9, reg_lambda=1.0,
        objective='binary', random_state=42, n_jobs=1
    )
    learners = [
        ('xgb', xgb),
        ('lgb', lgb)
    ]
    if _HAS_CATBOOST and CatBoostClassifier is not None:
        cat = CatBoostClassifier(
            iterations=800, depth=6, learning_rate=0.03,
            loss_function='Logloss', verbose=False, random_state=42
        )
        learners.append(('cat', cat))
    return learners


def train_and_save(data_path: Path | None = None):
    ensure_dirs()
    df = load_and_clean(data_path=data_path)
    X_train, X_test, y_train, y_test, preprocessor, smote, numeric, categorical = make_splits(df)

    # Fit preprocessing on training then apply SMOTE on transformed space
    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)

    X_train_bal, y_train_bal = smote.fit_resample(X_train_proc, y_train)

    base_learners = build_base_learners()
    meta = LogisticRegression(max_iter=200, solver='liblinear', class_weight='balanced')

    stack = StackingClassifier(
        estimators=base_learners,
        final_estimator=meta,
        stack_method='predict_proba',
        n_jobs=1
    )

    stack.fit(X_train_bal, y_train_bal)

    # Evaluate
    y_pred = stack.predict(X_test_proc)
    y_proba = stack.predict_proba(X_test_proc)[:, 1]
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_proba)
    report = classification_report(y_test, y_pred)

    # Save artifacts
    models_dir = ROOT / 'models'
    joblib.dump(stack, models_dir / 'stacking_model.pkl')
    joblib.dump(preprocessor, models_dir / 'scaler.pkl')

    # Save metrics
    report_dir = ROOT / 'report'
    with open(report_dir / 'accuracy_results.txt', 'w') as f:
        f.write(f"Accuracy: {acc:.4f}\nF1: {f1:.4f}\nROC-AUC: {roc:.4f}\n\n")
        f.write(report)

    print(f"Accuracy: {acc:.4f} | F1: {f1:.4f} | ROC-AUC: {roc:.4f}")
    return acc, f1, roc


if __name__ == '__main__':
    train_and_save()