import streamlit as st
from research_agent import research_tool
from draft_agent import draft_answer
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
import requests
from tenacity import retry, stop_after_attempt, wait_fixed

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
    except:
        return False

# Retry logic for API calls
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def run_research_with_retry(query):
    """Run research with retries on failure."""
    return research_tool.run(query)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def draft_answer_with_retry(data):
    """Draft answer with retries on failure."""
    return draft_answer(data)

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
st.sidebar.write("Dual-agent system using Tavily for research and OpenRouter for drafting with the qwen/qwen-vl-plus:free model.")
st.sidebar.write("Built with LangChain, LangGraph, and Streamlit.")

# User input
query = st.text_input("Research Query", "Latest advancements in quantum computing")

# Research button logic
if st.button("Run Research"):
    if not check_openrouter_status():
        st.error("OpenRouter is currently down. Please try again later.")
    else:
        with st.spinner("Fetching data and drafting response..."):
            progress_bar = st.progress(0)  # Progress indicator
            try:
                # Research phase
                research_data = run_research_with_retry(query)
                progress_bar.progress(50)  # Update progress

                if isinstance(research_data, dict) and "error" in research_data:
                    st.error(f"Research failed: {research_data['error']}")
                else:
                    st.write("### Research Data")
                    st.json(research_data)

                    # Drafting phase
                    response = draft_answer_with_retry(research_data)
                    progress_bar.progress(100)  # Complete progress

                    if "Error drafting response" in response:
                        st.error(response)
                    else:
                        st.success("Research completed!", icon="✅")
                        st.subheader("Structured Summary")
                        st.write(response)

                        # Function to generate PDF
                        def generate_pdf(query, data, summary):
                            """Generate a PDF report with query, data, and summary."""
                            buffer = io.BytesIO()
                            doc = SimpleDocTemplate(buffer, pagesize=letter)
                            styles = getSampleStyleSheet()
                            story = []

                            # Title
                            story.append(Paragraph("Research Report", styles['Title']))
                            story.append(Spacer(1, 12))

                            # OpenRouter Status
                            status = "Operational" if check_openrouter_status() else "Down"
                            story.append(Paragraph(f"OpenRouter Status: {status}", styles['Normal']))
                            story.append(Spacer(1, 12))

                            # Query
                            story.append(Paragraph(f"Query: {query}", styles['Heading2']))
                            story.append(Spacer(1, 12))

                            # Research Data
                            story.append(Paragraph("Research Data:", styles['Heading3']))
                            for item in data:
                                content = f"- {item['title']}: {item['content']}"
                                story.append(Paragraph(content, styles['BodyText']))
                            story.append(Spacer(1, 12))

                            # Summary
                            story.append(Paragraph("Summary:", styles['Heading3']))
                            summary_paragraphs = summary.split("\n\n")
                            for para in summary_paragraphs:
                                story.append(Paragraph(para, styles['BodyText']))
                                story.append(Spacer(1, 12))

                            doc.build(story)
                            buffer.seek(0)
                            return buffer

                        # Offer PDF download
                        pdf_buffer = generate_pdf(query, research_data, response)
                        st.download_button(
                            label="Download PDF Report",
                            data=pdf_buffer,
                            file_name="research_report.pdf",
                            mime="application/pdf"
                        )
            except Exception as e:
                st.error(f"Failed after retries: {str(e)}")
            finally:
                progress_bar.empty()  # Clear progress bar

# Feedback form in sidebar
st.sidebar.header("Feedback")
feedback = st.sidebar.text_area("How can we improve? (Optional)")
if st.sidebar.button("Submit Feedback"):
    st.sidebar.success("Thanks for your feedback!")    
    with open("feedback.txt", "a") as f:
     f.write(f"{feedback}\n")