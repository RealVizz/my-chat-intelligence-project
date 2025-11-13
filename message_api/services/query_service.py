from datetime import datetime, timezone

from message_api.schemas import ChatMessageSchemaObj
from message_api.utils import llm_utils, db_utils

_chat_history: list[ChatMessageSchemaObj] = []


def load_history_on_startup():
    """Loads chat history from DB into the in-memory cache when the app starts."""
    global _chat_history
    history_from_db = db_utils.load_chat_history()
    _chat_history = [ChatMessageSchemaObj(**msg) for msg in history_from_db]


def _add_turn_to_history(user_content: str, assistant_content: str):
    """Adds a full user/assistant turn to the history and database."""
    now_utc = datetime.now(timezone.utc)

    db_utils.add_message_to_chat_history(role="user", content=user_content, timestamp=now_utc.isoformat())
    _chat_history.append(ChatMessageSchemaObj(role="user", content=user_content, timestamp=now_utc))

    db_utils.add_message_to_chat_history(role="assistant", content=assistant_content, timestamp=now_utc.isoformat())
    _chat_history.append(ChatMessageSchemaObj(role="assistant", content=assistant_content, timestamp=now_utc))


def _prepare_messages_for_llm(question: str):
    """Prepares the full message list for the LLM, including history and the new question."""
    messages = [msg.model_dump(exclude={'timestamp'}) for msg in _chat_history]  # Existing history.
    messages.append({"role": "user", "content": question})  # User Input.

    return messages


def process_user_query(question: str):
    """Processes a user query using conversation history in a clean, segregated manner."""
    messages_for_llm = _prepare_messages_for_llm(question=question)
    llm_answer = llm_utils.get_llm_response(messages=messages_for_llm)

    if llm_answer:
        _add_turn_to_history(user_content=question, assistant_content=llm_answer)

    return llm_answer
