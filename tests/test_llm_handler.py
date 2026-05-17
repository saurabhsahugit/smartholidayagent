import json

from src.llm_handler import HolidayLLMHandler
from src.optimizer import UserConstraints


class FakeFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class FakeToolCall:
    def __init__(self, call_id, name, arguments):
        self.id = call_id
        self.type = "function"
        self.function = FakeFunction(name, arguments)


class FakeMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []


class FakeChoice:
    def __init__(self, message):
        self.message = message


class FakeResponse:
    def __init__(self, message):
        self.choices = [FakeChoice(message)]


class FakeCompletions:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)


class FakeChat:
    def __init__(self, responses):
        self.completions = FakeCompletions(responses)


class FakeClient:
    def __init__(self, responses):
        self.chat = FakeChat(responses)


def sample_holidays_2026():
    return [
        {"title": "Good Friday", "date": "2026-04-03", "notes": "", "bunting": True},
        {
            "title": "Easter Monday",
            "date": "2026-04-06",
            "notes": "",
            "bunting": True,
        },
    ]


def test_create_chat_completion_returns_direct_response_without_tool_call():
    client = FakeClient([FakeResponse(FakeMessage(content="Here is a direct answer."))])
    handler = HolidayLLMHandler(client=client, model="test-model")

    result = handler.create_chat_completion(
        messages=[{"role": "user", "content": "What is the next holiday?"}],
        holidays_data=sample_holidays_2026(),
        year=2026,
        region="england-and-wales",
    )

    assert result == "Here is a direct answer."
    assert len(client.chat.completions.calls) == 1
    assert client.chat.completions.calls[0]["tools"]


def test_create_chat_completion_executes_optimizer_tool_and_returns_final_answer():
    tool_arguments = json.dumps(
        {
            "max_leave_days": 2,
            "min_total_days_off": 5,
            "max_window_days": 7,
            "preferred_months": ["April"],
            "top_n": 2,
        }
    )
    client = FakeClient(
        [
            FakeResponse(
                FakeMessage(
                    tool_calls=[
                        FakeToolCall(
                            "call_1", "get_ranked_holiday_strategies", tool_arguments
                        )
                    ]
                )
            ),
            FakeResponse(
                FakeMessage(
                    content="Take Tuesday 7 April 2026 off to extend the Easter break."
                )
            ),
        ]
    )
    handler = HolidayLLMHandler(client=client, model="test-model")

    result = handler.create_chat_completion(
        messages=[{"role": "user", "content": "What is the best Easter strategy?"}],
        holidays_data=sample_holidays_2026(),
        year=2026,
        region="england-and-wales",
        planner_constraints=UserConstraints(
            max_leave_days=4, min_total_days_off=4, max_window_days=10
        ),
        top_n=3,
    )

    assert "Easter break" in result
    assert len(client.chat.completions.calls) == 2

    tool_message = client.chat.completions.calls[1]["messages"][-1]
    payload = json.loads(tool_message["content"])
    assert payload["constraints"]["max_leave_days"] == 2
    assert payload["plans"]


def test_create_chat_completion_includes_missing_holidays_instruction_in_context():
    client = FakeClient([FakeResponse(FakeMessage(content="Please load holidays first."))])
    handler = HolidayLLMHandler(client=client, model="test-model")

    result = handler.create_chat_completion(
        messages=[{"role": "user", "content": "What should I book for May?"}],
        holidays_data=None,
        year=2026,
        region="england-and-wales",
    )

    assert "Please load holidays first." == result
    first_call_messages = client.chat.completions.calls[0]["messages"]
    context_message = first_call_messages[1]["content"]
    assert "No holidays data is currently loaded." in context_message
