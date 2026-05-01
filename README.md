# 🌾 Smart Agriculture AI System

> An AI-powered crop recommendation system with a React Native (Expo Go) mobile app and Python FastAPI backend featuring SHAP explainable AI.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![React Native](https://img.shields.io/badge/React%20Native-0.76+-blue.svg)](https://reactnative.dev/)
[![Expo](https://img.shields.io/badge/Expo-52.0+-black.svg)](https://expo.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [🌟 Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [📦 Installation & Setup](#-installation--setup)
- [🚀 Usage Guide](#-usage-guide)
- [📡 API Documentation](#-api-documentation)
- [🧠 Machine Learning Model](#-machine-learning-model)
- [🔍 Explainable AI (SHAP)](#-explainable-ai-shap)
- [🔧 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🌟 Features

### 🌱 **AI-Powered Crop Recommendations**
- **Machine Learning Models**: Random Forest & Logistic Regression trained on 2,200+ soil samples
- **7 Key Parameters**: Nitrogen (N), Phosphorus (P), Potassium (K), Temperature, Humidity, Soil pH, Rainfall
- **22 Crop Types**: Supports recommendations for 22 different crops including rice, wheat, maize, cotton, etc.

### 📱 **Mobile-First Design**
- **React Native + Expo**: Cross-platform mobile app (iOS & Android)
- **Intuitive UI**: Beautiful gradient design with smooth animations
- **Interactive Sliders**: Real-time value adjustment with visual feedback
- **Responsive Layout**: Optimized for various screen sizes

### 🧠 **Explainable AI**
- **SHAP Integration**: Understand exactly why the AI made each recommendation
- **Feature Importance**: Global model insights showing which factors matter most
- **Per-Prediction Explanations**: Detailed breakdown of how each input affected the result
- **Human-Readable Text**: Natural language explanations for farmers

### 🌤️ **Live Weather Integration**
- **OpenWeatherMap API**: Optional real-time weather data fetching
- **Auto-Fill**: Automatically populate temperature, humidity, and rainfall
- **Fallback Support**: Works offline with manual input

### ⚡ **High Performance**
- **FastAPI Backend**: Asynchronous API with automatic documentation
- **Model Caching**: Pre-loaded ML models for instant predictions
- **Optimized Mobile**: Smooth 60fps animations and interactions

---

## 🏗️ Architecture

```
Smart Agriculture AI System
├── 📱 Mobile App (React Native + Expo)
│   ├── Home Screen - Welcome & Feature Overview
│   ├── Predict Screen - Input Form with Sliders
│   └── Result Screen - AI Results & Explanations
│
├── 🔧 Backend API (FastAPI + Python)
│   ├── /predict - Main prediction endpoint
│   ├── /crops - List supported crops
│   ├── /model-info - Model metadata
│   └── / - Health check
│
└── 🤖 Machine Learning Pipeline
    ├── Data Processing (Pandas + Scikit-learn)
    ├── Model Training (Random Forest + Logistic Regression)
    ├── SHAP Explainability Engine
    └── Model Serialization (Joblib)
```

---

## 🛠️ Tech Stack

### Backend (Python)
- **FastAPI** - Modern, fast web framework for APIs
- **Scikit-learn** - Machine learning algorithms and preprocessing
- **SHAP** - Explainable AI for model interpretability
- **Pandas** - Data manipulation and analysis
- **Joblib** - Model serialization and caching
- **Uvicorn** - ASGI server for production deployment

### Mobile App (React Native)
- **React Native 0.76** - Cross-platform mobile development
- **Expo SDK 52** - Development platform and native APIs
- **React Navigation** - Screen navigation and routing
- **Expo Linear Gradient** - Beautiful gradient backgrounds
- **React Native Community Slider** - Custom slider components
- **Expo Vector Icons** - Icon library

### Development Tools
- **Python 3.8+** - Backend runtime
- **Node.js 18+** - Mobile development
- **Git** - Version control
- **VS Code** - Recommended IDE

---

## 📦 Installation & Setup

### Prerequisites

- **Python 3.8 or higher** ([Download](https://python.org))
- **Node.js 18+ and npm** ([Download](https://nodejs.org))
- **Expo CLI** (`npm install -g @expo/cli`)
- **Git** ([Download](https://git-scm.com))

### 1. Clone the Repository

```bash
git clone https://github.com/abi-shek-dev/Jacob_AI_Project_Smart_Agriculture.git
cd Jacob_AI_Project_Smart_Agriculture
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Train the machine learning model
python model/train_model.py

# Start the FastAPI server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO | Model loaded: Random Forest (acc=96.82%)
INFO:     Started server process [XXXX] using WatchFiles
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Mobile App Setup

```bash
# Open new terminal and navigate to mobile directory
cd mobile

# Install Node.js dependencies
npm install

# Update API configuration (if needed)
# Edit constants/api.js to match your backend IP

# Start Expo development server
npx expo start
```

### 4. Configure API Connection

**For Android Emulator:**
- Keep default: `http://10.0.2.2:8000`

**For Physical Device:**
- Update `mobile/constants/api.js`:
```javascript
export const API_BASE_URL = "http://YOUR_LOCAL_IP:8000";
```
- Find your IP: `ipconfig` (Windows) or `ifconfig` (macOS/Linux)

---

## 🚀 Usage Guide

### Mobile App Workflow

1. **Launch App**: Open Expo Go on your device and scan QR code
2. **Home Screen**: View features and tap "Get Started"
3. **Input Parameters**: Adjust 7 soil/climate parameters using sliders:
   - **Nitrogen (N)**: 0-140 kg/ha
   - **Phosphorus (P)**: 5-145 kg/ha
   - **Potassium (K)**: 5-205 kg/ha
   - **Temperature**: 8-44°C
   - **Humidity**: 14-100%
   - **Soil pH**: 3.5-9.0
   - **Rainfall**: 20-300 mm
4. **Optional Weather**: Enter city name for live weather data
5. **Get Prediction**: Tap "Get Crop Recommendation"
6. **View Results**: See AI recommendation with explanations

### Backend API Usage

```bash
# Health check
curl http://localhost:8000/

# Get prediction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "N": 50,
    "P": 50,
    "K": 50,
    "temperature": 25,
    "humidity": 70,
    "ph": 6.5,
    "rainfall": 100
  }'

# List supported crops
curl http://localhost:8000/crops

# Get model information
curl http://localhost:8000/model-info
```

---

## 📡 API Documentation

### Endpoints

#### `GET /`
**Health Check**
- **Response**: Server status and model information

#### `POST /predict`
**Crop Prediction**
- **Request Body**:
```json
{
  "N": 50,
  "P": 50,
  "K": 50,
  "temperature": 25.0,
  "humidity": 70.0,
  "ph": 6.5,
  "rainfall": 100.0,
  "city": "Mumbai"  // Optional
}
```
- **Response**:
```json
{
  "recommended_crop": "maize",
  "confidence_pct": 96.82,
  "feature_importance": {
    "N": 0.1234,
    "P": 0.0987,
    "K": 0.0876,
    "temperature": 0.1567,
    "humidity": 0.1432,
    "ph": 0.1123,
    "rainfall": 0.1345
  },
  "shap_values": {
    "N": 0.234,
    "P": -0.123,
    "K": 0.456,
    "temperature": 0.789,
    "humidity": -0.234,
    "ph": 0.123,
    "rainfall": 0.345
  },
  "explanation_text": "Recommended crop: maize (confidence: 96.8%)...",
  "weather_used": false,
  "model_used": "Random Forest"
}
```

#### `GET /crops`
**List Supported Crops**
- **Response**: Array of 22 crop names

#### `GET /model-info`
**Model Metadata**
- **Response**: Model accuracy, training details, feature names

### Error Responses

```json
{
  "detail": "Model not loaded. Run `python model/train_model.py` first."
}
```

---

## 🧠 Machine Learning Model

### Dataset
- **Source**: Crop Recommendation Dataset (2,200+ samples)
- **Features**: 7 soil and climate parameters
- **Target**: 22 crop types
- **Preprocessing**: Standard scaling, label encoding

### Model Comparison
- **Random Forest**: 96.82% accuracy (selected as best model)
- **Logistic Regression**: 95.45% accuracy
- **Training Time**: ~2-3 seconds
- **Inference Time**: <100ms per prediction

### Model Files Generated
```
backend/model/
├── best_model.pkl          # Selected model (Random Forest)
├── rf_model.pkl            # Random Forest (for SHAP)
├── scaler.pkl              # Feature scaler
├── label_encoder.pkl       # Crop name encoder
├── shap_explainer.pkl      # SHAP explainer
├── model_meta.json         # Model metadata
└── feature_importance.png  # Global feature importance chart
```

### Training Script
```bash
cd backend
python model/train_model.py
```

**Features:**
- Automatic model selection based on accuracy
- Cross-validation for robust evaluation
- SHAP explainer generation
- Model serialization for production use

---

## 🔍 Explainable AI (SHAP)

### What is SHAP?
SHAP (SHapley Additive exPlanations) explains the output of any machine learning model by calculating the contribution of each feature to the prediction.

### How It Works in This App

1. **Global Feature Importance**: Shows which features the model relies on most overall
2. **Local SHAP Values**: Explains how each feature affected THIS specific prediction
3. **Human-Readable Explanations**: Converts technical SHAP values into natural language

### Example SHAP Explanation

**Input Values:**
- Nitrogen: 50 kg/ha
- Phosphorus: 50 kg/ha
- Potassium: 50 kg/ha
- Temperature: 25°C
- Humidity: 70%
- Soil pH: 6.5
- Rainfall: 100 mm

**SHAP Analysis:**
- **Temperature (+0.789)**: High positive contribution - maize prefers moderate temperatures
- **Humidity (-0.234)**: Slight negative contribution - current humidity is optimal
- **Rainfall (+0.345)**: Positive contribution - adequate rainfall for maize growth
- **Nitrogen (+0.234)**: Positive contribution - good nitrogen levels for maize

**Result**: "Maize is recommended because the moderate temperature (25°C) strongly supports its growth, while adequate nitrogen and rainfall provide good conditions for development."

---

## 🔧 Troubleshooting

### Backend Issues

**"Model not loaded" Error**
```bash
# Solution: Train the model first
cd backend
python model/train_model.py
```

**Port 8000 already in use**
```bash
# Find process using port 8000
netstat -ano | findstr :8000
# Kill the process (replace XXXX with actual PID)
taskkill /PID XXXX /F
```

**Missing Dependencies**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Mobile App Issues

**"Unable to reach API" Error**
- Check if backend server is running: `http://localhost:8000`
- Update IP address in `mobile/constants/api.js`
- For physical device: Use your computer's local IP, not `10.0.2.2`
- Check firewall: Allow port 8000 inbound connections

**Expo Go Connection Issues**
```bash
# Clear Expo cache
npx expo start --clear

# Reset Metro bundler
npx expo r -c
```

**Slider UI Glitches**
- Restart the app completely
- Clear Expo cache: `npx expo start --clear`
- Reinstall node modules: `rm -rf node_modules && npm install`

### Common Development Issues

**Python Virtual Environment Issues**
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**React Native Build Issues**
```bash
# Clear all caches
npx expo install --fix
rm -rf node_modules
npm install
npx expo start --clear
```

**SHAP Installation Issues**
```bash
# Install SHAP with specific dependencies
pip install shap matplotlib numpy --force-reinstall
```

---

## 🤝 Contributing

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature-name`
3. **Make** your changes
4. **Test** thoroughly:
   - Backend: Run unit tests and API tests
   - Mobile: Test on both iOS and Android
5. **Commit** your changes: `git commit -m 'Add some feature'`
6. **Push** to the branch: `git push origin feature/your-feature-name`
7. **Open** a Pull Request

### Code Style Guidelines

**Python (Backend)**
- Follow PEP 8 style guide
- Use type hints for function parameters
- Add docstrings to all functions
- Maximum line length: 88 characters

**JavaScript/React Native**
- Use ESLint configuration
- Follow React Native best practices
- Use meaningful component and variable names
- Add comments for complex logic

### Testing Requirements

- **Backend**: Test all API endpoints with various inputs
- **Mobile**: Test on multiple devices and screen sizes
- **Integration**: Test complete prediction workflow
- **Edge Cases**: Test with extreme values and error conditions

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Dataset**: Crop Recommendation Dataset from Kaggle
- **SHAP Library**: Scott Lundberg and SHAP contributors
- **FastAPI**: Sebastián Ramirez and FastAPI contributors
- **React Native**: Meta (Facebook) and React Native contributors
- **Expo**: Expo team for the amazing development platform

---

## 📞 Support

For questions, issues, or contributions:

- **GitHub Issues**: [Report bugs or request features](https://github.com/abi-shek-dev/Jacob_AI_Project_Smart_Agriculture/issues)
- **GitHub Discussions**: Ask questions and get help
- **Email**: Contact the maintainers

---

**Happy Farming with AI! 🌾🤖**
