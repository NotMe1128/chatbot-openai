import json

# --- Helper classes to perfectly mimic the OpenAI response structure ---
class MockFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class MockToolCall:
    def __init__(self, function_name, arguments):
        self.id = "call_abc123"
        self.type = "function"
        self.function = MockFunction(function_name, arguments)

class MockMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls

class MockChoice:
    def __init__(self, message):
        self.message = message

class MockResponse:
    def __init__(self, choices):
        self.choices = choices

# --- The Main Mock Client ---
class MockOpenAIClient:
    def get_mock_response(self, messages: list):
        """
        A smart mock function that always returns a perfectly structured MockResponse object.
        """
        last_message = messages[-1]

        # Case 1: The last message was a tool's output, so we need to summarize.
        if last_message['role'] == 'tool':
            tool_output = last_message['content']
            summary_text = f"Thank you. The eligibility check is complete. The result is: {tool_output}"
            # Build the full response structure for a simple text reply
            message = MockMessage(content=summary_text)
            return MockResponse(choices=[MockChoice(message)])

        # Case 2: The last message was from the user. Decide what to do.
        history_text = " ".join([m['content'] for m in messages if m['role'] == 'user'])
        has_email = "<EMAIL_ADDRESS>" in history_text
        has_age = any(char.isdigit() for char in history_text)

        if has_email and has_age:
            # We have enough info, so mock the tool call
            age_found = next(int(s) for s in history_text.split() if s.isdigit())
            arguments = json.dumps({"age": age_found, "email": "<EMAIL_ADDRESS>"})
            tool_call = MockToolCall("check_eligibility", arguments)
            # Build the full response structure for a tool call reply
            message = MockMessage(tool_calls=[tool_call])
            return MockResponse(choices=[MockChoice(message)])
        else:
            # We need more info, so ask a question
            reply_content = ""
            if "<PERSON>" not in history_text:
                reply_content = "Hello! What is your name?"
            elif not has_age:
                reply_content = "Thanks, <PERSON>. What is your age?"
            else: # Not has_email
                reply_content = "Great. And what is your email address?"
            # Build the full response structure for a simple text reply
            message = MockMessage(content=reply_content)
            return MockResponse(choices=[MockChoice(message)])