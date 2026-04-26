import json
import logging
import os
from datetime import date, datetime
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI

from src.optimizer import UserConstraints
from src.planning import build_constraints, format_plan_summary, generate_ranked_plans

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class HolidayLLMHandler:
    """
    Handles LLM interactions for holiday planning.

    This class manages:
    - Connection to OpenAI API
    - Conversation context
    - Function calling setup
    - Response generation
    """

    def __init__(self, client: OpenAI = None, model: str = "gpt-4o-mini"):
        """Initialize the OpenAI client and configuration."""

        if client is None:
            api_key = os.getenv("OPENAI_API_KEY")

            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY not found! Please add it to your .env file"
                )

            self.client = OpenAI(api_key=api_key)
        else:
            self.client = client
        self.model = model

        # System prompt: This tells the LLM who it is and how to behave
        # Update the system_prompt section (around line 55):

        self.system_prompt = """You are a Smart Holiday Agent for the UK, specializing in optimal leave planning.

        Your role:
        - Help users plan their holidays strategically to maximize time off
        - Provide information about UK public holidays (England & Wales)
        - Suggest optimal times to take leave days
        - Calculate the best "bang for buck" - most consecutive days off with fewest leave days used
        - Be friendly, helpful, and concise

        Holiday Planning Strategies:
        - Bridging: Taking 1 day off to connect a holiday with a weekend (e.g., holiday on Thursday → take Friday off → 4-day weekend)
        - Sandwiching: Taking days off between two holidays to create extended breaks
        - Efficiency Ratio: Total days off ÷ Leave days used (higher is better!)

        Guidelines:
        - Always mention specific dates and day names
        - Show calculations when suggesting leave plans
        - Example: "If you take Friday off, you'll get 4 consecutive days (1 leave day → 4 days off, ratio: 4:1)"
        - Use emojis sparingly (🎉 for holidays, 📅 for dates, 💡 for tips)
        - If you don't have enough information, ask the user for preferences
        - Focus on England & Wales bank holidays

        Example responses:
        User: "Help me plan around Easter"
        You: "Easter 2026 is on Sunday, April 5th. Good Friday (April 3rd) is a bank holiday.
        💡 Strategy: Take Monday April 6th and Tuesday April 7th off.
        Result: 5 consecutive days (Fri-Tue) using only 2 leave days! Ratio: 2.5:1"
    """
        logger.info(f"LLM Handler initialized with model: {self.model}")

    def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        holidays_data: List[Dict[str, Any]],
        year: int,
        region: str = None,
        planner_constraints: UserConstraints = None,
        top_n: int = 3,
    ) -> str:
        """
        Send messages to the LLM and get a response.

        This is the core function that talks to OpenAI.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
                     Example: [{"role": "user", "content": "Hello!"}]
            holidays_data: Optional holiday data to include in context

        Returns:
            str: The LLM's response

        How it works:
        1. Prepares the system prompt
        2. Adds holiday data to context if available
        3. Sends everything to OpenAI
        4. Returns the response
        """

        try:
            full_messages = [{"role": "system", "content": self.system_prompt}]

            context_parts = [
                f"Planning year: {year}",
                f"Region: {region or 'england-and-wales'}",
                self._format_constraints_for_context(planner_constraints, top_n),
            ]

            # Add holiday data to context if available
            if holidays_data:
                context_parts.append(
                    "Holidays data from the UK government website:\n"
                    f"{self._format_holidays_for_context(holidays_data)}"
                )
            else:
                context_parts.append(
                    "No holidays data is currently loaded. Ask the user to load it "
                    "before giving date-specific recommendations."
                )

            full_messages.append(
                {"role": "system", "content": "\n\n".join(context_parts)}
            )

            # Add user conversation history
            full_messages.extend(messages)
            logger.info(f"Messages to LLM: {full_messages}")
            logger.info(f"Sending {len(messages)} messages to LLM")

            # Make the API call to OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                tools=self._get_tools_definition(),
                tool_choice="auto",
                temperature=0.7,
                max_tokens=500,
            )

            assistant_message = response.choices[0].message

            if getattr(assistant_message, "tool_calls", None):
                full_messages.append(
                    self._serialize_assistant_message(assistant_message)
                )

                for tool_call in assistant_message.tool_calls:
                    tool_result = self._execute_tool_call(
                        tool_call=tool_call,
                        holidays_data=holidays_data,
                        year=year,
                        region=region or "england-and-wales",
                        planner_constraints=planner_constraints,
                        top_n=top_n,
                    )
                    full_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_result),
                        }
                    )

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=full_messages,
                    temperature=0.7,
                    max_tokens=500,
                )
                assistant_message = response.choices[0].message

            assistant_content = assistant_message.content or ""

            logger.info("LLM response received successfully")
            return assistant_content.strip() or (
                "⚠️ Sorry, I couldn't generate a response just now."
            )

        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return f"⚠️ Sorry, I encountered an error: {str(e)}\n\nPlease check your API key and internet connection."

    def _format_holidays_for_context(self, holidays_data: List[Dict[str, Any]]) -> str:
        """
        Format holiday data into a readable string for the LLM.

        The LLM needs holiday data as text, not raw JSON.
        This function converts the data into a format the LLM can understand.

        Args:
            holidays_data: Dictionary containing holiday events

        Returns:
            str: Formatted text describing all holidays
        """

        if not holidays_data:
            return "No holiday data available."

        events = holidays_data
        if isinstance(holidays_data, dict):
            events = holidays_data.get("events", [])

        if not isinstance(events, list):
            return "No holiday data available."

        # Build a formatted string
        formatted = "UK Public Holidays (England & Wales):\n\n"

        for event in events:
            date = event.get("date", "Unknown")
            title = event.get("title", "Unknown")
            notes = event.get("notes", "")
            bunting = "🎊" if event.get("bunting", False) else ""

            formatted += f"- {title}: {date} {bunting}\n"
            if notes:
                formatted += f"  Note: {notes}\n"

        return formatted

    def stream_chat_completion(
        self, messages: List[Dict[str, str]], holidays_data: List[Dict[str, Any]] = None
    ):
        """
        Stream responses from the LLM (word-by-word).

        This is more advanced - makes the response appear gradually
        like in ChatGPT. We'll implement this later if needed.

        For now, we'll use the non-streaming version above.
        """
        # TODO: Implement streaming for better UX
        pass

    def _format_constraints_for_context(
        self, planner_constraints: UserConstraints, top_n: int
    ) -> str:
        if planner_constraints is None:
            return "No planner constraints have been provided."

        preferred_months = sorted(planner_constraints.preferred_months)
        excluded_dates = sorted(
            day.isoformat() for day in planner_constraints.excluded_leave_dates
        )
        return (
            "Current planner defaults:\n"
            f"- Max leave days: {planner_constraints.max_leave_days}\n"
            f"- Minimum total days off: {planner_constraints.min_total_days_off}\n"
            f"- Maximum break window: {planner_constraints.max_window_days}\n"
            f"- Preferred months: {preferred_months or 'Any'}\n"
            f"- Excluded leave dates: {excluded_dates or 'None'}\n"
            f"- Number of ranked options to return: {top_n}"
        )

    @staticmethod
    def _get_tools_definition() -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_ranked_holiday_strategies",
                    "description": (
                        "Generate ranked holiday leave strategies using the "
                        "deterministic optimizer."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "max_leave_days": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 10,
                            },
                            "min_total_days_off": {
                                "type": "integer",
                                "minimum": 3,
                                "maximum": 18,
                            },
                            "max_window_days": {
                                "type": "integer",
                                "minimum": 4,
                                "maximum": 18,
                            },
                            "preferred_months": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": [
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
                                },
                            },
                            "excluded_leave_dates": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": "ISO date, for example 2026-12-24",
                                },
                            },
                            "top_n": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 3,
                            },
                        },
                    },
                },
            }
        ]

    def _execute_tool_call(
        self,
        tool_call: Any,
        holidays_data: List[Dict[str, Any]],
        year: int,
        region: str,
        planner_constraints: UserConstraints,
        top_n: int,
    ) -> dict[str, Any]:
        if tool_call.function.name != "get_ranked_holiday_strategies":
            return {"error": f"Unsupported tool: {tool_call.function.name}"}

        if not holidays_data:
            return {
                "error": "No holidays data loaded.",
                "guidance": "Ask the user to load holidays before planning.",
            }

        arguments = json.loads(tool_call.function.arguments or "{}")
        constraints = self._build_tool_constraints(arguments, planner_constraints)
        requested_top_n = arguments.get("top_n", top_n)
        plans = generate_ranked_plans(
            holidays_data=holidays_data,
            year=year,
            constraints=constraints,
            top_n=requested_top_n,
        )
        return {
            "year": year,
            "region": region,
            "constraints": self._serialize_constraints(constraints),
            "plans": [self._serialize_plan(plan) for plan in plans],
        }

    def _build_tool_constraints(
        self, arguments: dict[str, Any], planner_constraints: UserConstraints = None
    ) -> UserConstraints:
        planner_constraints = planner_constraints or UserConstraints()
        return build_constraints(
            max_leave_days=arguments.get(
                "max_leave_days", planner_constraints.max_leave_days
            ),
            min_total_days_off=arguments.get(
                "min_total_days_off", planner_constraints.min_total_days_off
            ),
            max_window_days=arguments.get(
                "max_window_days", planner_constraints.max_window_days
            ),
            preferred_month_labels=arguments.get("preferred_months")
            or self._month_numbers_to_labels(planner_constraints.preferred_months),
            excluded_leave_dates=self._parse_excluded_dates(
                arguments.get("excluded_leave_dates"),
                planner_constraints.excluded_leave_dates,
            ),
        )

    @staticmethod
    def _parse_excluded_dates(
        raw_dates: list[str] | None, fallback_dates: set[date]
    ) -> list[date]:
        if not raw_dates:
            return sorted(fallback_dates)
        parsed = []
        for raw_date in raw_dates:
            parsed.append(datetime.strptime(raw_date, "%Y-%m-%d").date())
        return parsed

    @staticmethod
    def _month_numbers_to_labels(month_numbers: set[int]) -> list[str]:
        month_lookup = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }
        return [month_lookup[number] for number in sorted(month_numbers)]

    @staticmethod
    def _serialize_constraints(constraints: UserConstraints) -> dict[str, Any]:
        return {
            "max_leave_days": constraints.max_leave_days,
            "min_total_days_off": constraints.min_total_days_off,
            "max_window_days": constraints.max_window_days,
            "preferred_months": sorted(constraints.preferred_months),
            "excluded_leave_dates": sorted(
                day.isoformat() for day in constraints.excluded_leave_dates
            ),
        }

    @staticmethod
    def _serialize_plan(plan: Any) -> dict[str, Any]:
        summary = format_plan_summary(plan)
        return {
            "summary": summary,
            "start_date": plan.start_date.isoformat(),
            "end_date": plan.end_date.isoformat(),
            "leave_dates": [day.isoformat() for day in plan.leave_dates],
            "holiday_dates": [day.isoformat() for day in plan.holiday_dates],
            "weekend_dates": [day.isoformat() for day in plan.weekend_dates],
        }

    @staticmethod
    def _serialize_assistant_message(message: Any) -> dict[str, Any]:
        return {
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in message.tool_calls
            ],
        }


# Example usage (for testing)
if __name__ == "__main__":
    # Test the LLM handler
    handler = HolidayLLMHandler()

    test_messages = [{"role": "user", "content": "What's the next bank holiday?"}]

    # Mock holiday data
    test_holidays = [
        {
            "title": "Christmas Day",
            "date": "2026-12-25",
            "notes": "",
            "bunting": True,
        }
    ]

    response = handler.create_chat_completion(test_messages, test_holidays, 2026)
    print(f"LLM Response: {response}")
