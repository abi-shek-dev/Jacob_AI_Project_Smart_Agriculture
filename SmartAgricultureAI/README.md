# 🌾 Smart Agriculture AI System

> An AI-powered crop recommendation system with a React Native (Expo Go) mobile app and Python FastAPI backend.  
> Enter your soil data → get the best crop to grow + a full explainable AI breakdown.

---

## 📁 Project Structure

```
SmartAgricultureAI/
├── data/
│   └── crop_recommendation.csv       ← Auto-generated or drop your own CSV
│
├── model/
│   ├── train_model.py                ← Train RF + LR, compare, save best
│   ├── best_model.pkl                ← Best trained model (git-ignored)
│   ├── rf_model.pkl                  ← Random Forest (used for SHAP)
│   ├── scaler.pkl                    ← StandardScaler
│   ├── label_encoder.pkl             ← Crop name encoder
│   ├── shap_explainer.pkl            ← SHAP TreeExplainer
│   ├── model_meta.json               ← Accuracy, classes, feature list
│   └── feature_importance.png        ← Feature importance chart
│
├── api/
│   ├── __init__.py
│   └── main.py                       ← FastAPI server (POST /predict)
│
├── frontend/                         ← React Native Expo Go app
│   ├── App.js                        ← Navigation root
│   ├── app.json                      ← Expo config
│   ├── constants/
│   │   ├── api.js                    ← API base URL
│   │   └── theme.js                  ← Design tokens (colors, spacing)
│   └── screens/
│       ├── HomeScreen.js             ← Landing page
│       ├── PredictScreen.js          ← Sliders for soil input
│       └── ResultScreen.js           ← Crop result + charts + SHAP
│
├── utils/
│   ├── __init__.py
│   ├── data_pipeline.py              ← Load, clean, scale data
│   ├── explainability.py             ← Feature importance + SHAP
│   └── generate_dataset.py           ← Synthetic dataset generator
│
├── requirements.txt                  ← Python packages
└── README.md
```

---

## 🎯 System Overview

| Layer       | Technology       | Purpose                                     |
|-------------|------------------|---------------------------------------------|
| Data        | Pandas, NumPy    | Load, clean, scale soil data                |
| ML Models   | scikit-learn     | Random Forest + Logistic Regression         |
| XAI         | SHAP             | Per-prediction explanations                 |
| Backend API | FastAPI (Python) | POST /predict endpoint                      |
| Mobile App  | React Native + Expo Go | Sliders UI + charts + result display |
| Weather     | OpenWeatherMap   | Optional real-time temperature/humidity     |

---

## ⚙️ Prerequisites

| Tool       | Version     | Download                              |
|------------|-------------|---------------------------------------|
| Python     | 3.10+       | https://python.org                    |
| Node.js    | 18+         | https://nodejs.org                    |
| Expo Go    | Latest      | Android Play Store / iOS App Store    |
| Git        | Any         | Optional                              |

---

## 🚀 Setup & Running

### Step 1 – Clone / Open the project

```bash
cd c:\Projects\Jacob_AI_Project\SmartAgricultureAI
```

### Step 2 – Install Python dependencies

```bash
pip install -r requirements.txt
```

> 💡 Use a virtual environment to avoid conflicts:
> ```bash
> python -m venv venv
> venv\Scripts\activate   # Windows
> pip install -r requirements.txt
> ```

### Step 3 – Train the ML model

```bash
python model/train_model.py
```

This will:
1. Generate `data/crop_recommendation.csv` (2,200 rows, 22 crops)
2. Train **Random Forest** and **Logistic Regression**
3. Print accuracy comparison
4. Save the best model + scaler + SHAP explainer to `model/`

Expected output:
```
[Train] Random Forest  accuracy: ~97–99%
[Train] Logistic Regression accuracy: ~92–96%
✅ Best Model: Random Forest
🎉 Training complete!
```

### Step 4 – Start the FastAPI backend

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Open in browser to verify: http://localhost:8000

You should see:
```json
{"status": "ok", "message": "Smart Agriculture AI API is running 🌾"}
```

Interactive API docs: http://localhost:8000/docs

### Step 5 – Configure the mobile app's API URL

Edit `frontend/constants/api.js`:

```js
// Android Emulator
export const API_BASE_URL = "http://10.0.2.2:8000";

// Physical Android/iOS device (replace with YOUR computer's local IP)
export const API_BASE_URL = "http://192.168.1.XXX:8000";
```

> Find your local IP:  
> **Windows**: `ipconfig` → look for IPv4 Address  
> **Mac/Linux**: `ifconfig` or `ip addr`

### Step 6 – Start the Expo app

```bash
cd frontend
npx expo start
```

Scan the QR code with **Expo Go** on your phone.

---

## 📱 App Screens

| Screen        | Description                                              |
|---------------|----------------------------------------------------------|
| Home          | Hero banner, feature overview, CTA button               |
| Predict       | 7 sliders (N, P, K, temperature, humidity, pH, rainfall) + optional city name |
| Result        | Recommended crop, confidence %, SHAP chart, Feature Importance chart, explanation text |

---

## 🌐 API Reference

### `GET /`
Health check.

### `POST /predict`
**Request body:**
```json
{
  "N": 90,
  "P": 42,
  "K": 43,
  "temperature": 20.8,
  "humidity": 82.0,
  "ph": 6.5,
  "rainfall": 202.9,
  "city": "Mumbai"
}
```
> `city` is optional. If provided and OWM_API_KEY is set, temperature/humidity/rainfall are overridden with live data.

**Response:**
```json
{
  "recommended_crop": "rice",
  "confidence_pct": 97.5,
  "feature_importance": {
    "N": 0.1832,
    "P": 0.1245,
    "K": 0.0991,
    "temperature": 0.1654,
    "humidity": 0.1823,
    "ph": 0.0845,
    "rainfall": 0.1610
  },
  "shap_values": {
    "N": 0.0821,
    "P": -0.0123,
    "K": 0.0015,
    "temperature": 0.0932,
    "humidity": 0.1241,
    "ph": -0.0087,
    "rainfall": 0.0997
  },
  "explanation_text": "The model predicted 'rice' mainly because:\n• Humidity increased confidence by 0.1241\n• Rainfall increased confidence by 0.0997\n• Temperature increased confidence by 0.0932",
  "weather_used": false,
  "model_used": "Random Forest"
}
```

### `GET /crops`
Lists all 22 supported crops.

### `GET /model-info`
Returns model metadata (accuracy, number of classes, feature list).

---

## 🌦️ OpenWeatherMap (Bonus)

1. Get a free API key at https://openweathermap.org/api
2. Set it as an environment variable before starting the server:

```bash
# Windows
set OWM_API_KEY=your_key_here

# Mac/Linux
export OWM_API_KEY=your_key_here
```

Now pass `"city": "Delhi"` in your predict request and the API will auto-fill temperature, humidity, and rainfall from live weather data.

---

## 🧠 ML Details

| Model               | Training Data | Accuracy (typical) |
|---------------------|---------------|--------------------|
| Random Forest        | Unscaled      | ~97–99%            |
| Logistic Regression  | Scaled        | ~92–96%            |

**Features used:**
- `N`  – Nitrogen (kg/ha)
- `P`  – Phosphorus (kg/ha)  
- `K`  – Potassium (kg/ha)
- `temperature` – °C
- `humidity` – %
- `ph` – Soil pH
- `rainfall` – mm

**Crops supported (22):**
rice, maize, chickpea, kidneybeans, pigeonpeas, mothbeans, mungbean, blackgram, lentil, pomegranate, banana, mango, grapes, watermelon, muskmelon, apple, orange, papaya, coconut, cotton, jute, coffee

---

## 🗒️ Common Issues

| Problem | Fix |
|---------|-----|
| `"Model not loaded"` from API | Run `python model/train_model.py` first |
| App shows "Network request failed" | Check API URL in `constants/api.js` matches your PC's IP |
| SHAP warnings during training | Normal – SHAP may show deprecation warnings, model still works |
| `uvicorn` not found | Run `pip install uvicorn[standard]` |
| Slider not showing on Android | Make sure `@react-native-community/slider` was installed via `npx expo install` |

---

## 👨‍💻 Authors

Built as a production-quality demonstration of:
- End-to-end ML pipeline
- Explainable AI (SHAP)
- FastAPI backend
- React Native + Expo Go mobile frontend
