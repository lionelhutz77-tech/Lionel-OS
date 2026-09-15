import unittest

from lionelos.config import ProviderConfig, build_providers


class ProviderConfigTests(unittest.TestCase):
    def test_general_config_builds_multiple_provider_kinds(self) -> None:
        providers = build_providers(
            {
                "offline": {"kind": "static", "response": {"verdict": "approve", "summary": "ok", "findings": []}},
                "openai": {"kind": "openai_responses", "model": "configured-at-runtime"},
                "codex": {"kind": "codex_cli"},
            }
        )
        self.assertEqual(set(providers), {"offline", "openai", "codex"})

    def test_unknown_fields_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown provider fields"):
            ProviderConfig.from_dict("bad", {"kind": "codex_cli", "secret": "must-not-be-here"})


if __name__ == "__main__":
    unittest.main()
