import os
import logging
import random
import numpy as np
import pandas as pd
import xgboost as xgb
import optuna
from sklearn.model_selection import KFold
import joblib

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, model_dir: str = "backend/models/artifacts"):
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        self.model_path = os.path.join(self.model_dir, "xgboost_ranker.joblib")
        self.model = None

    def generate_synthetic_training_data(self, df_jobs: pd.DataFrame, n_samples: int = 5000) -> pd.DataFrame:
        """
        Generates synthetic pairs of (Resume, Job) features to bootstrap the XGBoost model.
        In a real scenario, this would come from historical user applications/hires.
        """
        if df_jobs.empty:
            return pd.DataFrame()
            
        logger.info("Generating synthetic training data for XGBoost...")
        
        training_data = []
        jobs_list = df_jobs.to_dict('records')
        
        for _ in range(n_samples):
            # Select a random job
            job = random.choice(jobs_list)
            
            # 50% chance of creating a good match, 50% chance of a bad match
            is_good_match = random.random() > 0.5
            
            job_skills = set([s.strip().lower() for s in str(job.get("required_skills", "")).split(",") if s.strip()])
            num_job_skills = len(job_skills)
            
            if is_good_match:
                # Good match: high skill overlap, matching experience, high semantic sim
                overlap_ratio = random.uniform(0.6, 1.0)
                semantic_sim = random.uniform(0.7, 0.99)
                exp_diff = random.uniform(-1, 2)
            else:
                # Bad match: low skill overlap, mismatched experience, low semantic sim
                overlap_ratio = random.uniform(0.0, 0.3)
                semantic_sim = random.uniform(0.1, 0.4)
                exp_diff = random.uniform(-5, -2) # Resume has much less experience
                
            skill_overlap_count = int(num_job_skills * overlap_ratio)
            
            # Target Score Heuristic (0.0 to 1.0)
            target_score = (overlap_ratio * 0.5) + (semantic_sim * 0.4)
            if exp_diff >= 0:
                target_score += 0.1
            target_score = max(0.0, min(1.0, target_score))
            
            feature_vector = {
                "job_id": job.get("job_id"),
                "skill_overlap_ratio": overlap_ratio,
                "skill_overlap_count": skill_overlap_count,
                "semantic_similarity": semantic_sim,
                "experience_diff": exp_diff,
                "target_score": target_score
            }
            training_data.append(feature_vector)
            
        return pd.DataFrame(training_data)

    def train(self, df_jobs: pd.DataFrame):
        df_train = self.generate_synthetic_training_data(df_jobs)
        if df_train.empty:
            logger.warning("No data to train XGBoost model.")
            return

        X = df_train[["skill_overlap_ratio", "skill_overlap_count", "semantic_similarity", "experience_diff"]]
        y = df_train["target_score"]

        logger.info("Starting Hyperparameter Tuning with Optuna...")
        
        def objective(trial):
            param = {
                'max_depth': trial.suggest_int('max_depth', 3, 9),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            }
            
            kf = KFold(n_splits=3, shuffle=True, random_state=42)
            scores = []
            
            for train_idx, val_idx in kf.split(X):
                X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]
                
                model = xgb.XGBRegressor(**param, random_state=42, objective='reg:squarederror')
                model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
                
                preds = model.predict(X_val)
                # RMSE
                rmse = np.sqrt(np.mean((y_val - preds)**2))
                scores.append(rmse)
                
            return np.mean(scores)

        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=10) # Keep trials low for speed
        
        best_params = study.best_params
        logger.info(f"Best params found: {best_params}")
        
        logger.info("Training final model on full dataset...")
        self.model = xgb.XGBRegressor(**best_params, random_state=42, objective='reg:squarederror')
        self.model.fit(X, y)
        
        joblib.dump(self.model, self.model_path)
        logger.info(f"Model saved to {self.model_path}")

    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        else:
            logger.warning("XGBoost model not found. Call train() first.")

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            self.load_model()
            
        if self.model is None or features.empty:
            return np.zeros(len(features))
            
        X = features[["skill_overlap_ratio", "skill_overlap_count", "semantic_similarity", "experience_diff"]]
        return self.model.predict(X)
