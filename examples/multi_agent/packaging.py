from datetime import datetime

from examples.multi_agent import utils
from examples.multi_agent.client import CLIENT


def packaging_agent(
    trend_summary: str,
    image_path: str,
    quote: str,
    justification: str,
    output_path: str = "campaign_summary.md",
    model: str = "anthropic:claude-sonnet-4-6",
) -> str:
    """Assemble the campaign assets into an executive-ready Markdown report."""

    utils.log_agent_title("Packaging Agent", "[PK]")

    response = CLIENT.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a marketing communication expert writing elegant "
                    "campaign summaries for executives."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Rewrite the following trend summary to be clear, professional, "
                    f"and engaging for a CEO audience:\n\n\"\"\"{trend_summary.strip()}\"\"\""
                ),
            },
        ],
    )
    beautified = response.choices[0].message.content.strip()

    image_block = (
        f"![Campaign visual]({image_path})" if image_path else "_Image not generated._"
    )

    markdown = (
        "# Summer Sunglasses Campaign - Executive Summary\n\n"
        "## Refined Trend Insights\n"
        f"{beautified}\n\n"
        "## Campaign Visual\n"
        f"{image_block}\n\n"
        "## Campaign Quote\n"
        f"{quote.strip()}\n\n"
        "## Why This Works\n"
        f"{justification.strip()}\n\n"
        "---\n"
        f"*Report generated on {datetime.now().strftime('%Y-%m-%d')}*\n"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    return output_path
