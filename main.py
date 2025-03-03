from langgraph.graph import Graph
from research_agent import research_tool
from draft_agent import draft_answer

# Initialize the graph
workflow = Graph()

# Define the research node to update the state
def research_node(state):
    """Fetch research data and update the state."""
    query = state["query"]
    deep_research = state.get("deep_research", False)
    result = research_tool.run(query, deep_research=deep_research)
    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict) and "error" in result[0]:
        raise Exception(f"Research failed: {result[0]['error']}")
    state["research"] = result
    return state

# Define the draft node to use research data and update the state
def draft_node(state):
    """Draft a summary using research data and update the state."""
    research_data = state["research"]
    if not isinstance(research_data, list):
        raise Exception("Research data is not in the expected format (list required)")
    deep_research = state.get("deep_research", False)
    result = draft_answer(research_data, deep_research=deep_research)
    if "Error drafting response" in result:
        raise Exception(result)
    state["draft"] = result
    return state

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
def run_research(query, deep_research=False):
    """Run the research workflow with a given query and deep research option."""
    print(f"Running in {'Deep Research' if deep_research else 'Quick Research'} mode")
    input_dict = {"query": query, "deep_research": deep_research}
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
    research_data, response = run_research(query, deep_research)
    print("Research Data:", research_data)
    print("Research Response:", response)