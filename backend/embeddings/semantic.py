from sentence_transformers import SentenceTransformer, util
import torch

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def calculate_semantic_similarity(resume_text: str, jd_text: str) -> float:
    """
    Calculates the cosine similarity between the full resume and the job description.
    Returns a percentage (0-100).
    """
    if not resume_text or not jd_text:
        return 0.0
        
    # Compute embeddings
    model = get_model()
    embeddings1 = model.encode(resume_text, convert_to_tensor=True)
    embeddings2 = model.encode(jd_text, convert_to_tensor=True)
    
    # Compute cosine similarity
    cosine_scores = util.cos_sim(embeddings1, embeddings2)
    
    # Convert tensor to float and to percentage
    score = cosine_scores[0][0].item()
    
    # Ensure it's between 0 and 100
    percentage = max(0.0, min(100.0, score * 100))
    return round(percentage, 2)
