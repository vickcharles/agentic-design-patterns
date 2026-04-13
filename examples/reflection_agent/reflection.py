from examples.reflection_agent.client import CLIENT


def reflect_on_draft(draft: str, model: str = "anthropic:claude-haiku-4-5-20251001") -> str:
    """Step 2 - Reflect on a draft with constructive feedback."""

    prompt = f"""You are a critical essay reviewer. Analyze the following essay draft and provide
constructive feedback addressing structure, clarity, strength of argument, and writing style.
Be specific about what works and what needs improvement.

Essay Draft:
{draft}"""

    response = CLIENT.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,
    )

    return response.choices[0].message.content
