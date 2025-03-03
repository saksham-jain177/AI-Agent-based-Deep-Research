import os
import json
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
import requests
from openai import APIConnectionError
import logging
import re

# Set up logging
logging.basicConfig(filename="research_agent.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables from .env
load_dotenv()

# Initialize the ChatOpenAI client with OpenRouter
llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="cognitivecomputations/dolphin3.0-r1-mistral-24b:free"
)

# Prompts for shallow research mode
shallow_introduction_prompt = PromptTemplate(
    input_variables=["data"],
    template="""
    Generate a concise introduction for a research summary based on the following data. Briefly introduce the topic and its significance in 50-75 words, focusing on clarity and understanding with minimal context. Do not include the word "Introduction" in your response; only provide the content of the introduction section. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

shallow_key_findings_prompt = PromptTemplate(
    input_variables=["data"],
    template="""
    Generate a concise key findings section for a research summary based on the following data. Summarize the main points in a numbered list (3-5 points, 75-100 words total), focusing on clarity and understanding with minimal context. Each numbered point must be on a new line with a newline character (\n) between points (e.g., 1. First finding.\n2. Second finding.\n3. Third finding.). Ensure there is a space after each number and period (e.g., "1. " not "1."). Do not include the phrase "Key Findings" in your response; only provide the content of the key findings section. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

shallow_analysis_prompt = PromptTemplate(
    input_variables=["data"],
    template="""
    Generate a concise analysis section for a research summary based on the following data. Provide brief insights or implications of the findings in 50-75 words, focusing on clarity and understanding with minimal context. Do not include the word "Analysis" in your response; only provide the content of the analysis section. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

shallow_conclusion_prompt = PromptTemplate(
    input_variables=["data"],
    template="""
    Generate a concise conclusion section for a research summary based on the following data. Conclude with a short statement on potential future developments or recommendations in 25-50 words, focusing on clarity and understanding with minimal context. Do not include the word "Conclusion" in your response; only provide the content of the conclusion section. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

# Prompts for each section in deep research mode
abstract_prompt = PromptTemplate(
    input_variables=["data"],
    template="""
    Generate a detailed abstract for a research paper based on the following data. Provide a comprehensive overview of the topic, research objectives, key findings, and their implications (150-200 words). Include a brief mention of the methodology and significance of the research. Provide detailed insights and avoid summarizing the data directly—focus on synthesizing the overall narrative. Do not include the word "Abstract" in your response; only provide the content of the abstract section. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

introduction_prompt = PromptTemplate(
    input_variables=["data"],
    template="""
    Generate a detailed introduction for a research paper based on the following data. Introduce the topic in depth, covering its historical context, current significance, and the purpose of this research. Discuss its relevance in scientific, technological, or societal contexts, citing specific trends or events (400-600 words). Elaborate with examples, historical developments, and current challenges in the field. Do not include the word "Introduction" in your response; only provide the content of the introduction section. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

literature_review_prompt = PromptTemplate(
    input_variables=["data"],
    template="""
    Generate a detailed literature review for a research paper based on the following data. Synthesize existing knowledge and findings from all provided sources. Highlight trends, gaps, controversies, and key developments in the field, providing a critical overview of the current state of research (600-800 words). Include specific references to studies or advancements mentioned in the data, and discuss their implications. Do not include the phrase "Literature Review" in your response; only provide the content of the literature review section. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

key_findings_prompt = PromptTemplate(
    input_variables=["data"],
    template="""
    Generate a detailed key findings section for a research paper based on the following data. Summarize the main points in a numbered list (5-7 points, 800-1000 words total), including specific examples, data points, and insights from each source where applicable. Ensure comprehensive coverage of all relevant findings, discussing methodologies, results, and their significance. Each numbered point must be on a new line with a newline character (\n) between points (e.g., 1. First finding.\n2. Second finding.\n3. Third finding.). Ensure there is a space after each number and period (e.g., "1. " not "1."). Do not include the phrase "Key Findings" in your response; only provide the content of the key findings section. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

analysis_prompt = PromptTemplate(
    input_variables=["data"],
    template="""
    Generate a detailed analysis section for a research paper based on the following data. Provide in-depth insights, implications, and critical analysis of the findings. Discuss broader impacts, potential applications, limitations, challenges, and areas of uncertainty, integrating perspectives from the data. Compare and contrast findings, and propose hypotheses for future exploration (800-1000 words). Elaborate extensively with examples and potential scenarios. Do not include the word "Analysis" in your response; only provide the content of the analysis section. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

conclusion_prompt = PromptTemplate(
    input_variables=["data"],
    template="""
    Generate a detailed conclusion section for a research paper based on the following data. Provide a thorough summary of findings, their significance, and potential future developments. Offer detailed recommendations for further research, addressing how the findings contribute to the field and what steps should be taken next (400-600 words). Discuss long-term implications and future directions. Do not include the word "Conclusion" in your response; only provide the content of the conclusion section. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

# Function to clean <think> tags from text
def clean_think_tags(text):
    """Remove <think> tags and their contents from the text."""
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    cleaned_text = re.sub(r"</?think>", "", cleaned_text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    return cleaned_text

# Function to format Key Findings as a proper numbered list
def format_key_findings(text):
    """Format the Key Findings section as a numbered list with each point on a new line."""
    # Normalize whitespace and split on numbered points (e.g., "1.", "2.")
    text = re.sub(r"\s+", " ", text.strip())
    # Split on numbered points, allowing for optional space after the period
    points = re.split(r"(?=\d+\.\s?)", text)
    formatted_text = ""
    for point in points:
        point = point.strip()
        if point:
            # Ensure there's a space after the number and period (e.g., "1. " not "1.")
            point = re.sub(r"^(\d+\.)([^\s])", r"\1 \2", point)
            # Add a newline after each point
            formatted_text += point + "\n"
    # Remove trailing newline and normalize newlines
    formatted_text = formatted_text.strip()
    formatted_text = re.sub(r"\n{2,}", "\n", formatted_text)
    return formatted_text

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
                # Shallow mode: Split into multiple LLM calls for consistent structure
                response_text = ""
                sections = [
                    ("Introduction", shallow_introduction_prompt),
                    ("Key Findings", shallow_key_findings_prompt),
                    ("Analysis", shallow_analysis_prompt),
                    ("Conclusion", shallow_conclusion_prompt)
                ]
                for section_name, section_prompt in sections:
                    formatted_prompt = section_prompt.format(data=data_str)
                    messages = [{"role": "user", "content": formatted_prompt}]
                    response = llm.invoke(messages)
                    section_text = clean_think_tags(response.content.strip())
                    # Special handling for Key Findings to ensure numbered list formatting
                    if section_name == "Key Findings":
                        section_text = format_key_findings(section_text)
                    response_text += f"\n\n**{section_name}**\n\n{section_text}"
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
                    section_text = clean_think_tags(response.content.strip())
                    # Apply formatting to Key Findings in deep research mode as well
                    if section_name == "Key Findings":
                        section_text = format_key_findings(section_text)
                    response_text += f"\n\n**{section_name}**\n\n{section_text}"

                # Add References section
                references = "\n\n**References**\n"
                for i, item in enumerate(data, 1):
                    references += f"{i}. {item['url']}\n"
                response_text += references

            # Debug: Calculate and log word count of the response
            word_count = len(response_text.split())
            logging.info(f"Generated summary word count: {word_count}")
            return response_text

        except APIConnectionError as e:
            logging.error(f"APIConnectionError on attempt {attempt + 1}: {str(e)}")
            attempt += 1
            time.sleep(delay)
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error on attempt {attempt + 1}: {str(e)}")
            attempt += 1
            time.sleep(delay)
        except Exception as e:
            logging.error(f"Other error: {type(e).__name__} - {str(e)}")
            return f"Error drafting response: {type(e).__name__} - {str(e)}"
    return "Error drafting response: Max retries exceeded."

# Define the tool with support for deep research
draft_tool = Tool(
    name="DraftAnswer",
    func=lambda data, deep_research=False: draft_answer(data, deep_research),
    description="Drafts a structured research summary based on research data. Supports deep research mode for detailed, research-paper-style summaries."
)