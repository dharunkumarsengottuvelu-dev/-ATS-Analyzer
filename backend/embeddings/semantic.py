_model = None

def get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            return None
    return _model

def calculate_semantic_similarity(resume_text: str, jd_text: str) -> float:
    """
    Calculates the cosine similarity between the full resume and the job description.
    Returns a percentage (0-100).
    Falls back to 0.0 if sentence_transformers is not installed.
    """
    if not resume_text or not jd_text:
        return 0.0

    model = get_model()
    if model is None:
        return 0.0

    try:
        from sentence_transformers import util
        import torch  # noqa: F401 — needed by sentence_transformers internally
        embeddings1 = model.encode(resume_text, convert_to_tensor=True)
        embeddings2 = model.encode(jd_text, convert_to_tensor=True)
        cosine_scores = util.cos_sim(embeddings1, embeddings2)
        score = cosine_scores[0][0].item()
        percentage = max(0.0, min(100.0, score * 100))
        return round(percentage, 2)
    except Exception:
        return 0.0
