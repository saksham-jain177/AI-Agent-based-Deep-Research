import os
import json
from dotenv import load_dotenv
from langchain.tools import Tool
from tavily import TavilyClient
from urllib.parse import urlparse

# Load environment variables from .env
load_dotenv()

def research_web(query, deep_research=False):
    """Fetch data from the web using Tavily based on a query."""
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            # Return a structured error so callers can handle gracefully
            return [{
                "error": "Missing TAVILY_API_KEY",
                "message": "Set TAVILY_API_KEY in your environment or .env file to enable web research.",
            }]

        tavily_client = TavilyClient(api_key=api_key)
        # Domain filtering (avoid social chatter like reddit by default)
        excluded_env = os.getenv("EXCLUDE_DOMAINS", "reddit.com,x.com,twitter.com,tiktok.com,pinterest.com,instagram.com")
        EXCLUDED_DOMAINS = {d.strip().lower() for d in excluded_env.split(',') if d.strip()}
        # Adjust max_results based on deep_research mode
        max_results = 30 if deep_research else 5
        data = []
        url_set = set()

        # Initial query
        results = tavily_client.search(query, max_results=max_results)
        initial_data = []
        for r in results["results"]:
            u = r.get("url") or ""
            domain = urlparse(u).netloc.lower()
            if any(domain.endswith(ex) for ex in EXCLUDED_DOMAINS):
                continue
            initial_data.append({"title": r.get("title",""), "content": r.get("content",""), "url": u})
        for item in initial_data:
            if item["url"] not in url_set:
                data.append(item)
                url_set.add(item["url"])

        # If deep research mode and fewer than 20 results, try additional queries
        if deep_research and len(data) < 20:
            print(f"Initial query returned {len(data)} results, attempting additional queries...")
            # List of variant queries to broaden the search
            variant_queries = [
                f"{query} overview OR review OR advancements OR trends",
                f"{query} recent developments OR innovations OR breakthroughs",
                f"{query} applications OR use cases OR impact"
            ]
            for variant_query in variant_queries:
                if len(data) >= 20:
                    break
                results = tavily_client.search(variant_query, max_results=max_results)
                additional_data = []
                for r in results["results"]:
                    u = r.get("url") or ""
                    domain = urlparse(u).netloc.lower()
                    if any(domain.endswith(ex) for ex in EXCLUDED_DOMAINS):
                        continue
                    additional_data.append({"title": r.get("title",""), "content": r.get("content",""), "url": u})
                for item in additional_data:
                    if item["url"] not in url_set:
                        data.append(item)
                        url_set.add(item["url"])
                # Limit to 30 results to avoid overwhelming the model
                data = data[:30]

        with open("research_data.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"Fetched {len(data)} research items")
        return data
    except Exception as e:
        raise Exception(f"Research failed: {str(e)}")

research_tool = Tool(
    name="WebResearch",
    func=lambda query, deep_research=False: research_web(query, deep_research),
    description="Fetches data from the web based on a query. Supports deep research mode with more results."
)