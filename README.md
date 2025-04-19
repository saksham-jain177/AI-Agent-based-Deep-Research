# Deep Research AI Agent

## Overview

A dual-agent system for deep research, using Tavily for web crawling and OpenRouter for drafting structured summaries. Built with LangChain, LangGraph, and Streamlit.

## Live Demo

Access the live application at: [https://deep-research-ai-agent.streamlit.app/](https://deep-research-ai-agent.streamlit.app/)

## Watch the Demo

[![Watch the demo video](https://i.vimeocdn.com/video/2006782380-10ad9763c14f305a030d0d013b1c71528b7b836637d609c0829e52980037c6d3-d_640x360)](https://vimeo.com/1076886152)

## Setup

1. Clone the repo:

    ``` bash
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
   - `joblib`
   - Additional dependencies for document processing

3. Create a `.env` file with API keys:

      ```bash
      TAVILY_API_KEY=your_tavily_key
      OPENROUTER_API_KEY=your_openrouter_key
      ```

      - Obtain a Tavily API key from [Tavily](https://tavily.com) (free tier available).
      - Obtain an OpenRouter API key from [OpenRouter](https://openrouter.ai) (uses the free models, can be altered as per preference).

4. Run the app locally:

      ```streamlit run app.py```

## Features

- **Dual-Agent System**:
  - **Research Agent**: Fetches data from the web using Tavily, returning structured results (title, content, URL).
  - **Draft Agent**: Generates structured summaries with sections: Research Summary, Key Findings, Analysis, and Conclusion, using LLM model.
- **Customizable Settings**:
  - Writing styles (Academic, Casual, Technical, etc.)
  - Citation formats (APA, MLA, IEEE)
  - Target word count
  - Multiple output formats (PDF, Word, Markdown, Text)
- **Structured Summaries**: Outputs summaries with clear sections (Research Summary, Key Findings, Analysis, Conclusion) for readability.
- **PDF Report Download**: Allows users to download a PDF report containing the query, research data, and structured summary, with proper text wrapping and multi-page support.
- **Retry Logic**: Handles API failures with `tenacity`, retrying up to 3 times with a 2-second delay.
- **OpenRouter Status**: Displays real-time API status in the sidebar, alerting users if OpenRouter is unavailable.
- **Progress Indicator**: Shows a progress bar during research and drafting for better user experience.
- **User Feedback**: Includes a feedback form in the sidebar to collect user suggestions.
- **Custom Styling**: Features high-contrast colors, proper spacing, and readable typography for an enhanced UI.

## Deployment

The application is deployed on Streamlit Cloud. To deploy your own instance:

1. Fork this repository
2. Visit [Streamlit Cloud](https://share.streamlit.io)
3. Deploy using your forked repository
4. Add your API keys in Streamlit Cloud's secrets management (in TOML format)

## Usage

1. Visit the [live demo](https://deep-research-ai-agent.streamlit.app/) or run locally
2. Enter a research query (e.g., "Latest advancements in quantum computing")
3. Customize research settings (optional)
4. Click "Run Research" to fetch data and generate a summary
5. View the research data and structured summary
6. Download the report in your preferred format
7. Provide feedback via the sidebar form (optional)

## Contributing

Contributions are welcome! If you have suggestions or improvements:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-name`)
3. Make your changes and commit (`git commit -m "Add feature"`)
4. Push to your branch (`git push origin feature-name`)
5. Open a Pull Request
