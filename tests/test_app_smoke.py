from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import unittest
from urllib import request


class BantaramaAppSmokeTests(unittest.TestCase):
    def test_server_doctor_and_round(self) -> None:
        with tempfile.TemporaryDirectory(dir="D:\\Temp" if Path("D:\\Temp").exists() else None) as tmp:
            env = os.environ.copy()
            env["BANTARAMA_HOME"] = tmp
            env["BANTARAMA_DISABLE_OPEN"] = "1"
            proc = subprocess.Popen(
                [sys.executable, "-m", "house_rules_app.app", "--no-open", "--port", "0"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
            )
            try:
                url = self._read_url(proc)
                doctor = self._json(url + "/api/doctor")
                self.assertTrue(doctor["ok"])
                self.assertTrue(doctor["doctor"]["state_ok"])

                state = self._json(url + "/api/state")["state"]
                state["players"] = ["A", "B", "C"]
                saved = self._post_json(url + "/api/state", {"state": state})
                self.assertTrue(saved["readiness"]["can_start"])

                round_data = self._post_json(url + "/api/round", {"round_number": 1, "mode": "House Rules"})
                self.assertTrue(round_data["ok"])
                self.assertIn("script", round_data["round"])
                self.assertIn("WHY THIS HAPPENED", round_data["round"]["script"])
                awarded = self._post_json(url + "/api/award", {"round_id": round_data["round"]["id"], "winner": "The House"})
                self.assertEqual(awarded["state"]["scores"]["The House"], 1)
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                if proc.stdout:
                    proc.stdout.close()

    def _read_url(self, proc: subprocess.Popen[str]) -> str:
        assert proc.stdout is not None
        deadline = time.time() + 8
        while time.time() < deadline:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            match = re.search(r"http://127\.0\.0\.1:\d+", line)
            if match:
                return match.group(0)
        self.fail("Server did not print a local URL")

    def _json(self, url: str) -> dict:
        with request.urlopen(url, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def _post_json(self, url: str, payload: dict) -> dict:
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(url, data=data, headers={"content-type": "application/json"}, method="POST")
        with request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
