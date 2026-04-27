from pathlib import Path

from app.services.skill_manager import SkillManager


def test_skill_manager_only_reads_metadata_at_startup():
    """Test that startup indexing does not eagerly parse skill bodies."""
    manager = SkillManager(Path("app/skills"))

    assert manager.metadata["clarity"].name == "clarity"
    assert manager.metadata["clarity"].path.name == "SKILL.md"
    assert manager._skill_cache == {}


def test_skill_manager_parses_markdown_sections():
    """Test that required markdown sections are extracted correctly."""
    manager = SkillManager(Path("app/skills"))

    skill = manager.get_skill("mental_model")

    assert "mental model alignment expert" in skill.system_prompt
    assert skill.optimization_prompt.startswith("Original prompt: {input_prompt}")
