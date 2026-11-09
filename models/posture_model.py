"""
Lightweight posture classifier trained on provided angle datasets.
Uses a RandomForestClassifier over the angle features.
"""

import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from typing import Tuple, Optional


ARTIFACT_DIR = "artifacts"
MODEL_PATH = os.path.join(ARTIFACT_DIR, "posture_model.pkl")


class PostureClassifier:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.features = []
        os.makedirs(ARTIFACT_DIR, exist_ok=True)

    def _load_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        angles_path = os.path.join("archive", "angles.csv")
        labels_path = os.path.join("archive", "labels.csv")
        angles_df = pd.read_csv(angles_path)
        labels_df = pd.read_csv(labels_path)
        merged = angles_df.merge(labels_df, on="pose_id")
        X = merged.drop(columns=["pose_id", "pose"])
        y = merged["pose"]
        return X, y

    def train(self) -> None:
        X, y = self._load_data()
        self.features = list(X.columns)
        self.label_encoder = LabelEncoder()
        y_enc = self.label_encoder.fit_transform(y)

        # RandomForest for robustness without heavy tuning
        clf = RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            random_state=42,
            n_jobs=-1,
            class_weight="balanced"
        )
        clf.fit(X, y_enc)

        self.model = clf
        joblib.dump(
            {"model": clf, "label_encoder": self.label_encoder, "features": self.features},
            MODEL_PATH
        )

    def load(self) -> bool:
        if not os.path.exists(MODEL_PATH):
            return False
        data = joblib.load(MODEL_PATH)
        self.model = data["model"]
        self.label_encoder = data["label_encoder"]
        self.features = data["features"]
        return True

    def ensure_model(self) -> None:
        if not self.load():
            self.train()

    def predict(self, angles: dict) -> Tuple[Optional[str], float]:
        if not self.model or not self.label_encoder:
            return None, 0.0
        if not angles:
            return None, 0.0

        # Build feature vector with defaults if missing
        row = []
        for f in self.features:
            row.append(float(angles.get(f, 0.0)))
        probas = self.model.predict_proba([row])[0]
        idx = probas.argmax()
        label = self.label_encoder.inverse_transform([idx])[0]
        confidence = float(probas[idx])
        return label, confidence


