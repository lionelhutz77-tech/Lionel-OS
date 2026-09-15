import unittest

from scripts.audit_release import main


class ReleaseHygieneTests(unittest.TestCase):
    def test_public_tree_has_no_known_secret_or_personal_artifacts(self) -> None:
        self.assertEqual(main(), 0)


if __name__ == "__main__":
    unittest.main()
