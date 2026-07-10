import logging
from datetime import date, datetime
from time import perf_counter
from uuid import uuid4

import pandas as pd
import streamlit as st
from pandas.errors import EmptyDataError, ParserError

import src.llm_handler
from src.holidays import get_holidays
from src.planning import build_constraints, generate_ranked_plans
from src.telemetry import TELEMETRY_PATH, build_chat_event, log_event


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


def load_holidays_years(years: list[int]) -> dict[int, list[dict]]:
    loaded = {}
    for year in years:
        try:
            loaded[year] = get_holidays(year, "england-and-wales")
            logger.info(f"Preloaded holidays for {year}: {len(loaded[year])} events")
        except Exception as error:
            logger.warning(f"Unable to preload holidays for {year}: {error}")
            loaded[year] = []
    return loaded


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
    st.session_state.holidays_data = {}

if "excluded_leave_dates" not in st.session_state:
    st.session_state.excluded_leave_dates = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())

# In the session state initialization block:
if "llm_handler" not in st.session_state:
    try:
        st.session_state.llm_handler = src.llm_handler.HolidayLLMHandler()
    except ValueError as e:
        st.session_state.llm_handler = None
        logger.warning(f"LLM handler not initialized: {e}")

if "holidays_data" in st.session_state and not st.session_state.holidays_data:
    st.session_state.holidays_data = load_holidays_years([2026, 2027])

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

    max_leave_days = 4
    min_total_days_off = 5
    max_window_days = 12
    top_n = 3
    preferred_month_labels: list[str] = []
    selected_excluded_dates: list[date] = []

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
available_holidays = st.session_state.holidays_data.get(selected_year, [])
if available_holidays:
    recommended_plans = generate_ranked_plans(
        holidays_data=available_holidays,
        year=selected_year,
        constraints=planner_constraints,
        top_n=top_n,
    )

# Create two columns: chat on left, holidays on right
col1, col2, col3 = st.columns([5, 2, 1])

# Left column: Chat Interface
with col1:
    st.subheader("💬 Chat with Holiday Agent")

    # Display chat messages
    chat_container = st.container(height=500)
    with chat_container:
        if not st.session_state.messages:
            """
            👋 **Welcome!** I'm your Smart Holiday Agent.

            Ask me things like:
            - "What holidays are coming up?"
            - "When is the next bank holiday?"
            - "Show me all holidays in 2026"""
        else:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
with col1:
    # Chat input
    if prompt := st.chat_input("Ask about UK holidays..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        if st.session_state.llm_handler is None:
            response = (
                "⚠️ The AI chat is not configured yet. Add `OPENAI_API_KEY` to "
                "your environment and reload the app."
            )
        else:
            max_history_messages = 12
            recent_messages = st.session_state.messages[-max_history_messages:]
            start = perf_counter()
            error_type = ""
            try:
                response = st.session_state.llm_handler.create_chat_completion(
                    messages=recent_messages,
                    holidays_data=available_holidays,
                    year=st.session_state.selected_year,
                    region="england-and-wales",
                    planner_constraints=planner_constraints,
                    top_n=top_n,
                )
            except Exception as error:
                error_type = type(error).__name__
                response = "I hit an issue generating a response. Please try again."
            latency_ms = int((perf_counter() - start) * 1000)
            tool_name = (
                "get_ranked_holiday_strategies"
                if "get_ranked_holiday_strategies" in response
                else ""
            )
            event = build_chat_event(
                session_id=st.session_state.session_id,
                prompt=prompt,
                response=response,
                latency_ms=latency_ms,
                history_count_sent=len(recent_messages),
                has_holidays_data=bool(st.session_state.holidays_data),
                year_selected=st.session_state.selected_year,
                tool_called=bool(tool_name),
                tool_name=tool_name,
                planner_constraints=planner_constraints,
                error_type=error_type,
                # current_date=date.today(),
            )
            log_event(event)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

with col2:
    st.subheader(f"🎉 Holidays {selected_year}")

    available_holidays = st.session_state.holidays_data.get(selected_year, [])
    if available_holidays:
        logger.info(f"Displaying holidays for {selected_year}")
        year_events = [
            event
            for event in available_holidays
            if event["date"].startswith(str(selected_year))
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
        st.info("👈 Holidays are loading or unavailable for this year.")


# Footer
st.divider()
st.caption("Built with ❤️ using Streamlit and UK Government Data")
st.caption("Data source: gov.uk/bank-holidays | LLM integration enabled")

st.divider()
st.subheader("🧪 AI Telemetry Snapshot")
if TELEMETRY_PATH.exists():
    try:
        telemetry_df = pd.read_csv(TELEMETRY_PATH)
    except (EmptyDataError, ParserError):
        telemetry_df = pd.DataFrame()

    if not telemetry_df.empty:
        latest = telemetry_df.tail(200).copy()
        if "timestamp_utc" in latest.columns:
            latest["timestamp_utc"] = pd.to_datetime(
                latest["timestamp_utc"], errors="coerce", utc=True
            )
            latest["event_date"] = latest["timestamp_utc"].dt.date

        for numeric_col in [
            "latency_ms",
            "q_total",
            "q_completeness",
            "q_constraint_adherence",
            "q_actionable",
            "tool_called",
        ]:
            if numeric_col in latest.columns:
                latest[numeric_col] = pd.to_numeric(
                    latest[numeric_col], errors="coerce"
                )

        top_metrics = st.columns(4)

        if "latency_ms" in latest.columns:
            avg_latency = latest["latency_ms"].dropna().mean()
            p95_latency = latest["latency_ms"].dropna().quantile(0.95)
            top_metrics[0].metric(
                "Avg latency (ms)", int(avg_latency) if pd.notna(avg_latency) else "N/A"
            )
            top_metrics[1].metric(
                "P95 latency (ms)", int(p95_latency) if pd.notna(p95_latency) else "N/A"
            )
        else:
            top_metrics[0].metric("Avg latency (ms)", "N/A")
            top_metrics[1].metric("P95 latency (ms)", "N/A")

        if "q_total" in latest.columns:
            avg_quality = latest["q_total"].dropna().mean()
            top_metrics[2].metric(
                "Avg quality score",
                round(avg_quality, 2) if pd.notna(avg_quality) else "N/A",
            )
        else:
            top_metrics[2].metric("Avg quality score", "N/A")

        if "tool_called" in latest.columns:
            tool_rate = latest["tool_called"].fillna(0).mean() * 100
            top_metrics[3].metric("Tool usage rate", f"{tool_rate:.1f}%")
        else:
            top_metrics[3].metric("Tool usage rate", "N/A")

        if {"event_date", "latency_ms"}.issubset(latest.columns):
            latency_trend = (
                latest.dropna(subset=["event_date", "latency_ms"])
                .groupby("event_date", as_index=False)["latency_ms"]
                .agg(["median", lambda x: x.quantile(0.95)])
                .reset_index()
            )
            latency_trend.columns = [
                "event_date",
                "latency_ms",
                "p50_latency",
                "p95_latency",
            ]
            st.caption("Latency trend (P50 / P95 by day)")
            st.line_chart(
                latency_trend, x="event_date", y=["p50_latency", "p95_latency"]
            )

        quality_cols = [
            "q_completeness",
            "q_constraint_adherence",
            "q_actionable",
            "q_total",
        ]
        available_quality_cols = [col for col in quality_cols if col in latest.columns]
        if {"event_date", "q_total"}.issubset(latest.columns):
            quality_trend = (
                latest.dropna(subset=["event_date", "q_total"])
                .groupby("event_date", as_index=False)["q_total"]
                .mean()
            )
            st.caption("Quality trend (average q_total by day)")
            st.line_chart(quality_trend.set_index("event_date"))

        if available_quality_cols:
            st.caption("Quality signal distribution (last 200 events)")
            st.bar_chart(latest[available_quality_cols].mean(numeric_only=True))

        preview_columns = [
            "timestamp_utc",
            "latency_ms",
            "q_completeness",
            "q_constraint_adherence",
            "q_actionable",
            "q_total",
            "tool_called",
            "error_type",
        ]
        available_preview_columns = [
            col for col in preview_columns if col in latest.columns
        ]
        if available_preview_columns:
            st.dataframe(
                latest[available_preview_columns].tail(10),
                use_container_width=True,
            )
        else:
            st.info("Telemetry file exists but does not include preview fields yet.")
    else:
        st.info("Telemetry file exists but has no readable rows yet.")
else:
    st.info("No telemetry events yet. Ask a question in chat to generate metrics.")
