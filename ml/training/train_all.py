"""
Master Training Script
========================
Trains all 6 ML models and saves them as .joblib files.
Run this script once during development to generate bundled models.

Usage:
    python ml/training/train_all.py

Output:
    ml/models/bug_detector.joblib
    ml/models/security_risk.joblib
    ml/models/severity_classifier.joblib
    ml/models/quality_scorer.joblib
    ml/models/maintainability_scorer.joblib
    ml/models/readability_scorer.joblib
    ml/models/scaler.joblib
    ml/models/metadata.json
"""

import sys
import os
import json
import time
import numpy as np
import pandas as pd
import joblib
import warnings

from pathlib import Path

warnings.filterwarnings('ignore')

# Setup paths
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
ML_DIR       = os.path.dirname(SCRIPT_DIR)
ROOT_DIR     = os.path.dirname(ML_DIR)
MODELS_DIR   = os.path.join(ML_DIR, 'models')

sys.path.insert(0, ROOT_DIR)
os.makedirs(MODELS_DIR, exist_ok=True)

from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor, RandomForestRegressor
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    classification_report, confusion_matrix,
    mean_absolute_error, r2_score, roc_auc_score
)
from xgboost import XGBClassifier

from ml.training.generate_training_data import generate_training_data, FEATURE_NAMES


def train_all():
    """Train all 6 ML models and save to the models directory."""
    print("=" * 60)
    print("Offline Code Review Assistant — ML Training Pipeline")
    print("=" * 60)
    start_time = time.time()
    
    # Step 1: Generate training data
    print("\n[1/8] Generating synthetic training data...")
    df = generate_training_data(n_samples=10000)
    
    X = df[FEATURE_NAMES].values
    
    # Step 2: Fit feature scaler
    print("[2/8] Fitting feature scaler...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, os.path.join(MODELS_DIR, 'scaler.joblib'), compress=3)
    print(f"  Saved: scaler.joblib")
    
    # Step 3: Bug Probability — Random Forest Classifier
    print("[3/8] Training Bug Detector (Random Forest)...")
    y_bug = df['has_bug'].values
    X_tr, X_te, y_tr, y_te = train_test_split(X_scaled, y_bug, test_size=0.2, random_state=42, stratify=y_bug)
    
    bug_model = RandomForestClassifier(
        n_estimators=100, max_depth=12, min_samples_leaf=5,
        class_weight='balanced', random_state=42, n_jobs=-1,
    )
    bug_model.fit(X_tr, y_tr)
    y_pred = bug_model.predict(X_te)
    y_prob = bug_model.predict_proba(X_te)[:, 1]
    
    print(f"  Accuracy: {bug_model.score(X_te, y_te):.3f}")
    print(f"  AUC-ROC: {roc_auc_score(y_te, y_prob):.3f}")
    joblib.dump(bug_model, os.path.join(MODELS_DIR, 'bug_detector.joblib'), compress=3)
    print(f"  Saved: bug_detector.joblib")
    
    # Step 4: Security Risk — XGBoost Classifier
    print("[4/8] Training Security Risk Classifier (XGBoost)...")
    y_sec = df['has_security_risk'].values
    X_tr, X_te, y_tr, y_te = train_test_split(X_scaled, y_sec, test_size=0.2, random_state=42, stratify=y_sec)
    
    sec_model = XGBClassifier(
        n_estimators=150, max_depth=6, learning_rate=0.1,
        subsample=0.8, colsample_bytree=0.8,
        eval_metric='logloss', random_state=42,
        use_label_encoder=False,
    )
    sec_model.fit(X_tr, y_tr)
    y_pred = sec_model.predict(X_te)
    y_prob = sec_model.predict_proba(X_te)[:, 1]
    
    print(f"  Accuracy: {sec_model.score(X_te, y_te):.3f}")
    print(f"  AUC-ROC: {roc_auc_score(y_te, y_prob):.3f}")
    joblib.dump(sec_model, os.path.join(MODELS_DIR, 'security_risk.joblib'), compress=3)
    print(f"  Saved: security_risk.joblib")
    
    # Step 5: Issue Severity — SVM Classifier
    print("[5/8] Training Severity Classifier (SVM)...")
    le = LabelEncoder()
    y_sev = le.fit_transform(df['severity_label'].values)
    X_tr, X_te, y_tr, y_te = train_test_split(X_scaled, y_sev, test_size=0.2, random_state=42, stratify=y_sev)
    
    sev_model = SVC(
        kernel='rbf', C=10.0, gamma='scale',
        probability=True, class_weight='balanced', random_state=42,
    )
    sev_model.fit(X_tr, y_tr)
    
    print(f"  Accuracy: {sev_model.score(X_te, y_te):.3f}")
    print(f"  Classes: {list(le.classes_)}")
    joblib.dump(sev_model, os.path.join(MODELS_DIR, 'severity_classifier.joblib'), compress=3)
    joblib.dump(le,        os.path.join(MODELS_DIR, 'severity_label_encoder.joblib'), compress=3)
    print(f"  Saved: severity_classifier.joblib")
    
    # Step 6: Code Quality Score — Gradient Boosting Regressor
    print("[6/8] Training Quality Scorer (Gradient Boosting)...")
    y_qual = df['quality_score'].values
    X_tr, X_te, y_tr, y_te = train_test_split(X_scaled, y_qual, test_size=0.2, random_state=42)
    
    qual_model = GradientBoostingRegressor(
        n_estimators=150, max_depth=5, learning_rate=0.1,
        subsample=0.8, min_samples_leaf=5, random_state=42,
    )
    qual_model.fit(X_tr, y_tr)
    y_pred = qual_model.predict(X_te)
    
    print(f"  MAE: {mean_absolute_error(y_te, y_pred):.2f}")
    print(f"  R²:  {r2_score(y_te, y_pred):.3f}")
    joblib.dump(qual_model, os.path.join(MODELS_DIR, 'quality_scorer.joblib'), compress=3)
    print(f"  Saved: quality_scorer.joblib")
    
    # Step 7: Maintainability Score — Random Forest Regressor
    print("[7/8] Training Maintainability Scorer (Random Forest)...")
    y_maint = df['maintainability_score'].values
    X_tr, X_te, y_tr, y_te = train_test_split(X_scaled, y_maint, test_size=0.2, random_state=42)
    
    maint_model = RandomForestRegressor(
        n_estimators=100, max_depth=10, min_samples_leaf=5,
        random_state=42, n_jobs=-1,
    )
    maint_model.fit(X_tr, y_tr)
    y_pred = maint_model.predict(X_te)
    
    print(f"  MAE: {mean_absolute_error(y_te, y_pred):.2f}")
    print(f"  R²:  {r2_score(y_te, y_pred):.3f}")
    joblib.dump(maint_model, os.path.join(MODELS_DIR, 'maintainability_scorer.joblib'), compress=3)
    print(f"  Saved: maintainability_scorer.joblib")
    
    # Step 8: Readability Score — Gradient Boosting Regressor
    print("[8/8] Training Readability Scorer (Gradient Boosting)...")
    y_read = df['readability_score'].values
    X_tr, X_te, y_tr, y_te = train_test_split(X_scaled, y_read, test_size=0.2, random_state=42)
    
    read_model = GradientBoostingRegressor(
        n_estimators=150, max_depth=4, learning_rate=0.1,
        subsample=0.8, min_samples_leaf=5, random_state=42,
    )
    read_model.fit(X_tr, y_tr)
    y_pred = read_model.predict(X_te)
    
    print(f"  MAE: {mean_absolute_error(y_te, y_pred):.2f}")
    print(f"  R²:  {r2_score(y_te, y_pred):.3f}")
    joblib.dump(read_model, os.path.join(MODELS_DIR, 'readability_scorer.joblib'), compress=3)
    print(f"  Saved: readability_scorer.joblib")
    
    # Save metadata
    elapsed = time.time() - start_time
    metadata = {
        "version": "1.0.0",
        "trained_at": pd.Timestamp.now().isoformat(),
        "training_samples": len(df),
        "feature_names": FEATURE_NAMES,
        "feature_count": len(FEATURE_NAMES),
        "models": {
            "bug_detector":            {"algorithm": "RandomForestClassifier",    "type": "classification"},
            "security_risk":           {"algorithm": "XGBClassifier",             "type": "classification"},
            "severity_classifier":     {"algorithm": "SVC",                       "type": "classification"},
            "quality_scorer":          {"algorithm": "GradientBoostingRegressor", "type": "regression"},
            "maintainability_scorer":  {"algorithm": "RandomForestRegressor",     "type": "regression"},
            "readability_scorer":      {"algorithm": "GradientBoostingRegressor", "type": "regression"},
        },
        "training_time_seconds": round(elapsed, 2),
    }
    
    with open(os.path.join(MODELS_DIR, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n[OK] All 6 models trained in {elapsed:.1f}s")
    print(f"[OK] Models saved to: {MODELS_DIR}")
    print(f"[OK] Metadata saved to: {MODELS_DIR}/metadata.json")


if __name__ == '__main__':
    train_all()
