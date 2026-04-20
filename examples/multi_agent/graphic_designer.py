import json
import os
import re
import urllib.request

from examples.multi_agent import utils
from examples.multi_agent.client import CLIENT


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {"prompt": text.strip(), "caption": ""}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"prompt": text.strip(), "caption": ""}


def generate_image_with_openai(prompt: str, size: str = "1024x1024") -> str:
    """Call OpenAI image API and save the image locally; return path or empty string."""
    if not os.environ.get("OPENAI_API_KEY"):
        return ""
    try:
        import openai
    except ImportError:
        return ""

    client = openai.OpenAI()
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality="standard",
        n=1,
        response_format="url",
    )
    url = response.data[0].url
    filename = os.path.basename(url.split("?")[0]) or "campaign_image.png"
    with urllib.request.urlopen(url, timeout=60) as resp:
        data = resp.read()
    with open(filename, "wb") as f:
        f.write(data)
    return filename


def graphic_designer_agent(
    trend_insights: str,
    caption_style: str = "short punchy",
    size: str = "1024x1024",
    model: str = "anthropic:claude-sonnet-4-6",
) -> dict:
    """Produce a campaign prompt, caption, and (optionally) a DALL-E image."""

    utils.log_agent_title("Graphic Designer Agent", "[GD]")

    system = (
        "You are a visual marketing assistant. Based on the input trend insights, "
        "write a creative, vivid prompt for an AI image generation model, plus a "
        "short caption."
    )
    user_prompt = (
        f"Trend insights:\n{trend_insights}\n\n"
        "Return JSON with keys `prompt` (vivid image-generation description) and "
        f"`caption` (style: {caption_style}).\n"
        'Example: {"prompt": "...", "caption": "..."}'
    )

    response = CLIENT.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ],
    )
    parsed = _extract_json(response.choices[0].message.content.strip())
    prompt = parsed.get("prompt", "")
    caption = parsed.get("caption", "")

    image_path = generate_image_with_openai(prompt, size=size)

    utils.log_final_summary(
        f"prompt: {prompt}\ncaption: {caption}\nimage_path: {image_path or '(skipped)'}"
    )

    return {"prompt": prompt, "caption": caption, "image_path": image_path}
