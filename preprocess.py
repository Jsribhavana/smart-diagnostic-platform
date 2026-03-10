from __future__ import annotations
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from .utils import default_dataset_path


FEATURES_CANONICAL = [
    "hba1c", "glucose", "blood_pressure", "skin_thickness", "insulin",
    "nju", "age", "smoker", "physicalactivity", "bmi_category"
]
TARGET_CANONICAL = "outcome"

def load_and_clean(data_path: Path | None = None) -> pd.DataFrame:
    p = data_path or default_dataset_path()
    df = pd.read_csv(p)
    # Normalize column names
    df.columns = [c.strip() for c in df.columns]
    # Map to canonical names (case-insensitive)
    rename_map = {
        'hba1c': 'hba1c',
        'Glucose': 'glucose', 'glucose': 'glucose',
        'BloodPressure': 'blood_pressure', 'blood_pressure': 'blood_pressure',
        'SkinThickness': 'skin_thickness', 'skin_thickness': 'skin_thickness',
        'Insulin': 'insulin', 'insulin': 'insulin',
        'DiabetesPedigreeFunction': 'nju', 'nju': 'nju',
        'Age': 'age', 'age': 'age',
        'smoker': 'smoker', 'Smoker': 'smoker',
        'physicalactivity': 'physicalactivity', 'PhysicalActivity': 'physicalactivity',
        'BMI_Category': 'bmi_category', 'bmi_category': 'bmi_category',
        'Outcome': 'outcome', 'outcome': 'outcome'
    }
    for c in list(df.columns):
        if c in rename_map:
            df.rename(columns={c: rename_map[c]}, inplace=True)

    # Handle missing values: numeric -> median, categorical -> most frequent
    for col in df.columns:
        if col == TARGET_CANONICAL:
            continue
        if df[col].dtype.kind in 'biufc':
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna(df[col].mode().iloc[0])

    # Ensure smoker is binary 0/1 if strings present
    if df['smoker'].dtype == object:
        df['smoker'] = df['smoker'].str.lower().map({'yes': 1, 'no': 0}).fillna(df['smoker']).astype(int)

    # Ensure physicalactivity numeric (if categorical, map common labels)
    if df['physicalactivity'].dtype == object:
        mapping = {
            'low': 0,
            'medium': 1,
            'moderate': 1,
            'none': 0,
            'sedentary': 0,
            'high': 2,
            'active': 2,
            'very active': 2
        }
        df['physicalactivity'] = df['physicalactivity'].str.lower().map(mapping).fillna(df['physicalactivity'])
        # try to coerce to numeric
        df['physicalactivity'] = pd.to_numeric(df['physicalactivity'], errors='coerce').fillna(df['physicalactivity'].median())

    # BMI_Category should be categorical string; ensure string type
    df['bmi_category'] = df['bmi_category'].astype(str)

    # Restrict to features and target
    cols_needed = FEATURES_CANONICAL + [TARGET_CANONICAL]
    df = df[[c for c in cols_needed if c in df.columns]]
    return df

def make_splits(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    X = df.drop(columns=[TARGET_CANONICAL])
    y = df[TARGET_CANONICAL].astype(int)

    # Column groups
    categorical = ['bmi_category']
    numeric = [c for c in X.columns if c not in categorical]

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical)
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Apply SMOTE to the training set only
    smote = SMOTE(random_state=random_state)
    return X_train, X_test, y_train, y_test, preprocessor, smote, numeric, categorical