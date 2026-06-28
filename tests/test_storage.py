from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


class BantaramaStorageTests(unittest.TestCase):
    def test_storage_uses_override_and_exports(self) -> None:
        old_home = os.environ.get("BANTARAMA_HOME")
        with tempfile.TemporaryDirectory(dir="D:\\Temp" if Path("D:\\Temp").exists() else None) as tmp:
            tmp_root = Path(tmp).resolve()

            def assert_inside_tmp(path: str | Path) -> None:
                resolved = Path(path).resolve()
                self.assertTrue(resolved == tmp_root or tmp_root in resolved.parents, f"{resolved} is not inside {tmp_root}")

            os.environ["BANTARAMA_HOME"] = tmp
            try:
                from house_rules_app import storage

                state = storage.new_game()
                state["players"] = ["A", "B"]
                saved = storage.save_state(state)
                self.assertEqual(saved["players"], ["A", "B"])
                assert_inside_tmp(storage.user_state_path())

                round_data = {
                    "id": "round-test",
                    "title": "Tiny Round",
                    "script": "Round body",
                }
                storage.add_round(round_data)
                storage.add_round({"id": "round-new", "title": "Better", "script": "Better body"}, "round-test")
                self.assertEqual(len(storage.load_state()["history"]), 1)
                storage.award_round("round-new", "A")
                exported = storage.export_game("txt")
                self.assertTrue(Path(exported["path"]).exists())
                assert_inside_tmp(exported["path"])

                with mock.patch.object(storage, "_launch_folder", return_value=True) as launcher:
                    opened = storage.open_exports_folder()
                self.assertTrue(opened["opened"])
                assert_inside_tmp(opened["path"])
                self.assertEqual(Path(opened["path"]).name, "exports")
                launcher.assert_called_once()

                packs = storage.list_packs()
                self.assertTrue(any(pack["source"] == "built-in" for pack in packs))
                saved_pack = storage.save_pack("My Table", storage.load_state())
                self.assertEqual(saved_pack["id"], "user-my-table")
                self.assertTrue((Path(tmp) / "packs" / "my-table.json").exists())
                loaded = storage.apply_pack("user-my-table")
                self.assertEqual(loaded["history"], [])
                self.assertEqual(loaded["scores"], {"A": 0, "B": 0})
            finally:
                if old_home is None:
                    os.environ.pop("BANTARAMA_HOME", None)
                else:
                    os.environ["BANTARAMA_HOME"] = old_home


if __name__ == "__main__":
    unittest.main()
