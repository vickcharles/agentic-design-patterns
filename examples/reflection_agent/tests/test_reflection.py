import unittest
from unittest.mock import patch, MagicMock

from examples.reflection_agent.drafting import generate_draft
from examples.reflection_agent.reflection import reflect_on_draft
from examples.reflection_agent.revision import revise_draft


def _mock_response(content: str) -> MagicMock:
    """Create a mock LLM response."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    return response


class TestGenerateDraft(unittest.TestCase):
    @patch("examples.reflection_agent.drafting.CLIENT")
    def test_returns_string(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("Draft essay.")
        result = generate_draft("test topic")
        self.assertIsInstance(result, str)
        self.assertEqual(result, "Draft essay.")

    @patch("examples.reflection_agent.drafting.CLIENT")
    def test_calls_correct_model(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("Draft.")
        generate_draft("test topic", model="anthropic:claude-sonnet-4-6")
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "anthropic:claude-sonnet-4-6")

    @patch("examples.reflection_agent.drafting.CLIENT")
    def test_prompt_includes_topic(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("Draft.")
        generate_draft("climate change")
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        prompt = call_kwargs["messages"][0]["content"]
        self.assertIn("climate change", prompt)


class TestReflectOnDraft(unittest.TestCase):
    @patch("examples.reflection_agent.reflection.CLIENT")
    def test_returns_string(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("Feedback here.")
        result = reflect_on_draft("Some draft text.")
        self.assertIsInstance(result, str)
        self.assertEqual(result, "Feedback here.")

    @patch("examples.reflection_agent.reflection.CLIENT")
    def test_default_model(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("Feedback.")
        reflect_on_draft("Draft text.")
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "anthropic:claude-haiku-4-5-20251001")


class TestReviseDraft(unittest.TestCase):
    @patch("examples.reflection_agent.revision.CLIENT")
    def test_returns_string(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("Revised essay.")
        result = revise_draft("Original draft.", "Some feedback.")
        self.assertIsInstance(result, str)
        self.assertEqual(result, "Revised essay.")

    @patch("examples.reflection_agent.revision.CLIENT")
    def test_prompt_includes_both_inputs(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("Revised.")
        revise_draft("My draft.", "Fix the intro.")
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        prompt = call_kwargs["messages"][0]["content"]
        self.assertIn("My draft.", prompt)
        self.assertIn("Fix the intro.", prompt)


if __name__ == "__main__":
    unittest.main()
