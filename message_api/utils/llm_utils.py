from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from message_api import config


def _call_openai(messages: list[ChatCompletionMessageParam], model: str):
    """Calls the OpenAI API with a given conversation history and model."""
    client = OpenAI(api_key=config.OPENAI_API_KEY)

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0
    )

    return completion.choices[0].message.content


def get_llm_response(messages: list[ChatCompletionMessageParam], provider: str = "openai"):
    """Dispatches the conversation to the appropriate LLM provider."""
    if provider == "openai":
        return _call_openai(messages, model=config.OPENAI_API_MODEL)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
