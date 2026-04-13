from examples.reflection_agent.client import CLIENT


def revise_draft(original_draft: str, reflection: str, model: str = "anthropic:claude-sonnet-4-6") -> str:
    """Step 3 - Revise the draft using feedback from reflection."""

    prompt = f"""You are an expert essay editor. Below is an original essay draft and feedback from a reviewer.

Original Draft:
{original_draft}

Reviewer Feedback:
{reflection}

Using the feedback above, rewrite the essay to address all issues raised. Improve clarity, coherence, argument strength, and overall flow. Return only the final revised essay with no additional commentary."""

    response = CLIENT.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,
    )

    return response.choices[0].message.content
