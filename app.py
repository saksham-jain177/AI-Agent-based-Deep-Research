import streamlit as st
from main import run_research  # Import run_research from main.py
from draft_agent import format_citation, STYLE_TEMPLATES  # Add this import
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
import io
import json
import html
import requests
import datetime
import logging
import re
import os
import time
from dotenv import load_dotenv
from docx import Document
from docx.shared import Pt, Inches

# Set up logging
logging.basicConfig(filename="research_agent.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize all session state variables at the top
if "research_data" not in st.session_state:
    st.session_state.research_data = None
if "response" not in st.session_state:
    st.session_state.response = None
if "pdf_buffer" not in st.session_state:
    st.session_state.pdf_buffer = None
if "word_buffer" not in st.session_state:
    st.session_state.word_buffer = None
if "writing_style" not in st.session_state:
    st.session_state.writing_style = "Academic"
if "language" not in st.session_state:
    st.session_state.language = "English"
if "citation_format" not in st.session_state:
    st.session_state.citation_format = "APA"
if "target_word_count" not in st.session_state:
    st.session_state.target_word_count = 1000  # Default value

# Inject custom CSS for improved readability and aesthetics
st.markdown("""
    <style>
    /* Base styling - Futuristic Dark Theme */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.6;
    }
    
    /* Typography */
    h1 {
        color: #58a6ff;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 1.5rem;
        padding-bottom: 0.6rem; /* Removed bottom border to avoid double line */
        text-shadow: 0 0 15px rgba(88, 166, 255, 0.5);
    }
    
    h2 {
        color: #79c0ff;
        font-size: 1.8rem;
        font-weight: 600;
        margin-top: 1.8rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #a5d6ff;
        font-size: 1.4rem;
        font-weight: 500;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }
    
    p, li {
        font-size: 1rem;
        color: #c9d1d9;
        line-height: 1.7;
    }
    
    /* Text input styling */
    .stTextInput > div > input {
        background-color: #161b22;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 8px;
        box-shadow: 0 0 5px rgba(31, 111, 235, 0.2);
        padding: 12px 16px;
        font-size: 1rem;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > input:focus {
        border-color: #1f6feb;
        box-shadow: 0 0 10px rgba(31, 111, 235, 0.4);
        outline: none;
    }
    
    /* Button styling (for Download 📥 button) */
    .stButton > button {
        background: linear-gradient(45deg, #155e75, #0ea5e9);
        color: white;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(14, 165, 233, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(14, 165, 233, 0.6);
        transform: none; /* No growth/shift on hover */
    }
    
    .stButton > button:active {
        transform: translateY(1px);
        box-shadow: 0 0 10px rgba(14, 165, 233, 0.3);
    }

    /* Disabled button state: no hover animation, muted style */
    .stButton > button:disabled {
        background: #2d3748 !important;
        color: #a0aec0 !important;
        box-shadow: none !important;
        transform: none !important;
        cursor: not-allowed !important;
        opacity: 0.7 !important;
        pointer-events: none !important;
    }
    
    .stButton > button::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: rgba(255, 255, 255, 0.1);
        transform: rotate(30deg);
        transition: transform 0.3s ease;
    }
    
    .stButton > button:hover::after {
        transform: rotate(30deg) translate(-10%, -10%);
    }
    
    /* Download button styling (for Downloading PDF... 📄 button) */
    .stDownloadButton > button {
        background: linear-gradient(45deg, #065f46, #0ea5e9);
        color: white;
        font-weight: 600;
        padding: 0.7rem 2rem;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(14, 165, 233, 0.5);
        position: relative;
        overflow: hidden;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 0 25px rgba(14, 165, 233, 0.7);
        transform: translateY(-2px) scale(1.05);
        background: linear-gradient(45deg, #0ea5e9, #065f46);
    }
    
    .stDownloadButton > button:active {
        transform: translateY(1px) scale(0.98);
        box-shadow: 0 0 10px rgba(14, 165, 233, 0.3);
    }
    
    .stDownloadButton > button::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: rgba(255, 255, 255, 0.1);
        transform: rotate(30deg);
        transition: transform 0.3s ease;
    }
    
    .stDownloadButton > button:hover::after {
        transform: rotate(30deg) translate(-10%, -10%);
    }
    
    /* Custom Selectbox styling */
    .custom-select-wrapper {
        position: relative;
        width: 100%;
        font-size: 1rem;
    }
    
    .custom-select {
        background: linear-gradient(45deg, #065f46, #0ea5e9);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 10px;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(14, 165, 233, 0.3);
        width: 100%;
        cursor: pointer;
        appearance: none;
        -webkit-appearance: none;
        -moz-appearance: none;
    }
    
    .custom-select:hover {
        box-shadow: 0 0 15px rgba(14, 165, 233, 0.5);
        transform: translateY(-2px) scale(1.02);
        background: linear-gradient(45deg, #0ea5e9, #065f46);
    }
    
    .custom-select:focus {
        outline: none;
        box-shadow: 0 0 15px rgba(14, 165, 233, 0.5);
    }
    
    /* Custom arrow for the dropdown */
    .custom-select-wrapper::after {
        content: '\\25BC'; /* Unicode for down arrow */
        position: absolute;
        right: 15px;
        top: 50%;
        transform: translateY(-50%);
        color: white;
        font-size: 1rem;
        pointer-events: none;
    }
    
    /* Dropdown menu styling */
    .custom-select option {
        background: #161b22;
        color: #ffffff;
        font-weight: 500;
        border: 1px solid #1f6feb;
        border-radius: 8px;
        box-shadow: 0 0 5px rgba(14, 165, 233, 0.2);
        padding: 10px;
    }
    
    .custom-select option:hover {
        background: linear-gradient(45deg, #0ea5e9, #065f46);
        color: white;
        box-shadow: 0 0 10px rgba(14, 165, 233, 0.3);
    }
    
    /* Hide the default st.selectbox */
    .stSelectbox {
        display: none !important;
    }
    
    /* Sidebar styling */
    .stSidebar {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    .stSidebar .stMarkdown {
        color: #c9d1d9 !important;
    }
    
    .stSidebar h2 {
        color: #58a6ff;
        font-size: 1.4rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #30363d;
        text-shadow: 0 0 10px rgba(88, 166, 255, 0.3);
    }
    
    /* Status indicators in sidebar */
    .stSidebar .stSuccess {
        background: linear-gradient(90deg, #033a2c, #065f46) !important;
        color: #ecfdf5 !important;
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: 500;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        box-shadow: 0 0 10px rgba(6, 95, 70, 0.4);
        border-left: 3px solid #10b981;
    }
    
    .stSidebar .stError {
        background: linear-gradient(90deg, #770b0b, #9a1515) !important;
        color: #fee2e2 !important;
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: 500;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        box-shadow: 0 0 10px rgba(185, 28, 28, 0.4);
        border-left: 3px solid #ef4444;
    }
    
    /* JSON/Code block styling */
    .stCodeBlock {
        background-color: #0d1117;
        color: #c9d1d9;
        border-radius: 8px;
        padding: 1.2rem;
        font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
        font-size: 0.9rem;
        line-height: 1.6;
        overflow-x: auto;
        border: 1px solid #30363d;
        box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.2);
    }
    
    /* Progress bar - keep Streamlit defaults for correct fill behavior */
    .stProgress > div > div { height: 0.6rem !important; border-radius: 1rem; }
    .stProgress > div > div > div { border-radius: 1rem; }
    
    /* Notification messages */
    .stSuccess {
        background-color: rgba(6, 95, 70, 0.2) !important;
        color: #34d399 !important;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
        font-size: 1rem;
        box-shadow: 0 0 10px rgba(6, 95, 70, 0.2);
    }
    
    .stInfo {
        background-color: rgba(37, 99, 235, 0.2) !important;
        color: #93c5fd !important;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
        font-size: 1rem;
        box-shadow: 0 0 10px rgba(37, 99, 235, 0.2);
    }
    
    .stWarning {
        background-color: rgba(217, 119, 6, 0.2) !important;
        color: #fbbf24 !important;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
        font-size: 1rem;
        box-shadow: 0 0 10px rgba(217, 119, 6, 0.2);
    }
    
    .stError {
        background-color: rgba(185, 28, 28, 0.2) !important;
        color: #f87171 !important;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ef4444;
        margin: 1rem 0;
        font-size: 1rem;
        box-shadow: 0 0 10px rgba(185, 28, 28, 0.2);
    }
    
    /* JSON display */
    .stJson {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 1rem 0;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Download button container */
    .download-btn-container {
        margin-top: 1rem;
        text-align: center;
    }
    
    /* Format description */
    .format-description {
        margin-top: 0.5rem;
        font-size: 0.9rem;
        color: #a5d6ff;
        text-align: center;
        transition: opacity 0.3s ease;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #0ea5e9 !important;
        border-bottom-color: transparent !important;
        filter: drop-shadow(0 0 8px rgba(14, 165, 233, 0.6));
    }
    
    /* Feedback textarea */
    .stTextArea > div > textarea {
        background-color: #161b22;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px;
        font-size: 0.9rem;
        line-height: 1.5;
        resize: vertical;
        box-shadow: 0 0 5px rgba(31, 111, 235, 0.2);
    }
    
    .stTextArea > div > textarea:focus {
        border-color: #1f6feb;
        box-shadow: 0 0 10px rgba(31, 111, 235, 0.4);
        outline: none;
    }
    
    /* General spacing and containers */
    .main .block-container {
        padding: 2rem 1.5rem;
        max-width: 960px;
    }
    
    .stMarkdown {
        margin-bottom: 1.5rem;
    }
    
    /* Custom glowing effects and futuristic touches */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at top right, rgba(14, 165, 233, 0.05), transparent 60%);
        pointer-events: none;
        z-index: -1;
    }
    
    /* Title underline animation */
    h1::after {
        content: '';
        display: block;
        position: absolute;
        height: 2px;
        width: 0;
        bottom: 0;
        left: 0;
        background: linear-gradient(90deg, #0ea5e9, transparent);
        transition: width 0.5s ease;
    }
    
    h1:hover::after {
        width: 100%;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0d1117;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #30363d;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #58a6ff;
    }
    </style>
""", unsafe_allow_html=True)

# Function to check OpenRouter status
def check_openrouter_status():
    """Check if OpenRouter API is operational."""
    try:
        response = requests.get("https://openrouter.ai/api/v1/models", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logging.error(f"Failed to check OpenRouter status: {str(e)}")
        return False

# Function to add page numbers to the PDF
def on_page(canvas, doc):
    page_num = canvas.getPageNumber()
    text = f"Page {page_num}"
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(doc.rightMargin + doc.width, doc.bottomMargin - 10, text)
    canvas.restoreState()

def format_reference_for_pdf(ref_text):
    """Format a single reference for PDF."""
    # Extract date and URL using regex
    date_match = re.search(r'\(([0-9]{4},\s*[^)]+)\)', ref_text)
    url_match = re.search(r'Retrieved from\s+(https?://\S+)', ref_text)
    
    if date_match and url_match:
        date = date_match.group(1)
        url = url_match.group(1)
        return f"({date}). Retrieved from {url}"
    return ref_text

def preprocess_references(refs_section):
    """Preprocess references to ensure proper formatting."""
    # Split references by looking for date pattern and "Retrieved from"
    pattern = r'(?=\([0-9]{4},.*?\).*?Retrieved from)'
    refs = re.split(pattern, refs_section)
    # Clean up each reference
    refs = [ref.strip() for ref in refs if ref.strip()]
    
    formatted_refs = []
    for i, ref in enumerate(refs, 1):
        # Split URL if it's broken across lines
        ref = re.sub(r'(?<=https?://\S+)-\s*\n\s*(?=\S+)', '', ref)
        # Remove any "Page X" artifacts
        ref = re.sub(r'Page \d+\s*', '', ref)
        # Clean up extra whitespace
        ref = ' '.join(ref.split())
        formatted_ref = format_reference_for_pdf(ref, i)
        formatted_refs.append(formatted_ref)
    
    return formatted_refs

def format_references_section(refs_text):
    """Format references by adding line breaks after URLs."""
    # Split by "Retrieved from" to separate different references
    refs = refs_text.split("Retrieved from")
    formatted_refs = []
    
    for i, ref in enumerate(refs):
        if i == 0:  # First part might be empty
            continue
            
        # Find the URL pattern
        url_match = re.search(r'(https?://\S+)', ref)
        if url_match:
            url = url_match.group(1)
            # Get the text before the URL (title part)
            title_part = ref[:url_match.start()].strip()
            if i > 0 and formatted_refs:  # Add the previous title
                formatted_refs[-1] += f"Retrieved from {url}\n\n"
            formatted_refs.append(title_part)
    
    # Handle the last URL
    if formatted_refs and url_match:
        formatted_refs[-1] += f"Retrieved from {url}\n\n"
    
    return "".join(formatted_refs)

# Function to generate PDF with proper formatting and cover page
def generate_pdf(query, data, summary, deep_research=False):
    """Generate a PDF report with query, data, and summary in a research paper format."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=72,
        bottomMargin=72,
        leftMargin=72,
        rightMargin=72
    )
    styles = getSampleStyleSheet()

    # Customize styles for a research paper look
    styles['Title'].fontSize = 16
    styles['Title'].spaceAfter = 12
    styles['Heading2'].fontSize = 14
    styles['Heading2'].spaceAfter = 6
    styles['Heading3'].fontSize = 12
    styles['Heading3'].spaceAfter = 6
    styles['BodyText'].fontSize = 10
    styles['BodyText'].leading = 14
    styles['BodyText'].spaceAfter = 12

    # Add a custom style for references
    styles.add(ParagraphStyle(
        name='Reference',
        parent=styles['BodyText'],
        fontSize=10,
        leftIndent=36,
        firstLineIndent=-36,
        spaceAfter=12
    ))

    story = []

    # Cover Page
    story.append(Paragraph("Deep Research AI Agent Report", styles['Title']))
    story.append(Spacer(1, 24))
    story.append(Paragraph(f"Query: {query}", styles['Normal']))
    story.append(Paragraph(f"Date: {datetime.date.today().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Paragraph(f"Author: [Your Name]", styles['Normal']))
    story.append(Spacer(1, 48))

    # Metadata
    story.append(Paragraph(f"OpenRouter Status: {'Operational' if check_openrouter_status() else 'Down'}", styles['Normal']))
    story.append(Spacer(1, 12))
    mode = "Deep Research" if deep_research else "Quick Research"
    story.append(Paragraph(f"Mode: {mode}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Research Summary Section
    story.append(Paragraph("Research Summary", styles['Heading2']))
    story.append(Spacer(1, 12))

    # Add research data summary
    for item in data:
        story.append(Paragraph(f"• {item['title']}", styles['Heading3']))
        story.append(Paragraph(item['content'], styles['BodyText']))
        story.append(Spacer(1, 12))

    # Process the content sections
    sections = summary.split("\n\n")
    references = []
    current_heading = None
    
    for section in sections:
        if section.startswith("**") and section.endswith("**"):
            current_heading = section.strip("**").rstrip(":")
            if current_heading == "References":
                continue
            story.append(Paragraph(current_heading, styles['Heading2']))
            story.append(Spacer(1, 12))
        else:
            if current_heading == "References":
                # Collect references for later processing
                refs = section.split("\n")
                for ref in refs:
                    if ref.strip():
                        references.append(ref.strip())
            elif current_heading:
                if current_heading == "Analysis":
                    # Split into smaller paragraphs for readability
                    sentences = re.split(r'(?<=[.!?])\s+', section)
                    new_paragraphs = []
                    current_paragraph = []
                    sentence_count = 0
                    
                    max_sentences = 4 if len(sentences) < 15 else 6
                    
                    for sentence in sentences:
                        current_paragraph.append(sentence)
                        sentence_count += 1
                        if sentence_count >= max_sentences:
                            new_paragraphs.append(' '.join(current_paragraph))
                            current_paragraph = []
                            sentence_count = 0
                    
                    if current_paragraph:
                        new_paragraphs.append(' '.join(current_paragraph))
                    
                    for paragraph in new_paragraphs:
                        if paragraph.strip():
                            story.append(Paragraph(paragraph.strip(), styles['BodyText']))
                            story.append(Spacer(1, 12))
                elif current_heading == "Key Findings":
                    findings = re.split(r'(?=\d+\.)', section)
                    for finding in findings:
                        if finding.strip():
                            story.append(Paragraph(finding.strip(), styles['BodyText']))
                            story.append(Spacer(1, 6))
                else:
                    formatted_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", section)
                    formatted_text = formatted_text.replace("**", "")
                    story.append(Paragraph(formatted_text, styles['BodyText']))
                    story.append(Spacer(1, 12))

    # Add References section at the end
    if references:
        story.append(Paragraph("References", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        for i, ref in enumerate(references, 1):
            formatted_ref = format_reference_for_pdf(ref)
            if formatted_ref:
                ref_para = Paragraph(
                    f"{i}. {formatted_ref}",
                    styles['Reference']
                )
                story.append(ref_para)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buffer.seek(0)
    return buffer

# Function to generate Word document
def generate_docx(query, data, summary, deep_research=False):
    """Generate a Word document with query, data, and summary."""
    doc = Document()
    doc.add_heading("Deep Research AI Agent Report", 0)
    doc.add_paragraph(f"Query: {query}")
    doc.add_paragraph(f"Date: {datetime.date.today().strftime('%B %d, %Y')}")
    doc.add_paragraph(f"Author: [Your Name]")
    doc.add_paragraph(f"OpenRouter Status: {'Operational' if check_openrouter_status() else 'Down'}")
    doc.add_paragraph(f"Mode: {'Deep Research' if deep_research else 'Quick Research'}")
    
    # Research Summary Section
    doc.add_heading("Research Summary", level=1)
    for item in data:
        p = doc.add_paragraph()
        p.add_run(f"• {item['title']}").bold = True
        doc.add_paragraph(item['content'])
        doc.add_paragraph(f"Source: {item['url']}")
        doc.add_paragraph()  # Add spacing

    # Process other sections
    sections = summary.split("\n\n")
    current_heading = None
    references = []
    
    for section in sections:
        if section.startswith("**") and section.endswith("**"):
            current_heading = section.strip("**").rstrip(":")
            if current_heading != "References":
                doc.add_heading(current_heading, level=2)
        else:
            if current_heading == "References":
                # Collect references for later processing
                refs = section.split("\n")
                for ref in refs:
                    if ref.strip():
                        references.append(ref.strip())
            elif current_heading == "Analysis":
                # Split into smaller paragraphs for readability
                sentences = re.split(r'(?<=[.!?])\s+', section)
                new_paragraphs = []
                current_paragraph = []
                sentence_count = 0
                
                max_sentences = 4 if len(sentences) < 15 else 6
                
                for sentence in sentences:
                    current_paragraph.append(sentence)
                    sentence_count += 1
                    if sentence_count >= max_sentences:
                        new_paragraphs.append(' '.join(current_paragraph))
                        current_paragraph = []
                        sentence_count = 0
                
                if current_paragraph:
                    new_paragraphs.append(' '.join(current_paragraph))
                
                for paragraph in new_paragraphs:
                    if paragraph.strip():
                        p = doc.add_paragraph(paragraph.strip())
                        p.paragraph_format.space_after = Pt(12)
            elif current_heading == "Key Findings":
                findings = re.split(r'(?=\d+\.)', section)
                for finding in findings:
                    if finding.strip():
                        p = doc.add_paragraph(finding.strip())
                        p.paragraph_format.space_after = Pt(6)
            else:
                formatted_text = re.sub(r"\*\*(.*?)\*\*", r"\1", section)
                p = doc.add_paragraph(formatted_text)
                p.paragraph_format.space_after = Pt(12)

    # Add References section at the end
    if references:
        doc.add_heading("References", level=2)
        
        for i, ref in enumerate(references, 1):
            formatted_ref = format_reference_for_pdf(ref)
            if formatted_ref:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.5)
                p.paragraph_format.first_line_indent = Inches(-0.5)
                p.paragraph_format.space_after = Pt(12)
                p.add_run(f"{i}. {formatted_ref}")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Streamlit app setup
st.title("Deep Research AI Agent")
st.write("Enter a query to research and get a detailed response using Tavily and OpenRouter.")

# Load .env dynamically on each run to reflect external changes
try:
    load_dotenv(override=True)
except Exception:
    pass

# Sidebar: Status and Info
st.sidebar.header("OpenRouter Status")
if check_openrouter_status():
    st.sidebar.success("Operational", icon="✅")
else:
    st.sidebar.error("Down", icon="❌")

st.sidebar.header("About")
st.sidebar.write("Dual-agent system using Tavily for research and OpenRouter for drafting with the model of your choosing.")
st.sidebar.write("Built with LangChain, LangGraph, and Streamlit.")
def _fix_readability(text: str) -> str:
    if not isinstance(text, str):
        return ""
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    # Ensure a space after punctuation if followed by a letter (keep newlines)
    t = re.sub(r"([\.,;:])(?![\s\n])(?!$)(?=[A-Za-z])", r"\1 ", t)
    # Insert a space between ALL-CAPS token and following lowercase (avoid newlines)
    t = re.sub(r"\b([A-Z]{2,})([a-z])", r"\1 \2", t)
    # Insert a space between a closing alpha and opening parenthesis if missing
    t = re.sub(r"([A-Za-z])\(", r"\1 (", t)
    return t

def _render_small_text(text: str):
    t = _fix_readability(text)
    safe = html.escape(t)
    # Preserve paragraphs: split on blank lines
    parts = [p.strip() for p in safe.split("\n\n") if p.strip()]
    if not parts:
        st.markdown(f"<div style='font-size:0.95rem; line-height:1.7;'>{safe}</div>", unsafe_allow_html=True)
        return
    html_blocks = []
    for p in parts:
        p_clean = p.replace("\n", " ")
        html_blocks.append(f"<p style='margin:0 0 0.75rem 0;'>{p_clean}</p>")
    st.markdown("".join(html_blocks), unsafe_allow_html=True)


# API Keys gate & configuration
def _missing_api_keys():
    missing = []
    tav = os.getenv("TAVILY_API_KEY")
    router = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not tav:
        missing.append("TAVILY_API_KEY")
    if not router:
        missing.append("OPENROUTER_API_KEY or OPENAI_API_KEY")
    return missing

@st.cache_data(ttl=300, show_spinner=False)
def _validate_openrouter_key(key: str) -> bool:
    try:
        if not key:
            return False
        headers = {"Authorization": f"Bearer {key}"}
        r = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=10)
        return r.status_code == 200
    except Exception:
        return False

@st.cache_data(ttl=300, show_spinner=False)
def _validate_tavily_key(key: str) -> bool:
    try:
        if not key:
            return False
        from tavily import TavilyClient
        client = TavilyClient(api_key=key)
        # Minimal request; if unauthorized will raise
        client.search("ping", max_results=1)
        return True
    except Exception:
        return False

def _persist_keys_to_env(env_updates: dict) -> bool:
    try:
        current = {}
        if os.path.exists(".env"):
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        k, v = line.split("=", 1)
                        current[k.strip()] = v
        for k, v in env_updates.items():
            if v:
                current[k] = f"{k}={v}\n"
        with open(".env", "w", encoding="utf-8") as f:
            for _, line in current.items():
                f.write(line)
        return True
    except Exception as e:
        st.sidebar.error(f"Failed to write .env: {e}")
        return False

missing_keys = _missing_api_keys()

st.sidebar.header("API Keys")
if missing_keys:
    st.sidebar.warning("Missing: " + ", ".join(missing_keys))
    with st.sidebar.expander("Add API Keys", expanded=True):
        tavily = st.text_input("TAVILY_API_KEY", type="password", key="tavily_key_input")
        router = st.text_input("OPENROUTER_API_KEY or OPENAI_API_KEY", type="password", key="router_key_input")
        persist = st.checkbox("Save to .env", value=False, key="persist_keys_checkbox")
        if st.button("Save API Keys", key="save_keys_btn"):
            if tavily:
                os.environ["TAVILY_API_KEY"] = tavily
            if router:
                # Prefer OpenRouter key name; user can alternatively use OPENAI_API_KEY
                os.environ.setdefault("OPENAI_BASE_URL", os.getenv("OPENAI_BASE_URL") or "https://openrouter.ai/api/v1")
                os.environ["OPENROUTER_API_KEY"] = router
            if persist:
                updates = {}
                if tavily:
                    updates["TAVILY_API_KEY"] = tavily
                if router:
                    updates["OPENROUTER_API_KEY"] = router
                    updates.setdefault("OPENAI_BASE_URL", os.getenv("OPENAI_BASE_URL") or "https://openrouter.ai/api/v1")
                if _persist_keys_to_env(updates):
                    st.success("Saved to .env. Please rerun.")
            st.success("API keys saved for this session.")
            # Safe rerun across Streamlit versions
            try:
                st.rerun()
            except Exception:
                try:
                    st.experimental_rerun()
                except Exception:
                    pass
else:
    # Validate keys actually work against providers
    tav_ok = _validate_tavily_key(os.getenv("TAVILY_API_KEY",""))
    or_ok = _validate_openrouter_key(os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY",""))
    if tav_ok and or_ok:
        st.sidebar.success("All required API keys detected.")
    else:
        st.sidebar.warning("API keys present but failed validation. Please re-enter.")
        if st.sidebar.button("Clear session API keys"):
            for k in ["TAVILY_API_KEY","OPENROUTER_API_KEY","OPENAI_API_KEY"]:
                if k in os.environ:
                    os.environ.pop(k)
            try:
                st.rerun()
            except Exception:
                pass

# -------- OpenRouter model selection (dynamic fetch with fallback) --------
@st.cache_data(ttl=600, show_spinner=False)
def fetch_openrouter_models(api_key: str | None) -> list:
    try:
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        resp = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=15)
        if resp.status_code != 200:
            return []
        payload = resp.json()
        data = payload.get("data") or payload.get("models") or []
        models = []
        for m in data:
            mid = m.get("id") or m.get("name")
            if not mid:
                continue
            # Treat models marked ":free" or with zero pricing as free
            pricing = (m.get("pricing") or {})
            is_free = (":free" in mid) or all((not v or str(v).strip() in ("0", "0.0", "0.0000")) for v in pricing.values())
            # Attempt to capture context length from available fields
            ctx = m.get("context_length") or m.get("context")
            if not ctx:
                top = m.get("top_provider") or {}
                ctx = top.get("context_length") or top.get("context")
            models.append({"id": mid, "free": is_free, "context": ctx, "pricing": pricing})
        return models
    except Exception:
        return []

DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL") or "x-ai/grok-4-fast:free"
api_key_present = os.getenv("OPENROUTER_API_KEY")
all_models = fetch_openrouter_models(api_key_present)
free_models_meta = [m for m in all_models if m.get("free")]
free_models = [m["id"] for m in free_models_meta]
if not free_models:
    # Fallback curated set
    free_models_meta = [
        {"id": "x-ai/grok-4-fast:free", "free": True, "context": 2_000_000},
        {"id": "deepseek/deepseek-r1:free", "free": True, "context": None},
        {"id": "deepseek/deepseek-v3:free", "free": True, "context": None},
        {"id": "qwen/qwen2.5-7b-instruct:free", "free": True, "context": None},
    ]
    free_models = [m["id"] for m in free_models_meta]

st.sidebar.header("Model")
selected_model = st.sidebar.selectbox("OpenRouter model (free preferred)", free_models, index=(free_models.index(DEFAULT_MODEL) if DEFAULT_MODEL in free_models else 0))
os.environ["OPENROUTER_MODEL"] = selected_model

# Quick micro-benchmark for latency/throughput
@st.cache_data(ttl=900, show_spinner=False)
def benchmark_model(model_id: str, max_new_tokens: int = 64) -> dict | None:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Deep Research AI Agent"
    }
    body = {
        "model": model_id,
        "stream": True,
        "messages": [{"role": "user", "content": "Write a short sentence (~64 tokens)."}],
        "max_tokens": max_new_tokens,
        "temperature": 0.2
    }
    t0 = time.perf_counter()
    try:
        with requests.post(url, headers=headers, json=body, stream=True, timeout=60) as r:
            r.raise_for_status()
            ttfb = None
            token_chunks = 0
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if not ttfb:
                    ttfb = time.perf_counter() - t0
                token_chunks += 1
        total = time.perf_counter() - t0
        throughput = token_chunks / max(total - (ttfb or 0), 1e-6)
        return {"latency_s": round(ttfb or total, 3), "throughput_tps": round(throughput, 1), "chunks": token_chunks}
    except Exception:
        return None

# Show model metrics UI
meta_map = {m["id"]: m for m in free_models_meta}
ctx_len = meta_map.get(selected_model, {}).get("context")
bench = None
if st.sidebar.button("Benchmark model", help="Measures time to first token and tokens/sec (short run)."):
    bench = benchmark_model(selected_model)
if bench:
    st.sidebar.metric("Latency", f"{bench['latency_s']} s")
    st.sidebar.metric("Throughput", f"{bench['throughput_tps']} tkn/s")
elif ctx_len:
    st.sidebar.caption(f"Context: {ctx_len:,} tokens (reported)")
else:
    # If user clicked but benchmark failed
    if 'bench' in locals() and bench is None and api_key_present:
        st.sidebar.error("Benchmark failed (model/provider refused or network error). Try again or choose another model.")

# User input with Deep Research toggle
query = st.text_input("Research Query", "Latest advancements in quantum computing")
deep_research = st.checkbox("Deep Research Mode", value=False, help="Enable for a detailed, research-paper-style summary (5-6+ pages).")

# Research Settings Header
st.markdown("""
    <h2 style='color: #79c0ff; font-size: 1.8rem; font-weight: 600; margin-top: 1.8rem; margin-bottom: 1rem;'>
        🛠️ Research Settings
    </h2>
""", unsafe_allow_html=True)

# Create three columns for better organization
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Writing Style")
    writing_style = st.radio(
        "Select writing style",
        options=["Academic", "Business", "Technical", "Casual"],
        index=0,
        key="writing_style_radio",
        help="Choose the tone and style of your research"
    )

with col2:
    st.markdown("#### Language")
    language = st.radio(
        "Select language",
        options=["English", "Spanish", "German"],
        index=0,
        key="language_radio",
        help="Choose output language"
    )

with col3:
    st.markdown("#### Citation Format")
    citation_format = st.radio(
        "Select citation style",
        options=["APA", "MLA", "IEEE"],
        index=0,
        key="citation_format_radio",
        help="Choose citation formatting style"
    )

# Add word count slider below the columns
st.markdown("#### Target Word Count")
target_word_count = st.slider(
    "Select target word count",
    min_value=500,
    max_value=5000,
    value=1000,
    step=100,
    key="word_count_slider",
    help="Choose the approximate length of your research paper"
)

# Update all session state values
st.session_state.writing_style = writing_style
st.session_state.language = language
st.session_state.citation_format = citation_format
st.session_state.target_word_count = target_word_count

# Display current settings
st.markdown("""
    <div style='margin-top: 2rem;'>
        <p style='color: #58a6ff; font-size: 1.1rem; font-weight: 500;'>Current Settings:</p>
        <ul style='list-style-type: none; padding: 0; color: #c9d1d9;'>
            <li>📝 Writing Style: <strong>{}</strong></li>
            <li>📚 Citation Format: <strong>{}</strong></li>
            <li>🌐 Language: <strong>{}</strong></li>
            <li>📊 Target Words: <strong>{}</strong></li>
        </ul>
    </div>
""".format(
    writing_style.title(),
    citation_format,
    language.title(),
    target_word_count
), unsafe_allow_html=True)

# Style descriptions dictionary with capitalized keys
style_descriptions = {
    "Academic": "Formal scholarly writing with rigorous citations",
    "Business": "Professional tone with actionable insights",
    "Technical": "Detailed technical analysis and specifications",
    "Casual": "Accessible, conversational explanation"
}

with st.expander("📋 Writing Style Preview"):
    st.markdown(f"""
        <div style='background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1rem;'>
            <p style='color: #58a6ff; font-weight: bold;'>{writing_style}</p>
            <p style='color: #c9d1d9;'>{style_descriptions[writing_style]}</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"<p style='color: #c9d1d9;'>Example citation in {citation_format}:</p>", unsafe_allow_html=True)
    example_citation = {
        "title": "Sample Research Paper",
        "url": "https://example.com/research",
    }
    st.code(format_citation(example_citation, citation_format))

# Research button logic (disabled if keys missing)
run_disabled = (len(missing_keys) > 0) or st.session_state.get("__busy__", False)
if run_disabled:
    st.info("Add your API keys to enable research.")
if st.button("Run Research", disabled=run_disabled):
    if not query.strip():
        st.error("Please enter a valid research query.")
    elif not check_openrouter_status():
        st.error("OpenRouter is currently down. Please try again later.")
    else:
        try:
            with st.spinner("Processing your request..."):
                # Initialize progress bar and status
                progress_bar = st.progress(0)
                status_text = st.empty()
                # Disable Run button while in progress by setting a session flag
                st.session_state["__busy__"] = True

                # Step 1: Fetch research data
                status_text.text("Step 1/3: Fetching research data... 🔍")
                logging.info(f"Starting research for query: {query}, deep_research: {deep_research}, target_word_count: {target_word_count}")
                research_data, response = run_research(
                    query,
                    deep_research=deep_research,
                    target_word_count=target_word_count,
                    writing_style=writing_style,
                    citation_format=citation_format,
                    language=language
                )
                progress_bar.progress(20)

                # Step 2: Drafting response
                status_text.text("Step 2/3: Drafting response... ✍️")
                if "Error drafting response" in response:
                    st.error(response)
                    logging.error(f"Failed to draft response: {response}")
                else:
                    # Simulate gradual progress during drafting for better feedback
                    for p in (35, 45, 55, 65):
                        progress_bar.progress(p)

                    # Step 3: Generating PDF
                    status_text.text("Step 3/3: Generating PDF report... 📄")
                    st.success("Research completed! 🎉", icon="✅")
                    st.subheader("Structured Summary 📝")

                    # Display summary with structured JSON
                    try:
                        parsed = json.loads(response)
                    except Exception:
                        parsed = {"sections": [{"title": "Response", "content": response}], "references": []}

                    st.write("### Research Summary 📚")
                    with st.expander("View Research Summary", expanded=True):
                        for item in research_data:
                            st.markdown(f"<p style='font-weight:600; font-size:1.05rem; margin:0 0 0.25rem 0;'>{html.escape(item['title'])}</p>", unsafe_allow_html=True)
                            _render_small_text(item['content'])
                            st.markdown(f"[Source]({item['url']})")
                            st.markdown("---")

                    st.write("### Detailed Analysis 📝")
                    for sec in parsed.get("sections", []):
                        with st.expander(sec.get("title","Section"), expanded=True):
                            _render_small_text(sec.get("content",""))

                    refs = parsed.get("references", [])
                    if refs:
                        with st.expander("References", expanded=True):
                            for i, ref in enumerate(refs, 1):
                                st.markdown(f"{i}. {ref}")

                    # Calculate word count and page estimate
                    word_count = len(response.split())
                    page_estimate = word_count // 400 + 1  # Rough estimate: ~400 words per page
                    st.info(f"Summary contains {word_count} words, estimated at {page_estimate} pages.")
                    progress_bar.progress(85)

                    # Store results in session state
                    st.session_state.research_data = research_data
                    st.session_state.response = response
                    st.session_state.pdf_buffer = generate_pdf(query, research_data, response, deep_research=deep_research)
                    st.session_state.word_buffer = generate_docx(query, research_data, response, deep_research=deep_research)

                    # Interactive Research Data Display
                    st.write("### Research Data 📚")
                    for item in research_data:
                        with st.expander(item['title']):
                            st.write(item['content'])
                            st.markdown(f"[Visit Source]({item['url']})")

        except Exception as e:
            st.error(f"Failed after retries: {str(e)}")
            logging.error(f"Failed to process query '{query}': {str(e)}")
        finally:
            progress_bar.progress(100)
            progress_bar.empty()  # Clear progress bar
            status_text.empty()  # Clear status text
            st.session_state["__busy__"] = False

# Display download options if research data is available
if st.session_state.research_data and st.session_state.response:
    st.write("### Download Options")
    
    # Simple format selection without session state
    selected_format = st.radio(
        "Select format:",
        ["PDF (Recommended)", "Word", "Markdown", "JSON", "Text"],
        horizontal=True
    )

    # Show description based on selection
    if selected_format == "PDF (Recommended)":
        st.caption("Download as a PDF file, ideal for printing or sharing with formatted content.")
        st.download_button(
            label="Download PDF 📥",
            data=st.session_state.pdf_buffer,
            file_name="research_report.pdf",
            mime="application/pdf"
        )
    elif selected_format == "Word":
        st.caption("Download as a Word document, perfect for editing and professional documentation.")
        st.download_button(
            label="Download Word 📥",
            data=st.session_state.word_buffer,
            file_name="research_report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    elif selected_format == "Markdown":
        st.caption("Download as a Markdown file, great for lightweight formatting and version control.")
        st.download_button(
            label="Download Markdown 📥",
            data=st.session_state.response,
            file_name="research_summary.md",
            mime="text/markdown"
        )
    elif selected_format == "JSON":
        st.caption("Download as a JSON file (structured sections & references).")
        st.download_button(
            label="Download JSON 📥",
            data=st.session_state.response,
            file_name="research_summary.json",
            mime="application/json"
        )
    else:  # Text
        st.caption("Download as a plain text file, suitable for simple viewing or copying.")
        st.download_button(
            label="Download Text 📥",
            data=st.session_state.response,
            file_name="research_summary.txt",
            mime="text/plain"
        )

# Feedback form in sidebar
st.sidebar.header("Feedback")
feedback = st.sidebar.text_area("How can we improve? (Optional)")
if st.sidebar.button("Submit Feedback"):
    st.sidebar.success("Thanks for your feedback! 🙏")
    with open("feedback.txt", "a") as f:
        f.write(f"{feedback}\n")
        