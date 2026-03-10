# Diabetes Stacking Ensemble Model

This project trains a high‑accuracy diabetes prediction model using a stacking ensemble with XGBoost, LightGBM, and CatBoost as base learners and Logistic Regression as the meta‑learner. It includes preprocessing (missing values, categorical encoding, scaling), SMOTE for class imbalance, evaluation metrics, and a Flask API for predictions.

Run `python run.py` to preprocess, train, evaluate, and save artifacts. Start the API with `python app/main.py`.