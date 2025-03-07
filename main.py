from langgraph.graph import Graph
from research_agent import research_tool
from draft_agent import draft_tool
from joblib import Memory

# Initialize caching with joblib
memory = Memory("cache", verbose=0)

# Define the research node to update the state
@memory.cache
def fetch_research_data(query: str, deep_research: bool = False) -> list:
    """Fetch research data using the research tool with caching."""
    result = research_tool.run(query, deep_research=deep_research)
    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict) and "error" in result[0]:
        raise Exception(f"Research failed: {result[0]['error']}")
    return result

def research_node(state):
    """Fetch research data and update the state."""
    query = state["query"]
    deep_research = state.get("deep_research", False)
    research_data = fetch_research_data(query, deep_research)
    state["research"] = research_data
    return state

# Define the draft node to use research data and update the state
def draft_node(state):
    """Draft a summary using research data and update the state."""
    research_data = state["research"]
    if not isinstance(research_data, list):
        raise Exception("Research data is not in the expected format (list required)")
    deep_research = state.get("deep_research", False)
    target_word_count = state.get("target_word_count", 1000)
    result = draft_tool.invoke({
        "data": research_data,
        "deep_research": deep_research,
        "target_word_count": target_word_count,
        "retries": 3,
        "delay": 5
    })
    if "Error drafting response" in result:
        raise Exception(result)
    state["draft"] = result
    return state

# Initialize the graph
workflow = Graph()

# Add nodes to the workflow
workflow.add_node("research", research_node)
workflow.add_node("draft", draft_node)

# Define edges
workflow.add_edge("research", "draft")

# Set entry and finish points
workflow.set_entry_point("research")
workflow.set_finish_point("draft")

# Compile the workflow
app = workflow.compile()

# Function to run the research system
def run_research(query, deep_research=False, target_word_count=1000):
    """Run the research workflow with a given query, deep research option, and target word count."""
    print(f"Running in {'Deep Research' if deep_research else 'Quick Research'} mode with target word count: {target_word_count}")
    input_dict = {"query": query, "deep_research": deep_research, "target_word_count": target_word_count}
    try:
        result = app.invoke(input_dict)
        # Ensure result is a dictionary and extract outputs
        if not isinstance(result, dict):
            raise Exception(f"Workflow returned unexpected type: {type(result)}")
        research_data = result.get("research", [])
        draft_response = result.get("draft", "Error: Draft not generated")
        return research_data, draft_response
    except Exception as e:
        raise Exception(f"Workflow failed: {str(e)}")

# Example usage
if __name__ == "__main__":
    query = "why sugar is bad for your health"
    deep_research = False
    target_word_count = 1000
    research_data, response = run_research(query, deep_research, target_word_count)
    print("Research Data:", research_data)
    print("Research Response:", response)