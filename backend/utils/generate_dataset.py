"""
generate_dataset.py
===================
Creates a synthetic crop recommendation dataset.

If you have the real Kaggle dataset (Crop_recommendation.csv), you can
skip this step and place the CSV directly in data/.

The synthetic data is designed to match the statistical distributions of
the real dataset so models trained on it behave realistically.
"""

import os
import numpy as np
import pandas as pd

# Reproducibility
np.random.seed(42)

# ── Crop profiles: realistic soil & climate ranges ───────────────────────────
# Each crop has (mean, std) for every feature.
CROP_PROFILES = {
    "rice":        dict(N=(80, 10), P=(40,  8), K=(40,  8), temp=(25,  2), hum=(82, 5), ph=(6.5, 0.3), rain=(200, 30)),
    "maize":       dict(N=(80, 12), P=(48, 10), K=(50, 10), temp=(22,  2), hum=(65, 6), ph=(6.2, 0.3), rain=(65,  12)),
    "chickpea":    dict(N=(40,  8), P=(68, 10), K=(80, 10), temp=(18,  2), hum=(17, 4), ph=(7.2, 0.3), rain=(72,  10)),
    "kidneybeans": dict(N=(20,  5), P=(68, 10), K=(20,  5), temp=(19,  2), hum=(22, 4), ph=(5.7, 0.3), rain=(105, 15)),
    "pigeonpeas":  dict(N=(20,  5), P=(68,  8), K=(20,  5), temp=(28,  2), hum=(48, 6), ph=(5.7, 0.3), rain=(150, 20)),
    "mothbeans":   dict(N=(20,  5), P=(48,  8), K=(20,  5), temp=(28,  2), hum=(53, 6), ph=(6.8, 0.3), rain=(51,  10)),
    "mungbean":    dict(N=(20,  5), P=(48,  8), K=(20,  5), temp=(29,  2), hum=(85, 5), ph=(6.6, 0.3), rain=(48,   8)),
    "blackgram":   dict(N=(40,  8), P=(68, 10), K=(30,  6), temp=(30,  2), hum=(65, 6), ph=(7.0, 0.3), rain=(67,  10)),
    "lentil":      dict(N=(18,  4), P=(68,  8), K=(19,  4), temp=(24,  2), hum=(65, 6), ph=(6.9, 0.3), rain=(44,   8)),
    "pomegranate": dict(N=(18,  4), P=(18,  4), K=(40,  8), temp=(22,  2), hum=(90, 5), ph=(6.5, 0.3), rain=(107, 15)),
    "banana":      dict(N=(100,12), P=(82, 12), K=(50, 10), temp=(27,  2), hum=(80, 5), ph=(5.8, 0.3), rain=(105, 15)),
    "mango":       dict(N=(20,  5), P=(18,  4), K=(30,  6), temp=(31,  2), hum=(50, 6), ph=(5.7, 0.3), rain=(95,  12)),
    "grapes":      dict(N=(20,  5), P=(125,15), K=(200,20), temp=(24,  2), hum=(82, 5), ph=(6.0, 0.3), rain=(68,  10)),
    "watermelon":  dict(N=(100,12), P=(15,  4), K=(50, 10), temp=(25,  2), hum=(85, 5), ph=(6.5, 0.3), rain=(50,   8)),
    "muskmelon":   dict(N=(100,12), P=(18,  4), K=(50, 10), temp=(29,  2), hum=(92, 5), ph=(6.3, 0.3), rain=(25,   5)),
    "apple":       dict(N=(20,  5), P=(134,15), K=(200,20), temp=(22,  2), hum=(92, 5), ph=(5.8, 0.3), rain=(113, 15)),
    "orange":      dict(N=(20,  5), P=(16,  4), K=(10,  3), temp=(23,  2), hum=(92, 5), ph=(7.0, 0.3), rain=(110, 15)),
    "papaya":      dict(N=(50,  8), P=(59,  8), K=(50, 10), temp=(34,  2), hum=(92, 5), ph=(6.7, 0.3), rain=(143, 18)),
    "coconut":     dict(N=(20,  5), P=(18,  4), K=(30,  6), temp=(27,  2), hum=(94, 5), ph=(5.9, 0.3), rain=(175, 20)),
    "cotton":      dict(N=(118,12), P=(46,  8), K=(20,  5), temp=(24,  2), hum=(80, 5), ph=(6.5, 0.3), rain=(82,  12)),
    "jute":        dict(N=(78, 10), P=(46,  8), K=(40,  8), temp=(25,  2), hum=(80, 5), ph=(6.7, 0.3), rain=(174, 20)),
    "coffee":      dict(N=(100,12), P=(28,  6), K=(30,  6), temp=(27,  2), hum=(57, 6), ph=(6.5, 0.3), rain=(155, 20)),
}

SAMPLES_PER_CROP = 100   # 22 crops × 100 = 2,200 total rows


def generate(output_path: str = "data/crop_recommendation.csv"):
    """Generate synthetic dataset and save to CSV."""
    rows = []
    for crop, profile in CROP_PROFILES.items():
        for _ in range(SAMPLES_PER_CROP):
            row = {
                "N":           max(0, np.random.normal(*profile["N"])),
                "P":           max(0, np.random.normal(*profile["P"])),
                "K":           max(0, np.random.normal(*profile["K"])),
                "temperature": max(0, np.random.normal(*profile["temp"])),
                "humidity":    np.clip(np.random.normal(*profile["hum"]),   0, 100),
                "ph":          np.clip(np.random.normal(*profile["ph"]),  3.5, 9.0),
                "rainfall":    max(0, np.random.normal(*profile["rain"])),
                "label":       crop,
            }
            rows.append(row)

    df = pd.DataFrame(rows)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[Dataset] Generated {len(df):,} rows -> {output_path}")
    return df


if __name__ == "__main__":
    generate()
