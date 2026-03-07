# 🏖️ Smart Holiday Agent

AI-powered assistant for planning holidays within the UK. Maximizes your holiday breaks while minimizing the use of personal leave days.

## 🎯 What This Does

The Smart Holiday Agent helps UK residents:
- 📅 Identify optimal times to take holidays by analyzing UK public holidays
- 🧮 Maximize consecutive days off with minimal personal leave usage
- 💡 Get AI-powered suggestions ranked by efficiency
- 🎨 Plan holidays through an easy-to-use chat interface

## 🏗️ Current Status

**Phase 1: Foundation** ✅ (You are here!)
- Basic project structure
- Configuration files
- Hello World Streamlit app

**Future Phases:**
- Phase 2: UK holiday data fetching
- Phase 3: Chat interface
- Phase 4: LLM integration
- Phase 5: Optimization algorithm
- Phase 6: User authentication
- Phase 7: AWS deployment

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/saurabhsahugit/smartholidayagent.git
   cd smartholidayagent
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # On Windows: notepad .env
   # On macOS: open -e .env
   # On Linux: nano .env
   ```

5. **Run the app**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser**
   - The app will automatically open at `http://localhost:8501`
   - If not, navigate there manually

## 📁 Project Structure

```
smartholidayagent/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── config.yaml            # Application configuration
├── .env.example           # Environment variable template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── src/                  # Future: Python modules
├── tests/                # Future: Test files
├── data/                 # Future: User data storage
└── deployment/           # Future: AWS deployment configs
```

## 🛠️ Development

### Running Locally
```bash
streamlit run app.py
```

### Installing New Packages
```bash
pip install package-name
pip freeze > requirements.txt  # Update requirements
```

### Testing (Future)
```bash
pytest tests/
```

## 📚 Learning Resources

New to these technologies? Here are some helpful resources:

- **Streamlit:** [Official Tutorial](https://docs.streamlit.io/get-started)
- **OpenAI API:** [Quickstart Guide](https://platform.openai.com/docs/quickstart)
- **Python Basics:** [Python.org Tutorial](https://docs.python.org/3/tutorial/)
- **Git & GitHub:** [GitHub Skills](https://skills.github.com/)

## 🤝 Contributing

This is a personal learning project, but suggestions are welcome!

## 📄 License

MIT License - Feel free to use this for learning.

## 🙋 Questions?

Open an issue on GitHub if you run into any problems!

---

**Next Step:** Once you've got this running, we'll add UK holiday fetching in Phase 2! 🎉