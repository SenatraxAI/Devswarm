"""
Vector Store implementation for semantic search using FAISS and SentenceTransformers.
Provides long-term memory capabilities for the Swarm.
"""
import os
import json
import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from pathlib import Path

# Import dependencies
try:
    from sentence_transformers import SentenceTransformer
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

class VectorStore:
    """
    Manages semantic search index using FAISS.
    Stores embeddings for easy retrieval of relevant context.
    """
    def __init__(self, project_id: str = "default", data_dir: str = "data/vectors"):
        self.project_id = project_id
        self.index_dir = Path(data_dir) / project_id
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_path = self.index_dir / "index.faiss"
        self.metadata_path = self.index_dir / "metadata.json"
        
        self.model = None
        self.index = None
        self.metadata: List[Dict] = []
        self.HAS_DEPS = HAS_DEPS # Set instance attribute
        
        if HAS_DEPS:
            # Load model (lazy load could be better but sticking to init for now)
            print(f"🧠 Loading embedding model for project {project_id}...")
            # Use a lightweight model for speed
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self._load_index()
        else:
            print("⚠️ Vector dependencies missing. Semantic search disabled.")

    def _load_index(self):
        """Load FAISS index and metadata from disk"""
        if self.index_path.exists() and self.metadata_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                print(f"✅ Loaded vector index with {self.index.ntotal} entries")
            except Exception as e:
                print(f"❌ Error loading vector index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        """Create a new FAISS index"""
        # Dimension for all-MiniLM-L6-v2 is 384
        embedding_dim = 384 
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.metadata = []
        print("✨ Created new vector index")

    def add_text(self, text: str, meta: Dict[str, Any] = None):
        """
        Add text to the vector store.
        
        Args:
            text: The text content to embed
            meta: Metadata associated with the text (e.g. event_id, agent)
        """
        if not HAS_DEPS or not self.model or not self.index:
            return

        try:
            # Generate embedding
            embedding = self.model.encode([text])
            
            # Add to index
            self.index.add(np.array(embedding).astype('float32'))
            
            # Store metadata
            self.metadata.append({
                "text": text,
                "meta": meta or {}
            })
            
            # Save strictly to avoid data loss
            self.save()
            
        except Exception as e:
            print(f"❌ Error adding to vector store: {e}")

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar texts.
        
        Args:
            query: The search query
            k: Number of results to return
            
        Returns:
            List of results with text, metadata, and score
        """
        if not HAS_DEPS or not self.model or not self.index or self.index.ntotal == 0:
            return []

        try:
            # Embed query
            query_vector = self.model.encode([query])
            
            # Search
            D, I = self.index.search(np.array(query_vector).astype('float32'), k)
            
            results = []
            for i, idx in enumerate(I[0]):
                if idx != -1 and idx < len(self.metadata):
                    item = self.metadata[idx]
                    results.append({
                        "text": item["text"],
                        "metadata": item["meta"],
                        "score": float(D[0][i])
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

    def save(self):
        """Save index and metadata to disk"""
        if not self.index:
            return
            
        try:
            faiss.write_index(self.index, str(self.index_path))
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving vector store: {e}")
