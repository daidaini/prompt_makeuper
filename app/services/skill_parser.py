from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class SkillMetadata:
    name: str
    description: str
    path: Path


@dataclass(frozen=True)
class SkillDefinition:
    name: str
    description: str
    system_prompt: str
    optimization_prompt: str
    path: Path


def parse_skill_metadata(path: Path) -> SkillMetadata:
    """Parse only the frontmatter from a SKILL.md file."""
    metadata = _read_frontmatter(path)
    return SkillMetadata(
        name=metadata["name"],
        description=metadata["description"],
        path=path,
    )


def parse_skill_definition(path: Path) -> SkillDefinition:
    """Parse the full SKILL.md file into a structured skill definition."""
    metadata, body = _split_frontmatter_and_body(path)
    sections = _parse_sections(body)

    if "System Prompt" not in sections or "Optimization Prompt" not in sections:
        raise ValueError(
            f"Skill file '{path}' must contain '## System Prompt' and '## Optimization Prompt' sections"
        )

    return SkillDefinition(
        name=metadata["name"],
        description=metadata["description"],
        system_prompt=sections["System Prompt"],
        optimization_prompt=sections["Optimization Prompt"],
        path=path,
    )


def _read_frontmatter(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        first_line = handle.readline()
        if first_line.strip() != "---":
            raise ValueError(f"Skill file '{path}' must start with YAML frontmatter")

        frontmatter_lines = []
        for line in handle:
            if line.strip() == "---":
                metadata = yaml.safe_load("".join(frontmatter_lines)) or {}
                if not metadata.get("name") or not metadata.get("description"):
                    raise ValueError(
                        f"Skill file '{path}' must define 'name' and 'description' in frontmatter"
                    )
                return metadata
            frontmatter_lines.append(line)

    raise ValueError(f"Skill file '{path}' has unterminated YAML frontmatter")


def _split_frontmatter_and_body(path: Path) -> tuple[dict, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        raise ValueError(f"Skill file '{path}' must start with YAML frontmatter")

    closing_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing_index = index
            break

    if closing_index is None:
        raise ValueError(f"Skill file '{path}' has unterminated YAML frontmatter")

    metadata = _read_frontmatter(path)

    body = "\n".join(lines[closing_index + 1:]).strip()
    return metadata, body


def _parse_sections(body: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current_section = None

    for line in body.splitlines():
        if line.startswith("## "):
            current_section = line[3:].strip()
            sections[current_section] = []
            continue

        if current_section is not None:
            sections[current_section].append(line)

    return {
        name: "\n".join(lines).strip()
        for name, lines in sections.items()
    }
