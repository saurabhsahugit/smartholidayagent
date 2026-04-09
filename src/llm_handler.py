import logging
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI

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

    def __init__(self):
        """Initialize the OpenAI client and configuration."""

        # Get API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found! Please add it to your .env file"
            )

        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"

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
        holidays_data: Dict[str, Any],
        year: str,
        region: str = None,
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
            # Build the full message list
            full_messages = [
                {"role": "system", "content": "You are a Smart Holiday Agent..."},
                {"role": "system", "content": "Available holiday data: ..."},
                {"role": "user", "content": "What's the next holiday?"},
                {"role": "user", "content": f"Year: {year}"},
                {"role": "user", "content": f"Region: {region}"},
            ]

            # Add holiday data to context if available
            if holidays_data:
                context = holidays_data
                full_messages.append(
                    {
                        "role": "system",
                        "content": f"Holidays data from UK government website:\n{context}",
                    }
                )
            # Add user conversation history
            full_messages.extend(messages)
            logger.info(f"Messages to LLM: {full_messages}")
            logger.info(f"Sending {len(messages)} messages to LLM")

            # Make the API call to OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=full_messages,
                temperature=0.7,
                max_tokens=500,
            )

            # Extract the response text
            assistant_message = response.choices[0].message.content

            logger.info("LLM response received successfully")
            return assistant_message

        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return f"⚠️ Sorry, I encountered an error: {str(e)}\n\nPlease check your API key and internet connection."

    def _format_holidays_for_context(self, holidays_data: Dict[str, Any]) -> str:
        """
        Format holiday data into a readable string for the LLM.

        The LLM needs holiday data as text, not raw JSON.
        This function converts the data into a format the LLM can understand.

        Args:
            holidays_data: Dictionary containing holiday events

        Returns:
            str: Formatted text describing all holidays
        """

        if not holidays_data or "events" not in holidays_data:
            return "No holiday data available."

        events = holidays_data

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
        self, messages: List[Dict[str, str]], holidays_data: Dict[str, Any] = None
    ):
        """
        Stream responses from the LLM (word-by-word).

        This is more advanced - makes the response appear gradually
        like in ChatGPT. We'll implement this later if needed.

        For now, we'll use the non-streaming version above.
        """
        # TODO: Implement streaming for better UX
        pass


# Example usage (for testing)
if __name__ == "__main__":
    # Test the LLM handler
    handler = HolidayLLMHandler()

    test_messages = [{"role": "user", "content": "What's the next bank holiday?"}]

    # Mock holiday data
    test_holidays = {
        "events": [
            {
                "title": "Christmas Day",
                "date": "2026-12-25",
                "notes": "",
                "bunting": True,
            }
        ]
    }

    response = handler.create_chat_completion(test_messages, test_holidays)
    print(f"LLM Response: {response}")
