import os
import logging
from typing import Dict, Any, List

from backend.ai.recommendation.data_loader import DataLoader
from backend.ai.recommendation.cleaner import DataCleaner
from backend.ai.recommendation.feature_extractor import FeatureExtractor
from backend.ai.recommendation.vector_store import VectorStore
from backend.ai.recommendation.model_trainer import ModelTrainer
from backend.ai.recommendation.scorer import Scorer

logger = logging.getLogger(__name__)

class RecommendationEngine:
    def __init__(self, data_dir: str = "training_data"):
        self.data_loader = DataLoader(data_dir)
        self.cleaner = DataCleaner()
        self.feature_extractor = FeatureExtractor()
        
        # We assume project root is current working directory
        db_path = os.path.join("backend", "database", "chroma_db")
        model_path = os.path.join("backend", "models", "artifacts")
        
        self.vector_store = VectorStore(persist_directory=db_path)
        self.model_trainer = ModelTrainer(model_dir=model_path)
        self.scorer = Scorer(self.model_trainer)
        
        # Load the XGBoost model if it exists
        self.model_trainer.load_model()

    def run_training_pipeline(self) -> Dict[str, Any]:
        """
        Executes the entire ETL, Embedding, and XGBoost training pipeline.
        """
        logger.info("--- Starting Recommendation Engine Training Pipeline ---")
        
        # 1. Load Data
        raw_df = self.data_loader.load_all_data()
        if raw_df.empty:
            return {"status": "error", "message": "No data found to train."}
            
        # 2. Clean Data
        cleaned_df = self.cleaner.clean(raw_df)
        
        # 3. Extract Features
        featured_df = self.feature_extractor.extract_features(cleaned_df)
        
        # 4. Index in Vector Store (ChromaDB)
        self.vector_store.index_jobs(featured_df)
        
        # 5. Train XGBoost Ranking Model
        self.model_trainer.train(featured_df)
        
        logger.info("--- Training Pipeline Completed Successfully ---")
        return {
            "status": "success", 
            "message": "Model trained and embeddings indexed.",
            "total_jobs": len(featured_df)
        }

    def recommend_jobs(self, resume_data: Dict[str, Any], top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Takes parsed resume data and returns the top N recommended jobs.
        """
        logger.info("Processing resume for job recommendations...")
        
        # 1. Extract features from resume
        resume_features = self.feature_extractor.extract_resume_features(resume_data)
        query_text = resume_features["semantic_content"]
        
        # 2. Retrieve top candidates using Vector Search (fast filtering)
        # Fetch a bit more than top_n so XGBoost has a good pool to re-rank
        fetch_k = max(50, top_n * 3)
        candidate_ids, candidate_distances, candidate_metadatas = self.vector_store.search(
            query=query_text, 
            top_k=fetch_k
        )
        
        if not candidate_ids:
            logger.warning("No candidate jobs found in Vector Store.")
            return []
            
        # 3. Re-rank using Hybrid Scorer (XGBoost)
        ranked_results = self.scorer.score_candidates(
            resume_features=resume_features,
            candidate_metadatas=candidate_metadatas,
            candidate_distances=candidate_distances,
            candidate_ids=candidate_ids
        )
        
        # 4. Return Top N
        return ranked_results[:top_n]


_engine_instance = None

def get_recommendation_engine() -> RecommendationEngine:
    global _engine_instance
    if _engine_instance is None:
        logger.info("Initializing RecommendationEngine (this may take a moment)...")
        _engine_instance = RecommendationEngine()
    return _engine_instance
