import pytest
from app.services.skill_manager import SkillManager
from app.services.optimizer import PromptOptimizer
from pathlib import Path


def test_skill_manager_initialization():
    """Test that SkillManager indexes all skills from SKILL.md metadata."""
    skills_dir = Path("app/skills")
    manager = SkillManager(skills_dir)

    skills = manager.list_skills()
    expected_skills = [
        "clarity",
        "specificity",
        "structure",
        "examples",
        "constraints",
        "mental_model",
        "progressive",
        "self_verify",
    ]

    assert len(skills) == 8
    assert all(skill in skills for skill in expected_skills)


def test_skill_manager_get_skill():
    """Test retrieving and parsing an individual SKILL.md file."""
    skills_dir = Path("app/skills")
    manager = SkillManager(skills_dir)

    clarity_skill = manager.get_skill("clarity")
    assert clarity_skill is not None
    assert clarity_skill.name == "clarity"
    assert clarity_skill.description
    assert "You are a prompt clarity expert" in clarity_skill.system_prompt
    assert "{input_prompt}" in clarity_skill.optimization_prompt


def test_skill_manager_get_nonexistent_skill():
    """Test retrieving a non-existent skill."""
    skills_dir = Path("app/skills")
    manager = SkillManager(skills_dir)

    result = manager.get_skill("nonexistent")
    assert result is None


def test_skill_selection_prompt_generation():
    """Test that skill selection prompt is generated correctly."""
    skills_dir = Path("app/skills")
    manager = SkillManager(skills_dir)

    prompt = manager.get_skill_selection_prompt("write code")
    assert "write code" in prompt
    assert "clarity" in prompt
    assert "specificity" in prompt


def test_skill_manager_uses_lazy_loading_cache():
    """Test that skill bodies are loaded on demand and then cached."""
    skills_dir = Path("app/skills")
    manager = SkillManager(skills_dir)

    assert "clarity" in manager.metadata
    assert manager._skill_cache == {}

    first = manager.get_skill("clarity")
    second = manager.get_skill("clarity")

    assert first is second
    assert "clarity" in manager._skill_cache


@pytest.mark.asyncio
async def test_optimizer_uses_flash_model_for_skill_selection():
    class FakeLLMClient:
        def __init__(self):
            self.flash_calls = []
            self.chat_calls = []

        async def chat_flash(self, messages: list, stage: str = None, **kwargs) -> str:
            self.flash_calls.append((messages, stage, kwargs))
            return "structure"

        async def chat(self, messages: list, stage: str = None, **kwargs) -> str:
            self.chat_calls.append((messages, stage, kwargs))
            return "clarity"

    optimizer = PromptOptimizer(FakeLLMClient(), SkillManager(Path("app/skills")))

    selected_skill = await optimizer._select_skill("write a well-structured proposal")

    assert selected_skill == "structure"
    assert len(optimizer.llm.flash_calls) == 1
    assert optimizer.llm.flash_calls[0][1] == "skill_selection"
    assert optimizer.llm.chat_calls == []


@pytest.mark.asyncio
async def test_optimizer_falls_back_to_main_model_when_flash_returns_unknown_skill():
    class FakeLLMClient:
        def __init__(self):
            self.flash_calls = []
            self.chat_calls = []

        async def chat_flash(self, messages: list, stage: str = None, **kwargs) -> str:
            self.flash_calls.append((messages, stage, kwargs))
            return "unknown_skill"

        async def chat(self, messages: list, stage: str = None, **kwargs) -> str:
            self.chat_calls.append((messages, stage, kwargs))
            return "clarity"

    optimizer = PromptOptimizer(FakeLLMClient(), SkillManager(Path("app/skills")))

    selected_skill = await optimizer._select_skill("make this clearer")

    assert selected_skill == "clarity"
    assert len(optimizer.llm.flash_calls) == 1
    assert len(optimizer.llm.chat_calls) == 1
    assert optimizer.llm.chat_calls[0][1] == "skill_selection"


@pytest.mark.asyncio
async def test_optimizer_raises_error_when_no_model_returns_known_skill():
    class FakeLLMClient:
        async def chat_flash(self, messages: list, stage: str = None, **kwargs) -> str:
            return "unknown_skill"

        async def chat(self, messages: list, stage: str = None, **kwargs) -> str:
            return "still_unknown"

    optimizer = PromptOptimizer(FakeLLMClient(), SkillManager(Path("app/skills")))

    with pytest.raises(ValueError, match="Unknown skill: still_unknown"):
        await optimizer.optimize("write something")
