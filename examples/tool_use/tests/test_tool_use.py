import json
import unittest
from unittest.mock import MagicMock, patch

from examples.tool_use.html_conversion import convert_report_to_html
from examples.tool_use.reflection import reflection_and_rewrite
from examples.tool_use.report import generate_research_report_with_tools


def _mock_response(content: str, tool_calls=None) -> MagicMock:
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    response.choices[0].message.tool_calls = tool_calls
    return response


class TestGenerateResearchReport(unittest.TestCase):
    @patch("examples.tool_use.report.CLIENT")
    def test_returns_final_text_without_tool_calls(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("Final report.")
        result = generate_research_report_with_tools("test topic")
        self.assertEqual(result, "Final report.")

    @patch("examples.tool_use.report.CLIENT")
    def test_executes_tool_calls_then_finishes(self, mock_client):
        tool_call = MagicMock()
        tool_call.id = "call_1"
        tool_call.function.name = "arxiv_search_tool"
        tool_call.function.arguments = json.dumps({"query": "test", "max_results": 1})

        mock_client.chat.completions.create.side_effect = [
            _mock_response(None, tool_calls=[tool_call]),
            _mock_response("Done."),
        ]

        with patch(
            "examples.tool_use.report.TOOL_MAPPING",
            {"arxiv_search_tool": lambda **kw: [{"title": "mocked"}]},
        ):
            result = generate_research_report_with_tools("topic")

        self.assertEqual(result, "Done.")
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)

    @patch("examples.tool_use.report.CLIENT")
    def test_passes_tool_choice_auto(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("x")
        generate_research_report_with_tools("topic")
        kwargs = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(kwargs["tool_choice"], "auto")


class TestReflectionAndRewrite(unittest.TestCase):
    @patch("examples.tool_use.reflection.CLIENT")
    def test_parses_json_output(self, mock_client):
        payload = json.dumps(
            {
                "reflection": "Strengths, Limitations, Suggestions, Opportunities covered.",
                "revised_report": "Improved report.",
            }
        )
        mock_client.chat.completions.create.return_value = _mock_response(payload)
        result = reflection_and_rewrite("Some report.")
        self.assertEqual(result["reflection"], "Strengths, Limitations, Suggestions, Opportunities covered.")
        self.assertEqual(result["revised_report"], "Improved report.")

    @patch("examples.tool_use.reflection.CLIENT")
    def test_raises_on_invalid_json(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("not json")
        with self.assertRaises(ValueError):
            reflection_and_rewrite("Some report.")


class TestConvertReportToHtml(unittest.TestCase):
    @patch("examples.tool_use.html_conversion.CLIENT")
    def test_returns_html_string(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response(
            "<html><body><h1>Title</h1></body></html>"
        )
        result = convert_report_to_html("Some report.")
        self.assertIn("<html>", result)

    @patch("examples.tool_use.html_conversion.CLIENT")
    def test_prompt_includes_report(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("<html></html>")
        convert_report_to_html("unique-report-body-xyz")
        kwargs = mock_client.chat.completions.create.call_args[1]
        user_msg = kwargs["messages"][1]["content"]
        self.assertIn("unique-report-body-xyz", user_msg)


if __name__ == "__main__":
    unittest.main()
