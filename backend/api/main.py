"""
main.py - FastAPI Backend
============================
Provides the /predict endpoint for the Smart Agriculture AI System.

The React Native app sends soil & climate readings to this server,
and receives back the recommended crop + an explanation of WHY.

Start the server:
    cd SmartAgricultureAI
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
"""

import os
import sys
import json
import logging

import joblib
import numpy as np
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

# -- Ensure project root is importable ----------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from utils.explainability import explain_prediction

# -- Logging ------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)

# -- Paths ---------------------------------------------------------------------
MODEL_DIR     = os.path.join(ROOT, "model")
MODEL_PATH    = os.path.join(MODEL_DIR, "best_model.pkl")
RF_PATH       = os.path.join(MODEL_DIR, "rf_model.pkl")
SCALER_PATH   = os.path.join(MODEL_DIR, "scaler.pkl")
ENCODER_PATH  = os.path.join(MODEL_DIR, "label_encoder.pkl")
EXPLAINER_PATH= os.path.join(MODEL_DIR, "shap_explainer.pkl")
META_PATH     = os.path.join(MODEL_DIR, "model_meta.json")

# -- OpenWeatherMap (optional bonus) ------------------------------------------
OWM_API_KEY = os.getenv("OWM_API_KEY", "")   # set in your environment or .env

# -- Load model artefacts at startup ------------------------------------------
def load_artefacts():
    """Load saved model, scaler, encoder and SHAP explainer into memory."""
    missing = [p for p in [MODEL_PATH, SCALER_PATH, ENCODER_PATH, META_PATH] if not os.path.exists(p)]
    if missing:
        raise RuntimeError(
            f"Missing model files: {missing}\n"
            "Please run: python model/train_model.py"
        )

    model         = joblib.load(MODEL_PATH)
    rf_model      = joblib.load(RF_PATH) if os.path.exists(RF_PATH) else model
    scaler        = joblib.load(SCALER_PATH)
    label_encoder = joblib.load(ENCODER_PATH)
    explainer     = joblib.load(EXPLAINER_PATH) if os.path.exists(EXPLAINER_PATH) else None

    with open(META_PATH) as f:
        meta = json.load(f)

    log.info(f"Model loaded: {meta['best_model_name']} (acc={meta['best_accuracy']*100:.2f}%)")
    return model, rf_model, scaler, label_encoder, explainer, meta


# Load once when the server starts (not on every request)
try:
    model, rf_model, scaler, label_encoder, explainer, meta = load_artefacts()
    USES_SCALED = meta["uses_scaled_input"]
    FEATURE_NAMES = meta["feature_names"]
except RuntimeError as e:
    log.error(str(e))
    model = rf_model = scaler = label_encoder = explainer = meta = None
    USES_SCALED = False
    FEATURE_NAMES = ["N","P","K","temperature","humidity","ph","rainfall"]


# -- FastAPI app ---------------------------------------------------------------
app = FastAPI(
    title="Smart Agriculture AI API",
    description="Recommends the best crop based on soil and climate data.",
    version="1.0.0",
)

# Allow React Native (and any origin during dev) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # Restrict to your app URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# -- Request / Response schemas ------------------------------------------------

class SoilInput(BaseModel):
    """The 7 soil & climate features the user must provide."""
    N:           float = Field(..., ge=0,   le=200,  description="Nitrogen content (kg/ha)")
    P:           float = Field(..., ge=0,   le=200,  description="Phosphorus content (kg/ha)")
    K:           float = Field(..., ge=0,   le=200,  description="Potassium content (kg/ha)")
    temperature: float = Field(..., ge=0,   le=60,   description="Temperature (°C)")
    humidity:    float = Field(..., ge=0,   le=100,  description="Relative humidity (%)")
    ph:          float = Field(..., ge=0,   le=14,   description="Soil pH (0–14)")
    rainfall:    float = Field(..., ge=0,   le=500,  description="Rainfall (mm)")

    # Optional: city name to auto-fill weather from OpenWeatherMap
    city:        str   = Field(None, description="City name for real-time weather (optional)")

    @validator("ph")
    def ph_must_be_valid(cls, v):
        if v < 3 or v > 10:
            raise ValueError("Soil pH is typically between 3 and 10.")
        return v


class PredictionResponse(BaseModel):
    recommended_crop:  str
    confidence_pct:    float
    feature_importance: dict
    shap_values:       dict
    explanation_text:  str
    weather_used:      bool
    model_used:        str

    # Suppress Pydantic V2 warning about 'model_' prefix
    model_config = {"protected_namespaces": ()}


# -- Helper: Fetch real-time weather ------------------------------------------

def fetch_weather(city: str) -> dict | None:
    """
    Calls OpenWeatherMap API to get current temperature, humidity and rainfall.
    Returns None if the city is not found or the API key is missing.
    """
    if not OWM_API_KEY or not city:
        return None
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={OWM_API_KEY}&units=metric"
        )
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            log.warning(f"OWM API error {resp.status_code} for city '{city}'")
            return None
        data = resp.json()
        weather = {
            "temperature": data["main"]["temp"],
            "humidity":    data["main"]["humidity"],
            # OWM gives rainfall in mm for last 1 hour; default to 0 if missing
            "rainfall":    data.get("rain", {}).get("1h", 0.0),
        }
        log.info(f"Weather fetched for '{city}': {weather}")
        return weather
    except Exception as e:
        log.warning(f"Weather fetch failed: {e}")
        return None


# -- Routes --------------------------------------------------------------------

@app.get("/", summary="Health check")
def root():
    """Simple ping endpoint to confirm the server is running."""
    return {
        "status":  "ok",
        "message": "Smart Agriculture AI API is running",
        "model":   meta["best_model_name"] if meta else "not loaded",
    }


@app.post("/predict", response_model=PredictionResponse, summary="Crop prediction")
def predict(input_data: SoilInput):
    """
    Main prediction endpoint.

    Accepts soil + climate values, returns:
      * recommended_crop   - the crop the model recommends
      * confidence_pct     - how confident the model is (0-100 %)
      * feature_importance - global RF importance scores
      * shap_values        - per-feature contribution for THIS prediction
      * explanation_text   - human-readable reason
    """
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run `python model/train_model.py` first.",
        )

    # -- 1. Build feature array ------------------------------------------------
    inp = {
        "N":           input_data.N,
        "P":           input_data.P,
        "K":           input_data.K,
        "temperature": input_data.temperature,
        "humidity":    input_data.humidity,
        "ph":          input_data.ph,
        "rainfall":    input_data.rainfall,
    }

    # -- 2. Optionally override temperature/humidity/rainfall from live weather -
    weather_used = False
    if input_data.city:
        weather = fetch_weather(input_data.city)
        if weather:
            inp["temperature"] = weather["temperature"]
            inp["humidity"]    = weather["humidity"]
            inp["rainfall"]    = weather["rainfall"]
            weather_used = True
            log.info(f"Weather override applied from city='{input_data.city}'")

    # -- 3. Prepare input array ------------------------------------------------
    x_raw = np.array([[inp[f] for f in FEATURE_NAMES]])   # shape: (1, 7)
    x_scaled = scaler.transform(x_raw)

    x_for_pred = x_scaled if USES_SCALED else x_raw

    # -- 4. Predict ------------------------------------------------------------
    pred_class_index = int(model.predict(x_for_pred)[0])
    probabilities    = model.predict_proba(x_for_pred)[0]   # shape: (n_classes,)
    confidence_pct   = round(float(probabilities[pred_class_index]) * 100, 2)
    recommended_crop = label_encoder.inverse_transform([pred_class_index])[0]

    log.info(f"Prediction: {recommended_crop} ({confidence_pct:.1f}%)")

    # -- 5. Feature importance (from RF, not scaled input) ---------------------
    fi_scores = {
        feat: round(float(imp), 4)
        for feat, imp in zip(FEATURE_NAMES, rf_model.feature_importances_)
    }

    # -- 6. SHAP explanation ---------------------------------------------------
    shap_vals = {}
    explanation_text = f"Recommended crop: {recommended_crop} (confidence: {confidence_pct:.1f}%)"

    if explainer is not None:
        try:
            xai_result = explain_prediction(
                explainer        = explainer,
                input_array      = x_raw[0],   # always pass raw (unscaled) to RF explainer
                feature_names    = FEATURE_NAMES,
                label_encoder    = label_encoder,
                predicted_class_index = pred_class_index,
            )
            shap_vals        = xai_result["shap_values"]
            explanation_text = xai_result["explanation_text"]
        except Exception as e:
            log.warning(f"SHAP explanation failed: {e}")

    # -- 7. Return response ----------------------------------------------------
    return PredictionResponse(
        recommended_crop   = recommended_crop,
        confidence_pct     = confidence_pct,
        feature_importance = fi_scores,
        shap_values        = shap_vals,
        explanation_text   = explanation_text,
        weather_used       = weather_used,
        model_used         = meta["best_model_name"] if meta else "unknown",
    )


@app.get("/crops", summary="List all supported crops")
def list_crops():
    """Returns all crop classes the model was trained on."""
    if label_encoder is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")
    return {"crops": list(label_encoder.classes_)}


@app.get("/model-info", summary="Model metadata")
def model_info():
    """Returns accuracy and other metadata about the trained model."""
    if meta is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")
    return meta
