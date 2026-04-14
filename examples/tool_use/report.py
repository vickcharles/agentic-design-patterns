import json

from examples.tool_use.client import CLIENT
from examples.tool_use.research_tools import (
    TOOL_MAPPING,
    arxiv_tool_def,
    tavily_tool_def,
)


SYSTEM_PROMPT = (
    "You are a research assistant that can search the web and arXiv to write detailed, "
    "accurate, and properly sourced research reports.\n\n"
    "Use tools when appropriate (e.g., to find scientific papers or web content).\n"
    "Cite sources whenever relevant. Do NOT omit citations for brevity.\n"
    "When possible, include full URLs (arXiv links, web sources, etc.).\n"
    "Use an academic tone, organize output into clearly labeled sections, and include "
    "inline citations or footnotes as needed.\n"
    "Do not include placeholder text such as '(citation needed)' or '(citations omitted)'."
)


def generate_research_report_with_tools(
    prompt: str,
    model: str = "anthropic:claude-sonnet-4-6",
    max_turns: int = 10,
) -> str:
    """Generate a research report using tool-calling with arXiv and Tavily tools."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
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
            tool_name = call.function.name
            args = json.loads(call.function.arguments)

            try:
                tool_func = TOOL_MAPPING[tool_name]
                result = tool_func(**args)
            except Exception as exc:
                result = {"error": str(exc)}

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": tool_name,
                    "content": json.dumps(result),
                }
            )

    return final_text
