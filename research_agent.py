import os
import json
from dotenv import load_dotenv
from langchain.tools import Tool
from tavily import TavilyClient
from urllib.parse import urlparse
from typing import List, Dict, Any

# Load environment variables from .env
load_dotenv()

# Optional: Import vector store if available
VECTOR_STORE_ENABLED = os.getenv("ENABLE_VECTOR_STORE", "false").lower() == "true"
vector_store = None
if VECTOR_STORE_ENABLED:
    try:
        from vector_store import get_vector_store
        vector_store = get_vector_store()
        print("Vector store enabled and initialized")
    except ImportError:
        print("Vector store dependencies not installed, proceeding without it")
        VECTOR_STORE_ENABLED = False
    except Exception as e:
        print(f"Vector store initialization failed: {e}, proceeding without it")
        VECTOR_STORE_ENABLED = False

def research_web(query, deep_research=False, language='en'):
    """Fetch data from the web using Tavily based on a query, with optional vector store integration."""
    try:
        # Check if we should prefer cache (can be configured)
        PREFER_CACHE = os.getenv("PREFER_CACHE_RESULTS", "false").lower() == "true"
        
        # First, check vector store if enabled
        vector_results = []
        if VECTOR_STORE_ENABLED and vector_store:
            try:
                # Search vector store for relevant past research
                vector_results = vector_store.search(
                    query=query,
                    language=language,
                    top_k=10 if deep_research else 5
                )
                print(f"Found {len(vector_results)} relevant items from vector store")
                
                # If we prefer cache and have good results, skip web search
                if PREFER_CACHE and len(vector_results) >= 5:
                    print("Using cached results only (PREFER_CACHE_RESULTS=true)")
                    return [
                        {
                            "title": r['metadata'].get('title', 'Cached Result'),
                            "content": r['content'],
                            "url": r['metadata'].get('url', 'cache://local')
                        }
                        for r in vector_results
                    ]
            except Exception as e:
                print(f"Vector search failed: {e}, continuing with web search")
        
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            # If we have vector results, return those; otherwise return error
            if vector_results:
                return [
                    {
                        "title": r['metadata'].get('title', 'Cached Result'),
                        "content": r['content'],
                        "url": r['metadata'].get('url', 'cache://local')
                    }
                    for r in vector_results
                ]
            return [{
                "error": "Missing TAVILY_API_KEY",
                "message": "Set TAVILY_API_KEY in your environment or .env file to enable web research.",
            }]

        tavily_client = TavilyClient(api_key=api_key)
        # Domain filtering (avoid social chatter like reddit by default)
        excluded_env = os.getenv("EXCLUDE_DOMAINS", "reddit.com,x.com,twitter.com,tiktok.com,pinterest.com,instagram.com")
        EXCLUDED_DOMAINS = {d.strip().lower() for d in excluded_env.split(',') if d.strip()}
        # Adjust max_results based on deep_research mode and vector results
        # If we have vector results, fetch fewer new results
        max_results = (20 if deep_research else 5) if vector_results else (30 if deep_research else 5)
        data = []
        url_set = set()
        
        # Add vector results first (they're most relevant)
        for vr in vector_results:
            url = vr['metadata'].get('url', 'cache://local')
            if url not in url_set and not url.startswith('cache://'):
                data.append({
                    "title": vr['metadata'].get('title', 'Cached Result'),
                    "content": vr['content'],
                    "url": url,
                    "from_cache": True
                })
                url_set.add(url)

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

        # Store results in vector store if enabled
        if VECTOR_STORE_ENABLED and vector_store and data:
            try:
                # Only store non-cached results
                new_sources = [d for d in data if not d.get('from_cache', False)]
                if new_sources:
                    added = vector_store.add_research_data(
                        query=query,
                        sources=new_sources,
                        language=language
                    )
                    print(f"Added {added} new items to vector store")
            except Exception as e:
                print(f"Failed to store in vector DB: {e}")
        
        # Clean up the from_cache flag before returning
        for item in data:
            item.pop('from_cache', None)
        
        with open("research_data.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"Fetched {len(data)} research items ({len([d for d in data if d.get('from_cache')])} from cache)")
        return data
    except Exception as e:
        raise Exception(f"Research failed: {str(e)}")

research_tool = Tool(
    name="WebResearch",
    func=lambda query, deep_research=False, language='en': research_web(query, deep_research, language),
    description="Fetches data from the web based on a query. Supports deep research mode with more results and vector store integration."
)