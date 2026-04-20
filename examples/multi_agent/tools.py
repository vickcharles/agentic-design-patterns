import json

from examples.tool_use.research_tools import tavily_search_tool, tavily_tool_def


_CATALOG = [
    {
        "id": "SG-001",
        "name": "Coastline Aviators",
        "description": "Polarized gold-frame aviators with gradient amber lenses.",
        "stock": 42,
        "price": 159.0,
        "tags": ["aviator", "polarized", "metal frame", "summer"],
    },
    {
        "id": "SG-002",
        "name": "Sunset Oversized Cat-Eye",
        "description": "Bold cat-eye sunglasses with tortoise acetate frame and rose lenses.",
        "stock": 18,
        "price": 189.0,
        "tags": ["cat-eye", "oversized", "tortoise", "retro"],
    },
    {
        "id": "SG-003",
        "name": "Lagoon Round Wire",
        "description": "Minimal round wire-frame sunglasses with blue-tinted lenses.",
        "stock": 27,
        "price": 129.0,
        "tags": ["round", "wire", "minimalist", "y2k"],
    },
    {
        "id": "SG-004",
        "name": "Riviera Chunky Square",
        "description": "Chunky square-frame sunglasses with matte-black acetate and dark lenses.",
        "stock": 33,
        "price": 169.0,
        "tags": ["square", "chunky", "bold", "gender-neutral"],
    },
    {
        "id": "SG-005",
        "name": "Dune Rimless Shield",
        "description": "Rimless futuristic shield sunglasses with mirrored silver lenses.",
        "stock": 9,
        "price": 219.0,
        "tags": ["shield", "rimless", "futurism", "techwear"],
    },
]


def product_catalog_tool() -> list[dict]:
    """Return the internal sunglasses product catalog."""
    return _CATALOG


product_catalog_tool_def = {
    "type": "function",
    "function": {
        "name": "product_catalog_tool",
        "description": "Return the internal sunglasses catalog as a list of products.",
        "parameters": {"type": "object", "properties": {}},
    },
}


TOOL_MAPPING = {
    "tavily_search_tool": tavily_search_tool,
    "product_catalog_tool": product_catalog_tool,
}


def get_available_tools() -> list[dict]:
    return [tavily_tool_def, product_catalog_tool_def]


def handle_tool_call(tool_call) -> object:
    name = tool_call.function.name
    args_raw = tool_call.function.arguments or "{}"
    try:
        args = json.loads(args_raw) if args_raw else {}
    except json.JSONDecodeError:
        args = {}
    try:
        return TOOL_MAPPING[name](**args)
    except KeyError:
        return {"error": f"Unknown tool: {name}"}
    except Exception as exc:
        return {"error": str(exc)}


def create_tool_response_message(tool_call, result) -> dict:
    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "name": tool_call.function.name,
        "content": json.dumps(result),
    }
