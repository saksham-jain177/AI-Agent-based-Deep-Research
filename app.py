import streamlit as st
from main import run_research  # Import run_research from main.py
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
import io
import requests
import datetime
import logging
import re

# Set up logging
logging.basicConfig(filename="research_agent.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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
        border-bottom: 2px solid #1f6feb;
        padding-bottom: 0.6rem;
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
    
    /* Button styling */
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
        transform: translateY(-2px);
    }
    
    .stButton > button:active {
        transform: translateY(1px);
        box-shadow: 0 0 10px rgba(14, 165, 233, 0.3);
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
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #21262d;
        height: 0.6rem !important;
        border-radius: 1rem;
    }
    
    .stProgress > div > div > div {
        background-image: linear-gradient(to right, #0891b2, #22d3ee);
        border-radius: 1rem;
        box-shadow: 0 0 10px rgba(14, 165, 233, 0.5);
    }
    
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
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(45deg, #065f46, #0ea5e9);
        color: white;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.7rem 1.4rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(14, 165, 233, 0.4);
        margin-top: 1.2rem;
        position: relative;
        overflow: hidden;
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 0 15px rgba(14, 165, 233, 0.6);
        transform: translateY(-2px);
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

# Streamlit app setup
st.title("Deep Research AI Agent")
st.write("Enter a query to research and get a detailed response using Tavily and OpenRouter.")

# Sidebar: Status and Info
st.sidebar.header("OpenRouter Status")
if check_openrouter_status():
    st.sidebar.success("Operational", icon="✅")
else:
    st.sidebar.error("Down", icon="❌")

st.sidebar.header("About")
st.sidebar.write("Dual-agent system using Tavily for research and OpenRouter for drafting with the cognitivecomputations/dolphin3.0-r1-mistral-24b:free model.")
st.sidebar.write("Built with LangChain, LangGraph, and Streamlit.")

# User input with Deep Research toggle
query = st.text_input("Research Query", "Latest advancements in quantum computing")

# Add the Deep Research toggle button below the query input
deep_research = st.checkbox("Deep Research Mode", value=False, help="Enable for a detailed, research-paper-style summary (5-6+ pages).")

# Research button logic
if st.button("Run Research"):
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

                # Step 1: Fetch research data
                status_text.text("Step 1/3: Fetching research data... 🔍")
                logging.info(f"Starting research for query: {query}, deep_research: {deep_research}")
                research_data, response = run_research(query, deep_research=deep_research)
                progress_bar.progress(33)

                # Step 2: Drafting response
                status_text.text("Step 2/3: Drafting response... ✍️")
                if "Error drafting response" in response:
                    st.error(response)
                    logging.error(f"Failed to draft response: {response}")
                else:
                    progress_bar.progress(66)

                    # Step 3: Generating PDF
                    status_text.text("Step 3/3: Generating PDF report... 📄")
                    st.success("Research completed! 🎉", icon="✅")
                    st.subheader("Structured Summary 📝")
                    st.markdown(response)

                    # Calculate word count and page estimate
                    word_count = len(response.split())
                    page_estimate = word_count // 400 + 1  # Rough estimate: ~400 words per page
                    st.info(f"Summary contains {word_count} words, estimated at {page_estimate} pages.")

                    st.write("### Research Data 📚")
                    st.json(research_data)

                    # Function to generate PDF with proper formatting
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

                        # Define a style for references (smaller font, hanging indent, blue hyperlinks)
                        reference_style = ParagraphStyle(
                            name='Reference',
                            parent=styles['BodyText'],
                            fontSize=9,
                            leading=12,
                            firstLineIndent=-18,
                            leftIndent=18,
                            textColor=colors.blue
                        )

                        # Define a bold style for headings
                        heading_style = ParagraphStyle(
                            name='HeadingBold',
                            parent=styles['Heading2'],
                            fontName='Helvetica-Bold',
                            fontSize=14,
                            textColor=colors.black,
                            spaceAfter=6
                        )

                        # Define a style for subheadings (bold, slightly smaller than main headings)
                        subheading_style = ParagraphStyle(
                            name='SubheadingBold',
                            parent=styles['Heading3'],
                            fontName='Helvetica-Bold',
                            fontSize=12,
                            textColor=colors.black,
                            spaceAfter=6
                        )

                        story = []

                        # Title
                        story.append(Paragraph("Research Report", styles['Title']))
                        story.append(Spacer(1, 12))

                        # Metadata
                        story.append(Paragraph("Author: [Your Name]", styles['Normal']))
                        story.append(Paragraph(f"Date: {datetime.date.today().strftime('%B %d, %Y')}", styles['Normal']))
                        story.append(Spacer(1, 12))

                        # OpenRouter Status
                        status = "Operational" if check_openrouter_status() else "Down"
                        story.append(Paragraph(f"OpenRouter Status: {status}", styles['Normal']))
                        story.append(Spacer(1, 12))

                        # Research Mode
                        mode = "Deep Research" if deep_research else "Quick Research"
                        story.append(Paragraph(f"Mode: {mode}", styles['Normal']))
                        story.append(Spacer(1, 12))

                        # Query
                        story.append(Paragraph(f"Query: {query}", heading_style))
                        story.append(Spacer(1, 12))

                        # Research Data
                        story.append(Paragraph("Research Data:", heading_style))
                        for item in data:
                            content = f"- {item['title']}: {item['content']}"
                            story.append(Paragraph(content, styles['BodyText']))
                        story.append(Spacer(1, 24))  # Extra space before summary

                        # Summary with research paper structure
                        story.append(Paragraph("Summary:", heading_style))
                        # Split summary into sections, ensuring proper separation
                        summary_sections = summary.split("\n\n")
                        current_heading = None
                        for section in summary_sections:
                            section = section.strip()
                            if not section:
                                continue
                            # Check if the section starts with a heading (e.g., **Abstract**)
                            if section.startswith("**") and section.endswith("**"):
                                # Remove the Markdown ** syntax and use the bold style
                                current_heading = section.strip("**").rstrip(":")
                                story.append(Paragraph(current_heading, heading_style))
                                story.append(Spacer(1, 6))
                            else:
                                # If it's not a heading, treat it as content under the current heading
                                if current_heading:
                                    # Skip the section if it exactly matches the current heading (safeguard)
                                    if section.strip(":") == current_heading:
                                        continue
                                    # Check if the section starts with ## indicating a subheading
                                    if section.startswith("##"):
                                        # Extract subheading text, removing ## and any surrounding whitespace
                                        subheading_text = section[2:].strip()
                                        # Remove any lingering Markdown bold (**)
                                        if subheading_text.startswith("*") and subheading_text.endswith("*"):
                                            subheading_text = subheading_text.strip("*")
                                        story.append(Paragraph(subheading_text, subheading_style))
                                        story.append(Spacer(1, 6))
                                    else:
                                        # Handle inline Markdown bold (**...**) within the content
                                        # Replace **text** with <b>text</b> for reportlab
                                        formatted_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", section)
                                        # Remove any lingering Markdown bold that might remain unmatched
                                        formatted_text = formatted_text.replace("**", "")
                                        story.append(Paragraph(formatted_text, styles['BodyText']))
                                        story.append(Spacer(1, 12))
                                else:
                                    # Handle References section separately
                                    if "References" in section:
                                        story.append(Paragraph("References", heading_style))
                                        story.append(Spacer(1, 6))
                                        # Extract numbered references
                                        ref_lines = section.split("\n")[1:]  # Skip the "References" line
                                        for ref_line in ref_lines:
                                            ref_line = ref_line.strip()
                                            if ref_line:
                                                # Extract the URL (after the number and dot, e.g., "1. https://...")
                                                parts = ref_line.split(" ", 1)
                                                if len(parts) > 1:
                                                    url = parts[1].strip()
                                                    link_text = f'<link href="{url}" color="blue">{ref_line}</link>'
                                                    story.append(Paragraph(link_text, reference_style))
                                                    story.append(Spacer(1, 6))
                                                else:
                                                    story.append(Paragraph(ref_line, reference_style))
                                                    story.append(Spacer(1, 6))
                                    else:
                                        # Handle inline Markdown bold in content
                                        formatted_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", section)
                                        formatted_text = formatted_text.replace("**", "")
                                        story.append(Paragraph(formatted_text, styles['BodyText']))
                                        story.append(Spacer(1, 12))

                        doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
                        buffer.seek(0)
                        return buffer

                    # Generate PDF
                    pdf_buffer = generate_pdf(query, research_data, response, deep_research=deep_research)
                    word_count = len(response.split())
                    page_estimate = word_count // 400 + 1  # Rough estimate: ~400 words per page
                    progress_bar.progress(100)
                    status_text.text(f"Done! Generated a {word_count}-word summary, estimated at {page_estimate} pages. 📊")

                    # Offer PDF download
                    st.download_button(
                        label=f"Download PDF Report ({page_estimate} pages) 📄",
                        data=pdf_buffer,
                        file_name="research_report.pdf",
                        mime="application/pdf"
                    )

                    # Offer text download
                    st.download_button(
                        label="Download Summary as Text 📝",
                        data=response,
                        file_name="research_summary.txt",
                        mime="text/plain"
                    )

        except Exception as e:
            st.error(f"Failed after retries: {str(e)}")
            logging.error(f"Failed to process query '{query}': {str(e)}")
        finally:
            progress_bar.empty()  # Clear progress bar
            status_text.empty()  # Clear status text

# Feedback form in sidebar
st.sidebar.header("Feedback")
feedback = st.sidebar.text_area("How can we improve? (Optional)")
if st.sidebar.button("Submit Feedback"):
    st.sidebar.success("Thanks for your feedback! 🙏")
    with open("feedback.txt", "a") as f:
        f.write(f"{feedback}\n")