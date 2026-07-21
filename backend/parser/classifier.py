import os
import joblib
from backend.models.train_classifier import clean_text

class ResumeClassifier:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        # Model is loaded lazily on first prediction

    def load_model(self):
        artifacts_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'artifacts')
        model_path = os.path.join(artifacts_dir, 'resume_classifier.pkl')
        vectorizer_path = os.path.join(artifacts_dir, 'tfidf_vectorizer.pkl')

        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            try:
                self.model = joblib.load(model_path)
                self.vectorizer = joblib.load(vectorizer_path)
                print("Successfully loaded resume category classification model.")
            except Exception as e:
                print(f"Error loading classification model: {e}")
        else:
            print("Classification model artifacts not found. Run train_classifier.py first.")

    def predict_category(self, text: str) -> str:
        if not self.model or not self.vectorizer:
            self.load_model()
            
        if not self.model or not self.vectorizer or not text:
            return "Unknown"
        
        cleaned = clean_text(text)
        if not cleaned:
            return "Unknown"
            
        vec = self.vectorizer.transform([cleaned])
        prediction = self.model.predict(vec)
        return str(prediction[0])

# Global instance to be imported and used
classifier_instance = ResumeClassifier()

def predict_resume_category(text: str) -> str:
    return classifier_instance.predict_category(text)
