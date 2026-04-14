import json

from examples.tool_use.client import CLIENT
from examples.tool_use.research_tools import parse_input


def reflection_and_rewrite(
    report,
    model: str = "anthropic:claude-haiku-4-5-20251001",
    temperature: float = 0.3,
) -> dict:
    """Generate a structured reflection and a revised version of the report."""

    report = parse_input(report)

    user_prompt = f"""You are reviewing the following research report:

{report}

Provide a structured reflection covering four sections: Strengths, Limitations,
Suggestions, and Opportunities. Then produce a revised, improved version of the
report that applies your suggestions.

Return ONLY valid JSON with this exact structure and no additional commentary:
{{ "reflection": "<your reflection text covering Strengths, Limitations, Suggestions, Opportunities>", "revised_report": "<improved report text>" }}"""

    response = CLIENT.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an academic reviewer and editor."},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )

    llm_output = response.choices[0].message.content.strip()

    try:
        data = json.loads(llm_output)
    except json.JSONDecodeError as exc:
        raise ValueError("The output of the LLM was not valid JSON.") from exc

    return {
        "reflection": str(data.get("reflection", "")).strip(),
        "revised_report": str(data.get("revised_report", "")).strip(),
    }
