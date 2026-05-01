"""
train_model.py
==============
Trains two ML models (Random Forest & Logistic Regression), compares them,
selects the best, and saves everything needed for inference.

Run this once before starting the API:
    cd SmartAgricultureAI
    python model/train_model.py
"""

import os
import sys
import json
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# -- Ensure project root is on sys.path so `utils` can be imported ------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from utils.data_pipeline import prepare_data, FEATURE_COLUMNS
from utils.explainability import (
    build_shap_explainer,
    plot_feature_importance,
)
from utils.generate_dataset import generate as generate_dataset


# -- Paths --------------------------------------------------------------------
DATA_CSV      = os.path.join(ROOT, "data", "crop_recommendation.csv")
MODEL_DIR     = os.path.join(ROOT, "model")
MODEL_PATH    = os.path.join(MODEL_DIR, "best_model.pkl")
SCALER_PATH   = os.path.join(MODEL_DIR, "scaler.pkl")
ENCODER_PATH  = os.path.join(MODEL_DIR, "label_encoder.pkl")
EXPLAINER_PATH= os.path.join(MODEL_DIR, "shap_explainer.pkl")
META_PATH     = os.path.join(MODEL_DIR, "model_meta.json")
FI_CHART_PATH = os.path.join(MODEL_DIR, "feature_importance.png")


def evaluate_model(model, X_test, y_test, label_encoder, name: str) -> float:
    """
    Print classification report and return accuracy.

    The classification report shows:
      - Precision: of all predictions for class X, how many were correct?
      - Recall   : of all actual class X samples, how many did we catch?
      - F1-Score : harmonic mean of precision and recall.
    """
    y_pred = model.predict(X_test)
    acc    = accuracy_score(y_test, y_pred)
    report = classification_report(
        y_test, y_pred,
        target_names=label_encoder.classes_,
        zero_division=0,
    )
    print(f"\n{'-'*60}")
    print(f"  Model : {name}")
    print(f"  Accuracy : {acc*100:.2f}%")
    print(f"{'-'*60}")
    print(report)
    return acc


def train():
    """Full training pipeline."""

    # -- 0. Generate dataset if missing ---------------------------------------
    if not os.path.exists(DATA_CSV):
        print("[Train] Dataset not found - generating synthetic data ...")
        generate_dataset(DATA_CSV)

    # -- 1. Load and prepare data ----------------------------------------------
    print("\n[Train] Preparing data ...")
    data = prepare_data(DATA_CSV)

    X_train        = data["X_train"]
    X_test         = data["X_test"]
    X_train_scaled = data["X_train_scaled"]
    X_test_scaled  = data["X_test_scaled"]
    y_train        = data["y_train"]
    y_test         = data["y_test"]
    scaler         = data["scaler"]
    label_encoder  = data["label_encoder"]

    # -- 2. Train Model 1: Random Forest --------------------------------------
    #
    # Random Forest = many decision trees, each trained on a random subset.
    # They vote together -> more robust than a single tree.
    #
    # n_estimators = 200 trees (more = more stable but slower to train)
    # max_depth    = None -> trees grow until leaves are pure (good for RF)
    # n_jobs = -1  -> use all CPU cores

    print("\n[Train] Training Random Forest ...")
    rf = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",   # handles slightly imbalanced classes
    )
    rf.fit(X_train, y_train)   # RF does NOT need scaled features
    rf_acc = evaluate_model(rf, X_test, y_test, label_encoder, "Random Forest")

    # -- 3. Train Model 2: Logistic Regression --------------------------------
    #
    # Despite the name, Logistic Regression is a CLASSIFICATION model.
    # It fits a sigmoid curve to separate classes.
    # DOES need scaled features - that's why we use X_train_scaled here.
    #
    # max_iter = 2000 because with 22 classes it needs more iterations to converge.

    print("\n[Train] Training Logistic Regression ...")
    lr = LogisticRegression(
        max_iter=2000,
        random_state=42,
        solver="lbfgs",
        multi_class="multinomial",
        C=1.0,                     # regularisation strength (1.0 = default)
    )
    lr.fit(X_train_scaled, y_train)
    lr_acc = evaluate_model(lr, X_test_scaled, y_test, label_encoder, "Logistic Regression")

    # -- 4. Compare and select the best model ---------------------------------
    print("\n[Train] Comparing models ...")
    results = {
        "Random Forest":      {"model": rf,  "acc": rf_acc, "uses_scaled": False},
        "Logistic Regression": {"model": lr,  "acc": lr_acc, "uses_scaled": True},
    }

    best_name = max(results, key=lambda k: results[k]["acc"])
    best      = results[best_name]
    print(f"\n[*]  Best Model: {best_name}  (accuracy={best['acc']*100:.2f}%)")

    # -- 5. Save model artefacts -----------------------------------------------
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Always save Random Forest as best_model for SHAP (RF gives better explanations).
    # If Logistic Regression won, we still keep RF for XAI but note the winner.
    # For production prediction we always use the winner.
    joblib.dump(best["model"],   MODEL_PATH)
    joblib.dump(rf,              os.path.join(MODEL_DIR, "rf_model.pkl"))   # always keep RF for XAI
    joblib.dump(scaler,          SCALER_PATH)
    joblib.dump(label_encoder,   ENCODER_PATH)

    print(f"[Train] Model  saved -> {MODEL_PATH}")
    print(f"[Train] Scaler saved -> {SCALER_PATH}")
    print(f"[Train] Encoder saved -> {ENCODER_PATH}")

    # Save metadata so the API knows which model won and whether to scale
    meta = {
        "best_model_name":  best_name,
        "best_accuracy":    round(best["acc"], 4),
        "rf_accuracy":      round(rf_acc, 4),
        "lr_accuracy":      round(lr_acc, 4),
        "uses_scaled_input": best["uses_scaled"],
        "feature_names":    FEATURE_COLUMNS,
        "n_classes":        int(len(label_encoder.classes_)),
        "classes":          list(label_encoder.classes_),
    }
    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[Train] Metadata saved -> {META_PATH}")

    # -- 6. Feature importance chart (always uses RF) --------------------------
    print("\n[Train] Generating feature importance chart ...")
    plot_feature_importance(rf, FEATURE_COLUMNS, FI_CHART_PATH)

    # -- 7. Build and save SHAP explainer -------------------------------------
    print("\n[Train] Building SHAP explainer (this may take ~30 seconds) ...")
    try:
        explainer = build_shap_explainer(rf, X_train)
        joblib.dump(explainer, EXPLAINER_PATH)
        print(f"[Train] SHAP explainer saved -> {EXPLAINER_PATH}")
    except Exception as e:
        print(f"[Train] [!] SHAP explainer failed: {e}\n"
              "         The API will still work but won't return SHAP values.")

    print("\n[SUCCESS] Training complete! All artefacts saved to model/")
    return meta


if __name__ == "__main__":
    train()
