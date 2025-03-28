import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

class VectorStore:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', index_path: str = 'vector_db/faiss.index'):
        self.model = SentenceTransformer(model_name)
        self.index_path = index_path
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = None
        self.texts = []
        self.load_or_create_index()

    def load_or_create_index(self):
        """Load existing index or create a new one."""
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            # Load texts from a separate file
            texts_path = self.index_path.replace('.index', '_texts.txt')
            if os.path.exists(texts_path):
                with open(texts_path, 'r', encoding='utf-8') as f:
                    self.texts = [line.strip() for line in f.readlines()]
        else:
            self.index = faiss.IndexFlatL2(self.dimension)

    def add_texts(self, texts: List[str]):
        """Add texts to the vector store."""
        if not texts:
            return

        # Create embeddings
        embeddings = self.model.encode(texts)
        
        # Add to FAISS index
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Save texts
        self.texts.extend(texts)
        
        # Save index and texts
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        texts_path = self.index_path.replace('.index', '_texts.txt')
        with open(texts_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.texts))

    def similarity_search(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        """Search for similar texts."""
        # Create query embedding
        query_embedding = self.model.encode([query])[0]
        
        # Search in FAISS
        distances, indices = self.index.search(
            np.array([query_embedding]).astype('float32'), k
        )
        
        # Return results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.texts):  # Ensure valid index
                results.append((self.texts[idx], float(distance)))
        
        return results 