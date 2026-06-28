from __future__ import annotations

import unittest

from house_rules_app.engine import generate_finale, generate_round, prime_trace, readiness
from house_rules_app.storage import load_default_state
from scripts.write_demo_scenes import DEMO_CASES, build_demo_state


class BantaramaEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = load_default_state()
        self.state["players"] = ["Martin", "Newton", "Pavarotti", "Rocky"]
        self.state["game_seed"] = "test-game"

    def test_same_seed_same_round(self) -> None:
        options = {"round_number": 1, "mode": "House Rules", "weirdness": 70}
        first = generate_round(self.state, options)
        second = generate_round(self.state, options)
        self.assertEqual(first["script"], second["script"])

    def test_round_contains_required_parts(self) -> None:
        round_data = generate_round(self.state, {"round_number": 2, "mode": "Relic Trial"})
        self.assertIn("Setup:", round_data["script"])
        self.assertIn("Evidence:", round_data["script"])
        self.assertIn("Callback:", round_data["script"])
        self.assertIn("Table Action:", round_data["script"])
        self.assertIn("Vote Prompt:", round_data["script"])
        self.assertEqual(len(round_data["trace"]), 7)
        self.assertTrue(round_data["callback"])
        self.assertTrue(round_data["table_action"])

    def test_prime_trace_always_seven_steps(self) -> None:
        self.assertEqual(len(prime_trace(3, 17, 62)), 7)

    def test_readiness_blocks_without_players(self) -> None:
        state = load_default_state()
        ready = readiness(state)
        self.assertEqual(ready["checks"]["players"]["level"], "red")
        self.assertFalse(ready["can_start"])

    def test_finale_uses_scores(self) -> None:
        self.state["scores"] = {"Martin": 3, "Newton": 1}
        finale = generate_finale(self.state)
        self.assertEqual(finale["winner"], "Martin")
        self.assertIn("Final House Law", finale["script"])

    def test_demo_cases_render_valid_scripts(self) -> None:
        for case in DEMO_CASES:
            with self.subTest(case=case["slug"]):
                state = build_demo_state(case)
                round_data = generate_round(
                    state,
                    {
                        "round_number": case["round_number"],
                        "mode": case["mode"],
                        "weirdness": case["weirdness"],
                    },
                )
                script = round_data["script"]
                self.assertIn("Setup:", script)
                self.assertIn("Evidence:", script)
                self.assertIn("Escalation:", script)
                self.assertIn("Callback:", script)
                self.assertIn("Table Action:", script)
                self.assertIn("Vote Prompt:", script)
                self.assertIn("Closing Sting:", script)
                self.assertIn("WHY THIS HAPPENED", script)
                self.assertEqual(len(round_data["trace"]), 7)
                self.assertNotIn("{player}", script)
                self.assertNotIn("{relic}", script)


if __name__ == "__main__":
    unittest.main()
