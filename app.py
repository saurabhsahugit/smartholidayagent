import logging
from datetime import date, datetime

import streamlit as st

import src.llm_handler
from src.holidays import get_holidays
from src.planning import build_constraints, format_plan_summary, generate_ranked_plans


# Configure logging
def configure_logging() -> None:
    """Configure logging once, avoiding duplicate handlers on Streamlit reruns."""
    root_logger = logging.getLogger()
    if root_logger.handlers:
        # Logging is already configured; avoid adding duplicate handlers.
        return
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


configure_logging()


logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Smart Holiday Agent",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "holidays_data" not in st.session_state:
    st.session_state.holidays_data = None

if "excluded_leave_dates" not in st.session_state:
    st.session_state.excluded_leave_dates = []

# In the session state initialization block:
if "llm_handler" not in st.session_state:
    try:
        st.session_state.llm_handler = src.llm_handler.HolidayLLMHandler()
    except ValueError as e:
        st.session_state.llm_handler = None
        logger.warning(f"LLM handler not initialized: {e}")
# Main page content
st.title("🏖️ Smart Holiday Agent")
st.markdown("### AI-Powered UK Holiday Planning Assistant")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # Year selector
    current_year = datetime.now().year
    selected_year = st.selectbox(
        "Select Year", options=[current_year, current_year + 1], index=0
    )
    st.session_state.selected_year = selected_year

    st.subheader("Holiday Strategy")
    max_leave_days = st.slider("Max leave days", min_value=1, max_value=10, value=4)
    min_total_days_off = st.slider(
        "Minimum total days off", min_value=3, max_value=14, value=5
    )
    max_window_days = st.slider(
        "Maximum break window", min_value=4, max_value=18, value=12
    )
    top_n = st.slider("Number of options", min_value=1, max_value=5, value=3)
    preferred_month_labels = st.multiselect(
        "Preferred months",
        options=[
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ],
        help="Leave blank to search the whole year.",
    )
    excluded_leave_dates = st.date_input(
        "Unavailable leave date",
        value=None,
        min_value=date(selected_year, 1, 1),
        max_value=date(selected_year, 12, 31),
        help="Optional single date to exclude from leave plans.",
    )

    selected_excluded_dates = []
    if excluded_leave_dates:
        selected_excluded_dates = [excluded_leave_dates]

    # Fetch holidays button
    if st.button("🔄 Load Holidays", use_container_width=True):
        with st.spinner("Fetching holiday data..."):
            st.session_state.holidays_data = get_holidays(
                selected_year, "england-and-wales"
            )
            logger.info(f"Holidays data loaded for {selected_year}")
            if st.session_state.holidays_data:
                events = st.session_state.holidays_data
                year_events = [
                    event
                    for event in events
                    if event["date"].startswith(str(selected_year))
                ]
                st.success(
                    f"✅ Loaded {len([event for event in events if event['date'].startswith(str(selected_year))])} holidays!"
                )

    st.divider()

    if st.session_state.llm_handler is None:
        st.warning("Add `OPENAI_API_KEY` to use the AI chat experience.")

    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

planner_constraints = build_constraints(
    max_leave_days=max_leave_days,
    min_total_days_off=min_total_days_off,
    max_window_days=max_window_days,
    preferred_month_labels=preferred_month_labels,
    excluded_leave_dates=selected_excluded_dates,
)

recommended_plans = []
if st.session_state.holidays_data:
    recommended_plans = generate_ranked_plans(
        holidays_data=st.session_state.holidays_data,
        year=selected_year,
        constraints=planner_constraints,
        top_n=top_n,
    )

# Create two columns: chat on left, holidays on right
col1, col2 = st.columns([2, 1])


def generate_response(user_input: str, holidays_data: dict) -> str:
    """
    Generate a response to user input (basic implementation).
    In Phase 4, this will be replaced with LLM integration.

    Args:
        user_input (str): User's message
        holidays_data (dict): Holiday data

    Returns:
        str: Response message
    """
    user_input_lower = user_input.lower()

    logger.info(f"All events: {holidays_data}")
    events = holidays_data

    # Check if holidays data is loaded
    if not holidays_data:
        return "⚠️ Clicking the '🔄 Load Holidays' button to reload!"
    else:
        events = holidays_data

    # Simple keyword matching for now
    if any(word in user_input_lower for word in ["next", "upcoming", "soon"]):
        today = datetime.now().date()
        upcoming = [
            event
            for event in events
            if datetime.strptime(event["date"], "%Y-%m-%d").date() > today
        ]
        if upcoming:
            next_holiday = upcoming[0]
            date_obj = datetime.strptime(next_holiday["date"], "%Y-%m-%d")
            return f"🎉 The next bank holiday is **{next_holiday['title']}** on {date_obj.strftime('%A, %d %B %Y')}!"
        else:
            return "No upcoming holidays found in the loaded data."

    elif any(word in user_input_lower for word in ["all", "list", "show"]):
        response = "📅 Here are all the holidays:\n\n"
        for event in events:
            date_obj = datetime.strptime(event["date"], "%Y-%m-%d")
            response += f"- **{event['title']}**: {date_obj.strftime('%d %B %Y')}\n"
        return response

    elif "how many" in user_input_lower:
        return f"📊 There are **{len(events)}** bank holidays in the loaded data."

    else:
        return """
            I'm still learning! 🤖

            Right now I can answer:
            - "What's the next holiday?"
            - "Show me all holidays"
            - "How many holidays are there?"

            *In Phase 4, I'll be powered by AI and can answer much more!*
            """


# Left column: Chat Interface
with col1:
    st.subheader("💬 Chat with Holiday Agent")

    # Display chat messages
    chat_container = st.container(height=500)
    with chat_container:
        if not st.session_state.messages:
            st.info(
                """
            👋 **Welcome!** I'm your Smart Holiday Agent.

            Ask me things like:
            - "What holidays are coming up?"
            - "When is the next bank holiday?"
            - "Show me all holidays in 2026"

            *AI chat is available when `OPENAI_API_KEY` is configured.*
            """
            )
        else:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about UK holidays..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        if st.session_state.llm_handler is None:
            response = (
                "⚠️ The AI chat is not configured yet. Add `OPENAI_API_KEY` to "
                "your environment and reload the app."
            )
        else:
            response = st.session_state.llm_handler.create_chat_completion(
                messages=st.session_state.messages,
                holidays_data=st.session_state.holidays_data,
                year=st.session_state.selected_year,
                region="england-and-wales",
                planner_constraints=planner_constraints,
                top_n=top_n,
            )

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# Right column: Holiday Display
with col2:
    st.subheader("📈 Top Leave Strategies")

    if recommended_plans:
        for index, plan in enumerate(recommended_plans, start=1):
            details = format_plan_summary(plan)
            with st.container(border=True):
                st.markdown(
                    f"**Option {index}: {details['total_days_off']} days off, "
                    f"{details['leave_days_used']} leave day(s)**"
                )
                st.caption(details["date_range"])
                metric_columns = st.columns(3)
                metric_columns[0].metric("Efficiency", details["efficiency_ratio"])
                metric_columns[1].metric("Leave used", details["leave_days_used"])
                metric_columns[2].metric("Weekend days", details["weekend_count"])
                st.markdown(f"**Take leave:** {details['leave_dates']}")
                st.markdown(f"**Public holidays included:** {details['holiday_dates']}")
    elif st.session_state.holidays_data:
        st.info("No plans matched the current strategy filters. Try relaxing them.")
    else:
        st.info("Load holidays to generate ranked leave strategies.")

    st.divider()
    st.subheader(f"🎉 Holidays {selected_year}")

    if st.session_state.holidays_data:
        logger.info(f"Displaying holidays for {selected_year}")
        events = st.session_state.holidays_data
        year_events = [
            event for event in events if event["date"].startswith(str(selected_year))
        ]

        if year_events:
            for event in year_events:
                date_str = event["date"]
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d %b")

                # Compact display
                with st.container():
                    cols = st.columns([1, 1])
                    with cols[0]:
                        st.markdown(f"**{event['title']}**")
                    with cols[1]:
                        st.caption(formatted_date)
        else:
            st.warning(f"No holidays found for {selected_year}")
    else:
        st.info("👈 Click 'Load Holidays' to see the list!")


# Footer
st.divider()
st.caption("Built with ❤️ using Streamlit and UK Government Data")
st.caption("Data source: gov.uk/bank-holidays | LLM integration enabled")
