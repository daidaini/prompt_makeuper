from typing import List, Dict, Optional
from pathlib import Path

from app.services.skill_parser import (
    SkillDefinition,
    SkillMetadata,
    parse_skill_definition,
    parse_skill_metadata,
)


class SkillManager:
    """Manages loading and selection of optimization skills."""

    def __init__(self, skills_dir: Path):
        """
        Initialize the skill manager.

        Args:
            skills_dir: Path to directory containing per-skill SKILL.md files
        """
        self.skills_dir = skills_dir
        self.metadata = self._scan_skills()
        self._skill_cache: Dict[str, SkillDefinition] = {}

    def _scan_skills(self) -> Dict[str, SkillMetadata]:
        """Index available skills by parsing only SKILL.md frontmatter."""
        skills: Dict[str, SkillMetadata] = {}
        for skill_file in sorted(self.skills_dir.glob("*/SKILL.md")):
            metadata = parse_skill_metadata(skill_file)
            skills[metadata.name] = metadata
        return skills

    def get_skill(self, name: str) -> Optional[SkillDefinition]:
        """
        Get a specific skill by name.

        Args:
            name: The skill name to retrieve

        Returns:
            Parsed skill definition or None if not found
        """
        metadata = self.metadata.get(name)
        if metadata is None:
            return None

        if name not in self._skill_cache:
            self._skill_cache[name] = parse_skill_definition(metadata.path)

        return self._skill_cache[name]

    def list_skills(self) -> List[str]:
        """
        List all available skill names.

        Returns:
            List of skill names
        """
        return list(self.metadata.keys())

    def get_skill_selection_prompt(self, user_prompt: str) -> str:
        """
        Generate prompt for LLM to select appropriate skill.

        Args:
            user_prompt: The user's input prompt to analyze

        Returns:
            A prompt string for skill selection
        """
        skill_descriptions = "\n".join(
            f"- {name}: {skill.description}"
            for name, skill in self.metadata.items()
        )
        return f"""Analyze the user's prompt and select the most appropriate optimization skill from:

{skill_descriptions}

Respond with ONLY the skill name (e.g., "clarity", "specificity", "structure", "examples", "constraints").
If multiple skills are equally applicable, choose the most critical one.

User prompt: {user_prompt}

Selected skill:"""
