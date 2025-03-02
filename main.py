from langgraph.graph import Graph
from research_agent import research_tool
from draft_agent import draft_answer

# Initialize the graph
workflow = Graph()

# Define a wrapper for research node to extract query
def research_node(input_dict):
    query = input_dict["query"]
    return research_tool.run(query)

# Add nodes
workflow.add_node("research", research_node)
workflow.add_node("draft", draft_answer)

# Define edges
workflow.add_edge("research", "draft")

# Set entry and exit points
workflow.set_entry_point("research")
workflow.set_finish_point("draft")

# Compile the workflow
app = workflow.compile()

# Function to run the research system
def run_research(query):
    """Run the research workflow with a given query."""
    result = app.invoke({"query": query})
    # Return both research data and drafted summary
    return result["research"], result["draft"]


if __name__ == "__main__":
    query = "why sugar is bad for your health"
    research_data, response = run_research(query)
    print("Research Data:", research_data)
    print("Research Response:", response)