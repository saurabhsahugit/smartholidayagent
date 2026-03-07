"""
Smart Holiday Agent - Main Application
======================================

This is the entry point for the Smart Holiday Agent.
Currently, this is just a basic Streamlit app to verify setup.

Future development will add:
- Chat interface
- UK holiday data fetching
- LLM-powered optimization
- User authentication

Author: Saurabh Sahu
Repository: github.com/saurabhsahugit/smartholidayagent
"""

import streamlit as st

# Set page configuration - this must be the first Streamlit command
st.set_page_config(
    page_title="Smart Holiday Agent",
    page_icon="🏖️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Main page content
st.title("🏖️ Smart Holiday Agent")
st.markdown("### AI-Powered UK Holiday Planning Assistant")

st.info("""
👋 **Welcome!** This is the foundation of your Smart Holiday Agent.

**Current Status:** Basic scaffolding complete ✅

**Next Steps:**
1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your OpenAI API key
3. Run this app: `streamlit run app.py`
4. Start building features incrementally!
"""
)

# Sidebar placeholder
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("_Settings will appear here in future versions_")
    
    st.divider()
    
    st.markdown("**Project Status:**")
    st.markdown("- ✅ Project structure")
    st.markdown("- ⏳ UK holidays fetching")
    st.markdown("- ⏳ Chat interface")
    st.markdown("- ⏳ LLM integration")
    st.markdown("- ⏳ Optimization engine")

# Footer
st.divider()
st.caption("Built with ❤️ using Streamlit and OpenAI")