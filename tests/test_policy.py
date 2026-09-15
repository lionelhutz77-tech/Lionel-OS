import unittest

from lionelos.policy import AllowedChangeScope, ChangeProposal, evaluate_change_scope

ZERO = "0" * 64
ONE = "1" * 64


class ChangePolicyTests(unittest.TestCase):
    def test_exact_bounded_proposal_is_authorized(self) -> None:
        proposal = ChangeProposal("src/lionelos/cli.py", ZERO, ONE, "Add a verified command")
        decision = evaluate_change_scope((proposal,), AllowedChangeScope(("src/lionelos/*.py",)))
        self.assertTrue(decision.authorized)
        self.assertEqual(len(decision.proposal_sha256), 64)

    def test_traversal_and_out_of_scope_fail_closed(self) -> None:
        proposals = (
            ChangeProposal("../secret.txt", ZERO, ONE, "Read secret"),
            ChangeProposal("README.md", ZERO, ONE, "Unapproved file"),
        )
        decision = evaluate_change_scope(proposals, AllowedChangeScope(("src/lionelos/*.py",)))
        self.assertFalse(decision.authorized)
        self.assertIn("UNSAFE_PATH:../secret.txt", decision.reasons)
        self.assertIn("OUT_OF_SCOPE:README.md", decision.reasons)


if __name__ == "__main__":
    unittest.main()
