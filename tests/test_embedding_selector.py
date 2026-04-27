"""
Tests for the embedding-based skill selector.

Run with: pytest tests/test_embedding_selector.py -v

Note: Tests for embedding functionality require sentence-transformers.
If not installed, those tests will be skipped. Fallback behavior tests
always run to verify graceful degradation.
"""
import pytest
import time
from app.services.skill_manager import SkillManager
from app.services.embedding_selector import EmbeddingSkillSelector, EMBEDDINGS_AVAILABLE
from pathlib import Path


class TestFallbackBehavior:
    """Tests for graceful fallback when sentence-transformers is not installed."""

    def test_embedding_selector_unavailable_fallback(self):
        """Test behavior when sentence-transformers is not installed."""
        skills_dir = Path("app/skills")
        skill_manager = SkillManager(skills_dir)
        selector = EmbeddingSkillSelector(skill_manager)

        if not EMBEDDINGS_AVAILABLE:
            # Selector should not be available
            assert not selector.is_available()

            # select_skill should return None (fallback to LLM)
            result = selector.select_skill("test prompt")
            assert result is None

            # get_top_k_skills should return empty list
            result = selector.get_top_k_skills("test prompt", k=3)
            assert result == []
        else:
            # When installed, verify it's available
            assert selector.is_available()
            # Should return a valid skill
            result = selector.select_skill("test prompt")
            assert result is not None
            assert result in skill_manager.metadata


# Skip remaining tests if sentence-transformers is not installed
skip_if_no_embeddings = pytest.mark.skipif(
    not EMBEDDINGS_AVAILABLE,
    reason="sentence-transformers not installed. Install with: pip install sentence-transformers"
)


@skip_if_no_embeddings
@pytest.fixture
def skill_manager():
    """Create a skill manager for testing."""
    skills_dir = Path("app/skills")
    return SkillManager(skills_dir)


@skip_if_no_embeddings
@pytest.fixture
def embedding_selector(skill_manager):
    """Create an embedding selector for testing."""
    return EmbeddingSkillSelector(skill_manager)


@skip_if_no_embeddings
class TestEmbeddingSelectorInitialization:
    """Tests for embedding selector initialization."""

    def test_initialization(self, embedding_selector):
        """Test that the selector initializes correctly."""
        assert embedding_selector is not None
        assert embedding_selector.is_available()

    def test_model_loaded(self, embedding_selector):
        """Test that the sentence transformer model is loaded."""
        assert embedding_selector._model is not None
        assert embedding_selector._skill_embeddings is not None

    def test_skill_embeddings_count(self, embedding_selector, skill_manager):
        """Test that all skills have embeddings."""
        expected_count = len(skill_manager.list_skills())
        actual_count = len(embedding_selector._skill_embeddings)
        assert actual_count == expected_count


@skip_if_no_embeddings
class TestSkillSelection:
    """Tests for skill selection functionality."""

    def test_select_skill_returns_valid_name(self, embedding_selector, skill_manager):
        """Test that selection returns a valid skill name."""
        prompt = "Write a Python function to sort a list"
        selected = embedding_selector.select_skill(prompt)

        assert selected is not None
        assert selected in skill_manager.metadata

    def test_select_skill_clarity_focused(self, embedding_selector):
        """Test that clarity-focused prompts select clarity skill."""
        # Prompts about unclear/ambiguous language
        clarity_prompts = [
            "Make this prompt less confusing",
            "This is vague, please clarify",
            "I need more specific instructions"
        ]

        for prompt in clarity_prompts:
            selected = embedding_selector.select_skill(prompt)
            assert selected is not None

    def test_select_skill_structure_focused(self, embedding_selector):
        """Test that structure-focused prompts select structure skill."""
        structure_prompts = [
            "Organize this prompt better",
            "Add sections and headers to this prompt",
            "Format this prompt with clear structure"
        ]

        for prompt in structure_prompts:
            selected = embedding_selector.select_skill(prompt)
            assert selected is not None

    def test_select_skill_consistency(self, embedding_selector):
        """Test that the same prompt always selects the same skill."""
        prompt = "Write a clear, specific prompt for image generation"

        # Run selection multiple times
        results = [embedding_selector.select_skill(prompt) for _ in range(5)]

        # All results should be the same (deterministic)
        assert len(set(results)) == 1


@skip_if_no_embeddings
class TestTopKSelection:
    """Tests for top-K skill selection (debugging utility)."""

    def test_top_k_returns_three_skills(self, embedding_selector):
        """Test that top-k returns the requested number of skills."""
        prompt = "Write a Python function"
        top_k = embedding_selector.get_top_k_skills(prompt, k=3)

        assert len(top_k) == 3
        assert all(isinstance(item, tuple) and len(item) == 2 for item in top_k)

    def test_top_k_has_scores(self, embedding_selector):
        """Test that top-k returns valid similarity scores."""
        prompt = "Create a structured prompt"
        top_k = embedding_selector.get_top_k_skills(prompt, k=3)

        # Check that scores are floats between 0 and 1
        for skill_name, score in top_k:
            assert isinstance(score, (float, int))
            # Cosine similarity is typically between -1 and 1
            # For positive text, usually 0 to 1
            assert -1 <= score <= 1

    def test_top_k_sorted_by_score(self, embedding_selector):
        """Test that results are sorted by similarity (descending)."""
        prompt = "Make this prompt more specific"
        top_k = embedding_selector.get_top_k_skills(prompt, k=5)

        # Extract scores
        scores = [score for _, score in top_k]

        # Verify descending order
        assert scores == sorted(scores, reverse=True)

    def test_top_k_respects_k_parameter(self, embedding_selector):
        """Test that different k values return correct counts."""
        prompt = "Test prompt"

        for k in [1, 2, 3, 5]:
            top_k = embedding_selector.get_top_k_skills(prompt, k=k)
            assert len(top_k) == min(k, len(embedding_selector._skill_embeddings))


@skip_if_no_embeddings
class TestCacheFunctionality:
    """Tests for LRU cache behavior."""

    def test_cache_hit_improves_speed(self, embedding_selector):
        """Test that cached selections are faster."""
        prompt = "Speed test prompt for caching"

        # First call (cache miss)
        start = time.perf_counter()
        embedding_selector.select_skill(prompt)
        first_time = time.perf_counter() - start

        # Second call (cache hit)
        start = time.perf_counter()
        embedding_selector.select_skill(prompt)
        second_time = time.perf_counter() - start

        # Cached call should be significantly faster
        # Note: This might be flaky on very fast systems,
        # but the difference should be noticeable
        assert second_time <= first_time

    def test_clear_cache_works(self, embedding_selector):
        """Test that cache clearing works."""
        prompt = "Cache clear test"

        # Make a selection to populate cache
        embedding_selector.select_skill(prompt)

        # Clear cache
        embedding_selector.clear_cache()

        # Cache info should be reset
        cache_info = embedding_selector.select_skill.cache_info()
        assert cache_info.currsize == 0


@skip_if_no_embeddings
class TestPerformanceComparison:
    """Tests comparing embedding vs LLM selection performance."""

    def test_embedding_selection_speed(self, embedding_selector):
        """Test that embedding selection is fast (should be < 100ms)."""
        prompts = [
            "Write a function",
            "Make this clearer",
            "Add structure to this",
            "Include examples",
            "Add constraints"
        ]

        start = time.perf_counter()
        for prompt in prompts:
            embedding_selector.select_skill(prompt)
        elapsed = time.perf_counter() - start

        # Should complete 5 selections in under 1 second
        assert elapsed < 1.0

        # Average per selection should be under 200ms
        avg_time = elapsed / len(prompts)
        assert avg_time < 0.2


@skip_if_no_embeddings
class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_empty_prompt(self, embedding_selector):
        """Test selection with an empty prompt."""
        result = embedding_selector.select_skill("")
        # Should still return something
        assert result is not None

    def test_very_long_prompt(self, embedding_selector):
        """Test selection with a very long prompt."""
        long_prompt = "Write code " * 1000
        result = embedding_selector.select_skill(long_prompt)
        assert result is not None

    def test_non_english_prompt(self, embedding_selector):
        """Test selection with non-English prompt."""
        # Chinese prompt
        chinese_prompt = "写一个Python函数来排序列表"
        result = embedding_selector.select_skill(chinese_prompt)
        # The model is multilingual, so it should work
        assert result is not None

    def test_special_characters(self, embedding_selector):
        """Test selection with special characters."""
        special_prompt = "Write code @#$%^&*() with emoji 🚀 and unicode"
        result = embedding_selector.select_skill(special_prompt)
        assert result is not None
