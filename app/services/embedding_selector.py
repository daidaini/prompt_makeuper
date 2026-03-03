"""
Embedding-based skill selector using sentence transformers.

This module provides fast, cost-effective skill selection using semantic
similarity between user prompts and skill descriptions via embeddings.

Note: This implementation requires sentence-transformers to be installed.
If the library is not available, the selector gracefully falls back
to None, allowing the optimizer to use LLM-based selection instead.
"""
from typing import List, Dict, Optional, Tuple
from functools import lru_cache

# Optional imports - embedding selector is not required for basic functionality
try:
    import numpy as np
    from scipy.spatial.distance import cosine
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    np = None
    cosine = None
    SentenceTransformer = None

from app.services.skill_manager import SkillManager


class EmbeddingSkillSelector:
    """
    Fast embedding-based skill selector.

    Uses sentence-transformers to compute semantic similarity between
    user prompts and skill descriptions. Much faster and cheaper than
    LLM-based selection (30-50x speedup).

    Model: all-MiniLM-L6-v2 (80MB, fast inference)

    If sentence-transformers is not installed, is_available() returns False
    and the optimizer will fall back to LLM-based selection.
    """

    def __init__(self, skill_manager: SkillManager, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding selector.

        Args:
            skill_manager: SkillManager instance with loaded skills
            model_name: HuggingFace model name for sentence transformers
        """
        if not EMBEDDINGS_AVAILABLE:
            print("Warning: sentence-transformers not installed. Embedding selector disabled.")
            print("To enable: pip install sentence-transformers")
            self.skill_manager = skill_manager
            self.model_name = model_name
            self._model = None
            self._skill_embeddings = None
            return

        self.skill_manager = skill_manager
        self.model_name = model_name
        self._model: Optional[SentenceTransformer] = None
        self._skill_embeddings: Optional[Dict[str, np.ndarray]] = None
        self._initialize()

    def _initialize(self) -> None:
        """
        Load the sentence transformer model and compute skill embeddings.

        This is done once at initialization to avoid repeated loading.
        Skills are embedded using a combination of name and description
        for better semantic matching.
        """
        if not EMBEDDINGS_AVAILABLE:
            return

        try:
            # Load the sentence transformer model
            self._model = SentenceTransformer(self.model_name)

            # Generate embeddings for all skills
            self._skill_embeddings = {}
            for skill_name, skill_data in self.skill_manager.skills.items():
                # Combine name and description for richer semantic representation
                skill_text = f"{skill_name}: {skill_data['description']}"
                embedding = self._model.encode(skill_text, convert_to_numpy=True)
                self._skill_embeddings[skill_name] = embedding

        except Exception as e:
            # Log error but don't fail - allows fallback to LLM selection
            print(f"Warning: Failed to initialize embedding selector: {e}")
            self._model = None
            self._skill_embeddings = None

    @lru_cache(maxsize=1000)
    def select_skill(self, prompt: str) -> Optional[str]:
        """
        Select the best skill for a given prompt using embedding similarity.

        Args:
            prompt: The user's input prompt

        Returns:
            Selected skill name, or None if embedding selector is unavailable
        """
        if self._model is None or self._skill_embeddings is None:
            return None

        try:
            # Generate embedding for the user prompt
            prompt_embedding = self._model.encode(prompt, convert_to_numpy=True)

            # Calculate cosine similarity with each skill
            similarities = {}
            for skill_name, skill_embedding in self._skill_embeddings.items():
                # Cosine similarity = 1 - cosine distance
                similarity = 1 - cosine(prompt_embedding, skill_embedding)
                similarities[skill_name] = similarity

            # Return the skill with highest similarity
            best_skill = max(similarities, key=similarities.get)
            return best_skill

        except Exception as e:
            print(f"Warning: Error during skill selection: {e}")
            return None

    def get_top_k_skills(self, prompt: str, k: int = 3) -> List[Tuple[str, float]]:
        """
        Get top-K candidate skills with similarity scores (for debugging).

        Args:
            prompt: The user's input prompt
            k: Number of top skills to return

        Returns:
            List of (skill_name, similarity_score) tuples, sorted by similarity
        """
        if self._model is None or self._skill_embeddings is None:
            return []

        try:
            # Generate embedding for the user prompt
            prompt_embedding = self._model.encode(prompt, convert_to_numpy=True)

            # Calculate cosine similarity with each skill
            similarities = {}
            for skill_name, skill_embedding in self._skill_embeddings.items():
                similarity = 1 - cosine(prompt_embedding, skill_embedding)
                similarities[skill_name] = similarity

            # Sort by similarity (descending) and return top-k
            sorted_skills = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
            return sorted_skills[:k]

        except Exception as e:
            print(f"Warning: Error during top-k selection: {e}")
            return []

    def is_available(self) -> bool:
        """
        Check if the embedding selector is properly initialized.

        Returns:
            True if ready to use, False otherwise
        """
        return self._model is not None and self._skill_embeddings is not None

    def clear_cache(self) -> None:
        """Clear the LRU cache (useful for testing or memory management)."""
        self.select_skill.cache_clear()
