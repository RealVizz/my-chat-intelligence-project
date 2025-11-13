from openai import OpenAI

from message_api import config


def _call_openai(prompt: str, model: str):
    """Calls the OpenAI API with a given prompt and model."""
    client = OpenAI(api_key=config.OPENAI_API_KEY)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]

    completion = client.chat.completions.create(
        model=model,
        messages=messages
    )

    return completion.choices[0].message.content


def get_llm_response(prompt: str, provider: str = "openai"):
    """Dispatches the prompt to the appropriate LLM provider."""
    if provider == "openai":
        return _call_openai(prompt, model=config.OPENAI_API_MODEL)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
