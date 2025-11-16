import google.generativeai as genai
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai import APIError as OpenAIAPIError

from message_api import config


# --- OpenAI Specific ---
def _call_openai(messages: list[ChatCompletionMessageParam], model: str):
    """Calls the OpenAI API with a given conversation history and model."""
    try:
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0
        )
        return completion.choices[0].message.content
    except OpenAIAPIError as e:
        print(f"ERROR: OpenAI API call failed: {e}")
        return None


# --- Gemini Specific ---
def _convert_messages_to_gemini_format(messages: list[dict]):
    """Converts the standard message format to Gemini's format."""
    gemini_messages = []
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else msg["role"]
        gemini_messages.append({"role": role, "parts": [msg["content"]]})
    return gemini_messages


def _ensure_alternating_gemini_roles(messages: list[dict]):
    """
    Ensures the message history alternates between 'user' and 'model' roles,
    as required by the Gemini API.
    """
    cleaned_messages = []
    for i, msg in enumerate(messages):
        is_model_role = msg['role'] == 'model'
        is_first_message = i == 0
        previous_role_is_user = not is_first_message and messages[i - 1]['role'] == 'user'

        if is_model_role and (is_first_message or not previous_role_is_user):
            # Skip model message if it's first or not preceded by a user message.
            continue

        cleaned_messages.append(msg)
    return cleaned_messages


def _call_gemini(messages: list[dict], model: str):
    """Calls the Google Gemini API with a given conversation history and model."""
    try:
        genai.configure(api_key=config.GOOGLE_API_KEY)
        gemini_model = genai.GenerativeModel(model)

        gemini_messages = _convert_messages_to_gemini_format(messages)
        alternating_messages = _ensure_alternating_gemini_roles(gemini_messages)
        print(gemini_messages)
        response = gemini_model.generate_content(
            alternating_messages,
            generation_config=genai.types.GenerationConfig(temperature=0.0)
        )
        return response.text
    except Exception as e:
        print(f"ERROR: Gemini API call failed: {e}")
        return None


def get_llm_response(messages: list, provider: str = "openai"):
    """Dispatches the conversation to the appropriate LLM provider."""
    if provider == "openai":
        return _call_openai(messages, model=config.OPENAI_API_MODEL)
    elif provider == "gemini":
        return _call_gemini(messages, model=config.GEMINI_API_MODEL)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
