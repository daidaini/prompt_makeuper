import argparse
import asyncio
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.llm_client import LLMClient
from app.services.optimizer import PromptOptimizer
from app.services.skill_manager import SkillManager


def load_evals(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


async def run_eval(output_path: Path, output_type: str) -> None:
    evals_path = PROJECT_ROOT / "evals" / "skills_evals.json"
    payload = load_evals(evals_path)

    optimizer = PromptOptimizer(LLMClient(), SkillManager(PROJECT_ROOT / "app" / "skills"))

    results = []
    for item in payload["evals"]:
        result = await optimizer.optimize(item["prompt"], output_type=output_type)
        results.append(
            {
                "id": item["id"],
                "prompt": item["prompt"],
                "expected_output": item["expected_output"],
                "expectations": item.get("expectations", []),
                "selected_skill": result["skill"],
                "output_prompt": result["prompt"],
                "iterations": result["iterations"],
            }
        )

    output = {
        "skill_name": payload["skill_name"],
        "output_type": output_type,
        "results": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run prompt skill evaluation samples")
    parser.add_argument(
        "--output",
        default="evals/skills_eval_results.json",
        help="Path to write JSON results",
    )
    parser.add_argument(
        "--output-type",
        choices=["markdown", "xml"],
        default="markdown",
        help="Optimizer output format to evaluate",
    )
    args = parser.parse_args()

    output_path = PROJECT_ROOT / args.output
    asyncio.run(run_eval(output_path, args.output_type))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
