import json
import unittest
from unittest.mock import MagicMock, patch

from examples.component_level_eval.evaluator import (
    TOP_DOMAINS,
    evaluate_preferred_domains,
)
from examples.component_level_eval.find_references import find_references


def _mock_response(content, tool_calls=None):
    r = MagicMock()
    r.choices = [MagicMock()]
    r.choices[0].message.content = content
    r.choices[0].message.tool_calls = tool_calls
    return r


class TestEvaluatePreferredDomains(unittest.TestCase):
    def test_flags_no_urls(self):
        result = evaluate_preferred_domains("No URLs here.")
        self.assertFalse(result["passed"])
        self.assertEqual(result["total"], 0)
        self.assertIn("No URLs detected", result["report"])

    def test_all_preferred(self):
        text = "See https://arxiv.org/abs/1234 and https://nature.com/article"
        result = evaluate_preferred_domains(text, min_ratio=0.5)
        self.assertTrue(result["passed"])
        self.assertEqual(result["preferred"], 2)
        self.assertEqual(result["total"], 2)

    def test_below_threshold_fails(self):
        text = "See https://example.com/x and https://random.io/y"
        result = evaluate_preferred_domains(text, min_ratio=0.4)
        self.assertFalse(result["passed"])
        self.assertEqual(result["preferred"], 0)

    def test_mixed_ratio(self):
        text = "https://arxiv.org/a https://example.com/b"
        result = evaluate_preferred_domains(text)
        self.assertAlmostEqual(result["ratio"], 0.5)

    def test_report_contains_status(self):
        result = evaluate_preferred_domains("https://arxiv.org/a", min_ratio=0.5)
        self.assertIn("PASS", result["report"])

    def test_default_domain_set_includes_known(self):
        self.assertIn("arxiv.org", TOP_DOMAINS)
        self.assertIn("nature.com", TOP_DOMAINS)


class TestFindReferences(unittest.TestCase):
    @patch("examples.component_level_eval.find_references.CLIENT")
    def test_returns_final_text_without_tool_calls(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("Refs.")
        result = find_references("task")
        self.assertEqual(result, "Refs.")

    @patch("examples.component_level_eval.find_references.CLIENT")
    def test_executes_tool_calls_then_finishes(self, mock_client):
        call = MagicMock()
        call.id = "c1"
        call.function.name = "arxiv_search_tool"
        call.function.arguments = json.dumps({"query": "x"})

        mock_client.chat.completions.create.side_effect = [
            _mock_response(None, tool_calls=[call]),
            _mock_response("Done."),
        ]

        with patch(
            "examples.component_level_eval.find_references.TOOL_MAPPING",
            {"arxiv_search_tool": lambda **kw: []},
        ):
            result = find_references("task")

        self.assertEqual(result, "Done.")
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)


if __name__ == "__main__":
    unittest.main()
