from examples.reflection_agent import generate_draft, reflect_on_draft, revise_draft
from examples.reflection_agent.utils import show_output


def run_reflection_workflow(topic: str) -> dict:
    """Run the full 3-step reflection workflow: Draft -> Reflect -> Revise."""

    # Step 1 - Drafting
    print("Step 1: Generating draft...")
    draft = generate_draft(topic)
    show_output("Step 1 - Draft", draft)

    # Step 2 - Reflection
    print("Step 2: Reflecting on draft...")
    feedback = reflect_on_draft(draft)
    show_output("Step 2 - Reflection", feedback)

    # Step 3 - Revision
    print("Step 3: Revising draft...")
    revised = revise_draft(draft, feedback)
    show_output("Step 3 - Revision", revised)

    return {
        "draft": draft,
        "feedback": feedback,
        "revised": revised,
    }


if __name__ == "__main__":
    topic = "Should social media platforms be regulated by the government?"
    results = run_reflection_workflow(topic)
