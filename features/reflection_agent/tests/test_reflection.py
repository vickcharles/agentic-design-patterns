import unittest
from unittest.mock import patch, MagicMock


def _mock_response(content: str) -> MagicMock:
    """Create a mock LLM response."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    return response


class TestGenerateDraft(unittest.TestCase):
    @patch("features.reflection_agent.drafting.CLIENT")
    def test_returns_string(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("Draft essay.")
        from features.reflection_agent.drafting import generate_draft

        result = generate_draft("test topic")
        self.assertIsInstance(result, str)
        self.assertEqual(result, "Draft essay.")

    @patch("features.reflection_agent.drafting.CLIENT")
    def test_calls_model(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("Draft.")
        from features.reflection_agent.drafting import generate_draft

        generate_draft("test topic", model="openai:gpt-4o")
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "openai:gpt-4o")


class TestReflectOnDraft(unittest.TestCase):
    @patch("features.reflection_agent.reflection.CLIENT")
    def test_returns_string(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("Feedback here.")
        from features.reflection_agent.reflection import reflect_on_draft

        result = reflect_on_draft("Some draft text.")
        self.assertIsInstance(result, str)
        self.assertEqual(result, "Feedback here.")


class TestReviseDraft(unittest.TestCase):
    @patch("features.reflection_agent.revision.CLIENT")
    def test_returns_string(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("Revised essay.")
        from features.reflection_agent.revision import revise_draft

        result = revise_draft("Original draft.", "Some feedback.")
        self.assertIsInstance(result, str)
        self.assertEqual(result, "Revised essay.")

    @patch("features.reflection_agent.revision.CLIENT")
    def test_prompt_includes_both_inputs(self, mock_client):
        mock_client.chat.completions.create.return_value = _mock_response("Revised.")
        from features.reflection_agent.revision import revise_draft

        revise_draft("My draft.", "Fix the intro.")
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        prompt = call_kwargs["messages"][0]["content"]
        self.assertIn("My draft.", prompt)
        self.assertIn("Fix the intro.", prompt)


if __name__ == "__main__":
    unittest.main()
