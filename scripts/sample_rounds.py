from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from house_rules_app.engine import MODES, generate_round
from house_rules_app.storage import load_default_state


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic Bantarama sample rounds.")
    parser.add_argument("--count", type=int, default=5)
    args = parser.parse_args()

    state = load_default_state()
    state["players"] = ["Martin", "Newton", "Pavarotti", "Rocky"]
    state["game_seed"] = "sample-game"
    for index in range(args.count):
        sample_state = deepcopy(state)
        sample_state["history"] = [{}] * index
        mode = MODES[index % len(MODES)]
        round_data = generate_round(sample_state, {"round_number": index + 1, "mode": mode})
        print("=" * 72)
        print(round_data["script"])
        print()


if __name__ == "__main__":
    main()
