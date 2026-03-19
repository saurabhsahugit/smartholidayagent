"""
Smart Holiday Agent - Main Application
======================================

AI-powered UK holiday planning assistant.

Author: Saurabh Sahu
Repository: github.com/saurabhsahugit/smartholidayagent
"""

import streamlit as st
from datetime import datetime
from src.holidays import get_holidays
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Year selector
    current_year = datetime.now().year
    selected_year = st.selectbox(
        "Select Year",
        options=[current_year, current_year + 1],
        index=0
    )
    
    st.divider()
    
    st.markdown("**Project Status:**")
    st.markdown("- ✅ Project structure")
    st.markdown("- ✅ UK holidays fetching")
    st.markdown("- ⏳ Chat interface")
    st.markdown("- ⏳ LLM integration")
    st.markdown("- ⏳ Optimization engine")

# Main content area
st.info("""
👋 **Welcome!** View UK public holidays and plan your time off strategically.

**Phase 2 Complete:** Holiday data fetching and display ✅
""")

# Fetch and display holidays
st.subheader(f"🎉 England & Wales Public Holidays {selected_year}")

try:
    # Fetch holidays
    with st.spinner("Fetching holiday data..."):
        holidays_data = get_holidays(selected_year, 'england-and-wales')
        logger.info(f"Holiday data received: {holidays_data}")
# Display holidays in a nice format
    for events in holidays_data:
        date_str = events["date"]
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = date_obj.strftime("%A")
        formatted_date = date_obj.strftime("%d %B %Y")
                
        # Create columns for better layout
        col1, col2 = st.columns([2, 1])
                
        with col1:
            st.markdown(f"**{events['title']}**")
        with col2:
            st.caption(f"{day_name}, {formatted_date}")
        
except Exception as e:
    st.error(f"Error loading holidays: {str(e)}")
    st.info("💡 Make sure you have an internet connection and the API is accessible.")

# Footer
st.divider()
st.caption("Built with ❤️ using Streamlit and UK Government Data")
st.caption("Data source: gov.uk/bank-holidays")