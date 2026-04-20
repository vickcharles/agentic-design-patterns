from examples.component_level_eval import evaluate_preferred_domains, find_references
from examples.reflection_agent.utils import show_output


def run_component_eval_workflow(topic: str, min_ratio: float = 0.4) -> dict:
    """Research a topic and score the returned sources against preferred domains."""

    task = f"Find 2-3 key papers and reliable overviews about {topic}."

    print("Step 1: Gathering references...")
    references = find_references(task)
    show_output("Step 1 - References", references)

    print("Step 2: Evaluating preferred domains...")
    result = evaluate_preferred_domains(references, min_ratio=min_ratio)
    show_output("Step 2 - Evaluation", result["report"])

    return {"references": references, "evaluation": result}


if __name__ == "__main__":
    topic = "recent developments in black hole science"
    run_component_eval_workflow(topic)
