import os
import logging
from typing import List, Dict, Any, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persist_directory: str = "backend/database/chroma_db", collection_name: str = "jobs"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Ensure directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Initialize Embedding Model
        logger.info("Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate dense vector embeddings using SentenceTransformers."""
        if not texts:
            return []
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def index_jobs(self, df):
        """Index job dataframe into ChromaDB."""
        import pandas as pd
        if df.empty:
            logger.warning("Empty dataframe provided for indexing.")
            return

        logger.info(f"Indexing {len(df)} jobs into ChromaDB...")
        
        ids = df["job_id"].astype(str).tolist()
        documents = df["semantic_content"].tolist()
        
        # Generate metadata dicts (excluding complex types or long texts)
        metadatas = []
        for _, row in df.iterrows():
            meta = {
                "job_title": str(row.get("job_title", "")),
                "company_name": str(row.get("company_name", "")),
                "location": str(row.get("location", "")),
                "experience_years": float(row.get("experience_years", 0.0)),
                "required_skills": str(row.get("required_skills", ""))
            }
            metadatas.append(meta)
            
        embeddings = self.generate_embeddings(documents)
        
        # ChromaDB requires batches if data is huge, but for now we assume it fits in memory 
        # (Chroma's default max batch size is usually 41666 or similar, we can batch if needed)
        batch_size = 5000
        for i in range(0, len(ids), batch_size):
            self.collection.upsert(
                ids=ids[i:i+batch_size],
                embeddings=embeddings[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
                documents=documents[i:i+batch_size]
            )
            
        logger.info(f"Successfully indexed {len(ids)} jobs.")

    def _reload_client(self):
        """Re-initializes the ChromaDB persistent client to pick up updated index files on disk."""
        logger.info("Refreshing ChromaDB PersistentClient handle...")
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def search(self, query: str, top_k: int = 100) -> Tuple[List[str], List[float], List[Dict[str, Any]]]:
        """
        Search for top_k similar jobs using semantic search.
        Returns: (job_ids, distances, metadatas)
        """
        if not query or not query.strip():
            return [], [], []

        query_embedding = self.generate_embeddings([query])[0]
        
        # Ensure top_k does not exceed total count in collection if known
        try:
            total_count = self.collection.count()
            if total_count == 0:
                logger.warning("VectorStore collection is currently empty.")
                return [], [], []
            n_results = min(top_k, total_count)
        except Exception:
            n_results = top_k

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["metadatas", "distances"]
            )
        except Exception as e:
            logger.warning(f"ChromaDB query error ({e}). Attempting client refresh and retry...")
            try:
                self._reload_client()
                total_count = self.collection.count()
                if total_count == 0:
                    return [], [], []
                n_results = min(top_k, total_count)
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    include=["metadatas", "distances"]
                )
            except Exception as retry_err:
                logger.error(f"ChromaDB retry failed: {retry_err}")
                return [], [], []
        
        if not results or not results.get('ids') or not results['ids'][0]:
            return [], [], []
            
        # ChromaDB returns a list of lists since we can query multiple vectors at once
        job_ids = results['ids'][0]
        distances = results['distances'][0]
        metadatas = results['metadatas'][0]
        
        return job_ids, distances, metadatas
