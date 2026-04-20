import base64
import json
import os
import re

from examples.multi_agent import utils
from examples.multi_agent.client import CLIENT


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {"quote": "", "justification": text.strip()}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"quote": "", "justification": text.strip()}


def _build_user_content(trend_summary: str, image_path: str):
    text_block = {
        "type": "text",
        "text": (
            f"Here is a trend analysis:\n\n\"\"\"{trend_summary}\"\"\"\n\n"
            "Return JSON with keys `quote` (short elegant campaign phrase, max 12 "
            "words) and `justification` (why this quote matches the trend and visual)."
        ),
    }
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64}"},
            },
            text_block,
        ]
    return [text_block]


def copywriter_agent(
    image_path: str,
    trend_summary: str,
    model: str = "anthropic:claude-sonnet-4-6",
) -> dict:
    """Generate a campaign quote and justification grounded in the image + trend."""

    utils.log_agent_title("Copywriter Agent", "[CW]")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a copywriter creating elegant campaign quotes based on an "
                "image and a marketing trend summary."
            ),
        },
        {"role": "user", "content": _build_user_content(trend_summary, image_path)},
    ]

    response = CLIENT.chat.completions.create(model=model, messages=messages)
    content = response.choices[0].message.content.strip()
    utils.log_final_summary(content)

    parsed = _extract_json(content)
    parsed["image_path"] = image_path
    return parsed
