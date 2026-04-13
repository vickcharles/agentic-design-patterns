def show_output(title: str, content: str) -> None:
    """Display a step's output with a formatted header."""
    separator = "=" * 60
    print(f"\n{separator}")
    print(f"  {title}")
    print(separator)
    print(content)
    print(separator)
