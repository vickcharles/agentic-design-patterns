import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from examples.multi_agent import tools as team_tools
from examples.multi_agent.copywriter import copywriter_agent
from examples.multi_agent.graphic_designer import graphic_designer_agent
from examples.multi_agent.market_research import market_research_agent
from examples.multi_agent.packaging import packaging_agent
from examples.multi_agent.pipeline import run_sunglasses_campaign_pipeline


def _mock_response(content, tool_calls=None):
    r = MagicMock()
    r.choices = [MagicMock()]
    r.choices[0].message.content = content
    r.choices[0].message.tool_calls = tool_calls
    return r


class TestTools(unittest.TestCase):
    def test_product_catalog_returns_list(self):
        catalog = team_tools.product_catalog_tool()
        self.assertIsInstance(catalog, list)
        self.assertGreater(len(catalog), 0)
        self.assertIn("id", catalog[0])

    def test_get_available_tools_has_expected_names(self):
        names = {t["function"]["name"] for t in team_tools.get_available_tools()}
        self.assertIn("tavily_search_tool", names)
        self.assertIn("product_catalog_tool", names)

    def test_handle_tool_call_unknown_tool(self):
        call = MagicMock()
        call.function.name = "mystery_tool"
        call.function.arguments = "{}"
        result = team_tools.handle_tool_call(call)
        self.assertIn("error", result)

    def test_create_tool_response_message_shape(self):
        call = MagicMock()
        call.id = "abc"
        call.function.name = "product_catalog_tool"
        msg = team_tools.create_tool_response_message(call, [{"a": 1}])
        self.assertEqual(msg["role"], "tool")
        self.assertEqual(msg["tool_call_id"], "abc")
        self.assertIn("a", msg["content"])


class TestMarketResearchAgent(unittest.TestCase):
    @patch("examples.multi_agent.market_research.CLIENT")
    def test_returns_content_without_tool_calls(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("brief")
        result = market_research_agent()
        self.assertEqual(result, "brief")

    @patch("examples.multi_agent.market_research.CLIENT")
    def test_runs_tool_calls_then_finishes(self, mock_client):
        call = MagicMock()
        call.id = "t1"
        call.function.name = "product_catalog_tool"
        call.function.arguments = "{}"
        mock_client.chat.completions.create.side_effect = [
            _mock_response(None, tool_calls=[call]),
            _mock_response("final brief"),
        ]
        result = market_research_agent()
        self.assertEqual(result, "final brief")


class TestGraphicDesignerAgent(unittest.TestCase):
    @patch("examples.multi_agent.graphic_designer.generate_image_with_openai", return_value="")
    @patch("examples.multi_agent.graphic_designer.CLIENT")
    def test_parses_prompt_and_caption(self, mock_client, _img):
        mock_client.chat.completions.create.return_value = _mock_response(
            json.dumps({"prompt": "sunny", "caption": "bright!"})
        )
        out = graphic_designer_agent("trends")
        self.assertEqual(out["prompt"], "sunny")
        self.assertEqual(out["caption"], "bright!")
        self.assertEqual(out["image_path"], "")

    @patch("examples.multi_agent.graphic_designer.generate_image_with_openai", return_value="")
    @patch("examples.multi_agent.graphic_designer.CLIENT")
    def test_handles_non_json_gracefully(self, mock_client, _img):
        mock_client.chat.completions.create.return_value = _mock_response("not json")
        out = graphic_designer_agent("trends")
        self.assertEqual(out["caption"], "")
        self.assertEqual(out["image_path"], "")


class TestCopywriterAgent(unittest.TestCase):
    @patch("examples.multi_agent.copywriter.CLIENT")
    def test_text_only_when_no_image(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response(
            '{"quote": "Summer is here.", "justification": "fits the vibe"}'
        )
        out = copywriter_agent(image_path="", trend_summary="trend")
        self.assertEqual(out["quote"], "Summer is here.")
        kwargs = mock_client.chat.completions.create.call_args[1]
        user_msg = kwargs["messages"][1]["content"]
        self.assertEqual(len(user_msg), 1)
        self.assertEqual(user_msg[0]["type"], "text")

    @patch("examples.multi_agent.copywriter.CLIENT")
    def test_returns_image_path_in_result(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response(
            '{"quote": "q", "justification": "j"}'
        )
        out = copywriter_agent(image_path="", trend_summary="trend")
        self.assertIn("image_path", out)


class TestPackagingAgent(unittest.TestCase):
    @patch("examples.multi_agent.packaging.CLIENT")
    def test_writes_markdown_file(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("refined")
        with tempfile.TemporaryDirectory() as td:
            out_path = os.path.join(td, "out.md")
            result = packaging_agent(
                trend_summary="ts",
                image_path="",
                quote="Q",
                justification="J",
                output_path=out_path,
            )
            self.assertTrue(os.path.exists(result))
            with open(result, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("Refined Trend Insights", content)
            self.assertIn("refined", content)
            self.assertIn("Q", content)
            self.assertIn("J", content)


class TestPipeline(unittest.TestCase):
    @patch("examples.multi_agent.pipeline.packaging_agent")
    @patch("examples.multi_agent.pipeline.copywriter_agent")
    @patch("examples.multi_agent.pipeline.graphic_designer_agent")
    @patch("examples.multi_agent.pipeline.market_research_agent")
    def test_runs_full_pipeline(self, m_market, m_design, m_copy, m_pack):
        m_market.return_value = "trend"
        m_design.return_value = {"image_path": "", "prompt": "p", "caption": "c"}
        m_copy.return_value = {"quote": "q", "justification": "j"}
        m_pack.return_value = "out.md"

        result = run_sunglasses_campaign_pipeline(output_path="out.md")

        self.assertEqual(result["trend_summary"], "trend")
        self.assertEqual(result["markdown_path"], "out.md")
        m_pack.assert_called_once()


if __name__ == "__main__":
    unittest.main()
