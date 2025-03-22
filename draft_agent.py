import os
import json
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.tools import StructuredTool
import requests
from openai import APIConnectionError
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from pydantic import BaseModel, Field  # Import Pydantic for schema definition
from urllib.parse import urlparse
from datetime import datetime

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

# Writing style templates
STYLE_TEMPLATES = {
    "academic": {
        "tone": "formal and scholarly",
        "vocabulary": "academic terminology and precise language",
        "structure": "rigorous academic structure with clear theoretical foundations"
    },
    "business": {
        "tone": "professional and action-oriented",
        "vocabulary": "business terminology and clear, direct language",
        "structure": "executive summary style with actionable insights"
    },
    "technical": {
        "tone": "precise and technical",
        "vocabulary": "technical terminology and specific technical concepts",
        "structure": "systematic technical documentation style"
    },
    "casual": {
        "tone": "conversational and accessible",
        "vocabulary": "clear, everyday language",
        "structure": "engaging and easy-to-follow format"
    }
}

# Citation formatting functions
def format_citation(item: Dict[str, Any], format_style: str) -> str:
    """Format citation according to specified style."""
    title = item.get('title', '')
    url = item.get('url', '')
    # Extract domain as publisher
    publisher = urlparse(url).netloc if url else "Unknown Publisher"
    # Extract date or use current
    date = datetime.now().strftime("%Y, %B %d")
    
    if format_style == "APA":
        return f"{title}. ({date}). Retrieved from {url}"
    elif format_style == "MLA":
        return f'"{title}." {publisher}, {date}, {url}'
    elif format_style == "IEEE":
        return f"[{hash(url) % 100 + 1}] {title}, {publisher}, {date}."
    return f"{title} - {url}"

def apply_writing_style(prompt: str, style: str) -> str:
    """Apply writing style to prompt template."""
    style_config = STYLE_TEMPLATES.get(style, STYLE_TEMPLATES["academic"])
    return prompt + f"\n\nUse a {style_config['tone']} tone with {style_config['vocabulary']}, following a {style_config['structure']}."

# Prompts for shallow research mode
def get_shallow_word_counts(target_word_count):
    """Distribute the target word count across sections in shallow mode."""
    intro = max(50, int(target_word_count * 0.25))  # 25%
    findings = max(75, int(target_word_count * 0.35))  # 35%
    analysis = max(50, int(target_word_count * 0.25))  # 25%
    conclusion = max(25, int(target_word_count * 0.15))  # 15%
    return intro, findings, analysis, conclusion

shallow_introduction_prompt = PromptTemplate(
    input_variables=["data", "word_count"],
    template="""
    Generate a concise introduction for a research summary based on the following data. Briefly introduce the topic and its significance in approximately {word_count} words, focusing on clarity and understanding with minimal context. Do not include the word "Introduction" in your response; only provide the content of the introduction section. Do not use Markdown formatting (e.g., **bold**) within the content; provide plain text only. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

shallow_key_findings_prompt = PromptTemplate(
    input_variables=["data", "word_count"],
    template="""
    Generate a concise key findings section for a research summary based on the following data. Summarize the main points in a numbered list (3-5 points, approximately {word_count} words total), focusing on clarity and understanding with minimal context. Each numbered point must be on a new line with a newline character (\n) between points (e.g., 1. First finding.\n2. Second finding.\n3. Third finding.). Ensure there is a space after each number and period (e.g., "1. " not "1."). Do not include the phrase "Key Findings" in your response; only provide the content of the key findings section. Do not use Markdown formatting (e.g., **bold**) within the content; provide plain text only. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

shallow_analysis_prompt = PromptTemplate(
    input_variables=["data", "word_count"],
    template="""
    Generate a concise analysis section for a research summary based on the following data. Structure your analysis exactly as follows, with each section clearly marked:

    [PARA1]
    Initial assessment (~75 words): Provide primary observations and immediate implications.
    [/PARA1]

    [PARA2]
    Detailed examination (~50 words): Explore key patterns and relationships.
    [/PARA2]

    [PARA3]
    Critical insights (~50 words): Discuss significant findings and their impact.
    [/PARA3]

    [PARA4]
    Future implications (~25 words): Brief outlook on potential developments.
    [/PARA4]

    Data: {data}
    """
)

shallow_conclusion_prompt = PromptTemplate(
    input_variables=["data", "word_count"],
    template="""
    Generate a concise conclusion section for a research summary based on the following data. Conclude with a short statement on potential future developments or recommendations in approximately {word_count} words, focusing on clarity and understanding with minimal context. Do not include the word "Conclusion" in your response; only provide the content of the conclusion section. Do not use Markdown formatting (e.g., **bold**) within the content; provide plain text only. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

# Prompts for each section in deep research mode
def get_deep_word_counts(target_word_count):
    """Distribute the target word count across sections in deep mode."""
    abstract = max(150, int(target_word_count * 0.05))  # 5%
    intro = max(400, int(target_word_count * 0.15))  # 15%
    lit_review = max(600, int(target_word_count * 0.20))  # 20%
    findings = max(800, int(target_word_count * 0.30))  # 30%
    analysis = max(800, int(target_word_count * 0.20))  # 20%
    conclusion = max(400, int(target_word_count * 0.10))  # 10%
    return abstract, intro, lit_review, findings, analysis, conclusion

abstract_prompt = PromptTemplate(
    input_variables=["data", "word_count"],
    template="""
    Generate a detailed abstract for a research paper based on the following data. Provide a comprehensive overview of the topic, research objectives, key findings, and their implications in approximately {word_count} words. Include a brief mention of the methodology and significance of the research. Provide detailed insights and avoid summarizing the data directly—focus on synthesizing the overall narrative. Do not include the word "Abstract" in your response; only provide the content of the abstract section. Do not use Markdown formatting (e.g., **bold**) within the content; provide plain text only. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

introduction_prompt = PromptTemplate(
    input_variables=["data", "word_count"],
    template="""
    Generate a detailed introduction for a research paper based on the following data. Introduce the topic in depth, covering its historical context, current significance, and the purpose of this research in approximately {word_count} words. Discuss its relevance in scientific, technological, or societal contexts, citing specific trends or events. Elaborate with examples, historical developments, and current challenges in the field. Do not include the word "Introduction" in your response; only provide the content of the introduction section. Do not use Markdown formatting (e.g., **bold**) within the content; provide plain text only. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

literature_review_prompt = PromptTemplate(
    input_variables=["data", "word_count"],
    template="""
    Generate a detailed literature review for a research paper based on the following data. Synthesize existing knowledge and findings from all provided sources in approximately {word_count} words. Highlight trends, gaps, controversies, and key developments in the field, providing a critical overview of the current state of research. Include specific references to studies or advancements mentioned in the data, and discuss their implications. Do not include the phrase "Literature Review" in your response; only provide the content of the literature review section. Do not use Markdown formatting (e.g., **bold**) within the content; provide plain text only. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

key_findings_prompt = PromptTemplate(
    input_variables=["data", "word_count"],
    template="""
    Generate a detailed key findings section for a research paper based on the following data. Summarize the main points in a numbered list (5-7 points, approximately {word_count} words total), including specific examples, data points, and insights from each source where applicable. Ensure comprehensive coverage of all relevant findings, discussing methodologies, results, and their significance. Each numbered point must be on a new line with a newline character (\n) between points (e.g., 1. First finding.\n2. Second finding.\n3. Third finding.). Ensure there is a space after each number and period (e.g., "1. " not "1."). Do not include the phrase "Key Findings" in your response; only provide the content of the key findings section. Do not use Markdown formatting (e.g., **bold**) within the content; provide plain text only. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

analysis_prompt = PromptTemplate(
    input_variables=["data", "word_count"],
    template="""
    Generate a detailed analysis section for a research paper based on the following data. Provide in-depth insights, implications, and critical analysis of the findings in approximately {word_count} words. Discuss broader impacts, potential applications, limitations, challenges, and areas of uncertainty, integrating perspectives from the data. Compare and contrast findings, and propose hypotheses for future exploration. Elaborate extensively with examples and potential scenarios. Do not include the word "Analysis" in your response; only provide the content of the analysis section. Do not use Markdown formatting (e.g., **bold**) within the content; provide plain text only. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

    Data: {data}
    """
)

conclusion_prompt = PromptTemplate(
    input_variables=["data", "word_count"],
    template="""
    Generate a detailed conclusion section for a research paper based on the following data. Provide a thorough summary of findings, their significance, and potential future developments in approximately {word_count} words. Offer detailed recommendations for further research, addressing how the findings contribute to the field and what steps should be taken next. Discuss long-term implications and future directions. Do not include the word "Conclusion" in your response; only provide the content of the conclusion section. Do not use Markdown formatting (e.g., **bold**) within the content; provide plain text only. Do not include any internal reasoning tags like <think> or similar markers in your response; only provide the final content.

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
    text = re.sub(r"\s+", " ", text.strip())
    points = re.split(r"(?=\d+\.\s?)", text)
    formatted_text = ""
    for point in points:
        point = point.strip()
        if point:
            point = re.sub(r"^(\d+\.)([^\s])", r"\1 \2", point)
            formatted_text += point + "\n"
    formatted_text = formatted_text.strip()
    formatted_text = re.sub(r"\n{2,}", "\n", formatted_text)
    return formatted_text

# Function to generate a section (for parallel processing)
def generate_section(section_name, section_prompt, data_str, word_count):
    """Generate a single section using the LLM."""
    try:
        formatted_prompt = section_prompt.format(data=data_str, word_count=word_count)
        messages = [{"role": "user", "content": formatted_prompt}]
        response = llm.invoke(messages)
        section_text = clean_think_tags(response.content.strip())
        if section_name == "Key Findings":
            section_text = format_key_findings(section_text)
        return section_name, section_text
    except Exception as e:
        logging.error(f"Error generating section {section_name}: {str(e)}")
        return section_name, f"Error generating section: {str(e)}"

# Define the schema for StructuredTool arguments using Pydantic
class DraftAnswerArgs(BaseModel):
    data: List[Dict[str, Any]] = Field(description="List of research data dictionaries containing title, content, and url")
    deep_research: bool = Field(default=False, description="Whether to perform deep research mode (detailed summary)")
    target_word_count: int = Field(default=1000, description="Target word count for the summary")
    writing_style: str = Field(default="academic", description="Writing style for the summary")
    citation_format: str = Field(default="APA", description="Citation format for references")
    language: str = Field(default="english", description="Language for the summary")
    retries: int = Field(default=3, description="Number of retries for API calls")
    delay: int = Field(default=5, description="Delay between retries in seconds")

STYLE_PROMPTS = {
    "academic": """Write in a formal academic style with:
        - Scholarly terminology and precise language
        - Clear theoretical foundations
        - Objective analysis
        - Proper citations and references""",
    
    "business": """Write in a professional business style with:
        - Executive summary approach
        - Action-oriented insights
        - Clear ROI and business implications
        - Professional but accessible language""",
    
    "technical": """Write in a technical style with:
        - Detailed technical specifications
        - Step-by-step explanations
        - Technical terminology
        - Data-driven insights""",
    
    "casual": """Write in an accessible, casual style with:
        - Clear, everyday language
        - Engaging examples
        - Conversational tone
        - Relatable explanations"""
}

LANGUAGE_PROMPTS = {
    "english": """Write in standard academic English following international research paper standards:
        - Use British/American English consistently
        - Follow academic writing conventions
        - Maintain formal scholarly tone""",
    
    "spanish": """Escriba en español académico siguiendo los estándares internacionales de investigación:
        - Use español académico estándar
        - Siga las convenciones académicas españolas
        - Mantenga un tono académico formal""",
    
    "french": """Rédigez en français académique selon les normes internationales de recherche:
        - Utilisez le français académique standard
        - Suivez les conventions académiques françaises
        - Maintenez un ton académique formel""",
    
    "german": """Schreiben Sie in akademischem Deutsch nach internationalen Forschungsstandards:
        - Verwenden Sie Standard-Wissenschaftsdeutsch
        - Folgen Sie deutschen akademischen Konventionen
        - Halten Sie einen formellen akademischen Ton""",
    
    "chinese": """按照国际研究论文标准使用学术中文写作：
        - 使用规范的学术中文
        - 遵循中文学术写作规范
        - 保持正式的学术语气""",
}

def format_citation(source: Dict[str, str], style: str) -> str:
    """Format citation based on selected style."""
    title = source.get('title', '')
    url = source.get('url', '')
    date = datetime.now().strftime("%Y, %B %d")
    domain = urlparse(url).netloc

    citations = {
        "APA": f"{title}. ({date}). Retrieved from {url}",
        "MLA": f'"{title}." {domain}. {date}. Web.',
        "IEEE": f"[{hash(url) % 100 + 1}] {title}. {domain}. {date}.",
    }
    
    return citations.get(style, citations["APA"])

# Drafting function with retry logic and deep research support
def draft_answer(
    data: List[Dict[str, Any]], 
    deep_research: bool = False, 
    target_word_count: int = 1000,
    writing_style: str = "academic",
    citation_format: str = "APA",
    language: str = "english",
    retries: int = 3, 
    delay: int = 5
) -> str:
    """Enhanced draft function with style, citations, and language support."""
    if not data:
        return "Error drafting response: No research data provided"

    attempt = 0
    while attempt < retries:
        try:
            data_str = json.dumps(data)
            
            # Add citations to data
            citations = [format_citation(item, citation_format) for item in data]
            data_with_citations = {
                "content": data_str,
                "citations": citations,
                "style": writing_style,
                "language": language
            }

            # Modify prompts with style and language
            if not deep_research:
                sections = [
                    ("Key Findings", apply_writing_style(key_findings_prompt.template, writing_style)),
                    ("Analysis", apply_writing_style(analysis_prompt.template, writing_style))
                ]
            else:
                sections = [
                    ("Abstract", apply_writing_style(abstract_prompt.template, writing_style)),
                    ("Introduction", apply_writing_style(introduction_prompt.template, writing_style)),
                    ("Literature Review", apply_writing_style(literature_review_prompt.template, writing_style)),
                    ("Key Findings", apply_writing_style(key_findings_prompt.template, writing_style)),
                    ("Analysis", apply_writing_style(analysis_prompt.template, writing_style)),
                    ("Conclusion", apply_writing_style(conclusion_prompt.template, writing_style))
                ]

            # Add language instruction to system message
            system_message = f"Please provide the response in {language}. "
            system_message += f"Use {citation_format} citation format when referencing sources."

            response_text = ""
            for section_name, prompt_template in sections:
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt_template.format(
                        data=json.dumps(data_with_citations),
                        word_count=target_word_count // len(sections)
                    )}
                ]
                
                response = llm.invoke(messages)
                section_text = clean_think_tags(response.content.strip())
                
                if section_name == "Key Findings":
                    section_text = format_key_findings(section_text)
                
                response_text += f"\n\n**{section_name}**\n\n{section_text}"

            # Add References section
            response_text += "\n\n**References**\n\n"
            response_text += "\n".join(citations)

            return response_text

        except Exception as e:
            attempt += 1
            if attempt < retries:
                time.sleep(delay)
                continue
            return f"Error drafting response: {type(e).__name__} - {str(e)}"
    
    return "Error drafting response: Max retries exceeded."

# Define the tool with support for deep research and target word count using StructuredTool
draft_tool = StructuredTool.from_function(
    func=draft_answer,
    name="DraftAnswer",
    description="Drafts a structured research summary based on research data. Supports deep research mode for detailed summaries and customizable word count.",
    args_schema=DraftAnswerArgs
)
