import re


TOP_DOMAINS = {
    "wikipedia.org", "nature.com", "science.org", "sciencemag.org", "cell.com",
    "mit.edu", "stanford.edu", "harvard.edu", "nasa.gov", "noaa.gov", "europa.eu",
    "arxiv.org", "acm.org", "ieee.org", "neurips.cc", "icml.cc", "openreview.net",
    "elifesciences.org", "pnas.org", "jmlr.org", "springer.com", "sciencedirect.com",
}

URL_PATTERN = re.compile(r"https?://[^\s\]\)>\}]+", flags=re.IGNORECASE)


def evaluate_preferred_domains(
    text: str,
    preferred_domains: set[str] = TOP_DOMAINS,
    min_ratio: float = 0.4,
) -> dict:
    """Check how many URLs in `text` come from a preferred domain list.

    Returns a dict with `passed`, `total`, `preferred`, `ratio`, `details`, and a
    Markdown `report` summarising the evaluation.
    """

    urls = URL_PATTERN.findall(text or "")

    if not urls:
        return {
            "passed": False,
            "total": 0,
            "preferred": 0,
            "ratio": 0.0,
            "details": [],
            "report": (
                "### Evaluation — Preferred Domains\n"
                "No URLs detected. Include links in your research results."
            ),
        }

    details = []
    preferred_count = 0
    for url in urls:
        domain = url.split("/")[2]
        is_preferred = any(td in domain for td in preferred_domains)
        if is_preferred:
            preferred_count += 1
        details.append({"url": url, "domain": domain, "preferred": is_preferred})

    total = len(urls)
    ratio = preferred_count / total
    passed = ratio >= min_ratio

    detail_lines = [
        f"- {d['url']} -> {'PREFERRED' if d['preferred'] else 'NOT PREFERRED'}"
        for d in details
    ]
    report = (
        "### Evaluation — Preferred Domains\n"
        f"- Total results: {total}\n"
        f"- Preferred results: {preferred_count}\n"
        f"- Ratio: {ratio:.2%}\n"
        f"- Threshold: {min_ratio:.0%}\n"
        f"- Status: {'PASS' if passed else 'FAIL'}\n\n"
        "**Details:**\n" + "\n".join(detail_lines)
    )

    return {
        "passed": passed,
        "total": total,
        "preferred": preferred_count,
        "ratio": ratio,
        "details": details,
        "report": report,
    }
