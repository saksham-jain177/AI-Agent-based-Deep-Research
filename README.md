# Deep Research AI Agent

## Overview

A dual-agent system for deep research, using Tavily for web crawling and OpenRouter for drafting structured summaries. Built with LangChain, LangGraph, and Streamlit.

## Setup

1. Clone the repo:

    ``` 
    git clone https://github.com/saksham-jain177/AI-Agent-based-Deep-Research.git
    cd AI-Agent-based-Deep-Research
   ```

2. Install dependencies:

   ``` pip install -r requirements.txt ```

      Ensure you have Python 3.8+ installed. The `requirements.txt` file includes:
   - `streamlit`
   - `langchain`
   - `langgraph`
   - `tavily-python`
   - `requests`
   - `tenacity`
   - `reportlab`

3. Create a `.env` file with API keys:

      ```
      TAVILY_API_KEY=your_tavily_key
      OPENROUTER_API_KEY=your_openrouter_key
      ```
      - Obtain a Tavily API key from [Tavily](https://tavily.com) (free tier available).
      - Obtain an OpenRouter API key from [OpenRouter](https://openrouter.ai) (uses the free models, can be altered as per preference).

4. Run the app:
      ```streamlit run app.py```

## Features

- **Dual-Agent System**:
- **Research Agent**: Fetches data from the web using Tavily, returning structured results (title, content, URL).
- **Draft Agent**: Generates structured summaries with sections: Introduction, Key Findings, Analysis, and Conclusion, using OpenRouter’s available models.
- **Structured Summaries**: Outputs summaries with clear sections (Introduction, Key Findings, Analysis, Conclusion) for readability.
- **PDF Report Download**: Allows users to download a PDF report containing the query, research data, and structured summary, with proper text wrapping and multi-page support.
- **Retry Logic**: Handles API failures with `tenacity`, retrying up to 3 times with a 2-second delay.
- **OpenRouter Status**: Displays real-time API status in the sidebar, alerting users if OpenRouter is unavailable.
- **Progress Indicator**: Shows a progress bar during research and drafting for better user experience.
- **User Feedback**: Includes a feedback form in the sidebar to collect user suggestions.
- **Custom Styling**: Features high-contrast colors, proper spacing, and readable typography for an enhanced UI.

## Usage

1. Open the app in your browser (default: `http://localhost:8501`).
2. Enter a research query (e.g., "Latest advancements in quantum computing").
3. Click "Run Research" to fetch data and generate a summary.
4. View the research data and structured summary.
5. Download the PDF report using the "Download PDF Report" button.
6. Provide feedback via the sidebar form (optional), will generate a .txt file in same working directory.

## Contributing

Contributions are welcome! If you have suggestions or improvements:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Make your changes and commit (`git commit -m "Add feature"`).
4. Push to your branch (`git push origin feature-name`).
5. Open a Pull Request.
