from examples.reflection_agent.client import CLIENT


def generate_draft(topic: str, model: str = "anthropic:claude-sonnet-4-6") -> str:
    """Step 1 - Generate an initial essay draft from a topic."""

    prompt = f"Write a complete draft essay on the following topic: {topic}"

    response = CLIENT.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,
    )

    return response.choices[0].message.content
