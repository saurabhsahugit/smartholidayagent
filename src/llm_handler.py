"""
LLM Handler for Smart Holiday Agent
===================================

This module handles all interactions with OpenAI's GPT models.

Key Concepts:
1. System Prompt: Instructions that tell the LLM who it is and how to behave
2. Messages: Conversation history (user + assistant messages)
3. Function Calling: Letting the LLM use our Python functions
4. Context: Giving the LLM relevant information (like holiday data)

Author: Saurabh Sahu
"""

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

        # Model configuration
        # gpt-4o-mini is cheaper and faster, good for learning
        # gpt-4o is more powerful but costs more
        self.model = "gpt-4o-mini"

        # System prompt: This tells the LLM who it is and how to behave
        self.system_prompt = """
        You are a Smart Holiday Agent for the UK.
        Your role:
        - Help users plan their holidays strategically
        - Provide information about UK public holidays
        - Suggest optimal times to take leave
        - Be friendly, helpful, and concise
        Guidelines:
        - Always mention specific dates and day names
        - Use emojis sparingly (🎉 for holidays, 📅 for dates)
        - If you don't have enough information, ask the user
        - Focus on England & Wales bank holidays
        Current capabilities:
        - Answer questions about public holidays
        - Find next upcoming holidays
        - Count holidays in a period
        - Provide holiday details (date, day of week)
        """

        logger.info(f"LLM Handler initialized with model: {self.model}")

    def create_chat_completion(
        self, messages: List[Dict[str, str]], holidays_data: Dict[str, Any] = None
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
            full_messages = [{"role": "system", "content": self.system_prompt}]

            # Add holiday data to context if available
            if holidays_data:
                context = self._format_holidays_for_context(holidays_data)
                full_messages.append(
                    {"role": "system", "content": f"Available holiday data:\n{context}"}
                )

            # Add user conversation history
            full_messages.extend(messages)

            logger.info(f"Sending {len(messages)} messages to LLM")

            # Make the API call to OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=0.7,  # Controls randomness (0=focused, 1=creative)
                max_tokens=500,  # Maximum response length
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

        events = holidays_data.get("events", [])

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
