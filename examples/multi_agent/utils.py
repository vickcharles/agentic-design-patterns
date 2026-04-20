def _banner(title: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def log_agent_title(name: str, emoji: str = "") -> None:
    _banner(f"{emoji} {name}".strip())


def log_tool_call(name: str, args: str) -> None:
    print(f"[tool call] {name}({args})")


def log_tool_result(result) -> None:
    text = result if isinstance(result, str) else str(result)
    if len(text) > 500:
        text = text[:500] + "... [truncated]"
    print(f"[tool result] {text}")


def log_final_summary(content: str) -> None:
    print("[final]")
    print(content)
