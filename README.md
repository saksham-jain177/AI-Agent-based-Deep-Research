# 🔬 Deep Research AI Agent

> **Your Personal AI Research Assistant** - Generate comprehensive research reports on any topic in seconds!

## 🌟 What is This?

Deep Research AI Agent is a **free web application** that helps you research any topic and generates professional research reports automatically. Simply type in what you want to research, and our AI agents will:
- 🔍 Search the web for reliable information
- 📊 Analyze and synthesize the data
- 📝 Create a structured research report
- 📄 Let you download it in multiple formats (PDF, Word, Markdown)

**No technical knowledge required!** Just visit the website and start researching.

## 🚀 Try It Now!

**Live Demo:** [https://deep-research-ai-agent.streamlit.app/](https://deep-research-ai-agent.streamlit.app/)

## 🎥 See It In Action

[![Watch the demo video](https://i.vimeocdn.com/video/2006782380-10ad9763c14f305a030d0d013b1c71528b7b836637d609c0829e52980037c6d3-d_640x360)](https://vimeo.com/1076886152)

## ✨ Key Features

### 🤖 Intelligent Research System
- **Dual AI Agents**: One searches the web, another writes your report
- **Smart Source Filtering**: Excludes low-quality sources (social media, etc.)
- **Multi-Language Support**: Generate reports in English, Spanish, or German
- **Free AI Models**: Uses OpenRouter's free models (10+ requests/day)

### 📝 Customizable Output
- **Writing Styles**: Academic, Business, Technical, or Casual
- **Citation Formats**: APA, MLA, or IEEE standards
- **Word Count Control**: 500 to 5000 words
- **Multiple Export Formats**: PDF, Word, Markdown, JSON, or Plain Text

### 🎨 User-Friendly Interface
- **No Login Required**: Start researching immediately
- **API Key Management**: Built-in secure key storage
- **Progress Tracking**: Real-time updates as your research generates
- **Dark Theme**: Easy on the eyes for extended use
- **Mobile Responsive**: Works on phones, tablets, and desktops

### 🔧 Advanced Features
- **Deep Research Mode**: For comprehensive, academic-style papers
- **Model Selection**: Choose from multiple free AI models
- **Performance Metrics**: See model speed and quality
- **Duplicate Detection**: Automatically removes redundant content
- **Markdown Rendering**: Proper formatting with bold, lists, and more

## 🎯 Perfect For

- 📚 **Students**: Research papers, essays, assignments
- 💼 **Professionals**: Market research, industry analysis, reports
- 📰 **Writers**: Article research, fact-checking, content ideas
- 🔬 **Researchers**: Literature reviews, topic exploration
- 🎓 **Educators**: Lesson planning, curriculum development
- 💡 **Anyone Curious**: Learn about any topic quickly!

## 💻 For Developers

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

3. **Get your free API keys:**
   - [Tavily API](https://tavily.com) - For web search (free tier available)
   - [OpenRouter API](https://openrouter.ai) - For AI models (free models included)

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
- **LLM Provider**: OpenRouter (free models)
- **Document Generation**: ReportLab (PDF), python-docx (Word)
- **Styling**: Custom CSS with dark theme

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

## 🚀 Deploy Your Own

### Streamlit Cloud (Recommended - Free)

1. Fork this repository
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Deploy your forked repo
5. Add API keys in Streamlit's Secrets (Settings → Secrets)

### Other Platforms

- **Render**: Free tier available, supports Python apps
- **Railway**: One-click deploy with environment variables
- **Heroku**: Free tier discontinued, but paid plans work
- **Local Server**: Run on your own computer or VPS

## 🔮 Upcoming Features

Based on user feedback, we're working on:

- 🧠 **Memory System**: Remember your research history
- 🔄 **Auto-Update**: Refresh research with latest information
- 📊 **Data Visualization**: Charts and graphs in reports
- 🌐 **More Languages**: French, Chinese, Japanese, etc.
- 📱 **Mobile App**: Native iOS/Android applications
- 🤝 **Collaboration**: Share research with teams
- 📈 **Analytics**: Track research trends and insights

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

## 📊 Statistics

- ✅ **100% Free** to use with free API tiers
- 🚀 **< 30 seconds** average research time
- 📄 **5+ export formats** supported
- 🌍 **3 languages** available
- 🤖 **10+ AI models** to choose from
- ⭐ **500+ GitHub stars** (and growing!)

## ❓ FAQ

**Q: Is this really free?**
A: Yes! The app uses free tiers of APIs. You get ~10 free researches per day.

**Q: Do I need coding knowledge?**
A: No! Just visit the website and start researching.

**Q: Can I use this for academic work?**
A: Yes, but always verify sources and cite appropriately. This is a research tool, not a substitute for critical thinking.

**Q: How accurate is the information?**
A: We search reputable sources and filter out social media. However, always fact-check important information.

**Q: Can I customize the AI model?**
A: Yes! Choose from multiple free models in the sidebar.

**Q: Is my data private?**
A: We don't store your searches. API providers may have their own policies.

## 🙏 Acknowledgments

Built with amazing open-source projects:
- [Streamlit](https://streamlit.io) - Web framework
- [LangChain](https://langchain.com) - AI orchestration  
- [Tavily](https://tavily.com) - Web search API
- [OpenRouter](https://openrouter.ai) - LLM gateway

## 📜 License

MIT License - Use freely for personal or commercial projects!

## 📧 Contact

- **GitHub Issues**: [Report bugs or request features](https://github.com/saksham-jain177/AI-Agent-based-Deep-Research/issues)
- **Discussions**: [Join the community](https://github.com/saksham-jain177/AI-Agent-based-Deep-Research/discussions)

---

<div align="center">
  
**Made with ❤️ by the open-source community**

⭐ **Star this repo** if you find it helpful!

</div>