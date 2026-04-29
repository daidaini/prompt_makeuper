import json
from pathlib import Path

from scripts import eval_skills


def test_skill_evals_cover_all_skills():
    evals_path = Path("evals/skills_evals.json")
    payload = json.loads(evals_path.read_text(encoding="utf-8"))

    assert payload["skill_name"] == "prompt-makeuper-skills"
    assert len(payload["evals"]) >= 10

    prompts = [item["prompt"] for item in payload["evals"]]
    assert any("更清楚" in prompt or "clarity" in prompt for prompt in prompts)
    assert any("补完整" in prompt or "success criteria" in prompt for prompt in prompts)
    assert any("结构化" in prompt or "sections" in prompt for prompt in prompts)
    assert any("例子" in prompt or "examples" in prompt for prompt in prompts)
    assert any("限制" in prompt or "不超过" in prompt for prompt in prompts)
    assert any("假设" in prompt or "成功标准" in prompt for prompt in prompts)
    assert any("分阶段" in prompt or "阶段" in prompt for prompt in prompts)
    assert any("自检" in prompt or "验证" in prompt for prompt in prompts)


def test_skill_evals_have_expectations_for_each_case():
    evals_path = Path("evals/skills_evals.json")
    payload = json.loads(evals_path.read_text(encoding="utf-8"))

    for item in payload["evals"]:
        assert item["expected_output"]
        assert isinstance(item["expectations"], list)
        assert len(item["expectations"]) >= 2


def test_select_evals_filters_by_ids_in_requested_order():
    evals = [
        {"id": 1, "prompt": "one"},
        {"id": 2, "prompt": "two"},
        {"id": 3, "prompt": "three"},
    ]

    selected = eval_skills.select_evals(evals, ids=[3, 1], limit=None)

    assert [item["id"] for item in selected] == [3, 1]


def test_select_evals_applies_limit_after_filtering():
    evals = [
        {"id": 1, "prompt": "one"},
        {"id": 2, "prompt": "two"},
        {"id": 3, "prompt": "three"},
    ]

    selected = eval_skills.select_evals(evals, ids=[2, 3, 1], limit=2)

    assert [item["id"] for item in selected] == [2, 3]


def test_parse_ids_handles_commas_and_whitespace():
    assert eval_skills.parse_ids(" 7, 2,10 ") == [7, 2, 10]
