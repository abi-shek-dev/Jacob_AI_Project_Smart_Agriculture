"""
data_pipeline.py
================
Handles all data loading, cleaning, and preprocessing steps.
This is the FIRST step in building any ML project.

Think of a pipeline like a factory assembly line:
  Raw Data -> Clean Data -> Scaled Data -> Ready for Training
"""

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler


# -- The 7 soil/weather features the model uses ------------------------------
FEATURE_COLUMNS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TARGET_COLUMN   = "label"   # The crop name we are trying to predict


def load_dataset(csv_path: str) -> pd.DataFrame:
    """
    Load the CSV file into a Pandas DataFrame.

    A DataFrame is like an Excel spreadsheet in Python -
    rows are samples, columns are features.

    Parameters
    ----------
    csv_path : str
        Absolute or relative path to the CSV file.

    Returns
    -------
    pd.DataFrame
        Raw (un-cleaned) dataset.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Dataset not found at '{csv_path}'.\n"
            "Run `python utils/generate_dataset.py` to create a synthetic dataset."
        )

    df = pd.read_csv(csv_path)
    print(f"[Data Pipeline] Loaded {len(df):,} rows x {len(df.columns)} columns.")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the raw DataFrame.

    Steps performed:
      1. Keep only the columns we need (drop any extra columns).
      2. Drop duplicate rows (identical soil readings are likely errors).
      3. Fill missing numeric values with the column median.
         We use median (not mean) because it is less sensitive to outliers.
      4. Strip whitespace from the crop label and lower-case it.

    Parameters
    ----------
    df : pd.DataFrame  Raw data from `load_dataset`.

    Returns
    -------
    pd.DataFrame  Cleaned data.
    """
    required_cols = FEATURE_COLUMNS + [TARGET_COLUMN]

    # -- Step 1: Keep only required columns ----------------------------------
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"[Data Pipeline] Missing columns in dataset: {missing}")

    df = df[required_cols].copy()
    print(f"[Data Pipeline] Selected columns: {required_cols}")

    # -- Step 2: Drop duplicates ----------------------------------------------
    before = len(df)
    df.drop_duplicates(inplace=True)
    print(f"[Data Pipeline] Removed {before - len(df)} duplicate rows.")

    # -- Step 3: Handle missing numeric values --------------------------------
    for col in FEATURE_COLUMNS:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            print(f"[Data Pipeline] Filled {null_count} NaN(s) in '{col}' with median={median_val:.4f}")

    # -- Step 4: Normalise label text -----------------------------------------
    df[TARGET_COLUMN] = df[TARGET_COLUMN].str.strip().str.lower()
    print(f"[Data Pipeline] Unique crops: {sorted(df[TARGET_COLUMN].unique())}")

    return df


def encode_labels(df: pd.DataFrame):
    """
    Convert string crop names to integers (ML models need numbers, not words).

    Example:  'rice' -> 0,  'wheat' -> 1,  'maize' -> 2 ...

    Parameters
    ----------
    df : pd.DataFrame  Cleaned data.

    Returns
    -------
    (pd.DataFrame, LabelEncoder)
        DataFrame with an integer 'label' column, and the fitted encoder
        (needed later to convert integers back to crop names).
    """
    le = LabelEncoder()
    df = df.copy()
    df[TARGET_COLUMN] = le.fit_transform(df[TARGET_COLUMN])
    print(f"[Data Pipeline] Encoded {len(le.classes_)} crop classes.")
    return df, le


def scale_features(X_train: np.ndarray, X_test: np.ndarray):
    """
    Standardise features so every column has mean=0 and std=1.

    WHY? Logistic Regression is sensitive to feature scale.
    E.g., 'rainfall' might range 0–300 mm while 'ph' only ranges 3–9.
    Without scaling, the model will incorrectly treat rainfall as more important.

    We fit the scaler ONLY on training data, then apply to both train & test.
    This prevents data leakage (test data must stay "unseen").

    Parameters
    ----------
    X_train, X_test : np.ndarray  Feature matrices.

    Returns
    -------
    (np.ndarray, np.ndarray, StandardScaler)
    """
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)   # learn mean/std from train
    X_test_scaled  = scaler.transform(X_test)         # apply same transform to test
    print("[Data Pipeline] Features scaled (StandardScaler).")
    return X_train_scaled, X_test_scaled, scaler


def prepare_data(csv_path: str, test_size: float = 0.2, random_state: int = 42):
    """
    Master function: runs the full pipeline from raw CSV -> training-ready arrays.

    Parameters
    ----------
    csv_path     : Path to the CSV file.
    test_size    : Fraction of data for testing (default 20 %).
    random_state : Seed for reproducibility.

    Returns
    -------
    dict with keys:
        X_train, X_test, y_train, y_test  - numpy arrays
        X_train_scaled, X_test_scaled     - scaled versions
        scaler                             – fitted StandardScaler
        label_encoder                      – fitted LabelEncoder
        feature_names                      – list of feature column names
    """
    # 1. Load
    df = load_dataset(csv_path)

    # 2. Clean
    df = clean_data(df)

    # 3. Encode labels
    df, label_encoder = encode_labels(df)

    # 4. Split features vs target
    X = df[FEATURE_COLUMNS].values   # shape: (n_samples, 7)
    y = df[TARGET_COLUMN].values     # shape: (n_samples,)

    # 5. Train/test split (stratified so every crop appears in both sets)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    print(f"[Data Pipeline] Train: {len(X_train):,} | Test: {len(X_test):,}")

    # 6. Scale
    X_train_scaled, X_test_scaled, scaler = scale_features(X_train, X_test)

    return {
        "X_train":        X_train,
        "X_test":         X_test,
        "X_train_scaled": X_train_scaled,
        "X_test_scaled":  X_test_scaled,
        "y_train":        y_train,
        "y_test":         y_test,
        "scaler":         scaler,
        "label_encoder":  label_encoder,
        "feature_names":  FEATURE_COLUMNS,
    }
