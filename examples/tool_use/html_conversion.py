from examples.tool_use.client import CLIENT
from examples.tool_use.research_tools import parse_input


def convert_report_to_html(
    report,
    model: str = "anthropic:claude-sonnet-4-6",
    temperature: float = 0.5,
) -> str:
    """Convert a plaintext research report into a styled HTML document."""

    report = parse_input(report)

    system_prompt = "You convert plaintext reports into full clean HTML documents."
    user_prompt = f"""Convert the following research report into a full, clean, styled HTML document.
Use semantic section headers, formatted paragraphs, and clickable links. Preserve the
citation style from the source. Return ONLY valid HTML with no additional text or markdown.

{report}"""

    response = CLIENT.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )

    return response.choices[0].message.content.strip()
