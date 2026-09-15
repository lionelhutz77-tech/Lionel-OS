import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from lionelos.models import AgentSpec, TaskSpec
from lionelos.providers import CodexCliProvider, CommandProvider, CommandProviderConfig, OpenAIResponsesConfig, OpenAIResponsesProvider, ProviderError


class ProviderTests(unittest.TestCase):
    def test_command_provider_uses_no_shell_and_stdin(self) -> None:
        config = CommandProviderConfig("local", ("example", "--json"))
        completed = type("Completed", (), {"returncode": 0, "stdout": json.dumps({"verdict": "approve", "summary": "ok", "findings": []}), "stderr": ""})()
        with patch("lionelos.providers.subprocess.run", return_value=completed) as run:
            result = CommandProvider(config).run(AgentSpec("a", "reviewer", "local"), TaskSpec("T", "Review"))
        self.assertEqual(result.verdict, "approve")
        self.assertFalse(run.call_args.kwargs["shell"])
        self.assertIn("Review", run.call_args.kwargs["input"])

    def test_openai_provider_requires_environment_secret(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            provider = OpenAIResponsesProvider(OpenAIResponsesConfig(model="example-model"))
            with self.assertRaisesRegex(ProviderError, "missing environment variable"):
                provider.run(AgentSpec("a", "reviewer", "openai"), TaskSpec("T", "Review"))

    def test_openai_provider_is_stateless_bounded_and_structured(self) -> None:
        envelope = {"output": [{"content": [{"text": json.dumps({"verdict": "approve", "summary": "ok", "findings": []})}]}]}

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self, amount=None):
                del amount
                return json.dumps(envelope).encode("utf-8")

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-only-secret"}, clear=True), patch(
            "lionelos.providers.urllib.request.urlopen", return_value=Response()
        ) as urlopen:
            result = OpenAIResponsesProvider(OpenAIResponsesConfig(model="configured-model")).run(
                AgentSpec("a", "reviewer", "openai"), TaskSpec("T", "Review")
            )
        request = urlopen.call_args.args[0]
        body = json.loads(request.data)
        self.assertEqual(result.verdict, "approve")
        self.assertFalse(body["store"])
        self.assertEqual(body["max_output_tokens"], 1200)
        self.assertEqual(body["text"]["format"]["type"], "json_schema")

    def test_openai_provider_rejects_oversized_http_response(self) -> None:
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self, amount=None):
                return b"x" * int(amount)

        config = OpenAIResponsesConfig(model="configured-model", max_response_bytes=32)
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-only-secret"}, clear=True), patch(
            "lionelos.providers.urllib.request.urlopen", return_value=Response()
        ):
            with self.assertRaisesRegex(ProviderError, "response exceeds configured byte limit"):
                OpenAIResponsesProvider(config).run(
                    AgentSpec("a", "reviewer", "openai"), TaskSpec("T", "Review")
                )

    def test_codex_cli_is_ephemeral_read_only_and_isolated(self) -> None:
        captured = {}

        def complete(argv, **kwargs):
            captured["argv"] = argv
            captured["kwargs"] = kwargs
            output_path = Path(argv[argv.index("--output-last-message") + 1])
            output_path.write_text(json.dumps({"verdict": "approve", "summary": "ok", "findings": []}), encoding="utf-8")
            return type("Completed", (), {"returncode": 0, "stderr": ""})()

        with patch("lionelos.providers.subprocess.run", side_effect=complete):
            result = CodexCliProvider(executable="codex-test").run(
                AgentSpec("a", "reviewer", "codex"), TaskSpec("T", "Review")
            )
        self.assertEqual(result.verdict, "approve")
        self.assertIn("--ephemeral", captured["argv"])
        self.assertEqual(captured["argv"][captured["argv"].index("--sandbox") + 1], "read-only")
        self.assertFalse(captured["kwargs"]["shell"])


if __name__ == "__main__":
    unittest.main()
