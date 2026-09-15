import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from lionelos.cli import main


class CliTests(unittest.TestCase):
    def test_demo_is_complete_and_offline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()) as stdout:
            output = Path(temporary) / "demo.json"
            self.assertEqual(main(["demo", "--output", str(output)]), 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["decision"], "accepted")
            self.assertEqual(payload["approvals"], 2)
            self.assertTrue(payload["divergence"])
            self.assertIn("accepted", stdout.getvalue())

    def test_status_is_local_and_lists_provider_kinds(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(main(["status"]), 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["version"], "0.1.0")
            self.assertIn("codex_cli", payload["provider_kinds"])

    def test_verify_detects_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
            output = Path(temporary) / "demo.json"
            self.assertEqual(main(["demo", "--output", str(output)]), 0)
            self.assertEqual(main(["verify", str(output)]), 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            payload["approvals"] = 99
            output.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(main(["verify", str(output)]), 3)


if __name__ == "__main__":
    unittest.main()
