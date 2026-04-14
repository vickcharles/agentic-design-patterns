import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


ARXIV_API_URL = "http://export.arxiv.org/api/query"
ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}


def arxiv_search_tool(query: str, max_results: int = 5) -> list[dict]:
    """Search arXiv and return a list of papers."""
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
    }
    url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            body = response.read().decode("utf-8")
    except Exception as exc:
        return [{"error": f"arXiv request failed: {exc}"}]

    root = ET.fromstring(body)
    papers = []
    for entry in root.findall("atom:entry", ARXIV_NS):
        title = (entry.findtext("atom:title", default="", namespaces=ARXIV_NS) or "").strip()
        summary = (entry.findtext("atom:summary", default="", namespaces=ARXIV_NS) or "").strip()
        published = (entry.findtext("atom:published", default="", namespaces=ARXIV_NS) or "").strip()
        url_ = (entry.findtext("atom:id", default="", namespaces=ARXIV_NS) or "").strip()

        authors = [
            (a.findtext("atom:name", default="", namespaces=ARXIV_NS) or "").strip()
            for a in entry.findall("atom:author", ARXIV_NS)
        ]

        link_pdf = None
        for link in entry.findall("atom:link", ARXIV_NS):
            if link.get("title") == "pdf":
                link_pdf = link.get("href")
                break

        paper = {
            "title": title,
            "authors": authors,
            "published": published[:10] if published else "",
            "url": url_,
            "summary": summary,
        }
        if link_pdf:
            paper["link_pdf"] = link_pdf
        papers.append(paper)

    return papers


def tavily_search_tool(
    query: str,
    max_results: int = 5,
    include_images: bool = False,
) -> list[dict]:
    """Search the web via the Tavily API."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return [{"error": "TAVILY_API_KEY is not set in the environment."}]

    try:
        from tavily import TavilyClient
    except ImportError:
        return [{"error": "tavily-python is not installed. Run: pip install tavily-python"}]

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            max_results=max_results,
            include_images=include_images,
        )
    except Exception as exc:
        return [{"error": f"Tavily request failed: {exc}"}]

    results = []
    for item in response.get("results", []):
        results.append(
            {
                "title": item.get("title", ""),
                "content": item.get("content", ""),
                "url": item.get("url", ""),
            }
        )
    return results


arxiv_tool_def = {
    "type": "function",
    "function": {
        "name": "arxiv_search_tool",
        "description": "Search arXiv for academic papers related to a query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query for arXiv.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of papers to return.",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}


tavily_tool_def = {
    "type": "function",
    "function": {
        "name": "tavily_search_tool",
        "description": "Search the web via Tavily for general web content.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The web search query.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return.",
                    "default": 5,
                },
                "include_images": {
                    "type": "boolean",
                    "description": "Whether to include image URLs.",
                    "default": False,
                },
            },
            "required": ["query"],
        },
    },
}


TOOL_MAPPING = {
    "arxiv_search_tool": arxiv_search_tool,
    "tavily_search_tool": tavily_search_tool,
}


def parse_input(report) -> str:
    """Accept either a plain string or a messages list and return the final text."""
    if isinstance(report, str):
        return report

    if isinstance(report, list):
        for msg in reversed(report):
            content = getattr(msg, "content", None)
            if content is None and isinstance(msg, dict):
                content = msg.get("content")
            role = getattr(msg, "role", None)
            if role is None and isinstance(msg, dict):
                role = msg.get("role")
            if role == "assistant" and content:
                return content
        return ""

    return str(report)
