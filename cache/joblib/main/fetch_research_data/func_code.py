# first line: 10
@memory.cache
def fetch_research_data(query: str, deep_research: bool = False) -> list:
    """Fetch research data using the research tool with caching."""
    result = research_tool.run(query, deep_research=deep_research)
    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict) and "error" in result[0]:
        raise Exception(f"Research failed: {result[0]['error']}")
    return result
