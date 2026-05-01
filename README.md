# 🌾 Smart Agriculture AI System

> An AI-powered crop recommendation system with a React Native (Expo Go) mobile app and Python FastAPI backend.

---

## 📁 Project Structure

```
Jacob_AI_Project/
├── backend/                          ← Python FastAPI & ML Logic
│   ├── api/                          ← FastAPI server
│   ├── data/                         ← Dataset (CSV)
│   ├── model/                        ← Trained models & training script
│   ├── utils/                        ← Data pipeline & XAI logic
│   ├── requirements.txt              ← Python dependencies
│   └── .gitignore
│
└── mobile/                           ← React Native Expo Go app
    ├── screens/                      ← App screens (Home, Predict, Result)
    ├── constants/                    ← API & Theme configuration
    ├── App.js                        ← Navigation root
    └── package.json
```

---

## 🚀 Setup & Running

### 1. Backend (FastAPI + ML)
1.  **Navigate to backend**: `cd backend`
2.  **Install dependencies**: `pip install -r requirements.txt`
3.  **Train the model**: `python model/train_model.py`
4.  **Start the server**: `uvicorn api.main:app --reload --host 0.0.0.0 --port 8000`

### 2. Mobile (Expo Go)
1.  **Navigate to mobile**: `cd mobile`
2.  **Update API URL**: Open `constants/api.js` and set your local IP.
3.  **Start Expo**: `npx expo start`
4.  Scan the QR code with **Expo Go**.

---

## 🧠 Explainable AI
The system uses **SHAP (SHapley Additive exPlanations)** to explain exactly why a crop was recommended based on your soil's N, P, K, pH, and climate data.
