import os
import json
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
import requests
from openai import APIConnectionError

# Load environment variables from .env
load_dotenv()
#print("OpenRouter API Key:", os.getenv("OPENROUTER_API_KEY"))

# Initialize the ChatOpenAI client with OpenRouter
llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="qwen/qwen-vl-plus:free"
)

# Define the prompt for a structured summary
prompt = PromptTemplate(
    input_variables=["data"],
    template="""
    Generate a structured research summary based on the following data. The summary must include the following sections, each separated by a blank line and labeled with bold subheadings:
    1. **Introduction**: Briefly introduce the topic and its significance.
    2. **Key Findings**: Summarize the main points from the data.
    3. **Analysis**: Provide insights or implications of the findings.
    4. **Conclusion**: Conclude with potential future developments or recommendations.

    Ensure each section starts on a new line with its subheading in bold, followed by its content.

    Data: {data}
    """
)

# Drafting function with retry logic
def draft_answer(data, retries=3, delay=5):
    attempt = 0
    while attempt < retries:
        try:
            data_str = json.dumps(data)
            #print("Data being passed to LLM:", data_str[:500] + "..." if len(data_str) > 500 else data_str)
            # Test API endpoint connectivity
            test_response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"},
                timeout=10
            )
            #print("API endpoint test response:", test_response.status_code, test_response.text[:200])
            # Format the prompt and invoke the LLM
            formatted_prompt = prompt.format(data=data_str)
            messages = [{"role": "user", "content": formatted_prompt}]
            response = llm.invoke(messages)
            return response.content
        except APIConnectionError as e:
            print(f"APIConnectionError on attempt {attempt + 1}: {str(e)}")
            attempt += 1
            time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"Network error on attempt {attempt + 1}: {str(e)}")
            attempt += 1
            time.sleep(delay)
        except Exception as e:
            print(f"Other error: {type(e).__name__} - {str(e)}")
            return f"Error drafting response: {type(e).__name__} - {str(e)}"
    return "Error drafting response: Max retries exceeded."

# Define the tool
draft_tool = Tool(
    name="DraftAnswer",
    func=draft_answer,
    description="Drafts a structured research summary based on research data."
)