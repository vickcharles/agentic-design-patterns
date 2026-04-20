from datetime import datetime

from examples.multi_agent.copywriter import copywriter_agent
from examples.multi_agent.graphic_designer import graphic_designer_agent
from examples.multi_agent.market_research import market_research_agent
from examples.multi_agent.packaging import packaging_agent


def run_sunglasses_campaign_pipeline(output_path: str | None = None) -> dict:
    """Run the full summer sunglasses campaign pipeline end to end."""

    trend_summary = market_research_agent()
    visual = graphic_designer_agent(trend_insights=trend_summary)
    quote = copywriter_agent(
        image_path=visual["image_path"],
        trend_summary=trend_summary,
    )

    md_path = output_path or (
        f"campaign_summary_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"
    )
    markdown_path = packaging_agent(
        trend_summary=trend_summary,
        image_path=visual["image_path"],
        quote=quote.get("quote", ""),
        justification=quote.get("justification", ""),
        output_path=md_path,
    )

    return {
        "trend_summary": trend_summary,
        "visual": visual,
        "quote": quote,
        "markdown_path": markdown_path,
    }
