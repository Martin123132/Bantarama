from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from house_rules_app.engine import generate_round
from house_rules_app.storage import load_default_state


DEMO_CASES = [
    {"slug": "01-house-rules-mug-law", "seed": "demo-mug-law", "mode": "House Rules", "weirdness": 58, "round_number": 1, "cast_size": 4},
    {"slug": "02-cult-laminated-prophecy", "seed": "demo-laminated-cult", "mode": "Cult Night", "weirdness": 73, "round_number": 2, "cast_size": 4},
    {"slug": "03-five-a-side-bib-var", "seed": "demo-bib-var", "mode": "Five-a-Side Incident", "weirdness": 65, "round_number": 3, "cast_size": 4},
    {"slug": "04-relic-trial-spoon", "seed": "demo-spoon-trial", "mode": "Relic Trial", "weirdness": 51, "round_number": 4, "cast_size": 4},
    {"slug": "05-under-stairs-breakthrough", "seed": "demo-stairs-breakthrough", "mode": "Under The Stairs", "weirdness": 69, "round_number": 5, "cast_size": 4},
    {"slug": "06-chaos-council-remote", "seed": "demo-remote-council", "mode": "Chaos Council", "weirdness": 62, "round_number": 6, "cast_size": 4},
    {"slug": "07-house-rules-cupboard", "seed": "demo-cupboard-law", "mode": "House Rules", "weirdness": 82, "round_number": 7, "cast_size": 5},
    {"slug": "08-cult-biscuit-schism", "seed": "demo-biscuit-schism", "mode": "Cult Night", "weirdness": 88, "round_number": 8, "cast_size": 5},
    {"slug": "09-relic-trial-chair", "seed": "demo-chair-trial", "mode": "Relic Trial", "weirdness": 77, "round_number": 9, "cast_size": 5},
    {"slug": "10-chaos-council-kettle", "seed": "demo-kettle-council", "mode": "Chaos Council", "weirdness": 91, "round_number": 10, "cast_size": 5},
]

DEMO_PLAYERS = ["Martin", "Newton", "Pavarotti", "Rocky", "Ada"]


def build_demo_state(case: dict[str, object]) -> dict:
    state = deepcopy(load_default_state())
    cast_size = int(case.get("cast_size") or 4)
    state["players"] = DEMO_PLAYERS[:cast_size]
    state["scores"] = {name: 0 for name in state["players"]}
    state["game_seed"] = str(case["seed"])
    state["settings"] = {
        "round_count": 10,
        "tone": str(case["mode"]),
        "weirdness": int(case["weirdness"]),
    }
    state["history"] = _fake_history(int(case["round_number"]) - 1)
    return state


def render_demo(case: dict[str, object]) -> str:
    state = build_demo_state(case)
    round_data = generate_round(
        state,
        {
            "round_number": int(case["round_number"]),
            "mode": str(case["mode"]),
            "weirdness": int(case["weirdness"]),
        },
    )
    cast = ", ".join(state["players"])
    return "\n".join(
        [
            f"# {round_data['title']}",
            "",
            f"- Seed: `{case['seed']}`",
            f"- Mode: `{case['mode']}`",
            f"- Weirdness: `{case['weirdness']}`",
            f"- Cast size: `{case['cast_size']}`",
            f"- Cast: {cast}",
            "",
            "```text",
            round_data["script"],
            "```",
            "",
        ]
    )


def write_demo_scenes(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    index_lines = ["# Bantarama Demo Scenes", "", "Reproducible fixed-seed comedy samples for tuning.", ""]
    for case in DEMO_CASES:
        path = out_dir / f"{case['slug']}.md"
        path.write_text(render_demo(case), encoding="utf-8")
        written.append(path)
        index_lines.append(f"- [{case['slug']}]({path.name})")
    index_path = out_dir / "README.md"
    index_path.write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    written.append(index_path)
    return written


def _fake_history(count: int) -> list[dict]:
    titles = [
        "The Rule About The Remote of Final Authority",
        "The Small Cult of nobody check the cupboard",
        "Rocky's Goal With A Damp Five-a-Side Bib",
    ]
    return [{"round": {"title": titles[index % len(titles)]}, "winner": None} for index in range(max(0, count))]


def main() -> None:
    parser = argparse.ArgumentParser(description="Write fixed-seed Bantarama demo scenes.")
    parser.add_argument("--out", default="docs/demo-scenes")
    args = parser.parse_args()
    for path in write_demo_scenes(Path(args.out)):
        print(path)


if __name__ == "__main__":
    main()
