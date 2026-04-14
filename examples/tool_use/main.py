from examples.reflection_agent.utils import show_output
from examples.tool_use import (
    convert_report_to_html,
    generate_research_report_with_tools,
    reflection_and_rewrite,
)


def run_tool_use_workflow(topic: str) -> dict:
    """Run the full tool-use workflow: Research -> Reflection -> HTML."""

    print("Step 1: Generating research report with tools...")
    preliminary_report = generate_research_report_with_tools(topic)
    show_output("Step 1 - Research Report", preliminary_report)

    print("Step 2: Reflecting and rewriting...")
    reflection = reflection_and_rewrite(preliminary_report)
    show_output("Step 2 - Reflection", reflection["reflection"])
    show_output("Step 2 - Revised Report", reflection["revised_report"])

    print("Step 3: Converting revised report to HTML...")
    html = convert_report_to_html(reflection["revised_report"])
    show_output("Step 3 - HTML", html[:600] + "\n... [truncated]")

    return {
        "preliminary_report": preliminary_report,
        "reflection": reflection["reflection"],
        "revised_report": reflection["revised_report"],
        "html": html,
    }


if __name__ == "__main__":
    topic = "Radio observations of recurrent novae"
    results = run_tool_use_workflow(topic)
