import os
import json
from dotenv import load_dotenv
from langchain.tools import Tool
from tavily import TavilyClient

# Load environment variables from .env
load_dotenv()

# Initialize Tavily client with API key from .env
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def research_web(query, deep_research=False):
    """Fetch data from the web using Tavily based on a query."""
    try:
        # Adjust max_results based on deep_research mode
        max_results = 30 if deep_research else 5
        data = []
        url_set = set()

        # Initial query
        results = tavily_client.search(query, max_results=max_results)
        initial_data = [{"title": r["title"], "content": r["content"], "url": r["url"]} for r in results["results"]]
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
                additional_data = [{"title": r["title"], "content": r["content"], "url": r["url"]} for r in results["results"]]
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