from datetime import datetime

from examples.multi_agent import tools as team_tools
from examples.multi_agent import utils
from examples.multi_agent.client import CLIENT


MARKET_RESEARCH_PROMPT = """You are a fashion market research agent preparing a trend
analysis for a summer sunglasses campaign.

Goal:
1. Explore current fashion trends related to sunglasses using web search.
2. Review the internal product catalog to identify items that align with those trends.
3. Recommend one or more products from the catalog that best match emerging trends.

You can call these tools:
- tavily_search_tool: discover external web trends.
- product_catalog_tool: inspect the internal sunglasses catalog.

Today is {today}.

Return a short brief with:
- The top 2-3 trends you found.
- The matching product(s) from the catalog.
- A justification for the summer campaign fit."""


def market_research_agent(
    model: str = "anthropic:claude-sonnet-4-6",
    max_turns: int = 8,
) -> str:
    """Run the market research agent and return its trend brief."""

    utils.log_agent_title("Market Research Agent", "[MR]")

    prompt = MARKET_RESEARCH_PROMPT.format(today=datetime.now().strftime("%Y-%m-%d"))
    messages = [{"role": "user", "content": prompt}]
    available = team_tools.get_available_tools()

    for _ in range(max_turns):
        response = CLIENT.chat.completions.create(
            model=model,
            messages=messages,
            tools=available,
            tool_choice="auto",
        )
        msg = response.choices[0].message
        messages.append(msg)

        if not getattr(msg, "tool_calls", None):
            content = msg.content or ""
            utils.log_final_summary(content)
            return content

        for call in msg.tool_calls:
            utils.log_tool_call(call.function.name, call.function.arguments)
            result = team_tools.handle_tool_call(call)
            utils.log_tool_result(result)
            messages.append(team_tools.create_tool_response_message(call, result))

    return ""
