"""
explainability.py
=================
Provides tools to explain WHY the model made a prediction.

This is called "Explainable AI" (XAI) and is important in agriculture
because farmers need to understand the reason behind a recommendation,
not just receive a black-box answer.

Two techniques are used here:
  1. Feature Importance - which features the model relies on most overall.
  2. SHAP (SHapley Additive exPlanations) - how each feature pushed the
     prediction for ONE specific input up or down.
"""

import numpy as np
import shap
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")   # Use non-interactive backend (needed for servers/APIs)

# -- Feature display names for charts ----------------------------------------
FEATURE_LABELS = {
    "N":           "Nitrogen (N)",
    "P":           "Phosphorus (P)",
    "K":           "Potassium (K)",
    "temperature": "Temperature (°C)",
    "humidity":    "Humidity (%)",
    "ph":          "Soil pH",
    "rainfall":    "Rainfall (mm)",
}


# ----------------------------------------------------------------------------
# 1.  FEATURE IMPORTANCE  (works only for tree-based models like Random Forest)
# ----------------------------------------------------------------------------

def get_feature_importance(model, feature_names: list) -> dict:
    """
    Extract the built-in feature importances from a tree-based model.

    Random Forest assigns a score to every feature based on how much
    it reduces prediction error when used to split data.

    Parameters
    ----------
    model        : Trained RandomForestClassifier.
    feature_names: List of feature column names.

    Returns
    -------
    dict  {feature_name: importance_score (0–1)}
    """
    if not hasattr(model, "feature_importances_"):
        raise AttributeError(
            "This model does not support feature importances. "
            "Use a tree-based model like RandomForestClassifier."
        )

    importances = model.feature_importances_
    return {name: round(float(score), 4) for name, score in zip(feature_names, importances)}


def plot_feature_importance(model, feature_names: list, save_path: str = None) -> str:
    """
    Draw a horizontal bar chart of feature importances and save it to disk.

    Parameters
    ----------
    model        : Trained model with feature_importances_.
    feature_names: Column names.
    save_path    : Where to save the PNG. Defaults to 'model/feature_importance.png'.

    Returns
    -------
    str  Path where the image was saved.
    """
    save_path = save_path or "model/feature_importance.png"

    fi = get_feature_importance(model, feature_names)
    sorted_fi = sorted(fi.items(), key=lambda x: x[1], reverse=True)

    labels   = [FEATURE_LABELS.get(k, k) for k, _ in sorted_fi]
    scores   = [v for _, v in sorted_fi]
    colours  = plt.cm.viridis(np.linspace(0.2, 0.9, len(labels)))

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(labels[::-1], scores[::-1], color=colours[::-1], edgecolor="white")
    ax.bar_label(bars, fmt="%.4f", padding=4, fontsize=9)
    ax.set_xlabel("Importance Score", fontsize=11)
    ax.set_title("Feature Importance - Random Forest", fontsize=14, fontweight="bold")
    ax.set_xlim(0, max(scores) * 1.18)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"[XAI] Feature importance chart saved -> {save_path}")
    return save_path


# ----------------------------------------------------------------------------
# 2.  SHAP - per-prediction explanations
# ----------------------------------------------------------------------------

def build_shap_explainer(model, X_train_sample: np.ndarray):
    """
    Create a SHAP TreeExplainer using a small sample of training data.

    SHAP is a game-theory based method. It asks:
      "How much did each feature contribute to THIS prediction?"

    TreeExplainer is fast and accurate for tree-based models.

    Parameters
    ----------
    model           : Trained RandomForestClassifier.
    X_train_sample  : A sample of training data (100-200 rows is enough).

    Returns
    -------
    shap.TreeExplainer
    """
    explainer = shap.TreeExplainer(model, data=X_train_sample[:200])
    print("[XAI] SHAP TreeExplainer built successfully.")
    return explainer


def explain_prediction(
    explainer,
    input_array: np.ndarray,
    feature_names: list,
    label_encoder,
    predicted_class_index: int,
    save_path: str = None,
) -> dict:
    """
    Explain a single prediction using SHAP values.

    For a multiclass model, SHAP returns one value per feature per class.
    We focus on the PREDICTED class only.

    Parameters
    ----------
    explainer            : SHAP explainer (from build_shap_explainer).
    input_array          : 1D array of the input features (shape: (7,) or (1, 7)).
    feature_names        : List of feature column names.
    label_encoder        : Fitted LabelEncoder (to convert index -> crop name).
    predicted_class_index: The integer index the model predicted.
    save_path            : Optional path to save a SHAP waterfall PNG.

    Returns
    -------
    dict with:
        "shap_values"     : {feature: shap_value} for the predicted class
        "base_value"      : baseline (expected) log-odds before any features
        "predicted_crop"  : crop name string
        "explanation_text": human-readable string
    """
    x = np.array(input_array).reshape(1, -1)  # ensure shape (1, 7)

    # shap_vals shape for multiclass: (1, n_features, n_classes)
    shap_vals_obj = explainer(x)

    # Extract SHAP values for the predicted class
    shap_for_class = shap_vals_obj.values[0, :, predicted_class_index]  # shape: (7,)
    base_value     = float(shap_vals_obj.base_values[0, predicted_class_index])

    shap_dict = {
        name: round(float(val), 4)
        for name, val in zip(feature_names, shap_for_class)
    }

    predicted_crop = label_encoder.inverse_transform([predicted_class_index])[0]

    # -- Build a human-readable explanation text ------------------------------
    sorted_shap = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)
    top_features = sorted_shap[:3]  # top 3 most influential features

    explanation_parts = []
    for feat, val in top_features:
        direction = "increased" if val > 0 else "decreased"
        explanation_parts.append(
            f"* {FEATURE_LABELS.get(feat, feat)} {direction} confidence by {abs(val):.4f}"
        )

    explanation_text = (
        f"The model predicted '{predicted_crop}' mainly because:\n"
        + "\n".join(explanation_parts)
    )
    print(f"[XAI] Explanation generated for class '{predicted_crop}'.")

    # -- Optional: Save SHAP waterfall chart ----------------------------------
    if save_path:
        try:
            fig, ax = plt.subplots(figsize=(9, 5))
            colours = ["#2ecc71" if v > 0 else "#e74c3c" for v in shap_for_class]
            feature_labels_display = [FEATURE_LABELS.get(f, f) for f in feature_names]
            ax.barh(feature_labels_display, shap_for_class, color=colours, edgecolor="white")
            ax.axvline(0, color="black", linewidth=0.8)
            ax.set_xlabel("SHAP Value (impact on prediction)", fontsize=11)
            ax.set_title(f"SHAP Explanation - Predicted: {predicted_crop}", fontsize=13, fontweight="bold")
            ax.spines[["top", "right"]].set_visible(False)
            plt.tight_layout()
            plt.savefig(save_path, dpi=150)
            plt.close(fig)
            print(f"[XAI] SHAP chart saved -> {save_path}")
        except Exception as e:
            print(f"[XAI] Warning: Could not save SHAP chart: {e}")

    return {
        "shap_values":      shap_dict,
        "base_value":       base_value,
        "predicted_crop":   predicted_crop,
        "explanation_text": explanation_text,
    }
