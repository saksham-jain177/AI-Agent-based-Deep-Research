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

# Initialize the ChatOpenAI client with OpenRouter
llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="cognitivecomputations/dolphin3.0-r1-mistral-24b:free"  # Using the specified model
)

# Prompt for shallow research (unchanged)
shallow_prompt = PromptTemplate(
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

# Prompts for each section in deep research mode (updated to prevent section name repetition)
abstract_prompt = PromptTemplate(
    input_variables=["data"],
    template="""
    Generate a detailed abstract for a research paper based on the following data. Provide a comprehensive overview of the topic, research objectives, key findings, and their implications (150-200 words). Include a brief mention of the methodology and significance of the research. Provide detailed insights and avoid summarizing the data directly—focus on synthesizing the overall narrative. Do not include the word "Abstract" in your response; only provide the content of the abstract section.

    Data: {data}
    """
)

introduction_prompt = PromptTemplate(
    input_variables=["data"],
    template="""
    Generate a detailed introduction for a research paper based on the following data. Introduce the topic in depth, covering its historical context, current significance, and the purpose of this research. Discuss its relevance in scientific, technological, or societal contexts, citing specific trends or events (400-600 words). Elaborate with examples, historical developments, and current challenges in the field. Do not include the word "Introduction" in your response; only provide the content of the introduction section.

    Data: {data}
    """
)

literature_review_prompt = PromptTemplate(
    input_variables=["data"],
    template="""
    Generate a detailed literature review for a research paper based on the following data. Synthesize existing knowledge and findings from all provided sources. Highlight trends, gaps, controversies, and key developments in the field, providing a critical overview of the current state of research (600-800 words). Include specific references to studies or advancements mentioned in the data, and discuss their implications. Do not include the phrase "Literature Review" in your response; only provide the content of the literature review section.

    Data: {data}
    """
)

key_findings_prompt = PromptTemplate(
    input_variables=["data"],
    template="""
    Generate a detailed key findings section for a research paper based on the following data. Summarize the main points in exhaustive detail, including specific examples, data points, and insights from each source. Ensure comprehensive coverage of all relevant findings, discussing methodologies, results, and their significance (800-1000 words). Provide in-depth explanations of each finding. Do not include the phrase "Key Findings" in your response; only provide the content of the key findings section.

    Data: {data}
    """
)

analysis_prompt = PromptTemplate(
    input_variables=["data"],
    template="""
    Generate a detailed analysis section for a research paper based on the following data. Provide in-depth insights, implications, and critical analysis of the findings. Discuss broader impacts, potential applications, limitations, challenges, and areas of uncertainty, integrating perspectives from the data. Compare and contrast findings, and propose hypotheses for future exploration (800-1000 words). Elaborate extensively with examples and potential scenarios. Do not include the word "Analysis" in your response; only provide the content of the analysis section.

    Data: {data}
    """
)

conclusion_prompt = PromptTemplate(
    input_variables=["data"],
    template="""
    Generate a detailed conclusion section for a research paper based on the following data. Provide a thorough summary of findings, their significance, and potential future developments. Offer detailed recommendations for further research, addressing how the findings contribute to the field and what steps should be taken next (400-600 words). Discuss long-term implications and future directions. Do not include the word "Conclusion" in your response; only provide the content of the conclusion section.

    Data: {data}
    """
)

# Drafting function with retry logic and deep research support
def draft_answer(data, deep_research=False, retries=3, delay=5):
    """Draft a research summary with retry logic, supporting deep research mode."""
    if not data:
        return "Error drafting response: No research data provided"

    attempt = 0
    while attempt < retries:
        try:
            data_str = json.dumps(data)
            # Test API endpoint connectivity
            test_response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"},
                timeout=10
            )

            if not deep_research:
                # Shallow mode: Single LLM call
                selected_prompt = shallow_prompt
                formatted_prompt = selected_prompt.format(data=data_str)
                messages = [{"role": "user", "content": formatted_prompt}]
                response = llm.invoke(messages)
                response_text = response.content
            else:
                # Deep research mode: Split into multiple LLM calls
                response_text = ""
                sections = [
                    ("Abstract", abstract_prompt),
                    ("Introduction", introduction_prompt),
                    ("Literature Review", literature_review_prompt),
                    ("Key Findings", key_findings_prompt),
                    ("Analysis", analysis_prompt),
                    ("Conclusion", conclusion_prompt)
                ]
                for section_name, section_prompt in sections:
                    formatted_prompt = section_prompt.format(data=data_str)
                    messages = [{"role": "user", "content": formatted_prompt}]
                    response = llm.invoke(messages)
                    section_text = response.content.strip()
                    response_text += f"\n\n**{section_name}**\n\n{section_text}"

                # Add References section
                references = "\n\n**References**\n"
                for i, item in enumerate(data, 1):
                    references += f"{i}. {item['url']}\n"
                response_text += references

            # Debug: Calculate and print word count of the response
            word_count = len(response_text.split())
            print(f"Generated summary word count: {word_count}")
            return response_text

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

# Define the tool with support for deep research
draft_tool = Tool(
    name="DraftAnswer",
    func=lambda data, deep_research=False: draft_answer(data, deep_research),
    description="Drafts a structured research summary based on research data. Supports deep research mode for detailed, research-paper-style summaries."
)