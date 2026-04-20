import json
from datetime import datetime

from examples.tool_use.client import CLIENT
from examples.tool_use.research_tools import (
    TOOL_MAPPING,
    arxiv_tool_def,
    tavily_tool_def,
)


def find_references(
    task: str,
    model: str = "anthropic:claude-sonnet-4-6",
    max_turns: int = 5,
) -> str:
    """Run the research step: gather references via arXiv and Tavily."""

    prompt = f"""You are a research function with access to:
- arxiv_search_tool: academic papers
- tavily_search_tool: general web search

Task:
{task}

Today is {datetime.now().strftime('%Y-%m-%d')}.
Include full URLs for every source you reference."""

    messages = [{"role": "user", "content": prompt}]
    tools = [arxiv_tool_def, tavily_tool_def]
    final_text = ""

    for _ in range(max_turns):
        response = CLIENT.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=1,
        )

        msg = response.choices[0].message
        messages.append(msg)

        if not getattr(msg, "tool_calls", None):
            final_text = msg.content or ""
            break

        for call in msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            try:
                result = TOOL_MAPPING[name](**args)
            except Exception as exc:
                result = {"error": str(exc)}
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": name,
                    "content": json.dumps(result),
                }
            )

    return final_text
