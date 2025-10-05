# Deep Research AI Agent

Generate comprehensive research reports on any topic in seconds.

## 🌟 What is This?

Deep Research AI Agent is a web application that helps you research any topic and generates professional research reports automatically. Simply type in what you want to research, and our AI agents will:
- 🔍 Search the web for reliable information
- 📊 Analyze and synthesize the data
- 📝 Create a structured research report
- 📄 Let you download it in multiple formats (PDF, Word, Markdown)

**No technical knowledge required!** Just visit the website and start researching.

## Live Demo

[https://deep-research-ai-agent.streamlit.app/](https://deep-research-ai-agent.streamlit.app/)

## 🎥 See It In Action

[![Watch the demo video](https://i.vimeocdn.com/video/2006782380-10ad9763c14f305a030d0d013b1c71528b7b836637d609c0829e52980037c6d3-d_640x360)](https://vimeo.com/1076886152)

## ✨ Key Features

### 🤖 Intelligent Research System
- **Dual AI Agents**: One searches the web, another writes your report
- **Multi-Language Support**: Generate reports in English, Spanish, or German
- **Model Selection**: Choose models via OpenRouter

### 📝 Customizable Output
- **Writing Styles**: Academic, Business, Technical, or Casual
- **Citation Formats**: APA, MLA, or IEEE standards
- **Word Count Control**: 500 to 5000 words
- **Multiple Export Formats**: PDF, Word, Markdown, JSON, or Plain Text

### 🎨 User-Friendly Interface
- **No Login Required**: Start researching immediately
- **Progress Tracking**: Real-time updates as your research generates
- **Mobile Responsive**: Works on phones, tablets, and desktops

### 🔧 Advanced Features
- **Deep Research Mode**: For comprehensive, academic-style papers
- **Model Selection**: Choose from multiple models
- **Duplicate Detection**: Automatically removes redundant content

## Architecture (agent‑like)

- Orchestrated with LangGraph as a two‑node state machine:
  - `research` → gathers sources via Tavily (with domain filtering)
  - `draft` → composes structured Markdown based on style/language/citations
- Post‑processing normalizes lists, paragraph spacing, and references across PDF/Word/Markdown/Text.

## 🎯 Perfect For

- 📚 **Students**: Research papers, essays, assignments
- 📰 **Writers**: Article research, fact-checking, content ideas
- 🎓 **Educators**: Lesson planning, curriculum development
- 💡 **Anyone Curious**: Learn about any topic quickly!

## For Developers

### Quick Setup

1. **Clone the repository:**
   ```bash
    git clone https://github.com/saksham-jain177/AI-Agent-based-Deep-Research.git
    cd AI-Agent-based-Deep-Research
   ```

2. **Install Python 3.8+ and dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get API keys:**
   - [Tavily API](https://tavily.com) - For web search (free tier available)
   - [OpenRouter API](https://openrouter.ai) - For AI models

4. **Create `.env` file:**
   ```
   TAVILY_API_KEY=your_tavily_key_here
   OPENROUTER_API_KEY=your_openrouter_key_here
   ```

5. **Run the app:**
   ```bash
   streamlit run app.py
   ```

### Tech Stack

- **Frontend**: Streamlit (Python web framework)
- **AI Framework**: LangChain & LangGraph
- **Web Search**: Tavily API
- **LLM Provider**: OpenRouter
- **Document Generation**: ReportLab (PDF), python-docx (Word)

### Project Structure

```
AI-Agent-based-Deep-Research/
├── app.py              # Main Streamlit application
├── main.py             # Orchestrates research workflow
├── research_agent.py   # Web search functionality
├── draft_agent.py      # AI report generation
├── requirements.txt    # Python dependencies
└── .env               # API keys (create this)
```

## Deploy your own instance

### If you'd like to deploy your own version of this app with customizations with Streamlit Cloud : 

1. Fork this repository
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Deploy your forked repo
5. Add API keys in Streamlit's Secrets (Settings → Secrets)

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Report Bugs**: Open an issue describing the problem
2. **Suggest Features**: Share your ideas in discussions
3. **Submit Code**: Fork, modify, and create a pull request
4. **Improve Docs**: Help make this README even better
5. **Share**: Tell others about this project!

### Development Setup

      ```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/AI-Agent-based-Deep-Research.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -r requirements.txt

# Make your changes and test
streamlit run app.py
```
## ❓ FAQ

**Q: Do I need coding knowledge?**
A: No. Open the web app, enter a query, and click Run.

**Q: Can I use this for academic work?**
A: Yes, but always verify sources and cite appropriately. This is a research tool, not a substitute for critical thinking.

**Q: How accurate is the information?**
A: We search reputable sources and filter out social media. However, always fact-check important information.

**Q: Can I customize the AI model?**
A: Yes. Choose a model from the sidebar (OpenRouter).

**Q: Is my data private?**
A: We don't store your searches. API providers may have their own policies.

## 📜 License

MIT License - Use freely for personal or commercial projects!

## 📧 Contact

- **GitHub Issues**: [Report bugs or request features](https://github.com/saksham-jain177/AI-Agent-based-Deep-Research/issues)
- **Discussions**: [Join the community](https://github.com/saksham-jain177/AI-Agent-based-Deep-Research/discussions)

---

<div align="center">
  
⭐ **Star this repo** if you find it helpful!

</div>