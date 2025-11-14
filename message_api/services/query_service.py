import json
from datetime import datetime, timezone

from rapidfuzz import process

from message_api.config import ENTITY_RESOLUTION_HISTORY_LENGTH, ANSWER_GENERATION_HISTORY_LENGTH
from message_api.prompts import system_prompts
from message_api.schemas import ChatMessageSchemaObj
from message_api.utils import llm_utils, db_utils, rag_utils

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


def _resolve_entity_and_optimize_query(question: str, history: list[ChatMessageSchemaObj], candidates: list[str]):
    """
    Uses an LLM call to identify the subject and create an optimal search query.
    Returns a tuple of (resolved_name, search_query).
    """
    if not candidates:
        return None, question  # Fallback to original question

    history_str = "\n".join([f"{msg.role}: {msg.content}" for msg in history[-ENTITY_RESOLUTION_HISTORY_LENGTH:]])
    candidates_str = ", ".join(candidates)

    prompt = system_prompts.ENTITY_RESOLUTION_PROMPT.format(
        history_str=history_str,
        candidates_str=candidates_str,
        question=question
    )

    llm_response = llm_utils.get_llm_response(messages=[{"role": "user", "content": prompt}])

    try:
        response_data = json.loads(llm_response)
        resolved_name = response_data.get("resolved_name")
        search_query = response_data.get("search_query", question)

        if resolved_name == "None" or (resolved_name and resolved_name not in candidates):
            return None, search_query

        return resolved_name, search_query
    except (json.JSONDecodeError, AttributeError):
        # If LLM fails to return valid JSON, fallback gracefully
        return None, question


def _prepare_context_from_retrieved_docs(docs: list[dict]):
    """Formats the retrieved documents into a string context for the LLM."""
    if not docs:
        return "No relevant information found in the knowledge base."

    context_str = "Relevant Information:\n"
    for doc in docs:
        context_str += f"- From {doc.get('user_name', 'Unknown')}: '{doc.get('message', '')}'\n"
    return context_str


def _retrieve_context(search_query: str, resolved_identity: str | None) -> str:
    """Encapsulates the 'Filter' and 'Search' steps: retrieves relevant context."""
    if resolved_identity:
        print(f"--- Entity Resolution: LLM identified '{resolved_identity}' ---")
    else:
        print("--- Entity Resolution: LLM could not identify a subject. ---")

    relevant_doc_ids = rag_utils.find_relevant_documents(query=search_query, user_name=resolved_identity,
                                                         top_k=50)
    retrieved_docs = db_utils.get_raw_messages_by_ids(relevant_doc_ids)
    context = _prepare_context_from_retrieved_docs(retrieved_docs)
    return context


def _generate_answer(question: str, context: str) -> str:
    """Encapsulates the 'Answer' step: generates the LLM's response."""

    prompt = system_prompts.ANSWER_GENERATION_PROMPT.format(context=context, question=question)

    # For the final answer, we still provide chat history for conversational context.
    messages_for_llm = \
        [msg.model_dump(exclude={'timestamp'}) for msg in _chat_history[-ANSWER_GENERATION_HISTORY_LENGTH:]]
    messages_for_llm.append({"role": "user", "content": prompt})

    llm_answer = llm_utils.get_llm_response(messages=messages_for_llm, provider="gemini")
    return llm_answer


def process_user_query(question: str):
    """Processes a user query using the full RAG pipeline."""
    # "Who" & "Optimize" - Entity Resolution and Query Transformation.
    potential_matches = _find_potential_identity_matches(question)
    resolved_identity, search_query = _resolve_entity_and_optimize_query(
        question=question,
        history=_chat_history,
        candidates=potential_matches
    )

    # "Filter" & "Search" - Retrieval.
    context = _retrieve_context(search_query, resolved_identity)

    # "Answer" - Generation.
    llm_answer = _generate_answer(question, context)

    # History.
    if llm_answer:
        _add_turn_to_history(user_content=question, assistant_content=llm_answer)

    return llm_answer
