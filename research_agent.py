import os
import json
from dotenv import load_dotenv
from langchain.tools import Tool
from tavily import TavilyClient

# Load environment variables from .env
load_dotenv()

# Initialize Tavily client with API key from .env
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def research_web(query):
    """Fetch data from the web using Tavily based on a query."""
    try:
        results = tavily_client.search(query, max_results=5)
        data = [{"title": r["title"], "content": r["content"], "url": r["url"]} for r in results["results"]]
        with open("research_data.json", "w") as f:
            json.dump(data, f, indent=2)
        return data
    except Exception as e:
        return {"error": str(e)}

research_tool = Tool(
    name="WebResearch",
    func=research_web,
    description="Fetches data from the web based on a query."
)