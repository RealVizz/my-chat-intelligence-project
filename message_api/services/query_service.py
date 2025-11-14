from datetime import datetime, timezone

from rapidfuzz import process

from message_api.prompts import system_prompts
from message_api.schemas import ChatMessageSchemaObj
from message_api.utils import llm_utils, db_utils

_chat_history: list[ChatMessageSchemaObj] = []
_identities_cache: list[str] = []


def load_history_on_startup():
    """Loads chat history from DB into the in-memory cache."""
    global _chat_history
    history_from_db = db_utils.load_chat_history()
    _chat_history = [ChatMessageSchemaObj(**msg) for msg in history_from_db]
    # print(f"Loaded {_chat_history.__len__()} messages from chat history.")


def load_identities_on_startup():
    """Loads unique identity names from DB into the in-memory cache."""
    global _identities_cache
    _identities_cache = db_utils.load_unique_identities()
    # print(f"Loaded {_identities_cache.__len__()} unique identities into cache.")


def _add_turn_to_history(user_content: str, assistant_content: str):
    """Adds a full user/assistant turn to the history and database."""
    now_utc = datetime.now(timezone.utc)

    db_utils.add_message_to_chat_history(role="user", content=user_content, timestamp=now_utc.isoformat())
    _chat_history.append(ChatMessageSchemaObj(role="user", content=user_content, timestamp=now_utc))

    db_utils.add_message_to_chat_history(role="assistant", content=assistant_content, timestamp=now_utc.isoformat())
    _chat_history.append(ChatMessageSchemaObj(role="assistant", content=assistant_content, timestamp=now_utc))


def _find_potential_identity_matches(question: str):
    """Uses fuzzy matching to find the top 5 potential identity matches."""
    potential_matches = process.extract(question, _identities_cache, score_cutoff=45.0, limit=5)
    print([match[0] for match in potential_matches])
    return [match[0] for match in potential_matches]


def _identify_subject_of_query(question: str, history: list[ChatMessageSchemaObj], candidates: list[str]):
    """Uses an LLM call to determine the subject of the user's query from a list of candidates."""
    if not candidates:
        return None

    history_str = "\n".join([f"{msg.role}: {msg.content}" for msg in history[-10:]])
    candidates_str = ", ".join(candidates)

    prompt = system_prompts.ENTITY_RESOLUTION_PROMPT.format(
        history_str=history_str,
        candidates_str=candidates_str,
        question=question
    )

    llm_response = llm_utils.get_llm_response(messages=[{"role": "user", "content": prompt}])

    if llm_response and llm_response.strip() != "None":
        if llm_response.strip() in candidates:
            return llm_response.strip()
    return None


def _prepare_messages_for_llm(question: str, context: str = None):
    """Prepares the full message list for the main LLM call."""
    messages = [msg.model_dump(exclude={'timestamp'}) for msg in _chat_history]

    if context:
        question_with_context = f"Context: {context}\n\nQuestion: {question}"
        messages.append({"role": "user", "content": question_with_context})
    else:
        messages.append({"role": "user", "content": question})

    return messages


def process_user_query(question: str):
    """Processes a user query using a two-step LLM approach for entity resolution and answering."""
    potential_matches = _find_potential_identity_matches(question)

    resolved_identity = _identify_subject_of_query(
        question=question,
        history=_chat_history,
        candidates=potential_matches
    )

    context = None
    if resolved_identity:
        print(f"--- Entity Resolution: LLM identified '{resolved_identity}' ---")
        context = f"The user is asking about {resolved_identity}."
    else:
        print("--- Entity Resolution: LLM could not identify a subject. ---")

    messages_for_llm = _prepare_messages_for_llm(question=question, context=context)

    llm_answer = llm_utils.get_llm_response(messages=messages_for_llm, provider="gemini")

    if llm_answer:
        _add_turn_to_history(user_content=question, assistant_content=llm_answer)

    return llm_answer
